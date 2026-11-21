# Multilingual Writing Skills for AI Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-2-blue)](https://agents.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![Word](https://img.shields.io/badge/Microsoft%20Word-2016--2024-2B579A)](references/word-roundtrip.md)
[![RTL](https://img.shields.io/badge/Persian-RTL-2ea44f)](README.fa.md)

[راهنمای فارسی](README.fa.md) · [Installation](INSTALLATION.md) · [نصب فارسی](INSTALLATION.fa.md)

Two production-grade **Agent Skills** that keep Persian/Farsi (RTL) and English
(LTR) content correct in the two places where mixed direction normally breaks:

| Skill | Where it applies | What it adds |
|---|---|---|
| `build-bilingual-docx` | Microsoft Word files | Explicit paragraph/run bidi, complex-script fonts, RTL lists, tables, TOC, headers, page fields |
| `multilingual-chat-writing` | AI chat surfaces | Persian-first anchors, LTR-atom isolation, arrow chains, RTL tables, host bidi capability test |

Both follow the open **Agent Skills** directory format (`<name>/SKILL.md`), so
they work with DeepSeek Harness, Codex, ChatGPT surfaces that load standalone
skills, and any agent that can read files and run Python.

## Why this exists

Setting a paragraph to "right aligned" is not enough for Persian documents.
Reliable output also needs explicit `w:bidi`, run direction, `w:cs` font slots,
`w:bCs` on bold Persian runs, RTL list indents, and separate processing of
headers, footers and tables. Word can silently fix or break each of these on
save, so the only trustworthy gate is a render audit in the target engine.

Chat is a different failure mode: many hosts set no `direction` at all, so a
Persian paragraph renders left-aligned and mixed sentences wrap in the wrong
visual order. Invisible Unicode controls alone cannot repair block alignment;
that requires a host rule (`unicode-bidi: plaintext` or `dir="auto"`). The
skill ships the detection test and the exact fix.

## Install in three steps

1. Copy each skill folder into your agent's skills directory:

```text
Windows:     %USERPROFILE%\.agents\skills\build-bilingual-docx
             %USERPROFILE%\.agents\skills\multilingual-chat-writing
macOS/Linux: $HOME/.agents/skills/build-bilingual-docx
             $HOME/.agents/skills/multilingual-chat-writing
```

2. Each final folder must contain `SKILL.md` directly.
3. Restart the agent if the skills do not appear.

Codex users can use `~/.codex/skills/` instead. See
[INSTALLATION.md](INSTALLATION.md) for every supported path.

## Quick start

Ask for a document, or name the skill explicitly:

```text
Use $build-bilingual-docx to create a production-ready Persian DOCX with
numbered headings, an RTL table of contents, and Word-compatible headers.
```

For chat output, no explicit call is needed: the chat skill applies to every
Persian message. When a host renders left-aligned despite Persian-first text,
the skill tells the agent to test the host and fix the direction rule.

## Deterministic tooling

The DOCX skill is not just prose. It ships runnable gates:

```bash
python scripts/make_bidi_fixture.py fixture_raw.docx
python scripts/harden_docx_bidi.py fixture_raw.docx fixture_hardened.docx --mode auto
python scripts/audit_docx_bidi.py fixture_hardened.docx --json audit.json
python scripts/audit_docx_run_props.py fixture_hardened.docx --report run_audit.json
python scripts/smoke_test.py
```

With Microsoft Word installed, two COM audits prove what XML cannot:

```powershell
powershell -File scripts/audit_word_table_order.ps1 -Docx file.docx -Report order.json
powershell -File scripts/audit_word_effective_alignment.ps1 -Docx file.docx -Report align.json -BodyAlignment justify
```

The table audit fails unless logical column 1 is physically rightmost and the
last column is leftmost in **every** table. The alignment audit checks Reading
Order and Alignment together on the exact file hash.

## Verified quality

- Word 16 COM audits: table order and effective alignment, zero failures.
- Structural audits: paragraph and run direction, fonts, fields, tables.
- Isolated smoke test: fixture generation, hardening, right and Justify modes.
- Host bidi lab: headless-browser screenshots compared by measured line bounds.

Structural validation is necessary but never sufficient; every release claim
names the engine and scope that actually rendered the file.

## Compatibility

| Environment | Status |
|---|---|
| Microsoft Word 2016, 2019, 2021, 2024 | Primary, verified target |
| LibreOffice | Fallback, disclosed when used |
| Python 3.10+ with `python-docx`, `lxml` | Required for scripts |
| DeepSeek Harness, Codex, ChatGPT skills | Supported layout |
| Windows PowerShell 5.1 / 7 | Word COM audits |

## Repository layout

```text
.
├── SKILL.md                     # build-bilingual-docx instructions
├── multilingual-chat-writing/
│   ├── SKILL.md                 # chat response-layer rules
│   └── references/              # rendering patterns and QA matrix
├── agents/openai.yaml
├── references/                  # OOXML, TOC, roundtrip, portability, QA
├── scripts/                     # harden, audit, fixture, smoke test
├── tests/
├── INSTALLATION.md / .fa.md
└── README.md / README.fa.md
```

## Contributing

Issues and pull requests are welcome. A useful report includes the renderer,
Word version, installed fonts, and a minimal DOCX fixture that shows the bidi
failure. Never commit confidential source documents.

## License

MIT License. See [LICENSE](LICENSE).
