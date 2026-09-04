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
FA_LETTER = r"[\u0621-\u063a\u0641-\u064a\u066e-\u06d3\u06fa-\u06ff]"
GLUED_SCRIPTS = re.compile(rf"(?:{FA_LETTER}(?=[A-Za-z0-9])|[A-Za-z0-9](?={FA_LETTER}))")
RUN_LEADING_COMBINING = re.compile(r"^[\u064b-\u065f\u0670]")
COMBINING_DOTTED_CIRCLE = "\u25cc"


def attr(node, name):
    return None if node is None else node.get(W + name)


def first_table_row_paragraph(p):
    tr = p.getparent()
    while tr is not None and tr.tag != W + "tr":
        tr = tr.getparent()
    if tr is None:
        return False
    tbl = tr.getparent()
    while tbl is not None and tbl.tag != W + "tbl":
        tbl = tbl.getparent()
    if tbl is None:
        return False
    rows = [child for child in tbl if child.tag == W + "tr"]
    return bool(rows) and rows[0] is tr


def inside_table_cell(p):
    node = p.getparent()
    while node is not None:
        if node.tag == W + "tc":
            return True
        node = node.getparent()
    return False


def paragraph_style(p):
    ppr = p.find("w:pPr", NS)
    style = None if ppr is None else ppr.find("w:pStyle", NS)
    return attr(style, "val") or ""


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
                part_has_persian = bool(FA.search("".join(root.xpath(".//w:t/text()", namespaces=NS))))
                for table_index, table in enumerate(root.xpath(".//w:tbl", namespaces=NS), 1):
                    if not part_has_persian:
                        continue
                    tbl_pr = table.find("w:tblPr", NS)
                    bidi_visual = None if tbl_pr is None else tbl_pr.find("w:bidiVisual", NS)
                    if attr(bidi_visual, "val") not in {"1", "true", "on"}:
                        errors.append({"part": part, "table": table_index, "issue": "Persian-document table is not visually RTL (missing w:bidiVisual=1)"})
                    for cell_index, cell in enumerate(table.xpath("w:tr[1]/w:tc", namespaces=NS), 1):
                        vertical = cell.find("w:tcPr/w:vAlign", NS)
                        if attr(vertical, "val") != "center":
                            errors.append({"part": part, "table": table_index, "cell": cell_index, "issue": "Table header cell is not vertically centered"})
                for i, p in enumerate(root.xpath(".//w:p", namespaces=NS), 1):
                    text = "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
                    if not text:
                        continue
                    stats["paragraphs"] += 1
                    ppr = p.find("w:pPr", NS)
                    jc = None if ppr is None else ppr.find("w:jc", NS)
                    bidi = None if ppr is None else ppr.find("w:bidi", NS)
                    is_header_footer = bool(re.match(r"word/(header|footer)\d+\.xml$", part))
                    is_table_header = inside_table_cell(p) and first_table_row_paragraph(p)
                    is_table_body = inside_table_cell(p) and not is_table_header
                    if jc is None:
                        errors.append({"part": part, "paragraph": i, "issue": "missing w:jc", "text": text[:80]})
                    if bidi is None:
                        errors.append({"part": part, "paragraph": i, "issue": "missing w:bidi", "text": text[:80]})
                    if FA.search(text) and attr(bidi, "val") not in {"1", "true", "on"}:
                        errors.append({"part": part, "paragraph": i, "issue": "Persian paragraph is not RTL", "text": text[:80]})
                    if FA.search(text) and not is_table_header and attr(jc, "val") != "right":
                        errors.append({"part": part, "paragraph": i, "issue": "Persian/mixed paragraph is not directly right aligned", "text": text[:80]})
                    if GLUED_SCRIPTS.search(text):
                        errors.append({"part": part, "paragraph": i, "issue": "missing Persian/Latin boundary separator", "text": text[:80]})
                    for run_index, run in enumerate(p.xpath(".//w:r", namespaces=NS), 1):
                        run_text = "".join(run.xpath(".//w:t/text()", namespaces=NS))
                        if RUN_LEADING_COMBINING.search(run_text):
                            errors.append({"part": part, "paragraph": i, "run": run_index, "issue": "run begins with a combining mark", "text": run_text[:80]})
                        if COMBINING_DOTTED_CIRCLE in run_text:
                            errors.append({"part": part, "paragraph": i, "run": run_index, "issue": "literal dotted-circle character remains", "text": run_text[:80]})
                    if is_header_footer and FA.search(text) and attr(jc, "val") != "right":
                        errors.append({"part": part, "paragraph": i, "issue": "Persian-containing header/footer is not right aligned", "text": text[:80]})
                    if is_table_header and attr(jc, "val") != "center":
                        errors.append({"part": part, "paragraph": i, "issue": "Table header is not directly center aligned", "text": text[:80]})
                    if is_table_body and FA.search(text) and attr(jc, "val") != "right":
                        errors.append({"part": part, "paragraph": i, "issue": "Persian table-body paragraph is not right aligned", "text": text[:80]})
                    if is_table_body and not FA.search(text):
                        if attr(jc, "val") != "left":
                            errors.append({"part": part, "paragraph": i, "issue": "English/numeric table-body paragraph is not left aligned", "text": text[:80]})
                        if attr(bidi, "val") not in {"0", "false", "off"}:
                            errors.append({"part": part, "paragraph": i, "issue": "English/numeric table-body paragraph is not explicitly LTR", "text": text[:80]})
                    style = paragraph_style(p).casefold()
                    if FA.search(text) and style.startswith("heading") and attr(jc, "val") != "right":
                        errors.append({"part": part, "paragraph": i, "issue": "Persian heading is not right aligned", "text": text[:80]})
                    if style == "title":
                        borders = None if ppr is None else ppr.find("w:pBdr", NS)
                        if borders is not None and len(borders):
                            errors.append({"part": part, "paragraph": i, "issue": "Title paragraph has a decorative border", "text": text[:80]})
                    ind = None if ppr is None else ppr.find("w:ind", NS)
                    if FA.search(text) and ind is not None and attr(ind, "left") not in {None, "0"}:
                        warnings.append({"part": part, "paragraph": i, "issue": "Persian paragraph has left indent", "text": text[:80]})
            if "word/styles.xml" in zf.namelist():
                styles = etree.fromstring(zf.read("word/styles.xml"))
                for style in styles.xpath('.//w:style[@w:styleId="Title" or w:name[@w:val="Title"]]', namespaces=NS):
                    borders = style.find("w:pPr/w:pBdr", NS)
                    if borders is not None and len(borders):
                        errors.append({"part": "word/styles.xml", "issue": "Title style has a decorative border"})
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
