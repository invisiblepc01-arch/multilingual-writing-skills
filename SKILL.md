---
name: build-bilingual-docx
description: Create, repair, and validate production-grade Microsoft Word DOCX files containing Persian/Farsi RTL, English LTR, or mixed bilingual content. Use for Persian manuals, reports, headings, numbered lists, static or dynamic tables of contents, headers/footers, tables, captions, diagrams, and any DOCX whose alignment, bidi order, numbering, fonts, or Word 2016/2019/2021/2024 rendering must remain stable.
---

# Build bilingual DOCX

Treat layout as a compiled artifact: author semantically, encode direction explicitly, render, inspect, iterate. Never infer layout from extracted text.

## Workflow

1. Map the target language of every role: body, heading, list, table cell, caption, header/footer, TOC, code, URL, diagram.
2. Preserve a supplied DOCX: work on a copy, make local changes unless a redesign is requested.
3. Author with `python-docx`; use direct OOXML where it cannot express the property.
4. Set paragraph direction, then physical alignment, directly. Any paragraph containing at least one Persian/Arabic character is Persian/mixed: `w:bidi=1` first, then its role alignment. Direction and alignment are separate checks.
   - Body prose: physically right by role; Microsoft Word Justify only for explicitly selected body styles (normally `Normal`/`Body Text`) via direct `w:jc=both`, plus `w:compat/w:doNotExpandShiftReturn` so the final incomplete line and manual breaks stay right-anchored.
   - Right-aligned RTL role: direct `w:jc=start` on the validated Word 2024 profile. On that profile `w:jc=right` rendered physically left, a release failure; any other target needs a minimal matrix plus the effective Word audit.
   - Overall titles and chapter-opening `Title`/`Heading 1`: centered, `B Titr`/`B Titr Bold`. Subordinate Persian headings: RTL/right.
   - English prose: `w:bidi=0`, normally `w:jc=left`.
   - Centered objects/page numbers: explicit `w:jc=center`, bidi chosen by content.
   - Headers/footers: unified content is centered; two independent pieces are separate paragraphs (Persian/mixed piece RTL/right, page-number or LTR piece LTR/left).
   - Table header row: every nonempty paragraph direct `w:jc=center`; Persian/mixed also direct `w:bidi=1`, Latin-only direct `w:bidi=0`; center cell vertical alignment.
   - Table body: nothing centered. Persian/mixed (including one Latin term): direct `w:bidi=1` and `w:jc=start`; English-only or numeric-only: `w:bidi=0` and `w:jc=left`.
5. Runs:
   - Persian: `w:rtl=1`, `w:lang w:val=fa-IR w:bidi=fa-IR`. English: `w:rtl=0`, `w:lang w:val=en-US`. Set all four `w:rFonts` slots (`ascii`, `hAnsi`, `eastAsia`, `cs`). Persian bold runs also need `w:bCs`.
   - Keep each Latin token in its own LTR run inside an RTL paragraph, with a real boundary space or punctuation so Word never shows joined forms such as `SAPنام`.
   - Never start a run with a combining mark; keep Persian base letters and marks in one run with identical font/language/direction. Preserve `هٔ` as U+0647 U+0654 in one run; never silently substitute U+06C0 (requires explicit user approval). Re-render every occurrence and reject a dotted circle or detached hamza.
6. Apply the rules at style level and at direct paragraph level.
7. Cover every story: body, tables, headers, footers, footnotes/endnotes, comments, text boxes, drawing text, content controls.
8. Tables: semantic column 1 is the first cell of every row and `w:tblPr/w:bidiVisual=1` per table, so Word shows column 1 far right, the last column far left. Apply to every table independently; verify physical column position in Word for all tables. Use light gray `#D9D9D9` outer and inner borders unless the user supplies a design.
9. Lists: real numbering where possible; RTL right indent plus hanging indent, remove inherited left indents; never space-based alignment.
10. Keep BPMN/DFD/process diagrams LTR when the intended flow is LTR; never mirror an embedded image.
11. Read `references/toc-and-numbering.md` before creating or repairing a Persian TOC.
12. Remove paragraph borders and decorative rules from the `Title` style and title paragraphs unless explicitly requested.
13. Run `scripts/audit_docx_bidi.py` and fix every error.
14. A desktop Word save is a mutating build step: read `references/word-roundtrip.md`, harden Word's saved copy, re-run paragraph and run audits.
15. Render with Microsoft Word (2024 first, else newest); LibreOffice only when no usable Word exists or Word cannot render, and disclose the fallback. A LibreOffice pass never overrules a Word defect.
16. Stabilize fields: update TOC, PAGE, NUMPAGES, cross-references and pagination in Word, save a working copy, harden it, lock the final current TOC field tree and every nested TOC field in the release copy, then compare a read-only Word render before and after an in-memory field update. Page count and visible results must match; `updateFields=1` alone is not proof.
17. Open the exact hardened deliverable read-only in the named Word version; recheck headers, first/last lines, wrapped lists, mixed headings, TOC leaders, tables, page breaks. Do not save this verification copy.

## Deterministic tools

- Harden: `scripts/harden_docx_bidi.py INPUT OUTPUT --mode auto`; for justified body add `--body-alignment justify --rtl-right-jc start`, repeating `--justify-style STYLE` for each inspected ordinary-body style beyond `Normal`/`Body Text`.
- Paragraph audit: `scripts/audit_docx_bidi.py FILE --json REPORT.json` with the same alignment arguments.
- Run audit after any Word save: `scripts/audit_docx_run_props.py FILE --report REPORT.json` (`--require-toc`, `--require-page-fields` when applicable).
- Render stability: `scripts/verify_word_render.ps1 -Docx FILE -OutputDirectory DIR`; it must rasterize both PDFs with `pdftoppm` and require matching page-image hashes, page counts and field snapshots. A nonzero exit or `stable=false` blocks release.
- Table order: `scripts/audit_word_table_order.ps1 -Docx FILE -Report REPORT.json` in the target Word version; it fails unless logical header cell 1 is physically rightmost, later cells proceed monotonically leftward and the final cell is leftmost in every table. Any failing table blocks release.
- Effective alignment: `scripts/audit_word_effective_alignment.ps1 -Docx FILE -Report REPORT.json -BodyAlignment justify` for standard Justify; it checks ReadingOrder and Alignment on the exact hash and must report zero failures.
- Fixture: `scripts/make_bidi_fixture.py OUTPUT.docx`; after changing a bundled script run `scripts/smoke_test.py`, and after changing the table auditor run `tests/test_word_table_order.ps1` with Word.
- Read `references/ooxml-bidi.md` before XML work or Word-only debugging, `references/qa-matrix.md` before release, `references/word-roundtrip.md` before desktop Word steps, and `references/portability.md` when the agent is not Codex/OpenAI.

## Release gates

- DOCX ZIP passes CRC validation and opens without repair warnings.
- Every nonempty paragraph has an intentional `w:jc` and `w:bidi`; Persian paragraphs are directly `w:bidi=1` then match their role: selected body prose `both` in Justify mode, subordinate headings and Persian/mixed table body physically right (`start` on Word 2024), primary titles, unified headers/footers and table headers centered. Inherited or conflicting direct values fail.
- Justify mode includes `w:doNotExpandShiftReturn`; final incomplete lines and manual-break endings are not expanded.
- No nonempty table-body paragraph is centered or justified.
- Every visible Persian or Latin run has direct direction, language and all four font slots after the final Word save; Persian bold runs have `w:bCs`.
- Persian headings begin at the right edge; the number is the rightmost token, then one space or ` - ` and the title.
- No Persian list inherits a left indent.
- Headers are separate story parts and pass the same audit.
- Persian TOC entries read from the right: number, separator, title, dot leader, page number at far left.
- English/code/URL runs stay LTR and are not character-reversed.
- No run starts with a combining mark; no detached or dotted-circle hamza; Persian/Latin boundaries keep visible spacing.
- In any Persian or Persian/English document every table has `w:bidiVisual=1`, Word shows column 1 far right and the final column far left on every page, and the Word position audit passes for the complete table count with zero failures; checking the first table or the attribute alone is insufficient.
- Title paragraphs have no unintended border or decorative rule.
- A no-update read-only Word render and an update-in-memory Word render agree on page count, TOC entries, PAGE and NUMPAGES results.
- The final TOC field tree is locked only after Word generated and saved its current results; PAGE/NUMPAGES and other unlocked fields remain verifiable.
- Required LTR diagrams remain LTR.
- No clipping, overlap, missing glyph, broken table, orphaned heading or unexpected blank page remains in the inspected render.
- The read-only render and every audit refer to the exact final DOCX; Word 2024 is the first-choice engine, LibreOffice only a documented fallback.
- The effective Word audit confirms direction and physical alignment together; RTL-but-left or right-but-LTR fails.

## Honesty boundary

Never claim flawless, Word-verified or tested in Word 2024 unless the final DOCX was actually opened and rendered by that engine. Inspect every page unless the user requests representative sampling, then state the sampling scope; whole-document automated audits stay complete. Structural XML validation is necessary but never replaces visual QA.
