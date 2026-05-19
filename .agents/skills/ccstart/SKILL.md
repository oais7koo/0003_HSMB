---
name: ccstart
description: "세션 시작 시 공통 가이드 로드, 문서 동기화 및 품질 검사 | ref: `.codex/guides/common_guide.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# ccstart - 세션 시작 워크플로우

> 세션 시작 시 공통 가이드 로드, 문서 동기화 및 품질 검사 | ref: `.codex/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 세션 시작 시 환경 점검·문서 동기화·체크리스트 실행 |
| **하는 것** | 서브프로젝트 스캔, common_guide 로드, 문서 상태 점검, cccheck 연동 안내 |
| **하지 않는 것** | 코드 수정(→ccdev), 환경 설치(→ooenv), 파일 생성(→ccdoc) |
| **참조 범위** | 현재 프로젝트 내부 문서 파일 + 환경변수 / 외부 시스템 자동 연결 안 함 |
| **수정 대상** | 없음 (점검·보고만) |
| **실행 레벨** | [자동] — 세션 시작 시 `uv run python ...` 자동 실행 |
| **에이전트 호환** | Codex 권장 — `uv run` 스크립트 실행 / 다른 에이전트: 문서 상태를 수동으로 확인하거나 점검 항목을 직접 실행 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ccskill run 자동)

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ccstart help` | 서브명령어 목록 표시 |
| `ccstart version` | 스킬 버전 정보 (v03) |
| `ccstart status` | 서브명령어 리스트, 스킬/문서 상태 |
| `ccstart check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ccstart show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ccstart add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ccstart run` | 세션 시작 실행 (기본) |

실행: `uv run python .agents/skills/ccstart/scripts/oostart_run.py`

## 워크플로우

**서브프로젝트 감지 (01~10)** → **common_guide.md 로드** → 문서 상태 점검 (PRD/TODO/HISTORY) → 동기화 체크리스트 → cccheck 연동 → 준비 완료

### 서브프로젝트 감지

- 01_* ~ 10_* 디렉토리를 자동 스캔
- 활성/미생성 상태 표시 (Active N / 10)
- 서브프로젝트는 동적으로 변경 가능

## 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 스캔 | Explore | haiku | 프로젝트 구조 (병렬) |
| 검증 | task-checker | sonnet | 환경/설정 (병렬) |

## 관련

`.agents/skills/ccstart/scripts/oostart_run.py` | `.agents/skills/cccheck/SKILL.md` | `00_doc/d{SP}0004_todo.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

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

