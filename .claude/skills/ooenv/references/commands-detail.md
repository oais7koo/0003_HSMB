# ooenv 서브명령어 상세 설명

> 요약: `.claude/skills/ooenv/SKILL.md` §2 서브명령어 테이블 참조

---

## 4. 환경 관리

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

---

## 5. CLI 관리

### 5.1 CLI 관리 대상

직접 실행하는 npm global CLI 도구.

| 명령어 | 패키지 | 용도 |
|--------|--------|------|
| `claude` | `@anthropic-ai/claude-code` | Claude Code CLI |
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

### 5.4 d0009_env.md CLI 섹션

`ooenv run` 시 **9. CLI 도구** 섹션 자동 생성:

| 도구 | 현재 버전 | 상태 |
|------|----------|------|
| claude-code | x.x.x | O/X |
| oh-my-claude-sisyphus | x.x.x | O/X |

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

---

## 6. 정합성 검증

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

---

## 7. 에이전트/커맨드 동기화

**Source:** `.claude/agents/` (우선) - **Target:** `.claude/agents/`, `.gemini/agents/`

| Source | Target | 결과 |
|--------|--------|------|
| 있음 | 없음 | 추가 |
| 없음 | 있음 | 역병합 후보 |
| 다름 | 다름 | Source 우선 |

에이전트/커맨드 관리는 폴더 이동으로 사용 상태를 관리:
- 삭제: `.claude/agents/xxx.md` -> `.claude/agents/unuse/xxx.md`
- 설치: `.claude/agents/unuse/xxx.md` -> `.claude/agents/xxx.md`

---

## 9. 컨텍스트 관리

| 카테고리 | 기능 | 설명 |
|----------|------|------|
| 토큰 모니터링 | `context token` | 파일별 토큰 사용량 추정 |
| Memory 연동 | `context save/load` | 세션 간 정보 유지 |
| 파일 관리 | `context files/validate` | 컨텍스트 파일 검증 |

실행: `uv run python .claude/skills/ooenv/scripts/ooenv_context.py [subcommand]`

토큰 추정: 영문 4자=1토큰, 한글 2자=1토큰, 컨텍스트 윈도우 200,000 토큰

---

## 11. Claude 설정 관리 정책

**원칙**: 복수 컴퓨터 사용 → `machines.json`으로 머신별 설정 중앙 관리, git 추적

### 설정 파일 계층

| 파일 | 관리 위치 | 포함 항목 |
|------|----------|----------|
| `~/.claude/settings.json` | 글로벌 (머신별) | `statusLine`만 (절대 경로 포함) |
| `.claude/settings.json` | **프로젝트 (git)** | permissions, plugins, env 등 공통 |
| `.claude/settings.local.json` | **프로젝트 (머신별)** | `env.TEMP`, `env.TMP` 등 머신별 |

### machines.json 기반 관리

**정의 파일**: `.claude/skills/ooenv/references/machines.json`

```json
{
  "hostname": {
    "user": "사용자명",
    "project_root": "프로젝트 경로",
    "settings_global": { "statusLine": { ... } },
    "settings_local": { "env": { "TEMP": "...", "TMP": "..." } }
  }
}
```

> **주의**: `alias` 필드는 사용하지 않는다. 머신 등록 시 alias를 설정하지 말 것.
> hostname 자체가 식별자이며, alias는 불필요한 중복 정보다.

**실행**: `uv run python .claude/skills/ooenv/scripts/ooenv_settings.py [options]`

| 옵션 | 동작 |
|------|------|
| (없음) | hostname 자동 감지 → machines.json 비교 → 동기화 |
| `--dry-run` | 변경 없이 차이점만 표시 |
| `--register` | 현재 머신 대화형 등록 (alias 입력 불필요) |
| `--show` | 현재 머신 설정 표시 |

### 동기화 동작

1. **글로벌** (`~/.claude/settings.json`): machines.json의 `settings_global` 정의와 일치시킴. 불필요 항목 자동 제거
2. **로컬** (`.claude/settings.local.json`): machines.json의 `settings_local` 정의를 deep merge

### VS Code 워크스페이스 설정 (.vscode/settings.json)

> **주의**: `.vscode/settings.json`은 VS Code 계정 기반 동기화에 포함되지 않는다.
> - **동기화되는 항목**: 사용자 설정(`%APPDATA%/Code/User/settings.json`), 키 바인딩, 확장, 테마
> - **동기화되지 않는 항목**: 프로젝트 폴더의 `.vscode/settings.json` (워크스페이스 전용)
>
> 따라서 `ooenv run`은 `.vscode/settings.json`에 **markdown preview 등 개인 편의 설정을 추가하지 않는다**.
> 전체 머신에 적용하려면 `File > Preferences > Settings`(사용자 설정)에서 직접 설정할 것.

**`.vscode/settings.json` 허용 항목** (머신 독립적·기능 필수 항목만):

| 항목 | 용도 |
|------|------|
| `git.ignoreLimitWarning` | git 대용량 파일 경고 억제 |

**추가하지 않을 항목** (개인 편의·머신별 다름):

| 항목 | 이유 |
|------|------|
| `markdown.preview.*` | 계정 동기화 불가 → 머신마다 수동 설정 필요 |

### 프로젝트 settings.json 필수 항목

| 항목 | 내용 |
|------|------|
| `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | "1" |
| `permissions.allow` | Bash, Edit, MultiEdit, Write, mcp__pencil |
| `enabledPlugins` | document-skills, oh-my-claudecode, context7 등 |
| `extraKnownMarketplaces` | claude-plugins-official |
| `autoUpdatesChannel` | "latest" |
| `skipDangerousModePermissionPrompt` | true |

### ooenv standard 체크 항목 (설정)

```
[ ] machines.json에 현재 hostname 등록 여부
[ ] ~/.claude/settings.json → statusLine만 있는지 (machines.json 일치)
[ ] .claude/settings.local.json → machines.json의 settings_local 포함 여부
[ ] .claude/settings.json → enabledPlugins에 document-skills, oh-my-claudecode 포함
[ ] .claude/settings.json → extraKnownMarketplaces 포함
[ ] .claude/CLAUDE.md → SuperClaude @참조 8개 + Korean note 포함
[ ] .claudeignore 파일 존재 여부 (컨텍스트 토큰 절감 목적)
```

### .claudeignore 관리

`.claudeignore`: Claude Code가 컨텍스트에 로드하지 않을 파일/폴더 지정. 토큰 절감 목적.

**표준 제외 대상**: `.venv/`, `node_modules/`, `.git/`, `data/`, `.obsidian/`, `.trash/`, `tmp/`, `.playwright-mcp/`, `.sync/`, lock 파일류

### 신규 컴퓨터 설정 워크플로우

1. `git clone` → 프로젝트 `.claude/settings.json` 자동 적용
2. `ooenv run` → 환경 점검 + settings 자동 수정 (machines.json 기반)
3. 커밋 → 다른 머신에서도 machines.json 공유

---

## 12. 스킬 약어(Alias) 관리

스킬 약어는 `.claude/skills/<약어>/SKILL.md` 파일로 관리된다.
`ooenv alias` 명령어로 목록 확인·추가·삭제·검증을 수행한다.

### 12.1 현재 등록된 약어 목록

| 약어 | 원본 스킬 | 경로 |
|------|----------|------|
| `oos` | `oostart` | `.claude/skills/oos/SKILL.md` |
| `oof` | `oofeature` | `.claude/skills/oof/SKILL.md` |
| `ooc` | `oocontext` | `.claude/skills/ooc/SKILL.md` |
| `ood` | `oodev` | `.claude/skills/ood/SKILL.md` |
| `ook` | `oocheck` | `.claude/skills/ook/SKILL.md` |

### 12.2 alias 명령어 동작

#### `ooenv alias list`
`.claude/skills/` 하위 폴더 중 SKILL.md의 description에 "alias" 키워드가 포함된 것을 스캔하여 표 형식으로 출력.

#### `ooenv alias add <약어> <원본스킬>`
1. `.claude/skills/<원본스킬>/SKILL.md` 존재 확인
2. `.claude/skills/<약어>/` 폴더 생성
3. 아래 템플릿으로 SKILL.md 생성:
```markdown
---
name: <약어>
description: "<원본스킬> 스킬의 약어 alias. '<약어>'로 호출하면 <원본스킬>와 동일하게 동작한다"
metadata:
  version: v01
  category: <원본스킬의 category>
---

이 스킬은 **`<원본스킬>`의 약어 alias**입니다.

전달된 인자(`$ARGUMENTS`)를 그대로 유지하여 **즉시 `<원본스킬>` 스킬을 실행**하세요.
Skill 도구로 `<원본스킬>`를 호출하고 `$ARGUMENTS`를 args로 전달합니다.
```
4. ooenv SKILL.md 13.1 테이블에 새 행 추가

#### `ooenv alias remove <약어>`
1. `.claude/skills/<약어>/SKILL.md` alias 여부 확인 (일반 스킬 오삭제 방지)
2. 폴더 삭제
3. ooenv SKILL.md 13.1 테이블에서 해당 행 제거

#### `ooenv alias check`
- 각 약어의 원본 스킬 경로 존재 여부 확인
- SKILL.md의 name 필드와 폴더명 일치 여부 확인
- 결과: PASS / WARN (원본 스킬 없음) 출력

---

## 13. 컨텍스트 최적화 (opti)

### 13.1 개요

Claude Code 세션의 **컨텍스트 윈도우(200K tokens)**에 영향을 주는 모든 요소를 스캔하여 최적화 상태를 점검하고, 가능한 항목을 자동 수정한다.

`ooenv context token`이 토큰 현황을 보여준다면, `ooenv opti`는 **개선 가능 항목을 진단하고 처방**한다.

### 13.2 점검 대상

| 카테고리 | 점검 항목 | 경고 기준 | 수정 방법 |
|---------|----------|----------|---------|
| 메모리 파일 | CLAUDE.md 계층 파일 크기 | 3KB 경고 / 5KB 위험 | 수동 압축 권장 |
| Auto-load 문서 | d0001/d0004 이력 테이블 행 수 | 5행 초과 | `oodoc clear` |
| Auto-load 문서 | d0001/d0004 파일 크기 | 4KB 경고 | `oodoc clear` |
| 스킬 파일 | oo*/SKILL.md 크기 | 3KB 초과 | `oodoc optimize` |
| .claudeignore | 표준 제외 항목 누락 | 표준 목록 기준 | `--fix` 자동 추가 |
| 에이전트 | .claude/agents/ 활성 에이전트 수 | 30개 초과 | 수동 unuse 이동 권장 |
| MCP 서버 | .mcp.json 등록 vs 실제 사용 | 미사용 등록 서버 | 수동 비활성화 |
| 커맨드 파일 | .claude/commands/sc/ 활성 수 | 20개 초과 | 수동 unuse 이동 권장 |

### 13.3 출력 예시

```
=== ooenv opti: 컨텍스트 최적화 리포트 ===
컨텍스트 윈도우: 200,000 tokens | 현재 사용: 62.5k (31%)

[A] 메모리 파일    39.5k (19.8%)  ⚠️ 최적화 가능
  ⚠️  ORCHESTRATOR.md   5.9k  → 압축 권장
  ⚠️  PERSONAS.md       4.6k  → 압축 권장
  ⚠️  .claude/CLAUDE.md 4.3k  → 압축 권장
  ✅  d0001_prd.md       2.6k  정상
  ✅  d0004_todo.md      3.7k  정상

[B] 스킬 파일      7.8k (3.9%)   ✅ 정상
  ✅  3KB 초과 스킬: 0개

[C] 에이전트       3.1k (1.6%)   ℹ️ 확인 권장
  ℹ️  활성 에이전트: 24개 (기준 30개 이내)

[D] .claudeignore                 ⚠️ 누락 항목 있음
  ⚠️  누락: .obsidian/, .trash/  (--fix로 자동 추가 가능)

[E] Auto-load 문서                ✅ 정상
  ✅  이력 테이블 행 수 5행 이내

[F] MCP 서버                      ✅ 정상
  ✅  등록된 MCP 14개 모두 사용 중

────────────────────────────────────────────
최적화 가능 토큰: ~11.9k  (절감 시 여유 +6%)
자동 수정 가능:  .claudeignore 2항목  →  ooenv opti --fix
수동 검토 권장:  메모리 파일 3개 (내용 압축/정리)
```

### 13.4 워크플로우

```
ooenv opti
  1. 파일 직접 스캔 (메모리 파일, 스킬, 에이전트, .claudeignore)
  2. 카테고리별 점검 (A~F 병렬)
  3. 경고/위험 항목 집계
  4. 리포트 출력 (dry-run)
  5. --fix 시 자동 수정 실행 (.claudeignore 추가, oodoc clear 호출)
  6. 권장 후속 명령어 안내
```

### 13.5 --fix 자동 수정 항목

| 항목 | 처리 내용 |
|------|---------|
| .claudeignore 누락 항목 | 표준 제외 목록에서 누락된 항목 추가 |
| Auto-load 문서 이력 초과 | `oodoc clear` 자동 실행 |

**수동 처리 필요 항목** (--fix 미지원, 판단 필요):

| 항목 | 이유 |
|------|------|
| 메모리 파일 내용 압축 | 내용 가치 판단은 사람이 |
| 에이전트 unuse 이동 | 의도적 사용 중일 수 있음 |
| MCP 서버 비활성화 | 프로젝트별 설정 필요 |
| SuperClaude 파일 압축 | OMC 프레임워크 구조 변경 필요 |

### 13.6 기준값

| 항목 | 기준값 | 출처 |
|------|--------|------|
| 컨텍스트 윈도우 | 200,000 tokens | Claude API |
| 메모리 파일 경고 | 3KB (≈1,500 tokens) | PRD §3.2 |
| 메모리 파일 위험 | 5KB (≈2,500 tokens) | PRD §3.2 |
| 스킬 파일 상한 | 3KB | oodoc optimize 기준 |
| Auto-load 이력 행 | 5행 | PRD §3.2 |
| 활성 에이전트 상한 | 30개 | 컨텍스트 효율 기준 |
| 토큰 추정 | 한글 2자=1토큰, 영문 4자=1토큰 | ooenv context |

---

## 14. HUD 설정 관리

### 14.1 표준 설정

**레퍼런스 파일**: `.claude/skills/ooenv/references/hud-config-default.json`
**실제 설정 파일**: `~/.claude/.omc/hud-config.json`

```json
{
  "preset": "minimal",
  "elements": {
    "omcLabel": true,
    "model": true, "modelFormat": "short",
    "rateLimits": true,
    "ralph": true,
    "lastSkill": true,
    "contextBar": true,
    "backgroundTasks": true,
    "agents": true,
    "todos": true,
    "maxOutputLines": 3
  },
  "layout": {
    "line1": ["hostname", "cwd", "gitRepo", "gitBranch", "gitStatus", "apiKeySource", "profile"],
    "main": ["omcLabel", "model", "rateLimits", "ralph", "lastSkill", "contextBar", "background"]
  },
  "thresholds": { "contextWarning": 70, "contextCritical": 85, "ralphWarning": 7 }
}
```

**출력 구조** (3줄):
- Line 1 (main): `[OMC] Sonnet · 5h:X/Y · W:X/Y · ⟳ ralph · lastSkill · ████ contextBar · bg`
- Line 2 (detail): agents 상태
- Line 3 (detail): todos 상태

### 14.2 HUD 설정 복원

```bash
cp .claude/skills/ooenv/references/hud-config-default.json ~/.claude/.omc/hud-config.json
```

### 14.3 주요 설정 원칙

> - `alias` 필드 사용 금지 — hostname이 식별자
> - `model`은 line1 기본 레이아웃이 아닌 layout.main에 배치 (중복 방지)
> - `maxOutputLines: 3` — main + agents + todos 3줄 표시
