#!/usr/bin/env python
"""
oopaper_auto.py - ccpaper 자동화 헬퍼 (v04+)

토큰 절감을 위해 Claude AI 대신 로컬 Python으로 처리하는 작업들.

서브명령어:
  organize  : 00_down/*.pdf → YYMMDD-HHMM 폴더 자동 생성·이동
  dedup     : 폴더 간 동일 논문 검출 (제목 정규화 + fuzzy)
  meta      : PDF 메타데이터 추출 (제목/저자/연도/DOI/arXiv)
  ref-match : 참고문헌 내부 폴더 매칭 (rapidfuzz)

실행 예:
  uv run python .claude/skills/ccpaper/scripts/oopaper_auto.py organize --dry-run
  uv run python .claude/skills/ccpaper/scripts/oopaper_auto.py dedup
  uv run python .claude/skills/ccpaper/scripts/oopaper_auto.py meta --folder 260428-0001
"""
import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 자동 감지
_HERE = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[4]  # scripts → ccpaper → skills → .claude → root
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
DOWN_DIR = PAPER_BASE / "00_down"
PAPER_DIR = PAPER_BASE / "11_paper_en"

FOLDER_PATTERN = re.compile(r"^\d{6}-\d{4}$")


# ─────────────────────────────────────────
# 공통: 제목 정규화
# ─────────────────────────────────────────
def normalize_title(title: str) -> str:
    """비교용 제목 정규화: 소문자 + 영숫자만."""
    if not title:
        return ""
    return re.sub(r"[^a-z0-9]+", "", title.lower())


# ─────────────────────────────────────────
# 1. organize: 00_down → YYMMDD-HHMM 폴더 자동 이동
# ─────────────────────────────────────────
def cmd_organize(args):
    """00_down/*.pdf 파일을 YYMMDD-HHMM/ 폴더로 자동 이동."""
    print(f"# ccpaper organize - 00_down 자동 정리\n")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if not DOWN_DIR.exists():
        print(f"[INFO] 00_down 폴더 없음: {DOWN_DIR}")
        return

    pdfs = sorted(DOWN_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"[INFO] 00_down에 PDF 없음.")
        return

    PAPER_DIR.mkdir(parents=True, exist_ok=True)

    # 기존 폴더 ID 수집 (충돌 방지)
    existing_ids = {d.name for d in PAPER_DIR.iterdir()
                    if d.is_dir() and FOLDER_PATTERN.match(d.name)}

    print(f"## 대상: {len(pdfs)}개 PDF\n")

    moved = 0
    skipped = 0

    for i, pdf in enumerate(pdfs):
        # 새 폴더 ID = 현재 시각 + 인덱스 (같은 분 내 다중 PDF 처리)
        now = datetime.now()
        base_id = now.strftime("%y%m%d-%H%M")

        # 충돌 시 마지막 4자리(분) 증가
        folder_id = base_id
        offset = 0
        while folder_id in existing_ids:
            offset += 1
            new_minute = (now.hour * 60 + now.minute + offset) % (24 * 60)
            hh, mm = divmod(new_minute, 60)
            folder_id = f"{now.strftime('%y%m%d')}-{hh:02d}{mm:02d}"
        existing_ids.add(folder_id)

        # 파일명 정규화: 공백→언더스코어, 특수문자 제거
        clean_name = re.sub(r"[^\w\-가-힣().]+", "_", pdf.stem)[:60].strip("_")
        new_name = f"{folder_id}_01_{clean_name}.pdf"

        target_dir = PAPER_DIR / folder_id
        target_path = target_dir / new_name

        if args.dry_run:
            print(f"- [DRY] `{pdf.name}` → `{folder_id}/{new_name}`")
            skipped += 1
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pdf), str(target_path))
        print(f"- [OK] `{pdf.name}` → `{folder_id}/`")
        moved += 1

    print(f"\n## 요약")
    print(f"- 이동: {moved}개")
    print(f"- 건너뜀: {skipped}개")
    if moved:
        print(f"\n**→ `ccpaper sync-list` 실행하여 paper_list.md 동기화하세요**")


# ─────────────────────────────────────────
# 2. dedup: 폴더 간 동일 논문 검출
# ─────────────────────────────────────────
def _extract_folder_title(folder: Path) -> str:
    """폴더의 서머리 또는 PDF 파일명에서 제목 추출."""
    summary_files = list(folder.glob("*_00_*_서머리.md"))
    if summary_files:
        try:
            content = summary_files[0].read_text(encoding="utf-8")
            m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if m:
                title = m.group(1).strip()
                title = re.sub(r"^서머리[:\s]*", "", title)
                return title
        except Exception:
            pass

    # PDF 파일명에서 추출
    pdfs = list(folder.glob("*_01_*.pdf"))
    if pdfs:
        m = re.match(r"\d{6}-\d{4}_01_(.+)\.pdf", pdfs[0].name)
        if m:
            return m.group(1).replace("_", " ")

    return folder.name


def cmd_dedup(args):
    """폴더 간 동일 논문(중복) 검출."""
    print(f"# ccpaper dedup - 폴더 간 중복 검출\n")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if not PAPER_DIR.exists():
        print(f"[ERROR] {PAPER_DIR} 없음")
        return

    folders = sorted([d for d in PAPER_DIR.iterdir()
                      if d.is_dir() and FOLDER_PATTERN.match(d.name)])
    print(f"총 {len(folders)}개 폴더 검사\n")

    # rapidfuzz 사용 시도 (없으면 정규화 비교만)
    try:
        from rapidfuzz import fuzz
        has_fuzz = True
    except ImportError:
        has_fuzz = False
        print("[WARN] rapidfuzz 없음 → 정규화 일치만 검출 (uv add rapidfuzz 권장)\n")

    # 정규화 제목 매핑
    title_map = {}  # normalized_title → [folder_id, ...]
    raw_titles = {}  # folder_id → raw title

    for folder in folders:
        title = _extract_folder_title(folder)
        norm = normalize_title(title)
        raw_titles[folder.name] = title
        if norm:
            title_map.setdefault(norm, []).append(folder.name)

    # 1. 정확한 중복
    exact_dups = {k: v for k, v in title_map.items() if len(v) > 1}

    print(f"## 정확한 중복 (정규화 일치): {len(exact_dups)}건\n")
    for norm, ids in list(exact_dups.items())[:30]:
        first_id = ids[0]
        print(f"- `{first_id}` 외 {len(ids)-1}건: {raw_titles[first_id][:80]}")
        for fid in ids[1:]:
            print(f"  - `{fid}`")

    # 2. fuzzy 유사 (옵션)
    if has_fuzz and args.fuzzy:
        print(f"\n## 유사 제목 (fuzzy ≥ {args.threshold})\n")
        seen_pairs = set()
        items = list(title_map.items())
        fuzzy_count = 0
        for i, (n1, ids1) in enumerate(items):
            for n2, ids2 in items[i+1:]:
                if n1 == n2:
                    continue
                score = fuzz.ratio(n1, n2)
                if score >= args.threshold:
                    pair = tuple(sorted([ids1[0], ids2[0]]))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    fuzzy_count += 1
                    if fuzzy_count <= 50:
                        print(f"- [{score:.0f}%] `{ids1[0]}` ↔ `{ids2[0]}`")
                        print(f"    {raw_titles[ids1[0]][:70]}")
                        print(f"    {raw_titles[ids2[0]][:70]}")
        print(f"\n총 {fuzzy_count}쌍 유사")

    print(f"\n## 요약")
    print(f"- 폴더 수: {len(folders)}")
    print(f"- 고유 제목: {len(title_map)}")
    print(f"- 정확 중복 그룹: {len(exact_dups)}")
    if exact_dups:
        total_dup_folders = sum(len(v) - 1 for v in exact_dups.values())
        print(f"- 중복 폴더 (병합 가능): {total_dup_folders}")


# ─────────────────────────────────────────
# 3. meta: PDF 메타데이터 추출
# ─────────────────────────────────────────
def cmd_meta(args):
    """PDF 메타데이터(제목/저자/연도/DOI/arXiv) 추출."""
    print(f"# ccpaper meta - PDF 메타데이터 추출\n")

    try:
        import pdfplumber
    except ImportError:
        print("[ERROR] pdfplumber 필요: uv add pdfplumber")
        return

    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
    else:
        target_folders = sorted([d for d in PAPER_DIR.iterdir()
                                 if d.is_dir() and FOLDER_PATTERN.match(d.name)])

    print(f"대상: {len(target_folders)}개 폴더\n")

    DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", re.I)
    ARXIV_RE = re.compile(r"\barXiv:\s*(\d{4}\.\d{4,5})", re.I)
    YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

    extracted = 0
    for folder in target_folders[:args.limit] if args.limit else target_folders:
        pdfs = list(folder.glob("*_01_*.pdf"))
        if not pdfs:
            continue
        try:
            with pdfplumber.open(pdfs[0]) as pdf:
                first_page = pdf.pages[0].extract_text() or ""
        except Exception as e:
            print(f"- [FAIL] `{folder.name}`: {e}")
            continue

        head = first_page[:2000]
        doi = DOI_RE.search(head)
        arxiv = ARXIV_RE.search(head)
        years = YEAR_RE.findall(head)
        # 첫 줄 = 제목 후보
        title = next((ln.strip() for ln in head.split("\n") if len(ln.strip()) > 15), "")[:120]

        meta = {
            "folder": folder.name,
            "title": title,
            "doi": doi.group(1) if doi else "",
            "arxiv": arxiv.group(1) if arxiv else "",
            "year": years[0] if years else "",
        }
        print(f"- `{folder.name}`")
        print(f"    제목: {meta['title'][:80]}")
        if meta["doi"]:
            print(f"    DOI: {meta['doi']}")
        if meta["arxiv"]:
            print(f"    arXiv: {meta['arxiv']}")
        if meta["year"]:
            print(f"    연도: {meta['year']}")
        extracted += 1

    print(f"\n## 요약: {extracted}개 추출")


# ─────────────────────────────────────────
# 4. ref-match-fuzzy: 참고문헌 내부 매칭 (rapidfuzz 강화)
# ─────────────────────────────────────────
def cmd_ref_match_fuzzy(args):
    """rapidfuzz 기반 참고문헌 → 폴더 매칭."""
    print(f"# ccpaper ref-match-fuzzy\n")

    try:
        from rapidfuzz import process, fuzz
    except ImportError:
        print("[ERROR] rapidfuzz 필요: uv add rapidfuzz")
        return

    if not PAPER_DIR.exists():
        print(f"[ERROR] {PAPER_DIR} 없음")
        return

    # 인덱스 구축: 정규화 제목 → 폴더ID
    folders = sorted([d for d in PAPER_DIR.iterdir()
                      if d.is_dir() and FOLDER_PATTERN.match(d.name)])
    title_to_folder = {}
    for f in folders:
        t = _extract_folder_title(f)
        n = normalize_title(t)
        if n:
            title_to_folder.setdefault(n, []).append(f.name)
    norms = list(title_to_folder.keys())

    target_folders = [PAPER_DIR / args.folder] if args.folder else folders[:args.limit] if args.limit else folders
    matched_total = 0

    for folder in target_folders:
        summaries = list(folder.glob("*_00_*_서머리.md"))
        if not summaries:
            continue
        try:
            content = summaries[0].read_text(encoding="utf-8")
        except Exception:
            continue

        # ## 참고 논문 → ### 외부 섹션 추출
        m = re.search(r"###\s*외부.*?(?=###|\Z)", content, re.DOTALL)
        if not m:
            continue

        ref_lines = [ln.strip("- ").strip() for ln in m.group(0).split("\n")
                     if ln.strip().startswith("-")]
        if not ref_lines:
            continue

        matches = []
        for ref in ref_lines:
            n_ref = normalize_title(ref)
            if not n_ref:
                continue
            best = process.extractOne(n_ref, norms, scorer=fuzz.partial_ratio,
                                      score_cutoff=args.threshold)
            if best:
                norm_match, score, _ = best
                folder_ids = title_to_folder[norm_match]
                matches.append((ref[:80], folder_ids[0], score))

        if matches:
            print(f"\n## `{folder.name}`: {len(matches)}건 매칭")
            for ref, fid, score in matches[:10]:
                print(f"  - [{score:.0f}%] → `{fid}` :: {ref}")
            matched_total += len(matches)

    print(f"\n## 요약: {matched_total}건 매칭")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="oopaper_auto", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_org = sub.add_parser("organize", help="00_down → YYMMDD-HHMM 폴더 자동 이동")
    p_org.add_argument("--dry-run", action="store_true")

    p_dedup = sub.add_parser("dedup", help="폴더 간 중복 검출")
    p_dedup.add_argument("--fuzzy", action="store_true", help="rapidfuzz 유사도 비교")
    p_dedup.add_argument("--threshold", type=int, default=92, help="fuzzy 임계값 (0-100)")

    p_meta = sub.add_parser("meta", help="PDF 메타데이터 추출")
    p_meta.add_argument("--folder", type=str, help="특정 폴더만")
    p_meta.add_argument("--limit", type=int, help="최대 N개")

    p_rm = sub.add_parser("ref-match-fuzzy", help="rapidfuzz 기반 참고문헌 매칭")
    p_rm.add_argument("--folder", type=str)
    p_rm.add_argument("--limit", type=int)
    p_rm.add_argument("--threshold", type=int, default=85)

    args = parser.parse_args()

    if args.cmd == "organize":
        cmd_organize(args)
    elif args.cmd == "dedup":
        cmd_dedup(args)
    elif args.cmd == "meta":
        cmd_meta(args)
    elif args.cmd == "ref-match-fuzzy":
        cmd_ref_match_fuzzy(args)


if __name__ == "__main__":
    main()
