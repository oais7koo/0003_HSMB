---
name: oohwp
description: "한글(HWPX) 문서 생성/읽기/편집 스킬 'oohwp', '한글 문서', 'hwpx 생성', '공문 작성', '아래한글' 등을 요청할 때 트리거된다"
metadata:
  version: "v02"
  category: "content"
---

> 공통: `.claude/guides/common_guide.md` | 스크립트: `.claude/skills/oohwp/scripts/` | 레퍼런스: `.claude/skills/oohwp/references/hwpx-format.md`

HWPX(아래한글) 문서를 XML-first 방식으로 생성/편집/읽는 스킬.
의존성: `lxml` (`uv run --with lxml`)

## 문서 이력 관리
- v02 2026-04-19 — validate → check 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 한글(HWPX) 문서를 XML-first 방식으로 생성·편집·읽기 |
| **하는 것** | HWPX 파일 생성/편집, 공문 작성, HWP→MD 읽기 |
| **하지 않는 것** | Word 문서(→ooword), PDF 변환(→oopdf), 한글 앱 직접 제어 |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 한글 서버 자동 연결 안 함 |
| **수정 대상** | `*.hwpx` 파일 |
| **실행 레벨** | [반자동] — 문서 구조 확인 후 생성 |
| **에이전트 호환** | Claude Code 권장 — `uv run --with lxml` 자동 실행 / 다른 에이전트: lxml 설치 후 수동 스크립트 실행 |

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oohwp help` | 서브명령어 목록 표시 |
| `oohwp version` | 스킬 버전 정보 (v01) |
| `oohwp status` | 서브명령어 리스트, 현재 상태 |
| `oohwp check --checklist` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oohwp build` | 템플릿 기반 HWPX 생성 |
| `oohwp extract` | HWPX에서 텍스트 추출 |
| `oohwp check` | HWPX 구조 검증 (구 `validate`) |
| `oohwp analyze` | 기존 HWPX 구조 분석 |
| `oohwp edit` | 기존 HWPX 편집 (unpack → 수정 → pack) |
| `oohwp convert <input.hwp> [output.hwpx]` | HWP → HWPX 변환 (pyhwpx, Windows + 한글 필요) |
| `oohwp convert --batch <dir>` | 폴더 내 모든 .hwp 일괄 변환 |
| `oohwp pagecount <dir>` | 폴더 내 문서 페이지 카운트 (HWP/HWPX/PDF 자동 감지) |

## 워크플로우

### 1. 신규 문서 생성 (`build`)

> 코드 예시: references/guide.md 참조

**사용 가능한 템플릿:**
| 템플릿 | 설명 |
|--------|------|
| `gonmun` | 공문 (기본) |
| `report` | 보고서 |
| `minutes` | 회의록 |
| `proposal` | 제안서 |

**Claude 직접 생성 방식:**
1. `references/hwpx-format.md` 참조하여 `section0.xml` 직접 작성
2. `examples/sample_section0.xml`, `examples/sample_header.xml` 참고
3. `build_hwpx.py --section <파일>` 으로 빌드

### 2. 텍스트 추출 (`extract`)

> 코드 예시: references/guide.md 참조

### 3. 구조 검증 (`check`)

> 코드 예시: references/guide.md 참조

### 4. 기존 문서 분석 (`analyze`)

> 코드 예시: references/guide.md 참조

### 5. 기존 문서 편집 (`edit`)

> 코드 예시: references/guide.md 참조

### 6. HWP → HWPX 변환 (`convert`)

> Windows + 아래한글 설치 필요. 의존성: `pyhwpx`

> 코드 예시: references/guide.md 참조

### 7. 페이지 카운트 (`pagecount`)

> Windows + 아래한글 설치 필요 (HWP/HWPX 변환 시). 의존성: `pyhwpx`, `pypdf`, `openpyxl`

> 코드 예시: references/guide.md 참조

**동작:**
1. 대상 폴더 내 파일 타입 자동 감지 (hwp > hwpx > pdf)
2. `<폴더>/pagecount/` 하위 구조 생성
   - `hwpx/` : HWP→HWPX 변환 (원본이 .hwp인 경우만)
   - `pdf/` : PDF 변환 결과 (순번 prefix: `01_파일명.pdf`)
3. `pagecount/pagecount.xlsx` 생성 (No, 파일명, 페이지수, 합계)

**파이프라인 (파일 타입별):**
| 원본 | 변환 과정 |
|------|----------|
| `.hwp` | hwp → pagecount/hwpx/ → pagecount/pdf/ → xlsx |
| `.hwpx` | hwpx → pagecount/pdf/ → xlsx |
| `.pdf` | pdf → pagecount/pdf/ (순번 복사) → xlsx |

## 핵심 HWPX 규칙

1. **HWPX만 지원** — `.hwp`(구형 바이너리) 불가
2. **secPr 필수** — section0.xml 첫 문단 첫 run에 반드시 포함
3. **mimetype 순서** — ZIP 첫 번째 엔트리, ZIP_STORED (비압축)
4. **네임스페이스 보존** — `hp:`, `hs:`, `hh:`, `hc:` 접두사
5. **빈 줄** — `<hp:t/>` self-closing tag 사용
6. **검증 필수** — 생성 후 반드시 `check`(validate.py) 실행

## 예제 파일

| 파일 | 설명 |
|------|------|
| `examples/sample_section0.xml` | 섹션 XML 예제 (표, 빈줄, 텍스트) |
| `examples/sample_header.xml` | 헤더 XML 예제 (폰트, 스타일) |
| `examples/*.hwpx` | 결과 예제 파일들 |

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 문서 작성/편집 | `task-executor` | sonnet | - |
| 구조 검증 | `task-checker` | sonnet | - |

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

## 관련 문서

- `references/hwpx-format.md` — OWPML XML 상세 레퍼런스
- `templates/` — 공문/보고서/회의록/제안서 XML 템플릿
