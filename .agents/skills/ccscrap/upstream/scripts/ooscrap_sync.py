# -*- coding: utf-8 -*-
# ################################################################################
# Title: ooscrap sync - 등록 채널 신규 영상 동기화
# Author: ookoo
# Date: 2026.04.03
# Version: v01
# Goal: 03_유튜브채널리스트.md의 등록 채널에서 신규 영상을 검색하여 01_다운로드.md에 추가
# Changes:
#   - v01: 초기 버전
# ################################################################################
import os
import re
import sys
import argparse
import datetime

from yt_dlp import YoutubeDL

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))

# 경로 설정
CHANNEL_LIST = os.path.join(project_root, "04_scraping", "00_down", "03_유튜브채널리스트.md")
HISTORY_FILE = os.path.join(project_root, "04_scraping", "00_down", "02_유튜브동영상리스트.md")
DOWNLOAD_FILE = os.path.join(project_root, "04_scraping", "00_down", "01_다운로드.md")


def parse_args():
    parser = argparse.ArgumentParser(description="ooscrap sync - 채널 신규 영상 동기화")
    parser.add_argument("--channel", type=str, default=None, help="특정 채널 URL만 동기화")
    parser.add_argument("--dry-run", action="store_true", help="실제 추가 없이 신규 영상 목록만 표시")
    return parser.parse_args()


def load_channel_list(filepath):
    """03_유튜브채널리스트.md 파싱 → [{url, name, last_scan, count}]
    채널명에 이스케이프된 파이프(\\|)가 포함될 수 있으므로 역방향 파싱 사용.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] 채널 리스트 파일 없음: {filepath}")
        return []

    channels = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or "채널 URL" in line or "---" in line:
                continue
            # 이스케이프된 파이프를 임시 치환 후 분할
            escaped = line.replace("\\|", "\x00")
            parts = [p.strip().replace("\x00", "|") for p in escaped.split("|")]
            # parts: ['', url, name, last_scan, count, '']
            if len(parts) < 5:
                continue
            url = parts[1]
            if not url.startswith("http"):
                continue
            channels.append({
                "url": url,
                "name": parts[2],
                "last_scan": parts[3],
                "count": int(parts[4]) if parts[4].isdigit() else 0,
            })
    return channels


def load_existing_video_ids(history_path):
    """02_유튜브동영상리스트.md에서 기존 처리된 비디오 ID 집합 로드"""
    ids = set()
    if not os.path.exists(history_path):
        return ids
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            if "http" in line:
                vid = extract_video_id(line)
                if vid:
                    ids.add(vid)
    return ids


def load_download_video_ids(download_path):
    """01_다운로드.md에 이미 등록된 비디오 ID 집합 로드"""
    ids = set()
    if not os.path.exists(download_path):
        return ids
    with open(download_path, "r", encoding="utf-8") as f:
        for line in f:
            if "http" in line:
                vid = extract_video_id(line)
                if vid:
                    ids.add(vid)
    return ids


def extract_video_id(text):
    """텍스트에서 YouTube 비디오 ID 추출"""
    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/live/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return None


def fetch_channel_videos(channel_url, after_date=None):
    """채널의 영상 목록을 가져와서 신규 영상 필터링
    Args:
        channel_url: 채널 URL
        after_date: 이 날짜 이후 영상만 (YYYY-MM-DD 문자열, None이면 전체)
    Returns:
        list of {id, title, url, upload_date, duration}
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": 200,  # 최근 200개까지 스캔
    }

    # /videos 탭 URL 구성
    if "/videos" not in channel_url:
        videos_url = channel_url.rstrip("/") + "/videos"
    else:
        videos_url = channel_url

    print(f"  채널 영상 목록 조회 중...")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(videos_url, download=False)
    except Exception as e:
        print(f"  [ERROR] 채널 조회 실패: {e}")
        return []

    entries = info.get("entries", [])
    if not entries:
        print(f"  영상 없음")
        return []

    videos = []
    for entry in entries:
        if not entry:
            continue
        vid = entry.get("id", "")
        title = entry.get("title", "")
        duration = entry.get("duration") or 0
        upload_date = entry.get("upload_date", "")  # YYYYMMDD

        # 쇼츠 제외 (60초 미만)
        if duration and duration < 60:
            continue

        # 날짜 필터링
        if after_date and upload_date:
            scan_date_str = after_date.replace("-", "")
            if upload_date <= scan_date_str:
                continue

        url = f"https://www.youtube.com/watch?v={vid}"
        videos.append({
            "id": vid,
            "title": title,
            "url": url,
            "upload_date": upload_date,
            "duration": duration,
        })

    return videos


def add_urls_to_download(download_path, urls):
    """01_다운로드.md의 ## 다운 섹션에 URL 추가"""
    if not os.path.exists(download_path):
        content = "\n## 다운\n\n## 동영상\n\n## 음악\n"
    else:
        with open(download_path, "r", encoding="utf-8") as f:
            content = f.read()

    lines = content.splitlines(keepends=True)
    result = []
    inserted = False

    for i, line in enumerate(lines):
        result.append(line)
        if not inserted and line.strip() == "## 다운":
            # 헤더 다음 빈 줄 유지
            if i + 1 < len(lines) and lines[i + 1].strip() == "":
                result.append(lines[i + 1])
                # 이미 있는 URL 뒤에 추가하기 위해 기존 URL 스캔
                j = i + 2
                while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("##"):
                    result.append(lines[j])
                    j += 1
                # 신규 URL 삽입
                for url in urls:
                    result.append(url + "\n")
                # 나머지 줄 추가
                for k in range(j, len(lines)):
                    result.append(lines[k])
                inserted = True
                break
            else:
                result.append("\n")
                for url in urls:
                    result.append(url + "\n")
                inserted = True

    if not inserted:
        result.append("\n## 다운\n\n")
        for url in urls:
            result.append(url + "\n")

    with open(download_path, "w", encoding="utf-8") as f:
        f.write("".join(result))


def update_channel_list(filepath, channel_url, new_count):
    """03_유튜브채널리스트.md에서 해당 채널의 마지막 스캔일과 등록 영상 수 업데이트"""
    if not os.path.exists(filepath):
        return

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated = []
    for line in lines:
        if channel_url in line and line.strip().startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                parts[3] = f" {today} "
                parts[4] = f" {new_count} "
                line = "|".join(parts) + "\n"
        updated.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(updated)


def main():
    args = parse_args()
    now = datetime.datetime.now().strftime("%y%m%d%H%M")
    print(f"ooscrap_sync_{now}")
    print(f"\n{'='*60}")
    print("ooscrap sync - 등록 채널 신규 영상 동기화")
    print(f"{'='*60}")

    # 1) 채널 리스트 로드
    channels = load_channel_list(CHANNEL_LIST)
    if not channels:
        print("[INFO] 등록된 채널이 없습니다.")
        return

    # 특정 채널만 필터
    if args.channel:
        channels = [c for c in channels if args.channel in c["url"]]
        if not channels:
            print(f"[ERROR] 채널을 찾을 수 없습니다: {args.channel}")
            return

    print(f"등록 채널: {len(channels)}개")

    # 2) 기존 처리 비디오 ID 로드
    existing_ids = load_existing_video_ids(HISTORY_FILE)
    download_ids = load_download_video_ids(DOWNLOAD_FILE)
    all_known_ids = existing_ids | download_ids
    print(f"기존 처리/대기 영상: {len(all_known_ids)}개")

    # 3) 채널별 신규 영상 검색
    total_new = 0
    all_new_urls = []

    for ch in channels:
        print(f"\n--- {ch['name']} ({ch['url']})")
        print(f"  마지막 스캔: {ch['last_scan']}")

        videos = fetch_channel_videos(ch["url"], after_date=ch["last_scan"])
        print(f"  스캔 날짜 이후 영상: {len(videos)}개")

        # 중복 제거
        new_videos = [v for v in videos if v["id"] not in all_known_ids]
        print(f"  신규 영상 (미처리): {len(new_videos)}개")

        if new_videos:
            for v in new_videos:
                date_str = v["upload_date"]
                if date_str:
                    date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                dur_min = v["duration"] // 60 if v["duration"] else "?"
                print(f"    + [{date_str}] {v['title'][:50]} ({dur_min}분)")
                all_new_urls.append(v["url"])
                all_known_ids.add(v["id"])  # 중복 방지

            total_new += len(new_videos)
            new_total_count = ch["count"] + len(new_videos)

            if not args.dry_run:
                update_channel_list(CHANNEL_LIST, ch["url"], new_total_count)
        else:
            if not args.dry_run:
                update_channel_list(CHANNEL_LIST, ch["url"], ch["count"])

    # 4) 01_다운로드.md에 추가
    if all_new_urls and not args.dry_run:
        add_urls_to_download(DOWNLOAD_FILE, all_new_urls)
        print(f"\n[OK] 01_다운로드.md에 {len(all_new_urls)}건 추가 완료")
    elif args.dry_run and all_new_urls:
        print(f"\n[DRY-RUN] 추가 예정: {len(all_new_urls)}건 (실제 추가 안 함)")

    # 5) 결과 요약
    print(f"\n{'='*60}")
    print("동기화 완료")
    print(f"{'='*60}")
    print(f"스캔 채널: {len(channels)}개")
    print(f"신규 영상: {total_new}건")
    if not args.dry_run and total_new > 0:
        print(f"\n→ `ooscrap run`으로 STT 처리하세요.")


if __name__ == "__main__":
    main()
