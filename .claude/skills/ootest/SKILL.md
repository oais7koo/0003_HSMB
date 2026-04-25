---
name: ootest
description: "통합 테스트 스킬 'ootest', '테스트', '테스트 코드 작성', '테스트 실행', 'TDD RED', '체크리스트' 등의 키워드로 트리거된다"
metadata:
  version: v09
  category: core-dev
---

> 참조: common_guide.md (에이전트) | oocontext.md (SP)
> 상세 가이드: .claude/skills/ootest/references/guide.md

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | TDD RED 단계 — TC 코드 작성 및 테스트 반복 실행 (PASS까지) |
| **하는 것** | tests/ TC 파일 생성, d{SP}0003 Part C 등록, pytest 반복 실행 |
| **하지 않는 것** | 구현 코드 작성(→oodev/GREEN), 정적 분석(→oocheck), 이슈 수정(→oofix) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `tests/TC*.py`, `d{SP}0003_test.md` Part C |
| **실행 레벨** | [자동] — TC 작성 후 pytest 반복 실행 (PASS까지) |
| **에이전트 호환** | Claude Code 권장 — `uv run pytest` 직접 실행 / 다른 에이전트: pytest 명령을 수동 실행하거나 별도 터미널에서 실행 |

## 1. 개요

TDD RED 단계 + 테스트 코드 작성 + 반복 실행 스킬. 컨텍스트: --sp N 또는 oocontext N

**문서 역할 분리:**

| 스킬 | 역할 | 문서 |
|------|------|------|
| `ootest help` | 서브명령어 목록 표시 | 터미널 |
| `ootest version` | 스킬 버전 정보 (v09) |
| oodev | d{SP}0003 생성 (INIT) | 첫 실행 시 자동 생성 |
| **ootest** | **TDD RED: TC 코드 작성** | d{SP}0003 Part C 등록 |
| **ootest** | **반복 실행 (pass까지)** | 실패 → 분석 → 재실행 루프 |
| ootest | 결과 갱신 | 테스트 실행 후 상태 업데이트 |
| ootest | Part D 재스캔 | run 실행 시 자동 선행 |
| oodev | GREEN: 최소 구현 | 테스트 통과 코드 작성 |
| oodev | REFACTOR: 품질 개선 | lint 통과 |

문서연계: 실패->d{SP}0004 | 개발->d{SP}0002 | 항목->d{SP}0003

## 2. 가이드

**통합 가이드**: .claude/skills/ootest/references/guide.md (방법론 How)

| 파트 | 내용 |
|------|------|
| 공통 | 우선순위/상태/에러분류 |
| A | 정적분석, 용어체크 |
| B | E2E/UI, Playwright |
| C | pytest, TDD |
| D | oo 모듈 전체 검증 |
| E | 런타임 검증 (import 테스트) - 필수 |

**Streamlit 프레임워크**: `pages/*.py` 존재 시 → `.claude/skills/ootest/references/streamlit_guide.md` 자동 참조

## 3. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootest status` | 서브명령어 리스트, 현재 상태 |
| `ootest check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ootest run` | 테스트 실행 | 터미널 |
| `ootest show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ootest add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| **write [ID]** | **TC 코드 생성 (TDD RED) + d{SP}0003 Part C 등록** |
| **write --all** | **미등록 TC 전체 코드 생성** |
| run | 전체 테스트 + d{SP}0003 자동 갱신 (Part D 재스캔 자동 선행) |
| **run this** | **직전 작업 파일 관련 TC 실행** (→ common_guide.md §9) |
| run --unit | Part C pytest (반복 루프 포함) + d{SP}0003 갱신 |
| run --e2e | Part B 시나리오 + d{SP}0003 갱신 |
| run --module | Part D oo 모듈 (재스캔 자동 선행) + d{SP}0003 갱신 |
| run --runtime | Part E 런타임 검증 + d{SP}0003 갱신 |
| run [ID] | 특정 TC 실행 (실패 시 자동 재시도) + d{SP}0003 갱신 |
| run [P0-P3] | 우선순위별 + d{SP}0003 갱신 |
| preview | 계획 출력 |
| checklist [domain] | 요구사항 품질 체크리스트 생성 |

옵션: --screenshot --fail-fast --verbose --max-retries N

## 4. 에이전트 매핑

| 유형 | 에이전트 | 모델 | 병렬 |
|------|----------|------|:----:|
| **TC 코드 생성 (RED)** | **test-engineer** | **sonnet** | **O** |
| Part A 정적 | python-code-reviewer | sonnet | O |
| Part A 품질 | ooqa | sonnet | O |
| Part B E2E | web-test-orchestrator | sonnet | - |
| Part C 단위 | task-executor | sonnet | - |
| Part D oo | task-executor | sonnet | - |
| Part E 런타임 | task-executor | sonnet | - |
| d0003 갱신 | task-executor | sonnet | - |

병렬: RED(test-engineer, run_in_background=true) | A(reviewer+qa) | B설계(qa+Explore, run_in_background=true)

## 5. 워크플로우

### 5.0 TDD RED (write)

**TC 코드 저장 경로**: `tests/sp{N}/TC[번호]_[모듈].py` (SP00 공통: `tests/TC[번호]_[모듈].py`)

```
ootest write [ID]
    1. d{SP}0003 시나리오 로드 (Part B)
    2. test-engineer → TC 코드 생성 (pytest/playwright)
    3. tests/sp{N}/ 폴더에 저장 (TC[번호]_[모듈].py)
    4. 실행 → 반드시 실패 확인 (pass 시 TC 재작성)
    5. d{SP}0003 Part C 등록
    6. oodev에 GREEN 신호 전달
```

> 코드 예시: references/guide.md §13.1 (폴더 구조), §14.3 (반복 루프) 참조

### 5.0.1 실행 정책

> **기본 원칙**: `ootest run`은 실서버 연결 테스트를 포함한 **모든 테스트를 실행**한다.
> - `--ignore` 없이 전체 실행이 기본값
> - 실서버 테스트(scp_real, E2E 등) 실패 시에도 나머지 테스트는 계속 실행
> - 실서버 미연결로 인한 실패는 결과 리포트에 별도 표기 (SKIP이 아닌 FAIL로 기록)
> - 특정 테스트만 제외하려면 명시적으로 `--exclude` 옵션 사용

### 5.0.2 완료 기준 (Definition of Done)

> **Part C(단위) 통과만으로는 완료가 아니다.** 단위 테스트 통과 ≠ 실제 화면 동작.
>
> | 파트 | 통과 필수 | 이유 |
> |------|:--------:|------|
> | Part C (pytest 단위) | ✅ 필수 | 로직 정확성 |
> | Part B (E2E/Playwright) | ✅ 필수 | 실제 브라우저 화면 동작 검증 |
> | Part D (모듈 연동) | ✅ 필수 | 모듈 간 통합 오류 감지 |
> | Part E (런타임 검증) | ✅ 필수 | import 오류·위젯 충돌 등 런타임 에러 감지 |
> | Part A (정적 분석) | ✅ 필수 | 코드 품질 |
> | 성능 체크리스트 | ✅ 필수 | 응답시간·부하 기준 충족 (`ootest checklist performance`) |
> | 보안 체크리스트 | ✅ 필수 | 인증·XSS·SQL인젝션 등 (`ootest checklist security`) |
>
> **E2E 미작성 시**: `ootest run` 완료 후 "Part B TC 없음 — E2E 테스트 작성 필요" 경고 출력.
> **모듈 TC 미작성 시**: "Part D TC 없음 — `ootest run --module`로 스캔 필요" 경고 출력.
> **실제 웹 동작 ≠ 단위 통과**: mock 기반 단위 테스트만으로 기능 완료 선언 금지.
>
> **조건 미충족 시 처리 원칙**: Part B/D/E 실행 전 전제 조건을 먼저 확인한다. 조건 미충족 시 건너뛰지 않고 **사용자에게 조건 갖추도록 요청 후 중단**한다. 조건을 갖춘 후 재실행해야 완료로 인정한다.

### 5.1 전체 (run)
가이드->Part D 재스캔->Part A->B->C->D->E->d{SP}0003->d{SP}0004

### 5.2 단위 (--unit)
d{SP}0003 Part C->TC매칭->pytest->실패 시 반복 루프->상태갱신

TC규칙: TC[번호]_[모듈].py

### 5.3 E2E (--e2e)

**전제 조건 확인 (실행 전 필수)**:

| 조건 | 확인 방법 | 미충족 시 |
|------|----------|----------|
| Playwright 설치 | `playwright --version` | "playwright 미설치. `uv add playwright && playwright install` 실행 후 재시도해주세요." 안내 후 중단 |
| 웹 서버 실행 중 | `localhost:{port}` 접속 가능 | "앱 서버가 실행되지 않았습니다. `streamlit run app.py` (또는 해당 실행 명령)로 서버를 먼저 실행해주세요." 안내 후 중단 |
| Part B TC 존재 | `tests/sp{N}/e2e/` 폴더 내 파일 | "E2E TC가 없습니다. `ootest write --e2e`로 먼저 TC를 작성해주세요." 안내 후 중단 |

조건 모두 충족 시: Part B->Playwright->상태갱신->스크린샷(tmp/test_screenshots/)->d{SP}0003 갱신

### 5.4 oo 모듈 (--module)

목적: oo 모듈 기능 전체 검증. 대상: oo/*.py 전체 함수

> 코드 예시: references/guide.md §6 (카테고리 목록, 테스트 패턴) 참조

### 5.5 런타임 검증 (Part E) - 필수

py_compile/pylint로 감지 불가능한 런타임 에러 검증

| 에러 유형 | 원인 | Part E 감지 |
|----------|------|:-----------:|
| StreamlitDuplicateElementKey | 위젯 key 중복 | O |
| ImportError (조건부) | if문 내 import | O |
| ImportError (동적 sys.path) | sys.path.insert 후 존재하지 않는 모듈 import | O |
| AttributeError | 런타임 객체 접근 | O |
| TypeError | 런타임 타입 불일치 | O |
| UnboundLocalError (함수 내부 import) | 함수 내 `import module` 이전에 같은 이름 사용 | △ |

> **⚠️ UnboundLocalError 한계**: 권한 체크(require_admin 등) 조기 종료로 문제 함수가 실행되지 않으면 import 테스트로 감지 불가.
> → **oocheck `함수 내부 import 스코프 오류 감지`** 룰로 AST 정적 분석 대체. `oocheck run` 선행 필수.

```bash
ootest run --runtime       # Part E만 실행
uv run pytest tests/test_page_import.py -v
```

#### Streamlit 프로젝트 Part E 자동 표준 TC

> `pages/*.py` 가 존재하는 SP에서 `ootest run --runtime` 실행 시,
> `tests/sp{N}/test_page_import.py` 가 없으면 **자동 생성** 후 실행한다.

**자동 생성 TC 내용**: 모든 `pages/*.py` 파일을 subprocess로 import 시도 → ImportError/ModuleNotFoundError를 FAIL로 기록  
**목적**: 동적 sys.path + 삭제된 모듈 조합으로 pylint가 놓친 import 오류를 런타임에서 반드시 감지

### 5.6 checklist (요구사항 품질 검증)

체크리스트는 "요구사항을 위한 유닛테스트" - 구현이 아닌 요구사항 자체의 품질 검증

**검증 차원**:

| 차원 | 검증 내용 |
|------|----------|
| 완전성 | 필요한 모든 요구사항이 문서화되었는가? |
| 명확성 | 요구사항이 구체적이고 모호하지 않은가? |
| 일관성 | 요구사항 간 충돌이 없는가? |
| 측정가능성 | 성공 기준이 객관적으로 검증 가능한가? |
| 커버리지 | 모든 흐름/케이스가 정의되었는가? |

**도메인별 체크리스트**:

| 도메인 | 파일명 | 주요 검증 항목 |
|--------|--------|---------------|
| ux | ux.md | 시각 계층, 상호작용 상태, 접근성 |
| api | api.md | 에러 응답, 인증, 버저닝 |
| performance | performance.md | 성능 지표, 부하 조건 |
| security | security.md | 인증/인가, 데이터 보호, 위협 모델 |

```bash
ootest checklist ux           # UX 요구사항 품질 체크리스트
ootest checklist api          # API 요구사항 품질 체크리스트
ootest checklist security     # 보안 요구사항 품질 체크리스트
ootest checklist              # 대화형으로 도메인 선택
```

> 코드 예시: references/guide.md §14.1 (워크플로우, 항목 형식) 참조

---

## 6. 컴팩트 생성 원칙 (--compact)

> `ootest run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

## 7. 프레임워크 레퍼런스 참조

> 테스트 작성 시, 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.claude/reference/development/{framework}/` 문서를 참조하여 테스트 구조를 맞춘다.

| 프레임워크 | 감지 조건 | 참조 경로 | 테스트 참조 항목 |
|-----------|----------|----------|----------------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | conftest fixture, TestClient, SFTP 서버, 테스트 분류 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 테스트 |

## 8. 관련문서

ootest_guide.md(통합가이드) | oodev.md(TDD) | oocheck.md(Part A) | d{SP}0003(항목) | d{SP}0004(이슈)

> **관련 명령어**: `.claude/commands/sc/test.md` | `.claude/commands/sc/analyze.md`

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

