# 플러그인: playwright

> E2E 테스트 자동화 및 브라우저 제어

## 개요

playwright 플러그인은 Playwright 브라우저 자동화 프레임워크를 Claude Code에 통합합니다. E2E 테스트 생성과 웹 UI 검증에 활용합니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `playwright` |
| 설치 여부 | ✅ 설치됨 |
| 설치 명령어 | `/plugin install playwright@claude-plugins-official` |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| E2E 테스트 생성 | 사용자 워크플로우 기반 자동 테스트 작성 |
| 크로스 브라우저 | Chrome, Firefox, Safari, Edge 지원 |
| 스크린샷 | 시각적 회귀 테스트 |
| 성능 측정 | Core Web Vitals, 로딩 시간 |
| 폼 자동화 | 입력, 클릭, 네비게이션 자동화 |

## 활성화

| 방법 | 설명 |
|------|------|
| `--play` / `--playwright` 플래그 | 명시적 활성화 |
| 자동 | `test/e2e` 키워드, QA 페르소나 활성 시 |

## 사용 예시

```bash
# 1. E2E 테스트 생성
"로그인 플로우 E2E 테스트 작성해줘 --play"

# 2. 특정 페이지 테스트
"http://localhost:8501 접속해서 버튼 동작 테스트해줘"

# 3. 스크린샷 캡처
"현재 상태 스크린샷 찍어줘"

# 4. 성능 측정
"페이지 로딩 성능 측정해줘 --play"
```

## oo 스킬 연계

| oo 스킬 | playwright 연계 |
|---------|---------------|
| `ootest run` | E2E 테스트 실행 시 활용 |
| `oostreamlit run` | Streamlit 앱 UI 테스트 |

## Streamlit 앱 테스트

```python
# playwright 기반 Streamlit 테스트 예시
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8501")
    page.click("button:has-text('실행')")
    page.screenshot(path="result.png")
    browser.close()
```

---

> 생성일: 2026-04-02 | ootutorial v01
