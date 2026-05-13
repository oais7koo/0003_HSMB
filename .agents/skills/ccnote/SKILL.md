---
name: ccnote
description: "공통 가이드: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

# ccnote - 연구노트 관리 스킬

> 공통 가이드: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 날짜/시간 기반 연구노트를 d{SP}0020_연구노트.md에 작성·조회 |
| **하는 것** | 연구노트 항목 추가(타임스탬프 자동), 조회, 요약 |
| **하지 않는 것** | 옵시디언 노트(→oosidi), 이력 관리(→oohistory), 연구 수행(→ooresearch) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `d{SP}0020_연구노트.md` |
| **실행 레벨** | [자동] — 입력 내용 즉시 파일에 기록 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

## 1. 개요

`d{SP}0020_연구노트.md` 문서에 날짜/시간 기반 연구노트를 작성하고 조회하는 스킬.

**핵심 기능**:
1. **노트 추가**: `ccnote add "내용"` → 오늘 날짜 섹션에 자동 기록
2. **오늘 조회**: `ccnote today` → 오늘 작성된 노트 표시
3. **날짜 조회**: `ccnote list [날짜]` → 특정 날짜 노트 표시
4. **검색**: `ccnote search "키워드"` → 전체 노트 검색
5. **현황**: `ccnote status` → 통계 및 최근 항목

**파일 위치**: `00_doc/d{SP}0020_연구노트.md`

> **문서 번호**: d0020

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccnote help` | 서브명령어 목록 표시 |
| `ccnote version` | 스킬 버전 정보 (v01) |
| `ccnote status` | 서브명령어 리스트, 오늘/전체 노트 현황 |
| `ccnote check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ccnote run` | 연구노트 작성 실행 |
| `ccnote show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ccnote add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ccnote` | 오늘 연구노트 표시 (= today) |
| `ccnote add "내용"` | **연구노트 추가** (현재 날짜/시간 자동 기록) |
| `ccnote today` | 오늘 작성된 노트 표시 |
| `ccnote list [날짜]` | 날짜별 조회 (예: `ccnote list 2026-03-21`) |
| `ccnote list --all` | 전체 날짜 목록 표시 |
| `ccnote search "키워드"` | 키워드 전체 검색 |
| `ccnote init` | 연구노트 파일 초기 생성 |

실행: `uv run python .claude/skills/ccnote/scripts/oonote_run.py [args]`

## 3. 노트 추가 워크플로우

> 코드 예시: references/guide.md 참조

### 3.1 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--title "제목"` | 제목 지정 | `ccnote add --title "실험 결과" "내용"` |
| `--tag "태그"` | 태그 지정 | `ccnote add --tag "실험" "내용"` |
| `--ref "참조"` | 참조 추가 | `ccnote add --ref "d0002_plan.md" "내용"` |
| `--time "HH:MM"` | 시간 수동 지정 | `ccnote add --time "09:00" "내용"` |
| `--sp N` | 서브프로젝트 지정 | `ccnote add --sp 03 "내용"` |

## 4. 파일 구조

> 코드 예시: references/guide.md 참조

### 4.1 서브프로젝트별 파일

| SP | 파일 |
|:--:|------|
| 00 | 00_doc/sp00/d0020_연구노트.md |
| 01 | 00_doc/sp01/d10020_연구노트.md |
| 02 | 00_doc/sp02/d20020_연구노트.md |
| 03 | 00_doc/sp03/d30020_연구노트.md |
| 04 | 00_doc/sp04/d40020_연구노트.md |

## 5. 태그 체계

| 태그 | 용도 |
|------|------|
| `[실험]` | 실험 수행 및 결과 |
| `[분석]` | 데이터/코드 분석 |
| `[회의]` | 미팅/토론 내용 |
| `[아이디어]` | 아이디어/가설 |
| `[문제]` | 발견된 문제/버그 |
| `[해결]` | 문제 해결 과정 |
| `[참고]` | 논문/문서 참조 메모 |
| `[계획]` | 향후 작업 계획 |

## 6. 검색 기능

> 코드 예시: references/guide.md 참조

### `ccnote search "키워드"` 옵션

| 옵션 | 설명 |
|------|------|
| `--tag "태그"` | 특정 태그만 검색 |
| `--date "YYYY-MM"` | 특정 월만 검색 |
| `--limit N` | 최근 N개만 표시 (기본: 10) |

## 7. status 출력

> 코드 예시: references/guide.md 참조

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 8. 서브에이전트

| 단계 | 에이전트 | 역할 | 병렬 |
|------|----------|------|:----:|
| 파일 탐색 | Explore (haiku) | 노트 파일 확인 | - |
| 노트 작성 | 직접 처리 | 파일 편집 | - |

> **관련 문서**: `00_doc/d{SP}0020_연구노트.md` | `.claude/skills/oocontext/SKILL.md`

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

