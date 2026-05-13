"""ooskill_qmd_ref.py - 문서 검색 관련 oo* SKILL.md에 QMD 검색 참조 블록 삽입/갱신.

블록은 HTML 주석 마커(`<!-- QMD-REF:START/END -->`)로 감싸 멱등적으로 갱신된다.
삽입 위치: `<!-- KARPATHY-REF:START -->` 직전, 없으면 `<!-- GEMMA-REF:START -->` 직전,
           없으면 `## 관련 문서` 직전, 없으면 파일 끝.

대상: 마크다운 문서 내용을 검색하거나 문서를 탐색하는 스킬만 포함.
"""
from __future__ import annotations

import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]  # .claude/skills
# 문서 검색을 수행하는 스킬
INCLUDE_SKILLS = {
    "oodoc",      # 문서 자동화 — 문서 탐색/생성
    "oocontext",  # 서브프로젝트 컨텍스트 — 관련 문서 검색
    "ooprd",      # PRD 생성 — 기존 문서 참조
    "ooplan",     # 구현 계획 — 기존 계획/문서 참조
    "oonext",     # 다음 작업 추천 — 컨텍스트 문서 검색
    "oonow",      # 현재 상태 — 최근 문서 탐색
    "ooresearch", # SOTA 연구 — 문서/논문 검색
    "oowork",     # 작업 관리 — 관련 문서 탐색
}
MARKER_START = "<!-- QMD-REF:START -->"
MARKER_END = "<!-- QMD-REF:END -->"


def build_block() -> str:
    """QMD 검색 참조 블록 생성."""
    return f"""{MARKER_START}

## QMD 마크다운 검색 (문서 내용 탐색 시)

> 마크다운 문서 **내용**을 찾을 때는 Glob/Grep 대신 **`mcp__qmd__query`** 우선 사용.
> qmd 미가동 시 Glob/Grep 폴백. 자세한 기준: `.claude/guides/common_guide.md §10`

| 도구 | 적합한 상황 |
|------|-----------|
| `mcp__qmd__query` (lex) | 키워드·문서번호·용어 검색 |
| `mcp__qmd__query` (vec) | 자연어 의미 검색 |
| `Glob` | 파일 경로 패턴 검색 |
| `Grep` | 코드·특정 문자열 검색 |

**인덱싱**: `oostart run` 시 `qmd update` 자동 실행 / 최초: `qmd collection add . --name {{프로젝트명}}`

{MARKER_END}
"""


def update_skill_file(skill_md: Path, *, dry_run: bool = False) -> str:
    """SKILL.md에 QMD 참조 블록 삽입 또는 갱신. 결과 상태 문자열 반환."""
    content = skill_md.read_text(encoding="utf-8")
    block = build_block()

    if MARKER_START in content and MARKER_END in content:
        start_idx = content.index(MARKER_START)
        end_idx = content.index(MARKER_END) + len(MARKER_END)
        prefix = content[:start_idx].rstrip() + "\n\n"
        suffix = content[end_idx:].lstrip("\n")
        new_content = prefix + block + "\n" + suffix
        status = "UPDATE"
    else:
        # 삽입 우선순위: KARPATHY-REF:START → GEMMA-REF:START → ## 관련 문서 → 파일 끝
        for anchor in ("<!-- KARPATHY-REF:START -->", "<!-- GEMMA-REF:START -->", "\n## 관련 문서"):
            if anchor in content:
                idx = content.index(anchor)
                new_content = content[:idx].rstrip() + "\n\n" + block + "\n" + content[idx:].lstrip("\n")
                break
        else:
            new_content = content.rstrip() + "\n\n" + block + "\n"
        status = "INSERT"

    if new_content == content:
        return "SKIP"

    if not dry_run:
        skill_md.write_text(new_content, encoding="utf-8")
    return status


def collect_targets() -> list[Path]:
    """INCLUDE_SKILLS 중 존재하는 SKILL.md 파일 목록 수집."""
    targets = []
    for name in sorted(INCLUDE_SKILLS):
        skill_md = SKILL_ROOT / name / "SKILL.md"
        if skill_md.exists():
            targets.append(skill_md)
    return targets


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    targets = collect_targets()
    print(f"# ooskill qmd-ref{' (dry-run)' if dry_run else ''}")
    print()
    print(f"스캔 경로: `{SKILL_ROOT}`")
    print(f"대상 스킬: {len(targets)}개 (문서 검색 관련)")
    print()
    print("| # | 스킬 | 결과 |")
    print("|---|------|------|")

    counts = {"INSERT": 0, "UPDATE": 0, "SKIP": 0, "ERROR": 0}
    for i, skill_md in enumerate(targets, 1):
        skill_name = skill_md.parent.name
        try:
            status = update_skill_file(skill_md, dry_run=dry_run)
        except Exception as exc:
            status = f"ERROR: {exc}"
            counts["ERROR"] += 1
        else:
            counts[status] += 1
        print(f"| {i} | {skill_name} | {status} |")

    print()
    print("## 요약")
    print()
    print(f"- INSERT: {counts['INSERT']}개")
    print(f"- UPDATE: {counts['UPDATE']}개")
    print(f"- SKIP:   {counts['SKIP']}개")
    print(f"- ERROR:  {counts['ERROR']}개")
    if dry_run:
        print()
        print("> --dry-run 모드: 실제 파일 수정 안 함")
    return 0 if counts["ERROR"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
