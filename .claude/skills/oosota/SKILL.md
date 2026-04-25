---
name: oosota
description: "SOTA급 학술 논문 작성 스킬. 'oosota', '논문 작성', '학술 논문', '저널 논문', 'paper draft', '논문 초안', 'IEEE', 'Elsevier', 'Springer' 등을 요청할 때 트리거된다"
model: opus
metadata:
  version: "v01"
  category: "content"
---

> 공통: `.claude/guides/common_guide.md` | 에이전트 참조: `agents.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 실험 결과 기반 SOTA급 저널 논문 초안 작성 (IEEE/Elsevier/Springer 포맷) |
| **하는 것** | 실험 데이터 분석, 논문 구조 생성, Abstract·Introduction·Conclusion 작성 |
| **하지 않는 것** | 연구 수행(→ooresearch), 문헌 수집(→oopaper), 서베이 작성(→oosurvey) |
| **참조 범위** | 현재 프로젝트 내부 파일 (실험 데이터) + 웹 참고문헌 검색 |
| **수정 대상** | 논문 초안 MD 파일 |
| **실행 레벨** | [반자동] — 실험 데이터 확인 후 작성 |
| **에이전트 호환** | Claude Code 권장 — academic-researcher 에이전트 연동 / 다른 에이전트: 연구 컨텍스트를 직접 제공하여 논문 작성 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 개요

실험 결과 문서(d0012, d3xxx, d4xxx 등)를 분석하여 IEEE/Elsevier/Springer 수준의 학술 논문 초안을 작성하는 스킬.

**역할 분리 (파이프라인):**

| 단계 | 스킬 | 역할 |
|------|------|------|
| 1 | `oopaper` | 참고 논문 수집/서머리/번역 |
| 2 | `ooresearch` | SOTA 조사, 관련 연구 분석, 갭 파악 → `d{SP}0200_research_*.md` |
| 3 | **`oosota`** | **ooresearch 결과 + 실험 데이터 → 논문 초안 작성** |
| 4 | `ooreport` | 논문 MD → PDF/DOCX 변환 (투고용) |

> `oosota`는 SOTA 조사를 직접 수행하지 않음. `ooresearch` 산출물을 related 섹션 입력으로 활용.

**핵심 원칙:**
- 실험 데이터(d3xxx/d4xxx)를 1차 소스로 활용
- ooresearch 산출물(`d{SP}0200_research_*.md`)을 related/discussion 섹션에 직접 활용
- SOTA 대비 기여점 중심으로 논문 구성
- 수치/테이블/수식은 실험 문서에서 직접 추출 (임의 생성 금지)

---

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oosota help` | 서브명령어 목록 표시 |
| `oosota version` | 스킬 버전 정보 (v01) |
| `oosota show checklist` | 역할 수행 체크리스트 표시 |
| `oosota add checklist "항목"` | 체크리스트 항목 추가 |
| `oosota status` | 현재 논문 초안 현황, 실험 문서 목록 |
| `oosota init` | 논문 구조 분석 → 섹션 골격 생성 (d{SP}6200_paper_draft.md) |
| `oosota run` | 전체 논문 초안 생성/업데이트 |
| `oosota section [섹션]` | 특정 섹션만 작성/수정 |
| `oosota review` | **논문 종합 교정** (논리 흐름, SOTA 비교, 일관성 + P01~P21 교정 체크리스트 통합). 기준: `paper_quality_checklist.md` 전체 적용 |
| `oosota table` | 실험 결과 테이블 자동 생성/업데이트 |
| `oosota figures` | Figure 목록 및 캡션 계획 생성 |
| `oosota submit [저널]` | 투고 저널 형식 검토 및 체크리스트 |
| `oosota diff [v1] [v2]` | 논문 버전 간 변경 내용 비교 |
| `oosota check` | 논문 품질 체크리스트 점검 (섹션 구조, 표 도입문 누락, 수치 일관성, 내부 마커 잔존 등) |
**섹션 지정** (`oosota section` 대상):

| 섹션 | 내용 |
|------|------|
| `abstract` | 초록 (문제/방법/결과/기여 4문단) |
| `intro` | 서론 (배경, 문제, 기여점, 논문 구성) |
| `related` | 관련 연구 (SOTA 흐름, 본 연구 위치) |
| `method` | 방법론 (아키텍처, 학습 전략, 수식) |
| `experiments` | 실험 (데이터셋, 지표, 비교 실험, 절제 연구) |
| `discussion` | 토론 (결과 해석, 한계, 향후 연구) |
| `conclusion` | 결론 |

**저널 옵션** (`oosota submit` 대상):

| 저널 | 약어 |
|------|------|
| Automation in Construction | `aic` |
| IEEE Transactions on Image Processing | `tip` |
| Pattern Recognition | `pr` |
| Expert Systems with Applications | `eswa` |
| Engineering Applications of AI | `eaai` |

---

## 3. 소스 문서 체계

> 코드 예시: references/guide.md 참조

---

## 4. 워크플로우

> 코드 예시: references/guide.md 참조

### 4.0 init — 논문 구조 초기화
### 4.1 run — 전체 논문 작성
### 4.2 section — 섹션별 작성/수정
### 4.3 review — 논문 종합 교정

> `ooreport review`(P01~P21) 기능을 통합. 기준 문서: `paper_quality_checklist.md` 전체 카테고리 적용.

### 4.4 check — 논문 품질 체크

> 체크 기준: `.claude/skills/oosota/paper_quality_checklist.md` (S/M/N/A/C/R/T 7개 카테고리, Critical/Warning/Info 3등급)

### 4.5 submit — 저널 투고 준비

---

## 5. 에이전트 매핑

| 단계 | 에이전트 | 모델 | 병렬 |
|------|----------|------|:----:|
| 실험 분석 | `data-analyst` | sonnet | O |
| 관련 연구 | `academic-researcher` | sonnet | O |
| 섹션 작성 | `oh-my-claudecode:writer` | haiku | O |
| 영문 교정 | `oh-my-claudecode:code-simplifier` | sonnet | - |
| 품질 검토 | `oh-my-claudecode:quality-reviewer` | sonnet | - |

---

## 6. 논문 품질 기준

| 항목 | 기준 |
|------|------|
| Abstract | 문제/방법/결과/기여 4요소 포함 |
| 기여점 | 3개 이상, 구체적 수치로 명시 |
| SOTA 비교 | 최신 3년 이내 논문 포함 |
| 테이블 | 모든 수치는 실험 문서에서 추출 (추정 금지) |
| 참고문헌 | 20개 이상, IEEE 스타일 번호 리스트 (테이블 형식 금지) |
| 영문 수준 | Native-level academic English |
| 섹션 구조 | 상위 섹션(###)은 하위 섹션(####) 나열 전에 5문장 이내로 해당 섹션의 목적·범위·전개 방향을 안내. 표(Table)만 단독으로 등장하는 섹션 금지; 반드시 도입 문장 포함 |

---

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 7. 관련 문서

`ooresearch`(SOTA 조사) | `oopaper`(문헌 수집) | `ooreport`(PDF 변환) | `d{SP}0001`(PRD) | `d{SP}0012`(실험결과)

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

