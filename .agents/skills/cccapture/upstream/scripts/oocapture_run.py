# -*- coding: utf-8 -*-
"""
oocapture - Flutter/Web 앱 화면 캡처 스크립트

Usage:
    uv run python .claude/skills/oocapture/scripts/oocapture_run.py [args]
"""

import argparse
import os
import shutil
import subprocess
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(description="oocapture - 앱 화면 캡처")
    parser.add_argument("--output", default="data/11_app_front", help="출력 경로")
    parser.add_argument("--port", type=int, default=8899, help="로컬 서버 포트")
    parser.add_argument("--width", type=int, default=390, help="뷰포트 너비")
    parser.add_argument("--height", type=int, default=844, help="뷰포트 높이")
    parser.add_argument("--scale", type=int, default=2, help="디바이스 스케일")
    parser.add_argument("--tabs-only", action="store_true", help="메인 탭만 캡처")
    parser.add_argument("--flutter-dir", default="08_flutterApp", help="Flutter 프로젝트 경로")
    parser.add_argument("--skip-build", action="store_true", help="빌드 건너뛰기")
    parser.add_argument("--skip-dart-copy", action="store_true", help="Dart 코드 복사 건너뛰기")
    return parser.parse_args()


# 탭 정의: (x, y, 파일명)
TAB_ITEMS = [
    (39, 820, "01_메인_홈탭"),
    (117, 820, "02_메인_오늘탭"),
    (195, 820, "03_메인_복지탭"),
    (273, 820, "04_메인_일자리탭"),
    (351, 820, "05_메인_전체탭"),
]

# 화면별 Dart 소스 매핑: (번호_카테고리_페이지명, 원본 경로)
DART_SCREENS = [
    ("01_메인_홈탭", "screens/tabs/home_tab.dart"),
    ("02_메인_오늘탭", "screens/tabs/today_tab.dart"),
    ("03_메인_일자리탭", "screens/tabs/job_tab.dart"),
    ("04_메인_복지탭", "screens/tabs/welfare_tab.dart"),
    ("05_메인_전체탭", "screens/tabs/all_tab.dart"),
    ("06_메인_메인셸", "screens/main_shell.dart"),
    ("07_인증_로그인", "screens/login_page.dart"),
    ("08_인증_게스트프로필설정", "screens/guest_profile_setup_page.dart"),
    ("09_인증_프로필수정", "screens/profile_edit_page.dart"),
    ("10_뉴스_최신기사", "screens/news_articles_recent_page.dart"),
    ("11_뉴스_동영상목록", "screens/news_videos_page.dart"),
    ("12_뉴스_동영상재생", "screens/news_video_watch_page.dart"),
    ("13_의료_채널상세", "screens/medical_channel_detail_page.dart"),
    ("14_의료_동영상재생", "screens/medical_video_watch_page.dart"),
    ("15_복지_혜택목록", "screens/welfare_benefits_page.dart"),
    ("16_복지_추천상세", "screens/featured_welfare_detail_page.dart"),
    ("17_병원_병원검색", "screens/hospital_search_page.dart"),
    ("18_약국_약국검색", "screens/drugstore_search_page.dart"),
    ("19_이벤트_목록", "screens/event_list_page.dart"),
    ("20_공지_목록", "screens/notices_page.dart"),
    ("21_공지_상세", "screens/notice_detail_page.dart"),
    ("22_알림_목록", "screens/notifications_page.dart"),
    ("23_문의_목록", "screens/inquiry_list_page.dart"),
    ("24_문의_작성", "screens/inquiry_create_page.dart"),
    ("25_문의_상세", "screens/inquiry_detail_page.dart"),
    ("26_콘텐츠_상세", "screens/detail_page.dart"),
    ("27_설정_설정", "screens/settings_page.dart"),
    ("28_FAQ_목록", "screens/faq_page.dart"),
]


def ensure_dirs(output):
    """출력 디렉토리 생성"""
    for sub in ("01_screenshot", "02_source_html", "03_source_dart"):
        os.makedirs(os.path.join(output, sub), exist_ok=True)


def flutter_build(flutter_dir):
    """Flutter web 빌드"""
    web_dir = os.path.join(flutter_dir, "web")
    if not os.path.isdir(web_dir):
        print("[oocapture] web 플랫폼 추가 중...")
        subprocess.run(
            ["flutter", "create", ".", "--platforms", "web"],
            cwd=flutter_dir,
            check=True,
        )

    print("[oocapture] Flutter web 빌드 중...")
    result = subprocess.run(
        ["flutter", "build", "web", "--release"],
        cwd=flutter_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[oocapture] 빌드 실패:\n{result.stderr}")
        sys.exit(1)
    print("[oocapture] 빌드 완료")


def capture_tabs(output, port, width, height, scale):
    """Playwright로 메인 탭 캡처"""
    from playwright.sync_api import sync_playwright

    ss_dir = os.path.join(output, "01_screenshot")
    html_dir = os.path.join(output, "02_source_html")
    url = f"http://localhost:{port}/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        page = ctx.new_page()

        # 첫 페이지 로드
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(5)

        for x, y, name in TAB_ITEMS:
            if name != TAB_ITEMS[0][2]:  # 첫 탭이 아니면 클릭
                page.mouse.click(x, y)
                time.sleep(2)

            page.screenshot(
                path=os.path.join(ss_dir, f"{name}.png"), full_page=True
            )
            with open(
                os.path.join(html_dir, f"{name}.html"), "w", encoding="utf-8"
            ) as f:
                f.write(page.content())
            print(f"  [OK] {name}")

        browser.close()


def copy_dart_sources(flutter_dir, output):
    """Dart 소스 코드 복사"""
    dart_dir = os.path.join(output, "03_source_dart")
    lib_dir = os.path.join(flutter_dir, "lib")

    for name, rel_path in DART_SCREENS:
        src = os.path.join(lib_dir, rel_path)
        dst = os.path.join(dart_dir, f"{name}.dart")
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            print(f"  [SKIP] {name} — {rel_path} 없음")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    args = parse_args()
    ensure_dirs(args.output)

    # 1. 빌드
    if not args.skip_build:
        flutter_build(args.flutter_dir)

    # 2. Dart 소스 복사
    if not args.skip_dart_copy:
        print("\n[oocapture] Dart 소스 복사")
        copy_dart_sources(args.flutter_dir, args.output)

    # 3. 캡처
    print(f"\n[oocapture] 캡처 시작 (port={args.port})")
    capture_tabs(args.output, args.port, args.width, args.height, args.scale)

    # 4. 결과
    ss_count = len(
        [f for f in os.listdir(os.path.join(args.output, "01_screenshot")) if f.endswith(".png")]
    )
    html_count = len(
        [f for f in os.listdir(os.path.join(args.output, "02_source_html")) if f.endswith(".html")]
    )
    dart_count = len(
        [f for f in os.listdir(os.path.join(args.output, "03_source_dart")) if f.endswith(".dart")]
    )

    print(f"\n[oocapture] 완료")
    print(f"  스크린샷: {ss_count}개")
    print(f"  HTML:     {html_count}개")
    print(f"  Dart:     {dart_count}개")
    print(f"  출력 경로: {args.output}")


if __name__ == "__main__":
    main()
