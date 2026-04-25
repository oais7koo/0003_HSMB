#!/usr/bin/env python3
"""
oorun_run.py - oorun 스킬 스크립트 (프로젝트 실행)
Usage: uv run python .claude/skills/oorun/scripts/oorun_run.py [help|version|status]
"""
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
        print(f"[ERROR] .claude/skills/{skill_name}/SKILL.md not found")
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

SKILL_NAME = "oorun"
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


def main():
    args = sys.argv[1:]
    if show_help_if_no_args(SKILL_NAME, args):
        return
    cmd = args[0].lower()
    if cmd == "version":
        cmd_version()
    elif cmd == "status":
        cmd_status()
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[{SKILL_NAME}] 알 수 없는 명령: {cmd}")
        _print_skill_help(SKILL_NAME)


if __name__ == "__main__":
    main()
