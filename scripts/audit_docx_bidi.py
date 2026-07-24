#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = f"{{{NS['w']}}}"
FA = re.compile(r"[\u0600-\u06ff]")


def attr(node, name):
    return None if node is None else node.get(W + name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--json", dest="json_path", type=Path)
    args = ap.parse_args()
    errors, warnings, stats = [], [], Counter()
    try:
        with ZipFile(args.docx) as zf:
            crc = zf.testzip()
            if crc:
                errors.append({"part": crc, "issue": "CRC failure"})
            parts = [
                n for n in zf.namelist()
                if n == "word/document.xml"
                or re.match(r"word/(header|footer)\d+\.xml$", n)
                or n in {"word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"}
            ]
            for part in parts:
                root = etree.fromstring(zf.read(part))
                for i, p in enumerate(root.xpath(".//w:p", namespaces=NS), 1):
                    text = "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
                    if not text:
                        continue
                    stats["paragraphs"] += 1
                    ppr = p.find("w:pPr", NS)
                    jc = None if ppr is None else ppr.find("w:jc", NS)
                    bidi = None if ppr is None else ppr.find("w:bidi", NS)
                    if jc is None:
                        errors.append({"part": part, "paragraph": i, "issue": "missing w:jc", "text": text[:80]})
                    if bidi is None:
                        errors.append({"part": part, "paragraph": i, "issue": "missing w:bidi", "text": text[:80]})
                    if FA.search(text) and attr(bidi, "val") not in {"1", "true", "on"}:
                        errors.append({"part": part, "paragraph": i, "issue": "Persian paragraph is not RTL", "text": text[:80]})
                    if FA.search(text) and attr(jc, "val") == "left":
                        errors.append({"part": part, "paragraph": i, "issue": "Persian paragraph is left aligned", "text": text[:80]})
                    ind = None if ppr is None else ppr.find("w:ind", NS)
                    if FA.search(text) and ind is not None and attr(ind, "left") not in {None, "0"}:
                        warnings.append({"part": part, "paragraph": i, "issue": "Persian paragraph has left indent", "text": text[:80]})
    except (BadZipFile, FileNotFoundError) as exc:
        errors.append({"part": str(args.docx), "issue": str(exc)})

    report = {
        "file": str(args.docx),
        "passed": not errors,
        "stats": dict(stats),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.json_path:
        args.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
