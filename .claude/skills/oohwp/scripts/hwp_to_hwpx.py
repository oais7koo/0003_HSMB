#!/usr/bin/env python3
"""
hwp_to_hwpx.py

HWP(구형 바이너리) → HWPX 변환 스크립트.
pyhwpx (COM 자동화) 방식 사용 — 아래한글이 설치된 Windows에서만 동작.

사용법:
    uv run --with pyhwpx python .claude/skills/oohwp/scripts/hwp_to_hwpx.py <input.hwp> [output.hwpx]

옵션:
    --visible       변환 중 한글 창 표시 (기본: 숨김)
    --keep-open     변환 후 한글 창 유지 (기본: 자동 종료)
    --batch <dir>   폴더 내 모든 .hwp 파일 일괄 변환
"""

import sys
import argparse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def convert_single(hwp_path: Path, hwpx_path: Path, visible: bool = False) -> bool:
    """HWP 파일 하나를 HWPX로 변환. 성공 시 True 반환."""
    try:
        import pyhwpx
    except ImportError:
        print("[ERROR] pyhwpx 미설치. 설치: pip install pyhwpx")
        return False

    hwp = None
    try:
        hwp = pyhwpx.Hwp(visible=visible)
        hwp.SetMessageBoxMode(0x10000)  # 팝업 자동 확인

        abs_input = str(hwp_path.resolve())
        abs_output = str(hwpx_path.resolve())

        # HWP 열기
        result = hwp.Open(abs_input)
        if not result:
            print(f"[ERROR] 파일 열기 실패: {hwp_path}")
            return False

        # HWPX로 저장
        hwp.SaveAs(abs_output, Format="HWPX")

        print(f"[OK] 변환 완료: {hwpx_path}")
        return True

    except Exception as e:
        print(f"[ERROR] 변환 중 오류: {e}")
        return False
    finally:
        if hwp is not None:
            try:
                hwp.Quit()
            except Exception:
                pass


def convert_batch(src_dir: Path, visible: bool = False) -> tuple[int, int]:
    """폴더 내 모든 .hwp 파일 일괄 변환. (성공수, 실패수) 반환."""
    hwp_files = list(src_dir.glob("*.hwp"))
    if not hwp_files:
        print(f"[WARN] .hwp 파일 없음: {src_dir}")
        return 0, 0

    success = 0
    fail = 0
    for hwp_file in hwp_files:
        hwpx_file = hwp_file.with_suffix(".hwpx")
        ok = convert_single(hwp_file, hwpx_file, visible=visible)
        if ok:
            success += 1
        else:
            fail += 1

    return success, fail


def main():
    parser = argparse.ArgumentParser(
        description="HWP → HWPX 변환 (pyhwpx, Windows + 아래한글 필요)"
    )
    parser.add_argument("input", nargs="?", help="입력 .hwp 파일 경로")
    parser.add_argument("output", nargs="?", help="출력 .hwpx 파일 경로 (생략 시 자동)")
    parser.add_argument("--visible", action="store_true", help="변환 중 한글 창 표시")
    parser.add_argument("--batch", metavar="DIR", help="폴더 내 모든 .hwp 일괄 변환")
    args = parser.parse_args()

    print("# oohwp hwp→hwpx 변환\n")

    # 일괄 변환
    if args.batch:
        src_dir = Path(args.batch)
        if not src_dir.is_dir():
            print(f"[ERROR] 폴더 없음: {src_dir}")
            sys.exit(1)
        print(f"대상 폴더: {src_dir}")
        success, fail = convert_batch(src_dir, visible=args.visible)
        print(f"\n완료: {success}개 성공, {fail}개 실패")
        sys.exit(0 if fail == 0 else 1)

    # 단일 파일 변환
    if not args.input:
        parser.print_help()
        sys.exit(1)

    hwp_path = Path(args.input)
    if not hwp_path.exists():
        print(f"[ERROR] 파일 없음: {hwp_path}")
        sys.exit(1)
    if hwp_path.suffix.lower() != ".hwp":
        print(f"[WARN] .hwp 파일이 아닙니다: {hwp_path}")

    hwpx_path = Path(args.output) if args.output else hwp_path.with_suffix(".hwpx")

    print(f"입력: {hwp_path}")
    print(f"출력: {hwpx_path}\n")

    ok = convert_single(hwp_path, hwpx_path, visible=args.visible)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
