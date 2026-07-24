#!/usr/bin/env python3
import argparse
from pathlib import Path

from docx import Document


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    doc = Document()
    doc.add_heading("۱ - راهنمای آزمایشی Visual Paradigm 15.2", level=1)
    doc.add_paragraph("این یک پاراگراف فارسی شامل BPMN، DFD، عدد 2024 و مسیر C:\\Temp\\file.docx است.")
    doc.add_paragraph("English paragraph with Persian واژه and punctuation (test).")
    doc.add_heading("۱.۱ - عنوان فارسی با English Span", level=2)
    doc.add_paragraph("مرحله نخست", style="List Number")
    doc.add_paragraph("مرحله دوم با عبارت Save As و کلید Ctrl+S", style="List Number")
    table = doc.add_table(rows=2, cols=3)
    for cell, text in zip(table.rows[0].cells, ["شماره", "عنوان", "English"]):
        cell.text = text
    for cell, text in zip(table.rows[1].cells, ["۱", "نمونه ترکیبی", "BPMN Task"]):
        cell.text = text
    header = doc.sections[0].header.paragraphs[0]
    header.text = "راهنمای فارسی | English Header"
    footer = doc.sections[0].footer.paragraphs[0]
    footer.text = "۱"
    doc.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
