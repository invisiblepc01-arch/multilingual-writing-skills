# DOCX QA matrix

## Structural

- ZIP CRC passes; required content types and relationships resolve.
- Document opens without repair prompt.
- Styles, numbering, headers, footers, fields, images, and tables are present.
- All nonempty paragraphs have intentional alignment and direction.
- All Persian runs have RTL/language/font properties; English runs remain LTR.
- After the final Word save, every visible run has all four direct font slots;
  Persian bold runs also have `w:bCs`.
- No unintended `updateFields=true` changes a static TOC.

## Visual, every page at 100%

- Page size, margins, header/footer distance, and section breaks are correct.
- Any header/footer containing Persian is centered and consistent; mixed Latin
  runs and page-number fields remain readable.
- Persian body headings are right-anchored, numbered correctly, and kept with
  following text.
- For a dedicated cover, page 1 contains the centered `B Titr`/`B Titr Bold`
  overall title and substantive content begins on page 2.
- Body endings align at the right margin; wrapped lines remain coherent.
- List markers sit on the right and wrapped lines align under item text.
- Tables fit the page, repeat headers when needed, and contain no clipped cells.
- Table headers are centered. Each body paragraph with Persian is RTL/right;
  pure English/Latin, URL, numeric, and mathematical content is LTR/left.
- Pages 1 and 2 have been inspected separately for cover isolation, orientation
  transition, table start, bad row pagination, and large blank gaps.
- TOC order, leaders, wrapping, page numbers, and page breaks are correct.
- Embedded LTR diagrams have not been mirrored.
- No font substitution, tofu, overlap, orphan, widow, or blank-page defect.

## Target-engine matrix

Test the actual required engine first:

1. Microsoft Word 2024/2021/2019/2016 on target Windows locale.
2. Word PDF export if PDF is a deliverable.
3. LibreOffice only as a secondary compatibility check.
4. Google Docs only when it is a target; expect conversion differences.

Record engine/version, installed fonts, page count, and whether fields were
updated. Screenshots/video are evidence, not a substitute for editing the root
OOXML defect.

For Word-targeted release, use this exact evidence chain: Word update/save on a
working copy, harden, both audits, read-only Word reopen/export, then every-page
inspection. Any later save invalidates the run-level audit and render evidence.

## Failure classification

- Correct XML, wrong Word display: inspect style inheritance, theme fonts,
  compatibility mode, missing fonts, fields, and hidden direction controls.
- Correct body, wrong header: process header story parts separately.
- Right alignment but apparent left start: inspect line length, paragraph mark,
  indents, tabs, list style, and mixed LTR runs.
- Correct PDF, wrong Word: trust Word as target and debug Word-specific XML.
- Correct Word, wrong PDF converter: disclose converter mismatch or use Word's
  export engine.
