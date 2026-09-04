#!/usr/bin/env python3
"""Audit direct run properties that Word can strip during a save round-trip."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from lxml import etree


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
Q = lambda name: f"{{{W}}}{name}"
FA_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_OR_ASCII_DIGIT_RE = re.compile(r"[A-Za-z0-9]")
STORY_PART_RE = re.compile(r"word/(header|footer)\d+\.xml$")
OPTIONAL_STORIES = {"word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"}


def value(element, name: str = "val"):
    return element.get(Q(name)) if element is not None else None


def duplicate_children(parent):
    if parent is None:
        return []
    tags = [child.tag for child in parent]
    return sorted({tag.split("}")[-1] for tag in tags if tags.count(tag) > 1})


def audit(path: Path, *, require_toc: bool, require_page_fields: bool):
    errors: list[dict] = []
    warnings: list[dict] = []
    stats = {
        "runs": 0,
        "visible_runs": 0,
        "rtl_runs": 0,
        "ltr_runs": 0,
        "hyperlinks": 0,
        "toc_fields": 0,
        "page_fields": 0,
        "numpages_fields": 0,
    }

    with zipfile.ZipFile(path) as archive:
        crc_failure = archive.testzip()
        if crc_failure:
            errors.append({"part": crc_failure, "error": "CRC failure"})
        names = [
            name
            for name in archive.namelist()
            if name == "word/document.xml"
            or STORY_PART_RE.fullmatch(name)
            or name in OPTIONAL_STORIES
        ]
        for part_name in names:
            root = etree.fromstring(archive.read(part_name))
            stats["hyperlinks"] += len(root.xpath(".//w:hyperlink", namespaces=NS))
            instructions = " ".join(root.xpath(".//w:instrText/text()", namespaces=NS))
            stats["toc_fields"] += len(re.findall(r"\bTOC\b", instructions))
            stats["page_fields"] += len(re.findall(r"(?<!NUM)\bPAGE\b", instructions))
            stats["numpages_fields"] += len(re.findall(r"\bNUMPAGES\b", instructions))

            for p_index, paragraph in enumerate(root.xpath(".//w:p", namespaces=NS), start=1):
                ppr = paragraph.find(Q("pPr"))
                duplicates = duplicate_children(ppr)
                if duplicates:
                    errors.append(
                        {
                            "part": part_name,
                            "paragraph": p_index,
                            "error": "duplicate paragraph properties",
                            "tags": duplicates,
                        }
                    )

                for r_index, run in enumerate(paragraph.xpath(".//w:r", namespaces=NS), start=1):
                    stats["runs"] += 1
                    text = "".join(run.xpath(".//w:t/text()", namespaces=NS))
                    if not text:
                        continue
                    has_fa = bool(FA_RE.search(text))
                    has_latin_or_digit = bool(LATIN_OR_ASCII_DIGIT_RE.search(text))
                    if not has_fa and not has_latin_or_digit:
                        continue
                    stats["visible_runs"] += 1
                    if has_fa and has_latin_or_digit:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "mixed strong directions in one run",
                                "text": text[:100],
                            }
                        )
                    if re.match(r"^[\u064B-\u065F\u0670]", text):
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "run begins with a combining mark",
                                "text": text[:100],
                            }
                        )
                    if "\u25CC" in text:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "literal dotted-circle character remains",
                                "text": text[:100],
                            }
                        )
                    expected_rtl = has_fa
                    stats["rtl_runs" if expected_rtl else "ltr_runs"] += 1
                    rpr = run.find(Q("rPr"))
                    if rpr is None:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "missing rPr",
                                "text": text[:100],
                            }
                        )
                        continue
                    duplicates = duplicate_children(rpr)
                    if duplicates:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "duplicate run properties",
                                "tags": duplicates,
                                "text": text[:100],
                            }
                        )
                    fonts = rpr.find(Q("rFonts"))
                    missing_slots = [
                        slot
                        for slot in ("ascii", "hAnsi", "eastAsia", "cs")
                        if fonts is None or not fonts.get(Q(slot))
                    ]
                    if missing_slots:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "missing font slots",
                                "slots": missing_slots,
                                "text": text[:100],
                            }
                        )
                    expected_direction = "1" if expected_rtl else "0"
                    actual_direction = value(rpr.find(Q("rtl")))
                    if actual_direction != expected_direction:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "wrong run direction",
                                "expected": expected_direction,
                                "actual": actual_direction,
                                "text": text[:100],
                            }
                        )
                    lang = rpr.find(Q("lang"))
                    expected_lang = "fa-IR" if expected_rtl else "en-US"
                    if value(lang) != expected_lang:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "wrong run language",
                                "expected": expected_lang,
                                "actual": value(lang),
                                "text": text[:100],
                            }
                        )
                    if expected_rtl and (lang is None or lang.get(Q("bidi")) != "fa-IR"):
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "missing Persian bidi language",
                                "text": text[:100],
                            }
                        )
                    if expected_rtl and rpr.find(Q("b")) is not None and rpr.find(Q("bCs")) is None:
                        errors.append(
                            {
                                "part": part_name,
                                "paragraph": p_index,
                                "run": r_index,
                                "error": "bold Persian run missing bCs",
                                "text": text[:100],
                            }
                        )

    if require_toc and stats["toc_fields"] != 1:
        errors.append({"error": "expected exactly one TOC field", "actual": stats["toc_fields"]})
    if require_page_fields and (stats["page_fields"] < 1 or stats["numpages_fields"] < 1):
        errors.append(
            {
                "error": "missing PAGE or NUMPAGES field",
                "page": stats["page_fields"],
                "numpages": stats["numpages_fields"],
            }
        )
    return {
        "file": str(path),
        "passed": not errors,
        "stats": stats,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-toc", action="store_true")
    parser.add_argument("--require-page-fields", action="store_true")
    args = parser.parse_args()
    result = audit(
        args.docx,
        require_toc=args.require_toc,
        require_page_fields=args.require_page_fields,
    )
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
