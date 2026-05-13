#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
oodoc numbering - 문서 번호 체계(SSOT) 조회/편집 스크립트

SSOT 파일: .claude/skills/oodoc/references/doc_numbering.md

사용법:
    uv run .claude/skills/oodoc/scripts/oodoc_numbering.py
        → 전체 SSOT 출력

    uv run .claude/skills/oodoc/scripts/oodoc_numbering.py add 0500 "d{SP}0500_사업계획서.md" "사업계획서" "수동/oowork"
        → §2.3 (0100~0999 범위) 표에 행 추가

    uv run .claude/skills/oodoc/scripts/oodoc_numbering.py remove 0500
        → §2.3 표에서 0500번 행 제거

    uv run .claude/skills/oodoc/scripts/oodoc_numbering.py edit
        → SSOT 파일 경로 안내
"""

import sys
import argparse
from pathlib import Path

# Windows cp949 인코딩 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
SSOT_PATH = SCRIPT_DIR.parent / "references" / "doc_numbering.md"

# §2.3 (선택 문서 0100~0999) 표 식별 마커
SEC_HEADER = "### 2.3 선택 문서 (0100~0999) — 특정 스킬 전용"
NEXT_SEC_HEADER = "### 2.4 상세 문서 (1000~9999) — oofeature 전용"


def read_ssot() -> str:
    if not SSOT_PATH.exists():
        sys.exit(f"[ERROR] SSOT 파일을 찾을 수 없음: {SSOT_PATH}")
    return SSOT_PATH.read_text(encoding="utf-8")


def write_ssot(content: str) -> None:
    SSOT_PATH.write_text(content, encoding="utf-8")


def cmd_show() -> int:
    """SSOT 파일 전체 출력."""
    print(f"# SSOT: {SSOT_PATH}\n")
    print(read_ssot())
    return 0


def cmd_edit() -> int:
    """편집 경로 안내."""
    print("SSOT 파일을 직접 편집하세요:")
    print(f"  {SSOT_PATH}")
    print("\n편집 후 파생 튜토리얼도 동기화 권장:")
    print("  .claude/tutorial/37_문서번호및파일명규칙.md")
    print("  00_doc/sp03/tutorial/37_문서번호및파일명규칙.md")
    return 0


def _find_section_range(lines: list[str], header: str, next_header: str) -> tuple[int, int]:
    """섹션 헤더 ~ 다음 섹션 헤더 직전까지 라인 인덱스 반환."""
    start = end = -1
    for i, line in enumerate(lines):
        if line.strip() == header:
            start = i
        elif start >= 0 and line.strip() == next_header:
            end = i
            break
    if start < 0:
        sys.exit(f"[ERROR] 섹션을 찾을 수 없음: {header}")
    if end < 0:
        end = len(lines)
    return start, end


def _find_main_table_range(lines: list[str], sec_start: int, sec_end: int) -> tuple[int, int]:
    """섹션 내 첫 번째 markdown 표(헤더|구분|행…)의 끝 라인 인덱스 반환."""
    table_start = table_end = -1
    for i in range(sec_start, sec_end):
        line = lines[i].rstrip()
        if line.startswith("|") and "번호" in line and "파일명" in line:
            table_start = i
            # 표 끝 = 빈 줄 또는 비-| 라인
            for j in range(i + 2, sec_end):  # i+1은 구분선 |---|
                if not lines[j].lstrip().startswith("|"):
                    table_end = j
                    break
            else:
                table_end = sec_end
            break
    if table_start < 0:
        sys.exit("[ERROR] §2.3 표를 찾을 수 없음")
    return table_start, table_end


def cmd_add(num: str, pattern: str, purpose: str, skill: str) -> int:
    """§2.3 표에 행 추가 (번호순 정렬 유지)."""
    if not num.isdigit() or not (100 <= int(num) <= 999):
        sys.exit(f"[ERROR] 번호는 0100~0999 범위만 지원: {num}")

    content = read_ssot()
    lines = content.splitlines()

    sec_start, sec_end = _find_section_range(lines, SEC_HEADER, NEXT_SEC_HEADER)
    tbl_start, tbl_end = _find_main_table_range(lines, sec_start, sec_end)

    # 중복 검사
    num4 = num.zfill(4)
    for i in range(tbl_start + 2, tbl_end):
        if f"| {num4} |" in lines[i] or f"| **{num4}** |" in lines[i]:
            sys.exit(f"[ERROR] {num4}번이 이미 존재함:\n  {lines[i]}")

    # 새 행 작성
    new_row = f"| {num4} | `{pattern}` | {purpose} | `{skill}` |"

    # 정렬: 번호순 삽입 위치 찾기
    insert_at = tbl_end
    for i in range(tbl_start + 2, tbl_end):
        line = lines[i].lstrip()
        if not line.startswith("|"):
            continue
        # 첫 셀에서 4자리 숫자 추출
        cells = [c.strip().strip("*").strip("`").strip() for c in line.split("|")]
        if len(cells) < 2:
            continue
        first = cells[1].split("~")[0].strip().strip("*")
        if first.isdigit() and int(first) > int(num):
            insert_at = i
            break

    lines.insert(insert_at, new_row)
    write_ssot("\n".join(lines) + ("\n" if content.endswith("\n") else ""))
    print(f"[OK] §2.3 표에 추가: {new_row}")
    return 0


def cmd_remove(num: str) -> int:
    """§2.3 표에서 번호 행 제거."""
    if not num.isdigit():
        sys.exit(f"[ERROR] 번호 형식 오류: {num}")

    content = read_ssot()
    lines = content.splitlines()

    sec_start, sec_end = _find_section_range(lines, SEC_HEADER, NEXT_SEC_HEADER)
    tbl_start, tbl_end = _find_main_table_range(lines, sec_start, sec_end)

    num4 = num.zfill(4)
    target_idx = -1
    for i in range(tbl_start + 2, tbl_end):
        if f"| {num4} |" in lines[i] or f"| **{num4}** |" in lines[i]:
            target_idx = i
            break

    if target_idx < 0:
        sys.exit(f"[ERROR] §2.3 표에서 {num4}번을 찾을 수 없음")

    removed = lines.pop(target_idx)
    write_ssot("\n".join(lines) + ("\n" if content.endswith("\n") else ""))
    print(f"[OK] §2.3 표에서 제거:\n  {removed}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="oodoc numbering",
        description="문서 번호 체계(SSOT) 조회/편집",
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("show", help="SSOT 전체 출력 (기본)")
    sub.add_parser("edit", help="SSOT 파일 편집 경로 안내")

    p_add = sub.add_parser("add", help="§2.3 표에 번호 항목 추가")
    p_add.add_argument("num", help="번호 (0100~0999)")
    p_add.add_argument("pattern", help="파일명 패턴 (예: d{SP}0500_사업계획서.md)")
    p_add.add_argument("purpose", help="용도")
    p_add.add_argument("skill", help="생성 스킬")

    p_rm = sub.add_parser("remove", help="§2.3 표에서 번호 항목 제거")
    p_rm.add_argument("num", help="번호")

    args = parser.parse_args()

    if args.cmd in (None, "show"):
        return cmd_show()
    if args.cmd == "edit":
        return cmd_edit()
    if args.cmd == "add":
        return cmd_add(args.num, args.pattern, args.purpose, args.skill)
    if args.cmd == "remove":
        return cmd_remove(args.num)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
