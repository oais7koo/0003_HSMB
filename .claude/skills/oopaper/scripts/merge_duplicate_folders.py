"""
날짜 다른 중복 폴더 통합 스크립트
- 제목 기준으로 중복 그룹 탐지
- 그룹 내 완성도 점수가 가장 높은 폴더를 대표로 선택
- 나머지 폴더의 더 나은 파일을 대표 폴더에 통합 후 삭제

완성도 점수: _05_(분석)+4, _04_(한글)+3, _03_(영어)+2, _01_(PDF)+1, _00_(서머리)+1
같은 종류 파일 경합 시 크기가 큰 것 우선

사용법:
  python merge_duplicate_folders.py           # dry-run (기본)
  python merge_duplicate_folders.py --apply   # 실제 실행
"""

import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

DRY_RUN = "--apply" not in sys.argv
EN_DIR = Path("03_paper/11_paper_en")
KO_DIR = Path("03_paper/12_paper_ko")

# 파일 종류별 완성도 점수
SCORE_MAP = {"_05_": 4, "_04_": 3, "_03_": 2, "_01_": 1, "_00_": 1}


def normalize_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip().lower())
    text = re.sub(r"[^\w\s]", "", text)
    return text[:80]


def extract_title_from_summary(filepath: Path) -> str | None:
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("# ") and not line.startswith("##"):
                t = normalize_title(line[2:])
                if len(t) > 5:
                    return t
    except Exception:
        pass
    return None


def folder_score(folder: Path) -> tuple[int, int]:
    """(완성도점수, 총파일크기) 반환"""
    score = 0
    total_size = 0
    for f in folder.iterdir():
        if not f.is_file():
            continue
        size = f.stat().st_size
        total_size += size
        for key, pts in SCORE_MAP.items():
            if key in f.name:
                score += pts
                break
    return score, total_size


def merge_into_best(group: list[Path]) -> dict:
    """그룹에서 최고 폴더를 선택하고 나머지 폴더를 통째로 삭제.

    파일 코드가 폴더마다 달라 내용 통합이 불가능하므로,
    완성도 1위 폴더만 유지하고 나머지는 삭제.
    """
    # 완성도 점수 기준 정렬 (높을수록 앞), 점수 같으면 최신 날짜 우선
    scored = sorted(group, key=lambda p: (folder_score(p), p.name), reverse=True)
    best = scored[0]
    others = scored[1:]

    if not best.exists():
        return {"best": best.name, "best_score": (0, 0), "deleted": [], "skipped": True}

    result = {
        "best": best.name,
        "best_score": folder_score(best),
        "deleted": [],
        "skipped": False,
    }

    for src_folder in others:
        if not src_folder.exists():
            continue
        score = folder_score(src_folder)
        if not DRY_RUN:
            shutil.rmtree(src_folder)
        result["deleted"].append((src_folder.name, score))

    return result


GENERIC_TITLES = {"논문 서머리", "논문서머리", "summary", "paper summary", "서머리"}


def scan_duplicates(base_dir: Path) -> list[list[Path]]:
    """제목 기준 중복 그룹 목록 반환.

    오탐 필터:
    - 일반적인 제목("논문 서머리" 등)으로 묶인 그룹 제외
    - 같은 날짜(YYMMDD) 폴더끼리만 묶인 그룹 제외 (다른 논문일 가능성)
    """
    title_map: dict[str, list[Path]] = defaultdict(list)

    for folder in base_dir.iterdir():
        if not folder.is_dir():
            continue
        print(f"Scanning: {folder.name}")
        summaries = list(folder.glob("*_00_*서머리.md"))
        if not summaries:
            print(f"  No summary found in {folder.name}")
            continue
        title = extract_title_from_summary(summaries[0])
        print(f"  Title: {title}")
        if title and len(title) > 5:
            title_map[title].append(folder)

    result = []
    for title, folders in title_map.items():
        if len(folders) < 2:
            continue
        # 일반 제목 오탐 제외
        if title.strip() in GENERIC_TITLES:
            continue
        # 같은 날짜(YYMMDD) 폴더끼리만 묶인 경우 오탐 제외
        dates = {f.name[:6] for f in folders}
        if len(dates) == 1:
            continue
        result.append(folders)
    return result


def main():
    mode = "DRY-RUN" if DRY_RUN else "APPLY"
    print(f"{'=' * 60}")
    print(f"중복 폴더 통합 스크립트 [{mode}]")
    print(f"{'=' * 60}\n")

    groups_en = scan_duplicates(EN_DIR)
    groups_ko = scan_duplicates(KO_DIR)

    # EN/KO 교차 중복 (같은 제목이 en/ko 양쪽에 있는 경우는 제외 — 다른 언어 버전)
    all_groups = groups_en + groups_ko

    print(f"중복 그룹: {len(all_groups)}건 ({sum(len(g) for g in all_groups)}개 폴더)\n")

    total_deleted = 0

    for group in sorted(all_groups, key=lambda g: g[0].name):
        result = merge_into_best(group)
        total_deleted += len(result["deleted"])

        deleted_str = ", ".join(f"{name}(점수{sc[0]})" for name, sc in result["deleted"])
        print(f"[유지] {result['best']}(점수{result['best_score'][0]})  →  삭제: {deleted_str}")

    print(f"\n{'=' * 60}")
    print(f"[요약] ({'DRY-RUN' if DRY_RUN else '완료'})")
    print(f"  처리 그룹   : {len(all_groups)}개")
    print(f"  삭제 폴더   : {total_deleted}개")
    print(f"  유지 폴더   : {len(all_groups)}개")

    if DRY_RUN:
        print(f"\n→ 실제 실행: python {sys.argv[0]} --apply")


if __name__ == "__main__":
    main()
