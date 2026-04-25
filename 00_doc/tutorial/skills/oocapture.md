# oocapture Tutorial

> Flutter/Web 앱 화면을 웹 빌드 후 Playwright로 캡처하여 스크린샷 + HTML 저장 | 버전: v03 | 카테고리: meta-util

## 1. 이 스킬은 왜 필요한가?

Flutter/Web 앱의 각 화면을 자동으로 캡처하여 스크린샷(PNG)과 HTML 소스를 저장합니다. 앱 UI 문서화, 설계 시스템 검증, 프로토타입 공유 시 유용합니다.

## 2. 빠른 시작 (5분 가이드)

```bash
# 전체 캡처 실행 (빌드 → 서버 → 캡처)
oocapture run

# 메인 탭만 캡처
oocapture run --tabs-only

# 상태 확인
oocapture status

# 도움말
oocapture help
```

## 3. 자주 쓰는 명령 요약

| # | 명령어 | 언제 쓰나 |
|---|--------|----------|
| 1 | `oocapture run` | 전체 화면 캡처 (빌드~캡처 전체) |
| 2 | `oocapture status` | 캡처 현황 확인 |
| 3 | `oocapture run --tabs-only` | 메인 탭만 빠르게 캡처 |
| 4 | `oocapture run --port 8899` | 커스텀 포트 지정 |

## 4. 권장 흐름 (이렇게 쓰세요)

```
[1] 앱 코드 수정 → [2] oocapture run → [3] 스크린샷 확인 → [4] 문서 업데이트
```

**단계별 설명:**
1. Flutter 앱 코드를 수정하고 저장
2. `oocapture run`으로 최신 화면 캡처 (웹 빌드 자동 포함)
3. `data/11_app_front/01_screenshot/` 폴더에서 스크린샷 확인
4. 필요시 설계 문서나 UI 가이드 업데이트

## 5. 전체 명령어

| 명령어 | 설명 |
|--------|------|
| `oocapture help` | 서브명령어 목록 표시 |
| `oocapture version` | 스킬 버전 정보 (v01) |
| `oocapture status` | 캡처 현황 조회 |
| `oocapture run` | 전체 캡처 실행 |
| `oocapture run --tabs-only` | 메인 탭만 캡처 |
| `oocapture run --port N` | 포트 지정 |
| `oocapture run --output DIR` | 출력 폴더 변경 |

## 6. 상세 사용법

### 핵심 기능

**웹 빌드 + 로컬 서버 + Playwright 캡처:**
- Flutter web 빌드 자동 실행
- 로컬 HTTP 서버로 `build/web` 서빙
- Playwright로 각 화면 스크린샷 + HTML 저장

**모바일 뷰포트 에뮬레이션:**
- 기본: 390x844 (모바일 표준)
- 2배 디바이스 배율 적용
- 탭 네비게이션은 좌표 기반 클릭

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--output DIR` | 출력 경로 | `data/11_app_front` |
| `--port N` | 로컬 서버 포트 | 8899 |
| `--width N` | 뷰포트 너비 | 390 |
| `--height N` | 뷰포트 높이 | 844 |
| `--scale N` | 디바이스 스케일 | 2 |
| `--tabs-only` | 메인 탭만 캡처 | false |
| `--with-api` | API 서버 연동 (콘텐츠 포함) | false |
| `--flutter-dir DIR` | Flutter 프로젝트 경로 | `08_flutterApp` |

### 탭 좌표 매핑 (390px 기준)

| 탭 | X 좌표 | Y 좌표 | 이름 |
|:--:|:------:|:------:|------|
| 1 | 39 | 820 | 홈 |
| 2 | 117 | 820 | 의료(오늘) |
| 3 | 195 | 820 | 복지 |
| 4 | 273 | 820 | 일자리 |
| 5 | 351 | 820 | 전체 |

> 탭 순서/위치는 앱 버전에 따라 변경될 수 있음. `--tabs-only` 시 자동 감지 시도.

### 제한사항

- Flutter web은 canvas 렌더링 → DOM 기반 요소 선택 불가, 좌표 기반 클릭 필요
- API 서버 미연결 시 콘텐츠 영역은 에러 메시지 표시
- 하위 페이지 캡처는 네비게이션 경로 정의 필요

### 전제 조건

- Flutter SDK 설치
- Playwright chromium 설치 (`uv run playwright install chromium`)
- web 플랫폼 추가 (`flutter create . --platforms web`)

## 5. 워크플로우

```
oocapture run
    │
    ▼
[1] Flutter web 빌드 (flutter build web)
    │ - web 플랫폼 없으면 자동 추가
    │
    ▼
[2] 로컬 HTTP 서버 시작 (python -m http.server)
    │ - build/web 디렉토리 서빙
    │
    ▼
[3] Playwright 캡처
    │ - 모바일 뷰포트 (390x844, 2x)
    │ - 탭 네비게이션: 좌표 기반 클릭
    │ - 하위 페이지: 메뉴 항목 클릭
    │
    ▼
[4] 저장
    │ - 스크린샷: {output}/01_screenshot/NO_카테고리_페이지명.png
    │ - HTML:     {output}/02_source_html/NO_카테고리_페이지명.html
    │
    ▼
[5] 서버 종료 + 결과 리포트
```

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oocapture run
```

### 서브명령어 활용
```bash
oocapture run  # 전체 캡처 실행 (빌드 → 서버 → 캡처)
```

### 옵션
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--output DIR` | 출력 경로 | `data/11_app_front` |
| `--port N` | 로컬 서버 포트 | 8899 |
| `--width N` | 뷰포트 너비 | 390 |
| `--height N` | 뷰포트 높이 | 844 |
| `--scale N` | 디바이스 스케일 | 2 |
| `--tabs-only` | 메인 탭만 캡처 | false |
| `--with-api` | API 서버 연동 (콘텐츠 포함) | false |
| `--flutter-dir DIR` | Flutter 프로젝트 경로 | `08_flutterApp` |

### 스크립트 직접 실행
```bash
uv run python .claude/skills/oocapture/scripts/oocapture_run.py
```

## 7. 입출력

```
{output}/
├── 01_screenshot/       # PNG 스크린샷 (모바일 사이즈)
├── 02_source_html/      # HTML 소스
└── 03_source_dart/      # Dart 원본 코드 (별도 복사)
```

파일명: `NO_카테고리_페이지명.{png|html|dart}` (NO는 2자리 숫자)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|----------|------|------|:----:|
| 빌드 | task-executor | sonnet | Flutter web 빌드 | - |
| 캡처 | task-executor | sonnet | Playwright 스크린샷 | - |

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
