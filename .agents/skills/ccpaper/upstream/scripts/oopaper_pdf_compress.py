#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oopaper_pdf_compress.py - PDF 압축 및 OCR 처리

텍스트를 보존하면서 PDF 용량을 줄이고,
이미지 기반 PDF의 경우 OCR을 적용하여 검색 가능하게 변환

사용법:
    python oopaper_pdf_compress.py input.pdf [output.pdf]
    python oopaper_pdf_compress.py input.pdf --ocr-only
    python oopaper_pdf_compress.py input.pdf --compress-only
    python oopaper_pdf_compress.py --batch input_dir output_dir

의존성:
    pip install pypdf pdfplumber pytesseract pdf2image pillow reportlab

시스템 요구사항:
    - Tesseract OCR 설치 필요 (https://github.com/tesseract-ocr/tesseract)
    - Poppler 설치 필요 (pdf2image용)
"""

import os
import sys
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass
from io import BytesIO

# PDF 라이브러리
from pypdf import PdfReader, PdfWriter
import pdfplumber

# 이미지 처리
from PIL import Image

# OCR
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[WARN] pytesseract 또는 pdf2image가 설치되지 않음. OCR 기능 비활성화")

# PDF 생성
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@dataclass
class CompressionResult:
    """압축 결과 정보"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    text_preserved: bool
    ocr_applied: bool
    pages_processed: int
    output_path: str


class PDFCompressor:
    """PDF 압축 및 OCR 처리 클래스"""

    def __init__(
        self,
        image_quality: int = 50,
        image_dpi: int = 150,
        ocr_lang: str = "kor+eng",
        verbose: bool = True
    ):
        """
        Args:
            image_quality: 이미지 압축 품질 (1-100, 낮을수록 작은 파일)
            image_dpi: 이미지 렌더링 DPI (낮을수록 작은 파일)
            ocr_lang: OCR 언어 설정 (kor+eng, eng 등)
            verbose: 상세 출력 여부
        """
        self.image_quality = image_quality
        self.image_dpi = image_dpi
        self.ocr_lang = ocr_lang
        self.verbose = verbose

    def log(self, message: str):
        """로그 출력"""
        if self.verbose:
            print(message)

    def get_file_size(self, file_path: str) -> int:
        """파일 크기 반환 (bytes)"""
        return os.path.getsize(file_path)

    def format_size(self, size_bytes: int) -> str:
        """파일 크기를 읽기 쉬운 형식으로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    def has_extractable_text(self, pdf_path: str, min_chars: int = 100) -> Tuple[bool, int]:
        """
        PDF에서 추출 가능한 텍스트가 있는지 확인

        Args:
            pdf_path: PDF 파일 경로
            min_chars: 텍스트로 판단할 최소 문자 수

        Returns:
            (텍스트 존재 여부, 추출된 문자 수)
        """
        total_chars = 0
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    # 공백 제거 후 문자 수 계산
                    text = text.strip()
                    total_chars += len(text.replace(" ", "").replace("\n", ""))
        except Exception as e:
            self.log(f"[WARN] 텍스트 추출 실패: {e}")
            return False, 0

        return total_chars >= min_chars, total_chars

    def compress_images_in_pdf(self, input_path: str, output_path: str) -> bool:
        """
        PDF 내 이미지 압축

        pypdf를 사용하여 PDF 내 이미지를 압축

        Args:
            input_path: 입력 PDF 경로
            output_path: 출력 PDF 경로

        Returns:
            성공 여부
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # 이미지 압축 설정
            for page in writer.pages:
                # 페이지 내 이미지 압축
                page.compress_content_streams()

            # 메타데이터 복사
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            with open(output_path, "wb") as f:
                writer.write(f)

            return True
        except Exception as e:
            self.log(f"[ERROR] 이미지 압축 실패: {e}")
            return False

    def reduce_image_quality(self, input_path: str, output_path: str) -> bool:
        """
        PDF를 이미지로 변환 후 재압축

        더 강력한 압축이 필요한 경우 사용

        Args:
            input_path: 입력 PDF 경로
            output_path: 출력 PDF 경로

        Returns:
            성공 여부
        """
        if not OCR_AVAILABLE:
            self.log("[ERROR] pdf2image가 필요합니다")
            return False

        try:
            # PDF를 이미지로 변환
            images = convert_from_path(
                input_path,
                dpi=self.image_dpi,
                fmt='jpeg'
            )

            if not images:
                return False

            # 첫 번째 이미지를 기준으로 PDF 생성
            compressed_images = []
            for img in images:
                # JPEG 압축 적용
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=self.image_quality, optimize=True)
                buffer.seek(0)
                compressed_images.append(Image.open(buffer))

            # 이미지들을 PDF로 저장
            if compressed_images:
                first_img = compressed_images[0]
                if len(compressed_images) > 1:
                    first_img.save(
                        output_path,
                        save_all=True,
                        append_images=compressed_images[1:],
                        format='PDF'
                    )
                else:
                    first_img.save(output_path, format='PDF')

            return True
        except Exception as e:
            self.log(f"[ERROR] 이미지 품질 감소 실패: {e}")
            return False

    def apply_ocr(self, input_path: str, output_path: str) -> bool:
        """
        이미지 기반 PDF에 OCR 적용

        Args:
            input_path: 입력 PDF 경로
            output_path: 출력 PDF 경로

        Returns:
            성공 여부
        """
        if not OCR_AVAILABLE:
            self.log("[ERROR] pytesseract와 pdf2image가 필요합니다")
            return False

        try:
            # PDF를 이미지로 변환
            self.log(f"[INFO] PDF를 이미지로 변환 중... (DPI: {self.image_dpi})")
            images = convert_from_path(input_path, dpi=self.image_dpi)

            if not images:
                self.log("[ERROR] PDF에서 이미지를 추출할 수 없습니다")
                return False

            self.log(f"[INFO] {len(images)}개 페이지 OCR 처리 중...")

            # OCR 적용하여 검색 가능한 PDF 생성
            pdf_pages = []
            for i, image in enumerate(images):
                self.log(f"  - 페이지 {i + 1}/{len(images)} 처리 중...")

                # OCR로 텍스트 추출
                try:
                    # PDF with text layer 생성
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                        image,
                        lang=self.ocr_lang,
                        extension='pdf'
                    )
                    pdf_pages.append(pdf_bytes)
                except Exception as e:
                    self.log(f"[WARN] 페이지 {i + 1} OCR 실패: {e}")
                    # OCR 실패 시 원본 이미지만 저장
                    buffer = BytesIO()
                    image.save(buffer, format='PDF')
                    pdf_pages.append(buffer.getvalue())

            # 모든 페이지를 하나의 PDF로 병합
            writer = PdfWriter()
            for pdf_bytes in pdf_pages:
                reader = PdfReader(BytesIO(pdf_bytes))
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            return True
        except Exception as e:
            self.log(f"[ERROR] OCR 적용 실패: {e}")
            return False

    def compress(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        force_ocr: bool = False,
        compress_only: bool = False
    ) -> CompressionResult:
        """
        PDF 압축 및 OCR 적용

        Args:
            input_path: 입력 PDF 경로
            output_path: 출력 PDF 경로 (None이면 자동 생성)
            force_ocr: 텍스트가 있어도 OCR 강제 적용
            compress_only: 압축만 수행 (OCR 비적용)

        Returns:
            CompressionResult: 압축 결과 정보
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

        # 출력 경로 설정
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_compressed.pdf"
        output_path = Path(output_path)

        original_size = self.get_file_size(str(input_path))
        self.log(f"\n{'=' * 60}")
        self.log(f"[INFO] PDF 압축 시작: {input_path.name}")
        self.log(f"[INFO] 원본 크기: {self.format_size(original_size)}")
        self.log(f"{'=' * 60}")

        # 텍스트 존재 여부 확인
        has_text, char_count = self.has_extractable_text(str(input_path))
        self.log(f"[INFO] 추출된 텍스트: {char_count}자")

        ocr_applied = False
        text_preserved = has_text

        # 임시 파일 사용
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "temp.pdf"
            current_path = str(input_path)

            # Step 1: 기본 이미지 압축 (pypdf)
            self.log("\n[Step 1] pypdf 이미지 압축 적용...")
            if self.compress_images_in_pdf(current_path, str(temp_path)):
                size_after = self.get_file_size(str(temp_path))
                self.log(f"  -> 크기: {self.format_size(size_after)}")
                if size_after < self.get_file_size(current_path):
                    current_path = str(temp_path)
                    temp_path = Path(temp_dir) / "temp2.pdf"

            # Step 2: 텍스트가 없는 경우 OCR 적용
            if not has_text and not compress_only:
                self.log("\n[Step 2] 텍스트 없음 감지 - OCR 적용...")
                if self.apply_ocr(current_path, str(temp_path)):
                    ocr_applied = True
                    text_preserved = True
                    size_after = self.get_file_size(str(temp_path))
                    self.log(f"  -> OCR 완료, 크기: {self.format_size(size_after)}")
                    current_path = str(temp_path)
                    temp_path = Path(temp_dir) / "temp3.pdf"
                else:
                    self.log("  -> OCR 실패, 원본 유지")
            elif force_ocr and not compress_only:
                self.log("\n[Step 2] 강제 OCR 적용...")
                if self.apply_ocr(current_path, str(temp_path)):
                    ocr_applied = True
                    size_after = self.get_file_size(str(temp_path))
                    self.log(f"  -> OCR 완료, 크기: {self.format_size(size_after)}")
                    current_path = str(temp_path)
                    temp_path = Path(temp_dir) / "temp3.pdf"

            # Step 3: 추가 이미지 품질 감소 (선택적)
            current_size = self.get_file_size(current_path)
            if current_size > original_size * 0.9:  # 10% 이상 압축되지 않은 경우
                self.log("\n[Step 3] 추가 이미지 압축 시도...")
                if has_text:
                    self.log("  -> 텍스트 보존을 위해 건너뜀")
                else:
                    if self.reduce_image_quality(current_path, str(temp_path)):
                        size_after = self.get_file_size(str(temp_path))
                        if size_after < current_size:
                            self.log(f"  -> 크기: {self.format_size(size_after)}")
                            current_path = str(temp_path)

            # 결과 복사
            shutil.copy2(current_path, str(output_path))

        # 결과 정보
        compressed_size = self.get_file_size(str(output_path))
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        reader = PdfReader(str(output_path))
        pages_processed = len(reader.pages)

        self.log(f"\n{'=' * 60}")
        self.log(f"[결과]")
        self.log(f"  원본 크기: {self.format_size(original_size)}")
        self.log(f"  압축 크기: {self.format_size(compressed_size)}")
        self.log(f"  압축률: {compression_ratio:.1f}%")
        self.log(f"  텍스트 보존: {'예' if text_preserved else '아니오'}")
        self.log(f"  OCR 적용: {'예' if ocr_applied else '아니오'}")
        self.log(f"  처리 페이지: {pages_processed}")
        self.log(f"  출력 파일: {output_path}")
        self.log(f"{'=' * 60}\n")

        return CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            text_preserved=text_preserved,
            ocr_applied=ocr_applied,
            pages_processed=pages_processed,
            output_path=str(output_path)
        )

    def batch_compress(
        self,
        input_dir: str,
        output_dir: str,
        recursive: bool = False
    ) -> List[CompressionResult]:
        """
        폴더 내 모든 PDF 일괄 압축

        Args:
            input_dir: 입력 디렉토리
            output_dir: 출력 디렉토리
            recursive: 하위 폴더 포함 여부

        Returns:
            압축 결과 리스트
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if recursive:
            pdf_files = list(input_dir.rglob("*.pdf"))
        else:
            pdf_files = list(input_dir.glob("*.pdf"))

        self.log(f"[INFO] {len(pdf_files)}개 PDF 파일 발견")

        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            self.log(f"\n[{i}/{len(pdf_files)}] 처리 중: {pdf_file.name}")

            # 출력 경로 계산
            rel_path = pdf_file.relative_to(input_dir)
            output_path = output_dir / rel_path

            # 출력 디렉토리 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                result = self.compress(str(pdf_file), str(output_path))
                results.append(result)
            except Exception as e:
                self.log(f"[ERROR] 처리 실패: {e}")

        # 배치 결과 요약
        if results:
            total_original = sum(r.original_size for r in results)
            total_compressed = sum(r.compressed_size for r in results)
            total_ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0

            self.log(f"\n{'=' * 60}")
            self.log(f"[배치 처리 완료]")
            self.log(f"  처리 파일: {len(results)}개")
            self.log(f"  전체 원본: {self.format_size(total_original)}")
            self.log(f"  전체 압축: {self.format_size(total_compressed)}")
            self.log(f"  평균 압축률: {total_ratio:.1f}%")
            self.log(f"{'=' * 60}\n")

        return results


def main():
    parser = argparse.ArgumentParser(
        description="PDF 압축 및 OCR 처리",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 단일 파일 압축 (자동 OCR)
  python oopaper_pdf_compress.py input.pdf

  # 출력 파일 지정
  python oopaper_pdf_compress.py input.pdf output.pdf

  # OCR만 적용 (압축 제외)
  python oopaper_pdf_compress.py input.pdf --ocr-only

  # 압축만 적용 (OCR 제외)
  python oopaper_pdf_compress.py input.pdf --compress-only

  # 배치 처리
  python oopaper_pdf_compress.py --batch input_dir output_dir
        """
    )

    parser.add_argument("input", nargs="?", help="입력 PDF 파일 또는 디렉토리")
    parser.add_argument("output", nargs="?", help="출력 PDF 파일 또는 디렉토리")

    parser.add_argument("--batch", action="store_true", help="배치 처리 모드")
    parser.add_argument("--recursive", "-r", action="store_true", help="하위 폴더 포함 (배치 모드)")

    parser.add_argument("--ocr-only", action="store_true", help="OCR만 적용")
    parser.add_argument("--compress-only", action="store_true", help="압축만 적용")
    parser.add_argument("--force-ocr", action="store_true", help="텍스트 있어도 OCR 강제 적용")

    parser.add_argument("--quality", type=int, default=50, help="이미지 품질 (1-100, 기본: 50)")
    parser.add_argument("--dpi", type=int, default=150, help="이미지 DPI (기본: 150)")
    parser.add_argument("--lang", default="kor+eng", help="OCR 언어 (기본: kor+eng)")

    parser.add_argument("--quiet", "-q", action="store_true", help="조용한 모드")

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return 1

    compressor = PDFCompressor(
        image_quality=args.quality,
        image_dpi=args.dpi,
        ocr_lang=args.lang,
        verbose=not args.quiet
    )

    try:
        if args.batch:
            if not args.output:
                print("[ERROR] 배치 모드에서는 출력 디렉토리가 필요합니다")
                return 1
            compressor.batch_compress(args.input, args.output, args.recursive)
        else:
            compressor.compress(
                args.input,
                args.output,
                force_ocr=args.force_ocr or args.ocr_only,
                compress_only=args.compress_only
            )
        return 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
