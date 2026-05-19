#!/usr/bin/env python
"""oohelp - OAIS 스킬 도움말 자동 생성 스크립트

.claude/skills/oo*/SKILL.md 파일을 스캔하여 스킬 목록과 서브명령어를 자동 추출합니다.

Usage:
    uv run .claude/skills/oohelp/scripts/oohelp_run.py           # 전체 스킬 목록
    uv run .claude/skills/oohelp/scripts/oohelp_run.py oodev   # 특정 스킬 상세
    uv run .claude/skills/oohelp/scripts/oohelp_run.py --json    # JSON 출력
"""

import re
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')

# --- oo_common inline ---
from pathlib import Path
import re as _re
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
import io
from pathlib import Path

# Windows 콘솔 UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 스킬 카테고리 매핑
SKILL_CATEGORIES = {
    "컨텍스트": ["oocontext"],
    "환경": ["ooenv", "oostart", "oostop"],
    "기획": ["ooprd", "ooplan"],
    "개발": ["oodev"],
    "품질": ["oocheck", "oofix", "ootest"],
    "모듈/DB": ["oolib", "oodb"],
    "문서": ["oodoc", "oohistory", "oocommit"],
    "보고서": ["ooppt", "ooreport"],
    "도움말": ["oohelp"],
}

def get_skill_files() -> list[Path]:
    """.claude/skills/oo*/SKILL.md 파일 목록 반환"""
    skills_path = Path(__file__).parent.parent.parent
    files = sorted(skills_path.glob("oo*/SKILL.md"))
    return files


def parse_skill_file(filepath: Path) -> dict:
    """스킬 파일에서 정보 추출"""
    content = filepath.read_text(encoding="utf-8")
    skill_name = filepath.parent.name

    # 제목에서 용도 추출 (# ooXXX - 용도)
    title_match = re.search(r"^# \w+ - (.+)$", content, re.MULTILINE)
    purpose = title_match.group(1).strip() if title_match else ""

    # 서브명령어 테이블에서 명령어 추출
    commands = []

    # 패턴 1: | `명령어` | 설명 | 형식
    cmd_pattern = r"\|\s*`([^`]+)`\s*\|"
    for match in re.finditer(cmd_pattern, content):
        cmd = match.group(1).strip()
        # 스킬명 제거하고 서브명령어만 추출
        if cmd.startswith(skill_name):
            subcmd = cmd.replace(skill_name, "").strip()
            if subcmd and subcmd not in commands:
                commands.append(subcmd)

    # 주요 명령어만 추출 (최대 4개)
    main_commands = []
    priority_cmds = ["status", "run", "optimize", "check", "create", "doc"]
    for cmd in priority_cmds:
        if cmd in commands and cmd not in main_commands:
            main_commands.append(cmd)
            if len(main_commands) >= 4:
                break

    # 나머지 추가
    for cmd in commands:
        if cmd not in main_commands and len(main_commands) < 4:
            main_commands.append(cmd)

    return {
        "name": skill_name,
        "purpose": purpose,
        "commands": main_commands,
        "all_commands": commands,
    }


def get_category(skill_name: str) -> str:
    """스킬의 카테고리 반환"""
    for category, skills in SKILL_CATEGORIES.items():
        if skill_name in skills:
            return category
    return "기타"


def print_skill_list(skills: list[dict]) -> None:
    """스킬 목록 출력"""
    print("## OAIS 스킬 도움말")
    print()
    print(f"### 스킬 목록 ({len(skills)}개)")
    print()
    print("| 카테고리 | 스킬 | 용도 | 주요 명령어 |")
    print("|----------|------|------|------------|")

    current_category = ""
    for skill in skills:
        category = get_category(skill["name"])
        cat_display = f"**{category}**" if category != current_category else ""
        current_category = category

        cmds = ", ".join(f"`{c}`" for c in skill["commands"][:4]) if skill["commands"] else "-"
        print(f"| {cat_display} | `{skill['name']}` | {skill['purpose'][:20]} | {cmds} |")

    print()
    print("---")
    print()
    print("### 워크플로우")
    print()
    print("**일일 개발**")
    print("```")
    print("oocontext 02 → oodev status → oodev run → oocheck → oofix run → oocommit")
    print("```")
    print()
    print("**전체 파이프라인**")
    print("```")
    print("ooflow run: prd → plan → feature → dev → check → fix → commit")
    print("```")
    print()
    print("---")
    print()
    print("**상세 도움말**: `uv run .claude/skills/oohelp/scripts/oohelp_run.py [스킬명]`")


def print_skill_detail(skill: dict) -> None:
    """특정 스킬 상세 정보 출력"""
    print(f"## {skill['name']}")
    print()
    print(f"**용도**: {skill['purpose']}")
    print()
    print("### 서브명령어")
    print()
    if skill["all_commands"]:
        for cmd in skill["all_commands"]:
            print(f"- `{skill['name']} {cmd}`" if cmd else f"- `{skill['name']}`")
    else:
        print("- (서브명령어 없음)")
    print()
    print(f"**상세 문서**: `.claude/skills/{skill['name']}/SKILL.md`")


def print_json(skills: list[dict]) -> None:
    """JSON 형식 출력"""
    import json
    output = {
        "total": len(skills),
        "categories": SKILL_CATEGORIES,
        "skills": skills,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    args = sys.argv[1:]

    if show_help_if_no_args("oohelp", args):
        return

    # 스킬 파일 스캔
    skill_files = get_skill_files()
    skills = [parse_skill_file(f) for f in skill_files]

    # 카테고리 순서로 정렬
    category_order = list(SKILL_CATEGORIES.keys())
    skills.sort(key=lambda s: (
        category_order.index(get_category(s["name"]))
        if get_category(s["name"]) in category_order else 999,
        s["name"]
    ))

    # 옵션 처리
    if "--json" in args:
        print_json(skills)
    elif args and not args[0].startswith("-"):
        # 특정 스킬 상세
        skill_name = args[0]
        if not skill_name.startswith("oo"):
            skill_name = f"oo{skill_name}"

        skill = next((s for s in skills if s["name"] == skill_name), None)
        if skill:
            print_skill_detail(skill)
        else:
            print(f"스킬을 찾을 수 없습니다: {skill_name}")
            print(f"사용 가능한 스킬: {', '.join(s['name'] for s in skills)}")
    else:
        # 전체 목록
        print_skill_list(skills)


if __name__ == "__main__":
    main()
