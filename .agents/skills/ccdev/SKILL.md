---
name: ccdev
description: "공통 가이드: .codex/guides/common_guide.md | 컨텍스트: .agents/skills/cccontext/SKILL.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

> 공통 가이드: .codex/guides/common_guide.md | 컨텍스트: .agents/skills/cccontext/SKILL.md
> 상세 가이드: .agents/skills/ccdev/references/guide.md

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | TDD GREEN 단계 구현 — 테스트 통과하는 최소 코드 작성 + REFACTOR |
| **하는 것** | d{SP}0003_test.md 초기 생성(INIT), GREEN 구현, REFACTOR |
| **하지 않는 것** | TC 코드 작성(→cctest/RED), 정적 분석(→cccheck), 이슈 등록(→cccheck) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (plan.md, test.md, 코드) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | 구현 코드 파일, `d{SP}0003_test.md` |
| **실행 레벨** | [자동] — explore→executor→reviewer 서브에이전트 순서 자동 위임 |
| **에이전트 호환** | Codex 권장 — Agent 도구 필수 / 다른 에이전트: 서브에이전트 위임 단계를 수동으로 실행 |

## 문서 이력 관리
- v09 2026-04-19 — optimize → check --fix 통합
- v08 2026-04-07 — dXXXX 단계 감지 + 자동전환 — 설계단계 자동전환, 기획단계 차단, TC(RED) 통합
- v03 2026-04-06 — 참조 문서 우선순위 표 명문화 (d0004→d0002→d0003→d0001)
- v02 2026-04-06 — 상세기획 문서 지정 개발 추가: `ccdev run dXXXX`
- v01 2026-03-24 — 문서이력 섹션 추가 (ccskill run 자동)

---

## 1. 개요

ccplan 태스크를 TDD 사이클(Red->Green->Refactor)로 구현. **첫 실행 시 테스트 문서 자동 생성.**

> ⚠️ **필수**: run/check --fix 명령 시 반드시 Agent 도구로
> explore(haiku) 분석 → executor(opus) 구현 → quality-reviewer(opus) 리팩터 순서로 위임할 것.
> 직접 처리 금지.

**옵션**: --sp N (서브프로젝트), --framework NAME (프레임워크 명시)

**프레임워크 가이드 참조**:

| 방식 | 조건 | 가이드 |
|------|------|--------|
| 명시 지정 | `--framework streamlit` | `references/streamlit_guide.md` 강제 참조 |
| 자동 감지 | `pages/*.py` 존재 또는 `import streamlit` 검출 | `references/streamlit_guide.md` 자동 참조 |
| 명시 지정 | `--framework django` (향후) | `references/django_guide.md` |
| 미지정 | 감지 없음 | 일반 TDD 모드 |

> `--framework`가 자동 감지보다 우선. 새 프로젝트 시작 시(파일 미존재) 명시 지정 권장.

| 스킬 | 역할 | 문서 |
|------|------|------|
| `ccdev help` | 서브명령어 목록 표시 | 터미널 |
| `ccdev version` | 스킬 버전 정보 (v07) |
| ccplan | 설계 | d{SP}0002_plan.md |
| ccdev | **d{SP}0003 생성 (INIT)** + **GREEN + REFACTOR** | d{SP}0002_plan.md, d{SP}0003_test.md |
| **cctest** | **RED: TC 코드 작성 + 반복 실행** | tests/, d{SP}0003 Part C |
| ccfix | 수정 | d{SP}0004_todo.md |

> **단일 문서**: 현재 SP의 d{SP}0004 사전 검토 (.agents/skills/cccontext/SKILL.md 섹션 8)

### ccdev run 참조 문서 우선순위

| 순서 | 문서 | 역할 |
|------|------|------|
| 1 | d{SP}0004_todo.md | 사전 검토 — 개발 전 활성 이슈 확인 |
| 2 | d{SP}0002_plan.md | **핵심** — 미완료 Feature/Task 탐색 (개발 대상 결정) |
| 3 | d{SP}0003_test.md | TC와 1:1 매핑 — GREEN 구현 기준 |
| 4 | d{SP}0001_prd.md | 요구사항 참고 — 구현 방향 확인 |

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| ccdev init --framework NAME [경로] | 프레임워크 템플릿 기반 개발서 생성 |
| `ccdev status` | 서브명령어 리스트, 진행 상태 |
| `ccdev check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| ccdev show checklist | 역할 수행 체크리스트 표시 |
| ccdev add checklist "항목" | 체크리스트 항목 추가 |
| ccdev run | 미완료 Feature 전체 구현 |
| ccdev run [ID] | 특정 Feature 구현 (F002-1 등) |
| ccdev run dXXXX | 상세기획 문서(dXXXX_*.md) 기반 개발 |
| ccdev run dXXXX [ID] | 상세기획 문서 기반 특정 Feature 구현 |
| **ccdev run this** | **직전 작업 Feature/파일 계속 구현** (→ common_guide.md §9) |
| ccdev queue | 대기 큐 처리 |
| ccdev check --fix | 코드 최적화 (구 `optimize`) |

**옵션**: --max-iterations N, --timeout M, --interactive, --skip-refactor

**개발 대상 조건** (d{SP}0002_plan.md 참조):
1. Task까지 세분화 완료 (Task 없으면 TC 매핑 불가 -> TDD 불가)
2. 상태가 완료가 아님
3. PRD 5.1 페이지 개요에서 진행=예인 페이지만 (아니오는 제외)

## 3. 서브에이전트

| 단계 | 에이전트 | 병렬 |
|------|----------|:----:|
| 분석 | codebase_investigator, Explore | O |
| GREEN | task-executor | - |
| REFACTOR | python-code-reviewer, ooqa | O |
| 검증 | task-checker | - |
| 에스컬레이션 | codebase_investigator | - |

> RED 단계(TC 코드 작성)는 **cctest**가 담당

## 4. TDD 사이클

| 단계 | 담당 | 작업 | 산출물 |
|------|------|------|--------|
| INIT | **ccdev** | 테스트 문서 생성 | d{SP}0003_test.md (첫 실행 시) |
| RED | **cctest** | TC 코드 작성 + 실패 확인 | tests/TC*.py, d{SP}0003 Part C |
| GREEN | **ccdev** | 최소 구현 | 테스트 통과 |
| REFACTOR | **ccdev** | 품질 개선 | lint 통과 |
| VERIFY | **cctest** | 런타임 검증 + 반복 루프 | import 테스트 통과 |
| COMPLETE | **ccdev** | 문서 갱신 | d{SP}0003 [x] |

### 네이밍 규칙

| 레벨 | 형식 | 예시 |
|------|------|------|
| Epic | E{순번} | E002 |
| Feature | F{Epic}-{순번} | F002-1 |
| Task | F{Epic}-{Feature}.{순번} | F002-1.1 |
| TC | TC{Epic}-{Feature}.{Task} | TC002-1.1 |

**Task <-> TC 1:1 매핑**: F002-1.1 -> TC002-1.1_보건복지부탭.py

### 4.1 테스트 문서 생성 (INIT)

**첫 실행 시 d{SP}0003 존재 여부 확인 -> 없으면 자동 생성**

> **컨텍스트 적용**: cccontext.md 규칙에 따라 d{SP}0003_test.md 생성
> - SP=00: d0003_test.md (PRD: d0001_prd.md)
> - SP=02: d20003_test.md (PRD: d20001_prd.md)

> 코드 예시: references/guide.md 참조

**Part별 생성 규칙:**

| Part | 생성 방법 | 갱신 시점 |
|------|----------|----------|
| A | 공통 에러체크 (고정) | - |
| B | PRD 기능 -> 시나리오 도출 | PRD 변경 시 |
| C | **cctest RED 단계에서 등록** | 개발 진행 시 |
| D | SP별 분기 (아래 참조) | cctest refresh |

**Part D 생성 규칙 (중복 방지):**

| SP | Part D 처리 |
|:--:|------------|
| 00 | oo 모듈 스캔하여 직접 생성 |
| !=00 | "d0003_test.md Part D 참조" 링크만 추가 |

**Part B 시나리오 도출:**

| PRD 우선순위 | 시나리오 우선순위 |
|-------------|------------------|
| Must | P0 |
| Should | P1 |
| Could | P2 |
| Won't | 제외 |

**템플릿**: .agents/skills/cctest/templates/test/common_test_template.md

### 4.2 런타임 검증 (VERIFY) - 필수

REFACTOR 완료 후, COMPLETE 전에 반드시 실행.

```bash
uv run pytest tests/test_page_import.py -v
```

실패 시 → GREEN 단계로 돌아가 수정. 통과 시 → COMPLETE 진행.

> 상세 에러 유형 및 검증 방법: `.agents/skills/cccheck/SKILL.md` 런타임 검증 섹션 참조
> 템플릿: `.agents/skills/cctest/templates/test_page_import_template.py`

## 5. 상세기획 문서 기반 개발 (dXXXX 모드)

### 5.1 개요

`ccdev run dXXXX` 형식으로 특정 상세기획 문서를 지정하면, `d{SP}0002_plan.md` 대신 해당 문서를 개발 스펙으로 사용합니다.

```
ccdev run d41001          # d41001_*.md 문서 기반 전체 개발
ccdev run d41001 F001-1   # 특정 Feature만 구현
```

### 5.2 문서 탐색 규칙

| 우선순위 | 탐색 경로 |
|---------|----------|
| 1 | 현재 SP 폴더: `00_doc/sp{SP}/dXXXX_*.md` |
| 2 | 전체 탐색: `00_doc/**/dXXXX_*.md` |
| 3 | 프로젝트 루트 직접 탐색 |

**예시**: `ccdev run d41001` → `00_doc/sp04/d41001_데이터수집소스.md` 자동 탐색

### 5.3 워크플로우

> 코드 예시: references/guide.md 참조

### 5.4 문서 포맷 요구사항

지정 문서에 명시적 Task 구조가 있으면 그대로 사용. 없으면 AI가 자동 분해:

| 문서 포맷 | 처리 방식 |
|----------|----------|
| Feature/Task 명시 | 그대로 TDD 사이클 적용 |
| 요구사항 나열 | AI가 Feature/Task로 자동 분해 후 진행 |
| 자유 형식 | 핵심 기능 추출 → Task 분해 → 사용자 확인 |

### 5.5 일반 모드와 차이점

| 항목 | 일반 모드 | dXXXX 모드 |
|------|----------|-----------|
| 스펙 소스 | `d{SP}0002_plan.md` | `dXXXX_*.md` |
| Task 구조 | ooplan으로 사전 구성 필요 | 문서에서 자동 추출 가능 |
| 테스트 문서 | `d{SP}0003_test.md` | 동일 (dXXXX 연계 명시) |
| 완료 기록 | d{SP}0003 [x] | d{SP}0003 [x] + dXXXX 완료 표기 |

### 5.6 단계별 동작 규칙

| 현재 단계 | `ccdev run dXXXX` 동작 |
|----------|----------------------|
| 상세기획 | ❌ 차단: "`ccfeature next dXXXX`로 설계 전환 후 설계를 완료하세요" |
| 상세설계 | ✅ 설계→개발 자동전환 + cctest write(RED) + GREEN→REFACTOR |
| 상세개발 | ✅ cctest write(RED) + GREEN→REFACTOR |
| 상세검증 | ⚠️ 안내: "이미 검증 단계. `cccheck run dXXXX` 실행" |

## 6. 반복/에스컬레이션

- **반복 제한**: --max-iterations (기본 10)
- **에스컬레이션**: 반복 초과, 모호한 요구사항, 환경 문제 시

## 6. check --fix

```bash
ccdev check --fix              # 전체
ccdev check --fix [파일]       # 특정 파일
ccdev check --fix --dry-run    # 분석만
```

## 7. 워크플로우

ccplan -> ccdev run

## 8. GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 페이즈 실행 (TDD) | `ccdev run` | `/gsd:execute-phase [N]` |
| 자연어 작업 라우팅 | 직접 명령 | `/gsd:do "작업 설명"` |
| 빠른 단일 작업 | `ccdev run [ID]` | `/gsd:quick "작업"` |
| 자율 실행 (무인) | `ccdev run` | `/gsd:autonomous` |

**차이점:**
- `ccdev run` → TDD 사이클(Red→Green→Refactor), d{SP}0003 테스트 문서 연동
- `/gsd:execute-phase` → gsd-executor 에이전트, 원자적 커밋, 체크포인트 프로토콜

**조합 패턴:** 코드 예시: references/guide.md 참조

## 9. 프레임워크 레퍼런스 참조

> 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.codex/reference/development/{framework}/` 문서를 사전 로드하여 구현에 반영한다.

| 프레임워크 | 감지 조건 | 참조 경로 | 구현 참조 항목 |
|-----------|----------|----------|--------------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | 라우터 패턴, 핸들러 구조, 테스트 fixture, 에러 핸들링 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 구조, UI 패턴 |

## 10. 관련 문서

- ccplan.md: 설계
- cctest.md: 테스트 실행
- cccheck.md: 코드 체크
- d{SP}0002_plan.md: 구현 계획
- d{SP}0003_test.md: 테스트 케이스 (본 스킬에서 생성)
- d{SP}0004_todo.md: 이슈
- .agents/skills/cctest/templates/test/: 테스트 문서 템플릿

> **관련 명령어**: `.claude/commands/sc/implement.md` | `.claude/commands/sc/build.md` | `.claude/commands/sc/test.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.codex/rules/karpathy-guidelines.md`

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

