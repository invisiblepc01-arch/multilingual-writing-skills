# DOCX QA matrix

## Structural

- ZIP CRC passes; required content types and relationships resolve.
- Document opens without repair prompt.
- Styles, numbering, headers, footers, fields, images, and tables are present.
- All nonempty paragraphs have intentional alignment and direction.
- All Persian runs have RTL/language/font properties; English runs remain LTR.
- No unintended `updateFields=true` changes a static TOC.

## Visual, every page at 100%

- Page size, margins, header/footer distance, and section breaks are correct.
- Header is legible, right-anchored for Persian, and consistent.
- Headings are right-anchored, numbered correctly, and kept with following text.
- Body endings align at the right margin; wrapped lines remain coherent.
- List markers sit on the right and wrapped lines align under item text.
- Tables fit the page, repeat headers when needed, and contain no clipped cells.
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

## Failure classification

- Correct XML, wrong Word display: inspect style inheritance, theme fonts,
  compatibility mode, missing fonts, fields, and hidden direction controls.
- Correct body, wrong header: process header story parts separately.
- Right alignment but apparent left start: inspect line length, paragraph mark,
  indents, tabs, list style, and mixed LTR runs.
- Correct PDF, wrong Word: trust Word as target and debug Word-specific XML.
- Correct Word, wrong PDF converter: disclose converter mismatch or use Word's
  export engine.
