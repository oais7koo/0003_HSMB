---
name: ccdoc
description: "공통: `.claude/guides/common_guide.md` / 옛 이력: `references/guide.md §12`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

# ccdoc - 문서 생성 통합 스킬

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d0001~d0010 핵심 문서 생성·업데이트·최적화 오케스트레이터 |
| **하는 것** | PRD·Plan·Test·Todo·History·User·Env 문서 일괄 생성/현행화, 문서 정합성 검사 |
| **하지 않는 것** | 코드 수정(→oodev), 이슈 수정(→oofix), 스킬 파일 수정(→ooskill) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (`00_doc/`, `.claude/skills/`) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `run/check --fix`: `d{SP}0001~d{SP}0010_*.md` / `clear`: `00_doc/**/d*.md` + skills + guides (전체) |
| **실행 레벨** | [자동] — 대상 문서 자동 탐지 후 일괄 처리 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v15 2026-04-19 — optimize → check --fix 통합 (check 명령으로 일원화)
- v14 2026-04-11 — std 추가: 문서 번호 체계 조회·편집 서브명령어
- v13 2026-04-04 — update 추가: 코드 작업 후 변경 영향 문서 자동 탐지 및 업데이트
- v12 2026-04-03 — list/gen SP-aware 추가: SP별 문서 현황 조회 및 빈 문서 일괄 생성
- v11 2026-03-02 — optimize 재정의: SKILL.md → 00_doc/ 문서(d0001~d0010) 최적화로 변경

> 공통: `.claude/guides/common_guide.md` / 옛 이력: `references/guide.md §12`

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccdoc help` | 서브명령어 목록 표시 |
| `ccdoc version` | 스킬 버전 정보 (v12) |
| `ccdoc status` | 서브명령어 리스트, 스킬/문서 현재 상태 |
| `ccdoc run [--doc 문서\|--required-only\|--dry-run\|--compact]` | d0001~d0010 문서 생성/업데이트 |
| `ccdoc create [문서ID]` | 특정 문서 생성 |
| `ccdoc explain [대상]` | 코드/함수/모듈/시스템 설명 생성 (explain 흡수) |
| `ccdoc check --fix [문서ID\|--content\|--size]` | 00_doc/ 문서(d0001~d0010) 최적화 (구 `optimize`) |
| `ccdoc clear [--keep N\|--scope 범위]` | 이력 초과 행 제거 (기본 5개 유지) — **범위: `00_doc/**/d*.md` 전체 + skills + guides** (d0010 이후 상세문서 포함) |
| `ccdoc check [SP번호] [--quality\|--integrity] [--skill\|--doc] [--fix]` | 품질+정합성 통합 검사 (기본: 전체) |
| `ccdoc show checklist` | 역할 수행 체크리스트 표시 |
| `ccdoc add checklist "항목"` | 체크리스트 항목 추가 |
| `ccdoc list [--sp N]` | SP별 문서 현황 조회 (존재/미생성 상태) |
| `ccdoc gen [--sp N] [--dry-run]` | SP별 미생성 문서를 빈 템플릿으로 일괄 생성 |
| `ccdoc update [--scope 범위] [--commit HEAD~N] [--dry-run]` | 코드 작업 후 관련 문서 자동 업데이트 |
| **`ccdoc update this`** | **직전 작업 영향 문서 업데이트** (→ common_guide.md §9) |
| `ccdoc manual [--update]` | d0000_manual.md 업데이트 (수동 관리 문서) |
| `ccdoc numbering` | 문서 번호 체계(SSOT) 조회 |
| `ccdoc numbering add [번호] [파일명패턴] [용도] [생성스킬]` | 새 번호 항목 추가 |
| `ccdoc numbering remove [번호]` | 번호 항목 제거 |
| `ccdoc numbering edit` | SSOT 파일 직접 편집 경로 안내 |

`explain` 옵션: `--level basic|intermediate|advanced`, `--format text|diagram|examples`

실행 (스크립트 매핑):
- `oodoc_run.py [args]`: run/create/check --fix/list/gen/validate
- `oodoc_clear.py [--keep N] [--scope all|00_doc|skills|guides]`: clear
- `oodoc_check.py [sp번호] [--fix]`: check --integrity (기본 check는 run+check 순차)
- `oodoc_numbering.py [show|edit|add|remove]`: numbering (SSOT 조회/편집 — add/remove는 §2.3 0100~0999 범위만)
- 모든 호출: `uv run python .claude/skills/ccdoc/scripts/{스크립트}`

## 3. 상세 워크플로우 (외부화)

> 모든 상세는 `references/guide.md` 참조: §2.1 Phase·의존 / §4 사용 예시 / §6 run 순서·병렬 / §7 check --fix / §8 --quality / §9 --integrity / §10 std / §11 update / §13 문서-스킬 매핑

## 6. 문서 번호 체계 (ccdoc numbering)

> SSOT: `references/doc_numbering.md` / 범위표: `references/guide.md §10`

## 7. 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 분석 | Explore | haiku | O |
| 최적화 | task-executor | sonnet | O |
| 검증 | task-checker | sonnet | - |

## 8. 관련 문서

CLAUDE.md · .claude/templates/ · 00_doc/sp00/d0001~d0010 / 명령어: `.claude/commands/sc/index.md`

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
