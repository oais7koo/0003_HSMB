#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""oodoc check - 문서 정합성 통합 검사

Part 1: d0001~d0010 교차 정합성 (문서 간 일관성 검증)
Part 2: SP 폴더 귀속 검사 (파일이 올바른 SP 폴더에 있는지)

사용법:
    uv run python .claude/skills/oodoc/scripts/oodoc_check.py
    uv run python .claude/skills/oodoc/scripts/oodoc_check.py sp04
    uv run python .claude/skills/oodoc/scripts/oodoc_check.py --fix
"""

import sys
import io
import re
import argparse
from pathlib import Path

# Windows cp949 환경에서 UTF-8 출력 강제
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트: scripts/ → oodoc/ → skills/ → .claude/ → D:/1_oo/
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DOC_ROOT = PROJECT_ROOT / "00_doc"

# --- 상수 ---
REQUIRED_DOCS = ["d0001_prd.md", "d0002_plan.md", "d0004_todo.md", "d0010_history.md"]
HISTORY_PATTERN = re.compile(r'^#{1,6}\s+.*이력', re.MULTILINE)
HISTORY_ROW_PATTERN = re.compile(r'^\|\s*v\d+', re.MULTILINE)
TODO_ID_PATTERN = re.compile(r'\b(T\d+|A\d+|D\d+|S\d+)\b')
LINK_PATTERN = re.compile(r'00_doc/([^\s\)\"\'>\n]+\.md)')
PLACEHOLDER_KEYWORDS = ['(작성 예정)', '(미작성)', 'TBD', '추후 작성']
EMPTY_THRESHOLD = 300  # bytes


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def get_sp_dir(sp_num: int) -> Path:
    """SP별 문서 디렉토리 반환 (00_doc/sp00/, 00_doc/sp04/ 등)"""
    return DOC_ROOT / f"sp{sp_num:02d}"


# ============================================================
# Part 1: d0001~d0010 교차 정합성
# ============================================================

def _sp_num(sp_dir_or_num) -> int:
    """SP 번호 추출. Path인 경우 폴더명에서, int/str인 경우 직접 반환"""
    if isinstance(sp_dir_or_num, Path):
        m = re.match(r'sp(\d+)', sp_dir_or_num.name)
        return int(m.group(1)) if m else 0
    return int(sp_dir_or_num)


def _required_docs(sp_num: int) -> list:
    """SP 번호에 맞는 필수 문서 목록 반환"""
    if sp_num == 0:
        return REQUIRED_DOCS  # d0001_prd.md, d0002_plan.md, d0004_todo.md, d0010_history.md
    return [
        f"d{sp_num}0001_prd.md",
        f"d{sp_num}0002_plan.md",
        f"d{sp_num}0004_todo.md",
        f"d{sp_num}0010_history.md",
    ]


def check_required_docs(sp_num: int) -> tuple:
    ok, warn, err = [], [], []
    sp_dir = get_sp_dir(sp_num)
    required = _required_docs(sp_num)
    existing = [req for req in required if (sp_dir / req).exists()]

    # 필수 문서가 하나도 없으면 기술 문서 전용 SP로 간주 (ERROR 대신 INFO)
    if not existing and sp_num != 0:
        ok.append(f"  [INFO]  핵심 관리 문서 없음 (기술 문서 전용 SP로 간주, 생성 권장)")
        return ok, warn, err

    for req in required:
        if (sp_dir / req).exists():
            ok.append(f"  [OK]    {req} 존재")
        else:
            err.append(f"  [ERROR] {req} 필수 문서 없음")
    return ok, warn, err


def check_history_tables(sp_num: int) -> tuple:
    """필수 문서(d0001~d0010)의 이력 테이블만 검사 (일반 분석 문서 제외)"""
    ok, warn, err = [], [], []
    sp_dir = get_sp_dir(sp_num)
    target_files = [sp_dir / req for req in _required_docs(sp_num) if (sp_dir / req).exists()]
    for md_file in target_files:
        content = load_text(md_file)
        if not HISTORY_PATTERN.search(content):
            warn.append(f"  [WARN]  {md_file.name}: 이력 테이블 없음")
        else:
            rows = HISTORY_ROW_PATTERN.findall(content)
            if len(rows) > 5:
                warn.append(f"  [WARN]  {md_file.name}: 이력 {len(rows)}개 (5개 초과)")
    return ok, warn, err


def check_todo_history_sync(sp_num: int) -> tuple:
    ok, warn, err = [], [], []
    sp_dir = get_sp_dir(sp_num)
    if sp_num == 0:
        todo_path = sp_dir / "d0004_todo.md"
        history_path = sp_dir / "d0010_history.md"
    else:
        todo_path = sp_dir / f"d{sp_num}0004_todo.md"
        history_path = sp_dir / f"d{sp_num}0010_history.md"
    if not (todo_path.exists() and history_path.exists()):
        return ok, warn, err

    todo_content = load_text(todo_path)
    history_content = load_text(history_path)

    # 해결된 이슈 섹션 추출
    m = re.search(r'### 해결된 이슈.*?(?=\n###|\Z)', todo_content, re.DOTALL)
    resolved_ids = set(TODO_ID_PATTERN.findall(m.group(0))) if m else set()
    history_ids = set(TODO_ID_PATTERN.findall(history_content))

    missing = resolved_ids - history_ids
    if missing:
        for tid in sorted(missing):
            warn.append(f"  [WARN]  {tid}: d0004 해결됨 → d0010 미기록")
    else:
        ok.append("  [OK]    d0004↔d0010 이슈 동기화 정상")
    return ok, warn, err


def check_cross_references(sp_num: int) -> tuple:
    ok, warn, err = [], [], []
    sp_dir = get_sp_dir(sp_num)
    if not sp_dir.exists():
        return ok, warn, err
    if sp_num == 0:
        pattern = "d0*.md"
    else:
        pattern = f"d{sp_num}*.md"
    for md_file in sorted(sp_dir.glob(pattern)):
        content = load_text(md_file)
        for line in content.splitlines():
            # 미생성/없음 명시 행은 제외
            if any(kw in line for kw in ['미생성', '(없음)', '(미생성)']):
                continue
            for link in LINK_PATTERN.findall(line):
                # 플레이스홀더(대문자 포함) 제외
                if any(c.isupper() for c in link.split('/')[-1]):
                    continue
                target = PROJECT_ROOT / "00_doc" / link
                if not target.exists():
                    warn.append(f"  [WARN]  {md_file.name}: 깨진 참조 → 00_doc/{link}")
    return ok, warn, err


def check_todo_index_detail_sync(sp_num: int) -> tuple:
    """R163: todo/ 폴더 인덱스↔상세 정합성 체크.
    - 대기 ToDo 표(`| R### |`)의 ID마다 todo/{ID}.md 존재 + 상태/우선순위 일치
    - 활성(OPEN/IN_PROGRESS/HOLD) 상세가 인덱스 대기 ToDo에 등재되어 있는지
    """
    ok, warn, err = [], [], []
    if sp_num == 0:
        return ok, warn, err
    sp_dir = get_sp_dir(sp_num)
    todo_dir = sp_dir / "todo"
    index_file = sp_dir / f"d{sp_num}0004_todo.md"
    if not todo_dir.exists() or not index_file.exists():
        return ok, warn, err
    idx_text = load_text(index_file)
    # 대기 ToDo 표 행 파싱: | ID | 우선순위 | 상태 | 제목 | 상세 |
    row_re = re.compile(
        r"^\|\s*(R\d+(?:-\d+)?(?:\.\d+)?)\s*\|\s*([^|]+?)\s*\|\s*([A-Z_]+)\s*\|",
        re.MULTILINE,
    )
    index_rows = {m.group(1): (m.group(2).strip(), m.group(3).strip()) for m in row_re.finditer(idx_text)}
    # 상세 파일 헤더 파싱
    head_re = re.compile(r"^>\s*우선순위:\s*([^|]+?)\s*\|\s*상태:\s*([A-Z_]+)", re.MULTILINE)
    detail_states = {}  # id → (priority, state)
    for fp in todo_dir.glob("*.md"):
        if fp.stem in ("_template", "README"):
            continue
        text = load_text(fp)
        m = head_re.search(text)
        if m:
            detail_states[fp.stem] = (m.group(1).strip(), m.group(2).strip())
    # 1) 인덱스 ID마다 상세 존재 + 일치
    for tid, (idx_pri, idx_state) in index_rows.items():
        if tid not in detail_states:
            warn.append(f"  [WARN]  인덱스 대기 ToDo {tid}: todo/{tid}.md 없음")
            continue
        d_pri, d_state = detail_states[tid]
        if d_state != idx_state:
            warn.append(f"  [WARN]  {tid}: 상태 불일치 (인덱스={idx_state} / 상세={d_state})")
        if d_pri.upper() != idx_pri.upper():
            warn.append(f"  [WARN]  {tid}: 우선순위 불일치 (인덱스={idx_pri} / 상세={d_pri})")
    # 2) 활성 상세이지만 인덱스 미참조
    for tid, (_, d_state) in detail_states.items():
        if d_state in ("OPEN", "IN_PROGRESS", "HOLD") and tid not in index_rows:
            warn.append(f"  [WARN]  활성 상세 {tid}({d_state})가 인덱스 대기 ToDo에 미등재")
    if not warn:
        ok.append(f"  [OK]    todo/ 인덱스↔상세 정합성 일치 ({len(detail_states)}개 상세, {len(index_rows)}개 대기)")
    return ok, warn, err


def part1_cross_consistency(sp_num: int) -> tuple:
    all_ok, all_warn, all_err = [], [], []
    for fn in [check_required_docs, check_history_tables,
               check_todo_history_sync, check_cross_references,
               check_todo_index_detail_sync]:
        o, w, e = fn(sp_num)
        all_ok.extend(o)
        all_warn.extend(w)
        all_err.extend(e)
    return all_ok, all_warn, all_err


# ============================================================
# Part 2: SP 폴더 귀속 검사
# ============================================================

def _is_core_doc(fname: str, sp_num: int) -> bool:
    """핵심 관리 문서 여부 (d*0001, d*0004, d*0010)"""
    sp_str = str(sp_num) if sp_num > 0 else "0"
    m = re.match(rf'd{sp_str}(\d{{4}})_', fname)
    if m:
        return m.group(1) in {'0001', '0004', '0010'}
    # SP00: d0001_prd.md 형태
    m0 = re.match(r'd(\d{4})_', fname)
    if m0 and sp_num == 0:
        return m0.group(1) in {'0001', '0004', '0010'}
    return False


def part2_attribution_check(sp_num: int) -> tuple:
    """SP 서브폴더 내 파일의 품질 검사"""
    ok, warn, err = [], [], []
    sp_dir = get_sp_dir(sp_num)
    if not sp_dir.exists():
        return ok, warn, err

    if sp_num == 0:
        pattern = "d0*.md"
    else:
        pattern = f"d{sp_num}*.md"

    for md_file in sorted(sp_dir.glob(pattern)):
        fname = md_file.name
        size = md_file.stat().st_size
        content = load_text(md_file)
        if size < EMPTY_THRESHOLD:
            # 핵심 문서(d*0001, d*0004, d*0010)만 WARN, 나머지 선택 문서는 INFO
            if _is_core_doc(fname, sp_num):
                warn.append(f"  [WARN]  {fname}: 내용 부족 ({size}B)")
            else:
                ok.append(f"  [OK]    {fname} (선택문서 미작성 {size}B)")
        elif any(kw in content for kw in PLACEHOLDER_KEYWORDS):
            warn.append(f"  [WARN]  {fname}: 플레이스홀더 존재")
        else:
            ok.append(f"  [OK]    {fname}")
    return ok, warn, err


# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="oodoc check - 문서 정합성 통합 검사")
    parser.add_argument("sp", nargs="?", help="SP 번호 (예: sp04 또는 04)")
    parser.add_argument("--fix", action="store_true", help="오류 조치 방안 출력")
    args = parser.parse_args()

    # 대상 SP 번호 결정
    if args.sp:
        sp_str = args.sp.replace("sp", "")
        sp_nums = [int(sp_str)]
    else:
        # 00_doc/sp??/ 서브폴더에서 SP 번호 자동 감지
        sp_set = set()
        if DOC_ROOT.exists():
            for sp_dir in DOC_ROOT.iterdir():
                if sp_dir.is_dir():
                    m = re.match(r'sp(\d+)', sp_dir.name)
                    if m:
                        sp_set.add(int(m.group(1)))
        sp_nums = sorted(sp_set) if sp_set else [0]

    total_ok = total_warn = total_error = 0
    all_issues = []

    for sp_num in sp_nums:
        print(f"\n{'='*60}")
        print(f"== SP{sp_num:02d} 정합성 검사 ==")
        print(f"{'='*60}")

        # Part 1
        print("\n[Part 1] d0001~d0010 교차 정합성")
        print("-" * 40)
        ok1, warn1, err1 = part1_cross_consistency(sp_num)
        for line in ok1 + warn1 + err1:
            print(line)

        # Part 2
        print("\n[Part 2] SP 문서 품질 검사")
        print("-" * 40)
        ok2, warn2, err2 = part2_attribution_check(sp_num)
        for line in ok2 + warn2 + err2:
            print(line)

        sp_ok = len(ok1) + len(ok2)
        sp_warn = len(warn1) + len(warn2)
        sp_err = len(err1) + len(err2)
        total_ok += sp_ok
        total_warn += sp_warn
        total_error += sp_err

        print(f"\n  소계: OK:{sp_ok} | WARN:{sp_warn} | ERROR:{sp_err}")
        all_issues.extend(err1 + err2 + warn1 + warn2)

    # 전체 요약
    print(f"\n{'='*60}")
    print(f"전체 결과: OK:{total_ok} | WARN:{total_warn} | ERROR:{total_error}")

    if total_error > 0:
        print("[FAIL] 오류 발견 - 조치 필요")
        if args.fix:
            print("\n[--fix 조치 권고]")
            for issue in all_issues:
                print(f"  -> {issue.strip()}")
            print("\n  ※ 자동 수정 없음. 직접 조치 후 재검사 권장.")
    elif total_warn > 0:
        print("[WARN] 경고 있음 - 검토 권장")
    else:
        print("[PASS] 모든 검사 통과")

    sys.exit(1 if total_error > 0 else 0)


if __name__ == "__main__":
    main()
