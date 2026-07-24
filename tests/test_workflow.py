import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        check=True,
        capture_output=True,
        text=True,
    )


def test_fixture_harden_and_audit(tmp_path):
    raw = tmp_path / "raw.docx"
    hardened = tmp_path / "hardened.docx"
    report = tmp_path / "audit.json"

    run(SCRIPTS / "make_bidi_fixture.py", raw)
    run(SCRIPTS / "harden_docx_bidi.py", raw, hardened, "--mode", "auto")
    run(SCRIPTS / "audit_docx_bidi.py", hardened, "--json", report)

    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["passed"] is True
    assert result["errors"] == []
    assert result["stats"]["paragraphs"] >= 10
