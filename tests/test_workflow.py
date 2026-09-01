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
    paragraph_report = tmp_path / "paragraph-audit.json"
    run_report = tmp_path / "run-audit.json"

    run(SCRIPTS / "make_bidi_fixture.py", raw)
    run(SCRIPTS / "harden_docx_bidi.py", raw, hardened, "--mode", "auto")
    run(SCRIPTS / "audit_docx_bidi.py", hardened, "--json", paragraph_report)
    run(SCRIPTS / "audit_docx_run_props.py", hardened, "--report", run_report)

    paragraph_result = json.loads(paragraph_report.read_text(encoding="utf-8"))
    assert paragraph_result["passed"] is True
    assert paragraph_result["errors"] == []
    assert paragraph_result["warnings"] == []
    assert paragraph_result["stats"]["paragraphs"] >= 10

    run_result = json.loads(run_report.read_text(encoding="utf-8"))
    assert run_result["passed"] is True
    assert run_result["errors"] == []
    assert run_result["warnings"] == []
    assert run_result["stats"]["visible_runs"] >= 20
