from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def test_secret_files_are_ignored():
    """Kiểm tra REQ-NFR-02: Các file chứa bí mật và credentials phải được .gitignore loại bỏ."""
    test_files = [
        ".env",
        ".env.local",
        ".env.production",
        "config/challenge.json",
        "data/logs.jsonl",
        "private.key",
        "certificate.pem",
    ]
    for rel_path in test_files:
        res = subprocess.run(
            ["git", "check-ignore", rel_path],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"File {rel_path} phải được ignore bởi git nhưng hiện tại không bị ignore!"


def test_env_example_is_not_ignored_and_contains_no_real_secrets():
    """Kiểm tra REQ-NFR-02: .env.example phải được theo dõi (không ignore) và không chứa API key thật."""
    res = subprocess.run(
        ["git", "check-ignore", ".env.example"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
    # Return code 1 nghĩa là .env.example không bị ignore
    assert res.returncode == 1, ".env.example không được phép bị ignore vì là file mẫu cấu hình!"

    env_example_path = ROOT_DIR / ".env.example"
    assert env_example_path.exists(), ".env.example phải tồn tại!"
    content = env_example_path.read_text(encoding="utf-8")

    # Kiểm tra không có secret key thật dạng pk-lf- / sk-lf-
    assert not re.search(r"LANGFUSE_PUBLIC_KEY=\s*pk-lf-[a-zA-Z0-9_-]{10,}", content)
    assert not re.search(r"LANGFUSE_SECRET_KEY=\s*sk-lf-[a-zA-Z0-9_-]{10,}", content)


def test_critical_files_not_tracked_in_git():
    """Kiểm tra REQ-NFR-02: .env và config/challenge.json không bao giờ được xuất hiện trong git index."""
    res = subprocess.run(
        ["git", "ls-files", ".env", "config/challenge.json"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
    tracked_files = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
    assert len(tracked_files) == 0, f"Phát hiện file nhạy cảm đang bị git theo dõi: {tracked_files}"


def test_codebase_source_has_no_hardcoded_secrets():
    """Kiểm tra REQ-NFR-02: Không hardcode secret keys trong mã nguồn Python thuộc app/."""
    app_dir = ROOT_DIR / "app"
    secret_patterns = [
        re.compile(r"""(?:sk|pk)-(?:lf-)?[a-zA-Z0-9]{20,}"""),
        re.compile(r"""(?i)secret[_-]?key\s*=\s*['"][a-zA-Z0-9_\-]{16,}['"]"""),
    ]
    for py_file in app_dir.glob("**/*.py"):
        text = py_file.read_text(encoding="utf-8")
        for pattern in secret_patterns:
            matches = pattern.findall(text)
            assert not matches, f"Phát hiện khả năng hardcode secret trong {py_file.name}: {matches}"
