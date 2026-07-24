#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

FA = re.compile(r"[\u0600-\u06ff]")
LATIN = re.compile(r"[A-Za-z]")


def add_or_set(parent, tag, value):
    node = parent.find(qn(tag))
    if node is None:
        node = OxmlElement(tag)
        parent.append(node)
    node.set(qn("w:val"), value)
    return node


def text_of(p):
    return "".join(t.text or "" for t in p._p.iter(qn("w:t")))


def set_paragraph(p, rtl, alignment):
    ppr = p._p.get_or_add_pPr()
    add_or_set(ppr, "w:bidi", "1" if rtl else "0")
    add_or_set(ppr, "w:jc", alignment)


def set_run(run_el, rtl):
    rpr = run_el.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        run_el.insert(0, rpr)
    add_or_set(rpr, "w:rtl", "1" if rtl else "0")
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), "fa-IR" if rtl else "en-US")
    lang.set(qn("w:bidi"), "fa-IR" if rtl else "en-US")


def process_paragraph(p, mode):
    text = text_of(p).strip()
    if not text:
        return
    rtl = mode == "rtl" or (mode == "auto" and bool(FA.search(text)))
    set_paragraph(p, rtl, "right" if rtl else "left")
    for run in p._p.iter(qn("w:r")):
        value = "".join(t.text or "" for t in run.iter(qn("w:t")))
        if not value:
            continue
        run_rtl = rtl and not (LATIN.search(value) and not FA.search(value))
        set_run(run, run_rtl)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--mode", choices=("auto", "rtl", "ltr"), default="auto")
    args = ap.parse_args()
    doc = Document(args.input)
    paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.extend(cell.paragraphs)
    for p in paragraphs:
        process_paragraph(p, args.mode)
    seen = set()
    for section in doc.sections:
        for story in (section.header, section.footer):
            if id(story._element) in seen:
                continue
            seen.add(id(story._element))
            for p in story.paragraphs:
                process_paragraph(p, args.mode)
            for table in story.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            process_paragraph(p, args.mode)
    doc.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
