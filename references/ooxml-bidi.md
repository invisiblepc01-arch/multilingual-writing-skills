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

For Persian:

```xml
<w:pPr>
  <w:jc w:val="right"/>
  <w:bidi w:val="1"/>
</w:pPr>
```

`w:bidi` controls paragraph reading order. `w:jc` controls physical alignment.
Neither substitutes for the other. “Right justify” in user language usually
means `right`, not Word's full-width `both`; confirm if ambiguous.

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
`en-US`. Never reverse English strings manually.

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

Keep the paragraph RTL when its semantic language is Persian. Split Persian and
English into separate runs and mark each direction. Use RLM/LRM or Unicode
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

- Header cells: `w:jc=center`; set vertical cell alignment to center.
- Any Persian/Arabic text: `w:bidi=1`, `w:jc=right`.
- Pure Latin/English, URL, code, numeric, or mathematical content:
  `w:bidi=0`, `w:jc=left`.

For a mixed-language paragraph, the presence of Persian makes the paragraph
RTL/right-aligned; keep its Latin fragments in explicit LTR runs. Center any
header or footer that contains Persian, even when it also contains Latin text
or a page-number field. Keep Persian body headings right-aligned.

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
