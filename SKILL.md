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
4. Apply paragraph direction and physical alignment explicitly. Treat any
   paragraph containing at least one Persian/Arabic character as a Persian or
   mixed paragraph, regardless of where the Latin fragments occur:
   - Persian and mixed prose, headings, list items, table-body paragraphs,
     captions, headers, and footers: direct `w:bidi=1` and direct `w:jc=right`.
   - Do not accept inherited RTL, `w:jc=center`, `both`, `start`, or merely
     "not left" as proof of compliance. Override conflicting style and direct
     properties. A centered Persian role is allowed only when the user
     explicitly requests that exact role to be centered.
   - English prose: `w:bidi=0`, normally `w:jc=left`.
   - Centered objects/page numbers: explicit `w:jc=center`; choose bidi based
     on their content.
   - Mandatory table-header exception: every nonempty paragraph in the first
     row of every table is directly `w:jc=center`, whether its text is Persian,
     Latin, numeric, or mixed. Persian/mixed headers still require direct
     `w:bidi=1`; pure Latin headers require direct `w:bidi=0`. Set header-cell
     vertical alignment to center too. This role exception overrides ordinary
     Persian right alignment only in the table header row.
   - Mandatory table-body rule: no nonempty paragraph below the first row may
     remain centered. If it contains any Persian/Arabic character, including a
     mixed Persian/Latin phrase, set direct `w:bidi=1` and `w:jc=right`. If it
     contains only English/Latin text, only digits, or their LTR combination,
     set direct `w:bidi=0` and `w:jc=left`.
5. Apply run direction and mixed-script boundaries explicitly:
   - Persian run: `w:rtl=1`, `w:lang w:val=fa-IR w:bidi=fa-IR`.
   - English run: `w:rtl=0`, `w:lang w:val=en-US`.
   - Set all four `w:rFonts` slots: `ascii`, `hAnsi`, `eastAsia`, and `cs`.
   - Keep every Latin token in its own LTR run inside an RTL paragraph. Preserve
     a real boundary space or punctuation mark so Word never displays joined
     forms such as `SAPنام`, `Systemسامانه`, or `FioriوHANA`.
   - Never start a run with a combining mark. Keep Persian base letters and
     combining marks in the same run, with identical font/language/direction.
     For Persian ezafe after heh, preserve `U+0647 U+0654` (`هٔ`) as one
     grapheme in one run. Do not silently replace it with `U+06C0` (`ۀ`), which
     is a different Unicode letter; any orthographic substitution requires the
     user's explicit approval. Re-render every occurrence in Word and reject a
     dotted circle or detached hamza; textual equality is not visual proof.
6. Apply the same rules at style level and direct paragraph level. Word may
   otherwise display correctly in one renderer but inherit LTR in Word.
7. Process every Word story: document body, tables, headers, footers,
   footnotes/endnotes, comments, text boxes, drawing text, and content controls.
8. For every Persian or mixed table, keep semantic column 1 as the first cell
   in each row and set `w:tblPr/w:bidiVisual=1`, so Word displays column 1 at
   the far right, column 2 immediately to its left, and the last column at the
   far left. Do not reverse only the header labels or rely on authoring-tool
   column order. Verify the rendered Word table against row data, not just XML.
   Every Persian/mixed table-body paragraph remains RTL/right; pure Latin or
   numeric table-body paragraphs are LTR/left. The first/header row follows the
   mandatory centered-header exception above. Use light gray `#D9D9D9` outer
   and inner table borders unless the user supplies a different table design.
9. Model lists with real numbering when possible. For RTL lists use a right
   indent plus hanging indent; remove inherited left indents. Do not use
   space-based alignment.
10. Keep BPMN/DFD/process diagrams LTR when the intended process flow is LTR,
   even when surrounding prose is RTL. Do not mirror an embedded image.
11. Build TOCs deliberately. Read `references/toc-and-numbering.md` before
    creating or repairing a Persian TOC.
12. Remove paragraph borders and decorative rules from the Word `Title` style
    and from title paragraphs unless the user explicitly requests them.
13. Run `scripts/audit_docx_bidi.py` and fix every error.
14. Treat a desktop Word save as a mutating build step. Read
    `references/word-roundtrip.md`, harden Word's saved copy, and run the
    paragraph- and run-level audits again.
15. Use Microsoft Word as the primary renderer whenever it is installed. Prefer
    Word 2024, otherwise use the newest available Word version. Use LibreOffice
    only after verifying that no usable Word installation exists or Word cannot
    render the file, and disclose that fallback. Never let a successful
    LibreOffice render overrule a Word defect.
16. Stabilize dynamic fields before release. Update the TOC, PAGE, NUMPAGES,
    cross-references, and pagination in Word, save a working copy, harden it,
    then lock the final current TOC field and every nested TOC field in the
    release copy so verification cannot regenerate its internal bookmarks,
    then compare a read-only Word render before and after an in-memory field
    update. Page count and visible field results must match. If they differ,
    repeat the Word-save/harden/audit cycle; `updateFields=1` alone is not proof.
17. Open the exact hardened deliverable read-only in the named Word version
    when available. Recheck headers, first/last lines, wrapped lists,
    mixed-language headings, TOC leaders, tables, and page breaks. Do not save
    this verification copy; another save requires another hardening/audit pass.

## Deterministic tools

- Run `scripts/harden_docx_bidi.py INPUT OUTPUT --mode auto` to repair paragraph,
  run, header/footer, style, and list-direction properties.
- Run `scripts/audit_docx_bidi.py FILE --json REPORT.json` for a machine-readable
  release gate.
- Run `scripts/audit_docx_run_props.py FILE --report REPORT.json` after any Word
  save. Add `--require-toc` and `--require-page-fields` when applicable.
- Run `scripts/verify_word_render.ps1 -Docx FILE -OutputDirectory DIR` on
  Windows to prove that the exact hardened DOCX is stable before and after an
  in-memory Word field update. It must rasterize both PDFs with `pdftoppm` and
  require page-image hashes, page counts, and field snapshots to match. Pass
  `-PdfToPpmPath` when the converter is not on `PATH`. A nonzero exit or
  `stable=false` blocks release.
- Run `scripts/make_bidi_fixture.py OUTPUT.docx` to generate an adversarial
  Persian/English test document.
- Run `scripts/smoke_test.py` after changing any bundled script.

Read `references/ooxml-bidi.md` before modifying XML or debugging Word-only
failures. Read `references/qa-matrix.md` before release. Read
`references/word-roundtrip.md` before using desktop Word to update or verify a
deliverable. Read
`references/portability.md` when the agent is not Codex/OpenAI or when tool
availability differs.

## Non-negotiable release gates

- The DOCX ZIP passes CRC validation and opens without repair warnings.
- Every nonempty paragraph has an intentional `w:jc` and `w:bidi`.
- Every paragraph containing Persian is directly `w:bidi=1` and
  `w:jc=right`, including headings, table body, and story parts. Every table
  header paragraph is directly `w:jc=center` for every language while retaining
  language-appropriate bidi; this mandatory header role is the explicit
  exception.
- No nonempty table-body paragraph is centered: Persian/mixed is RTL/right and
  English-only or numeric-only is LTR/left.
- Every visible Persian or Latin run has direct direction, language, and all
  four font slots after the final Word save; Persian bold runs also have
  `w:bCs`.
- Persian headings begin visually at the right edge; their number is the
  rightmost heading token, followed by one space or ` - ` and the title.
- No Persian list inherits a left indent.
- Headers are separate story parts and pass the same bidi audit as the body.
- Persian TOC entries read from the right: heading number, separator, title,
  dot leader, then page number at the far left.
- English/code/URL runs remain LTR and are not character-reversed.
- No run begins with a combining mark; no detached/dotted-circle hamza remains;
  Persian/Latin boundaries retain visible spacing in Word.
- In any document designated Persian or Persian/English, every table has
  `w:bidiVisual=1`; Word shows semantic column 1 at the far right and the final
  column at the far left on every page. A separate LTR-only document is outside
  this table policy; do not silently exempt individual tables inside a Persian
  deliverable.
- Title paragraphs have no unintended border or decorative rule.
- A no-update read-only Word render and an update-in-memory Word render agree on
  page count, TOC entries, PAGE, and NUMPAGES results.
- The final TOC field tree is locked only after Word generates and saves its
  current results; PAGE/NUMPAGES and other unlocked fields remain verifiable.
- Required LTR diagrams remain LTR.
- No clipping, overlap, missing glyph, broken table, orphaned heading, or
  unexpected blank page remains in the inspected render.
- The read-only Word render and every audit refer to the exact final DOCX. Word
  2024 is the first-choice evidence engine when installed; LibreOffice is only
  a documented fallback.

## Honesty boundary

Do not claim “flawless,” “Word-verified,” or “tested in Word 2024” unless the
final DOCX was actually opened/rendered by that engine and all pages were
inspected. Structural XML validation is necessary but cannot replace visual QA.
