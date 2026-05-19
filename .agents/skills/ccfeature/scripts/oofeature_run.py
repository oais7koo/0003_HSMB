#!/usr/bin/env python3
"""
oofeature_run.py - ccfeature 스킬 스크립트 (상세 문서 생명주기 관리)
Usage: uv run python .agents/skills/ccfeature/scripts/oofeature_run.py [help|version|status]
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

SKILL_NAME = "ccfeature"
VERSION = "v05"


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


def cmd_status():
    print(f"[{SKILL_NAME} status]\n")
    _print_skill_help(SKILL_NAME)
    print(f"\n버전: {VERSION}")


def cmd_update(args):
    import subprocess
    script = _SKILLS_DIR / "ccfeature" / "scripts" / "oofeature_update.py"
    if not script.exists():
        print(f"[ERROR] oofeature_update.py 없음: {script}")
        return
    extra = args[1:] if len(args) > 1 else []
    subprocess.run(
        [sys.executable, str(script)] + extra,
        encoding="utf-8", errors="replace"
    )


def cmd_note(args):
    import subprocess
    script = _SKILLS_DIR / "ccfeature" / "scripts" / "oofeature_note.py"
    if not script.exists():
        print(f"[ERROR] oofeature_note.py 없음: {script}")
        return
    extra = args[1:] if len(args) > 1 else []
    subprocess.run(
        [sys.executable, str(script)] + extra,
        encoding="utf-8", errors="replace"
    )


def cmd_issue(args):
    import subprocess
    script = _SKILLS_DIR / "ccfeature" / "scripts" / "oofeature_issue.py"
    if not script.exists():
        print(f"[ERROR] oofeature_issue.py 없음: {script}")
        return
    extra = args[1:] if len(args) > 1 else []
    subprocess.run(
        [sys.executable, str(script)] + extra,
        encoding="utf-8", errors="replace"
    )


def cmd_rmdup(args):
    import subprocess
    script = _SKILLS_DIR / "ccfeature" / "scripts" / "oofeature_rmdup.py"
    if not script.exists():
        print(f"[ERROR] oofeature_rmdup.py 없음: {script}")
        return
    extra = args[1:] if len(args) > 1 else []
    subprocess.run(
        [sys.executable, str(script)] + extra,
        encoding="utf-8", errors="replace"
    )



STAGE_MAP = {
    "기획": "상세기획", "상세기획": "상세기획",
    "설계": "상세설계", "상세설계": "상세설계",
    "개발": "상세구현", "상세개발": "상세구현", "구현": "상세구현", "상세구현": "상세구현",
    "검증": "상세검증", "상세검증": "상세검증",
    "완료": "상세완료", "상세완료": "상세완료",
}
FILE_PATTERN = _re.compile(r'^(d\d{4,})_(상세(?:기획|설계|구현|검증|완료))_(.+)\.md$')


def cmd_stage(args):
    # usage: ccfeature stage dXXXX 단계
    if len(args) < 3:
        print("[ERROR] 사용법: ccfeature stage dXXXX 단계")
        print("  단계: 기획|설계|개발|검증|완료")
        return

    doc_id = args[1].lower()
    stage_input = args[2]
    target_stage = STAGE_MAP.get(stage_input)
    if not target_stage:
        print(f"[ERROR] 알 수 없는 단계: {stage_input}")
        print("  허용값: 기획, 설계, 개발, 검증, 완료")
        return

    project_root = _SKILLS_DIR.parent.parent
    candidates = []
    for md in project_root.glob("00_doc/**/*.md"):
        m = FILE_PATTERN.match(md.name)
        if m and m.group(1).lower() == doc_id:
            candidates.append((md, m.group(1), m.group(2), m.group(3)))

    if not candidates:
        print(f"[ERROR] 파일 없음: {doc_id}_상세*_*.md")
        return
    if len(candidates) > 1:
        print(f"[WARN] 복수 파일 발견 — 첫 번째만 처리:")
        for c in candidates:
            print(f"  {c[0].relative_to(project_root)}")

    src_path, doc_num, cur_stage, func_name = candidates[0]
    if cur_stage == target_stage:
        print(f"[INFO] 이미 {target_stage} 단계: {src_path.name}")
        return

    new_name = f"{doc_num}_{target_stage}_{func_name}.md"
    new_path = src_path.parent / new_name
    src_path.rename(new_path)
    print(f"[OK] {cur_stage} → {target_stage}")
    print(f"  {src_path.name}")
    print(f"  → {new_name}")


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
    elif cmd == "update":
        cmd_update(args)
    elif cmd == "note":
        cmd_note(args)
    elif cmd == "issue":
        cmd_issue(args)
    elif cmd == "rmdup":
        cmd_rmdup(args)
    elif cmd == "stage":
        cmd_stage(args)
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[{SKILL_NAME}] 알 수 없는 명령: {cmd}")
        _print_skill_help(SKILL_NAME)


if __name__ == "__main__":
    main()
