"""ooskill_gemma_ref.py - 모든 oo* SKILL.md에 Gemma 위임 참조 블록 삽입/갱신.

블록은 HTML 주석 마커(`<!-- GEMMA-REF:START/END -->`)로 감싸 멱등적으로 갱신된다.
삽입 위치: `## 관련 문서` 직전 (없으면 파일 끝).

제외 대상:
- gemma 스킬 자신
- alias 스킬 (ccc, ccd, ccf, cck, ccs) — 본체 스킬을 참조할 뿐 실제 업무 수행 안 함
"""
from __future__ import annotations

import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]  # .codex/skills
EXCLUDE_SKILLS = {"gemma", "ccc", "ccd", "ccf", "cck", "ccs"}
MARKER_START = "<!-- GEMMA-REF:START -->"
MARKER_END = "<!-- GEMMA-REF:END -->"


def build_block() -> str:
    """Gemma 위임 참조 블록 생성."""
    return f"""{MARKER_START}

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |

{MARKER_END}
"""


def update_skill_file(skill_md: Path, *, dry_run: bool = False) -> str:
    """SKILL.md에 Gemma 참조 블록 삽입 또는 갱신. 결과 상태 문자열 반환."""
    content = skill_md.read_text(encoding="utf-8")
    block = build_block()

    if MARKER_START in content and MARKER_END in content:
        start_idx = content.index(MARKER_START)
        end_idx = content.index(MARKER_END) + len(MARKER_END)
        # 블록 앞뒤 공백도 함께 정리
        prefix = content[:start_idx].rstrip() + "\n\n"
        suffix = content[end_idx:].lstrip("\n")
        new_content = prefix + block + "\n" + suffix
        status = "UPDATE"
    else:
        # 삽입 위치: "## 관련 문서" 직전, 없으면 파일 끝
        anchor = "\n## 관련 문서"
        if anchor in content:
            idx = content.index(anchor)
            new_content = content[:idx].rstrip() + "\n\n" + block + "\n" + content[idx:].lstrip("\n")
        else:
            new_content = content.rstrip() + "\n\n" + block + "\n"
        status = "INSERT"

    if new_content == content:
        return "SKIP"

    if not dry_run:
        skill_md.write_text(new_content, encoding="utf-8")
    return status


def collect_targets() -> list[Path]:
    """대상 oo*/SKILL.md 파일 목록 수집."""
    targets = []
    for d in sorted(SKILL_ROOT.iterdir()):
        if not d.is_dir() or not d.name.startswith("oo"):
            continue
        if d.name in EXCLUDE_SKILLS:
            continue
        skill_md = d / "SKILL.md"
        if skill_md.exists():
            targets.append(skill_md)
    return targets


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    targets = collect_targets()
    print(f"# ccskill gemma-ref{' (dry-run)' if dry_run else ''}")
    print()
    print(f"스캔 경로: `{SKILL_ROOT}`")
    print(f"대상 스킬: {len(targets)}개 (제외: {', '.join(sorted(EXCLUDE_SKILLS))})")
    print()
    print("| # | 스킬 | 결과 |")
    print("|---|------|------|")

    counts = {"INSERT": 0, "UPDATE": 0, "SKIP": 0, "ERROR": 0}
    for i, skill_md in enumerate(targets, 1):
        skill_name = skill_md.parent.name
        try:
            status = update_skill_file(skill_md, dry_run=dry_run)
        except Exception as exc:  # pragma: no cover - 파일 I/O 오류
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
