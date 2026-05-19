---
name: ccpdf
description: "공통: `.codex/guides/common_guide.md` | 관련: `.agents/skills/ccreport/SKILL.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# ccpdf - PDF 변환/처리 스킬

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | Markdown→PDF 변환 및 PDF→이미지 변환 |
| **하는 것** | MD→PDF 변환(weasyprint/pandoc), PDF→PNG 변환(PyMuPDF) |
| **하지 않는 것** | Word 변환(→ccword), PPT 생성(→ccppt), 리포트 생성(→ccreport) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 PDF 서비스 자동 연동 안 함 |
| **수정 대상** | 출력 `*.pdf`, `*.png` 파일 |
| **실행 레벨** | [자동] — 변환 자동 실행 |
| **에이전트 호환** | Codex 권장 — weasyprint/pandoc/PyMuPDF `uv run` 자동 실행 / 다른 에이전트: 해당 CLI 도구 수동 실행 필요 |

## 문서 이력 관리
- v02 2026-04-02 — convert --image 추가 (PDF→이미지 변환, PyMuPDF)
- v01 2026-03-21 — 최초 생성 (ccreport pdf 기능 분리)

> 공통: `.codex/guides/common_guide.md` | 관련: `.agents/skills/ccreport/SKILL.md`

## 1. 개요

PDF 변환/처리 통합 스킬. `ccreport pdf`에서 분리.

- **weasyprint 모드**: MD→PDF 빠른 변환, 한국어 지원
- **pandoc 모드**: MD→PDF LaTeX 수식 + mermaid 다이어그램 지원
- **convert --image**: PDF→이미지 변환 (PyMuPDF)

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccpdf help` | 서브명령어 목록 표시 |
| `ccpdf version` | 스킬 버전 정보 (v02) |
| `ccpdf show checklist` | 역할 수행 체크리스트 표시 |
| `ccpdf add checklist "항목"` | 체크리스트 항목 추가 |
| `ccpdf status` | 서브명령어 리스트, 현재 상태 |
| `ccpdf run <file>` | Markdown → PDF 변환 (weasyprint) |
| **`ccpdf run this`** | **직전 작업 PDF 변환** (→ common_guide.md §9) |
| `ccpdf run <file> --pandoc` | Markdown → PDF 변환 (pandoc, LaTeX 수식 지원) |
| `ccpdf convert <file>` | PDF → 이미지 변환 (PyMuPDF, 기본 PNG) |
| `ccpdf check` | 의존성 설치 상태 확인 |

실행: `uv run python .agents/skills/ccpdf/scripts/oopdf_run.py [args]`

## 3. 사용 예시

```bash
ccpdf run 00_doc/sp00/d0001_prd.md
ccpdf run 00_doc/sp00/d0001_prd.md --pandoc
ccpdf run report.md --output output/report.pdf
ccpdf convert document.pdf
ccpdf convert document.pdf --dpi 300 --format jpg
ccpdf convert document.pdf --output ./images/
```

## 4. 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--pandoc` | pandoc 엔진 사용 (LaTeX 수식 지원) | false |
| `--output <path>` | 출력 파일/디렉토리 경로 | 입력파일명.pdf / 입력파일명/ |
| `--style <css>` | 커스텀 CSS 파일 경로 (run 전용) | 내장 스타일 |
| `--image` | PDF→이미지 변환 (convert 전용) | - |
| `--dpi <n>` | 이미지 해상도 (convert 전용) | 200 |
| `--format <fmt>` | 이미지 포맷 png/jpg (convert 전용) | png |

## 5. 의존성

| 패키지 | 용도 | 필수 |
|--------|------|:----:|
| markdown | MD → HTML 변환 | O (run) |
| weasyprint | HTML → PDF 변환 | O (run 기본) |
| pymupdf | PDF → 이미지 변환 | O (convert --image) |
| pandoc | MD → PDF 변환 (수식) | - (run --pandoc) |
| xelatex/pdflatex | PDF 엔진 | - (run --pandoc) |

```bash
uv pip install markdown weasyprint pymupdf
```

## 6. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 변환 | 직접 처리 | - | 스크립트 실행 | - |

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| `.agents/skills/ccreport/SKILL.md` | 리포트 생성 (run/write/algorithm) |
| `.agents/skills/ccword/SKILL.md` | Word 문서 생성 |

> 체크리스트: `.agents/skills/ccpdf/references/checklist.md`

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

