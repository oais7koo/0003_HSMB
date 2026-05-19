"""ooskill_karpathy_ref.py - 코딩 관련 oo* SKILL.md에 Karpathy 가이드라인 참조 블록 삽입/갱신.

블록은 HTML 주석 마커(`<!-- KARPATHY-REF:START/END -->`)로 감싸 멱등적으로 갱신된다.
삽입 위치: `<!-- GEMMA-REF:START -->` 직전, 없으면 `## 관련 문서` 직전, 없으면 파일 끝.

대상: 코드를 직접 쓰거나 수정·리뷰·테스트하는 스킬만 포함 (문서/메타 스킬 제외).
"""
from __future__ import annotations

import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]  # .codex/skills
# 코딩 관련 스킬 (직접 코드 작성·수정·리뷰·테스트 수행)
INCLUDE_SKILLS = {
    "ccflow",     # 전체 워크플로우 오케스트레이터
    "ccprd",      # PRD 생성
    "ccplan",     # 구현 계획
    "ccfeature",  # 기능 문서 생명주기
    "ccdev",      # TDD 개발
    "cctest",     # 테스트
    "cccheck",    # 코드 체크
    "ccfix",      # 오류 수정
    "cccommit",   # 커밋
    "cclib",      # 모듈 최적화
    "ccrun",      # TDD 실행
    "ccreview",   # 코드 리뷰
    "ccopti",     # 알고리즘/코드 최적화
}
MARKER_START = "<!-- KARPATHY-REF:START -->"
MARKER_END = "<!-- KARPATHY-REF:END -->"


def build_block() -> str:
    """Karpathy 가이드라인 참조 블록 생성."""
    return f"""{MARKER_START}

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.codex/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |
| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |
| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |
| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |

**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.

{MARKER_END}
"""


def update_skill_file(skill_md: Path, *, dry_run: bool = False) -> str:
    """SKILL.md에 Karpathy 참조 블록 삽입 또는 갱신. 결과 상태 문자열 반환."""
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
        # 삽입 우선순위: GEMMA-REF:START 직전 → ## 관련 문서 직전 → 파일 끝
        for anchor in ("<!-- GEMMA-REF:START -->", "\n## 관련 문서"):
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
    print(f"# ccskill karpathy-ref{' (dry-run)' if dry_run else ''}")
    print()
    print(f"스캔 경로: `{SKILL_ROOT}`")
    print(f"대상 스킬: {len(targets)}개 (코딩 관련만)")
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
