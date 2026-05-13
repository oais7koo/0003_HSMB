---
name: cccontext
description: "**SP 목록은 각 프로젝트의 `d0001_prd.md` §2.1에 정의됨** (SSOT)"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

# cccontext - 서브프로젝트 컨텍스트 관리

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 현재 세션의 서브프로젝트(SP) 컨텍스트 설정 — 이후 모든 스킬이 해당 SP 기준으로 동작 |
| **하는 것** | SP 번호 지정, SP별 문서 경로 규칙 설정, 현재 컨텍스트 표시 |
| **하지 않는 것** | 파일 생성·수정, 코드 실행, 외부 연동 |
| **참조 범위** | 세션 내 컨텍스트 설정만 / SP 목록은 `d0001_prd.md §2.1` 참조 |
| **수정 대상** | 없음 (세션 상태만 변경) |
| **실행 레벨** | [수동] — 즉시 적용, 파일 수정 없음 |
| **에이전트 호환** | 범용 — SP 번호를 환경 변수나 인자로 전달하는 방식으로 모든 에이전트 활용 가능 |

## 문서 이력 관리
- v09 2026-04-07 — SP 번호 체계 테이블 제거 — 프로젝트 전용 정보는 SKILL.md에 포함 불가 (d0001_prd.md §2.1이 SSOT)
- v08 2026-03-22 — SP04 프로젝트명 youtube→scraping 변경
- v07 2026-03-22 — SP 번호 이동: SP04→SP05(youtube_graphRAG), SP05→SP06(oohwp_skill)
- v06 2026-03-13 — SP 현행화 및 자동 감지 테이블 업데이트
- v05 2026-03-01 — 문서번호 = SP x 10000 + 기본번호 공식으로 통일

## 개요

서브프로젝트별 문서 컨텍스트 설정. 모든 oo 스킬이 해당 SP 문서 참조.

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `cccontext status` | 서브명령어 리스트, 현재 상태 |
| `cccontext check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `cccontext run` | 컨텍스트 전환 실행 (sp_config.json 자동 갱신 포함) | 터미널 |
| `cccontext show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `cccontext add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `cccontext` | 현재 컨텍스트 확인 |
| `cccontext [N]` | SP N으로 설정 (00~09) |
| `cccontext clear` | 공통(00) 초기화 |
| `cccontext list` | SP 목록 표시 |
| `cccontext load [경로]` | 프로젝트 구조/종속성/메타데이터 수집 (load 흡수) |

load 옵션: `--depth shallow\|deep\|full`, `--focus api\|ui\|db\|config`

## SP 번호 체계

> **SP 목록은 각 프로젝트의 `d0001_prd.md` §2.1에 정의됨** (SSOT)
> SKILL.md에 프로젝트 전용 SP 목록을 두지 않음 — oosync로 다른 프로젝트에 배포될 수 있음

SP 폴더는 `0N_*` 패턴으로 자동 감지됨 (아래 자동 감지 테이블 참조).

## 문서 매핑

```
문서번호 = SP x 10000 + 기본번호
예) SP=00: d0001 -> d0001,  d0004 -> d0004
    SP=02: d0001 -> d20001, d0004 -> d20004
    SP=05: d0001 -> d50001, d0004 -> d50004
```

## 우선순위

`--sp N` > 세션 컨텍스트 > CWD 감지(`0N_*`) > 기본값(00)

## 자동 감지

| CWD 패턴 | SP |
|----------|:--:|
| `*/01_*/*`, `01_*` | 01 |
| `*/02_*/*`, `02_*` | 02 |
| `*/03_*/*`, `03_*` | 03 |
| `*/04_*/*`, `04_*` | 04 |
| `*/05_*/*`, `05_*` | 05 |
| `*/06_*/*`, `06_*` | 06 |
| `*/07_*/*`, `07_*` | 07 |
| 그 외 | 00 |

## 문서 등록 규칙

> **핵심 규칙**: context 설정에 따라 **단일 문서**에만 등록

| 조건 | 등록 대상 | 예시 |
|------|----------|------|
| `cccontext` 미지정 (SP=00) | `00_doc/sp00/d0004_todo.md` | d0004 |
| `cccontext 02` (SP=02) | `00_doc/sp02/d20004_todo.md` | d20004 |
| `cccontext 05` (SP=05) | `00_doc/sp05/d50004_todo.md` | d50004 |

> **파일명 규칙**: 문서번호 = SP x 10000 + 기본번호 (예: SP=00 → d0004, SP=02 → d20004, SP=05 → d50004)

### 적용 대상

| 스킬 | 처리 방식 |
|------|----------|
| oocheck | 에러를 현재 SP의 todo 문서에 등록 |
| **oofix** | **SP!=00: `d{SP}0004` + `d0004` 둘 다 확인/수정** |
| oodev | 현재 SP의 todo 문서 사전 검토 |
| oohistory | 현재 SP의 todo -> history 아카이브 |

> **oofix 예외**: 수정 작업은 공통 모듈(oo)에도 영향을 줄 수 있으므로 d0004도 함께 처리

### 주의사항

- **파일 자동 생성**: `d{SP번호}0004` 파일이 없으면 즉시 생성 (예: SP=02 → `d20004_todo.md`)
- **context 전환 시**: 이전 SP 이슈는 해당 SP 문서에서만 관리
- **공통 oo 모듈 이슈**: context 미지정 상태에서 d0004에 등록 권장

> **관련 명령어**: `.claude/commands/sc/task.md` | `.claude/commands/sc/spawn.md`

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| SP 탐색 | `Explore` | haiku | - |
| 컨텍스트 검증 | `task-checker` | sonnet | - |

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

## 관련 문서

- `.claude/guides/common_guide.md`, `CLAUDE.md`
