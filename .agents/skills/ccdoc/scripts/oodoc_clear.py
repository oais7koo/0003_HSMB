#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ccdoc clear - 문서 이력 테이블 정리 (5개 초과 행 제거)

대상 범위:
  - 00_doc/d*.md       (00_doc 직접 하위 전체 문서)
  - .claude/skills/oo*/SKILL.md
  - .claude/skills/oo*/references/guide.md
  - .claude/guides/*.md

사용법:
    uv run python .claude/skills/ccdoc/scripts/oodoc_clear.py
    uv run python .claude/skills/ccdoc/scripts/oodoc_clear.py --keep 3
    uv run python .claude/skills/ccdoc/scripts/oodoc_clear.py --dry-run
    uv run python .claude/skills/ccdoc/scripts/oodoc_clear.py --scope 00_doc
    uv run python .claude/skills/ccdoc/scripts/oodoc_clear.py --scope skills
    uv run python .claude/skills/ccdoc/scripts/oodoc_clear.py --scope guides
"""

import sys
import io
import re
import argparse
from pathlib import Path

# Windows cp949 환경에서 UTF-8 출력 강제
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 경로 설정: scripts/ → ccdoc/ → skills/ → .claude/ → PROJECT_ROOT/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DOC_ROOT = PROJECT_ROOT / "00_doc"
CLAUDE_DIR = PROJECT_ROOT / ".claude"

# 이력 섹션 헤더 패턴
HISTORY_SECTION_RE = re.compile(r'^##\s+문서.{0,10}이력', re.MULTILINE)

# 테이블 헤더 + 구분자 패턴 (| 버전 | 날짜 | ...)
TABLE_HEADER_RE = re.compile(
    r'\|\s*버전\s*\|[^\n]*\n\s*\|[-|:\s]+\n',
    re.MULTILINE
)

# 이력 데이터 행 패턴: | v숫자 | ... |
ROW_RE = re.compile(r'^\|\s*v\d[^\n]*\n', re.MULTILINE)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [ERROR] 읽기 실패: {path.name} ({e})")
        return ""


def save_text(path: Path, content: str) -> bool:
    try:
        path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  [ERROR] 저장 실패: {path.name} ({e})")
        return False


def process_history(content: str, keep: int) -> tuple:
    """
    이력 테이블에서 keep개 초과 행 제거.

    Returns:
        (수정된 content, 제거된 행 수)
    """
    # Step 1: 이력 섹션 헤더 위치
    section_m = HISTORY_SECTION_RE.search(content)
    if not section_m:
        return content, 0

    # Step 2: 섹션 이후에서 테이블 헤더(버전|날짜) 찾기
    after_section = section_m.end()
    header_m = TABLE_HEADER_RE.search(content, after_section)
    if not header_m:
        return content, 0

    # 데이터 행 시작 위치 (헤더+구분자 바로 다음)
    data_start = header_m.end()

    # Step 3: 연속된 | v숫자 | 행 수집
    rows = []   # (start, end) 리스트
    pos = data_start

    for m in ROW_RE.finditer(content, pos):
        if m.start() == pos:
            rows.append((m.start(), m.end()))
            pos = m.end()
        else:
            break  # 연속되지 않으면 종료

    if not rows or len(rows) <= keep:
        return content, 0

    # keep개 초과분 제거 (앞 = 최신, 뒤 = 오래된 순)
    removed_count = len(rows) - keep
    delete_start = rows[keep][0]     # (keep+1)번째 행 시작
    delete_end   = rows[-1][1]       # 마지막 행 끝

    new_content = content[:delete_start] + content[delete_end:]
    return new_content, removed_count


def collect_targets(scope: str) -> list:
    """대상 파일 목록 수집"""
    targets = []

    if scope in ("all", "00_doc"):
        # 00_doc/d*.md (flat 구조)
        targets.extend(sorted(DOC_ROOT.glob("d*.md")))
        # 00_doc/sp*/d*.md (SP 서브폴더)
        for sp_dir in sorted(DOC_ROOT.iterdir()):
            if sp_dir.is_dir() and re.match(r'sp\d+', sp_dir.name):
                targets.extend(sorted(sp_dir.glob("d*.md")))

    if scope in ("all", "skills"):
        skills_dir = CLAUDE_DIR / "skills"
        if skills_dir.exists():
            for skill_dir in sorted(skills_dir.iterdir()):
                if skill_dir.is_dir() and skill_dir.name.startswith("oo"):
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        targets.append(skill_md)
                    ref_guide = skill_dir / "references" / "guide.md"
                    if ref_guide.exists():
                        targets.append(ref_guide)

    if scope in ("all", "guides"):
        guides_dir = CLAUDE_DIR / "guides"
        if guides_dir.exists():
            targets.extend(sorted(guides_dir.glob("*.md")))

    return targets


def run_clear(keep: int = 5, dry_run: bool = False, scope: str = "all") -> dict:
    targets = collect_targets(scope)

    stats = {
        "scanned":    0,
        "fixed":      0,
        "skipped":    0,
        "no_history": 0,
        "errors":     0,
    }
    fixed_files = []

    mode_label = "[DRY-RUN] " if dry_run else ""
    print(f"[ccdoc clear] {mode_label}이력 정리 시작")
    print(f"  keep={keep}  scope={scope}  대상={len(targets)}개")
    print()

    for path in targets:
        stats["scanned"] += 1
        try:
            rel = path.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = path

        content = load_text(path)
        if not content:
            stats["errors"] += 1
            continue

        if not HISTORY_SECTION_RE.search(content):
            stats["no_history"] += 1
            continue

        new_content, removed = process_history(content, keep)

        if removed > 0:
            print(f"  [FIX] {rel}")
            print(f"        이력 {removed}개 제거 → {keep}개 유지")
            if not dry_run:
                if save_text(path, new_content):
                    stats["fixed"] += 1
                    fixed_files.append(str(rel))
                else:
                    stats["errors"] += 1
            else:
                stats["fixed"] += 1
                fixed_files.append(str(rel))
        else:
            stats["skipped"] += 1

    # 결과 요약
    print()
    print("-" * 50)
    print(
        f"결과: 스캔 {stats['scanned']} | "
        f"수정 {stats['fixed']} | "
        f"정상 {stats['skipped']} | "
        f"이력없음 {stats['no_history']} | "
        f"오류 {stats['errors']}"
    )

    if fixed_files:
        print("\n수정 파일 목록:")
        for f in fixed_files:
            print(f"  - {f}")

    if dry_run:
        print("\n  ※ dry-run: 실제 파일 변경 없음")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="ccdoc clear - 문서 이력 테이블 정리"
    )
    parser.add_argument(
        "--keep", type=int, default=5,
        help="유지할 이력 개수 (기본: 5)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="변경 대상만 표시 (파일 수정 없음)"
    )
    parser.add_argument(
        "--scope",
        choices=["all", "00_doc", "skills", "guides"],
        default="all",
        help="정리 범위 (기본: all)"
    )
    args = parser.parse_args()

    run_clear(keep=args.keep, dry_run=args.dry_run, scope=args.scope)


if __name__ == "__main__":
    main()
