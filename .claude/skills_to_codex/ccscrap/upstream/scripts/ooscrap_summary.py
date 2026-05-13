# -*- coding: utf-8 -*-
# ################################################################################
# Title: ooscrap STT - 유튜브 음성→텍스트 변환
# Author: ookoo
# Date: 2026.02.19
# Version: v06
# Goal: youtube_url.md의 유튜브 URL에서 음성을 추출하여 텍스트로 변환
# Changes:
#   - v06: 경로 변경 (04_youtube/ → 03_paper/, 출력 폴더 03_paper/04_youtube/)
#   - v05: 자막 우선 모드 (수동자막 > 자동자막 > Whisper STT 폴백)
#   - v04: ffmpeg 의존성 제거 (webm 직접 사용)
#   - v03: 실패 URL은 youtube_url.md에서 # 주석 처리
#   - v02: 처리 완료된 URL을 youtube_url.md에서 자동 제거
#   - v01: 초기 버전 (ps8035 파이프라인 재활용)
# Description:
#   - 03_paper/youtube_url.md에서 URL 목록 읽기
#   - 자막 우선: 한국어 자막 있으면 다운로드, 없으면 Whisper STT
#   - 03_paper/04_youtube/YYMMDD-HHMM_제목.md 저장
#   - 03_paper/stt.xlsx에 이력 기록
# Input: 03_paper/youtube_url.md
# Output: 03_paper/04_youtube/*.md, 03_paper/stt.xlsx
# ################################################################################
# Library
# ################################################################################
import os
import re
import sys
import json
import time
import datetime
import glob as glob_module
import warnings

from yt_dlp import YoutubeDL

# Windows UTF-8 출력 설정 (cp949 인코딩 에러 방지)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 프로젝트 루트 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
sys.path.insert(0, project_root)

# ################################################################################
# Setting
# ################################################################################
dsr = datetime.datetime.now().strftime("%y%m%d%H%M")
print(f"ooscrap_summary_{dsr}")

stime = time.time()
warnings.filterwarnings("default")

# CLI 인자 파싱
import argparse
parser = argparse.ArgumentParser(description="ooscrap STT")
parser.add_argument("command", nargs="?", default="stt", help="서브명령어")
parser.add_argument("--force", action="store_true", help="중복 URL도 재처리")
parser.add_argument("--subtitle-only", action="store_true", help="자막만 처리 (Whisper STT 스킵)")
cli_args = parser.parse_args()

if cli_args.command in ("help", "-h"):
    print("ooscrap [summary|read|run|add|sync|status|help]\n콘텐츠 스크래핑 통합")
    sys.exit(0)

# 경로 설정
URL_FILE = os.path.join(project_root, "04_scraping", "00_down", "01_다운로드.md")
STT_DIR = os.path.join(project_root, "04_scraping", "01_유튜브서머리")
HISTORY_FILE = os.path.join(project_root, "04_scraping", "00_down", "02_유튜브동영상리스트.md")
TMP_DIR = os.path.join(project_root, "04_scraping", "00_down")

# Whisper 설정
WHISPER_CONFIG = {
    "model_size": "medium",
    "device": "cuda",
    "compute_type": "float16",
    "language": "ko",
    "beam_size": 5,
    "vad_filter": True,
}


# ################################################################################
# Function
# ################################################################################
def format_time(seconds):
    """초를 HH:MM:SS 형식으로 변환"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def clean_url(raw):
    """마크다운 링크/중첩 링크에서 URL 추출, &t= 제거, 정규화"""
    # 마크다운 링크 [text](url) → url 추출 (중첩 포함)
    url = raw
    while True:
        m = re.search(r'\[([^\]]*)\]\(([^)]+)\)', url)
        if not m:
            break
        # 괄호 안 URL 우선, 없으면 대괄호 텍스트
        candidate = m.group(2)
        if "youtube" in candidate or "youtu.be" in candidate:
            url = candidate
        else:
            url = m.group(1)
        # 한번 더 체크 (중첩 케이스)
        if "[" not in url:
            break
    # URL 디코딩 (%5d 등)
    url = url.replace("%5d", "").replace("%5D", "")
    url = url.replace("\\(", "").replace("\\)", "")
    # &t=XXs 타임스탬프 제거
    url = re.sub(r'[&?]t=\d+s?', '', url)
    # 후행 & 정리
    url = re.sub(r'&$', '', url)
    return url.strip()


def extract_video_id(url):
    """URL에서 YouTube 비디오 ID 추출"""
    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/live/([a-zA-Z0-9_-]{11})',
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def read_urls(filepath):
    """youtube_url.md에서 URL 목록 읽기 (정리+중복 제거)
    - 마크다운 링크 [URL](URL) → 기본 URL 변환
    - &t= 타임스탬프 제거
    - 동일 비디오 ID 중복 제거
    - 빈 줄/주석 무시
    - 정리 결과를 파일에 다시 저장
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] URL 파일 없음: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    urls = []
    seen_ids = set()
    cleaned = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # URL 정리
        url = clean_url(stripped)
        if url != stripped:
            cleaned = True
        # 중복 제거 (비디오 ID 기준)
        vid = extract_video_id(url)
        if vid and vid in seen_ids:
            cleaned = True
            continue
        if vid:
            seen_ids.add(vid)
        if url:
            urls.append(url)

    # 정리된 내용 파일에 반영 (섹션 헤더 보존)
    if cleaned and urls:
        cleaned_set = set(urls)
        new_lines = []
        for line in lines:
            stripped = line.strip()
            # 섹션 헤더(## 다운, ## 동영상, ## 음악)와 빈 줄은 보존
            if not stripped or stripped.startswith("## "):
                new_lines.append(line)
                continue
            # 주석(# [FAIL] 등)은 보존
            if stripped.startswith("#"):
                new_lines.append(line)
                continue
            # URL은 정리된 버전으로 교체
            url = clean_url(stripped)
            vid = extract_video_id(url)
            if url in cleaned_set:
                new_lines.append(url + "\n")
                cleaned_set.discard(url)
            # 중복 URL은 제거 (cleaned_set에 없으면 이미 작성됨)
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"  youtube_url.md 자동 정리: {len(urls)}개 URL")

    return urls


def load_existing_urls(history_path):
    """02_유튜브동영상리스트.md에서 기존 처리된 URL 목록 로드"""
    if not os.path.exists(history_path):
        return set()
    existing = set()
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|") and "http" in line:
                parts = [p.strip() for p in line.split("|")]
                for part in parts:
                    if part.startswith("http"):
                        existing.add(part)
    return existing


def make_safe_filename(title):
    """제목에서 안전한 파일명 생성 (파일시스템 금지 문자만 제거, 가독성 유지)"""
    # 파일시스템 금지 문자만 제거: \ / : * ? " < > | 및 이모지
    safe = re.sub(r'[\\/:*?"<>|\U00010000-\U0010ffff]', '', title).strip()
    safe = re.sub(r"\s+", " ", safe)
    if len(safe) > 80:
        safe = safe[:80].strip()
    return safe


# ################################################################################
# 자막 관련 함수
# ################################################################################
def extract_video_info(url):
    """URL에서 영상 정보 추출 (다운로드 없음)"""
    ydl_opts = {"skip_download": True, "quiet": True, "no_warnings": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "id": info["id"],
        "title": info.get("title", info["id"]),
        "subtitles": info.get("subtitles", {}),
        "automatic_captions": info.get("automatic_captions", {}),
    }


def download_subtitles(url, video_info, tmp_dir):
    """자막 다운로드 및 파싱. 자막 없으면 None 반환.
    우선순위: 수동 자막(ko) > 자동 자막(ko)
    Returns: (segments, sub_type) or (None, None)
    """
    subs = video_info.get("subtitles", {})
    auto_caps = video_info.get("automatic_captions", {})
    video_id = video_info["id"]

    # 한국어 자막 확인 (수동 > 자동)
    if "ko" in subs:
        sub_type = "수동"
        write_sub = True
        write_auto = False
        print("  한국어 수동 자막 발견")
    elif "ko" in auto_caps:
        sub_type = "자동"
        write_sub = False
        write_auto = True
        print("  한국어 자동 자막 발견")
    else:
        return None, None

    os.makedirs(tmp_dir, exist_ok=True)
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": write_sub,
        "writeautomaticsub": write_auto,
        "subtitleslangs": ["ko"],
        "subtitlesformat": "json3",
        "outtmpl": os.path.join(tmp_dir, "%(id)s"),
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"  자막 다운로드 실패: {e}")
        return None, None

    # 자막 파일 찾기
    sub_pattern = os.path.join(tmp_dir, f"{video_id}.ko.*")
    sub_files = glob_module.glob(sub_pattern)
    if not sub_files:
        print("  자막 파일 다운로드 실패")
        return None, None

    sub_path = sub_files[0]
    ext = os.path.splitext(sub_path)[1].lower()

    try:
        if ext == ".json3":
            segments = parse_json3(sub_path)
        elif ext in (".vtt", ".srt"):
            segments = parse_vtt_srt(sub_path)
        else:
            print(f"  미지원 자막 형식: {ext}")
            segments = None
    finally:
        for f in sub_files:
            if os.path.exists(f):
                os.remove(f)

    if segments:
        print(f"  자막 파싱 완료: {len(segments)}개 세그먼트")
    return segments, sub_type


def parse_json3(filepath):
    """json3 자막 파일 파싱"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = []
    for event in data.get("events", []):
        if "segs" not in event:
            continue
        start_ms = event.get("tStartMs", 0)
        duration_ms = event.get("dDurationMs", 0)
        text = "".join(seg.get("utf8", "") for seg in event["segs"]).strip()
        text = text.replace("\n", " ").strip()
        if not text:
            continue
        segments.append({
            "start": start_ms / 1000.0,
            "end": (start_ms + duration_ms) / 1000.0,
            "text": text,
        })
    return segments if segments else None


def parse_vtt_srt(filepath):
    """VTT/SRT 자막 파일 파싱"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(\d{2}:\d{2}:\d{2})[.,](\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2})[.,](\d{3})\s*\n(.+?)(?=\n\n|\n\d|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    segments = []
    for start_time, start_ms, end_time, end_ms, text in matches:
        text = re.sub(r"<[^>]+>", "", text)
        text = text.strip().replace("\n", " ")
        if not text:
            continue
        h, m, s = start_time.split(":")
        start_sec = int(h) * 3600 + int(m) * 60 + int(s) + int(start_ms) / 1000
        h, m, s = end_time.split(":")
        end_sec = int(h) * 3600 + int(m) * 60 + int(s) + int(end_ms) / 1000
        segments.append({
            "start": start_sec,
            "end": end_sec,
            "text": text,
        })
    return segments if segments else None


# ################################################################################
# 오디오/STT 관련 함수
# ################################################################################
def download_audio(url, audio_dir):
    """유튜브 영상에서 오디오만 추출 (ffmpeg 불필요, webm 직접 사용)"""
    os.makedirs(audio_dir, exist_ok=True)
    output_template = os.path.join(audio_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info["id"]

    # 다운로드된 파일 찾기 (확장자가 webm, m4a, opus 등 다양)
    pattern = os.path.join(audio_dir, f"{video_id}.*")
    matches = glob_module.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"다운로드된 오디오 파일 없음: {pattern}")
    audio_path = matches[0]
    return audio_path, video_id


def transcribe(audio_path):
    """음성 파일을 텍스트로 변환 (CUDA 실패 시 CPU 폴백)"""
    from faster_whisper import WhisperModel

    wcfg = WHISPER_CONFIG
    device = wcfg["device"]
    compute_type = wcfg["compute_type"]

    print(f"  Whisper 모델 로딩: {wcfg['model_size']} ({device})")
    try:
        model = WhisperModel(
            wcfg["model_size"],
            device=device,
            compute_type=compute_type,
        )
    except Exception as e:
        print(f"  [WARN] {device} 실패: {e}")
        device = "cpu"
        compute_type = "int8"
        print(f"  CPU 폴백으로 재시도: {wcfg['model_size']} ({device})")
        model = WhisperModel(
            wcfg["model_size"],
            device=device,
            compute_type=compute_type,
        )

    print("  음성 인식 시작...")
    segments, info = model.transcribe(
        audio_path,
        language=wcfg["language"],
        beam_size=wcfg["beam_size"],
        vad_filter=wcfg["vad_filter"],
    )

    results = []
    for seg in segments:
        results.append(
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
            }
        )

    print(f"  음성 인식 완료: {len(results)}개 세그먼트")
    return results


# ################################################################################
# 출력/기록 함수
# ################################################################################
def save_transcript(segments, output_path, video_title="", video_url="", source=""):
    """결과를 마크다운 파일로 저장 (타임스탬프 테이블 형식)"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(output_path, "w", encoding="utf-8") as f:
        if video_title:
            f.write(f"# {video_title}\n\n")
        if video_url:
            f.write(f"> URL: {video_url}\n")
        f.write(f"> 날짜: {now_str}\n")
        if source:
            f.write(f"> 소스: {source}\n")
        f.write("\n")
        f.write("## 트랜스크립트\n\n")
        f.write("| 시간 | 내용 |\n")
        f.write("|------|------|\n")
        for seg in segments:
            start = format_time(seg["start"])
            end = format_time(seg["end"])
            text = seg["text"].replace("|", "\\|")
            f.write(f"| {start} - {end} | {text} |\n")
    print(f"  트랜스크립트 저장: {output_path}")


def append_to_history(history_path, timestamp, title, url):
    """02_유튜브동영상리스트.md에 행 추가 (없으면 신규 생성)"""
    if not os.path.exists(history_path):
        with open(history_path, "w", encoding="utf-8") as f:
            f.write("# 유튜브 동영상 처리 이력\n\n")
            f.write("| 타임스탬프 | 제목 | URL |\n")
            f.write("|-----------|------|-----|\n")

    with open(history_path, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | {title} | {url} |\n")
    print(f"  이력 기록 완료: {history_path}")


def cleanup_url_file(filepath, processed_urls, failed_urls):
    """youtube_url.md 정리: 성공/스킵 URL 제거, 실패 URL은 # 주석+사유 기록
    Args:
        processed_urls: set - 성공/스킵된 URL
        failed_urls: dict - {URL: 에러사유}
    """
    if not os.path.exists(filepath):
        return
    if not processed_urls and not failed_urls:
        return
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    remaining = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped in processed_urls:
            continue
        if stripped and not stripped.startswith("#") and stripped in failed_urls:
            reason = failed_urls[stripped]
            remaining.append(f"# [FAIL] {stripped} | {reason}\n")
            continue
        remaining.append(line)
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(remaining)
    removed = len(processed_urls)
    commented = len(failed_urls)
    if removed:
        print(f"  youtube_url.md 정리: {removed}건 제거")
    if commented:
        print(f"  youtube_url.md 정리: {commented}건 주석 처리 (실패+사유)")


# ################################################################################
# Main
# ################################################################################
def main():
    print(f"\n{'='*60}")
    mode = "자막 전용" if cli_args.subtitle_only else "자막 우선"
    print(f"ooscrap STT 시작 (v05: {mode})")
    print(f"{'='*60}")

    # 1) URL 읽기
    urls = read_urls(URL_FILE)
    if not urls:
        print("[INFO] 처리할 URL이 없습니다.")
        return

    print(f"URL 목록: {len(urls)}개")

    # 2) 기존 처리 URL 로드 (중복 방지, --force 시 스킵)
    if cli_args.force:
        existing_urls = set()
        print("--force 모드: 중복 체크 건너뜀")
    else:
        existing_urls = load_existing_urls(HISTORY_FILE)
        print(f"기존 처리 URL: {len(existing_urls)}개")

    # 3) 출력 디렉토리 생성
    os.makedirs(STT_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)

    # 4) URL별 처리
    success_count = 0
    skip_count = 0
    fail_count = 0
    sub_count = 0  # 자막으로 처리된 건수
    stt_count = 0  # Whisper STT로 처리된 건수
    processed_urls = set()  # 처리 완료된 URL (성공+스킵)
    failed_urls = {}  # 실패한 URL -> 에러 사유

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")

        # 중복 체크
        if url.strip() in existing_urls:
            print("  -> 이미 처리됨, 스킵")
            skip_count += 1
            processed_urls.add(url.strip())
            continue

        try:
            # 4-1) 영상 정보 추출
            print("  영상 정보 확인...")
            video_info = extract_video_info(url)
            video_title = video_info["title"]
            print(f"  제목: {video_title}")

            # 4-2) 자막 우선 시도
            segments, sub_type = download_subtitles(url, video_info, TMP_DIR)

            if segments:
                # 자막으로 처리 완료
                source = f"자막 ({sub_type})"
                sub_count += 1
            elif cli_args.subtitle_only:
                # --subtitle-only 모드: Whisper 스킵
                print("  자막 없음, --subtitle-only 모드로 스킵")
                fail_count += 1
                failed_urls[url.strip()] = "자막 없음 (subtitle-only 모드)"
                continue
            else:
                # 4-3) 자막 없음 -> 오디오 다운로드 + Whisper STT
                print("  자막 없음, 오디오 다운로드...")
                audio_path, _ = download_audio(url, TMP_DIR)
                segments = transcribe(audio_path)
                source = "STT (Whisper)"
                stt_count += 1

                # 임시 오디오 삭제
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    print(f"  임시 파일 삭제: {audio_path}")

            # 4-4) 결과 파일 저장
            now = datetime.datetime.now()
            safe_title = make_safe_filename(video_title)
            filename = f"{now.strftime('%y%m%d-%H%M')}_{safe_title}.md"
            output_path = os.path.join(STT_DIR, filename)
            save_transcript(segments, output_path, video_title, url.strip(), source)

            # 4-5) Excel 기록
            timestamp = now.strftime("%Y-%m-%d %H:%M")
            append_to_history(HISTORY_FILE, timestamp, video_title, url.strip())

            success_count += 1
            processed_urls.add(url.strip())

        except Exception as e:
            err_msg = str(e).replace('\n', ' ').strip()
            print(f"  [ERROR] 처리 실패: {err_msg}")
            fail_count += 1
            failed_urls[url.strip()] = err_msg
            continue

    # 5) youtube_url.md 정리: 성공/스킵 제거, 실패 주석 처리
    if processed_urls or failed_urls:
        cleanup_url_file(URL_FILE, processed_urls, failed_urls)

    # 6) 유튜브팩토리.md 인덱스 갱신
    if success_count > 0:
        try:
            from ooscrap_factory import update_factory
            update_factory()
        except Exception as e:
            print(f"  [WARN] 유튜브팩토리.md 갱신 실패: {e}")

    # 7) 결과 요약
    etime = time.time()
    print(f"\n{'='*60}")
    print("처리 완료")
    print(f"{'='*60}")
    print(f"성공: {success_count}건 (자막: {sub_count}, STT: {stt_count})")
    print(f"스킵(중복): {skip_count}건")
    print(f"실패: {fail_count}건")
    print(f"소요 시간: {etime - stime:.2f}초")


if __name__ == "__main__":
    main()
