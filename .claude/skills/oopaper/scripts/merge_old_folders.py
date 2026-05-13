"""
구형(HHMMSS, 6자리) 폴더 → 신형(HHMM, 4자리) 폴더 통합 스크립트
- 구형 폴더 내 파일명 코드로 신형 폴더를 탐지
- 신형에 없는 파일 또는 더 완성된 파일을 신형으로 복사
- 구형 폴더 삭제

사용법:
  python merge_old_folders.py           # dry-run (기본)
  python merge_old_folders.py --apply   # 실제 실행
"""

import os
import re
import shutil
import sys
from pathlib import Path

DRY_RUN = "--apply" not in sys.argv
EN_DIR = Path("03_paper/11_paper_en")

OLD_PATTERN = re.compile(r"^\d{6}-\d{6}$")   # YYMMDD-HHMMSS
NEW_PATTERN = re.compile(r"^\d{6}-\d{4}$")    # YYMMDD-HHMM


def get_file_code(folder: Path) -> str | None:
    """폴더 내 파일명의 첫 번째 코드(YYMMDD-HHMMSS 또는 YYMMDD-HHMM) 반환"""
    for f in folder.iterdir():
        if f.suffix in (".md", ".pdf"):
            parts = f.name.split("_", 1)
            if parts:
                return parts[0]
    return None


def find_new_folder(old_folder: Path, file_code: str) -> Path | None:
    """파일 코드와 동일한 파일을 가진 신형(HHMM) 폴더 탐지"""
    for candidate in EN_DIR.iterdir():
        if not candidate.is_dir():
            continue
        if not NEW_PATTERN.match(candidate.name):
            continue
        if candidate == old_folder:
            continue
        # 후보 폴더 내에 같은 파일 코드가 있는지 확인
        for f in candidate.iterdir():
            if f.name.startswith(file_code + "_"):
                return candidate
    return None


def should_replace(src: Path, dst: Path) -> bool:
    """src 파일이 dst보다 더 완성된(큰) 파일이면 True"""
    return src.stat().st_size > dst.stat().st_size


def merge_folder(old_folder: Path, new_folder: Path) -> dict:
    """구형 폴더의 파일을 신형 폴더로 통합 (더 나은 파일 우선)"""
    result = {"copied": [], "replaced": [], "skipped": [], "deleted_folder": False}

    for src_file in old_folder.iterdir():
        dst_file = new_folder / src_file.name
        if not dst_file.exists():
            # 신형에 없는 파일 → 복사
            if not DRY_RUN:
                shutil.copy2(src_file, dst_file)
            result["copied"].append(src_file.name)
        elif should_replace(src_file, dst_file):
            # 구형이 더 크면 교체
            if not DRY_RUN:
                shutil.copy2(src_file, dst_file)
            result["replaced"].append(f"{src_file.name} ({dst_file.stat().st_size}B → {src_file.stat().st_size}B)")
        else:
            result["skipped"].append(src_file.name)

    # 구형 폴더 삭제
    if not DRY_RUN:
        shutil.rmtree(old_folder)
    result["deleted_folder"] = True
    return result


def main():
    mode = "DRY-RUN" if DRY_RUN else "APPLY"
    print(f"{'=' * 60}")
    print(f"구형 폴더 통합 스크립트 [{mode}]")
    print(f"{'=' * 60}\n")

    old_folders = [f for f in EN_DIR.iterdir()
                   if f.is_dir() and OLD_PATTERN.match(f.name)]
    old_folders.sort()

    print(f"구형 폴더 {len(old_folders)}개 탐지\n")

    unmapped = []
    total_copied = 0
    total_replaced = 0
    total_deleted = 0

    for old_folder in old_folders:
        file_code = get_file_code(old_folder)
        if not file_code:
            unmapped.append((old_folder.name, "파일 없음"))
            continue

        new_folder = find_new_folder(old_folder, file_code)
        if not new_folder:
            unmapped.append((old_folder.name, f"코드={file_code} → 신형 폴더 없음"))
            continue

        result = merge_folder(old_folder, new_folder)
        total_copied += len(result["copied"])
        total_replaced += len(result["replaced"])
        total_deleted += 1

        print(f"[{'삭제' if not DRY_RUN else '예정'}] {old_folder.name} → {new_folder.name}")
        if result["copied"]:
            for f in result["copied"]:
                print(f"  + 복사: {f}")
        if result["replaced"]:
            for f in result["replaced"]:
                print(f"  ↑ 교체: {f}")
        if result["skipped"]:
            print(f"  - 유지(신형우수): {len(result['skipped'])}개")

    print(f"\n{'=' * 60}")
    print(f"[요약] {'(DRY-RUN)' if DRY_RUN else '(완료)'}")
    print(f"  처리 폴더   : {total_deleted}개")
    print(f"  복사된 파일 : {total_copied}개")
    print(f"  교체된 파일 : {total_replaced}개")
    print(f"  미매핑 폴더 : {len(unmapped)}개")

    if unmapped:
        print(f"\n[미매핑 — 수동 확인 필요]")
        for name, reason in unmapped:
            print(f"  {name}: {reason}")

    if DRY_RUN:
        print(f"\n→ 실제 실행: python {sys.argv[0]} --apply")


if __name__ == "__main__":
    main()
