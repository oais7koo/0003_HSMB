---
name: oonext
description: "다음 작업 추천 스킬 'oonext', '다음 작업', '우선순위 추천', '뭐 할까' 등을 요청할 때 트리거된다"
metadata:
  version: "v01"
  category: "meta-util"
---

# oonext - 다음 작업 우선순위 추천

> PRD·Plan·Todo 문서를 분석하여 우선 진행할 작업을 추천 | ref: `.claude/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | PRD·Plan·Todo 문서를 분석하여 다음에 진행할 작업 우선순위 추천 |
| **하는 것** | 미완료 Feature/이슈 분석, 우선순위 정렬, 다음 작업 추천 목록 출력 |
| **하지 않는 것** | 작업 실행(→ooflow/oodev), 이슈 수정(→oofix), 문서 수정(→oodoc) |
| **참조 범위** | 현재 프로젝트 내부 문서 파일만 (d{SP}0001~0004) / 외부 시스템 자동 포함 안 함 |
| **수정 대상** | 없음 (읽기·분석·출력만) |
| **실행 레벨** | [수동] — 분석 결과 출력만, 파일 수정 없음 |
| **에이전트 호환** | 범용 — 파일 읽기 기반 분석으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v01 2026-03-25 — 초기 생성

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oonext help` | 서브명령어 목록 표시 |
| `oonext version` | 스킬 버전 정보 (v01) |
| `oonext status` | 서브명령어 리스트, 스킬 상태 |
| `oonext check` | references/checklist.md 기반 체크 및 리포팅 |
| `oonext show checklist` | 역할 수행 체크리스트 표시 |
| `oonext add checklist "항목"` | 체크리스트 항목 추가 |
| `oonext run` | **현재 컨텍스트 기준 다음 작업 추천 실행 (기본)** |
| **`oonext run this`** | **last_target 기반 다음 작업 추천** (→ common_guide.md §9) |
| `oonext run --sp N` | 특정 서브프로젝트 대상으로 추천 |
| `oonext run --all-sps` | 전체 서브프로젝트 대상으로 추천 |
| `oonext run --top N` | 상위 N개만 표시 (기본: 5) |

실행: `uv run python .claude/skills/oonext/scripts/oonext_run.py [args]`

## 워크플로우

**문서 수집** → **항목 추출** → **우선순위 점수 산정** → **추천 리스트 출력**

### 1. 문서 수집

| 문서 | 추출 대상 | 점수 가중치 |
|------|----------|------------|
| d{SP}0004_todo.md | Active Issues (CRITICAL/ERROR/WARNING) | 최고 |
| d{SP}0004_todo.md | 커스텀 Todo (대기 중) | 높음 |
| d{SP}0002_plan.md | 향후 계획 (Phase 2+), 기술 부채 | 중간 |
| d{SP}0001_prd.md | 미구현 요구사항 | 참고 |

### 2. 우선순위 점수 산정

| 요소 | 점수 | 설명 |
|------|------|------|
| CRITICAL 이슈 | 100 | 즉시 대응 필요 |
| ERROR 이슈 | 80 | 24시간 내 대응 |
| WARNING 이슈 | 40 | 1주일 내 대응 |
| 커스텀 Todo (high) | 70 | 사용자 지정 높음 |
| 커스텀 Todo (medium) | 50 | 사용자 지정 보통 |
| 커스텀 Todo (low) | 30 | 사용자 지정 낮음 |
| Plan 항목 (High) | 60 | 계획 우선순위 높음 |
| Plan 항목 (Medium) | 40 | 계획 우선순위 보통 |
| Plan 항목 (Low) | 20 | 계획 우선순위 낮음 |
| 기술 부채 (P1) | 55 | 긴급 기술 부채 |
| 기술 부채 (P2) | 35 | 일반 기술 부채 |

### 3. 출력 형식

```markdown
# oonext - 다음 작업 추천

현재 컨텍스트: SP07
분석 문서: d70001_prd.md, d70002_plan.md, d70004_todo.md

## 추천 작업 (상위 5개)

| 순위 | 점수 | 출처 | SP | 내용 |
|:----:|:----:|------|:--:|------|
| 1 | 100 | todo/이슈 | 05 | [CRITICAL] ... |
| 2 | 80 | todo/이슈 | 00 | [ERROR] ... |
| 3 | 70 | todo/커스텀 | 02 | ... |
| 4 | 60 | plan | 00 | 불필요 스크립트 정리 |
| 5 | 55 | plan/부채 | 00 | TD-01: oostart 스크립트 경로 수정 |

## 요약
- 활성 이슈: N건 (CRITICAL: X, ERROR: Y, WARNING: Z)
- 대기 Todo: N건
- 계획 항목: N건
- 기술 부채: N건
```

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 특정 서브프로젝트만 분석 | 현재 컨텍스트 |
| `--all-sps` | 전체 서브프로젝트 분석 | false |
| `--top N` | 상위 N개 표시 | 5 |
| `--all` | 모든 항목 표시 (점수순 정렬) | false |
| `--source [todo\|plan\|prd]` | 특정 출처만 분석 | 전체 |

## 서브프로젝트 지원

| SP | PRD | Plan | Todo |
|:--:|-----|------|------|
| 00 | d0001_prd.md | d0002_plan.md | d0004_todo.md |
| 01~10 | d{N}0001_prd.md | d{N}0002_plan.md | d{N}0004_todo.md |

## 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 스캔 | Explore | haiku | 문서 파일 탐색 (병렬) |

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 관련

`.claude/skills/ootodo/SKILL.md` | `.claude/skills/ooplan/SKILL.md` | `.claude/skills/ooprd/SKILL.md` | `00_doc/d{SP}0004_todo.md`

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

