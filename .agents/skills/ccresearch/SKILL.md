---
name: ccresearch
description: "공통: `.codex/guides/common_guide.md` | 에이전트 참조: `agents.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

> 공통: `.codex/guides/common_guide.md` | 에이전트 참조: `agents.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | SOTA 비교 기준으로 특정 분야 연구를 체계적으로 수행 (복수 에이전트 병렬) |
| **하는 것** | {paper_root}/ 기존 논문 활용, 부족 자료 ccpaper 자동 수집, 다각도 연구 분석 |
| **하지 않는 것** | 논문 작성(→ccsota), 서베이 생성(→ccsurvey), 문헌 수집만(→ccpaper) |
| **참조 범위** | 현재 프로젝트 `{paper_root}/` + 웹 검색 / 외부 DB 자동 크롤링 안 함 |
| **수정 대상** | 연구 결과 문서 파일 |
| **실행 레벨** | [자동] — 복수 에이전트 병렬 연구 자동 실행 |
| **에이전트 호환** | Codex 권장 — 병렬 서브에이전트 자동 배치 / 다른 에이전트: 연구 단계별 순차 실행 |

## 1. 개요

SOTA(State of the Art)를 항상 비교 기준으로 삼아 특정 분야의 연구를 체계적으로 수행하는 스킬.
`{paper_root}/` 보유 논문을 1차 소스로 활용하고, 부족한 자료는 `ccpaper`로 자동 수집한다.
복수 에이전트를 병렬 호출하여 다각도 연구를 수행한다.

**역할 분리 (oosota와의 관계)**:

| 스킬 | 역할 | 순서 |
|------|------|------|
| **`ccresearch`** | **논문 작성 전 조사** (SOTA 파악, 관련 연구 수집, 갭 분석) | 1단계 |
| `ccsota` | 논문 초안 작성 (ccresearch 결과를 입력으로 활용) | 2단계 |

→ `ccresearch` 산출물(`d{SP}0200_research_*.md`)이 `ccsota`의 related 섹션 입력이 됨.

**핵심 원칙**: 모든 분석은 SOTA 대비 상대적 평가. 절대 수치보다 SOTA와의 격차가 중요.

**지원 도메인**:

| 플래그 | 도메인 | 주요 소스 |
|--------|--------|----------|
| `--ai` | AI/ML | ArXiv, Papers With Code, NeurIPS/ICML/ICLR/CVPR |

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccresearch help` | 서브명령어 목록 표시 |
| `ccresearch version` | 스킬 버전 정보 (v02) |
| `ccresearch status` | 현재 연구 문서 목록, 보유 논문 현황, 도메인 현황 |
| `ccresearch check` | references/checklist.md 기반 체크 및 리포팅 |
| `ccresearch run` | 연구 수행 실행 |
| `ccresearch show checklist` | 역할 수행 체크리스트 표시 |
| `ccresearch add checklist "항목"` | 체크리스트 항목 추가 |
| `ccresearch run [topic]` | 종합 연구 수행 → 연구 문서 생성 |
| **`ccresearch run this`** | **직전 연구 주제 계속** (→ common_guide.md §9) |
| `ccresearch sota [topic]` | SOTA 현황만 조사 (빠른 스냅샷) |
| `ccresearch compare [topic]` | 주요 접근법 SOTA 비교 분석 |
| `ccresearch trend [topic]` | 연구 트렌드 및 방향성 분석 |
| `ccresearch gap [topic]` | SOTA 대비 연구 갭 분석 |

**도메인 플래그** (모든 서브명령어에 적용):

| 플래그 | 설명 |
|--------|------|
| `--ai` | AI/ML 분야 연구 수행 |

**공통 옵션**:

| 옵션 | 설명 |
|------|------|
| `--output [파일]` | 출력 파일 경로 지정 |
| `--depth [basic\|deep]` | 분석 깊이 (기본: basic) |
| `--year [N]` | 최근 N년 논문만 포함 (기본: 3) |
| `--no-download` | ccpaper 자동 다운로드 비활성화 |
| `--dry-run` | 계획만 출력, 실행 안 함 |

## 3. 논문 소스 체계

### 3.1 1차 소스: {paper_root}/ 보유 논문

`1_oais/03_paper/` 내 기존 논문을 최우선으로 활용한다.

> 코드 예시: references/guide.md 참조

**활용 우선순위**:

| 순위 | 파일 | 속도 |
|------|------|:----:|
| 1 | `*_서머리.md` | 빠름 |
| 2 | `*_전문(한글).md` | 보통 |
| 3 | `*_전문(영어).md` | 보통 |
| 4 | `*.pdf` | 느림 |

### 3.2 2차 소스: ccpaper 자동 수집

보유 논문으로 부족할 때 `ccpaper`를 호출하여 자동 다운로드한다.

**트리거 조건**:
- 주제 관련 보유 논문 5편 미만
- SOTA Top-3 논문이 보유 목록에 없음
- 최근 1년 논문이 없음

**ccpaper 호출 방식**: `ccpaper run --lang en [topic 키워드]`

### 3.3 3차 소스: 웹 실시간 조사

`document-specialist` 에이전트가 Papers With Code, ArXiv, 학회 사이트를 실시간 검색.

## 4. 워크플로우

### 4.1 run 워크플로우 (종합 연구)

> 코드 예시: references/guide.md 참조

### 4.2 sota 워크플로우 (빠른 스냅샷)

> 코드 예시: references/guide.md 참조

### 4.3 compare 워크플로우

> 코드 예시: references/guide.md 참조

## 5. 에이전트 매핑

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 논문 스캔 | `Explore` | haiku | {paper_root}/ 관련 논문 탐색 | O |
| 논문 수집 | `ccpaper` (스킬 호출) | - | 부족 논문 자동 다운로드 | - |
| SOTA 웹 조사 | `document-specialist` | sonnet | ArXiv, PWC, 학회 검색 | O |
| 논문 심층 분석 | `academic-researcher` | sonnet | 서머리/전문 분석 | O |
| 성능 비교 | `data-analyst` | sonnet | 벤치마크 수치 분석 | O |
| 결과 통합 | `task-executor` | sonnet | 연구 문서 작성 | - |
| 품질 검증 | `ccqa` | sonnet | 연구 완결성 검토 | - |

**병렬 실행 구성**:

> 코드 예시: references/guide.md 참조

## 6. 도메인별 SOTA 조사 방법

### 6.1 AI 도메인 (`--ai`)

**SOTA 소스 우선순위**:

| 순위 | 소스 | 내용 |
|------|------|------|
| 1 | Papers With Code | 벤치마크 리더보드, 공식 구현 |
| 2 | ArXiv (cs.LG, cs.CV, cs.CL) | 최신 프리프린트 |
| 3 | NeurIPS/ICML/ICLR/CVPR/ECCV | 주요 학회 채택 논문 |
| 4 | GitHub Trending | 실무 도입 모델 |
| 5 | Hugging Face Hub | 공개 모델 성능 |

**SOTA 판단 기준**:

| 유형 | 기준 |
|------|------|
| 성능 SOTA | 주요 벤치마크 최고 점수 |
| 효율 SOTA | 성능/파라미터 비율 최고 |
| 실용 SOTA | 속도/정확도 균형 최고 |
| 경량 SOTA | 모바일/엣지 환경 최고 |

**핵심 벤치마크 (분야별)**:

| 분야 | 벤치마크 |
|------|---------|
| 이미지 분류 | ImageNet Top-1, ImageNet-21K |
| 객체 탐지 | COCO mAP |
| 이미지 분할 | COCO Panoptic, ADE20K |
| NLP | GLUE, SuperGLUE, MMLU |
| 코드 생성 | HumanEval, MBPP |
| 멀티모달 | VQA, MMMU |

## 7. 출력 문서 구조

**파일명**: `00_doc/d{SP}0200_research_{topic}.md` (기본)

> 코드 예시: references/guide.md 참조

## 8. SOTA 비교 원칙

| 원칙 | 설명 |
|------|------|
| 공정 비교 | 동일 벤치마크, 동일 학습 조건 기준 |
| 최신성 | 6개월 이내 논문은 항상 확인 |
| 재현성 | 공식 구현/공개 코드 존재 여부 확인 |
| 실용성 | 학술 성능과 실제 사용 성능 구분 |
| 다면 평가 | 단일 지표 SOTA보다 복합 지표 우선 |
| 보유 우선 | {paper_root}/ 논문은 전문 분석, 웹 논문은 서머리 수준 |

## 9. 관련 문서

| 문서 | 용도 |
|------|------|
| `{paper_root}/11_paper_en/` | 1차 논문 소스 (보유 논문) |
| `.agents/skills/ccpaper/SKILL.md` | 논문 자동 수집 (2차 소스) |
| `.agents/skills/ccsurvey/SKILL.md` | 보유 논문 서베이 (연동 가능) |
| `.agents/skills/ccsota/SKILL.md` | **다음 단계**: ccresearch 결과 → 논문 초안 작성 |
| `00_doc/d{SP}0200_research_*.md` | 연구 결과 문서 (ccsota 입력) |
| `.agents/skills/ccresearch/references/guide.md` | 도메인별 상세 가이드 |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- QMD-REF:START -->

## QMD 마크다운 검색 (문서 내용 탐색 시)

> 마크다운 문서 **내용**을 찾을 때는 Glob/Grep 대신 **`mcp__qmd__query`** 우선 사용.
> qmd 미가동 시 Glob/Grep 폴백. 자세한 기준: `.codex/guides/common_guide.md §10`

| 도구 | 적합한 상황 |
|------|-----------|
| `mcp__qmd__query` (lex) | 키워드·문서번호·용어 검색 |
| `mcp__qmd__query` (vec) | 자연어 의미 검색 |
| `Glob` | 파일 경로 패턴 검색 |
| `Grep` | 코드·특정 문자열 검색 |

**인덱싱**: `ccstart run` 시 `qmd update` 자동 실행 / 최초: `qmd collection add . --name {프로젝트명}`

<!-- QMD-REF:END -->

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

