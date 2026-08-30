---
name: multilingual-chat-writing
description: Write, revise, translate, and display Persian/Farsi, English, or mixed-language content directly in ChatGPT or Codex chat. Use for RTL/LTR prose, mixed technical terms, lists, process arrows, Solar Hijri dates, formulas, code blocks, URLs, and tables whose visual order matters; do not use for DOCX generation or document rendering.
---

# Multilingual chat writing

Use this skill only for content displayed directly in ChatGPT or Codex. Keep it
independent from `build-bilingual-docx`, which owns DOCX authoring and file QA.

## Core outcome

- Detect the dominant language, intended audience, and requested level of
  formality before drafting. Match the user's terminology and assumed
  knowledge without silently changing the register.
- Preserve the semantic word order the user intended; never rewrite source
  order merely to compensate for bidirectional rendering.
- Keep Persian prose RTL and English terms, acronyms, code, URLs, file paths,
  identifiers, versions, dates inside filenames, and formulas internally LTR.
- Preserve the spelling, capitalization, product names, identifiers, and
  technical vocabulary supplied by the user. Do not translate, transliterate,
  expand, or normalize them unless requested or needed to correct a stated
  error.
- Do not invent claims, sources, citations, quotations, translations, or
  factual details. Keep supplied quotations and source attributions faithful.
- Choose formatting based on the target renderer, not on how the Markdown
  source looks. Inspect the rendered result when direction or alignment is
  consequential.

## Ordinary prose and lists

- Lead with the answer and use short RTL-compatible Persian paragraphs.
- Use meaningful headings only when they improve navigation. Keep a heading's
  Persian/English order, numbering, punctuation, and technical atoms stable.
- Preserve the user's choice of Persian or ASCII digits and Persian or English
  punctuation unless consistency or a requested house style requires a
  change. Treat mixed dates, decimals, units, and version numbers as atoms.
- A Persian sentence that starts with an LTR atom such as `URL`, `API`, a
  number, or a formula needs an RTL anchor. Prefer a visible Persian label when
  it does not change the requested wording. When the wording must begin with
  the LTR atom, prepend `RLM` and isolate each LTR atom with `LRI`/`PDI`.
- Markdown bullet lists may be placed in an LTR container by the host. When
  right alignment matters, replace `-` bullets with separate Persian
  paragraphs headed by visible labels such as `قاعدهٔ اول:`.
- Do not use a fenced code block merely to stabilize an ordinary Persian
  sentence; code blocks are LTR containers.

## Quotes, links, and citations

- Keep opening and closing quotation marks, parentheses, brackets, colons, and
  sentence-final punctuation attached to the intended RTL or LTR phrase.
- Preserve quoted wording exactly unless the user requests editing. Use a
  block quote only when the host renders its Persian direction readably;
  otherwise use a labeled Persian paragraph.
- Keep a URL as one LTR atom. In a Markdown link, preserve the visible label's
  language and the target URL separately; never reorder query characters such
  as `?`, `&`, `=`, or `#`.
- Place each citation immediately after the claim it supports. Keep English
  titles and identifiers LTR without forcing the surrounding Persian sentence
  to become LTR.

## Processes and arrows

- Write stages in semantic first-to-last order and put `←` between consecutive
  stages. In an RTL Persian chain, the first stage is the rightmost stage.
- Use the same arrow for progress, cause/effect, timelines, dependencies,
  branches, and retry loops.
- Add a trailing `←` only when the displayed line continues into later stages
  or branches; never leave one after a completed final stage.
- For a decision, show the shared path once and end it with a trailing `←`.
  Put each branch on its own RTL paragraph with a visible Persian condition
  label. Repeat the decision stage at the start of a branch only when needed to
  make the branch independently understandable.
- Keep each branch in first-to-last semantic order. Name any retry, return, or
  merge explicitly in Persian; never imply a return by reversing an arrow.
- When branches merge, show the common merge stage after each branch or add a
  separate labeled merge paragraph. Do not flatten mutually exclusive paths
  into one linear chain.
- Keep mixed process chains as ordinary RTL paragraphs when the first stage
  must appear at the right. Do not move such a chain into an LTR code block.
- Avoid nested Markdown backticks around LTR terms inside an outer inline-code
  span. If backticks or arrows render ambiguously, use one plain fenced-text
  line without inner backticks, or render a controlled visual.

## Code blocks

- Code, commands, paths, URLs, and formulas may remain LTR and left-aligned.
- When a Persian or Persian-dominant sentence must appear inside an LTR code
  block, preserve left alignment with an initial `LRM`; embed the sentence with
  `RLE`/`PDF`; and isolate each LTR atom with `LRI`/`PDI`.
- These controls affect presentation only. Keep the logical source words in
  their true semantic order and never use `RLO` or `LRO`.

## Persian and mixed tables

- In a Persian table, column one is the rightmost column. Prefer it for row
  numbering, followed by the remaining columns from right to left.
- A Markdown renderer displays source columns left to right, so author source
  columns in reverse display order when necessary. Ensure every header remains
  above the data belonging to that column.
- Do not rely on Markdown alignment markers, invisible controls, inline code,
  or raw HTML for pixel-accurate RTL table alignment in ChatGPT/Codex. Host CSS
  may style headers and cells differently, and raw HTML may be escaped.
- When exact alignment matters, render a controlled RTL table with explicit
  direction, fixed column order, identical header/cell alignment, and isolated
  LTR spans. Inspect a screenshot before delivery and display the verified
  image. Keep a textual or vertical alternative when copyability is required.

## Dates, formulas, and technical atoms

- Preserve a Solar Hijri date in `YYYY/MM/DD` order as one atom, preferably
  isolated in mixed prose, for example `۱۴۰۵/۰۶/۱۵`.
- Preserve ASCII dates inside LTR filenames, such as
  `daily-report-1405-06-15.pdf`.
- Put substantial formulas in an LTR block. Do not reorder operators,
  parentheses, variables, units, decimal points, or comparison signs.

## Conditional reference

Read [references/rtl-rendering-patterns.md](references/rtl-rendering-patterns.md)
before handling any sentence beginning with an LTR atom, Persian text inside a
code block, arrow chain, or Persian/mixed table whose alignment is important.

## Release check

Before sending a direction-sensitive response:

1. Confirm semantic first-to-last word and stage order.
2. Confirm Persian text reads RTL and each technical atom remains internally
   LTR without character reversal.
3. Confirm arrows, punctuation, quotes, parentheses, dates, and formulas remain
   attached to the intended content.
4. Confirm Persian lists and sensitive tables are aligned in the rendered
   surface, not merely in Markdown source.
5. Confirm tone, terminology, quotations, links, citations, numeral style, and
   factual content still match the user's request and sources.
6. If the host rendering remains ambiguous, switch to a vertical structure or
   a controlled, screenshot-verified visual rather than guessing.
