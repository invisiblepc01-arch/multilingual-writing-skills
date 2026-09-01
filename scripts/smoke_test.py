#!/usr/bin/env python3
"""Run an isolated end-to-end smoke test for the bundled DOCX tools."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    scripts = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="build-bilingual-docx-") as temp_dir:
        temp = Path(temp_dir)
        raw = temp / "fixture.docx"
        hardened = temp / "fixture-hardened.docx"
        run_report = temp / "run-audit.json"
        run(str(scripts / "make_bidi_fixture.py"), str(raw))
        run(str(scripts / "harden_docx_bidi.py"), str(raw), str(hardened), "--mode", "auto")
        run(str(scripts / "audit_docx_bidi.py"), str(hardened))
        run(str(scripts / "audit_docx_run_props.py"), str(hardened), "--report", str(run_report))
        report = json.loads(run_report.read_text(encoding="utf-8"))
        if report["warnings"]:
            raise RuntimeError(f"run audit emitted warnings: {report['warnings']}")
    print("PASS: fixture, hardening, paragraph audit, and run audit")


if __name__ == "__main__":
    main()
