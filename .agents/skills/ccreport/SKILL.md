---
name: ccreport
description: "공통: `.claude/guides/common_guide.md` | 가이드: `.claude/skills/ccreport/references/guide.md` | Word: `.claude/skills/ooword/SKILL.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

> 공통: `.claude/guides/common_guide.md` | 가이드: `.claude/skills/ccreport/references/guide.md` | Word: `.claude/skills/ooword/SKILL.md`

데이터 소스 기반 리포트 생성. 템플릿 렌더링, 다중 포맷(MD/PDF/PPTX) 지원.

> **Word 문서 생성**: `.claude/skills/ooword/SKILL.md` 스킬 참조 (word, quotation 기능 분리됨)

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 데이터 소스 기반 리포트 생성 (MD/PDF/PPTX 다중 포맷) |
| **하는 것** | 데이터 로드, 템플릿 렌더링, MD·PDF·PPTX 포맷 출력 |
| **하지 않는 것** | Word 문서(→ooword), 학술 논문(→oosota), PPT 노트(→ooppt) |
| **참조 범위** | 현재 프로젝트 내부 데이터 파일·템플릿 / 외부 데이터 서비스 자동 연동 안 함 |
| **수정 대상** | 리포트 출력 파일 (MD/PDF/PPTX) |
| **실행 레벨** | [반자동] — 데이터 소스·포맷 확인 후 생성 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 기반 변환 라이브러리 자동 실행 / 다른 에이전트: pandoc·weasyprint 수동 실행 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccreport help` | 서브명령어 목록 표시 |
| `ccreport version` | 스킬 버전 정보 (v12) |
| `ccreport status` | 서브명령어 리스트, 현재 상태 |
| `ccreport check` | references/checklist.md 기반 체크 및 리포팅 |
| `ccreport run` | 리포트 생성 실행 |
| `ccreport show checklist` | 역할 수행 체크리스트 표시 |
| `ccreport add checklist "항목"` | 체크리스트 항목 추가 (스킬 점검용, C계열) |
| `ccreport add reviewlist "항목"` | 논문 교정 체크리스트 항목 추가 (P계열) |
| `run` | 신규 리포트 생성 |
| `write` | **논문 작성/다듬기** (연구자 모드) |
| `pdf` | Markdown -> PDF 변환 |
| `pdf --pandoc` | Markdown -> PDF (LaTeX 수식 + mermaid 지원) |
| `update` | 기존 리포트 업데이트 |
| `list` | 리포트 목록 조회 |
| `algorithm` | **알고리즘 코드 분석** 문서 자동 생성 (ps*.py -> d*.md) |
| ~~`review`~~ | **`oosota review`로 이관됨**. 논문 교정은 `oosota review` 사용 (paper_quality_checklist.md 통합) |

## write 서브명령어 (논문 작성)

연구자 관점에서 논문을 작성하고 다듬는 스킬.

### write 사용법

```bash
ccreport write <file> --section "3.1 아키텍처 개요"
ccreport write <file> --refine
ccreport write <file> --review
```

### write 옵션

| 옵션 | 설명 |
|------|------|
| `--section <name>` | 특정 섹션 작성/확장 |
| `--refine` | 기존 내용 다듬기 (문체, 명확성, 논리) |
| `--review` | 전체 검토 및 개선점 제안 |
| `--style <type>` | 문체 지정 (academic, technical, survey) |
| `--lang <code>` | 언어 지정 (ko, en) 기본: ko |

### write 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 |
|------|---------|------|------|
| 분석 | academic-researcher | sonnet | 논문 구조, 선행연구 분석 |
| 작성 | task-executor + scribe | sonnet / haiku | 연구자 관점 글쓰기 |
| 검토 | task-checker | sonnet | 논리적 일관성, 학술적 정확성 검증 |

### write 작성 원칙

| 원칙 | 설명 |
|------|------|
| 객관성 | 주관적 표현 지양, 근거 기반 서술 |
| 명확성 | 모호한 표현 제거, 정확한 용어 사용 |
| 논리성 | 섹션 간 논리적 흐름 유지 |
| 인용 | 주장에 대한 적절한 참고문헌 연결 |

## algorithm 서브명령어 (알고리즘 코드 분석)

알고리즘/이미지 처리 스크립트(ps*.py)를 분석하여 문서(d*.md)를 자동 생성.

### algorithm 사용법

```bash
ccreport algorithm <script_path>
ccreport algorithm <script_path> --doc-id d6310
ccreport algorithm <script_path> --output 00_doc/sp00/d6310_nr_iqas.md
```

### algorithm 옵션

| 옵션 | 설명 |
|------|------|
| `<script_path>` | 분석할 스크립트 경로 (필수) |
| `--doc-id <id>` | 문서 번호 (예: d6310) |
| `--output <path>` | 출력 파일 경로 |
| `--include-lib` | 라이브러리/함수 정보 섹션 포함 (기본: 포함) |
| `--no-lib` | 라이브러리/함수 정보 섹션 제외 |

### algorithm 분석 항목

| 항목 | 설명 |
|------|------|
| 개요 | 목적, 주요 특징, 처리 단계 |
| 실행 방법 | 기본 실행, 명령행 옵션, 실행 예시 |
| 설정 | CONFIG 딕셔너리 분석 |
| 기능/메트릭 | 주요 기능 또는 메트릭 상세 (해당 시) |
| 출력 파일 | 출력 디렉토리, 파일 목록, 구조 |
| 코드 구조 | 핵심 함수, 로컬 함수, 의존성, 처리 흐름 |
| 참고사항 | 주의사항, 지원 형식 |
| 라이브러리 정보 | 사용 라이브러리 및 함수 상세 |

> **필수**: `.claude/skills/ccreport/templates/ooreport_algorithm.md` 템플릿 구조를 따를 것

### algorithm 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 |
|------|---------|------|------|
| 분석 | Explore | haiku | 스크립트 구조, 의존성 분석 |
| 수집 | task-executor | sonnet | CONFIG, 함수, 처리 흐름 추출 |
| 생성 | task-executor + scribe | sonnet / haiku | 템플릿 기반 문서 생성 |
| 검증 | task-checker | sonnet | 문서 완성도 검증 |

## 서브에이전트 (run/update)

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 수집 | Explore | haiku | O |
| 생성 | task-executor | sonnet | O |
| 검증 | task-checker | sonnet | - |

## 의존성

| 패키지 | 용도 | 필수 |
|--------|------|:----:|
| Jinja2 | 템플릿 렌더링 | O |
| markdown | MD 처리 | O |
| python-pptx | PPTX 출력 | - |
| weasyprint | PDF 출력 | - |
| pandoc | LaTeX 수식 변환 (PDF) | - |
| mermaid-cli | mermaid 다이어그램 -> PNG 변환 | - |

## 관련 경로

| 구분 | 경로 |
|------|------|
| 데이터 소스 | `00_doc/d{SP}*.md` |
| 출력 | 원본과 동일 폴더 (확장자만 변경) |
| 템플릿 | `.claude/skills/ccreport/templates/ooreport_*.md` |
| 스크립트 | `.claude/skills/ccreport/scripts/ooreport_*.py` |
| 가이드 | `.claude/skills/ccreport/references/guide.md` |

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

