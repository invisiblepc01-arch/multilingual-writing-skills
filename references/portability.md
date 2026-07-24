# Cross-engine portability

This bundle is instruction- and script-based. It can be used by any AI system
that can read files and run Python. `agents/openai.yaml` is optional UI metadata
for OpenAI products; other engines should ignore it and load `SKILL.md`.

Minimum runtime:

- Python 3.10+
- `python-docx`
- `lxml`
- Microsoft Word for authoritative Word rendering, or LibreOffice for fallback

Equivalent agent procedure:

1. Load `SKILL.md`.
2. Load only references relevant to the request.
3. Run bundled scripts from a writable working directory.
4. Never modify a source file in place without a backup.
5. Run the audit and visual release gates.

Tool mappings:

- Shell tool: run Python scripts and renderers.
- File patch/editor: modify scripts or configuration deterministically.
- Image viewer: inspect rendered page PNGs at 100%.
- Desktop/computer-control tool: open the final DOCX in the target Word version.

An AI without file execution or visual inspection can draft content but cannot
truthfully certify DOCX fidelity. It should return instructions or an
unverified artifact with the limitation stated.
