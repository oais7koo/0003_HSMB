---
name: ooprd
description: "PRD 생성 및 정합성 검증 스킬 'ooprd', 'PRD', '요구사항', 'clarify', 'unitdev' 등의 키워드로 트리거된다"
model: opus
metadata:
  version: v10
  category: core-dev
---

> 참조: common_guide.md, oocontext.md | 상세: .claude/skills/ooprd/references/guide.md

## 문서 이력 관리
- v10 2026-04-19 — validate/optimize → check/check --fix 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| 핵심 역할 | PRD 생성·현행화·코드/문서 정합성 검증 |
| 하지 않는 것 | 계획(→ooplan), 구현(→oodev), 이슈 수정(→oofix) |
| 수정 대상 | `00_doc/sp{N}/d{SP}0001_prd.md` |
| 실행 레벨 | [반자동] — 계획 표시 → 확인 후 실행 |

## 1. 개요

컨텍스트: `--sp N`/`oocontext N` · 출력: `d{SP}0001_prd.md` · 연계: `d{SP}0004_todo.md`(이슈), `d{SP}0002_plan.md`(개발) · 템플릿: guide.md §6.11

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooprd help` | 서브명령어 목록 | 터미널 |
| `ooprd version` | 스킬 버전 (v09) | 터미널 |
| `ooprd status` | 서브명령어 리스트, 상태 요약 | 터미널 |
| `ooprd check` | references/checklist.md 기반 체크 | 터미널 |
| `ooprd run` | PRD 생성 실행 | 터미널 |
| `ooprd run --with-update` | PRD 생성 후 현행화 | 터미널 |
| `ooprd show checklist` | 역할 체크리스트 표시 | 터미널 |
| `ooprd add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| ooprd run | PRD 생성/정합성 검증 | d{SP}0001_prd.md |
| `ooprd update` | 현행화 — 코드/현황 스캔 → PRD 반영 | d{SP}0001_prd.md |
| `ooprd update --dry-run` | 변경 예정 미리 출력 | 터미널 |
| **`ooprd run this`** | **직전 작업 PRD 섹션 갱신** (common_guide.md §9) | d{SP}0001_prd.md |
| ooprd run --template [type] | 템플릿 지정 생성 | d{SP}0001_prd.md |
| ooprd check --fix | PRD 최적화 (구 `optimize`) | d{SP}0001_prd.md |
| ooprd template | 템플릿 목록 | 터미널 |
| ooprd template [type] | 특정 템플릿 조회 | 터미널 |
| ooprd check --structure | 구조 검증 (구 `validate`) | 터미널 |
| ooprd section [N] | 특정 섹션 갱신 | d{SP}0001_prd.md |
| ooprd unitdev | 전체 단위개발문서 현행화 | d{SP}1XXX_*.md |
| ooprd unitdev [문서명] | 특정 단위개발문서 현행화 | 해당 문서 |
| ooprd clarify | PRD 모호성 해소 (최대 5개 질문) | d{SP}0001_prd.md |

## 3. 워크플로우

| 단계 | 동작 |
|------|------|
| run 분기 | PRD 없음→신규 / 있음→정합성 검증 |
| 신규 생성 | 템플릿 Must 누락 시 1개씩 질문 (빈칸 금지) — guide.md §6.1 |
| 정합성 검증 | 코드/d0002·d0003·d0005·d0006·d0008 비교 → d{SP}0004_todo 등록 |
| check --fix | 템플릿 완성·모호함 0·MoSCoW·중복 제거 |
| unitdev | 1.개요 기준 2~5 섹션 정합성 (연계: guide.md §6.2) |
| clarify | 6 영역 모호도 검사 → 최대 5개 질문 (guide.md §6.3) |

### 3.7 ooplan 분해용 PRD 필수 항목

| PRD 섹션 | ooplan 활용 |
|----------|------------|
| §기능요구사항 (MoSCoW) | Epic→Feature 분해 근거 |
| §기능 상세 (입출력/시나리오) | Feature→Task 세분화 근거 |
| §기술스택 (언어/프레임워크) | 기술 설계 방향 |

## 4. 정합성 검증 항목

> 코드 vs PRD / 문서 간 비교 표: references/guide.md §6.6

## 5. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|---------|------|------|:----:|
| 분석 | oh-my-claudecode:explore | haiku | 코드/문서 스캔 | O |
| 요구사항 분석 | oh-my-claudecode:analyst | opus | 명확화·수용 기준 | - |
| 검증 | task-checker | - | 정합성 검증 | - |
| PRD 품질 검토 | oh-my-claudecode:critic | opus | 비판적 검토 | - |
| 실행 | task-executor | - | 리포트/등록 | - |

## 6~10. 외부화 항목

| § | 주제 → 위치 |
|---|------|
| §6 | PRD 템플릿 → guide.md §6.11 |
| §7 | 검증 체크리스트(Must/Should/Could) → guide.md §6.7 |
| §8 | --compact 원칙(3KB·이력3·테이블) → guide.md §6.8 |
| §9 | PRD↔Plan 소유권/기재 금지 → guide.md §6.9 |
| §10 | SP00 플러그인 기재 금지 → guide.md §6.10 |

## 11. GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 신규 프로젝트 초기화 | `ooprd run` (신규) | `/gsd:new-project` |
| 신규 마일스톤 추가 | `ooprd run --template` | `/gsd:new-milestone` |
| 요구사항 모호성 해소 | `ooprd clarify` | `/gsd:discuss-phase [N]` |

> 조합 패턴: guide.md §6.4 / GSD `.planning/`, oo `00_doc/` 병행 가능

## 12. 관련 문서

- .claude/skills/ooprd/templates/prd/, .claude/templates/common_unit_dev_doc.md
- d{SP}0001_prd.md, d{SP}0002_plan.md, d{SP}0004_todo.md
- 관련 명령어: .claude/commands/sc/design.md, .claude/commands/sc/document.md

<!-- RUN-UPDATE-REF:START -->
## run과 update 분리 원칙
> `.claude/guides/run_update_separation.md` 준수. `run`이 `update`를 자동 호출 안 함.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 배치/구체 명령 실행 (일회성) |
| `update` | 상태·설정 현행화 (멱등) |
<!-- RUN-UPDATE-REF:END -->

<!-- QMD-REF:START -->
## QMD 마크다운 검색
> MD **내용** 탐색 시 `mcp__qmd__query` 우선, 미가동 시 Glob/Grep 폴백. 기준: common_guide.md §10

| 도구 | 적합한 상황 |
|------|-----------|
| `mcp__qmd__query` (lex) | 키워드·문서번호·용어 |
| `mcp__qmd__query` (vec) | 자연어 의미 검색 |
| `Glob` | 파일 경로 패턴 |
| `Grep` | 코드·특정 문자열 |

**인덱싱**: `oostart run` 시 `qmd update` / 최초: `qmd collection add . --name {프로젝트명}`
<!-- QMD-REF:END -->

<!-- KARPATHY-REF:START -->
## Karpathy 코딩 가이드라인 (필수 준수)
> `/andrej-karpathy-skills:karpathy-guidelines` 4원칙. 미러: `.claude/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | Think Before Coding | 가정 명시, 불확실하면 질문 |
| 2 | Simplicity First | 최소 코드, 투기적 추상화·에러처리 금지 |
| 3 | Surgical Changes | 범위 밖 "개선" 금지, 기존 스타일 유지 |
| 4 | Goal-Driven Execution | 검증 가능한 성공 기준 후 루프 |
<!-- KARPATHY-REF:END -->

<!-- GEMMA-REF:START -->
## Gemma 위임 (로컬 LLM)
> 단순/반복(번역·요약·분류·Rephrase·포맷 변환)은 승인 후 `gemma` 위임.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
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
