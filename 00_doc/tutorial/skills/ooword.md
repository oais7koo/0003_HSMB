# ooword Tutorial

> Word 문서 생성 및 변환 스킬 | 버전: v02 | 카테고리: content

## 1. 이 스킬은 왜 필요한가?

Word 문서 생성 및 변환 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ooword run

# 상태 확인
ooword status

# 도움말
ooword help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ooword help` | 서브명령어 목록 표시 |
| `ooword version` | 스킬 버전 정보 (v02) |
| `ooword status` | 서브명령어 리스트, 현재 상태 |
| `ooword check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ooword run` | Word 문서 생성 실행 |
| `ooword update` | 현행화 — 소스 변경분 감지 → Word 문서 재생성 | .docx |
| `ooword update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| `ooword show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooword add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `convert` | Markdown -> Word 기본 변환 (python-docx) |
| **`convert this`** | **직전 MD 파일 Word 변환** (→ common_guide.md §9) |
| `convert --pandoc` | Markdown -> Word (LaTeX 수식 + mermaid 지원) |
| `convert --plugin` | Markdown -> Word (플러그인, 고급 기능 지원) |
| `quotation` | 견적서 마크다운 -> 워드 (표/스타일 자동 서식) |
| `quotation --plugin` | 견적서 변환 (플러그인, 변경추적 지원) |
| `edit` | 기존 DOCX 편집 (플러그인 전용) |
| `template` | 커스텀 템플릿 기반 Word 생성 |

### --plugin 모드 추가 옵션

| 옵션 | 설명 |
|------|------|
| `--track-changes` | 변경 추적 활성화 (Tracked Changes) |
| `--comment "텍스트"` | 주석 추가 |
| `--redline` | Redlining 워크플로우 (문서 검토용) |
| `--author "이름"` | 작성자 이름 지정 (기본: Claude) |

## 4. 상세 사용법

### 의존성

### 기본 모드
| 패키지 | 용도 | 필수 |
|--------|------|:----:|
| python-docx | 기본 MD->DOCX 변환 | O |
| pandoc | LaTeX 수식/mermaid 지원 | - |
| mermaid-cli | mermaid -> PNG | - |
| docx (npm) | quotation용 워드 생성 | - |

### 스킬 의존성
| 스킬 | 용도 | 필수 |
|------|------|:----:|
| ooreport | MD->DOCX 변환 스크립트 (`ooreport_md2docx.py`) 제공 | O |

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | Markdown을 Word(.docx) 문서로 변환 |
| **하는 것** | MD→docx 변환, 스타일 적용, 견적서 생성 |
| **하지 않는 것** | PPT 생성(→ooppt), PDF 변환(→oopdf), HWP 생성(→oohwp) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 문서 서비스 자동 연동 안 함 |
| **수정 대상** | 출력 `*.docx` 파일 |
| **실행 레벨** | [자동] — 변환 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — python-docx/pandoc `uv run` 자동 실행 / 다른 에이전트: `pandoc input.md -o output.docx` 수동 실행 |

### convert 서브명령어

```bash
# 기본 변환 (python-docx)
ooword convert 00_doc/sp00/d0102_문서.md
# -> 00_doc/sp00/d0102_문서.docx

# LaTeX 수식 + mermaid 다이어그램 포함 (pandoc)
ooword convert 00_doc/sp00/d0102_논문.md --pandoc
```

### convert 지원 요소

| 마크다운 요소 | 변환 결과 |
|--------------|----------|
| `# H1` ~ `##### H5` | Word 제목 스타일 (Heading 0~4) |
| `- 목록` | 글머리 기호 목록 |
| `1. 번호` | 번호 매기기 목록 |
| `> 인용` | 들여쓰기 단락 |
| `**굵게**` | Bold |
| `*기울임*` | Italic |
| `` `코드` `` | Consolas 글꼴 (10pt) |
| `|표|` | Word 테이블 (테두리 자동) |

### quotation 서브명령어 (견적서)

```bash
ooword quotation 00_doc/sp00/d0023_견적.md
```

### quotation 자동 서식

| 기능 | 설명 |
|------|------|
| 표 헤더 | 배경색 자동 적용, 중앙 정렬, 굵게 |
| 금액 셀 | 우측 정렬 |
| 소계 행 | 회색 배경, 굵게 |
| 합계 행 | 노란색 배경, 굵게 |
| 서명란 | 문서 하단 자동 추가 (작성/검토/승인) |

### edit 서브명령어 (플러그인 전용)

```bash
ooword edit 00_doc/contract.docx --track-changes
ooword edit 00_doc/contract.docx --redline --author "검토자"
ooword edit 00_doc/report.docx --comment "3페이지 수정 필요"
```

### 관련 파일

| 구분 | 경로 |
|------|------|
| 스킬 정의 | `.claude/skills/ooword/SKILL.md` |
| 변환 스크립트 | `.claude/skills/ooreport/scripts/ooreport_md2docx.py` |
| 견적서 변환기 | `.claude/skills/ooword/templates/quotation_docx.js` |
| 견적서 스타일 | `.claude/skills/ooword/templates/quotation_docx.json` |
| 가이드 | `.claude/skills/ooword/references/guide.md` |

## 5. 워크플로우

### 기본 모드
```
입력 분석 -> 변환 방식 결정 -> 변환 실행 -> 출력 검증
     |
python-docx (기본) / pandoc (수식/mermaid) / Node.js docx (견적서)
```

### 플러그인 모드 (`--plugin`)
```
입력 분석 -> unpack -> Document 라이브러리 처리 -> pack -> 출력 검증
```

## 6. 실전 예시

```bash
# 단순 변환
ooword convert 00_doc/sp00/d0102_가상논문.md

# 수식 포함 논문 변환
ooword convert 00_doc/sp00/d0102_가상논문.md --pandoc

# 견적서 워드 생성
ooword quotation 00_doc/sp00/d0023_1차개발_견적.md

# 플러그인 모드
ooword convert 00_doc/sp00/d0102_문서.md --plugin
ooword edit 00_doc/contract.docx --track-changes

# 스크립트 직접 실행
uv run python .claude/skills/ooreport/scripts/ooreport_md2docx.py 00_doc/sp00/d0102_문서.md
node .claude/skills/ooword/templates/quotation_docx.js 00_doc/sp00/d0023_견적.md
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

**Q: 필요한 의존성은?**

### 기본 모드
| 패키지 | 용도 | 필수 |
|--------|------|:----:|
| python-docx | 기본 MD->DOCX 변환 | O |
| pandoc | LaTeX 수식/mermaid 지원 | - |
| mermaid-cli | mermaid -> PNG | - |
| docx (npm) | quotation용 워드 생성 | - |

### 스킬 의존성
| 스킬 | 용도 | 필수 |
|------|------|:----:|
| ooreport | MD->DOCX 변환 스크립트 (`ooreport_md2docx.py`) 제공 | O |


## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | Explore | haiku | 입력 파일 구조 분석 | - |
| 변환 | task-executor | sonnet | MD -> DOCX 변환 실행 | - |
| 검증 | task-checker | sonnet | 출력 파일 검증 | - |

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
