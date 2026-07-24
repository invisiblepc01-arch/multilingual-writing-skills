from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    "",
    ".md",
    ".py",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
}

WINDOWS_PROFILE_PATH = re.compile(
    r"(?i)\b[A-Z]:[\\/]+Users[\\/]+(?!<[^>]+>|%USERPROFILE%)[^\\/\s]+"
)
EMAIL_ADDRESS = re.compile(
    r"(?i)(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?![\w.-])"
)
PRIVATE_KEY_HEADER = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")


def repository_text_files() -> list[Path]:
    return [
        path
        for path in REPOSITORY_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix.lower() in TEXT_SUFFIXES
    ]


def test_repository_contains_no_local_identity_or_secret_markers() -> None:
    findings: list[str] = []

    for path in repository_text_files():
        text = path.read_text(encoding="utf-8", errors="strict")
        relative = path.relative_to(REPOSITORY_ROOT)

        for label, pattern in (
            ("Windows user-profile path", WINDOWS_PROFILE_PATH),
            ("email address", EMAIL_ADDRESS),
            ("private-key header", PRIVATE_KEY_HEADER),
        ):
            if pattern.search(text):
                findings.append(f"{relative}: {label}")

    assert not findings, "Potentially identifying or secret content:\n" + "\n".join(
        findings
    )
