---
name: ooplan
description: "구현 계획 및 상세 설계 스킬 'ooplan', '구현 계획', '설계', 'plan' 등의 키워드로 트리거된다"
model: opus
metadata:
  version: v07
  category: core-dev
---

> 공통 원칙: .claude/guides/common_guide.md 참조
> 상세 가이드: .claude/skills/ooplan/references/guide.md

## 문서 이력 관리
- v07 2026-04-19 — optimize → check --fix 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | PRD 기반 구현 계획(Epic/Feature/Task) 수립 |
| **하는 것** | d{SP}0002_plan.md 생성/갱신, 아키텍처·API·DB·워크플로우 설계 |
| **하지 않는 것** | PRD 작성(→ooprd), 코드 구현(→oodev), 이슈 수정(→oofix) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (PRD, 코드 구조) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/d{SP}0002_plan.md` |
| **실행 레벨** | [반자동] — 계획 구조 확인 후 실행 |
| **에이전트 호환** | 범용 — Claude Code에서 Explore·task-executor 서브에이전트 자동 활용 |

## 1. 개요

**역할**: Architect - PRD 기반 계획 수립 및 설계
**컨텍스트**: --sp N 또는 oocontext N
**문서 역할**: 개발->d{SP}0002_plan.md / 에러->d{SP}0004_todo.md

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooplan help` | 서브명령어 목록 표시 | 터미널 |
| `ooplan version` | 스킬 버전 정보 (v06) | 터미널 |
| `ooplan status` | 서브명령어 리스트, 현재 상태 | 터미널 |
| `ooplan check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ooplan run` | 구현 계획 생성 실행 | 터미널 |
| `ooplan show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooplan add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| run | PRD -> Task까지 완전 생성 (run task와 동일) | d{SP}0002_plan.md |
| **run this** | **직전 작업 관련 계획 업데이트** (→ common_guide.md §9) | d{SP}0002_plan.md |
| run epic | PRD -> Epic까지 생성 | d{SP}0002_plan.md |
| run feature | PRD -> Feature까지 생성 | d{SP}0002_plan.md |
| run task | PRD -> Task까지 생성 (기본값) | d{SP}0002_plan.md |
| detail | 실행 전 상세 설계 (->oodev) | 실행 큐 |
| check --fix | 현재 Plan 검토 및 개선 (구 `optimize`) | d{SP}0002_plan.md |
| sync | PRD 변경사항 동기화 | d{SP}0002_plan.md |
| design [대상] | 시스템/API/컴포넌트/DB 아키텍처 설계 (design 흡수) | 설계 문서 |
| workflow [prd] | PRD→워크플로우 생성, 페르소나/전략/리스크 (workflow 흡수) | 로드맵/태스크 |

design 옵션: `--type architecture\|api\|component\|database`, `--format diagram\|spec\|code`, `--iterative`
workflow 옵션: `--persona architect\|frontend\|backend\|security`, `--strategy systematic\|agile\|mvp`, `--output roadmap\|tasks\|detailed`, `--estimate`, `--risks`, `--parallel`

## 3. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|---------|------|------|:----:|
| 분석 | oh-my-claudecode:explore | haiku | 코드베이스/기술 스택 스캔 | O |
| 계획 수립 | oh-my-claudecode:planner | opus | Epic-Feature-Task 분해, 실행 계획, 리스크 파악 | - |
| 아키텍처 설계 | oh-my-claudecode:architect | opus | 시스템 설계, 인터페이스, 기술적 트레이드오프 | - |
| 계획 검토 | oh-my-claudecode:critic | opus | 계획 비판적 검토 및 개선 | - |
| 문서화 | task-executor | - | d{SP}0002_plan.md 작성 | - |
| 검증 | task-checker | - | 완성도/품질 검증 | - |

## 4. Plan 템플릿 목차

> 템플릿: `.claude/skills/ooplan/templates/plan_template.md`

1. 문서관리 -> 2. 구현개요 -> 3. WBS(Epic/Feature) -> 4. 스프린트 -> 5. 기술설계 -> 6. 리스크 -> 7. 의사결정 -> 8. 진행추적

## 5. 워크플로우

### 5.1 run

> **핵심 원칙**: PRD에서 Plan 생성에 필요한 정보를 먼저 파악하고, 부족한 항목은 사용자에게 1개씩 질문한다. 정보 부족 상태로 Plan을 생성하지 않는다.

**정보 수집 → Plan 생성 프로토콜**:

> 코드 예시: references/guide.md 참조

> **완료 후 권장**: `oofeature needed` 실행 — plan.md Feature vs 상세 문서 교차 비교로 미착수 Feature 확인 (gate check)

**PRD 필요 조건** (웹 개발 프로젝트):

| 옵션 | PRD 필요 섹션 | 근거 |
|------|-------------|------|
| run epic | 페이지 개요 (5.1) | 대분류 기반 Epic 도출 |
| run feature | 페이지 상세 (5.2) | 페이지별 기능 정의 필요 |
| run task | 페이지 상세 (5.2) + 상세기획 | 구현 단위 분해 |

**진행 컬럼 필터링**: PRD 5.1 페이지 개요의 진행=아니오인 페이지는 Plan 생성 시 자동 제외

**하위 레벨 처리**:

| 옵션 | 범위 | 기존 하위 레벨 |
|------|------|--------------|
| run epic | Epic까지 | Feature/Task 삭제 |
| run feature | Feature까지 | Task 삭제 |
| run task (기본) | Task까지 | 전체 업데이트 |

### 5.2 detail
입력 분석 -> 태스크 구체화 -> 실행 계획 -> 사용자 승인

### 5.3 check --fix
Plan 로드 -> PRD 정합성 -> 구조/일정 최적화 -> 리스크 검토 -> 업데이트

**체크**: PRD 커버리지 100% / 순환 의존성 없음 / 크리티컬 패스 최소화 / 스프린트 균형

### 5.4 sync
PRD 버전 확인 -> 변경 분석 -> Plan 업데이트

## 6. PRD -> Plan 매핑

### 6.1 계층 매핑
PRD 비전->목표요약 / 기능->Epic / 아키텍처->결정사항 / 마일스톤->스프린트 / 리스크->상세화

### 6.2 분해 체계

> 코드 예시: references/guide.md 참조

| 레벨 | 기준 | 예시 |
|------|------|------|
| Epic | 도메인/비즈니스 | 정책정보, 인증 |
| Feature | 사용자 기능 | 중앙정부 정책 |
| Task | 구현 단위 | 보건복지부 탭 |

**PRD 필요 섹션** (Feature 분해 근거):

| PRD 섹션 | ooplan 활용 |
|----------|------------|
| §기능요구사항 (MoSCoW 목록) | Epic → Feature 분해 근거 |
| §기능 상세 (입출력/시나리오) | Feature → Task 세분화 근거 |
| §기술스택 (언어/프레임워크) | 기술 설계 방향 |

## 7. Streamlit 프레임워크 (자동 감지)

**감지 조건**: `pages/*.py` 존재 | `import streamlit` 검출 | `run.bat`에 streamlit 포함
**감지 시**: `.claude/skills/ooplan/references/streamlit_guide.md` 자동 참조

**3계층**: PRD(What) -> Plan(Where) -> 개발서 d{SP}1XXX_페이지명_단위개발.md(How)
**명명**: `d{서브프로젝트번호}{4자리순번}_{페이지명}_단위개발.md`

> 설계 패턴(레이아웃/컴포넌트/DB): `streamlit_guide.md` 참조

## 8. 상세 문서 현황 (plan.md 8.2절)

### 8.1 자동 스캔 규칙

`ooplan sync` 또는 `ooplan run` 실행 시 현재 SP의 `00_doc/sp{N}/` 하위를 스캔하여 **파일명에 상세 단계가 포함된 문서**를 자동 탐색 → plan.md 8.2절 갱신.

**스캔 패턴**: `*_상세기획_*.md | *_상세설계_*.md | *_상세개발_*.md | *_상세검증_*.md`

**단계 감지**: 파일명에서 `_상세기획_` / `_상세설계_` / `_상세개발_` / `_상세검증_` 키워드로 현재 단계 판별.

### 8.2 plan.md 8.2절 형식

> 코드 예시: references/guide.md 참조

**단계 아이콘**: `⚪기획 → 🔵설계 → 🟡개발 → 🟢검증 → ✅완료`

### 8.3 연동 스킬

- **oofeature**: 상세 문서 생성/단계 전환/현황 조회
- **oodev run dXXXX**: 상세 문서 기반 개발 실행

## 9. 도구 연동

**oodev**: ooplan detail -> 상세 설계 -> oodev -> TDD 사이클

**Task Master**: Epic->Task / Feature->Subtask / 스프린트->태그 / 의존성->dependencies

## 9. 딥러닝 프로젝트 실험 결과 표기

### 실험 매트릭스 형식

> 코드 예시: references/guide.md 참조

### 필수 컬럼

| 컬럼 | 설명 |
|------|------|
| # | 실험 순번 |
| 실험 ID | 스크립트 파일명 (버전 제외) |
| 변경 사항 | 베이스라인 대비 변경점 |
| 하이퍼파라미터 | 주요 변경 파라미터들 |
| 상태 | 완료, 진행중, 실패 |
| 주요 메트릭 | 검증용 핵심 지표 |

### 종합 비교표 형식

> 코드 예시: references/guide.md 참조

### 메트릭 검증 원칙

1. **원본 데이터 기준**: 체크포인트 파일명, 로그, 또는 결과 CSV에서 추출
2. **검증 스크립트 활용**: tmp/extract_metrics.py 등으로 자동 검증
3. **불일치 시 원본 우선**: 문서와 실제 데이터 불일치 시 원본 데이터로 수정
4. **무효 실험 제외**: 학습 중단, 결과 파일 없음 등은 표에서 제외

### 상태 표기

| 상태 | 의미 | 조건 |
|------|------|------|
| 완료 | 학습+테스트 완료 | 체크포인트 + Excel + CSV 존재 |
| 진행중 | 학습 진행 중 | 체크포인트만 존재 |
| 실패 | 학습 중단/오류 | 불완전한 결과 |
| 대기 | 실험 예정 | 스크립트만 존재 |

## 10. Plan 콘텐츠 범위 규칙 (중복 방지)

> **근거**: common_guide.md §6.1.1 PRD/Plan 콘텐츠 소유권 매트릭스

Plan은 "어떻게(How)/언제(When)" 구현할지 정의하는 문서입니다. **PRD 내용을 복사하지 않습니다.**

**Plan이 소유하는 항목** (Plan에만 상세 기재):
- 기술 스택 상세 (버전, 라이브러리, 도구)
- 폴더 구조 트리
- DB DDL/스키마 설계
- WBS, 스프린트, 마일스톤
- 기술/일정 리스크
- 의사결정 로그

**Plan에서 금지하는 항목** (PRD 참조로 대체):
| 금지 항목 | 올바른 처리 |
|----------|-----------|
| 목적/범위 반복 서술 | `> PRD d{SP}0001 §2 참조` 1줄로 대체 |
| 기능 요구사항 목록 복사 | PRD §기능목록 참조 링크만 |
| UI/UX 요구사항 | PRD §UI/UX 참조 |
| 비기능 요구사항 | PRD §비기능 참조 |
| 사용자 스토리/페르소나 | PRD §사용자 참조 |

**Plan 구현개요 §1 작성 규칙**:
- §1.1 목적: PRD 참조 1줄 + Plan 고유 목적(구현 관점) 1~2줄
- §1.2 범위: PRD 참조 1줄 + 이번 스프린트 구현 범위만 명시

## 11. 컴팩트 생성 원칙 (--compact)

`ooplan run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

## 12. GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 페이즈 계획 생성 | `ooplan run` | `/gsd:plan-phase [N]` |
| 연구 포함 계획 | `ooplan run` + 수동 리서치 | `/gsd:plan-phase [N] --research` |
| 페이즈 요구사항 논의 | `ooprd clarify` | `/gsd:discuss-phase [N]` |
| 계획 Gap 보완 | `ooplan check --fix` | `/gsd:plan-milestone-gaps` |

**차이점:**
- `ooplan run` → `d{SP}0002_plan.md` 생성, OAIS SP 문서 체계 유지
- `/gsd:plan-phase` → `.planning/phases/N/PLAN.md` 생성, gsd-planner 에이전트 + 자동 검증 루프

**조합 패턴:**

> 코드 예시: references/guide.md 참조

## 13. 프레임워크 레퍼런스 참조

> 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.claude/reference/development/{framework}/` 문서를 사전 로드하여 계획 수립에 반영한다.

| 프레임워크 | 감지 조건 | 참조 경로 | 계획 반영 항목 |
|-----------|----------|----------|--------------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | 디렉토리 구조, 설정 패턴, 배치 엔진, 에러 핸들링 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 구조, UI 패턴 |

## 14. 관련 문서

- 00_doc/d{SP}0001_prd.md: PRD (입력)
- 00_doc/d{SP}0002_plan.md: 구현 계획 (출력)
- .claude/skills/oodev/SKILL.md: TDD 개발 스킬

> **관련 명령어**: `.claude/commands/sc/task.md` | `.claude/commands/sc/estimate.md`

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

