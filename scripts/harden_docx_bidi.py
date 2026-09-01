#!/usr/bin/env python3
import argparse
import re
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

FA = re.compile(r"[\u0600-\u06ff]")
LATIN = re.compile(r"[A-Za-z0-9]")
FA_FALLBACK = "B Nazanin"
FA_BOLD_FALLBACK = "B Nazanin Bold"
FA_TITLE_FALLBACK = "B Titr Bold"
EN_FALLBACK = "Arial"


def strong_direction(char):
    if FA.match(char):
        return "rtl"
    if char.isascii() and char.isalnum():
        return "ltr"
    return None


def directional_chunks(text, default="rtl"):
    current = next((strong_direction(char) for char in text if strong_direction(char)), default)
    chunks = []
    buffer = ""
    for char in text:
        direction = strong_direction(char)
        if direction is not None and direction != current:
            if buffer:
                chunks.append([current, buffer])
            buffer = char
            current = direction
        else:
            buffer += char
    if buffer:
        chunks.append([current, buffer])
    # In an RTL paragraph, trailing whitespace on an LTR boundary run renders
    # on the wrong side. Move it to the following RTL run.
    for index in range(len(chunks) - 1):
        direction, value = chunks[index]
        next_direction, next_value = chunks[index + 1]
        if direction == "ltr" and next_direction == "rtl":
            match = re.search(r"\s+$", value)
            if match:
                spaces = match.group(0)
                chunks[index][1] = value[: -len(spaces)]
                chunks[index + 1][1] = spaces + next_value
    return [(direction, value) for direction, value in chunks if value]


def split_mixed_text_run(run_el, paragraph_rtl):
    children = list(run_el)
    content_children = [child for child in children if child.tag != qn("w:rPr")]
    if not content_children or any(child.tag != qn("w:t") for child in content_children):
        return
    value = "".join(child.text or "" for child in content_children)
    if not (FA.search(value) and LATIN.search(value)):
        return
    chunks = directional_chunks(value, default="rtl" if paragraph_rtl else "ltr")
    if len(chunks) < 2:
        return
    parent = run_el.getparent()
    if parent is None:
        return
    insert_at = parent.index(run_el)
    parent.remove(run_el)
    for offset, (_, chunk) in enumerate(chunks):
        clone = deepcopy(run_el)
        for child in list(clone):
            if child.tag != qn("w:rPr"):
                clone.remove(child)
        text_node = OxmlElement("w:t")
        if chunk[:1].isspace() or chunk[-1:].isspace():
            text_node.set(qn("xml:space"), "preserve")
        text_node.text = chunk
        clone.append(text_node)
        parent.insert(insert_at + offset, clone)


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


def style_font_name(paragraph, rtl, run_el=None):
    if not rtl:
        return EN_FALLBACK
    style = paragraph.style
    if style is not None:
        rpr = style.element.find(qn("w:rPr"))
        fonts = None if rpr is None else rpr.find(qn("w:rFonts"))
        if fonts is not None:
            for slot in ("cs", "eastAsia", "hAnsi", "ascii"):
                name = fonts.get(qn(f"w:{slot}"))
                if name:
                    return name
        style_name = (style.name or "").casefold()
        if style_name == "title" or style_name == "heading 1" or "toc title" in style_name:
            return FA_TITLE_FALLBACK
        if style_name.startswith("heading "):
            return FA_BOLD_FALLBACK
    if run_el is not None:
        rpr = run_el.find(qn("w:rPr"))
        if rpr is not None and rpr.find(qn("w:b")) is not None:
            return FA_BOLD_FALLBACK
    return FA_FALLBACK


def set_run(run_el, rtl, font_name):
    rpr = run_el.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        run_el.insert(0, rpr)
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{slot}"), font_name)
    add_or_set(rpr, "w:rtl", "1" if rtl else "0")
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), "fa-IR" if rtl else "en-US")
    if rtl:
        lang.set(qn("w:bidi"), "fa-IR")
    elif qn("w:bidi") in lang.attrib:
        del lang.attrib[qn("w:bidi")]
    bold = rpr.find(qn("w:b"))
    if rtl and bold is not None:
        bold_cs = rpr.find(qn("w:bCs"))
        if bold_cs is None:
            bold_cs = OxmlElement("w:bCs")
            rpr.append(bold_cs)
        bold_cs.set(qn("w:val"), bold.get(qn("w:val"), "1"))


def current_alignment(p):
    ppr = p._p.get_or_add_pPr()
    jc = ppr.find(qn("w:jc"))
    return None if jc is None else jc.get(qn("w:val"))


def process_paragraph(p, mode, force_alignment=None):
    text = text_of(p).strip()
    if not text:
        return
    rtl = mode == "rtl" or (mode == "auto" and bool(FA.search(text)))
    # In automatic mode, preserve intentionally centered titles/captions. Table
    # header cells and Persian-containing header/footer stories are explicitly
    # forced to center by the caller. Other body content follows its language.
    alignment = force_alignment
    if alignment is None and mode == "auto" and current_alignment(p) == "center":
        alignment = "center"
    if alignment is None:
        alignment = "right" if rtl else "left"
    set_paragraph(p, rtl, alignment)
    for run in list(p._p.iter(qn("w:r"))):
        split_mixed_text_run(run, rtl)
    for run in p._p.iter(qn("w:r")):
        value = "".join(t.text or "" for t in run.iter(qn("w:t")))
        if not value:
            continue
        run_rtl = rtl and not (LATIN.search(value) and not FA.search(value))
        set_run(run, run_rtl, style_font_name(p, run_rtl, run))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--mode", choices=("auto", "rtl", "ltr"), default="auto")
    args = ap.parse_args()
    doc = Document(args.input)
    for p in doc.paragraphs:
        process_paragraph(p, args.mode)
    for table in doc.tables:
        for row_index, row in enumerate(table.rows):
            for cell in row.cells:
                for p in cell.paragraphs:
                    process_paragraph(
                        p,
                        args.mode,
                        force_alignment="center" if row_index == 0 else None,
                    )
    seen = set()
    for section in doc.sections:
        for story in (section.header, section.footer):
            if id(story._element) in seen:
                continue
            seen.add(id(story._element))
            for p in story.paragraphs:
                text = text_of(p).strip()
                process_paragraph(
                    p,
                    args.mode,
                    force_alignment="center" if FA.search(text) else None,
                )
            for table in story.tables:
                for row_index, row in enumerate(table.rows):
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            process_paragraph(
                                p,
                                args.mode,
                                force_alignment="center" if row_index == 0 else None,
                            )
    doc.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
