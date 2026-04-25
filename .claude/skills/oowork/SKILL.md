---
name: oowork
description: "범용 문서 작업 워크플로우 엔진. 기술수요조사, 제안서, 보고서, 견적서 등 다단계 문서 작업 프로세스를 정의하고 순차 실행한다. 'oowork', '워크플로우', '프로세스', '기술수요조사', '제안서 작성', '보고서 작성', '견적서' 등을 요청할 때 트리거된다."
---

> 공통: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 기술수요조사·제안서·보고서 등 반복 문서 작업 프로세스를 정의하고 순차 실행 |
| **하는 것** | 워크플로우 프로세스 등록, 단계별 문서 생성, 비텍스트 문서 마크다운 변환 |
| **하지 않는 것** | 코드 개발(→oodev), 논문 작성(→oosota), PPT 생성(→ooppt) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 시스템 자동 포함 안 함 |
| **수정 대상** | 워크플로우 정의 파일, 문서 산출물 |
| **실행 레벨** | [반자동] — 각 단계 완료 확인 후 다음 단계 진행 |
| **에이전트 호환** | 범용 — 문서 생성 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v02 2026-03-27 — extract 서브명령어 추가 (비텍스트 문서 → 마크다운 변환)
- v01 2026-03-26 — status/check 서브명령어 추가

---

## 1. 개요

다단계 **문서 작업** 프로세스를 정의하고 순차 실행하는 범용 워크플로우 엔진.
기술수요조사, 제안서, 보고서, 견적서 등 반복되는 문서 작업을 프로세스로 등록하여 재사용한다.
각 단계는 기존 oo 스킬(oopaper, oosurvey 등)을 호출하거나 직접 작업을 수행한다.

### 스코프 구분

| 영역 | 담당 | 비고 |
|------|------|------|
| 문서 작업 (조사, 기획, 보고서, 제안서, 견적서) | **oowork** | 본 스킬 |
| 코드 개발 (TDD, 구현, Streamlit, 리팩토링) | **oodev** | 개발 관련은 oodev 관할 |

> oostreamlit의 6단계 워크플로우(PRD→설계→구현→검증→리뷰)는 oodev가 담당.
> oowork는 코드가 아닌 문서 산출물 파이프라인만 관할.

### 등록 가능 프로세스 예시

| 프로세스 | 단계 | 상태 |
|---------|------|:----:|
| 기술수요조사 | 논문수집→서베이→기술연구→기술수요→hwpx | 등록 |
| 제안서 작성 | RFP분석→자료수집→기획→기술연구→제안작성 (확장 가능) | 등록 |
| 보고서 작성 | 자료수집→분석→초안→검토→최종본→PDF | 미등록 |
| 견적서 작성 | 요구사항→항목산정→단가→문서화→hwpx | 미등록 |

- 프로세스 정의: `references/processes/{프로세스명}.md`
- 문서 템플릿: `templates/` (아래 참조)
- 상태 추적: `scripts/oowork_run.py`

### 문서 템플릿

| 파일 | 용도 |
|------|------|
| `templates/d0100_개조식 보고서 샘플.md` | 개조식 보고서 작성 샘플 |
| `templates/d0102_논문_보고서_작성방법.md` | 논문/보고서 작성 가이드 |
| `templates/d0103_포스트논문 템플릿.md` | 포스트논문 형식 템플릿 |
| `templates/d0104_보고서샘플.md` | 일반 보고서 샘플 |
| `templates/d0105_소프트웨어등록신청서 샘플.md` | SW 등록 신청서 샘플 |

> 보고서/제안서 작성 시 해당 템플릿을 참고하여 문서 구조 및 형식 결정

### 비텍스트 문서 변환 규칙 (MANDATORY)

> HWP, PDF, DOC 등 비텍스트 문서가 입력으로 주어지면, **반드시 먼저 내용을 추출하여 마크다운(.md)으로 변환**한 후 작업을 시작한다.

| 항목 | 규칙 |
|------|------|
| 대상 | `.hwp`, `.pdf`, `.doc`, `.docx`, `.hwpx` 등 비텍스트 파일 |
| 변환 파일명 | 원본 파일명 유지, 넘버링만 +1 (예: `10_기술사업계획서.hwp` → `11_기술사업계획서.md`) |
| 넘버링 없는 원본 | 폴더 내 첫 번호 +1 할당, 파일명 유지 (예: `기술사업계획서.hwp` → `11_기술사업계획서.md`) |
| 변환 위치 | 원본과 동일 폴더 |
| 변환 후 | 마크다운 파일을 기준으로 작업 진행, 원본은 보존 |
| 중간물 관리 | HWPX 등 변환 중간물은 유지 (재추출 시 사용), 기타 임시파일(txt 등)은 삭제 |

**추출 도구 (형식별):**

| 형식 | 추출 파이프라인 | 스크립트 |
|------|---------------|---------|
| HWP | `pyhwpx`로 HWPX 변환 → PDF 변환 → `pdfplumber` → 구조화 MD | `scripts/hwp_to_md.py` |
| HWPX | `pyhwpx`로 PDF 변환 → `pdfplumber` → 구조화 MD | `scripts/hwp_to_md.py` |
| PDF | `Read`(내장) 또는 `pdfplumber` → .md | 직접 작성 |
| DOC/DOCX | `python-docx` → .md | 직접 작성 |
| PPT/PPTX | PDF로 변환 → PDF 추출 파이프라인 적용 → .md | 직접 작성 |

```bash
# HWP/HWPX → 구조화 마크다운 (자동 넘버링)
uv run python .claude/skills/oowork/scripts/hwp_to_md.py <입력.hwp|hwpx> [출력.md]
```

## 2. 명령어

| 명령어 | 설명 |
|--------|------|
| `oowork help` | 서브명령어 목록 |
| `oowork version` | 버전 정보 (v02) |
| `oowork status` | 서브명령어 리스트, 스킬/문서 상태 |
| `oowork check` | references/checklist.md 기반 체크 및 리포팅 |
| `oowork list` | 등록된 프로세스 목록 |
| `oowork status <프로세스>` | 진행 상태 확인 |
| `oowork run <프로세스> [옵션]` | 프로세스 실행 |
| `oowork add <프로세스명>` | 새 프로세스 등록 (템플릿 생성) |
| `oowork extract <파일경로> [출력경로]` | 비텍스트 문서 → 마크다운 변환 (HWP/HWPX/PDF/DOCX) |

## 3. run 옵션

| 옵션 | 설명 |
|------|------|
| `--topic "주제"` | 작업 주제 (예: "1-3 엣지전처리") |
| `--keywords "k1,k2"` | 검색 키워드 (0단계 논문 수집용) |
| `--step N` | 특정 단계만 실행 |
| `--step N-M` | N에서 M단계 범위 실행 |
| `--workdir 경로` | 작업 디렉토리 (기본: 현재 폴더) |
| `--dry-run` | 실행 없이 계획만 출력 |
| `--resume` | 마지막 중단 지점부터 재개 |

## 4. 실행 워크플로우

> 코드 예시: references/guide.md 참조

## 5. 프로세스 파일 형식

`references/processes/{프로세스명}.md`에 정의.

> 코드 예시: references/guide.md 참조

## 6. 상태 관리

실행: `uv run python .claude/skills/oowork/scripts/oowork_run.py`

상태 파일: `{workdir}/.oowork/{프로세스명}_state.json`

> 코드 예시: references/guide.md 참조

## 7. 검증 규칙

각 단계 완료 시 자동 검증:

| 단계 | 검증 항목 |
|------|---------|
| 논문 수집 | 폴더 생성 확인, 서머리 파일 존재 |
| 서베이 | 서베이 파일 생성, 섹션 구조 확인 |
| 기술연구 | 표준 넘버링, 폴더ID 전수 부여, 참고문헌 테이블 |
| 기술수요 | 양식 준수(40번), 인용 제거, 기호 자연어화 |
| hwpx | 붙여넣기용 txt 생성 |

## 8. 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 논문 수집 | academic-researcher | sonnet | O |
| 서베이 | academic-researcher | sonnet | O |
| 기술연구 | task-executor | sonnet | - |
| 기술수요 | task-executor | sonnet | - |
| 검증 | task-checker | sonnet | - |

## 9. 사용 예시

> 코드 예시: references/guide.md 참조

## 10. 체크리스트

- 공통 규칙: `references/checklist_common.md` (G01~G18, 모든 프로세스 적용)
- 프로세스별 규칙: `references/processes/{프로세스명}_checklist.md` (공통 상속 + 추가 규칙)

각 단계 완료 시 공통 + 프로세스별 체크리스트를 순차 검증.

> 관련: `oopaper`, `oosurvey`, `oocommit`

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

