---
name: ccref
description: "`.codex/reference/development/` 레퍼런스 기반 기술스펙 적용 체크 | ref: `.codex/reference/development/README.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# ccref - 프레임워크 레퍼런스 관리

> `.codex/reference/development/` 레퍼런스 기반 기술스펙 적용 체크 | ref: `.codex/reference/development/README.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 프레임워크 레퍼런스 목록 조회 + 현재 프로젝트 적용 여부 체크 |
| **하는 것** | 레퍼런스 목록 표시, 프레임워크 자동 감지, 구조/패턴 체크, 문제점 리스트업 |
| **하지 않는 것** | 코드 수정(→ccfix), 레퍼런스 문서 작성, 동기화(→ccsync) |
| **참조 범위** | `.codex/reference/development/` 폴더 전체 |
| **수정 대상** | 읽기 전용 (체크 결과만 출력) |
| **실행 레벨** | [반자동] — 프로젝트 경로 자동 감지 후 체크 |
| **에이전트 호환** | 범용 — 스크립트 실행 중심 |

## 문서 이력 관리
- v01 2026-04-11 — 초기 작성

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ccref help` | 서브명령어 목록 표시 |
| `ccref version` | 스킬 버전 정보 (v01) |
| `ccref list` | 사용 가능한 프레임워크 레퍼런스 목록 |
| `ccref check` | references/checklist.md 기반으로 ccref 스킬 자체 기능 검증 |
| `ccref add checklist "항목"` | checklist.md에 새 항목 추가 |
| `ccref run` | 현재 프로젝트 기술스펙 감지 + 레퍼런스 기준 체크 |
| `ccref run [path]` | 특정 프로젝트 경로 체크 |
| `ccref run [framework]` | 특정 프레임워크 강제 지정 후 체크 |

실행: `uv run python .agents/skills/ccref/scripts/ooref_run.py [subcommand] [args]`

---

## 워크플로우

**`ccref list`** → `README.md` 파싱 → 프레임워크 목록 + 감지 규칙 출력

**`ccref run`**:
1. 프로젝트 경로 결정 (기본: 현재 디렉토리)
2. 프레임워크 자동 감지 (`pyproject.toml`, `requirements.txt`, `main.py` import 패턴)
3. 해당 레퍼런스 폴더 로드 (`.codex/reference/development/{framework}/`)
4. 체크 실행:
   - 디렉토리 구조 (`01_directory_structure.md` 기준)
   - 파일 크기 (권장 한도 초과 여부)
   - 코드 패턴 (`lifespan`, rate limiting, 예외 핸들러)
   - 설정 파일 분리 여부
   - 테스트 구조 (`conftest.py`, `test_*.py`)
5. 문제점 CRITICAL/ERROR/WARNING/INFO 수준으로 리스트업

---

## 레퍼런스 구조

```
.codex/reference/development/
├── README.md                   # 프레임워크 목록 + 감지 규칙
└── fast-api/                   # FastAPI 레퍼런스 (13개 문서)
    ├── 00_overview.md
    ├── 01_directory_structure.md
    ├── 02_config_pattern.md
    ├── 03_main_app.md
    ├── 04_routers.md
    ├── 05_models_schemas.md
    ├── 06_batch_engine.md
    ├── 07_error_handling.md
    ├── 08_testing.md
    ├── 09_admin_dashboard.md
    ├── 10_external_integration.md
    ├── 11_menu_structure.md
    └── 12_dashboard_data.md
```

---

## 프레임워크 지원 현황

| 프레임워크 | 자동 감지 | 체크 구현 | 감지 조건 |
|-----------|----------|----------|----------|
| FastAPI | O | O | `pyproject.toml`/`requirements.txt`에 `fastapi` 또는 `main.py`에 `from fastapi import` |
| Django | O | - | `manage.py` + `settings.py` 존재 |
| Streamlit | O | - | `import streamlit` 패턴 |

---

## 출력 수준

| 수준 | 의미 | 대응 |
|------|------|------|
| CRITICAL | 즉시 수정 필요 (앱 동작 불가) | 즉시 |
| ERROR | 레퍼런스 패턴 미적용 (기능 누락) | 24시간 내 |
| WARNING | 권장 패턴 미적용 | 검토 후 적용 |
| INFO | 선택적 개선 사항 | 백로그 |

---

## 관련 스킬

`ccsync` (레퍼런스 동기화) | `cccheck` (코드 체크) | `ccdev` (개발) | `ccfix` (이슈 수정)

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 레퍼런스 탐색 | `Explore` | haiku | O |
| 적용 체크 | `task-executor` | sonnet | - |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

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
| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.agents/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

