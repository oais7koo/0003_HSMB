---
name: ooprd
description: "PRD 생성 및 정합성 검증 스킬 'ooprd', 'PRD', '요구사항', 'clarify', 'unitdev' 등의 키워드로 트리거된다"
model: opus
metadata:
  version: v10
  category: core-dev
---

> 참조: common_guide.md, oocontext.md
> 상세 가이드: .claude/skills/ooprd/references/guide.md

## 문서 이력 관리
- v10 2026-04-19 — validate/optimize → check/check --fix 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | PRD(요구사항 정의서) 생성 및 코드·문서 정합성 검증 |
| **하는 것** | d{SP}0001_prd.md 신규 생성, 현행화, PRD↔코드 정합성 검증 |
| **하지 않는 것** | 구현 계획 수립(→ooplan), 코드 구현(→oodev), 이슈 수정(→oofix) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (코드, 기존 문서) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/d{SP}0001_prd.md` |
| **실행 레벨** | [반자동] — 생성 계획 표시 → 확인 후 실행 |
| **에이전트 호환** | 범용 — Claude Code에서 Explore·task-checker 서브에이전트 자동 활용 |

## 1. 개요

PRD 생성 및 코드/문서 정합성 검증. 서브에이전트(Explore, task-checker) 병렬처리 지원.

- **컨텍스트**: --sp N 또는 oocontext N
- **출력**: 00_doc/d{SP}0001_prd.md
- **연계**: 이슈->d{SP}0004_todo.md, 개발->d{SP}0002_plan.md
- **템플릿**: .claude/skills/ooprd/templates/prd/ (프로젝트 유형별)

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooprd help` | 서브명령어 목록 표시 | 터미널 |
| `ooprd version` | 스킬 버전 정보 (v09) | 터미널 |
| `ooprd status` | 서브명령어 리스트, 상태 요약 | 터미널 |
| `ooprd check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ooprd run` | PRD 생성 실행 | 터미널 |
| `ooprd run --with-update` | PRD 생성 후 현행화 분석까지 실행 | 터미널 |
| `ooprd show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooprd add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| ooprd run | PRD 생성/정합성 검증 | d{SP}0001_prd.md |
| `ooprd update` | 현행화 — 현재 코드/현황 스캔 → PRD 문서 변경분 반영 | d{SP}0001_prd.md |
| `ooprd update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| **`ooprd run this`** | **직전 작업 관련 PRD 섹션 갱신** (→ common_guide.md §9) | d{SP}0001_prd.md |
| ooprd run --template [type] | 템플릿 지정 생성 | d{SP}0001_prd.md |
| ooprd check --fix | PRD 최적화 (구 `optimize`) | d{SP}0001_prd.md |
| ooprd template | 템플릿 목록 조회 | 터미널 |
| ooprd template [type] | 특정 템플릿 조회 | 터미널 |
| ooprd check --structure | 구조 검증 (구 `validate`) | 터미널 |
| ooprd section [N] | 특정 섹션 갱신 | d{SP}0001_prd.md |
| ooprd unitdev | 전체 단위개발문서 현행화 | d{SP}1XXX_*.md |
| ooprd unitdev [문서명] | 특정 단위개발문서 현행화 | 해당 문서 |
| ooprd clarify | PRD 모호성 해소 (최대 5개 질문) | d{SP}0001_prd.md |

## 3. 워크플로우

### 3.1 run 분기
run -> PRD 존재? -> 없음: 신규 생성 / 있음: 정합성 검증

### 3.2 신규 생성 (PRD 없음)

> **핵심 원칙**: 템플릿 Must 섹션을 기준으로 누락 정보를 파악하고, 채울 수 없는 항목은 사용자에게 1개씩 질문한다. 질문 없이 빈칸으로 생성하지 않는다.

**정보 수집 → PRD 생성 프로토콜**:

> 코드 예시: references/guide.md 참조

**템플릿 옵션**: `--template streamlit` (웹앱) | `--template algorithm` (알고리즘/ML) | `--template agent` (에이전트/CLI) | 미지정 시 common

### 3.3 정합성 검증
PRD 로드 -> 비교대상 스캔 -> 불일치 -> 리포트 -> d{SP}0004_todo.md 등록

**비교 대상**: 코드베이스, d{SP}0002_plan, d{SP}0003_test, d{SP}0005_lib, d{SP}0006_db, d{SP}0008_user

### 3.4 check --fix
PRD 로드 -> 구조/내용 검증 -> 일관성 최적화

**체크**: 템플릿 완성, 모호함 0건, MoSCoW 할당, 중복 제거

### 3.5 unitdev (단위개발문서 현행화)

앞 섹션(1. 개요)을 기준으로 뒤 섹션(2~5)을 정합성 맞춤

**섹션 연계 규칙**:

| 입력 섹션 | 출력 섹션 | 연계 규칙 |
|----------|----------|----------|
| 1.1 목적 | 2.1 기능요구사항 | 목적 달성을 위한 기능 도출 |
| 1.2 핵심가치 | 5.2 검증체크리스트 | 핵심가치별 검증항목 생성 |
| 1.3 아이템 | 2.1 기능요구사항 | 아이템별 기능 매핑 |
| 1.3.N 아이템상세 | 3.N 데이터구조 | 상세정보 -> 필드 정의 |
| 2.1 기능요구사항 | 4.2 주요함수 | 기능별 함수 매핑 |
| 2.2 시나리오 | 5.1 테스트케이스 | 시나리오별 TC 생성 |
| 2.3 UI/UX | 3.1 아키텍처 | UI 구성요소 -> 컴포넌트 |
| 3.N 데이터구조 | 4.5 DB | 필드 -> 테이블 정의 |

**워크플로우**:

> 코드 예시: references/guide.md 참조

### 3.7 ooplan Feature 분해를 위한 PRD 필수 항목

> PRD §기능요구사항이 불충분하면 `ooplan run`이 Feature를 제대로 분해할 수 없음

| PRD 섹션 | 내용 | ooplan 활용 |
|----------|------|------------|
| §기능요구사항 | MoSCoW 기능 목록 | Epic → Feature 분해 근거 |
| §기능 상세 | 기능별 입출력/시나리오 | Feature → Task 세분화 근거 |
| §기술스택 | 언어/프레임워크 요약 | 기술 설계 방향 |

### 3.6 clarify (모호성 해소)

PRD 내 불명확한 영역을 식별하고 최대 5개 질문으로 해소

**검사 영역 (Coverage Taxonomy)**:

| 영역 | 검사 항목 |
|------|----------|
| 기능 범위 | 핵심 목표, 제외 선언, 사용자 역할 |
| 도메인/데이터 | 엔티티, 관계, 상태 전이, 볼륨 |
| UX 흐름 | 핵심 여정, 에러/빈/로딩 상태, 접근성 |
| 비기능 | 성능, 확장성, 보안, 관찰성 |
| 통합 | 외부 서비스, 실패 모드, 프로토콜 |
| 엣지케이스 | 네거티브 시나리오, 충돌 해결 |

**워크플로우**:

> 코드 예시: references/guide.md 참조

## 4. 정합성 검증 항목

### 코드 vs PRD
| 검증 항목 | PRD 섹션 | 비교 대상 |
|----------|---------|----------|
| 기능 구현 | 4. 기능 요구사항 | 구현 파일/함수 |
| 기술 스택 | 5.2 기술 스택 | pyproject.toml |
| API 엔드포인트 | 5.3 API 명세 | 라우터/컨트롤러 |
| DB 스키마 | 5.4 DB 스키마 | 실제 테이블 |

### 문서 간 비교
| 검증 항목 | PRD 섹션 | 비교 문서 |
|----------|---------|----------|
| 구현 계획 | 4. 기능 요구사항 | d{SP}0002_plan.md |
| 테스트 커버리지 | 7. 테스트 전략 | d{SP}0003_test.md |
| 라이브러리 | 5.2 기술 스택 | d{SP}0005_lib.md |
| DB 구조 | 5.4 DB 스키마 | d{SP}0006_db.md |

## 5. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|---------|------|------|:----:|
| 분석 | oh-my-claudecode:explore | haiku | 코드/문서 스캔 | O |
| 요구사항 분석 | oh-my-claudecode:analyst | opus | 요구사항 명확화, 수용 기준 도출 | - |
| 검증 | task-checker | - | 정합성 검증 | - |
| PRD 품질 검토 | oh-my-claudecode:critic | opus | PRD 내용 비판적 검토 | - |
| 실행 | task-executor | - | 리포트/등록 | - |

## 6. PRD 템플릿

> 위치: .claude/skills/ooprd/templates/prd/

| 템플릿 | 유형 | 용도 |
|--------|------|------|
| common_prd_template.md | 공통 | 범용 PRD |
| streamlit_prd_template.md | Type B | Streamlit 웹 앱 |
| algorithm_prd_template.md | Type A | 알고리즘/분석 |
| agent_prd_template.md | Type C | 에이전트/CLI |

**선택 규칙**: Type A(알고리즘/연구) / Type B(Streamlit 웹) / Type C(에이전트/CLI) / 기타(common)

## 7. 검증 체크리스트

| 우선순위 | 섹션 | 검증 항목 |
|---------|------|----------|
| Must | 1,2,4,5 | 버전, 목표, 기능목록, 기술스택 |
| Should | 3,6,7 | 페르소나, 성능/보안, 테스트 |
| Could | 8~10 | 배포, 관리, 부록 |

## 8. 컴팩트 생성 원칙 (--compact)

`ooprd run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

## 9. PRD 콘텐츠 범위 규칙 (중복 방지)

> **근거**: common_guide.md §6.1.1 PRD/Plan 콘텐츠 소유권 매트릭스

PRD는 "무엇을(What)" 정의하는 문서입니다. 아래 항목은 **PRD에 기재 금지**이며, Plan(d{SP}0002)이 소유합니다:

| 금지 항목 | PRD에 허용되는 범위 | 올바른 위치 |
|----------|-------------------|-----------|
| 기술 스택 상세 테이블 | 1줄 요약 (예: "Python 3.13, FastAPI") | Plan §기술설계 |
| 폴더 구조 트리 | X (기재 금지) | Plan §기술설계 |
| DB DDL/CREATE TABLE | 테이블 목적 1줄만 (예: "추천정보 저장") | Plan §기술설계 또는 d0006_db |
| WBS/스프린트/마일스톤 | X (기재 금지) | Plan §WBS, §스프린트 |
| 구현 상태 (완료/진행중) | X (기재 금지) | Plan §진행추적 |
| 기술 리스크/일정 리스크 | X (기재 금지) | Plan §리스크 |
| 의사결정 로그 | X (기재 금지) | Plan §의사결정 |

**PRD check/check --fix 시 자동 검증**: 위 항목이 PRD에 존재하면 WARNING으로 리포트하고 Plan 이동을 권고합니다.

## 10. SP00 PRD 특수 규칙

> SP00 (`d0001_prd.md`) 생성/갱신 시 적용

| 항목 | 규칙 |
|------|------|
| 플러그인 관리 | PRD 내 플러그인 목록 **직접 기재 금지** |
| 플러그인 참조 | `d0009_env.md` 링크로 대체 (`ooenv` 관할) |
| 기술스택 플러그인 행 | `d0009_env.md 참조 (ooenv run으로 현행화)` 로 표기 |
| 이유 | 플러그인 현황은 `ooenv run`이 자동 생성 — PRD 중복 기재 시 불일치 발생 |

> **관련 명령어**: `.claude/commands/sc/design.md` | `.claude/commands/sc/document.md`

## 11. GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 신규 프로젝트 초기화 | `ooprd run` (신규) | `/gsd:new-project` |
| 신규 마일스톤 추가 | `ooprd run --template` | `/gsd:new-milestone` |
| 요구사항 모호성 해소 | `ooprd clarify` | `/gsd:discuss-phase [N]` |

**조합 패턴:**

> 코드 예시: references/guide.md 참조

> GSD는 `.planning/` 기반, oo는 `00_doc/` 기반 — 병행 사용 가능

## 12. 관련 문서

- .claude/skills/ooprd/templates/prd/: PRD 템플릿 파일
- .claude/templates/common_unit_dev_doc.md: 단위개발문서 템플릿
- d{SP}0001_prd.md: PRD
- d{SP}0002_plan.md: 계획
- d{SP}0004_todo.md: 이슈

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- QMD-REF:START -->

## QMD 마크다운 검색 (문서 내용 탐색 시)

> 마크다운 문서 **내용**을 찾을 때는 Glob/Grep 대신 **`mcp__qmd__query`** 우선 사용.
> qmd 미가동 시 Glob/Grep 폴백. 자세한 기준: `.claude/guides/common_guide.md §10`

| 도구 | 적합한 상황 |
|------|-----------|
| `mcp__qmd__query` (lex) | 키워드·문서번호·용어 검색 |
| `mcp__qmd__query` (vec) | 자연어 의미 검색 |
| `Glob` | 파일 경로 패턴 검색 |
| `Grep` | 코드·특정 문자열 검색 |

**인덱싱**: `oostart run` 시 `qmd update` 자동 실행 / 최초: `qmd collection add . --name {프로젝트명}`

<!-- QMD-REF:END -->

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

