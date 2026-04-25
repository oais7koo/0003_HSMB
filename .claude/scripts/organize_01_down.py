#!/usr/bin/env python3
"""
00_down 폴더 PDF 처리 스크립트
- 메타데이터 추출
- 11_paper_en 폴더로 표준 형식 이동
- download_list.md 처리
"""

import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
import json

# 경로 설정
BASE_DIR = Path(__file__).parent.parent.parent
DOWN_DIR = BASE_DIR / "data" / "01_book" / "00_down"
PAPER_DIR = BASE_DIR / "data" / "01_book" / "11_paper_en"
TMP_DIR = BASE_DIR / "tmp"


def extract_metadata_from_pdf(pdf_path):
    """PDF 파일명에서 메타데이터 추출"""
    filename = pdf_path.name

    # arXiv ID 추출
    arxiv_match = re.search(r"(\d{4}\.\d+)", filename)
    if arxiv_match:
        return {
            "type": "arxiv",
            "id": arxiv_match.group(1),
            "title": filename.replace(arxiv_match.group(0), "")
            .replace(".pdf", "")
            .strip(" _-"),
        }

    # 일반 논문 제목 추정
    title = re.sub(r"\.pdf$", "", filename)
    title = re.sub(r"^[R]?\d{6}-\d{4}_?", "", title)  # RYYMMDD-HHMM prefix 제거
    title = title.replace("_", " ").strip()

    return {"type": "general", "title": title, "filename": filename}


def generate_folder_id(counter=[0]):
    """YYMMDD-HHMM 형식 폴더 ID 생성 (카운터로 고유성 보장)"""
    now = datetime.now()
    base_id = now.strftime("%y%m%d-%H%M")
    if counter[0] == 0:
        folder_id = base_id
    else:
        folder_id = f"{base_id}{counter[0]:02d}"
    counter[0] += 1
    # 중복 확인
    while (PAPER_DIR / folder_id).exists():
        folder_id = f"{base_id}{counter[0]:02d}"
        counter[0] += 1
    return folder_id


def create_standard_folder(folder_id, metadata, pdf_path):
    """표준 폴더 구조 생성"""
    folder_path = PAPER_DIR / folder_id
    folder_path.mkdir(exist_ok=True)

    # PDF 이동
    title_safe = re.sub(r"[^\w\s-]", "", metadata.get("title", "Unknown"))[:30]
    title_safe = re.sub(r"\s+", "_", title_safe.strip())

    new_pdf_name = f"{folder_id}_01_{title_safe}.pdf"
    new_pdf_path = folder_path / new_pdf_name

    shutil.move(str(pdf_path), str(new_pdf_path))

    # 기본 파일들 생성
    files_created = []

    # 00_서머리.md
    summary_content = f"""# {metadata.get("title", "Unknown Title")}

## 문서 이력 관리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | {datetime.now().strftime("%Y-%m-%d")} | 최초 작성 |

---

## 1. 개요

### 1.1 논문 정보
- **제목**: {metadata.get("title", "Unknown Title")}
- **파일명**: {metadata.get("filename", pdf_path.name)}
- **폴더ID**: {folder_id}
- **등록일**: {datetime.now().strftime("%Y-%m-%d")}

### 1.2 메타데이터
"""

    if metadata.get("type") == "arxiv":
        summary_content += f"""- **arXiv ID**: {metadata.get("id", "Unknown")}
"""

    if metadata.get("author") and metadata["author"] != "-":
        summary_content += f"""- **저자**: {metadata["author"]}
"""
    if metadata.get("year") and metadata["year"] != "-":
        summary_content += f"""- **연도**: {metadata["year"]}
"""
    if metadata.get("source") and metadata["source"] != "-":
        summary_content += f"""- **출처**: {metadata["source"]}
"""

    keywords_val = metadata.get("keywords", "")
    summary_content += f"""
### 1.3 분류
- **키워드**: {keywords_val}
- **분야**:
- **연구 방법론**:

---

## 2. 핵심 내용 요약

### 2.1 연구 목적
[TODO: PDF 내용 분석 후 작성]

### 2.2 주요 기여
[TODO: PDF 내용 분석 후 작성]

### 2.3 실험 결과
[TODO: PDF 내용 분석 후 작성]

---

## 3. 상세 분석

### 3.1 방법론
[TODO: PDF 내용 분석 후 작성]

### 3.2 데이터셋
[TODO: PDF 내용 분석 후 작성]

### 3.3 평가 지표
[TODO: PDF 내용 분석 후 작성]

---

## 4. 평가

### 4.1 장점
[TODO: 분석 후 작성]

### 4.2 단점
[TODO: 분석 후 작성]

### 4.3 응용 가능성
[TODO: 분석 후 작성]

---

## 5. 인용 정보

```bibtex
[TODO: 메타데이터 완성 후 작성]
```
"""

    summary_file = folder_path / f"{folder_id}_00_{title_safe}_서머리.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_content)
    files_created.append(summary_file)

    # 03_전문(영어).md (placeholder)
    english_content = f"""# {metadata.get("title", "Unknown Title")}

*Extracted from PDF - English Text*

[TODO: PDF에서 영문 텍스트 추출 필요]
"""

    english_file = folder_path / f"{folder_id}_03_{title_safe}_전문(영어).md"
    with open(english_file, "w", encoding="utf-8") as f:
        f.write(english_content)
    files_created.append(english_file)

    # 04_전문(한글).md (placeholder)
    korean_content = f"""# {metadata.get("title", "Unknown Title")}

*번역된 한글 전문*

[TODO: 영문 전문 번역 필요]
"""

    korean_file = folder_path / f"{folder_id}_04_{title_safe}_전문(한글).md"
    with open(korean_file, "w", encoding="utf-8") as f:
        f.write(korean_content)
    files_created.append(korean_file)

    return {
        "folder_path": folder_path,
        "files_created": files_created,
        "pdf_moved": new_pdf_path,
    }


def parse_download_list(list_path):
    """download_list.md에서 논문 메타데이터 파싱"""
    with open(list_path, "r", encoding="utf-8") as f:
        content = f.read()

    papers = []
    current = {}
    for line in content.split("\n"):
        # ### N. 제목
        title_match = re.match(r"^### \d+\.\s+(.+)$", line)
        if title_match:
            if current:
                papers.append(current)
            current = {"title": title_match.group(1).strip()}
            continue

        if not current:
            continue

        # - **저자**: ...
        author_match = re.match(r"^- \*\*저자\*\*:\s*(.+)$", line)
        if author_match:
            current["author"] = author_match.group(1).strip()

        # - **연도**: ...
        year_match = re.match(r"^- \*\*연도\*\*:\s*(.+)$", line)
        if year_match:
            current["year"] = year_match.group(1).strip()

        # - **arXiv**: ...
        arxiv_match = re.match(r"^- \*\*arXiv\*\*:\s*(.+)$", line)
        if arxiv_match:
            current["arxiv"] = arxiv_match.group(1).strip()

        # - **출처**: ...
        source_match = re.match(r"^- \*\*출처\*\*:\s*(.+)$", line)
        if source_match:
            current["source"] = source_match.group(1).strip()

        # - **핵심**: ...
        core_match = re.match(r"^- \*\*핵심\*\*:\s*(.+)$", line)
        if core_match:
            current["keywords"] = core_match.group(1).strip()

    if current:
        papers.append(current)

    return papers


def match_pdf_to_arxiv(pdf_files, arxiv_id):
    """arXiv ID로 PDF 파일 매칭"""
    # arXiv ID에서 점 제거한 버전도 매칭
    arxiv_no_dot = arxiv_id.replace(".", "")
    for pdf in pdf_files:
        name = pdf.stem
        if arxiv_id in name or arxiv_no_dot in name:
            return pdf
    return None


def process_download_list(remaining_pdfs):
    """download_list.md 처리 - PDF와 메타데이터 매칭"""
    download_list_path = DOWN_DIR / "download_list.md"
    if not download_list_path.exists():
        return {"status": "no_list", "processed": 0, "matched": []}

    print("download_list.md 처리 시작...")
    papers = parse_download_list(download_list_path)
    print(f"   리스트에서 {len(papers)}개 논문 파싱")

    matched = []
    for paper in papers:
        arxiv_id = paper.get("arxiv", "")
        if not arxiv_id:
            continue

        pdf = match_pdf_to_arxiv(remaining_pdfs, arxiv_id)
        if pdf:
            matched.append({"pdf": pdf, "metadata": paper})
            remaining_pdfs.remove(pdf)

    print(f"   매칭 완료: {len(matched)}개")

    # 처리 완료된 리스트 파일 -> data/00_old 이동
    old_dir = BASE_DIR / "data" / "00_old"
    old_dir.mkdir(parents=True, exist_ok=True)
    dest = old_dir / f"download_list_{datetime.now().strftime('%Y%m%d')}.md"
    shutil.move(str(download_list_path), str(dest))
    print(f"   download_list.md -> {dest}")

    return {"status": "processed", "processed": len(matched), "matched": matched}


def main():
    """메인 처리 함수"""
    print("00_down 폴더 PDF 처리 시작...")

    # 디렉토리 확인
    if not DOWN_DIR.exists():
        print(f"{DOWN_DIR} 폴더가 존재하지 않습니다.")
        return

    PAPER_DIR.mkdir(exist_ok=True)

    # PDF 파일 찾기
    pdf_files = list(DOWN_DIR.glob("*.pdf"))
    print(f"PDF 파일 {len(pdf_files)}개 발견")

    processed_pdfs = []
    remaining_pdfs = list(pdf_files)

    # Phase 1: download_list.md 매칭 논문 우선 처리
    print(f"\n=== Phase 1: download_list.md 매칭 처리 ===")
    list_result = process_download_list(remaining_pdfs)

    for item in list_result.get("matched", []):
        pdf_path = item["pdf"]
        dl_meta = item["metadata"]
        print(f"\n처리 중 (리스트 매칭): {pdf_path.name}")

        # download_list.md 메타데이터 활용
        metadata = {
            "type": "arxiv",
            "id": dl_meta.get("arxiv", ""),
            "title": dl_meta.get("title", "Unknown"),
            "author": dl_meta.get("author", "-"),
            "year": dl_meta.get("year", "-"),
            "source": dl_meta.get("source", "-"),
            "keywords": dl_meta.get("keywords", ""),
            "filename": pdf_path.name,
        }
        print(f"   제목: {metadata['title']}")
        print(f"   arXiv: {metadata['id']}")

        folder_id = generate_folder_id()
        print(f"   폴더ID: {folder_id}")

        result = create_standard_folder(folder_id, metadata, pdf_path)
        processed_pdfs.append(
            {"folder_id": folder_id, "metadata": metadata, "result": result}
        )
        print(f"   성공: {result['folder_path']}")

    # Phase 2: 나머지 PDF 파일 처리
    print(f"\n=== Phase 2: 나머지 PDF 처리 ({len(remaining_pdfs)}개) ===")
    for idx, pdf_path in enumerate(remaining_pdfs):
        print(f"\n처리 중 ({idx + 1}/{len(remaining_pdfs)}): {pdf_path.name}")

        metadata = extract_metadata_from_pdf(pdf_path)
        print(f"   타입: {metadata['type']}")
        print(f"   제목: {metadata.get('title', 'Unknown')}")

        folder_id = generate_folder_id()
        print(f"   폴더ID: {folder_id}")

        result = create_standard_folder(folder_id, metadata, pdf_path)
        processed_pdfs.append(
            {"folder_id": folder_id, "metadata": metadata, "result": result}
        )
        print(f"   성공: {result['folder_path']}")

    # 결과 요약
    print(f"\n처리 결과:")
    print(f"   PDF 처리: {len(processed_pdfs)}개 성공")
    print(f"   리스트 처리: {list_result.get('processed', 0)}개")

    # paper_list.md 업데이트
    update_paper_list(processed_pdfs)

    print(f"\n처리 완료!")


def update_paper_list(processed_pdfs):
    """paper_list.md 업데이트"""
    paper_list_path = PAPER_DIR / "paper_list.md"

    # 기존 내용 읽기
    if paper_list_path.exists():
        with open(paper_list_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = """# d0014_논문리스트.md - 논문 목록

## 문서 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-01-21 | 최초 작성 |

---

## 총 논문수
**N개** (완료: X개, 미완료: Y개)

---

## 논문리스트

"""

    # 새로운 논문 추가
    new_entries = []
    for pdf_info in processed_pdfs:
        folder_id = pdf_info["folder_id"]
        metadata = pdf_info["metadata"]
        title = metadata.get("title", "Unknown")

        author = metadata.get("author", "-")
        year = metadata.get("year", "-")
        source = metadata.get("source", "-")
        keywords = metadata.get("keywords", "")

        entry = f"### {folder_id} - {title}\n"
        if keywords:
            entry += f"- **키워드**: {keywords}\n"
        entry += f"- **저자**: {author} | **연도**: {year} | **출처**: {source}\n"
        entry += f"- **등록일**: {datetime.now().strftime('%Y-%m-%d')} | **완료**: X\n\n"
        new_entries.append(entry)

    # 업데이트
    if new_entries:
        content += "\n".join(new_entries)

        with open(paper_list_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"paper_list.md 업데이트 완료 ({len(new_entries)}개 추가)")


if __name__ == "__main__":
    main()
