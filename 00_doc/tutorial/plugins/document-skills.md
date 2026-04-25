# 플러그인: document-skills

> 문서 생성 스킬 모음 (DOCX, PDF, PPTX, 디자인 등)

## 개요

document-skills는 Markdown을 Word, PDF, PowerPoint 등 다양한 문서 형식으로 변환하는 스킬 모음 플러그인입니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `document-skills` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | - |

## 포함 스킬

| 스킬 | 설명 |
|------|------|
| `document-skills:docx` | Markdown → Word 문서 (.docx) |
| `document-skills:pdf` | Markdown → PDF |
| `document-skills:pptx` | Markdown → PowerPoint |
| `document-skills:xlsx` | 데이터 → Excel |
| `document-skills:frontend-design` | 프론트엔드 UI/UX 디자인 |
| `document-skills:canvas-design` | 캔버스 기반 디자인 |
| `document-skills:brand-guidelines` | 브랜드 가이드라인 생성 |
| `document-skills:doc-coauthoring` | 문서 공동 작성 |
| `document-skills:webapp-testing` | 웹앱 테스트 자동화 |
| `document-skills:mcp-builder` | MCP 서버 빌더 |
| `document-skills:skill-creator` | 새 스킬 생성 |

## 사용 예시

```bash
# 1. Markdown → Word
/document-skills:docx
# → 현재 컨텍스트 또는 지정 .md 파일을 Word로 변환

# 2. Markdown → PDF
/document-skills:pdf

# 3. 프레젠테이션 생성
/document-skills:pptx

# 4. 프론트엔드 디자인
/document-skills:frontend-design "대시보드 UI 디자인해줘"
```

## oo 스킬과의 관계

| document-skills | oo 스킬 | 차이점 |
|----------------|---------|--------|
| `docx` | `ooword` | ooword는 OAIS 문서 특화 |
| `pdf` | `oopdf` | oopdf는 pandoc 기반, OAIS 연동 |
| `pptx` | `ooppt` | ooppt는 Marp/오피스 변환 특화 |

> **권장**: OAIS 프로젝트에서는 oo 스킬(ooword, oopdf, ooppt) 사용 권장

---

> 생성일: 2026-04-02 | ootutorial v01
