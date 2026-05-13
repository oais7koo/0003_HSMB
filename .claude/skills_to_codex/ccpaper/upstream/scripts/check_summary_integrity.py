"""
03_paper 서머리 정합성 검증 스크립트 (C018)
검사 항목:
  1. 빈/0바이트 파일
  2. 매우 작은 파일 (200바이트 미만 — 헤더만 있는 파일)
  3. HTML 태그 포함 (깨진 파일)
  4. 중복 서머리 (폴더 간 동일 파일명 또는 동일 제목)
  5. 미완성 서머리 (TODO / 작성중 / 섹션 본문 없음)
"""

import os
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path("03_paper")
EN_DIR = ROOT / "11_paper_en"
KO_DIR = ROOT / "12_paper_ko"

HTML_PATTERN = re.compile(r"<html|<!DOCTYPE|<head|<body|<div|<script", re.IGNORECASE)
TODO_PATTERN = re.compile(r"\bTODO\b|작성\s*중|미작성|작성예정", re.IGNORECASE)

# 핵심 섹션 헤더 (서머리에 있어야 할 내용)
REQUIRED_SECTIONS = ["##", "###"]

results = {
    "empty": [],        # 0바이트
    "tiny": [],         # 200바이트 미만 (헤더만)
    "html_broken": [],  # HTML 태그 포함
    "incomplete": [],   # TODO/작성중/헤더만
    "duplicates": [],   # 중복
}

title_map = defaultdict(list)   # 제목 → 파일 목록 (중복 탐지용)
filename_map = defaultdict(list) # 파일명(폴더명 제외) → 경로 목록

def normalize_title(text: str) -> str:
    """제목 정규화 (비교용)"""
    text = re.sub(r"\s+", " ", text.strip().lower())
    text = re.sub(r"[^\w\s]", "", text)
    return text

def extract_title(content: str, filepath: Path) -> str:
    """서머리에서 제목 추출 (# 제목 또는 파일명에서)"""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# ") and not line.startswith("##"):
            return normalize_title(line[2:])
    # 파일명에서 추출
    name = filepath.stem
    parts = name.split("_", 2)
    if len(parts) >= 3:
        return normalize_title(parts[2].replace("_서머리", "").replace("_summary", ""))
    return normalize_title(name)

def check_file(filepath: Path):
    stat = filepath.stat()
    size = stat.st_size

    # 1. 빈 파일
    if size == 0:
        results["empty"].append(str(filepath))
        return

    content = filepath.read_text(encoding="utf-8", errors="replace")

    # 2. 매우 작은 파일
    if size < 200:
        results["tiny"].append((str(filepath), size))
        return

    # 3. HTML 태그 포함
    if HTML_PATTERN.search(content[:2000]):
        results["html_broken"].append(str(filepath))
        return

    # 4. 미완성 체크
    is_incomplete = False
    if TODO_PATTERN.search(content):
        is_incomplete = True
    else:
        # 섹션 본문이 거의 없는 경우: ## 헤더만 있고 내용 없음
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        non_header_lines = [l for l in lines if not l.startswith("#") and not l.startswith("|") and l != "---"]
        if len(non_header_lines) < 3:
            is_incomplete = True

    if is_incomplete:
        results["incomplete"].append(str(filepath))

    # 5. 중복 탐지용 수집
    title = extract_title(content, filepath)
    if title:
        title_map[title].append(str(filepath))

    # 파일명 기반 중복 (stem에서 폴더ID 부분 제거)
    stem = filepath.stem
    title_map_key = re.sub(r"^\d{6}-\d{4}/", "", stem)
    filename_map[stem].append(str(filepath))


def scan_dir(base_dir: Path):
    if not base_dir.exists():
        return
    for f in base_dir.rglob("*_00_*서머리.md"):
        try:
            check_file(f)
        except Exception as e:
            print(f"  [ERROR] {f}: {e}")


print("=" * 60)
print("03_paper 서머리 정합성 검증 (C018)")
print("=" * 60)

scan_dir(EN_DIR)
scan_dir(KO_DIR)

# 중복 집계
for title, paths in title_map.items():
    if len(paths) > 1:
        results["duplicates"].append((title[:60], paths))

# ── 결과 출력 ──────────────────────────────────────────────

total = (len(results["empty"]) + len(results["tiny"]) +
         len(results["html_broken"]) + len(results["incomplete"]) +
         len(results["duplicates"]))

print(f"\n[요약]")
print(f"  빈 파일 (0바이트)     : {len(results['empty'])}건")
print(f"  극소 파일 (<200B)     : {len(results['tiny'])}건")
print(f"  HTML 깨진 파일        : {len(results['html_broken'])}건")
print(f"  미완성 서머리         : {len(results['incomplete'])}건")
print(f"  중복 서머리           : {len(results['duplicates'])}건")
print(f"  ──────────────────────")
print(f"  총 이슈               : {total}건")

if results["empty"]:
    print(f"\n[빈 파일]")
    for p in results["empty"]:
        print(f"  {p}")

if results["tiny"]:
    print(f"\n[극소 파일 (<200B)]")
    for p, sz in results["tiny"][:20]:
        print(f"  {sz:4d}B  {p}")
    if len(results["tiny"]) > 20:
        print(f"  ... 외 {len(results['tiny'])-20}건")

if results["html_broken"]:
    print(f"\n[HTML 깨진 파일]")
    for p in results["html_broken"]:
        print(f"  {p}")

if results["incomplete"]:
    print(f"\n[미완성 서머리 (상위 30건)]")
    for p in results["incomplete"][:30]:
        print(f"  {p}")
    if len(results["incomplete"]) > 30:
        print(f"  ... 외 {len(results['incomplete'])-30}건")

if results["duplicates"]:
    print(f"\n[중복 서머리 (상위 20건)]")
    for title, paths in results["duplicates"][:20]:
        print(f"  '{title}'")
        for pp in paths:
            print(f"    → {pp}")
    if len(results["duplicates"]) > 20:
        print(f"  ... 외 {len(results['duplicates'])-20}건")

print(f"\n[완료] 정합성 검증 종료")
