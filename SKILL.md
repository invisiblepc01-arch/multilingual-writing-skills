---
name: build-bilingual-docx
description: Create, repair, and validate production-grade Microsoft Word DOCX files containing Persian/Farsi RTL, English LTR, or mixed bilingual content. Use for Persian manuals, reports, headings, numbered lists, static or dynamic tables of contents, headers/footers, tables, captions, diagrams, and any DOCX whose alignment, bidi order, numbering, fonts, or Word 2016/2019/2021/2024 rendering must remain stable.
---

# Build bilingual DOCX

Treat Word layout as a compiled artifact: author semantically, encode direction
explicitly, render with the target engine, inspect, and iterate. Never infer
correct layout from extracted text alone.

## Required workflow

1. Identify the target language of every structural role: body, heading, list,
   table cell, caption, header/footer, TOC, code, URL, and diagram.
2. Preserve a supplied DOCX. Work on a copy and make local changes unless the
   user requests a redesign.
3. Use `python-docx` for authoring and direct OOXML for properties it cannot
   express reliably.
4. Apply paragraph direction and physical alignment explicitly:
   - Persian prose and headings: `w:bidi=1`, `w:jc=right`.
   - English prose: `w:bidi=0`, normally `w:jc=left`.
   - Centered objects/page numbers: explicit `w:jc=center`; choose bidi based
     on their content.
5. Apply run direction explicitly:
   - Persian run: `w:rtl=1`, `w:lang w:val=fa-IR w:bidi=fa-IR`.
   - English run: `w:rtl=0`, `w:lang w:val=en-US`.
   - Set all four `w:rFonts` slots: `ascii`, `hAnsi`, `eastAsia`, and `cs`.
6. Apply the same rules at style level and direct paragraph level. Word may
   otherwise display correctly in one renderer but inherit LTR in Word.
7. Process every Word story: document body, tables, headers, footers,
   footnotes/endnotes, comments, text boxes, drawing text, and content controls.
8. Model lists with real numbering when possible. For RTL lists use a right
   indent plus hanging indent; remove inherited left indents. Do not use
   space-based alignment.
9. Keep BPMN/DFD/process diagrams LTR when the intended process flow is LTR,
   even when surrounding prose is RTL. Do not mirror an embedded image.
10. Build TOCs deliberately. Read `references/toc-and-numbering.md` before
    creating or repairing a Persian TOC.
11. Run `scripts/audit_docx_bidi.py` and fix every error.
12. Render with Microsoft Word when Word fidelity is required. Otherwise render
    with LibreOffice and disclose the renderer. Inspect every page at 100%.
13. Open the final file in the named Word version when available. Recheck
    headers, first/last lines, wrapped lists, mixed-language headings, TOC
    leaders, tables, and page breaks.

## Deterministic tools

- Run `scripts/harden_docx_bidi.py INPUT OUTPUT --mode auto` to repair paragraph,
  run, header/footer, style, and list-direction properties.
- Run `scripts/audit_docx_bidi.py FILE --json REPORT.json` for a machine-readable
  release gate.
- Run `scripts/make_bidi_fixture.py OUTPUT.docx` to generate an adversarial
  Persian/English test document.

Read `references/ooxml-bidi.md` before modifying XML or debugging Word-only
failures. Read `references/qa-matrix.md` before release. Read
`references/portability.md` when the agent is not Codex/OpenAI or when tool
availability differs.

## Non-negotiable release gates

- The DOCX ZIP passes CRC validation and opens without repair warnings.
- Every nonempty paragraph has an intentional `w:jc` and `w:bidi`.
- Persian headings begin visually at the right edge; their number is the
  rightmost heading token, followed by one space or ` - ` and the title.
- No Persian list inherits a left indent.
- Headers are separate story parts and pass the same bidi audit as the body.
- Persian TOC entries read from the right: heading number, separator, title,
  dot leader, then page number at the far left.
- English/code/URL runs remain LTR and are not character-reversed.
- Required LTR diagrams remain LTR.
- No clipping, overlap, missing glyph, broken table, orphaned heading, or
  unexpected blank page remains in the inspected render.

## Honesty boundary

Do not claim “flawless,” “Word-verified,” or “tested in Word 2024” unless the
final DOCX was actually opened/rendered by that engine and all pages were
inspected. Structural XML validation is necessary but cannot replace visual QA.
