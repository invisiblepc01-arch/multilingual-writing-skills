# Installation and migration guide

## 1. Download

Use one of these methods:

- Download the repository ZIP from GitHub and extract it.
- Clone it:

```bash
git clone https://github.com/invisiblepc01-arch/build-bilingual-docx.git
```

The extracted folder must contain `SKILL.md` directly. Avoid an accidental
double folder such as:

```text
build-bilingual-docx/build-bilingual-docx/SKILL.md
```

## 2. Install for your user

### Windows

Preferred current user location:

```text
%USERPROFILE%\.codex\skills\build-bilingual-docx
```

PowerShell:

```powershell
$source = (Resolve-Path ".\build-bilingual-docx").Path
$root = Join-Path $env:USERPROFILE ".codex\skills"
New-Item -ItemType Directory -Force -Path $root | Out-Null
Copy-Item -LiteralPath $source -Destination $root -Recurse
```

Other Agent Skills-compatible engines may discover personal skills under:

```text
%USERPROFILE%\.agents\skills\build-bilingual-docx
```

Use only one location to avoid duplicate entries.

### macOS and Linux

```bash
mkdir -p "$HOME/.codex/skills"
cp -R "/path/to/build-bilingual-docx" "$HOME/.codex/skills/"
```

Compatibility location for other Agent Skills-compatible engines:

```text
$HOME/.agents/skills/build-bilingual-docx
```

Again, install only one copy.

## 3. Restart and verify discovery

1. Fully close ChatGPT Desktop/Codex.
2. Start it again and open a new task.
3. Open **Skills** in the desktop sidebar, or run `/skills` in Codex CLI/IDE.
4. Look for `build-bilingual-docx`.

Codex normally detects skill changes automatically. Restart if it does not
appear.

## 4. Test invocation

Explicit:

```text
Use $build-bilingual-docx to create a Persian-English DOCX with correct RTL/LTR
formatting and run the included audit.
```

Implicit:

```text
Create a reliable Persian Word document from this content.
```

Implicit matching is enabled by default. If `agents/openai.yaml` contains
`allow_implicit_invocation: false`, change it to `true` or remove that policy.

## 5. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

For an isolated environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 6. Run the self-test

```bash
python scripts/make_bidi_fixture.py fixture_raw.docx
python scripts/harden_docx_bidi.py fixture_raw.docx fixture_hardened.docx --mode auto
python scripts/audit_docx_bidi.py fixture_hardened.docx --json fixture_audit.json
python scripts/audit_docx_run_props.py fixture_hardened.docx --report fixture_run_audit.json
python scripts/smoke_test.py
```

Open `fixture_hardened.docx` in Microsoft Word and verify:

- Persian headings and numbers are anchored on the right;
- Persian body text is RTL and right aligned;
- English tokens are not reversed;
- list markers appear on the right;
- headers are right anchored;
- tables and footers remain readable.

## 7. Troubleshooting

### Skill does not appear

- Confirm `SKILL.md` is directly inside the skill folder.
- Remove accidental nested duplicate folders.
- Check the user skill path.
- Restart Codex.
- Confirm the skill is not disabled in `~/.codex/config.toml`.

### Skill appears twice

Remove one duplicate installation from `.agents/skills`, `.codex/skills`, or a
repository `.agents/skills` directory.

### Python import error

```bash
python -m pip install python-docx lxml
```

### Word layout differs on another machine

Install the same fonts, check the Word version and Office language settings,
and update fields only when intended. Always validate with the target Word
engine.

## 8. Use with another AI engine

If the engine does not support Agent Skills directly:

1. Give it `SKILL.md` as persistent project/system instructions.
2. Make `references/` and `scripts/` available.
3. Allow it to read files and run Python.
4. Require the audit after generation.
5. Require visual inspection in the target Word version.

An engine without file execution or visual inspection cannot honestly certify
Word fidelity.

## 9. Update or remove

To update, close Codex and replace the whole skill folder with the new version.
Do not merge old and new files unless you have reviewed the differences.

To remove, close Codex and delete/move the installed `build-bilingual-docx`
folder.

To disable without deleting:

```toml
[[skills.config]]
path = "/full/path/to/build-bilingual-docx/SKILL.md"
enabled = false
```

Restart Codex after changing `config.toml`.

## Official reference

OpenAI skill documentation:

https://learn.chatgpt.com/docs/build-skills
