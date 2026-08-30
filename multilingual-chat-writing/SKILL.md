---
name: multilingual-chat-writing
description: Write, revise, translate, and display Persian/Farsi, English, or mixed-language content directly in ChatGPT or Codex. Apply it as a mandatory response layer to every user-visible message containing Persian, including commentary, progress, questions, and final answers, alongside any primary task skill—even for DOCX, code, data, artifact, or skill-development work. It governs only direct-chat wording and RTL/LTR rendering; it must never author, edit, render, validate, or otherwise modify a user's DOCX, another user artifact, or another skill.
---

# Multilingual chat writing

## Response-layer scope and co-invocation

Use this skill for every assistant-authored message containing Persian/Farsi
that is displayed directly in ChatGPT or Codex. This includes commentary,
progress updates, clarifying questions, summaries, and final answers, even
when the primary task is owned by another skill.

Treat this skill as a mandatory response-layer companion. The primary domain
skill owns facts, actions, files, artifacts, and domain-specific decisions;
this skill owns only the wording and RTL/LTR rendering of the visible chat
response.

A statement that another skill or directory is read-only, closed, or outside
the editing scope does not prohibit read-only invocation of this skill for chat
rendering. Do not interpret “do not edit `multilingual-chat-writing`” as “do
not apply `multilingual-chat-writing` to the response.”

Never use this skill to author, revise, format, render, validate, or change
content inside a DOCX or another user artifact. Never modify, merge, copy, or
reinterpret files or instructions belonging to another skill. Co-invocation
does not transfer artifact ownership to this skill. In particular,
`build-bilingual-docx` remains the sole owner of DOCX authoring and file QA.
Temporary visual QA of chat rendering is permitted. If the user deliverable
itself must be an image or another artifact, delegate its creation and artifact
validation to the appropriate primary or visual skill; this skill only selects
and words the direction-safe chat representation.

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
- For every assistant-authored Persian-dominant paragraph, heading, status
  line, caption, and labeled link line, the first strong visible directional
  character after Markdown syntax must be Persian/Arabic. This is a hard
  pre-send invariant. Start with a visible Persian anchor such as
  `ثبت نهایی:`, `گفت‌وگوی مقصد:`, or `نام فایل:` before any English term,
  ASCII number, inline code, Markdown link, filename, icon, emoji, or quoted
  LTR name.
- A Persian word later in the line does not repair an LTR paragraph base.
  Never write mixed labels such as `Commit نهایی:` or start a Persian report
  line with `Task`, `GitHub`, `URL`, a commit hash, or a Markdown link. Rewrite
  them as Persian-first labels such as `ثبت نهایی در Git:` and
  `اعمال در گفت‌وگوی دیگر:`. Neutral opening punctuation such as quotes or
  parentheses is not an RTL anchor.
- Exception: when exact user-supplied wording must visibly begin with an LTR
  atom, preserve that semantic order and use the validated `RLM` plus
  `LRI`/`PDI` construction from the reference. Do not add a Persian label if it
  would change the requested wording. This exception requires rendered QA; it
  does not apply to assistant-authored status labels that can be rewritten.
- Use meaningful headings only when they improve navigation. Keep a heading's
  Persian/English order, numbering, punctuation, and technical atoms stable.
- Preserve the user's choice of Persian or ASCII digits and Persian or English
  punctuation unless consistency or a requested house style requires a
  change. Treat mixed dates, decimals, units, and version numbers as atoms.
- A Persian sentence that starts with an LTR atom such as `URL`, `API`, a
  number, or a formula needs an RTL anchor. Prefer a visible Persian label when
  it does not change the requested wording. When the wording must begin with
  the LTR atom, prepend `RLM` and isolate each LTR atom with `LRI`/`PDI`.
- Treat any Persian sentence containing an LTR atom as direction-sensitive,
  not only sentences that start with one. Isolate every LTR atom when a
  sentence contains multiple LTR atoms, punctuation around them, probable
  line wrapping, or an LTR atom followed by a Persian tail or final verb.
  Inline-code styling may preserve an atom's internal order, but it does not
  establish the paragraph's RTL base direction.
- `RLM` establishes an RTL anchor only in an auto-directed or already RTL
  paragraph; it cannot override a host block whose CSS explicitly sets
  `direction: ltr`. If inspection shows reversed continuation-line order in an
  explicitly LTR container, use a whole-sentence RTL embedding/isolate as
  defined in the reference, split the content into shorter labeled Persian
  paragraphs, or use a controlled RTL render.
- Do not use Markdown `-`, `*`, or `+` bullets—or native Markdown numbering—
  for Persian-dominant lists by default. The host can keep the list container,
  indentation, and generated `::marker` LTR even when each item begins with
  Persian. This applies to top-level and nested lists.
- Replace Persian Markdown lists with separate RTL-compatible paragraphs
  headed by visible Persian labels such as `نتیجهٔ اول:`, `مرحلهٔ دوم:`, or
  `علت:`. This is the default, not merely a fallback when the user has already
  reported a defect.
- If visible bullets are explicitly required, use a literal `•` inside each
  RTL paragraph only after rendered inspection. If exact bullet placement or
  nesting is required, select a controlled, screenshot-verified visual plus a
  copyable labeled-paragraph alternative. Any deliverable visual is created
  and validated by the appropriate primary or visual skill.
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
  LTR spans through the appropriate primary or visual skill. Inspect a
  screenshot before delivery and display the verified image. Keep a textual or
  vertical alternative when copyability is required.

## Dates, formulas, and technical atoms

- Preserve a Solar Hijri date in `YYYY/MM/DD` order as one atom, preferably
  isolated in mixed prose, for example `۱۴۰۵/۰۶/۱۵`.
- Preserve ASCII dates inside LTR filenames, such as
  `daily-report-1405-06-15.pdf`.
- Put substantial formulas in an LTR block. Do not reorder operators,
  parentheses, variables, units, decimal points, or comparison signs.

## Conditional reference

Read [references/rtl-rendering-patterns.md](references/rtl-rendering-patterns.md)
before handling any Persian list, any sentence containing an LTR atom, Persian
text inside a code block, arrow chain, or Persian/mixed table whose alignment
is important. Use
[references/adversarial-qa-matrix.md](references/adversarial-qa-matrix.md)
for regression testing after changing this skill or after a reported visual
defect.

## Per-message invocation gate

Before sending any commentary or final response, check whether the visible
message contains Persian/Farsi. If it does, apply this skill's rendering rules
to that message regardless of which primary skill owns the task.

For a Persian-dominant response, scan every proposed Markdown list before
sending. Convert it to labeled Persian paragraphs unless right-side markers
and RTL wrapping have been verified in the actual host. Then inspect mixed
sentences containing inline code, two or more LTR atoms, or an LTR atom near a
Persian sentence-final verb. Finally, perform a first-strong-character audit
on every non-code paragraph, heading, caption, and standalone link/status line.
If its first strong character is LTR, either add a visible Persian-first anchor
or apply the exact-wording exception and visually verify it.

## Release check

Before sending a direction-sensitive response:

1. Confirm semantic first-to-last word and stage order.
2. Confirm every Persian-dominant non-code block begins with a strong Persian
   character before any LTR atom, link, code span, number, icon, or neutral
   punctuation, unless the validated exact-wording exception applies.
3. Confirm Persian text reads RTL and each technical atom remains internally
   LTR without character reversal.
4. Confirm arrows, punctuation, quotes, parentheses, dates, and formulas remain
   attached to the intended content.
5. Confirm Persian lists and sensitive tables are aligned in the rendered
   surface, not merely in Markdown source.
6. Confirm tone, terminology, quotations, links, citations, numeral style, and
   factual content still match the user's request and sources.
7. Check both normal and narrow viewport widths when wrapping could occur.
   A correct logical source that fails after line wrapping is a rendering
   failure.
8. If the host rendering remains ambiguous, switch to a vertical structure or
   a controlled, screenshot-verified visual rather than guessing.
