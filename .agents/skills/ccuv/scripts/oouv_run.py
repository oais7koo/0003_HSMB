#!/usr/bin/env python3
"""
oouv_run.py - ccuv 스킬 스크립트 (uv 패키지 관리)
Usage: uv run python .agents/skills/ccuv/scripts/oouv_run.py [help|version|status|update]
"""
import subprocess
import sys
from pathlib import Path
import re as _re

# --- oo_common inline ---
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
        sys.stdout.reconfigure(encoding='utf-8')
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .agents/skills/{skill_name}/SKILL.md not found")
        return
    _c = _sf.read_text(encoding="utf-8")
    _m = _re.search(r"##[^\n]*(?:서브명령어|명령어)\n\n((?:\|.+\n)+)", _c)
    if _m:
        print(f"`{skill_name} help` 서브명령어 목록:\n")
        print(_m.group(1).strip())
    else:
        print(f"[WARN] 서브명령어 섹션 없음: {skill_name}/SKILL.md")

def show_help_if_no_args(skill_name, args):
    if not args or args[0].lower() in ("help", "-h", "--help"):
        _print_skill_help(skill_name)
        return True
    return False
# --- end oo_common inline ---

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SKILL_NAME = "ccuv"
VERSION = "v02"


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


def cmd_status():
    print(f"[{SKILL_NAME} status]\n")
    _print_skill_help(SKILL_NAME)
    print(f"\n버전: {VERSION}")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def cmd_update(dry_run: bool = False) -> int:
    """uv.lock 갱신 — 의존성을 최신 호환 버전으로 업그레이드.

    동작:
      - dry_run=True : `uv lock --upgrade --dry-run` (변경 예정 출력만)
      - dry_run=False: `uv sync --upgrade` (실제 잠금 갱신 + 환경 동기화)
    """
    print(f"# {SKILL_NAME} update\n")
    pyproject = Path.cwd() / "pyproject.toml"
    if not pyproject.exists():
        print(f"[ERROR] pyproject.toml 이 현재 디렉토리에 없습니다: {Path.cwd()}")
        return 1

    if dry_run:
        cmd = ["uv", "lock", "--upgrade", "--dry-run"]
        print(f"[DRY-RUN] 실행 예정: {' '.join(cmd)}\n")
    else:
        cmd = ["uv", "sync", "--upgrade"]
        print(f"실행: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        print("[ERROR] 'uv' 명령을 찾을 수 없습니다. uv가 설치되어 있는지 확인하세요.")
        return 1

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode == 0:
        print(f"[OK] {SKILL_NAME} update 완료")
    else:
        print(f"[FAIL] uv 명령 실패 (exit={result.returncode})")
    return result.returncode


def main():
    args = sys.argv[1:]
    if show_help_if_no_args(SKILL_NAME, args):
        return
    cmd = args[0].lower()
    dry_run = "--dry-run" in args
    if cmd == "version":
        cmd_version()
    elif cmd == "status":
        cmd_status()
    elif cmd == "update":
        sys.exit(cmd_update(dry_run=dry_run))
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[{SKILL_NAME}] 알 수 없는 명령: {cmd}")
        _print_skill_help(SKILL_NAME)


if __name__ == "__main__":
    main()
