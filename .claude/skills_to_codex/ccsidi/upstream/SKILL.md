---
name: oosidi
description: "옵시디언 볼트 문서 작성/관리 스킬 'oosidi', '옵시디언', 'obsidian', '노트 작성', '볼트 관리' 등을 요청할 때 트리거된다"
metadata:
  version: "v01"
  category: "doc-env"
---

# oosidi - 옵시디언 볼트 문서 관리

> 01_obsidian/ 볼트의 마크다운 문서 생성·편집·검색·구조 관리 스킬 | ref: `.claude/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 01_obsidian/ 볼트의 마크다운 문서 생성·편집·검색·구조 관리 |
| **하는 것** | 옵시디언 노트 CRUD, 태그·링크 관리, 볼트 구조 탐색 |
| **하지 않는 것** | 연구노트(→oonote), 프로젝트 문서(→oodoc), 소개서 작성(→oosidi [소개서]) |
| **참조 범위** | `01_obsidian/` 볼트 내부 파일만 / 외부 볼트 자동 포함 안 함 |
| **수정 대상** | `01_obsidian/**/*.md` |
| **실행 레벨** | [반자동] — 노트 생성/수정 내용 확인 후 실행 |
| **에이전트 호환** | 범용 — 마크다운 파일 작업 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v03 2026-03-29 — 페이지 정리 표준 포맷 가이드 추가 (참조: android studio 환경.md)
- v02 2026-03-26 — 표준 폴더 구조 패턴 반영: init-topic, init-folder 명령 추가
- v01 2026-03-26 — 초기 생성

---

## 개요

옵시디언 볼트(`01_obsidian/`)의 마크다운 문서를 체계적으로 관리하는 스킬이다.

- 폴더별 문서 생성·편집·검색
- 볼트 구조 탐색 및 상태 리포팅
- 인덱스 파일 자동 갱신
- `[[위키링크]]` 기반 문서 간 연결 관리

### 볼트 구조

> 코드 예시: references/guide.md 참조

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oosidi help` | 서브명령어 목록 표시 |
| `oosidi version` | 스킬 버전 정보 (v01) |
| `oosidi status` | 볼트 폴더별 문서 수, 전체 현황 |
| `oosidi run` | 상태 점검 + 리포트 (기본) |
| `oosidi list <폴더>` | 특정 폴더의 문서 목록 |
| `oosidi create <폴더> "<제목>"` | 새 문서 생성 |
| `oosidi index <폴더>` | 폴더 인덱스 파일 갱신 |
| `oosidi search "<키워드>"` | 볼트 전체 키워드 검색 |
| `oosidi init-topic <폴더> "<주제>"` | 주제 서브폴더 + 개요 5종 세트 생성 |
| `oosidi init-folder <NNNN> "<이름>"` | 최상위 폴더 + 인덱스 + 개요 5종 세트 |
| `oosidi links <파일>` | 문서의 위키링크 연결 상태 확인 |
| `oosidi check` | references/checklist.md 기반 전체 체크 |
| `oosidi check <NNNN>` | 해당 번호로 시작하는 폴더만 C05/C06 체크 (예: `check 0004`) |

실행: `uv run python .claude/skills/oosidi/scripts/oosidi_run.py [args]`

---

## 워크플로우

> 코드 예시: references/guide.md 참조

---

## 문서 작성 규칙

### 파일명 규칙
- 폴더 인덱스: `{폴더번호}_{폴더명}.md` (예: `0004_DesignSystem.md`)
- 일반 문서: `{번호}_{제목}.md` (예: `01_DesignSystem 개요.md`)
- 한글 파일명 허용

### 표준 서브폴더 구조

모든 주제 폴더는 다음 기본 서브폴더를 공통으로 가진다:

| 서브폴더 | 용도 | 비고 |
|----------|------|------|
| `01_개요/` | 개요 5종 세트 (개요/환경/사용/APIs/채널) | 필수 |
| `02_개념/` | 핵심 개념, 용어 정리, 원리 설명 | 필수 |
| 이후 폴더 | 주제별 자유 구성 | 선택 |

> 코드 예시: references/guide.md 참조

> `oosidi init-folder`는 `01_개요/` + 5종 세트를 자동 생성. `02_개념/`은 수동 생성.

### 문서 구조
- 모든 문서는 `## 개요` 헤더로 시작
- 관련 문서는 `[[위키링크]]`로 연결
- 인덱스 파일에 하위 문서 목록 유지

### 페이지 정리 표준 포맷

`oosidi 정리` 요청 시 아래 포맷을 기준으로 정리한다.

**구조 규칙:**
1. `## 개요` — 한 줄 요약 설명으로 시작
2. `## 섹션` — 주요 주제별 H2 헤딩
3. `### N단계:` — 순차 절차는 번호 + 헤딩 (`### 1단계: 제목`)
4. 순서 있는 항목은 번호 리스트 (`1. 2. 3.`)
5. 순서 없는 항목은 불릿 리스트 (`- `)

**서식 규칙:**
- 메뉴 경로: 인라인 코드 (`` `Settings → SDK` ``)
- 핵심 용어: **볼드** (`**AVD**`)
- 명령어/코드: ` ```bash ` 코드 블록 (언어 지정 필수)
- 불필요한 공백 라인 제거, 들여쓰기 통일

**참조 예시:** `7934_android studio/02_android studio 환경.md`

> 코드 예시: references/guide.md 참조

---

## 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 스캔 | Explore | haiku | 볼트 구조 탐색 (병렬) |
| 검색 | Explore | haiku | 키워드 검색 (병렬) |

---

## 관련

`.claude/skills/oosidi/scripts/oosidi_run.py` | `.claude/skills/oodoc/SKILL.md` | `01_obsidian/`

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

