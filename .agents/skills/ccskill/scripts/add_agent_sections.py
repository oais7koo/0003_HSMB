#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_agent_sections.py - 9개 스킬에 표준 서브에이전트 섹션 추가 (일회성)

각 스킬의 <!-- RUN-UPDATE-REF:START --> 마커 직전에 삽입.
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

SKILLS_DIR = Path(__file__).parent.parent.parent

# 스킬별 에이전트 매핑
AGENT_TABLES = {
    "cccheck": [
        ("코드 탐색", "Explore", "haiku", "O"),
        ("에러 검사", "code-error-checker", "sonnet", "O"),
        ("품질 분석", "ooqa", "sonnet", "O"),
        ("결과 검증", "task-checker", "sonnet", "-"),
    ],
    "cccontext": [
        ("SP 탐색", "Explore", "haiku", "-"),
        ("컨텍스트 검증", "task-checker", "sonnet", "-"),
    ],
    "ccdata": [
        ("백업/복원 실행", "task-executor", "sonnet", "O"),
        ("결과 검증", "task-checker", "sonnet", "-"),
    ],
    "ccdb": [
        ("스키마 분석", "Explore", "haiku", "O"),
        ("마이그레이션", "task-executor", "sonnet", "O"),
        ("DB 검증", "task-checker", "sonnet", "-"),
    ],
    "ccfix": [
        ("이슈 분석", "Explore", "haiku", "O"),
        ("에러 검사", "code-error-checker", "sonnet", "O"),
        ("자동 수정", "task-executor", "sonnet", "O"),
        ("결과 검증", "task-checker", "sonnet", "-"),
    ],
    "cchwp": [
        ("문서 작성/편집", "task-executor", "sonnet", "-"),
        ("구조 검증", "task-checker", "sonnet", "-"),
    ],
    "ccref": [
        ("레퍼런스 탐색", "Explore", "haiku", "O"),
        ("적용 체크", "task-executor", "sonnet", "-"),
    ],
    "ccscrap": [
        ("스크래핑 실행", "task-executor", "sonnet", "O"),
        ("데이터 정제", "data-analyst", "sonnet", "-"),
    ],
    "ccuv": [
        ("의존성 분석", "Explore", "haiku", "O"),
        ("패키지 업데이트", "task-executor", "sonnet", "-"),
        ("검증", "task-checker", "sonnet", "-"),
    ],
}

MARKER = "<!-- RUN-UPDATE-REF:START -->"


def build_section(rows: list) -> str:
    lines = [
        "## 서브에이전트",
        "",
        "| 단계 | 에이전트 | 모델 | 병렬 |",
        "|------|---------|------|:----:|",
    ]
    for stage, agent, model, parallel in rows:
        lines.append(f"| {stage} | `{agent}` | {model} | {parallel} |")
    lines.append("")
    return "\n".join(lines)


def patch_skill(skill_name: str, rows: list) -> bool:
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_md.exists():
        print(f"[SKIP] {skill_name}: 파일 없음")
        return False

    content = skill_md.read_text(encoding="utf-8")
    if "## 서브에이전트" in content or "## 에이전트 활용" in content:
        print(f"[SKIP] {skill_name}: 이미 서브에이전트 섹션 존재")
        return False

    if MARKER not in content:
        print(f"[WARN] {skill_name}: RUN-UPDATE-REF 마커 없음")
        return False

    section = build_section(rows)
    new_content = content.replace(
        MARKER,
        f"{section}\n{MARKER}",
        1,
    )
    skill_md.write_text(new_content, encoding="utf-8")
    print(f"[OK]   {skill_name}: 서브에이전트 섹션 추가 ({len(rows)}행)")
    return True


def main() -> int:
    print(f"# add_agent_sections — 대상 {len(AGENT_TABLES)}개 스킬\n")
    ok = 0
    for skill_name, rows in AGENT_TABLES.items():
        if patch_skill(skill_name, rows):
            ok += 1
    print(f"\n완료: {ok}/{len(AGENT_TABLES)}개 수정됨")
    return 0


if __name__ == "__main__":
    sys.exit(main())
