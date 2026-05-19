# d0009_env.md - 개발 환경 현황

## 문서 이력 관리
- v01 {{DATE}} — ooenv run 자동 생성

---

## 목차

1. [시스템 환경](#1-시스템-환경)
2. [MCP 서버 현황](#2-mcp-서버-현황)
3. [Claude 플러그인](#3-claude-플러그인)
4. [스킬 현황](#4-스킬-현황)
5. [에이전트 현황](#5-에이전트-현황)
6. [커맨드 현황](#6-커맨드-현황)
7. [HUD 설정](#7-hud-설정)
8. [Python 패키지](#8-python-패키지)
9. [CLI 도구](#9-cli-도구)
10. [검증 결과](#10-검증-결과)

---

> 스킬: `.claude/skills/ooenv/SKILL.md` | 마지막 업데이트: {{DATETIME}}

## 1. 시스템 환경

### 1.1 런타임 버전

| 항목 | 현재 | 표준 | 상태 |
|------|------|------|:----:|
{{RUNTIME_TABLE}}

### 1.2 개발 도구 상태

| 도구 | 상태 |
|------|------|
{{DEV_TOOLS_TABLE}}

---

## 2. MCP 서버 현황 ({{MCP_INSTALLED_COUNT}}/{{MCP_TOTAL_COUNT}}개 설치)

| MCP 서버 | 역할 | 필수 | 설치 | 설치 방법 |
|---------|------|:----:|:----:|----------|
{{MCP_STATUS_TABLE}}

---

## 3. Claude 플러그인 ({{PLUGINS_INSTALLED_COUNT}}/{{PLUGINS_TOTAL_COUNT}}개 설치)

| 플러그인 | 역할 | 필수 | 설치 | 설치 방법 |
|---------|------|:----:|:----:|----------|
{{PLUGINS_STATUS_TABLE}}

---

## 4. 스킬 현황

### 4.1 Claude 공식 스킬 ({{CLAUDE_SKILLS_INSTALLED_COUNT}}/14개 설치)

> 스킬 디렉토리: https://skills.sh/ | 설치: `npx skills add <url> --skill <name>`

| 스킬 | 역할 | 필수 | 설치 | 설치 방법 |
|------|------|:----:|:----:|----------|
| algorithmic-art | 알고리즘 아트 생성 (p5.js) | - | {{S_algorithmic-art}} | `npx skills add https://github.com/anthropics/skills --skill algorithmic-art` |
| brand-guidelines | 브랜드 가이드라인 적용 | - | {{S_brand-guidelines}} | `npx skills add https://github.com/anthropics/skills --skill brand-guidelines` |
| canvas-design | 비주얼 아트 생성 (.png, .pdf) | - | {{S_canvas-design}} | `npx skills add https://github.com/anthropics/skills --skill canvas-design` |
| doc-coauthoring | 문서 공동 작성 워크플로우 | - | {{S_doc-coauthoring}} | `npx skills add https://github.com/anthropics/skills --skill doc-coauthoring` |
| docx | Word 문서 생성/편집 | ★ | {{S_docx}} | `npx skills add https://github.com/anthropics/skills --skill docx` |
| mcp-builder | MCP 서버 구축 가이드 | - | {{S_mcp-builder}} | `npx skills add https://github.com/anthropics/skills --skill mcp-builder` |
| pdf | PDF 조작/생성/분석 | ★ | {{S_pdf}} | `npx skills add https://github.com/anthropics/skills --skill pdf` |
| pptx | PowerPoint 생성/편집 | ★ | {{S_pptx}} | `npx skills add https://github.com/anthropics/skills --skill pptx` |
| skill-creator | 스킬 생성 가이드 | ★ | {{S_skill-creator}} | `npx skills add https://github.com/anthropics/skills --skill skill-creator` |
| slack-gif-creator | Slack용 GIF 생성 | - | {{S_slack-gif-creator}} | `npx skills add https://github.com/anthropics/skills --skill slack-gif-creator` |
| theme-factory | 아티팩트 테마 적용 | - | {{S_theme-factory}} | `npx skills add https://github.com/anthropics/skills --skill theme-factory` |
| webapp-testing | 웹앱 테스팅 (Playwright) | - | {{S_webapp-testing}} | `npx skills add https://github.com/anthropics/skills --skill webapp-testing` |
| web-artifacts-builder | 복합 웹 아티팩트 구축 | - | {{S_web-artifacts-builder}} | `npx skills add https://github.com/anthropics/skills --skill web-artifacts-builder` |
| xlsx | Excel 스프레드시트 생성/편집 | ★ | {{S_xlsx}} | `npx skills add https://github.com/anthropics/skills --skill xlsx` |

> **일괄 설치**: `npx skills add https://github.com/anthropics/skills` (전체 Anthropic 공식 스킬)

### 4.2 oo 프로젝트 스킬 ({{OAIS_SKILLS_COUNT}}개)

{{SKILLS_TABLE}}

---

## 5. 에이전트 현황 ({{AGENTS_INSTALLED_COUNT}}/{{AGENTS_TOTAL_COUNT}}개 사용)

> 설치: `.claude/agents/unuse/xxx.md` → `.claude/agents/` | 삭제: `.claude/agents/xxx.md` → `.claude/agents/unuse/`

| 에이전트 | 사용 | 역할 |
|---------|:----:|------|
{{AGENTS_TABLE}}

---

## 6. 커맨드 현황 ({{COMMANDS_INSTALLED_COUNT}}/{{COMMANDS_TOTAL_COUNT}}개 사용)

> 설치: `.claude/commands/sc/unuse/xxx.md` → `.claude/commands/sc/` | 삭제: `.claude/commands/sc/xxx.md` → `.claude/commands/sc/unuse/`

| 커맨드 | 사용 | 역할 |
|--------|:----:|------|
{{COMMANDS_TABLE}}

---

## 7. HUD 설정

| 항목 | 상태 |
|------|------|
| HUD 스크립트 | {{HUD_SCRIPT_STATUS}} |
| HUD 설정 파일 | {{HUD_CONFIG_STATUS}} |
| 프리셋 | {{HUD_PRESET}} |
| 활성 요소 | {{HUD_ELEMENTS_ON}} |
| 비활성 요소 | {{HUD_ELEMENTS_OFF}} |

> 설정 파일: `~/.claude/.omc/hud-config.json` | 변경: `/oh-my-claudecode:hud minimal/focused/full`

---

## 8. Python 패키지

| 항목 | 값 |
|------|---|
| 설치된 패키지 | {{PACKAGES_COUNT}}개 |
| PyTorch | {{PYTORCH_VERSION}} |
| CUDA | {{CUDA_AVAILABLE}} |

---

## 9. CLI 도구 ({{CLI_INSTALLED_COUNT}}/{{CLI_TOTAL_COUNT}}개 설치)

> 관리: `ooenv cli [list|check|update|add|remove]`

| 명령어 | 설명 | 방법 | 설치 | 버전 |
|--------|------|------|:----:|------|
{{CLI_TABLE}}

---

## 10. 검증 결과

| 항목 | 결과 |
|------|------|
| 발견된 이슈 | {{ISSUES_FOUND}} |
| 수정된 이슈 | {{ISSUES_FIXED}} |
| 남은 이슈 | {{ISSUES_REMAINING}} |
| 검증 상태 | {{VALIDATION_STATUS}} |

{{VALIDATION_ISSUES_SECTION}}

---

*이 문서는 `ooenv run` 명령으로 자동 생성됩니다.*
