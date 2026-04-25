# oopdf Tutorial

> PDF 변환/처리 스킬 | 버전: v02 | 카테고리: content

## 1. 이 스킬은 왜 필요한가?


**이런 상황에서 사용합니다:**
- **weasyprint 모드**: MD→PDF 빠른 변환, 한국어 지원
- **pandoc 모드**: MD→PDF LaTeX 수식 + mermaid 다이어그램 지원
- **convert --image**: PDF→이미지 변환 (PyMuPDF)

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oopdf run

# 상태 확인
oopdf status

# 도움말
oopdf help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oopdf help` | 서브명령어 목록 표시 |
| `oopdf version` | 스킬 버전 정보 (v02) |
| `oopdf show checklist` | 역할 수행 체크리스트 표시 |
| `oopdf add checklist "항목"` | 체크리스트 항목 추가 |
| `oopdf status` | 서브명령어 리스트, 현재 상태 |
| `oopdf run <file>` | Markdown → PDF 변환 (weasyprint) |
| **`oopdf run this`** | **직전 작업 PDF 변환** (→ common_guide.md §9) |
| `oopdf run <file> --pandoc` | Markdown → PDF 변환 (pandoc, LaTeX 수식 지원) |
| `oopdf convert <file>` | PDF → 이미지 변환 (PyMuPDF, 기본 PNG) |
| `oopdf check` | 의존성 설치 상태 확인 |

실행: `uv run python .claude/skills/oopdf/scripts/oopdf_run.py [args]`

## 4. 상세 사용법

### 의존성

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

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | Markdown→PDF 변환 및 PDF→이미지 변환 |
| **하는 것** | MD→PDF 변환(weasyprint/pandoc), PDF→PNG 변환(PyMuPDF) |
| **하지 않는 것** | Word 변환(→ooword), PPT 생성(→ooppt), 리포트 생성(→ooreport) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 PDF 서비스 자동 연동 안 함 |
| **수정 대상** | 출력 `*.pdf`, `*.png` 파일 |
| **실행 레벨** | [자동] — 변환 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — weasyprint/pandoc/PyMuPDF `uv run` 자동 실행 / 다른 에이전트: 해당 CLI 도구 수동 실행 필요 |

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--pandoc` | pandoc 엔진 사용 (LaTeX 수식 지원) | false |
| `--output <path>` | 출력 파일/디렉토리 경로 | 입력파일명.pdf / 입력파일명/ |
| `--style <css>` | 커스텀 CSS 파일 경로 (run 전용) | 내장 스타일 |
| `--image` | PDF→이미지 변환 (convert 전용) | - |
| `--dpi <n>` | 이미지 해상도 (convert 전용) | 200 |
| `--format <fmt>` | 이미지 포맷 png/jpg (convert 전용) | png |

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

```bash
oopdf run 00_doc/sp00/d0001_prd.md
oopdf run 00_doc/sp00/d0001_prd.md --pandoc
oopdf run report.md --output output/report.pdf
oopdf convert document.pdf
oopdf convert document.pdf --dpi 300 --format jpg
oopdf convert document.pdf --output ./images/
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

**Q: 필요한 의존성은?**

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


## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 변환 | 직접 처리 | - | 스크립트 실행 | - |

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
