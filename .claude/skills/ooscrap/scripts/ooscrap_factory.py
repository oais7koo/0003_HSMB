# -*- coding: utf-8 -*-
# ################################################################################
# Title: ooscrap factory - 유튜브팩토리.md 인덱스 자동 갱신
# Author: ookoo
# Date: 2026.03.22
# Version: v01
# Goal: 01_유튜브서머리/, 04_읽을거리/ 파일 목록을 유튜브팩토리.md에 옵시디언 링크로 갱신
# ################################################################################
import os
import sys
import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))

SCRAPING_DIR = os.path.join(project_root, "04_scraping")
FACTORY_FILE = os.path.join(SCRAPING_DIR, "유튜브팩토리.md")
SUMMARY_DIR = os.path.join(SCRAPING_DIR, "01_유튜브서머리")
READ_DIR = os.path.join(SCRAPING_DIR, "04_읽을거리")


def get_md_files(directory):
    """디렉토리에서 .md 파일 목록을 최신순으로 반환 (확장자 제거)"""
    if not os.path.exists(directory):
        return []
    files = []
    for f in os.listdir(directory):
        if f.endswith(".md"):
            name = f[:-3]  # .md 제거
            mtime = os.path.getmtime(os.path.join(directory, f))
            files.append((name, mtime))
    # 최신순 정렬 (파일명이 YYMMDD-HHMMSS로 시작하므로 역순 정렬)
    files.sort(key=lambda x: x[0], reverse=True)
    return [name for name, _ in files]


def update_factory():
    """유튜브팩토리.md 갱신"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    summary_files = get_md_files(SUMMARY_DIR)
    read_files = get_md_files(READ_DIR)

    lines = []
    lines.append("## 개요")
    lines.append("유튜브 읽기 싫어서 자막 추출")
    lines.append("")
    lines.append("## 다운리스트")
    lines.append("[[01_다운로드]]")
    lines.append("")
    lines.append(f"## 유튜브서머리 ({len(summary_files)}건)")
    for name in summary_files:
        lines.append(f"- [[{name}]]")
    lines.append("")
    lines.append(f"## 읽을거리 ({len(read_files)}건)")
    for name in read_files:
        lines.append(f"- [[{name}]]")
    lines.append("")
    lines.append(f"> 마지막 갱신: {now}")
    lines.append("")

    with open(FACTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"유튜브팩토리.md 갱신 완료")
    print(f"  유튜브서머리: {len(summary_files)}건")
    print(f"  읽을거리: {len(read_files)}건")


if __name__ == "__main__":
    update_factory()
