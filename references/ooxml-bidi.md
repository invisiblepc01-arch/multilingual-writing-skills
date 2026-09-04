# OOXML bidi reference

## Contents

1. Paragraph properties
2. Run properties
3. Styles and inheritance
4. Lists and indents
5. Story parts
6. Mixed-language text
7. Tables, headers, footers, and cover pages
8. Compatibility hazards

## 1. Paragraph properties

For every paragraph containing Persian/Arabic script, including a paragraph
that also contains Latin text:

```xml
<w:pPr>
  <w:jc w:val="right"/>
  <w:bidi w:val="1"/>
</w:pPr>
```

`w:bidi` controls paragraph reading order. `w:jc` controls physical alignment.
Neither substitutes for the other. “Right justify” in user language usually
means `right`, not Word's full-width `both`; confirm if ambiguous.

The release audit must require both direct properties. Do not treat inherited
style direction, `center`, `both`, `start`, or "not left" as equivalent to
right alignment. Apply the same rule inside tables and all story parts. Center
a Persian paragraph only when the user explicitly requests that role.

For English use `w:bidi=0` and normally `w:jc=left`. For a centered page number,
use `center` explicitly.

## 2. Run properties

Persian runs require complex-script properties:

```xml
<w:rPr>
  <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin"
            w:eastAsia="B Nazanin" w:cs="B Nazanin"/>
  <w:rtl w:val="1"/>
  <w:lang w:val="fa-IR" w:bidi="fa-IR"/>
</w:rPr>
```

English runs inside Persian paragraphs should use `w:rtl=0`, an LTR font, and
`en-US`. Never reverse English strings manually. Preserve a visible separator
at Persian/Latin boundaries: a space belongs in one of the adjacent runs and
must still render between them in Word. Reject visually joined output such as
`SAPنام`, `Systemسامانه`, and `FioriوHANA` even when the extracted text appears
correct.

### Combining hamza and Persian ezafe

Never create a run whose first character is a combining mark. A base letter and
its combining mark must share one run, one font, one language, and one direction.
The sequence `U+0647 U+0654` (`ه` plus combining hamza above) can show a dotted
circle after Word splits the grapheme across runs or applies different fonts.
Keep the pair in one Persian run with identical font, language, and direction.
Do not silently replace it with `U+06C0` (`ۀ`): that code point is not the NFC
equivalent of `U+0647 U+0654` and changes the underlying letter. An orthographic
substitution requires explicit user approval. Audit the XML for run-leading
combining marks and inspect every ezafe occurrence in the actual Word render;
search/extraction cannot prove glyph attachment.

## 3. Styles and inheritance

Set direction/font on `Normal`, `Heading 1..3`, and list styles. Also set direct
paragraph properties on fragile deliverables. Direct formatting protects
against template and locale differences; styles keep Word's UI and newly
inserted paragraphs consistent.

## 4. Lists and indents

For an RTL list, remove `left`, `start`, and `end` inherited values and use:

```xml
<w:ind w:right="360" w:hanging="180"/>
<w:mirrorIndents w:val="1"/>
```

Tune values to the document. Wrapped lines must align under item text. Use real
`w:numPr` numbering for editable lists; manual numbers are acceptable only for
static headings/TOCs with deliberate bidi controls.

## 5. Story parts

The body audit does not cover headers and footers. Inspect:

- `word/document.xml`
- `word/header*.xml`, `word/footer*.xml`
- `word/footnotes.xml`, `word/endnotes.xml`
- `word/comments.xml`
- paragraphs nested in `w:txbxContent`, tables, SDTs, hyperlinks, and drawings

## 6. Mixed-language text

Keep the paragraph RTL and physically right-aligned whenever it contains any
Persian. Split Persian and English into separate runs and mark each direction.
Use RLM/LRM or Unicode
isolates only when run boundaries do not resolve punctuation/number placement.
Do not scatter invisible controls without an audit; they can pollute headings,
TOCs, search, copying, and accessibility.

Persian heading contract:

```text
۳.۲ - عنوان فارسی با BPMN
```

The number is logically first and visually rightmost. The English token remains
an LTR run.

## 7. Tables, headers, footers, and cover pages

Classify every table paragraph by its actual text instead of inheriting one
alignment for the whole table:

- Header cells: set both vertical cell alignment and every nonempty header
  paragraph's horizontal alignment to center. This applies to Persian, Latin,
  numeric, and mixed headers. Persian/mixed headers remain `w:bidi=1`; pure
  Latin headers remain `w:bidi=0`. The mandatory `w:jc=center` is a role-based
  exception to the ordinary Persian right-alignment rule.
- Any Persian/Arabic text: `w:bidi=1`, `w:jc=right`.
- Pure Latin/English, URL, code, numeric, or mathematical content:
  `w:bidi=0`, `w:jc=left`.

The two rules immediately above are mandatory for every nonempty table-body
paragraph below the first row. Table-body centering is a release failure; the
center exception belongs only to the first/header row.

For a mixed-language paragraph, the presence of Persian makes the paragraph
directly RTL/right-aligned; keep its Latin fragments in explicit LTR runs.
Apply this to headers, footers, page-number labels, captions, headings, and
table-body rows. In the first/header row, keep the same language-appropriate
bidi direction but apply the mandatory horizontal `center` role.

In any deliverable designated Persian or Persian/English, add this property to
every table so semantic cell 1 displays at the far right. Do not infer a silent
per-table exemption merely because one table happens to contain only Latin
text. LTR-only documents use the separate LTR policy:

```xml
<w:tblPr>
  <w:bidiVisual w:val="1"/>
</w:tblPr>
```

Keep semantic column 1 as XML cell 1 in every row. In Word it must appear at the
far right; subsequent columns proceed leftward and the final semantic column is
far left. Do not manually reverse only one row, header labels, or extracted
data. Validate every table, not only the first or a sample. Use Word's physical
horizontal positions to prove that logical header cell 1 is rightmost, each
subsequent logical header cell is farther left, and the final cell is leftmost;
then inspect a complete header/data row in the Word render to confirm that data
still belongs to the correct header. Set table outer and inner borders explicitly to
`D9D9D9` unless the user supplies another design.

For book, manual, and reference-guide deliverables with a dedicated cover,
reserve page 1 for the centered overall title in `B Titr` or `B Titr Bold`.
Start TOC/front matter/body content on page 2, using a real page or section
break. Recheck the page-1/page-2 transition and do not let `cantSplit` on long
table rows create large empty areas; allow data rows to split when necessary.

## 8. Compatibility hazards

- LibreOffice, Google Docs, PDF converters, and Word may resolve bidi
  inheritance differently.
- `python-docx` paragraph `.text` can omit text nested in hyperlinks, fields,
  SDTs, or other XML structures. Use `.//w:t`.
- Dynamic TOCs can be rebuilt by Word and lose custom visual ordering. Decide
  whether the TOC must remain dynamic or be materialized/static.
- Fonts absent on the target machine will substitute and change pagination.
- A right-aligned long line naturally begins far from the right edge; judge its
  ending edge and paragraph mark, not only its first visible glyph.
- A table can have right-aligned cells while its columns still display LTR;
  `w:jc=right` does not replace `w:bidiVisual=1`.
- A document can pass XML bidi checks yet fail Word visually because a combining
  mark starts a run, styles override direct intent, or field updates repaginate
  the file. Treat the Word render as the decisive target-engine evidence.
