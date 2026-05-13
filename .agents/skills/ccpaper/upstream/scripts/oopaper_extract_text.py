#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oopaper_extract_text.py - pdfplumber 기반 PDF 전문 텍스트 추출

사용법:
    uv run python .claude/skills/oopaper/scripts/oopaper_extract_text.py <pdf_path> [--output <output_path>]
    uv run python .claude/skills/oopaper/scripts/oopaper_extract_text.py --folder <folder_path> [--force]
    uv run python .claude/skills/oopaper/scripts/oopaper_extract_text.py --batch <ko_dir> [--force]

예시:
    # 단일 PDF
    uv run python .claude/skills/oopaper/scripts/oopaper_extract_text.py 03_paper/12_paper_ko/260324-1526/260324-1526_01_스마트도로_통합체계.pdf

    # 폴더 내 모든 PDF
    uv run python .claude/skills/oopaper/scripts/oopaper_extract_text.py --folder 03_paper/12_paper_ko/260324-1526/

    # 12_paper_ko 전체 배치
    uv run python .claude/skills/oopaper/scripts/oopaper_extract_text.py --batch 03_paper/12_paper_ko/ --force
"""

import argparse
import sys
import re
from pathlib import Path

# PDF 백업 폴백 지원 (OAIS=03_paper/ 하위, 독립 프로젝트=루트 직하)
_root = Path(__file__).resolve().parent.parent.parent.parent.parent
_paper_base_for_import = _root / "03_paper" if (_root / "03_paper").exists() else _root
sys.path.insert(0, str(_paper_base_for_import))
try:
    from pdf_resolver import resolve_pdf, find_pdfs_in_folder
except ModuleNotFoundError:
    def resolve_pdf(p): return p if p.exists() else None
    def find_pdfs_in_folder(folder): return list(folder.glob("*.pdf")) if folder.exists() else []

try:
    import pdfplumber
except ImportError:
    print("[ERROR] pdfplumber 미설치. 설치: uv add pdfplumber")
    sys.exit(1)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """pdfplumber로 PDF 전체 텍스트 추출."""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"<!-- page {i+1}/{total} -->\n{text}")
    return "\n\n".join(pages_text)


def clean_text(raw: str) -> str:
    """추출 텍스트 정리: 불필요한 공백/줄바꿈 정리."""
    # 연속 빈 줄 → 2줄로
    text = re.sub(r'\n{4,}', '\n\n\n', raw)
    # 페이지 번호 패턴 제거 (단독 숫자 줄)
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)
    return text.strip()


def guess_title(text: str, pdf_name: str) -> str:
    """텍스트 첫 부분에서 제목 추정."""
    lines = [l.strip() for l in text.split('\n') if l.strip()][:10]
    for line in lines:
        if len(line) > 10 and not line.startswith('<!--'):
            return line
    return pdf_name


def make_markdown(text: str, pdf_path: Path) -> str:
    """추출 텍스트를 마크다운 형식으로 변환."""
    title = guess_title(text, pdf_path.stem)
    cleaned = clean_text(text)

    # 페이지 수 카운트
    page_count = len(re.findall(r'<!-- page \d+', cleaned))

    header = f"""# {title}

> 원본: {pdf_path.name}
> 추출: pdfplumber (전체 {page_count}페이지)
> 주의: 자동 추출 텍스트로, 표/그림은 텍스트로 변환됨

---

"""
    return header + cleaned


def process_single(pdf_path: Path, output_path: Path = None, force: bool = False) -> bool:
    """단일 PDF 처리. 원본에 없으면 백업에서 탐색."""
    resolved = resolve_pdf(pdf_path)
    if resolved is None:
        print(f"[ERROR] 파일 없음 (원본+백업): {pdf_path}")
        return False
    if resolved != pdf_path:
        print(f"[INFO] 백업에서 발견: {resolved}")
    pdf_path = resolved

    # 출력 경로 자동 결정
    if output_path is None:
        stem = pdf_path.stem
        # _01_ → _04_ 변환
        if '_01_' in stem:
            out_stem = stem.replace('_01_', '_04_')
        else:
            out_stem = stem
        output_path = pdf_path.parent / f"{out_stem}_전문(한글).md"

    if output_path.exists() and not force:
        print(f"[SKIP] 이미 존재: {output_path.name}")
        return True

    print(f"[추출] {pdf_path.name} ({pdf_path.stat().st_size / 1024 / 1024:.1f}MB)")

    try:
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text.strip():
            print(f"[WARN] 텍스트 없음 (스캔 PDF일 수 있음): {pdf_path.name}")
            return False

        md = make_markdown(raw_text, pdf_path)
        output_path.write_text(md, encoding='utf-8')

        size_kb = output_path.stat().st_size / 1024
        page_count = len(re.findall(r'<!-- page \d+', md))
        print(f"[OK] → {output_path.name} ({page_count}p, {size_kb:.1f}KB)")
        return True

    except Exception as e:
        print(f"[ERROR] 추출 실패: {e}")
        return False


def process_folder(folder_path: Path, force: bool = False) -> dict:
    """폴더 내 모든 *_01_*.pdf 처리."""
    results = {"ok": 0, "skip": 0, "fail": 0}

    pdf_files = sorted(folder_path.glob("*_01_*.pdf"))
    if not pdf_files:
        # _01_ 패턴 없으면 모든 PDF (원본 + 백업 통합)
        pdf_files = find_pdfs_in_folder(folder_path)
    if not pdf_files:
        pdf_files = find_pdfs_in_folder(folder_path, "*_01_*.pdf")

    for pdf in pdf_files:
        ok = process_single(pdf, force=force)
        if ok:
            results["ok"] += 1
        else:
            results["fail"] += 1

    return results


def process_batch(ko_dir: Path, force: bool = False) -> dict:
    """12_paper_ko/ 전체 폴더 배치 처리."""
    total = {"ok": 0, "skip": 0, "fail": 0, "folders": 0}

    for folder in sorted(ko_dir.iterdir()):
        if not folder.is_dir():
            continue
        # _04_*전문(한글)*.md 없는 폴더만 처리 (force 시 전체)
        existing = list(folder.glob("*_04_*전문*한글*.md"))
        if existing and not force:
            total["skip"] += len(existing)
            continue

        print(f"\n--- {folder.name} ---")
        results = process_folder(folder, force=force)
        total["ok"] += results["ok"]
        total["fail"] += results["fail"]
        total["folders"] += 1

    return total


def main():
    parser = argparse.ArgumentParser(description="PDF 전문 텍스트 추출 (pdfplumber)")
    parser.add_argument("pdf", nargs="?", help="단일 PDF 파일 경로")
    parser.add_argument("--output", "-o", help="출력 마크다운 경로")
    parser.add_argument("--folder", help="폴더 내 모든 PDF 처리")
    parser.add_argument("--batch", help="12_paper_ko/ 전체 배치 처리")
    parser.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    args = parser.parse_args()

    if args.batch:
        ko_dir = Path(args.batch)
        if not ko_dir.exists():
            print(f"[ERROR] 디렉토리 없음: {ko_dir}")
            return 1
        print(f"# 배치 추출: {ko_dir}\n")
        results = process_batch(ko_dir, force=args.force)
        print(f"\n# 결과: {results['folders']}폴더, OK:{results['ok']}, SKIP:{results['skip']}, FAIL:{results['fail']}")
        return 0 if results['fail'] == 0 else 1

    elif args.folder:
        folder = Path(args.folder)
        if not folder.exists():
            print(f"[ERROR] 디렉토리 없음: {folder}")
            return 1
        print(f"# 폴더 추출: {folder}\n")
        results = process_folder(folder, force=args.force)
        print(f"\n# 결과: OK:{results['ok']}, FAIL:{results['fail']}")
        return 0 if results['fail'] == 0 else 1

    elif args.pdf:
        pdf = Path(args.pdf)
        output = Path(args.output) if args.output else None
        ok = process_single(pdf, output, force=args.force)
        return 0 if ok else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
