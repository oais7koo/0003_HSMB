"""ccwork 개조식(S01) 종결어미·마커 검증 스크립트.

용도: HWP 붙여넣기용 통합본·정부 R&D 제안서 등 S01 개조식 적용 문서가
서술식 종결어미(~한다/~된다/~이다 등)를 포함하는지, □/○/- 3단 마커 계층을
실제로 적용하고 있는지, 항목 내 ①②③④+→ 화살표 체인 표현을 사용하는지,
원문자(①~⑳)를 단독으로 사용하는지 확인하여 BLOCK/PASS 결과를 반환한다.

Reference: .agents/skills/ccwork/references/checklist_common.md (G20·G21·G25·G26)
           .agents/skills/ccwork/references/writing_styles.md (S01)

Usage:
    uv run python .agents/skills/ccwork/scripts/oowork_check_style.py <대상.md>
    uv run python .agents/skills/ccwork/scripts/oowork_check_style.py <대상.md> --strict

Exit codes:
    0 — PASS (개조식 준수)
    1 — BLOCK (서술식 종결어미 또는 마커 누락 발견)
    2 — 입력 오류
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

# Windows cp949 환경에서도 UTF-8로 출력
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 서술식 종결어미 패턴 (S01 금지)
NARRATIVE_PATTERNS = [
    (r"한다\.", "~한다."),
    (r"된다\.", "~된다."),
    (r"있다\.", "~있다."),
    (r"없다\.", "~없다."),
    (r"이다\.", "~이다."),
    (r"하였다\.", "~하였다."),
    (r"되었다\.", "~되었다."),
    (r"합니다\.", "~합니다."),
    (r"입니다\.", "~입니다."),
    (r"습니다\.", "~습니다."),
    (r"한 상태이다\.", "~한 상태이다."),
]

# 본문 영역에서 제외할 라인 (표·인용·코드·헤더·구분선)
EXCLUDE_PREFIX = ("|", ">", "```", "#", "---", "*(", "[그림")
EXCLUDE_INLINE = ("|",)


def is_excluded(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith(EXCLUDE_PREFIX):
        return True
    if stripped.startswith(EXCLUDE_INLINE):
        return True
    return False


def find_narrative_endings(lines: list[str]) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    for idx, line in enumerate(lines, start=1):
        if is_excluded(line):
            continue
        for pat, label in NARRATIVE_PATTERNS:
            if re.search(pat, line):
                hits.append((idx, label, line.rstrip()))
                break
    return hits


# ①~⑳ 유니코드 범위: ① U+2460 ~ ⑳ U+2473
_CIRCLE_NUM = r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]"
_CIRCLE_NUM_PAT = re.compile(_CIRCLE_NUM)
_INLINE_CHAIN_PAT = re.compile(_CIRCLE_NUM + r".{0,40}→.{0,40}" + _CIRCLE_NUM)


def _is_code_excluded(stripped: str) -> bool:
    return stripped.startswith(("|", ">", "#", "---", "*(", "[그림"))


def find_inline_chains(lines: list[str]) -> list[tuple[int, str]]:
    """○/□/- 항목 내 ①②③④+→ 화살표 체인 표현 검출 (G25)."""
    hits: list[tuple[int, str]] = []
    in_code = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or _is_code_excluded(stripped):
            continue
        if _INLINE_CHAIN_PAT.search(stripped):
            hits.append((idx, stripped[:120]))
    return hits


def find_circle_numbers(lines: list[str]) -> list[tuple[int, str]]:
    """원문자(①~⑳) 단독 사용 검출 (G26) — 체인 포함 모든 원문자 사용."""
    hits: list[tuple[int, str]] = []
    in_code = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or _is_code_excluded(stripped):
            continue
        if _CIRCLE_NUM_PAT.search(stripped):
            hits.append((idx, stripped[:120]))
    return hits


def find_paragraph_orphans(lines: list[str]) -> list[tuple[int, str]]:
    """3단 마커(□/○/-) 적용 안 된 일반 단락 검출."""
    orphans: list[tuple[int, str]] = []
    in_code = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or is_excluded(line):
            continue
        if stripped.startswith(("□", "○", "-", "*", "■", "◆", "◇", "★", "※")):
            continue
        if re.match(r"^\d+\.", stripped):
            continue
        if re.match(r"^[A-Za-z가-힣]", stripped) and len(stripped) > 30:
            orphans.append((idx, stripped[:80]))
    return orphans


def _strip_appendix(lines: list[str]) -> list[str]:
    """`# 부록` 또는 `## 부록` 헤더 이후 라인 제외 (S01 규칙 미적용 영역)."""
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("# 부록") or stripped.startswith("## 부록"):
            return lines[:idx]
    return lines


def check_file(path: Path, strict: bool) -> int:
    if not path.is_file():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    lines = _strip_appendix(text.splitlines())

    narrative = find_narrative_endings(lines)
    orphans = find_paragraph_orphans(lines) if strict else []
    chains = find_inline_chains(lines)
    circle_nums = find_circle_numbers(lines)

    print(f"# ccwork 개조식(S01) 검증 — {path}")
    print()
    print(f"- 총 라인 수: {len(lines)}")
    print(f"- 서술식 종결어미 발견: **{len(narrative)}건** (G20)")
    print(f"- 마커 누락 단락 후보: **{len(orphans)}건** (G21, strict)")
    print(f"- ①②③④+→ 화살표 체인 발견: **{len(chains)}건** (G25)")
    print(f"- 원문자(①~⑳) 사용 발견: **{len(circle_nums)}건** (G26)")
    print()

    if narrative:
        print("## ❌ G20 위반 — 서술식 종결어미 (S01에서 금지)")
        print()
        print("| 라인 | 종결어미 | 본문 |")
        print("|:--:|:--:|------|")
        for ln, lbl, body in narrative[:50]:
            preview = body[:120].replace("|", "\\|")
            print(f"| {ln} | `{lbl}` | {preview} |")
        if len(narrative) > 50:
            print(f"| … | … | (+{len(narrative)-50}건 추가) |")
        print()

    if orphans:
        print("## 🟡 G21 후보 — 마커 누락 단락 (검토 필요)")
        print()
        print("| 라인 | 본문 (앞 80자) |")
        print("|:--:|------|")
        for ln, body in orphans[:30]:
            preview = body.replace("|", "\\|")
            print(f"| {ln} | {preview} |")
        if len(orphans) > 30:
            print(f"| … | (+{len(orphans)-30}건 추가) |")
        print()

    if chains:
        print("## ❌ G25 위반 — 항목 내 ①②③④+→ 화살표 체인 (S01에서 금지)")
        print()
        print("| 라인 | 본문 (앞 120자) |")
        print("|:--:|------|")
        for ln, body in chains[:30]:
            preview = body.replace("|", "\\|")
            print(f"| {ln} | {preview} |")
        if len(chains) > 30:
            print(f"| … | (+{len(chains)-30}건 추가) |")
        print("→ 수정 방법: ①②③④ 각 항목을 `-` 3단 마커로 분리하거나 표로 변환")
        print()

    if circle_nums:
        print("## ❌ G26 위반 — 원문자(①~⑳) 사용 (S01에서 금지)")
        print()
        print("| 라인 | 본문 (앞 120자) |")
        print("|:--:|------|")
        for ln, body in circle_nums[:30]:
            preview = body.replace("|", "\\|")
            print(f"| {ln} | {preview} |")
        if len(circle_nums) > 30:
            print(f"| … | (+{len(circle_nums)-30}건 추가) |")
        print("→ 수정 방법: 순서 표현은 표 또는 `-` 3단 마커 개별 항목으로 대체")
        print()

    if narrative or chains or circle_nums or (strict and orphans):
        print("## 결과: ❌ **BLOCK** — S01 개조식 미준수")
        return 1

    print("## 결과: ✅ **PASS** — S01 개조식 준수")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ccwork 개조식(S01) 검증")
    parser.add_argument("path", type=Path, help="검증 대상 .md 파일 경로")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="마커 누락 단락(G21)까지 BLOCK 처리",
    )
    args = parser.parse_args()
    return check_file(args.path, args.strict)


if __name__ == "__main__":
    sys.exit(main())
