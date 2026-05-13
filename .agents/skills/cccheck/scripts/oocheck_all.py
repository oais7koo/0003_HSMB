"""
cccheck run --all: 모든 oo 스킬의 checklist.md 기반 체크 일괄 실행
- .claude/skills/oo*/references/checklist.md 스캔
- 각 스킬의 체크 항목 수 + 필수 파일 존재 여부 검증
"""

import os
import re
import sys

SKILLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "skills",
)


def parse_checklist(filepath):
    """checklist.md에서 체크 항목 파싱"""
    items = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            # | ID | 항목 | 검증 내용 | 심각도 | 형식
            match = re.match(r"\|\s*(C\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\w+)\s*\|", line)
            if match:
                items.append({
                    "id": match.group(1),
                    "name": match.group(2).strip(),
                    "desc": match.group(3).strip(),
                    "severity": match.group(4).strip(),
                })
    return items


def check_skill_health(skill_name, skill_dir):
    """스킬 기본 건강 상태 체크"""
    results = []

    # SKILL.md 존재
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md):
        results.append(("OK", "SKILL.md 존재"))
    else:
        results.append(("ERROR", "SKILL.md 누락"))

    # checklist.md 존재
    checklist = os.path.join(skill_dir, "references", "checklist.md")
    if os.path.exists(checklist):
        items = parse_checklist(checklist)
        results.append(("OK", f"checklist.md ({len(items)}개 항목)"))
    else:
        results.append(("WARN", "checklist.md 누락"))

    # scripts/ 폴더
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        scripts = [f for f in os.listdir(scripts_dir) if f.endswith(".py")]
        results.append(("OK", f"scripts/ ({len(scripts)}개)"))
    else:
        results.append(("INFO", "scripts/ 없음"))

    return results


def main():
    print("# cccheck run --all")
    print(f"대상: .claude/skills/oo*/")
    print()

    total_ok = 0
    total_warn = 0
    total_error = 0
    skill_count = 0

    # oo* 스킬 스캔
    skills = sorted([
        d for d in os.listdir(SKILLS_DIR)
        if d.startswith("oo") and os.path.isdir(os.path.join(SKILLS_DIR, d))
    ])

    for skill_name in skills:
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        results = check_skill_health(skill_name, skill_dir)
        skill_count += 1

        # 스킬별 결과
        has_issue = any(r[0] in ("ERROR", "WARN") for r in results)
        if has_issue:
            print(f"[{skill_name}]")
            for status, msg in results:
                icon = {"OK": "[OK]", "WARN": "[WARN]", "ERROR": "[ERROR]", "INFO": "[INFO]"}[status]
                print(f"  {icon:8s} {msg}")
            print()

        for status, _ in results:
            if status == "OK":
                total_ok += 1
            elif status == "WARN":
                total_warn += 1
            elif status == "ERROR":
                total_error += 1

    print("-" * 50)
    print(f"스킬: {skill_count}개 | OK: {total_ok} | WARN: {total_warn} | ERROR: {total_error}")

    # checklist.md가 있는 스킬 목록
    with_checklist = []
    without_checklist = []
    for skill_name in skills:
        cl = os.path.join(SKILLS_DIR, skill_name, "references", "checklist.md")
        if os.path.exists(cl):
            items = parse_checklist(cl)
            with_checklist.append((skill_name, len(items)))
        else:
            without_checklist.append(skill_name)

    print(f"\nchecklist 보유: {len(with_checklist)}개 | 미보유: {len(without_checklist)}개")

    if without_checklist:
        print(f"\nchecklist 미보유 스킬:")
        for s in without_checklist:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
