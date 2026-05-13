"""
서머리 파일 표준화 스크립트
- YAML frontmatter 없는 서머리 파일에 표준 frontmatter 추가
- 기존 내용에서 folder_id, source_pdf, tags 등 추출
- --dry-run: 실제 수정 없이 대상 목록만 출력
"""
import re
import sys
import os
from pathlib import Path
from datetime import datetime

def get_paper_root():
    cwd = Path.cwd()
    if (cwd / "03_paper").exists():
        return cwd / "03_paper"
    return cwd

def extract_meta(content: str, folder_id: str) -> dict:
    """기존 서머리 내용에서 메타데이터 추출"""
    meta = {
        "folder_id": folder_id,
        "generated_at": "",
        "engine": "legacy",
        "source_pdf": "",
        "language": "영어",
        "translation_status": "unknown",
        "translation_ratio": "",
        "translation_note": "레거시 포맷에서 변환",
    }

    # source_pdf 추출
    m = re.search(r"출처:\s*(.+\.pdf)", content)
    if m:
        meta["source_pdf"] = m.group(1).strip()

    # language 추출
    m = re.search(r"논문 언어\s*[:\：]\s*(.+)", content)
    if m:
        meta["language"] = m.group(1).strip()

    return meta

def build_frontmatter(meta: dict) -> str:
    return f"""---
type: summary
folder_id: {meta['folder_id']}
generated_at: {meta['generated_at']}
engine: {meta['engine']}
source_pdf: {meta['source_pdf']}
language: {meta['language']}
translation:
  status: {meta['translation_status']}
  ratio: {meta['translation_ratio']}
  note: {meta['translation_note']}
---

"""

def process_file(path: Path, dry_run: bool) -> str:
    content = path.read_text(encoding="utf-8")

    # 이미 frontmatter 있으면 스킵
    if content.startswith("---"):
        return "skip"

    folder_id = path.parent.name
    meta = extract_meta(content, folder_id)
    frontmatter = build_frontmatter(meta)

    if not dry_run:
        path.write_text(frontmatter + content, encoding="utf-8")
    return "updated"

def main():
    dry_run = "--dry-run" in sys.argv
    paper_root = get_paper_root()
    en_root = paper_root / "11_paper_en"

    if not en_root.exists():
        print(f"[ERROR] 경로 없음: {en_root}")
        sys.exit(1)

    files = sorted(en_root.rglob("*_00_*서머리.md"))
    total = len(files)
    updated = skipped = 0

    print(f"# 서머리 표준화 {'(dry-run)' if dry_run else ''}")
    print(f"대상: {total}개\n")

    for f in files:
        result = process_file(f, dry_run)
        if result == "updated":
            updated += 1
            if dry_run:
                try:
                    print(f"  [TO-UPDATE] {f.parent.name}/{f.name}")
                except UnicodeEncodeError:
                    print(f"  [TO-UPDATE] {f.parent.name}/(파일명 인코딩 오류)")
        else:
            skipped += 1

    print(f"\n## 결과")
    print(f"- 업데이트: {updated}개")
    print(f"- 스킵(이미 표준): {skipped}개")
    print(f"- 총: {total}개")
    if dry_run:
        print("\n※ dry-run 모드 — 실제 변경 없음")

if __name__ == "__main__":
    main()
