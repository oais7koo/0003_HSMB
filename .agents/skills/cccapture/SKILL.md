---
name: cccapture
description: "Flutter/Web 앱 화면을 Playwright로 캡처하여 스크린샷 + HTML 저장"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

# cccapture - 앱 화면 캡처 스킬

> Flutter/Web 앱 화면을 Playwright로 캡처하여 스크린샷 + HTML 저장

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | Flutter/Web 앱을 웹 빌드 후 Playwright로 화면 캡처 (PNG + HTML 저장) |
| **하는 것** | Flutter 웹 빌드, Playwright 브라우저 실행, 스크린샷·HTML 저장 |
| **하지 않는 것** | 코드 수정(→oodev), E2E 테스트(→ootest), 앱 배포 |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 서버 자동 배포 안 함 |
| **수정 대상** | 캡처 저장 폴더 내 PNG, HTML 파일 |
| **실행 레벨** | [자동] — 빌드→실행→캡처 자동 처리 |
| **에이전트 호환** | Claude Code 권장 — Playwright MCP 서버 사용 / 다른 에이전트: Playwright 직접 실행으로 대체 |

## 문서 이력 관리
- v01 2026-04-04 — 초기 생성 — Flutter web 빌드 → Playwright 캡처

---

## 1. 개요

Flutter/Web 앱을 웹 빌드 후 Playwright로 각 화면을 캡처하여 스크린샷(PNG)과 HTML 소스를 저장한다.

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `cccapture help` | 서브명령어 목록 |
| `cccapture version` | 스킬 버전 (v01) |
| `cccapture run` | 전체 캡처 실행 (빌드 → 서버 → 캡처) |
| `cccapture run --tabs-only` | 메인 탭만 캡처 |
| `cccapture run --port N` | 서버 포트 지정 (기본: 8899) |
| `cccapture run --output DIR` | 출력 경로 지정 |
| `cccapture status` | 현재 캡처 현황 |

실행: `uv run python .claude/skills/cccapture/scripts/oocapture_run.py [args]`

## 3. 워크플로우

```
cccapture run
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

## 4. 출력 구조

```
{output}/
├── 01_screenshot/       # PNG 스크린샷 (모바일 사이즈)
├── 02_source_html/      # HTML 소스
└── 03_source_dart/      # Dart 원본 코드 (별도 복사)
```

파일명: `NO_카테고리_페이지명.{png|html|dart}` (NO는 2자리 숫자)

## 5. 옵션

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

## 6. 탭 좌표 매핑 (390px 기준)

| 탭 | X 좌표 | Y 좌표 | 이름 |
|:--:|:------:|:------:|------|
| 1 | 39 | 820 | 홈 |
| 2 | 117 | 820 | 의료(오늘) |
| 3 | 195 | 820 | 복지 |
| 4 | 273 | 820 | 일자리 |
| 5 | 351 | 820 | 전체 |

> 탭 순서/위치는 앱 버전에 따라 변경될 수 있음. `--tabs-only` 시 자동 감지 시도.

## 7. 제한사항

- Flutter web은 canvas 렌더링 → DOM 기반 요소 선택 불가, 좌표 기반 클릭 필요
- API 서버 미연결 시 콘텐츠 영역은 에러 메시지 표시
- 하위 페이지 캡처는 네비게이션 경로 정의 필요

## 8. 전제 조건

- Flutter SDK 설치
- Playwright chromium 설치 (`uv run playwright install chromium`)
- web 플랫폼 추가 (`flutter create . --platforms web`)

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|----------|------|------|:----:|
| 빌드 | task-executor | sonnet | Flutter web 빌드 | - |
| 캡처 | task-executor | sonnet | Playwright 스크린샷 | - |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

