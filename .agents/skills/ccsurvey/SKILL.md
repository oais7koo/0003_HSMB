---
name: ccsurvey
description: "공통: `.codex/guides/common_guide.md` | 컨텍스트: `.agents/skills/cccontext/SKILL.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

> 공통: `.codex/guides/common_guide.md` | 컨텍스트: `.agents/skills/cccontext/SKILL.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 논문 서베이 및 선행연구 체계적 정리 |
| **하는 것** | 논문 분류·비교표 생성, 연구 동향 분석, 서베이 문서 작성 |
| **하지 않는 것** | 새 논문 작성(→ccsota), 문헌 수집(→ccpaper), 연구 수행(→ccresearch) |
| **참조 범위** | 현재 프로젝트 `03_paper/` 내부 파일 + 웹 검색 보조 |
| **수정 대상** | 서베이 결과 MD 파일 |
| **실행 레벨** | [반자동] — 분석 범위 확인 후 생성 |
| **에이전트 호환** | Codex 권장 — Agent 도구로 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ccskill run 자동)

---

## 1. 개요

> ⚠️ **필수**: run/deeprun 명령 시 반드시 Agent 도구로
> explore(haiku) 논문 목록 스캔 → executor(sonnet) 논문 분석 및 서베이 작성 순서로 위임할 것.
> 논문 전문 직접 읽기 금지 — 메인 컨텍스트 보호.

논문 폴더를 분석하여 연구 주제 관련 서베이 문서를 생성/관리.

- **입력**: 논문 폴더 내 논문 (PDF, 서머리, 전문)
- **출력**: `00_doc/sp00/d0110_survey.md` 서베이 문서
- **연동**: d0001_prd.md (연구 주제), d0004_todo.md (이슈)
- **컨텍스트**: `--sp N` 또는 `cccontext N`

### 1.1 논문 폴더 설정

**.env 파일에서 설정** (권장): `OAIS_PAPER_DIR=../0002_paper/02_paper`

**우선순위**: `--paper-dir` 옵션 > `.env`의 `OAIS_PAPER_DIR` > 기본값 `paper/`

> 코드 예시: references/guide.md 참조

### 1.2 연구 주제 자동 감지

PRD(`00_doc/sp00/d0001_prd.md`)에서 연구 주제 및 키워드를 자동 추출. 수동 설정: `--topic`, `--keywords` 옵션.

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccsurvey help` | 서브명령어 목록 표시 |
| `ccsurvey version` | 스킬 버전 정보 (v07) |
| `ccsurvey status` | paper 폴더 현황, d0110 상태, 미분석 논문 |
| `ccsurvey check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ccsurvey show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ccsurvey add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ccsurvey list` | 논문 목록 (paper_list.md 참조, 없으면 폴더 스캔) |
| `ccsurvey run` | 서머리 기반 분석 -> d0110_survey.md 생성 |
| `ccsurvey deeprun` | PDF 포함 정밀 분석 -> d0110_survey.md 생성 |
| `ccsurvey compare` | 논문 간 비교 분석 (모델, 성능, 방법론) |
| `ccsurvey cite` | 인용 형식 생성 (APA, IEEE, BibTeX) |
| `ccsurvey add [폴더]` | 새 논문 추가 분석 -> 기존 d0110에 병합 |

### 2.1 공통 옵션

| 옵션 | 설명 |
|------|------|
| `--paper-dir` | 논문 폴더 경로 오버라이드 |
| `--topic` | 연구 주제 오버라이드 |
| `--keywords` | 키워드 오버라이드 (콤마 구분) |
| `--threshold` | 관련성 임계값 (기본 2) |
| `--output` | 출력 파일 경로 지정 |
| `--dry-run` | 실행 없이 계획만 출력 |
| `--verbose` | 상세 로그 출력 |

### 2.2 list 옵션

| 옵션 | 설명 |
|------|------|
| `--all` | 전체 목록 |
| `--pending` | 미완료만 |
| `--recent N` | 최근 N개 |
| `--search 키워드` | 제목 검색 |

## 3. paper 폴더 구조

### 3.1 지원 구조

**구조 A**: `{YYMMDD}-{HHMM}/` 날짜-시간 코드 (권장) | **구조 B**: 논문명 기반 | **구조 C**: 단순 PDF

> 코드 예시: references/guide.md 참조

### 3.2 파일 우선순위

| 순서 | 패턴 | 분석 대상 |
|------|------|:--------:|
| 1 | `*서머리*.md`, `summary*.md` | run, deeprun |
| 2 | `*전문(한글)*.md` | run, deeprun |
| 3 | `*전문(영어)*.md` | deeprun |
| 4 | `*.pdf` | deeprun |

## 4. run 워크플로우

### 4.1 핵심 기능

1. 사용자 지정 주제로 논문 폴더 검색
2. 관련 논문의 선행연구 내용 정리
3. 지정 문서에 결과 저장 (기본: `00_doc/sp00/d0110_survey.md`)
4. 추가 연구 분석이 필요한 논문/주제 제안

### 4.2 실행 흐름

> 코드 예시: references/guide.md 참조

### 4.3 관련성 판단

| 카테고리 | 예시 키워드 | 가중치 |
|----------|------------|:------:|
| 핵심 기술 | PRD에서 추출한 키워드 | 2.0 |
| 모델/아키텍처 | U-Net, ResNet, Transformer | 1.5 |
| 방법론 | segmentation, detection, attention | 1.0 |
| 도메인 | image, vision, NLP | 0.5 |

기본 임계값: 2.0

### 4.4 출력 형식

> 코드 예시: references/guide.md 참조

## 5. deeprun 워크플로우

run의 모든 기능 + 추가 분석:

| 항목 | 설명 |
|------|------|
| 모델 아키텍처 | 상세 구조, 레이어, 파라미터 수 |
| 실험 설정 | 데이터셋, 하이퍼파라미터, 학습 전략 |
| 성능 수치 | 정량적 메트릭 (IoU, F1, mAP 등) |
| 핵심 수식 | Loss function, 핵심 알고리즘 |
| Figure/Table | 주요 시각자료 분석 |
| 한계점 | 논문에서 언급한 한계 |

## 6. compare 워크플로우

출력: 성능 비교표, 아키텍처 비교표, 추천 (성능/경량화/균형)

> 코드 예시: references/guide.md 참조

## 7. cite 워크플로우

지원 형식: apa, ieee, bibtex, mla

> 코드 예시: references/guide.md 참조

## 8. d0004 연동

| 유형 | 분류 | 설명 |
|------|------|------|
| 서머리 누락 | DOCS | 논문에 서머리 파일 없음 |
| PDF 분석 실패 | BUGFIX | PDF 읽기/파싱 오류 |
| 관련성 미판단 | MISC | 키워드 매칭 불가 |

ID 규칙: `P` Prefix (예: P001, P002)

## 9. 병렬 처리

### 서브에이전트 매핑

| 작업 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 서머리 분석 | Explore | haiku | O |
| 전문 분석 | academic-researcher | sonnet | O |
| PDF 분석 | data-analyst | sonnet | O |
| 문서 생성 | task-executor | sonnet | - |

## 10. 완료 조건

| 조건 | 검증 방법 |
|------|----------|
| d0110 생성/업데이트 | 파일 존재 및 버전 증가 |
| 관련 논문 전체 분석 | 참고 목록에 누락 없음 |
| d0004 이슈 등록 | 분석 불가 논문 기록 |
| PRD 연동 확인 | 연구 주제 일치 |

> **관련 문서**: `00_doc/sp00/d0001_prd.md` | `00_doc/sp00/d0110_survey.md` | `00_doc/sp00/d0004_todo.md` | `.agents/skills/ccsurvey/references/guide.md`

## 11. 관련 문서

| 문서 | 용도 |
|------|------|
| `00_doc/sp00/d0001_prd.md` | 연구 주제 및 키워드 소스 |
| `00_doc/sp00/d0110_survey.md` | 서베이 출력 문서 |
| `00_doc/sp00/d0004_todo.md` | 분석 불가 논문 이슈 등록 |
| `.agents/skills/ccsurvey/references/guide.md` | 상세 가이드 |
| `.agents/skills/ccpaper/SKILL.md` | 논문 수집/정리 (입력 소스) |

## 12. 사용 예시

> 코드 예시: references/guide.md 참조

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

