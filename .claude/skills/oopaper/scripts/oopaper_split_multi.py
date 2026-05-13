#!/usr/bin/env python
"""
oopaper_split_multi.py - 다중 PDF 폴더 분리 (v01)

원칙: 1 폴더 1 논문. 한 FOLDER_ID 폴더에 PDF가 2개 이상이면
첫 번째는 그대로 두고 나머지는 신규 FOLDER_ID 폴더로 분리한다.
신규 ID는 PDF 파일의 mtime을 기반으로 발급 (충돌 시 분 +1).

사용법:
    uv run python .claude/skills/oopaper/scripts/oopaper_split_multi.py --folder ID [--lang en|ko] [--dry-run]

주의:
    - suffix 부착(-NN) 절대 금지
    - 분리 후 paper_list 동기화는 `oopaper update --lang en` 수동 실행
    - 분리 전 산출물(서머리·전문 등)은 첫 번째 PDF에만 귀속됨 (재처리 권장)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple

_HERE = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[4]
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT

FOLDER_ID = re.compile(r"^\d{6}-\d{4}$")


def issue_new_id(mtime_ts: float, taken: Set[str]) -> str:
    """mtime 기반 신규 FOLDER_ID 발급 (충돌 시 분 +1)."""
    dt = datetime.fromtimestamp(mtime_ts)
    base = dt.strftime("%y%m%d-%H%M")
    if base not in taken:
        return base
    base_minutes = dt.hour * 60 + dt.minute
    for offset in range(1, 24 * 60):
        new_minute = (base_minutes + offset) % (24 * 60)
        hh, mm = divmod(new_minute, 60)
        cand = f"{dt.strftime('%y%m%d')}-{hh:02d}{mm:02d}"
        if cand not in taken:
            return cand
    raise RuntimeError("FOLDER_ID 충돌 해결 실패 (24시간 분 모두 사용)")


def normalize_title(stem: str) -> str:
    """파일명 정규화: 공백·특수문자 → 언더스코어, 60자 컷."""
    return re.sub(r"[^\w\-가-힣().]+", "_", stem)[:60].strip("_")


def collect_taken_ids(paper_dir: Path) -> Set[str]:
    return {d.name for d in paper_dir.iterdir() if d.is_dir() and FOLDER_ID.match(d.name)}


def cmd_split(args) -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    paper_dir = PAPER_BASE / ("12_paper_ko" if args.lang == "ko" else "11_paper_en")
    target = paper_dir / args.folder

    if not target.exists():
        print(f"[ERROR] {target} 없음")
        return 1
    if not target.is_dir():
        print(f"[ERROR] {target} 디렉토리 아님")
        return 1

    pdfs = sorted(target.glob("*.pdf"))
    if len(pdfs) < 2:
        print(f"[INFO] {args.folder}: PDF {len(pdfs)}개 — 분리 불필요")
        return 0

    print(f"# split-multi: {args.folder} (PDF {len(pdfs)}개){' [DRY-RUN]' if args.dry_run else ''}\n")
    print(f"paper_dir: {paper_dir}")
    print(f"대상 폴더: {target}\n")

    taken = collect_taken_ids(paper_dir)
    keep = pdfs[0]
    print(f"## 유지: `{keep.name}`")
    print(f"  → 폴더: `{args.folder}` (현 위치)\n")

    plan: List[Tuple[Path, str, Path, str]] = []
    for pdf in pdfs[1:]:
        new_id = issue_new_id(pdf.stat().st_mtime, taken)
        taken.add(new_id)
        new_dir = paper_dir / new_id
        clean = normalize_title(pdf.stem)
        new_pdf = f"{new_id}_01_{clean}.pdf"
        plan.append((pdf, new_id, new_dir, new_pdf))
        print(f"## 분리: `{pdf.name}`")
        print(f"  → 신규 폴더: `{new_id}/`")
        print(f"  → 정규화 파일명: `{new_pdf}`")
        print(f"  → mtime 기반: {datetime.fromtimestamp(pdf.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
        print()

    if args.dry_run:
        print(f"\n[DRY-RUN] {len(plan)}개 분리 예정. 실제 적용은 --dry-run 제거 후 재실행.")
        return 0

    # 실제 적용
    moved = 0
    for src, nid, ndir, npname in plan:
        try:
            ndir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            print(f"[SKIP] {nid} 이미 존재")
            continue
        shutil.move(str(src), str(ndir / npname))
        print(f"[OK] {src.name} → {nid}/{npname}")
        moved += 1

    # 1번째 PDF 정규화 (필요 시)
    if not keep.name.startswith(f"{args.folder}_01_"):
        clean = normalize_title(keep.stem)
        expected = f"{args.folder}_01_{clean}.pdf"
        new_path = target / expected
        if not new_path.exists():
            keep.rename(new_path)
            print(f"[OK] 1번째 PDF 정규화: {keep.name} → {expected}")

    print(f"\n## 완료")
    print(f"분리: {moved}개 폴더 신규 발급")
    print(f"\n다음 단계 권장:")
    print(f"  1. `oopaper update --lang {args.lang}` — paper_list 동기화")
    print(f"  2. `oopaper run --folder <NEW_ID>` — 신규 폴더별 산출물 생성")
    return 0


def main():
    parser = argparse.ArgumentParser(description="다중 PDF 폴더 분리 (1폴더 1논문 정책)")
    parser.add_argument("--folder", required=True, help="대상 FOLDER_ID")
    parser.add_argument("--lang", choices=["en", "ko"], default="en")
    parser.add_argument("--dry-run", action="store_true", help="계획만 출력")
    args = parser.parse_args()
    sys.exit(cmd_split(args))


if __name__ == "__main__":
    main()
