#!/usr/bin/env python3
"""
oonow_run.py - oonow 스킬 스크립트 (현재 작업 상태 확인)
Usage: uv run python .claude/skills/oonow/scripts/oonow_run.py [help|version|status]
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

SKILL_NAME = "oonow"
VERSION = "v01"


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


def _get_current_sp() -> str:
    """oocontext 상태에서 현재 SP 번호 문자열 반환 (없으면 "00")."""
    import json
    state_file = Path(".") / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8")).get("sp", "00")
        except Exception:
            pass
    return "00"


def _scan_todo_states(sp_str: str) -> dict:
    """todo/{ID}.md 상세 파일에서 상태별 항목 수집 — R163."""
    todo_dir = Path(".") / "00_doc" / f"sp{int(sp_str):02d}" / "todo"
    items = {"IN_PROGRESS": [], "OPEN": [], "HOLD": []}
    if not todo_dir.exists():
        return items
    head_re = _re.compile(r"^>\s*우선순위:\s*([^|]+?)\s*\|\s*상태:\s*([A-Z_]+)", _re.MULTILINE)
    title_re = _re.compile(r"^#\s*([^\n]+)", _re.MULTILINE)
    for fp in sorted(todo_dir.glob("*.md")):
        if fp.stem in ("_template", "README"):
            continue
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        m_head = head_re.search(text)
        if not m_head:
            continue
        state = m_head.group(2).strip()
        if state not in items:
            continue
        priority = m_head.group(1).strip()
        m_title = title_re.search(text)
        title = m_title.group(1).strip() if m_title else fp.stem
        items[state].append({"id": fp.stem, "title": title, "priority": priority, "path": str(fp.as_posix())})
    return items


def cmd_status():
    print(f"# oonow - 현재 작업 상황\n")
    sp_str = _get_current_sp()
    sp_num = int(sp_str) if sp_str.isdigit() else 0
    print(f"현재 컨텍스트: **SP{sp_num:02d}**\n")
    if sp_num == 0:
        print("[INFO] SP00 (공통) — todo 폴더 점검 생략")
        return
    items = _scan_todo_states(sp_str)
    # IN_PROGRESS 우선 표시
    if items["IN_PROGRESS"]:
        print(f"## 🔄 진행 중 ({len(items['IN_PROGRESS'])}건)\n")
        for it in items["IN_PROGRESS"]:
            print(f"- **{it['id']}** [{it['priority']}] — {it['title']}")
            print(f"  → [{it['path']}]({it['path']})")
        print()
    else:
        print("## 🔄 진행 중\n")
        print("- (없음)\n")
    # OPEN/HOLD 요약
    if items["OPEN"] or items["HOLD"]:
        print(f"## 📋 대기/보류 (OPEN {len(items['OPEN'])} · HOLD {len(items['HOLD'])})\n")
        for it in items["OPEN"][:5]:
            print(f"- {it['id']} [{it['priority']}] — {it['title']}")
        if len(items["OPEN"]) > 5:
            print(f"- ... 외 {len(items['OPEN']) - 5}건")
        for it in items["HOLD"]:
            print(f"- ⏸ {it['id']} [{it['priority']}] — {it['title']}")
        print()


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
