---
name: cccheck
description: "참조: .claude/guides/common_guide.md, .claude/guides/debugging_guide.md, .claude/skills/oocontext/SKILL.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

> 참조: .claude/guides/common_guide.md, .claude/guides/debugging_guide.md, .claude/skills/oocontext/SKILL.md
> 결과: 에러 -> d0004 AND d{SP}0004 | 개발 -> d{SP}0002_plan.md | 이력 -> d{SP}0010_history.md
> 상세 가이드: .claude/skills/cccheck/references/guide.md

**옵션**: --sp N (서브프로젝트) | **에이전트**: code-error-checker, python-code-reviewer, ooqa

> ⚠️ **필수**: 체크/debug 명령 시 반드시 Agent 도구로
> explore(haiku) 스캔 → quality-reviewer(opus) 분석 → debugger(opus) 심층 디버깅 순서로 위임할 것.
> 직접 처리 금지.

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 코드 정적 분석 및 품질 체크 (Python/Flutter 자동 감지) |
| **하는 것** | py_compile→pylint→mypy→pytest 검증 체인 실행, 이슈 d{SP}0004 등록 |
| **하지 않는 것** | 이슈 수정(→oofix), 설계 검토(→ooreview), 실행 테스트(→ootest) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (src/, oo/, tests/, lib/) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `d{SP}0004_todo.md` (이슈 등록만, 코드 수정 안 함) |
| **실행 레벨** | [자동] — 스캔→분석→등록 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 기반 도구 체인 자동 실행 / 다른 에이전트: pylint·mypy·pytest를 수동 실행 후 결과를 d{SP}0004에 직접 기록 |

## 문서 이력 관리
- v07 2026-04-23 — Streamlit API 오용 감지 섹션 추가 — E2E 렌더링(Playwright) 필수 명시, 검증 체인 업데이트
- v06 2026-04-23 — 함수 내부 import 스코프 오류 감지 룰 추가 — UnboundLocalError 위험 AST 분석으로 감지
- v05 2026-04-07 — dXXXX 단계 감지 + 자동전환 — 개발→검증 자동전환, 기획/설계 차단, 결과 저장 명시
- v04 2026-04-07 — cccheck run dXXXX 추가 — 상세 문서 기반 관련 코드만 체크
- v02 2026-03-29 — Flutter/Dart 지원 추가 — 프로젝트 자동 감지, dart analyze 연동, Dart 체크 워크플로우
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `cccheck help` | 서브명령어 목록 표시 |
| `cccheck version` | 스킬 버전 정보 (v02) |
| `cccheck status` | 서브명령어 리스트, 체크 대상 현황, 최근 이슈 |
| `cccheck check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `cccheck run` | 코드 품질 분석 실행 (배치 실행) |
| `cccheck update` | d0004_todo.md / d0010_history.md 정리 및 동기화 (현행화) |
| `cccheck show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `cccheck add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| **`cccheck run dXXXX`** | **상세 문서 기반 관련 코드만 체크 (oofeature 연동)** |
| **`cccheck run this`** | **직전 작업 파일만 체크** (→ common_guide.md §9) |
| cccheck / cccheck [대상] | 전체 또는 특정 대상 체크 |
| cccheck oo / error / term | oo모듈 / 에러 / 표준용어 체크 |
| cccheck debug [에러] | 심층 디버깅 (troubleshoot 흡수) |
| cccheck debug --trace | 실행 추적 활성화 |
| cccheck debug --fix | 디버깅 후 자동 수정 시도 |
| cccheck circular [모듈] | 순환 참조 감지 |

## 체크 대상

**다중 언어 지원**: 프로젝트 유형 자동 감지 (pubspec.yaml → Flutter, pyproject.toml → Python)

### Python 프로젝트
**포함**: src/, oo/, tests/, 04_app/, 루트 *.py | **제외**: data/, tmp/, db/, .git/, __pycache__/, node_modules/

### Flutter/Dart 프로젝트
**포함**: lib/, test/ | **제외**: build/, .dart_tool/, *.g.dart, *.freezed.dart, firebase_options.dart

## 워크플로우

### cccheck run dXXXX (상세 문서 기반 체크)

> oofeature 상세개발 또는 상세검증 단계에서 해당 기능 코드만 집중 체크할 때 사용.
> **자동 단계전환**: 상세개발 단계 → 상세검증으로 자동 전환 후 실행.

> 코드 예시: references/guide.md §2.7 참조

- **병렬 실행**: Task 도구 run_in_background=true
- **프로젝트 감지**: pubspec.yaml → Flutter/Dart | pyproject.toml → Python
- **분류**: [CRITICAL] 즉시 | [ERROR] 24h | [WARNING] 1주 | [INFO] 백로그

### Python 검증 체인
py_compile [필수] -> import 가용성 -> AST 스캔(check_inner_imports.py) -> pylint && mypy -> pytest -> **이슈 → d{SP}0004_todo.md 등록**

**Streamlit pages 포함 시 추가**: E2E 렌더링 (`uv run pytest tests/sp02/e2e/ -v`) — 서버 실행 필요

### Flutter/Dart 검증 체인
dart analyze [필수] -> dart fix --dry-run (자동수정 가능 건수) -> flutter test -> **이슈 → d{SP}0004_todo.md 등록**

## 결과 기록

d{SP}0004_todo.md: | ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
태그: [CRITICAL] 심각 | [ERROR] 에러 | [WARNING] 경고 | [INFO] 정보 | [SECURITY] 보안

### 병행 등록 규칙 (SP!=00)

SP!=00일 때 에러를 d0004 AND d{SP}0004 양쪽에 등록

> 코드 예시: references/guide.md §3.2 참조

## 표준용어 검증

용어집: .claude/skills/cccheck/templates/oocheck_standard_word.md

## oo 모듈 검증

올바른: oo.date_utils.get_date_range() / 잘못된: oo.get_date_range()

## 순환 참조 감지

[CRITICAL] __init__.py 포함 | [ERROR] 직접순환 (A<->B) | [WARNING] 간접순환 (A->B->C->A)
해결: 함수 내부 import, TYPE_CHECKING 활용

## Import 가용성 체크

각 `.py` 파일의 import 문을 파싱 후 uv 환경에서 실제 가용 여부 확인.

> 코드 예시: references/guide.md §2.8 참조

**분류**: [ERROR] ModuleNotFoundError - 미설치 모듈 import
**주의**: `pythoncom`, `win32api` 등 Windows 전용 모듈은 [WARNING] 플랫폼 의존성으로 추가 분류

### 동적 sys.path 파일 별도 실행 검증

> pylint는 `sys.path.insert/append` 호출을 실행하지 않으므로 그 이후의 import를 정적으로 검증할 수 없다.
> 이 경우 pylint E0401이 누락될 수 있으므로 **subprocess 실행 검증을 추가 적용**한다.

**감지 조건**: 파일 내 `sys.path.insert` 또는 `sys.path.append` 패턴 존재  
**추가 검증**: `uv run python -c "import <파일>" 또는 subprocess로 해당 파일 import 시도`  
**분류**: [ERROR] ImportError/ModuleNotFoundError 발생 시  
**적용 대상**: Streamlit pages/*.py, scripts/, 루트 *.py 중 동적 경로 주입 파일

### 함수 내부 import 스코프 오류 감지

> Python은 함수 스코프 전체를 컴파일 타임에 스캔하여 `import [module]`이 있으면 `[module]`을 로컬 변수로 취급한다.
> import 구문보다 위에서 같은 이름을 사용하면 런타임에 `UnboundLocalError`가 발생한다.
> import 테스트(importlib)는 권한 체크 등 조기 종료로 인해 이 오류를 감지하지 못할 수 있다.

**감지 조건**: 함수/메서드 내부(들여쓰기 있음)에 `import [module]` 또는 `import [module].[sub]` 패턴 존재  
**추가 검증**: 해당 함수 내에서 import 구문 이전 라인에 `[module].*` 사용 여부 AST로 확인  
**분류**: [ERROR] UnboundLocalError 위험 — import를 파일 상단으로 이동 권장  
**적용 대상**: 모든 `.py` 파일 (특히 Streamlit pages/*.py)  
**예외**: docstring·멀티라인 문자열·주석 내부의 import는 제외

### Streamlit API 오용 감지 (E2E 렌더링 필수)

> pylint/mypy는 서드파티 라이브러리(Streamlit) 함수의 파라미터명을 검증하지 못한다.
> `st.data_editor(column_options=...)` 같은 잘못된 파라미터는 실제 렌더링 시에만 TypeError로 드러난다.
> import 테스트(test_page_import.py)는 권한 체크 조기 종료로 렌더링 경로에 미도달 → E2E 필수.

**감지 조건**: `pages/*.py` 파일에서 `st.*` API 호출 존재  
**검증 방법**: Playwright E2E — `[data-testid="stException"]` 감지  
**분류**: [ERROR] TypeError/AttributeError 발생 시 → 즉시 수정  
**실행**: `uv run pytest tests/sp02/e2e/ -v` (서버 실행 필요: `run02_poc_dev.bat`)  
**한계**: 정적 분석 불가 — 브라우저 렌더링만 감지 가능

## 디버깅 (cccheck debug)

**체크포인트**: 에러라인 주변, 변수타입, 입력유효성, DB결과, NULL처리, 라이브러리버전
**Streamlit**: session_state 키, 위젯 key 중복, st.rerun() 무한루프
**프로세스**: 원인파악 -> 최소변경 -> 영향분석 -> 수정 -> 테스트

## GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 코드 품질 체크 | `cccheck run` | - |
| 페이즈 완료 검증 | `cccheck run` | `/gsd:validate-phase [N]` |
| 작업 완료 확인 | `cccheck run` | `/gsd:verify-work` |
| 디버깅 | `cccheck debug` | `/gsd:debug` |
| 전체 건강 상태 | `ooenv run` | `/gsd:health` |
| 법의학적 버그 추적 | `cccheck debug --trace` | `/gsd:forensics` |

**조합 패턴:** `oodev run` → `cccheck run` → `/gsd:verify-work`

> 코드 예시: references/guide.md §5.5 참조

## 프레임워크 레퍼런스 참조

> 코드 품질 체크 시, 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.claude/reference/development/{framework}/` 문서를 참조하여 표준 패턴 준수 여부를 검증한다.

| 프레임워크 | 감지 조건 | 참조 경로 | 체크 항목 |
|-----------|----------|----------|---------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | 에러 핸들링 계층, 디렉토리 구조, 설정 패턴 준수 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 구조, UI 패턴 |

## 관련 명령어

| 명령어 | 용도 |
|--------|------|
| .claude/skills/ootest/SKILL.md | 테스트 실행 |

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 코드 탐색 | `Explore` | haiku | O |
| 에러 검사 | `code-error-checker` | opus | O |
| 품질 분석 | `ooqa` | opus | O |
| 결과 검증 | `task-checker` | opus | - |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.claude/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |
| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |
| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |
| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |

**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.

<!-- KARPATHY-REF:END -->

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

