#!/usr/bin/env python3
"""
ooskill_backup.py

Claude 환경 파일(.claude/, CLAUDE.md 등)을 날짜별 zip 파일로 백업.
원래 oosync backup 기능에서 이동됨.
"""

import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

BACKUP_TARGETS = [
    ".claude/",
    "CLAUDE.md",
    ".mcp.json",
    "cclaude.bat",
    "cclaude.sh",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".git",
    "tmp",
    ".venv",
    "node_modules",
    "settings.json",
    "settings.local.json",
]


def log_ok(msg): print(f"[OK] {msg}")
def log_warn(msg): print(f"[WARN] {msg}")


def should_exclude(path: Path) -> bool:
    parts = path.parts
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("."):
            if any(p == pattern or p.endswith(pattern) for p in parts):
                return True
        else:
            if any(pattern in p for p in parts):
                return True
    return False


def cmd_backup():
    today = datetime.now().strftime("%y%m%d%H%M")
    backup_base = PROJECT_ROOT / "data" / "04_claude_backup"
    zip_path = backup_base / f"{today}.zip"

    print(f"# ooskill backup\n")
    print(f"백업 경로: data/04_claude_backup/{today}.zip\n")

    backup_base.mkdir(parents=True, exist_ok=True)

    added = 0
    skipped = 0

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for target in BACKUP_TARGETS:
            target_name = target.rstrip("/\\")
            source_path = PROJECT_ROOT / target_name

            if not source_path.exists():
                log_warn(f"없음 (건너뜀): {target_name}")
                skipped += 1
                continue

            if source_path.is_file():
                if not should_exclude(source_path):
                    zf.write(source_path, target_name)
                    log_ok(f"추가: {target_name}")
                    added += 1
                else:
                    skipped += 1
            elif source_path.is_dir():
                file_count = 0
                for file in source_path.rglob("*"):
                    if file.is_file() and not should_exclude(file):
                        arcname = file.relative_to(PROJECT_ROOT)
                        zf.write(file, arcname)
                        file_count += 1
                log_ok(f"추가: {target_name}/ ({file_count}개 파일)")
                added += 1

    size_kb = zip_path.stat().st_size // 1024
    print(f"\n완료: {added}개 추가, {skipped}개 건너뜀")
    print(f"크기: {size_kb} KB")
    print(f"경로: {zip_path}")


if __name__ == "__main__":
    cmd_backup()
