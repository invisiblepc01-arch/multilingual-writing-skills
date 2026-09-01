# Build Bilingual DOCX

[راهنمای فارسی](README.fa.md) · [Installation guide](INSTALLATION.md) ·
[راهنمای نصب فارسی](INSTALLATION.fa.md)

`build-bilingual-docx` is an open Agent Skill for creating, repairing, and
validating Microsoft Word documents that contain:

- Persian/Farsi right-to-left text;
- English left-to-right text;
- mixed Persian and English runs;
- numbered RTL headings and lists;
- Persian tables of contents;
- headers, footers, tables, captions, and diagrams;
- layouts that must remain stable in Word 2016–2024.

The skill combines reusable instructions, detailed OOXML references, and
deterministic Python utilities. It follows the open Agent Skills directory
format and can be used by Codex, ChatGPT surfaces that support standalone
skills, or other AI agents that can read files and run Python.

## Why this exists

Setting a paragraph to “right aligned” is not enough for Persian Word
documents. Reliable output also requires explicit paragraph bidi direction,
run direction, complex-script language and font properties, correct RTL list
indents, and separate processing of headers and footers. Different renderers
may hide these defects until the file is opened in Microsoft Word.

This project makes those requirements explicit and testable.

## Repository contents

```text
.
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── ooxml-bidi.md
│   ├── portability.md
│   ├── qa-matrix.md
│   ├── toc-and-numbering.md
│   └── word-roundtrip.md
├── scripts/
│   ├── audit_docx_bidi.py
│   ├── audit_docx_run_props.py
│   ├── harden_docx_bidi.py
│   ├── make_bidi_fixture.py
│   └── smoke_test.py
├── tests/test_workflow.py
├── INSTALLATION.md
└── INSTALLATION.fa.md
```

## Quick installation

Clone or download this repository. Put the repository folder in your personal
skills directory:

```text
Windows: %USERPROFILE%\.codex\skills\build-bilingual-docx
macOS/Linux: $HOME/.codex/skills/build-bilingual-docx
```

The final path must contain `SKILL.md` directly:

```text
.../build-bilingual-docx/SKILL.md
```

Restart Codex if the skill does not appear. See [INSTALLATION.md](INSTALLATION.md)
for complete instructions and compatibility paths.

## Quick use

Explicit invocation:

```text
Use $build-bilingual-docx to create a production-ready Persian DOCX with
numbered headings, an RTL table of contents, and Word-compatible headers.
```

Implicit invocation is enabled by default, so a request such as the following
should also match the skill:

```text
Create a properly formatted Persian and English Word document from these notes.
```

## Command-line tools

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create an adversarial bilingual fixture:

```bash
python scripts/make_bidi_fixture.py fixture_raw.docx
```

Harden its paragraph and run directions:

```bash
python scripts/harden_docx_bidi.py fixture_raw.docx fixture_hardened.docx --mode auto
```

Audit the result:

```bash
python scripts/audit_docx_bidi.py fixture_hardened.docx --json fixture_audit.json
python scripts/audit_docx_run_props.py fixture_hardened.docx --report fixture_run_audit.json
```

A successful audit exits with code `0` and reports:

```json
{
  "passed": true,
  "errors": []
}
```

Run the complete isolated smoke test:

```bash
python scripts/smoke_test.py
```

## Validation policy

Structural OOXML validation is necessary but not sufficient. A document must
also be rendered and inspected in its target engine. Do not claim that a file
is “Word 2024 verified” unless the final DOCX was actually opened or rendered
by Word 2024 and every page was reviewed. Follow the post-Word hardening and
read-only verification sequence in [word-roundtrip.md](references/word-roundtrip.md)
so a later Word save cannot silently invalidate the evidence.

## Supported environments

- Python 3.10+
- `python-docx`
- `lxml`
- Microsoft Word for authoritative Word fidelity
- LibreOffice as a secondary/fallback renderer

The skill instructions remain useful without Python, but its deterministic
repair and audit scripts will not run.

## Contributing

Issues and pull requests are welcome. Include a minimal DOCX fixture or a clear
description of the renderer, Word version, installed fonts, and observed bidi
failure. Never commit confidential source documents.

## License

MIT License. See [LICENSE](LICENSE).
