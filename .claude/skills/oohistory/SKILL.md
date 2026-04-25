---
name: oohistory
description: "완료 항목 이력 이동 스킬 'oohistory', '이력 이동', '히스토리 관리', '아카이브' 등을 요청할 때 사용한다"
metadata:
  version: "v01"
  category: "doc-env"
---

# oohistory - 완료 항목 이력 이동 스킬

> 공통: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d{SP}0004_todo.md 완료 항목을 d{SP}0010_history.md로 이동 (아카이브) |
| **하는 것** | 완료 이슈 이동, 오래된 이력 자동 축약(>20K→10K), SP 병행 처리 |
| **하지 않는 것** | Git 커밋(→oocommit), 이슈 수정(→oofix), 커스텀 Todo 처리(→ootodo) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `d{SP}0004_todo.md`, `d{SP}0010_history.md` |
| **실행 레벨** | [자동] — 완료 항목 자동 탐지 후 이동 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

## 1. 개요

d{SP}0004_todo.md 완료 항목 -> d{SP}0010_history.md 이동

**컨텍스트**: `--sp N` 또는 `oocontext N`

> **스코프 경계**: oohistory는 **문서 이력 아카이브** 전담 (d0004→d0010). git 커밋/푸시는 `oocommit` 담당.

| 기능 | 설명 |
|------|------|
| `oohistory help` | 서브명령어 목록 표시 |
| `oohistory version` | 스킬 버전 정보 (v01) | 터미널 |
| 이력 이동 | d{SP}0004 -> d{SP}0010 |
| 병행 처리 | SP!=00일 때 d0004->d0010 AND d{SP}0004->d{SP}0010 |
| 자동 요약 | >20K -> 10K 축소 |

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `oohistory status` | 서브명령어 리스트, 이동 대상 항목 수, d0010 토큰 상태 | - |
| `oohistory check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oohistory show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oohistory add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oohistory run` | 완료 항목 d{SP}0010 이동 | 00_doc/d{SP}0010_history.md |
| **`oohistory run this`** | **직전 완료 이슈 아카이브** (→ common_guide.md §9) | 00_doc/d{SP}0010_history.md |

실행: `uv run python .claude/skills/oohistory/scripts/oohistory_run.py [args]`

## 3. 워크플로우

**타이밍**: 해결 후 1~2주 안정성 확인

```
d{SP}0004 스캔 -> 태그 추론 -> d{SP}0010 등록 -> 토큰 체크(>20K시 요약) -> d{SP}0004 삭제
```

### 자동 요약

| 항목 | 값 |
|------|-----|
| 트리거 | >20K |
| 목표 | 10K |
| 보존 | 최근 30일 상세 |

**방식**: FIFO 1줄 요약 -> "## 아카이브 요약" 이동

## 4. 형식 처리

**대상**: d{SP}0004 "해결된 이슈" 섹션 (표준/비표준)

| 형식 | 처리 |
|------|------|
| 표준 테이블 | 태그 유지 |
| 마크다운 목록 | 태그 추론 |
| 텍스트/인용 | MISC 적용 |

**태그 추론**:

| 키워드 | 태그 |
|--------|------|
| error, fix, bug | BUGFIX |
| security, 보안 | HOTFIX |
| update, 버전 | UPDATE |
| feature, 기능 | FEATURE |
| refactor, optimize | IMPROVE |
| doc, 문서 | DOCS |
| (없음) | MISC |

## 5. d0010 형식

```
#### YYYY-MM-DD - [태그] [제목]
- 파일: 경로 | 원인: 내용 | 해결: 방법
```

**태그**: HOTFIX | BUGFIX | UPDATE | FEATURE | IMPROVE | DOCS | REFACTOR | CONFIG | MISC

## 6. 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|----------|------|:----:|
| 스캔 | Explore | haiku | O |
| 요약 | task-executor | sonnet | - |
| 검증 | task-checker | sonnet | - |

## 7. 컴팩트 생성 원칙 (--compact)

`oohistory run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

## 8. 관련 문서

- **입력**: 00_doc/d{SP}0004_todo.md
- **출력**: 00_doc/d{SP}0010_history.md
- **태그**: .claude/skills/ootodo/references/guide.md

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

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
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->

