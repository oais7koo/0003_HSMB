#!/usr/bin/env python
"""
oopaper_fix_suffix.py - suffix 폴더(`-NN`) 정규화 (v01)

대상: `^\\d{6}-\\d{4}-\\d{1,3}$` 패턴 폴더 (예: 260222-1851-08)
동작: mtime 기반 신규 정상 FOLDER_ID 발급 → 폴더·내부 파일 prefix 일괄 rename

사용법:
    uv run python .claude/skills/ccpaper/scripts/oopaper_fix_suffix.py [--folder ID] [--batch] [--dry-run] [--lang en|ko]

옵션:
    --folder ID  특정 suffix 폴더만 (예: 260222-1851-08)
    --batch      doctor가 검출한 모든 suffix 폴더 일괄 처리
    --dry-run    계획만 출력
    --lang       언어 (기본 en)

처리:
    1. 폴더 mtime → 신규 FOLDER_ID 발급
    2. 폴더 rename: 260222-1851-08 → 260222-1859 (예시)
    3. 내부 파일 prefix 갱신: 260222-1851-08_00_*.md → 260222-1859_00_*.md
    4. PDF 정규화 (prefix 미적용 PDF만): OG-RAG_*.pdf → 260222-1859_01_OG-RAG.pdf
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple

_HERE = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[4]
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT

FOLDER_ID = re.compile(r"^\d{6}-\d{4}$")
SUFFIX_PATTERN = re.compile(r"^(\d{6}-\d{4})-\d{1,3}$")


def issue_new_id(mtime_ts: float, taken: Set[str]) -> str:
    dt = datetime.fromtimestamp(mtime_ts)
    base = dt.strftime("%y%m%d-%H%M")
    if base not in taken:
        return base
    base_min = dt.hour * 60 + dt.minute
    for offset in range(1, 24 * 60):
        new_min = (base_min + offset) % (24 * 60)
        hh, mm = divmod(new_min, 60)
        cand = f"{dt.strftime('%y%m%d')}-{hh:02d}{mm:02d}"
        if cand not in taken:
            return cand
    raise RuntimeError("FOLDER_ID 충돌 해결 실패")


def normalize_title(stem: str) -> str:
    return re.sub(r"[^\w\-가-힣().]+", "_", stem)[:60].strip("_")


def collect_taken_ids(paper_dir: Path) -> Set[str]:
    return {d.name for d in paper_dir.iterdir() if d.is_dir() and FOLDER_ID.match(d.name)}


def find_suffix_folders(paper_dir: Path) -> List[Path]:
    return sorted(p for p in paper_dir.iterdir()
                  if p.is_dir() and SUFFIX_PATTERN.match(p.name))


def folder_mtime(folder: Path) -> float:
    """폴더 내 PDF mtime > 폴더 자체 mtime > 산출물 md mtime 순서."""
    pdfs = list(folder.glob("*.pdf"))
    if pdfs:
        return min(p.stat().st_mtime for p in pdfs)
    mds = list(folder.glob("*.md"))
    if mds:
        return min(m.stat().st_mtime for m in mds)
    return folder.stat().st_mtime


def plan_rename(folder: Path, new_id: str) -> List[Tuple[Path, str]]:
    """폴더 내 파일별 (원본, 신규 파일명) 계획."""
    old_id = folder.name
    plan: List[Tuple[Path, str]] = []

    for sub in folder.iterdir():
        if not sub.is_file():
            continue
        name = sub.name
        # Case 1: 기존 prefix 갱신 (old_id 포함)
        if name.startswith(f"{old_id}_"):
            new_name = new_id + name[len(old_id):]
            plan.append((sub, new_name))
        # Case 2: PDF 정규화 (prefix 미적용 PDF)
        elif name.lower().endswith(".pdf"):
            clean = normalize_title(sub.stem)
            new_name = f"{new_id}_01_{clean}.pdf"
            plan.append((sub, new_name))
        # Case 3: 기타 — 그대로 유지 (rename 안 함)
        else:
            pass
    return plan


def issue_new_id_from_baseline(baseline: str, taken: Set[str]) -> str:
    """baseline FOLDER_ID(`260222-1851`) 우선 → 충돌 시 분 +1."""
    if baseline not in taken:
        return baseline
    yymmdd, hhmm = baseline.split("-")
    base_min = int(hhmm[:2]) * 60 + int(hhmm[2:])
    for offset in range(1, 24 * 60):
        new_min = (base_min + offset) % (24 * 60)
        hh, mm = divmod(new_min, 60)
        cand = f"{yymmdd}-{hh:02d}{mm:02d}"
        if cand not in taken:
            return cand
    raise RuntimeError("FOLDER_ID 충돌 해결 실패")


def cmd_fix_one(folder: Path, paper_dir: Path, taken: Set[str], dry_run: bool,
                use_mtime: bool = False) -> bool:
    """suffix 폴더 1개 정규화."""
    m = SUFFIX_PATTERN.match(folder.name)
    if not m:
        print(f"[SKIP] {folder.name}: suffix 패턴 아님")
        return False

    pdfs = list(folder.glob("*.pdf"))
    if len(pdfs) >= 2:
        print(f"[SKIP] {folder.name}: PDF {len(pdfs)}개 — split-multi 먼저 실행 필요")
        return False

    if use_mtime:
        new_id = issue_new_id(folder_mtime(folder), taken)
    else:
        # 기본: baseline prefix(`260222-1851`) 보존
        baseline = m.group(1)
        new_id = issue_new_id_from_baseline(baseline, taken)
    taken.add(new_id)
    new_folder = paper_dir / new_id

    print(f"\n## {folder.name} → {new_id}")
    if new_folder.exists():
        print(f"  [ERROR] 신규 폴더 이미 존재: {new_folder}")
        return False

    plan = plan_rename(folder, new_id)
    for src, new_name in plan:
        print(f"  - {src.name} → {new_name}")

    if dry_run:
        return True

    # 실제 적용: 1) 내부 파일 rename → 2) 폴더 rename
    for src, new_name in plan:
        src.rename(folder / new_name)
    folder.rename(new_folder)
    print(f"  [OK] 폴더 rename 완료")
    return True


def cmd_fix_suffix(args) -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    paper_dir = PAPER_BASE / ("12_paper_ko" if args.lang == "ko" else "11_paper_en")
    if not paper_dir.exists():
        print(f"[ERROR] {paper_dir} 없음")
        return 1

    taken = collect_taken_ids(paper_dir)

    if args.batch:
        targets = find_suffix_folders(paper_dir)
        if not targets:
            print(f"[INFO] suffix 폴더 없음 ({paper_dir.name})")
            return 0
        print(f"# fix-suffix {'[DRY-RUN]' if args.dry_run else ''}")
        print(f"paper_dir: {paper_dir}")
        print(f"대상: {len(targets)}개 suffix 폴더\n")
    elif args.folder:
        target = paper_dir / args.folder
        if not target.exists():
            print(f"[ERROR] {target} 없음")
            return 1
        targets = [target]
        print(f"# fix-suffix {'[DRY-RUN]' if args.dry_run else ''}")
        print(f"paper_dir: {paper_dir}\n")
    else:
        print("[ERROR] --folder 또는 --batch 중 하나 필요")
        return 1

    success = 0
    for folder in targets:
        if cmd_fix_one(folder, paper_dir, taken, args.dry_run, use_mtime=args.use_mtime):
            success += 1

    print(f"\n## 요약")
    print(f"처리: {success}/{len(targets)}개")
    if args.dry_run:
        print(f"\n[DRY-RUN] 실제 적용은 --dry-run 제거 후 재실행")
    else:
        print(f"\n다음 단계: `ccpaper update --lang {args.lang}` — paper_list 동기화")
    return 0


def main():
    parser = argparse.ArgumentParser(description="suffix 폴더(-NN) 정규화")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--folder", help="특정 suffix 폴더만 (예: 260222-1851-08)")
    g.add_argument("--batch", action="store_true", help="모든 suffix 폴더 일괄")
    parser.add_argument("--lang", choices=["en", "ko"], default="en")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-mtime", action="store_true",
                        help="baseline 대신 PDF mtime 기반 ID (기본: baseline prefix 보존)")
    args = parser.parse_args()
    sys.exit(cmd_fix_suffix(args))


if __name__ == "__main__":
    main()
