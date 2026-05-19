"""ooskill_run_update_ref.py - 모든 oo* SKILL.md에 run/update 분리 원칙 참조 블록 삽입/갱신.

블록은 HTML 주석 마커(`<!-- RUN-UPDATE-REF:START/END -->`)로 감싸 멱등적으로 갱신된다.
삽입 위치: `## Gemma 위임` 블록 바로 위 (없으면 `## 관련 문서` 직전, 그것도 없으면 파일 끝).

제외 대상:
- gemma 스킬 자신 (위임 전용)
- alias 스킬 (ccc, ccd, ccf, cck, ccs) — 본체 스킬만 원칙 명시
"""
from __future__ import annotations

import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]  # .codex/skills
EXCLUDE_SKILLS = {"gemma", "ccc", "ccd", "ccf", "cck", "ccs"}
MARKER_START = "<!-- RUN-UPDATE-REF:START -->"
MARKER_END = "<!-- RUN-UPDATE-REF:END -->"


def build_block() -> str:
    """run/update 분리 원칙 참조 블록 생성."""
    return f"""{MARKER_START}

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

{MARKER_END}
"""


def update_skill_file(skill_md: Path, *, dry_run: bool = False) -> str:
    """SKILL.md에 run/update 참조 블록 삽입 또는 갱신. 결과 상태 문자열 반환."""
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
        # 삽입 위치 우선순위: Gemma 블록 직전 → ## 관련 문서 직전 → 파일 끝
        anchors = ["<!-- GEMMA-REF:START -->", "\n## 관련 문서"]
        inserted = False
        for anchor in anchors:
            if anchor in content:
                idx = content.index(anchor)
                new_content = content[:idx].rstrip() + "\n\n" + block + "\n" + content[idx:].lstrip("\n")
                inserted = True
                break
        if not inserted:
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
    print(f"# ccskill run-update-ref{' (dry-run)' if dry_run else ''}")
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
        except Exception as exc:  # pragma: no cover
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
