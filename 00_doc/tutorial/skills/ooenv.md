# ooenv Tutorial

> 개발 환경 및 스킬 정합성 검증 스킬 | 버전: v16 | 카테고리: doc-env

## 1. 이 스킬은 왜 필요한가?

개발 환경 및 스킬 정합성 검증 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ooenv run

# 상태 확인
ooenv status

# 도움말
ooenv help
```

## 3. 전체 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooenv help` | 서브명령어 목록 표시 | 터미널 |
| `ooenv version` | 스킬 버전 정보 (v08) | 터미널 |
| `ooenv status` | 서브명령어 리스트, 상태 요약 | 터미널 |
| `ooenv standard` | 표준 스펙(d0012)과 현재 환경 비교 (PASS/FAIL) | 터미널 |
| `ooenv standard --fix` | 비교 후 자동 수정 (플러그인 추가 + 수동항목 안내) | 터미널 |
| `ooenv run` | 통합 점검 + 자동 수정 + 상세 출력 | **d0009_env.md** + 터미널 |
| `ooenv run --dry-run` | 점검만 (수정 안 함) | 터미널 |
| `ooenv plugin` | 플러그인 상태 확인 | 설치 가이드 |
| `ooenv check` | 스킬 정합성 검증 | d{SP}0004 업데이트 |
| `ooenv show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooenv add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ooenv check --full` | oo*.md 전체 스캔 - 에이전트/커맨드/MCP 참조 검증 | 터미널 + d{SP}0004 |
| `ooenv agent` | 에이전트 경로 검증 | 터미널 + d{SP}0004 |
| `ooenv structure` | 문서 구조 검증 | 터미널 |
| `ooenv reflect` | 설정 파일 반영 검증 | 터미널 + d{SP}0004 |
| `ooenv command` | .claude/commands/sc/ 연동 검증 | 터미널 + d{SP}0004 |
| `ooenv uv check` | UV 의존성 상태 체크 | 터미널 + d{SP}0004 |
| `ooenv uv update` | UV 의존성 업데이트 | 패키지 업데이트 |
| `ooenv uv cleanup` | 미사용 패키지 탐지 및 삭제 | 터미널 (대화형) |
| `ooenv cli` | CLI 도구 현황 확인 (npm global, uv tools) | 터미널 |
| `ooenv cli check` | CLI 설치 상태 및 버전 확인 | 터미널 |
| `ooenv cli update` | CLI 도구 업데이트 | 터미널 |
| `ooenv cli add <pkg>` | CLI 도구 설치 | 터미널 |
| `ooenv cli remove <pkg>` | CLI 도구 제거 | 터미널 |
| `ooenv mcp` | MCP 서버 현황 확인 (필수/선택 상태) | 터미널 |
| `ooenv mcp check` | MCP 설치/등록 상태 확인 | 터미널 |
| `ooenv mcp add <srv>` | MCP 서버 npm 설치 | 터미널 |
| `ooenv mcp remove <srv>` | MCP 서버 npm 제거 | 터미널 |
| `ooenv context status` | 컨텍스트 전체 상태 | 터미널 |
| `ooenv context token` | 토큰 사용량 추정 | 터미널 |
| `ooenv context files` | 컨텍스트 파일 목록 | 터미널 |
| `ooenv context size` | 파일별 토큰 크기 | 터미널 |
| `ooenv context validate` | 컨텍스트 파일 검증 | 터미널 |
| `ooenv context save "msg"` | 메모리에 정보 저장 | tmp/context_memory.json |
| `ooenv context load` | 메모리에서 로드 | 터미널 |
| `ooenv context list` | 저장된 엔티티 목록 | 터미널 |
| `ooenv context clear` | 메모리 초기화 | 터미널 |
| `ooenv gpu` | GPU 환경 테스트 (NVIDIA 드라이버/CUDA/PyTorch GPU) | 터미널 |
| `ooenv kill <target>` | 좀비 프로세스 탐지 및 종료 (node/python/chrome/edge) | 터미널 |
| `ooenv kill <target> --dry-run` | 프로세스 목록만 표시 (종료 안 함) | 터미널 |
| `ooenv kill <target> --force` | 강제 종료 (/F) | 터미널 |
| `ooenv kill --list` | 지원 프로세스 별칭 목록 | 터미널 |
| `ooenv alias` | 등록된 스킬 약어 목록 표시 | 터미널 |
| `ooenv alias list` | 약어 목록 (약어 → 원본 스킬) | 터미널 |
| `ooenv alias add <약어> <스킬>` | 새 약어 등록 (SKILL.md 자동 생성) | `.claude/skills/<약어>/` |
| `ooenv alias remove <약어>` | 약어 삭제 (폴더 제거) | 터미널 |
| `ooenv alias check` | 약어 파일 정합성 검증 (원본 스킬 존재 확인) | 터미널 |
| `ooenv opti` | 컨텍스트 최적화 전체 스캔 + 리포트 (dry-run 기본) | 터미널 |
| `ooenv opti --fix` | 자동 수정 가능 항목 최적화 (.claudeignore 추가, oodoc clear) | 파일 수정 |
| `ooenv opti memory` | 메모리 파일(CLAUDE.md 계층) 토큰 크기 분석 | 터미널 |
| `ooenv opti skills` | 스킬 파일 크기 점검 (3KB 초과 탐지) | 터미널 |
| `ooenv opti docs` | Auto-load 문서 최적화 점검 (이력 행 수, 파일 크기) | 터미널 |
| `ooenv opti agents` | 에이전트 미사용 현황 분석 | 터미널 |
| `ooenv opti ignore` | .claudeignore 누락 항목 점검 | 터미널 |
| `ooenv opti mcp` | 미사용 MCP 서버 등록 점검 | 터미널 |

실행: `uv run python .claude/skills/ooenv/scripts/ooenv_run.py [args]`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 개발 환경(플러그인·Python 의존성·스킬 정합성) 일괄 점검 및 수정 |
| **하는 것** | uv 의존성 확인, 플러그인 상태 점검, d0009_env.md 현행화, 스킬 alias 관리 |
| **하지 않는 것** | 코드 품질 체크(→oocheck), 패키지 업데이트(→oouv) |
| **참조 범위** | 현재 프로젝트 + 로컬 환경 설정 파일 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp00/d0009_env.md` |
| **실행 레벨** | [자동] — 환경 스캔 후 d0009 자동 생성/갱신 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 스크립트 및 플러그인 시스템 사용 / 다른 에이전트: uv 명령 수동 실행 후 결과를 d0009에 직접 기록 |

### 에이전트 활용

| 단계 | 작업 | 에이전트 | 모델 |
|------|------|----------|------|
| 1 | 환경 구조 탐색 | Explore (내장) | haiku |
| 2 | 정합성 분석 | ooqa | sonnet |
| 3-4 | 동기화/기록 | task-executor | sonnet |

### 환경 관리

### 4.0 설정 파일 분리 (settings.local.json)

Claude Code는 두 가지 설정 파일을 지원하며 자동 병합됩니다.

| 파일 | 역할 | oosync | git |
|------|------|--------|-----|
| `settings.json` | 공통 설정 (훅, 권한, 모델 등) | 동기화 O | 커밋 O |
| `settings.local.json` | 프로젝트별 설정 (플러그인 활성화 등) | 동기화 X | .gitignore 권장 |

- `settings.local.json`은 `settings.json`과 병합되어 동작
- 프로젝트마다 다른 플러그인(obsidian, paper-search-tools 등)은 `settings.local.json`에 작성
- oosync가 `settings.local.json`을 제외 목록에 포함하므로 동기화 시 덮어쓰지 않음

**예시** — 특정 프로젝트에서만 플러그인 활성화:
```json
{
  "enabledPlugins": {
    "obsidian@obsidian-skills": true,
    "paper-search-tools@claude-settings": true
  }
}
```

### 4.1 UV 의존성

- `ooenv uv check`: 오래된/취약점 패키지 감지
- `ooenv uv update`: 패키지 업데이트
- `ooenv uv cleanup`: 미사용 패키지 탐지 및 삭제

**uv cleanup 실행:**

```bash
uv run python .claude/skills/ooenv/scripts/ooenv_uv_cleanup.py
uv run python .claude/skills/ooenv/scripts/ooenv_uv_cleanup.py --dry-run    # 삭제 없이 미리보기
uv run python .claude/skills/ooenv/scripts/ooenv_uv_cleanup.py --auto       # 확인 없이 자동 삭제
```

옵션: `--dry-run`, `--auto`, `--exclude PKG`, `--include-dev`

### cli 관리

### 5.1 CLI 관리 대상

직접 실행하는 npm global CLI 도구.

| 명령어 | 패키지 | 용도 |
|--------|--------|------|
| `claude` | `@anthropic-ai/claude-code` | Claude Code CLI |
| `task-master` | `task-master-ai` | Task Master |
| `oh-my-claude-sisyphus` | `oh-my-claude-sisyphus` | OMC 플러그인 |
| `qmd` | `@tobilu/qmd` | 로컬 마크다운 검색 엔진 (BM25/벡터/MCP) |

### 5.2 MCP 서버 패키지

Claude가 내부적으로 사용하는 MCP 서버 (npm global 설치, .mcp.json 등록으로 활성화).

> **웹 검색**: Claude Code 내장 WebSearch 기능 사용 (`brave-search` MCP 불필요 — deprecated + 2026-02 유료화로 제거)

| 서버명 | 패키지 | 용도 | 필수 |
|--------|--------|------|:----:|
| puppeteer | `puppeteer-mcp-server` | 웹 자동화 | 선택 |
| figma | `figma-mcp` | Figma 연동 | 선택 |
| qmd | `@tobilu/qmd` | 로컬 마크다운 검색 엔진 (BM25/벡터/MCP) | 선택 |

> **필수**: .mcp.json에 등록하여 항상 활성화 / **선택**: 필요 시 수동 등록

**설치 경로:** `C:\Users\oaiskoo\home\util\nodejs\node-v22.17.0-win-x64`

### 5.3 CLI 명령어

```bash
# 현황 확인
ooenv cli             # 설치된 CLI 목록 + 버전
ooenv cli check       # 최신 버전 비교

# 업데이트
ooenv cli update                        # 전체 업데이트
ooenv cli update @anthropic-ai/claude-code  # 특정 패키지

# 설치/제거
ooenv cli add <pkg>      # npm install -g <pkg>
ooenv cli remove <pkg>   # npm uninstall -g <pkg>
```

실행: npm global 패키지 관리 (`npm list -g`, `npm update -g`, `npm install -g`)

### 5.5 MCP 명령어

```bash
# 현황 확인
ooenv mcp             # MCP 서버 목록 + 필수/선택 + 설치 여부
ooenv mcp check       # npm 설치 및 .mcp.json 등록 상태 확인

# 설치/제거 (npm global)
ooenv mcp add <srv>      # npm install -g <pkg>
ooenv mcp remove <srv>   # npm uninstall -g <pkg>
```

실행: npm global 패키지 관리 + `.mcp.json` 등록 상태 교차 확인

### 5.6 QMD (Quick Markdown Search) 설정 가이드

QMD는 로컬 마크다운 검색 엔진. BM25 키워드 + 벡터 의미 + LLM 재랭킹 하이브리드 검색 지원. MCP 서버로 Claude Code 직접 연동.

**설치:**
```bash
npm install -g @tobilu/qmd
```

**초기 설정:**
```bash
qmd collection add . --name 1_oais                         # 컬렉션 등록 (프로젝트 폴더명과 통일)
qmd context add qmd://1_oais/ "OAIS 프로젝트 설명"          # 컨텍스트 추가
qmd update                                                  # BM25 인덱싱
qmd embed                                                   # 벡터 임베딩 (느림)
```

**`.mcp.json` 등록 (Windows):**
```json
{
  "mcpServers": {
    "qmd": { "type": "stdio", "command": "qmd.cmd", "args": ["mcp"] }
  }
}
```

**Claude Code 스킬 설치:**
```bash
qmd skill install
# PowerShell에서 junction 생성:
New-Item -ItemType Junction -Path '.claude/skills/qmd' -Target '.agents/skills/qmd'
```

**자동 업데이트:** `oostart run` 실행 시 `qmd update` 자동 호출 (섹션 0-3)

| 기능 | Windows 동작 | 비고 |
|------|-------------|------|
| BM25 키워드 검색 | 정상 동작 | 즉시 사용 가능 |
| 벡터 임베딩 (embed) | Vulkan GPU 사용 | 대량 파일 시 수십 분 소요 |
| MCP 서버 | 정상 동작 | command에 `qmd.cmd` 지정 필수 |

### 5.4 d0009_env.md CLI 섹션

`ooenv run` 시 **9. CLI 도구** 섹션 자동 생성:

| 도구 | 현재 버전 | 상태 |
|------|----------|------|
| claude-code | x.x.x | O/X |
| task-master-ai | x.x.x | O/X |
| oh-my-claude-sisyphus | x.x.x | O/X |

### 정합성 검증

| 명령어 | 검증 대상 | 규칙 |
|--------|----------|------|
| `agent` | 에이전트 테이블 | .claude/agents/ 경로 존재 |
| `structure` | 문서 구조 | 필수 섹션, 번호 연속성 |
| `reflect` | CLAUDE.md/GEMINI.md | MIR 스킬 등록 |
| `command` | .claude/commands/sc/*.md | 통합 명령어 매핑 |
| `check --full` | oo*.md 전체 스캔 | 에이전트/커맨드/MCP 교차 검증 |

### 6.1 check --full 상세

| 리소스 | 추출 패턴 | 검증 경로 |
|--------|----------|----------|
| 에이전트 | `subagent_type="xxx"`, `.claude/agents/xxx.md` | .claude/agents/, .claude/agents/ |
| 커맨드 | `.claude/commands/sc/xxx.md` | .claude/commands/sc/, .claude/commands/ |
| MCP | `mcp__xxx__`, 서버명 직접 참조 | .mcp.json mcpServers |

실행: `uv run python .claude/skills/ooenv/scripts/ooenv_validate_full.py [--verbose] [--output-todo] [--sp N]`

### 에이전트/커맨드 동기화

**Source:** `.claude/agents/` (우선) - **Target:** `.claude/agents/`, `.gemini/agents/`

| Source | Target | 결과 |
|--------|--------|------|
| 있음 | 없음 | 추가 |
| 없음 | 있음 | 역병합 후보 |
| 다름 | 다름 | Source 우선 |

에이전트/커맨드 관리는 폴더 이동으로 사용 상태를 관리:
- 삭제: `.claude/agents/xxx.md` -> `.claude/agents/unuse/xxx.md`
- 설치: `.claude/agents/unuse/xxx.md` -> `.claude/agents/xxx.md`

## 5. 워크플로우

### 8.1 ooenv run 흐름

```
ooenv run
  1. 플러그인 -> [ENV]
  2. UV 의존성 -> [DEP]
  3. 정합성 -> [VALIDATION]
  4. 환경 리포트 생성 -> 00_doc/sp00/d0009_env.md
  5. 리포팅/수정
```

### 8.2 d0009_env.md 리포트 내용

| 섹션 | 내용 |
|------|------|
| 1. 시스템 환경 | Python, UV, Node.js, npm, Git, Pandoc 버전 |
| 2. MCP 서버 | 설치/미설치 상태, 설치 방법 |
| 3. Claude 플러그인 | 설치/미설치 상태 (O/X) |
| 4. 스킬 현황 | 4.1 Claude 공식 스킬 (O/X), 4.2 oo 프로젝트 스킬 목록 |
| 5. 에이전트 현황 | 사용/미사용 상태 (O/X) |
| 6. 커맨드 현황 | 활성/비활성 상태 (O/X), sc/ 전체 목록 |
| 7. Python 패키지 | 패키지 수, PyTorch 버전, CUDA 상태 |
| 8. 명령어 집계 | oo 스킬 전체 서브명령어 목록 (.claude/CLAUDE.md 카탈로그) |
| 9. 검증 결과 | 발견/수정/남은 이슈 |

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ooenv run
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/ooenv/scripts/ooenv_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

(서브에이전트 정보 없음)

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-17 19:49 | ootutorial v02
