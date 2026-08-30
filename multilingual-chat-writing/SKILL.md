---
name: multilingual-chat-writing
description: Write, revise, translate, and display Persian/Farsi, English, or mixed-language content directly in ChatGPT or Codex chat. Use for readable RTL/LTR prose, mixed inline text, lists, headings, tables, citations, and process descriptions; do not use for DOCX file generation or document rendering.
---

# Multilingual chat writing

Use this skill only for content that will be displayed directly in chat. Keep
it independent from `build-bilingual-docx`, which owns DOCX authoring and file
rendering.

## Language and direction

- Detect the dominant language and audience before drafting.
- Write Persian prose naturally in RTL-compatible text; keep English terms,
  code, URLs, file paths, identifiers, and numbers in their natural LTR form.
- For mixed sentences, preserve the original spelling and order of each term;
  do not reverse characters or transliterate unless requested.
- Use Persian punctuation and digits only when the user requests them or the
  surrounding text clearly follows that convention.

## Structure and display

- Lead with the answer or finished text.
- Use short paragraphs and meaningful headings. Use Markdown lists and tables
  only when they improve readability.
- Put code, commands, URLs, and file paths in fenced code or inline code so
  they remain LTR and copyable.
- For Persian process flows, timelines, arrows, and cause/effect chains, write
  the sequence in an RTL-safe form; keep technical identifiers isolated from
  directional punctuation.
- Preserve the requested voice, register, and terminology. Do not add claims,
  citations, or translations that were not requested.

## Mixed-language quality checks

Before responding, check that:

1. Persian sentences read naturally from right to left.
2. English names, acronyms, URLs, numbers, and code are not character-reversed.
3. Markdown markers, bullets, parentheses, quotes, and punctuation remain
   attached to the intended text.
4. The response is directly usable in ChatGPT/Codex without DOCX-only XML or
   rendering instructions.

When the user asks for a DOCX, stop using this skill for the deliverable and
route the request to `build-bilingual-docx`.
