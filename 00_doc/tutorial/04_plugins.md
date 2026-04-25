# 플러그인 · MCP 서버 사용법

> `ooenv tutorial --update`로 현행화 | `ooenv run`으로 현황 확인

## Claude Code 플러그인

### 설치된 플러그인

| 플러그인 | 용도 | 관리 |
|----------|------|------|
| `document-skills` | PDF/PPTX/DOCX/XLSX 변환 툴킷 | `ooenv settings` |
| `oh-my-claudecode` | 멀티에이전트 오케스트레이션 | `ooenv settings` |
| `context7` | 라이브러리 공식 문서 조회 | `ooenv settings` |

### 플러그인 확인/설치

```bash
# 현황 확인
ooenv settings       # 설치 상태 CHECK-3

# 설치
claude plugin install <key>

# 플러그인 스킬 사용 예시
/document-skills:pdf        # PDF 처리
/document-skills:docx       # Word 문서
/document-skills:pptx       # PPT 처리
/document-skills:xlsx       # Excel 처리
```

### document-skills 플러그인 스킬

| 스킬 | 용도 |
|------|------|
| `document-skills:pdf` | PDF 추출/조작 |
| `document-skills:docx` | Word 문서 생성/편집 |
| `document-skills:pptx` | 프레젠테이션 생성 |
| `document-skills:xlsx` | 스프레드시트 처리 |
| `document-skills:canvas-design` | 이미지/PDF 디자인 |
| `document-skills:frontend-design` | 프론트엔드 UI |
| `document-skills:webapp-testing` | 웹앱 테스트 |

---

## MCP 서버

현황 확인: `ooenv mcp` | 설정: `.mcp.json`

### 주요 MCP 서버

| 서버명 | 용도 | 도구 prefix |
|--------|------|-------------|
| `desktop-commander` | 파일/프로세스 제어 | `mcp__desktop-commander__` |
| `brave-search` | 웹 검색 | `mcp__brave-search__` |
| `github` | GitHub 연동 | `mcp__github__` |
| `pencil` | .pen 디자인 파일 | `mcp__pencil__` |
| `claude.ai Figma` | Figma 디자인 | `mcp__claude_ai_Figma__` |
| `docs-server` | Cloudflare 문서 | `mcp__docs-server__` |
| `puppeteer` | 웹 자동화 | `mcp__puppeteer__` |

### MCP 서버 관리

```bash
# 현황 확인
ooenv mcp              # 서버 목록 + 설치 여부
ooenv mcp check        # npm 설치 + .mcp.json 등록 교차 확인

# 설치/제거
ooenv mcp add brave-search
ooenv mcp remove puppeteer
```

---

## CLI 도구

현황 확인: `ooenv cli`

### 설치된 CLI

| 도구 | 패키지 | 용도 |
|------|--------|------|
| `claude` | `@anthropic-ai/claude-code` | Claude Code CLI |
| `task-master` | `task-master-ai` | Task Master AI |
| `oh-my-claude-sisyphus` | `oh-my-claude-sisyphus` | OMC 플러그인 |

### CLI 관리

```bash
ooenv cli              # 설치 목록 + 버전
ooenv cli check        # 최신 버전 비교
ooenv cli update       # 전체 업데이트
ooenv cli add <pkg>    # npm install -g <pkg>
```

---

## Python 패키지 (UV)

현황 확인: `ooenv uv check`

### 주요 의존성 그룹

| 그룹 | 패키지 | 용도 |
|------|--------|------|
| 핵심 | numpy, pandas, matplotlib | 데이터/시각화 |
| 이미지 | pillow, opencv-python, scikit-image | 이미지 처리 |
| PDF | pypdf, pdf2image, pdfplumber, pymupdf | PDF 처리 |
| 문서 | python-docx, pyhwpx, hwpx | 문서 생성 |
| 스크래핑 | yt-dlp, faster-whisper | 유튜브 STT |
| 웹 | openpyxl, playwright | Excel/웹자동화 |
| AI | anthropic, langchain, langchain-ollama | LLM |
| 지도 | geopandas, adjusttext | 지리정보 |

### 의존성 관리

```bash
# 확인
ooenv uv check         # 상태 확인
uv sync                # 의존성 동기화

# 추가/제거
uv add numpy
uv remove numpy

# 정리
ooenv uv cleanup       # 미사용 패키지 탐지
ooenv uv cleanup --dry-run   # 미리보기만
```

---

## 환경 설정 파일

| 파일 | 위치 | 내용 |
|------|------|------|
| `.claude/settings.json` | 프로젝트 (git) | 권한, 플러그인, MCP 설정 |
| `~/.claude/settings.json` | 글로벌 (머신별) | statusLine만 |
| `.claude/settings.local.json` | 로컬 (git 제외) | TEMP/TMP 경로 등 |
| `.mcp.json` | 프로젝트 | MCP 서버 등록 |

```bash
# 설정 점검
ooenv settings         # 3가지 CHECK 실행
ooenv standard         # 표준 스펙과 비교
ooenv standard --fix   # 비교 후 자동 수정
```
