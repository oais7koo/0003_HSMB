# -*- coding: utf-8 -*-
# ################################################################################
# Title: ooscrap add - 다운로드 리스트에 URL 추가
# Author: ookoo
# Date: 2026.03.26
# Version: v01
# Goal: 04_scraping/00_down/01_다운로드.md에 URL을 추가
# ################################################################################
import os
import re
import sys
import argparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))

DOWNLOAD_FILE = os.path.join(project_root, "04_scraping", "00_down", "01_다운로드.md")

SECTIONS = {
    "다운": "## 다운",
    "동영상": "## 동영상",
    "음악": "## 음악",
}


def parse_args():
    parser = argparse.ArgumentParser(description="ooscrap add - URL 추가")
    parser.add_argument("urls", nargs="+", help="추가할 URL (여러 개 가능)")
    parser.add_argument(
        "--section",
        choices=["다운", "동영상", "음악"],
        default="다운",
        help="추가할 섹션 (기본: 다운)",
    )
    parser.add_argument("--video", action="store_true", help="## 동영상 섹션에 추가")
    parser.add_argument("--music", action="store_true", help="## 음악 섹션에 추가")
    return parser.parse_args()


def clean_url(raw):
    """마크다운 링크에서 URL 추출, 공백 제거"""
    url = raw.strip()
    m = re.search(r"\[([^\]]*)\]\(([^)]+)\)", url)
    if m:
        url = m.group(2)
    url = re.sub(r"[&?]t=\d+s?", "", url)
    url = re.sub(r"&$", "", url)
    return url.strip()


def read_file(filepath):
    """파일 읽기, 없으면 기본 템플릿 반환"""
    if not os.path.exists(filepath):
        return "\n## 다운\n\n## 동영상\n\n## 음악\n"
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def get_existing_urls(content):
    """파일 내 기존 URL 목록 추출"""
    urls = set()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("http"):
            urls.add(stripped)
    return urls


def insert_urls(content, section_header, urls):
    """지정 섹션 헤더 바로 아래에 URL 삽입"""
    lines = content.splitlines(keepends=True)
    result = []
    inserted = False
    skip_next_blank = False

    for i, line in enumerate(lines):
        if skip_next_blank:
            skip_next_blank = False
            continue
        result.append(line)
        if not inserted and line.strip() == section_header:
            # 헤더 다음 빈 줄 유지 후 URL 삽입
            if i + 1 < len(lines) and lines[i + 1].strip() == "":
                result.append(lines[i + 1])  # 빈 줄 유지
                skip_next_blank = True
            else:
                result.append("\n")
            for url in urls:
                result.append(url + "\n")
            result.append("\n")  # URL 뒤 빈 줄 (다음 섹션과 구분)
            inserted = True

    if not inserted:
        result.append(f"\n{section_header}\n\n")
        for url in urls:
            result.append(url + "\n")
        result.append("\n")

    return "".join(result)


def main():
    args = parse_args()

    # 섹션 결정
    if args.video:
        section = "동영상"
    elif args.music:
        section = "음악"
    else:
        section = args.section

    section_header = SECTIONS[section]

    # URL 정리
    urls = [clean_url(u) for u in args.urls]
    urls = [u for u in urls if u.startswith("http")]

    if not urls:
        print("[ERROR] 유효한 URL이 없습니다.")
        sys.exit(1)

    # 파일 읽기
    content = read_file(DOWNLOAD_FILE)
    existing = get_existing_urls(content)

    # 중복 체크
    new_urls = []
    dup_urls = []
    for url in urls:
        if url in existing:
            dup_urls.append(url)
        else:
            new_urls.append(url)

    if dup_urls:
        for u in dup_urls:
            print(f"  [SKIP] 이미 존재: {u}")

    if not new_urls:
        print("[INFO] 추가할 새 URL이 없습니다 (모두 중복).")
        return

    # URL 삽입
    content = insert_urls(content, section_header, new_urls)

    # 디렉토리 생성 + 파일 저장
    os.makedirs(os.path.dirname(DOWNLOAD_FILE), exist_ok=True)
    with open(DOWNLOAD_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    # 결과 출력
    print(f"\n[OK] {len(new_urls)}건 추가 → [{section}] 섹션")
    for u in new_urls:
        print(f"  + {u}")
    print(f"  파일: {DOWNLOAD_FILE}")


if __name__ == "__main__":
    main()
