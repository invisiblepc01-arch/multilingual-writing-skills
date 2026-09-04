# DOCX QA matrix

## Structural

- ZIP CRC passes; required content types and relationships resolve.
- Document opens without repair prompt.
- Styles, numbering, headers, footers, fields, images, and tables are present.
- Every nonempty paragraph has direct alignment and direction. Every paragraph
  containing Persian is `w:bidi=1` and `w:jc=right`; centered or justified
  Persian fails except for the mandatory table-header role below.
- Every nonempty paragraph in the first row of every table is directly
  `w:jc=center`, for Persian, Latin, numeric, and mixed text; Persian/mixed
  headers keep `w:bidi=1`, pure Latin headers keep `w:bidi=0`, and the cells are
  vertically centered.
- Every nonempty paragraph below the first row is never centered: any Persian
  or mixed content is directly `w:bidi=1` and `w:jc=right`; English-only,
  digits-only, or LTR alphanumeric content is directly `w:bidi=0` and
  `w:jc=left`.
- All Persian runs have RTL/language/font properties; English runs remain LTR.
- After the final Word save, every visible run has all four direct font slots;
  Persian bold runs also have `w:bCs`.
- In every Persian or Persian/English deliverable, every table has
  `w:bidiVisual=1`; semantic cell 1 remains XML cell 1 and is rendered at the
  far right in Word. Do not silently exempt a Latin-only table inside it.
- No run begins with a combining mark. Every `U+0647 U+0654` grapheme is wholly
  inside one Persian run with one font/language/direction and renders without a
  dotted circle. Do not substitute `U+06C0` without explicit user approval.
- The `Title` style and title paragraphs contain no unintended `w:pBdr` or
  decorative rule.
- Dynamic fields are saved with current cached results. `updateFields=true`
  does not replace the stability comparison; static TOCs must not be changed.
- After Word generates the final current TOC, the release copy locks the outer
  TOC field and its nested HYPERLINK/PAGEREF fields. Verification confirms the
  locked TOC remains unchanged while all other fields update in memory.
- The Word verifier's two PDF exports rasterize to the same page count and
  byte-identical page images; any mismatched page blocks release and is then
  inspected visually at 100%.

## Visual, every page at 100%

- Page size, margins, header/footer distance, and section breaks are correct.
- Any header/footer containing Persian is right-aligned unless the user
  explicitly requested centering; mixed Latin runs and page-number fields
  remain readable.
- Persian body headings are right-anchored, numbered correctly, and kept with
  following text.
- For a dedicated cover, page 1 contains the centered `B Titr`/`B Titr Bold`
  overall title and substantive content begins on page 2.
- Body endings align at the right margin; wrapped lines remain coherent.
- List markers sit on the right and wrapped lines align under item text.
- Tables fit the page, repeat headers when needed, and contain no clipped cells.
- Each header or body cell paragraph containing Persian is RTL/right; pure
  English/Latin, URL, numeric, and mathematical content is LTR/left unless the
  user explicitly requested another alignment.
- For every Persian/mixed table, compare a complete header/data row in the Word
  render: semantic column 1 is far right, later columns proceed leftward, and
  the last column is far left. Checking only cell alignment is insufficient.
- Pages 1 and 2 have been inspected separately for cover isolation, orientation
  transition, table start, bad row pagination, and large blank gaps.
- TOC order, leaders, wrapping, page numbers, and page breaks are correct.
- Embedded LTR diagrams have not been mirrored.
- Latin/Persian boundaries retain visible spaces and punctuation; no joined
  forms or reversed Latin tokens remain.
- Every ezafe/hamza occurrence is attached to its base letter; no dotted circle
  or isolated combining glyph appears.
- No font substitution, tofu, overlap, orphan, widow, or blank-page defect.

## Target-engine matrix

Test the actual required engine first. If desktop Word is installed, using
LibreOffice as the primary release renderer is a failure:

1. Microsoft Word 2024/2021/2019/2016 on target Windows locale.
2. Word PDF export if PDF is a deliverable.
3. LibreOffice only as a secondary compatibility check or documented fallback
   after Word is confirmed unavailable/unusable.
4. Google Docs only when it is a target; expect conversion differences.

Record engine/version, installed fonts, page count, and whether fields were
updated. Screenshots/video are evidence, not a substitute for editing the root
OOXML defect.

For Word-targeted release, use this exact evidence chain: Word update/save on a
working copy, harden, both audits, read-only Word reopen/export without field
updates, a second read-only export with in-memory field updates, comparison of
page count and visible TOC/PAGE/NUMPAGES results, then every-page inspection.
Any mismatch or later save invalidates the release evidence and requires another
save/harden/audit cycle.

## Failure classification

- Correct XML, wrong Word display: inspect style inheritance, theme fonts,
  compatibility mode, missing fonts, fields, and hidden direction controls.
- Correct body, wrong header: process header story parts separately.
- Right alignment but apparent left start: inspect line length, paragraph mark,
  indents, tabs, list style, and mixed LTR runs.
- Correct PDF, wrong Word: trust Word as target and debug Word-specific XML.
- Correct Word, wrong PDF converter: disclose converter mismatch or use Word's
  export engine.
