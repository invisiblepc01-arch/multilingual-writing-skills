# Multilingual Chat Writing

An independent, mandatory response-layer Agent Skill for writing and displaying
Persian, English, and mixed-language content directly in ChatGPT or Codex. It
co-invokes with any primary task Skill whenever a visible chat message contains
Persian, while leaving every file and artifact under the primary Skill's sole
ownership. It covers direction-safe
prose, LTR technical atoms, Persian process arrows, code blocks, Solar Hijri
dates, formulas, lists, headings, quotations, links, citations, tone fidelity,
and visually verified RTL tables.

This Skill is intentionally separate from the repository's root
`build-bilingual-docx` Skill, which alone handles Microsoft Word files. The two
can run at the same time without sharing responsibilities: one owns DOCX work;
this one owns only the text displayed in chat.

## Installation

Copy this directory to the personal skills directory so that `SKILL.md` is at:

```text
%USERPROFILE%\.codex\skills\multilingual-chat-writing\SKILL.md
```

Implicit invocation is enabled. Ordinary Persian, English, or mixed-language
chat-writing requests can activate it without an explicit `$` invocation. In
addition, every visible assistant message that contains Persian must apply it
as the chat-only response layer, even when another Skill owns the task.
