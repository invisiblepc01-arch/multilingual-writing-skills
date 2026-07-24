# Persian TOC and heading numbering

## Heading contract

- Use hierarchical meaningful numbers: `۱`, `۱.۱`, `۱.۱.۱`.
- Put the number at the visual far right.
- Follow it with one space or ` - `, then the title.
- Set the whole paragraph to `w:bidi=1` and `w:jc=right`.
- Split English title spans into LTR runs.

## Dynamic TOC

Use real Heading styles and a real TOC field when users must update it. Test an
actual Word field update. Word-generated RTL TOCs may vary by locale/template;
customize `TOC 1..3` styles, right tabs, leaders, and bidi properties.

## Static TOC

Use when visual stability is more important than automatic updating. A robust
three-column table can encode:

1. page number at far left;
2. dot leader in the middle;
3. numbered RTL title at far right.

Use fixed DXA widths, explicit cell widths, no autofit, zero paragraph spacing,
and a compact font. Keep page and leader cells LTR/centered and title cells
RTL/right. Do not use typed spaces to align columns.

## Release checks

- Every required heading is present once.
- Heading text and TOC text match after removing intentional direction marks.
- Page numbers are current.
- Leaders fill but do not wrap.
- Long entries wrap under title text and never under the page number.
- TOC rows do not split unexpectedly across pages.
