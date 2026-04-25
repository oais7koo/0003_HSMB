# ooenv_guide - 개발 환경 검증 가이드

## 문서 이력 관리
- v05 2026-04-14 — Rust/burn 환경 설정 가이드 추가 (섹션 3.8)
- v04 2026-04-09 — OMC 플러그인 캐시 재빌드 트러블슈팅 추가 (섹션 3.7 원인 4)
- v03 2026-04-02 — OMC HUD 설치 트러블슈팅 가이드 추가 (섹션 3.7)
- v02 2026-03-19 — 설정 파일 정리 가이드 추가 (섹션 3.6)
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/ooenv/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

개발 전 환경 점검, 정합성 검증, 컨텍스트 관리를 통합 처리하는 가이드입니다.

**목적**: 플러그인, Python 의존성, 스킬 정합성 일괄 점검/수정
**대상**: .mcp.json, pyproject.toml, .claude/skills/oo*/SKILL.md, .claude/, .claude/agents/, .claude/commands/sc/
**출력**: 00_doc/sp00/d0009_env.md (환경 리포트), 터미널 (검증 결과)

## 2. 워크플로우

### 2.1 통합 점검 (run)

```
플러그인 상태 확인 → [ENV]
    ↓
UV 의존성 체크 → [DEP]
    ↓
스킬 정합성 검증 → [VALIDATION]
    ↓
환경 리포트 생성 (d0009_env.md)
    ↓
자동 수정 (--fix)
```

### 2.2 스킬 정합성 검증 (validate --full)

```
.claude/skills/oo*/SKILL.md 스캔
    ↓
에이전트/커맨드/MCP 참조 추출
    ↓
현재 환경과 교차 검증
    ↓
누락 항목 보고 (d{SP}0004)
```

### 2.3 컨텍스트 관리 (context)

```
토큰 사용량 추정
    ↓
Memory 연동 (save/load)
    ↓
컨텍스트 파일 검증
```

## 3. 상세 사용법

### 3.1 환경 점검

```bash
# 통합 점검 + 자동 수정 + d0009 생성
uv run python .claude/skills/ooenv/scripts/ooenv_run.py run

# 점검만 (수정 안 함)
uv run python .claude/skills/ooenv/scripts/ooenv_run.py run --dry-run

# 상태 요약
uv run python .claude/skills/ooenv/scripts/ooenv_run.py status
```

### 3.2 UV 의존성 관리

```bash
# 의존성 상태 체크 (오래된/취약점 패키지)
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv check

# 패키지 업데이트
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv update

# 미사용 패키지 정리
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv cleanup

# 드라이런 (삭제 없이 미리보기)
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv cleanup --dry-run

# 자동 삭제 (확인 없이)
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv cleanup --auto
```

**제외 대상 (자동)**:
- 런타임: uvicorn, gunicorn
- 테스트: pytest, coverage
- 타입 힌트: types-*
- 빌드: setuptools, wheel

### 3.3 스킬 정합성 검증

```bash
# 전체 정합성 검증
uv run python .claude/skills/ooenv/scripts/ooenv_run.py validate --full

# 상세 출력
uv run python .claude/skills/ooenv/scripts/ooenv_run.py validate --full --verbose

# todo 형식으로 출력
uv run python .claude/skills/ooenv/scripts/ooenv_run.py validate --full --output-todo --sp 02
```

**검증 대상**:
| 리소스 | 추출 패턴 | 검증 경로 |
|--------|----------|----------|
| 에이전트 | `subagent_type="xxx"` | .claude/agents/, .claude/agents/ |
| 커맨드 | `.claude/commands/sc/xxx.md` | .claude/commands/sc/, .claude/commands/ |
| MCP | `mcp__xxx__`, 서버명 | .mcp.json mcpServers |

### 3.4 에이전트/커맨드 동기화

```bash
# .claude/agents/ → .claude/agents/
uv run python .claude/skills/ooenv/scripts/ooenv_run.py sync-agents

# .claude/skills/oo*/SKILL.md 동기화
uv run python .claude/skills/ooenv/scripts/ooenv_run.py sync-skills

# 드라이런
uv run python .claude/skills/ooenv/scripts/ooenv_run.py sync-agents --dry-run

# 역병합 (Target → Source)
uv run python .claude/skills/ooenv/scripts/ooenv_run.py sync-agents --reverse
```

### 3.6 설정 파일 정리 (settings 중복 제거)

Claude Code 설정은 3개 파일로 구성되며 우선순위는 `local > project > user`.
**혼자 쓰는 프로젝트**는 project 중심으로 통합하여 중복을 제거한다.

#### 파일 역할 분담

| 파일 | 경로 | 용도 |
|------|------|------|
| project | `.claude/settings.json` | 플러그인 활성화, env, permissions, hooks |
| local | `.claude/settings.local.json` | MCP 서버 활성화, 개인 권한 (git 미포함) |
| user | `~/.claude/settings.json` | 전역 설정 (statusLine, model, marketplace 등) |

#### 정리 원칙

1. **플러그인** → project `settings.json`에서 일괄 관리 (enabled/disabled 모두)
2. **MCP 서버** → local `settings.local.json`의 `enabledMcpjsonServers`에서 관리
3. **env 변수** → project에 정의한 것은 user에서 제거 (중복 방지)
4. **orphan 항목** → 설치되지 않은 플러그인 항목 제거
5. **레거시 permissions** → 과거 작업 흔적(bash 명령어 조각 등) 정기 정리

#### 권장 구조

**`.claude/settings.json` (project)**:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "BASH_DEFAULT_TIMEOUT_MS": "60000",
    "TEMP": "D:\\resilio\\1_oais\\tmp"
  },
  "permissions": { "allow": ["Bash", "Edit", "Write"], "deny": [...] },
  "enabledPlugins": {
    "context7@claude-plugins-official": true,
    "code-review@claude-plugins-official": true,
  }
}
```

**`.claude/settings.local.json` (local)**:
```json
{
  "permissions": { "allow": ["Bash(uv run:*)", "WebSearch", ...] },
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["sequential-thinking", "desktop-commander", "taskmaster-ai"]
}
```

**`~/.claude/settings.json` (user)**:
```json
{
  "statusLine": { ... },
  "model": "...",
  "extraKnownMarketplaces": { ... },
  "enabledPlugins": { "oh-my-claudecode@omc": true }
}
```

#### 중복 체크 명령

```bash
# 설치된 플러그인 + 스코프 확인
claude plugin list

# 플러그인 업데이트 (스코프 지정 필수)
claude plugin update <name>@<source> --scope local|project|user
```

### 3.5 컨텍스트 관리

```bash
# 전체 상태
uv run python .claude/skills/ooenv/scripts/ooenv_context.py status

# 토큰 사용량 추정
uv run python .claude/skills/ooenv/scripts/ooenv_context.py token

# 컨텍스트 파일 목록
uv run python .claude/skills/ooenv/scripts/ooenv_context.py files

# 파일별 토큰 크기
uv run python .claude/skills/ooenv/scripts/ooenv_context.py size

# 정보 저장 (Memory)
uv run python .claude/skills/ooenv/scripts/ooenv_context.py save "PRD 변경: JWT 인증 방식 결정"

# 저장된 정보 로드
uv run python .claude/skills/ooenv/scripts/ooenv_context.py load

# 메모리 초기화
uv run python .claude/skills/ooenv/scripts/ooenv_context.py clear
```

**토큰 추정 기준**:
- 영문: 4자 = 1토큰
- 한글: 2자 = 1토큰
- 컨텍스트 윈도우: 200,000 토큰

### 3.8 Rust/burn 환경 설정

burn은 Rust ML 프레임워크로, ndarray(CPU) / wgpu(GPU) / tch(PyTorch) 백엔드를 지원합니다.

#### 설치 순서 (Windows, ndarray 백엔드 기준)

**Step 1. Rust(rustup) 설치**
```bash
winget install Rustlang.Rustup --accept-package-agreements --accept-source-agreements
```
> winget 설치 후 새 터미널에서 `~/.cargo/bin`이 PATH에 자동 추가됨

**Step 2. MSYS2 + MinGW gcc 설치** (MSVC 링커 대신 GNU 사용)
```bash
# MSYS2 설치
winget install msys2.msys2 --accept-package-agreements --accept-source-agreements

# MinGW gcc 설치
/c/msys64/usr/bin/pacman.exe -S --noconfirm mingw-w64-x86_64-gcc
```
> 이유: Git Bash 환경에서 `/usr/bin/link`(GNU link)가 MSVC `link.exe`보다 먼저 실행되어 링크 오류 발생

**Step 3. Rust GNU 타깃으로 전환**
```bash
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu
```

**Step 4. ~/.bashrc에 PATH 등록**
```bash
# ~/.bashrc
export PATH="$HOME/.cargo/bin:$PATH"
export PATH="/c/msys64/mingw64/bin:$PATH"
```

**Step 5. burn 프로젝트 생성 및 빌드**
```bash
export PATH="/c/msys64/mingw64/bin:$PATH:$HOME/.cargo/bin"

cargo new my_burn_project
cd my_burn_project

# Cargo.toml에 추가
# [dependencies]
# burn = { version = "0.17", features = ["ndarray"] }

cargo build   # 첫 빌드: 5~15분 소요
cargo run
```

#### 버전 현황 (2026-04-14 기준)

| 구성 요소 | 버전 | 위치 |
|----------|------|------|
| rustup | 1.29.0 | winget |
| Rust stable (GNU) | 1.94.1 | `~/.cargo/bin/` |
| MinGW gcc | MSYS2 경유 | `/c/msys64/mingw64/bin/` |
| burn | 0.17.1 | crates.io |

#### 예제 프로젝트

`C:\Users\oaiskoo\burn_hello` — ndarray 백엔드 텐서 연산 예제

```bash
export PATH="/c/msys64/mingw64/bin:$PATH:$HOME/.cargo/bin"
cd /c/Users/oaiskoo/burn_hello && cargo run
```

#### 체크 항목 (ooenv checklist C18~C20)

| ID | 확인 명령 | 정상 조건 |
|----|----------|----------|
| C18 | `ls ~/.cargo/bin/cargo.exe` | 파일 존재 |
| C19 | `ls /c/msys64/mingw64/bin/gcc.exe` | 파일 존재 |
| C20 | `grep cargo ~/.bashrc` | PATH 등록 확인 |

---

## 4. 사용 예시

### 예시 1: 개발 환경 초기 점검

```bash
# 1. 통합 점검
uv run python .claude/skills/ooenv/scripts/ooenv_run.py run

# 결과:
# - 플러그인: superpowers ❌ → 설치 안내
# - UV: pandas 취약점 → uv update 권장
# - 스킬: oocheck → code-error-checker ✅

# 2. d0009_env.md 생성 완료
```

### 예시 2: 미사용 패키지 정리

```bash
# 1. 미리보기
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv cleanup --dry-run

# 결과:
# - requests (미사용)
# - beautifulsoup4 (미사용)

# 2. 대화형 삭제
uv run python .claude/skills/ooenv/scripts/ooenv_run.py uv cleanup
# 선택: requests [y/n]? y
```

### 예시 3: 에이전트/커맨드 관리

```bash
# 1. 에이전트 삭제 (미사용으로 이동)
# .claude/agents/old-agent.md → .claude/agents/unuse/old-agent.md

# 2. 에이전트 복원
# .claude/agents/unuse/old-agent.md → .claude/agents/old-agent.md

# 3. d0009 업데이트
uv run python .claude/skills/ooenv/scripts/ooenv_run.py run
# → d0009_env.md 섹션 5: 에이전트 현황 (O/X 표시)
```

### 3.7 OMC HUD 설치 트러블슈팅

#### 증상: HUD에 "[OMC] run /omc-setup to install properly" 표시

이 메시지는 HUD 스크립트가 Claude Code로부터 stdin(JSON) 데이터를 받지 못할 때 발생합니다.

**원인 1: combined-statusline.js stdin 미포워딩** (가장 흔한 원인)

`.claude/settings.json`에 OMC HUD와 다른 statusLine 스크립트를 합치는
`combined-statusline.js`를 사용할 때 발생합니다.
Claude Code는 JSON 데이터를 `combined-statusline.js`의 stdin으로 전달하지만,
이 스크립트가 `execSync`로 HUD를 호출할 때 stdin을 포워딩하지 않으면 HUD가 데이터를 못 받습니다.

**해결책**: `combined-statusline.js`에서 stdin을 읽어 HUD에 전달:
```javascript
const { readFileSync } = require('fs');

// Claude Code JSON stdin 읽기
let claudeStdin = '';
try {
  if (!process.stdin.isTTY) {
    claudeStdin = readFileSync(0, 'utf8'); // fd 0 = stdin
  }
} catch (_) {}

// OMC HUD 호출 시 input으로 전달
const opts = { timeout: 3000, encoding: 'utf8' };
if (claudeStdin) opts.input = claudeStdin;
execSync('node C:/Users/oaiskoo/.claude/hud/omc-hud.mjs', opts);
```

**원인 2: omc-setup 불완전 실행 (jq 미설치)**

`jq`가 없으면 `setup-progress.sh complete` 명령이 실패하며
`.omc-config.json`의 `setupCompleted` 필드가 설정되지 않아
omc-setup이 완료로 인식되지 않습니다.

**해결책**: jq 대신 Node.js로 수동 완료 처리:
```bash
node -e "
const fs = require('fs'), path = require('path');
const configFile = path.join(require('os').homedir(), '.claude', '.omc-config.json');
let existing = {};
try { existing = JSON.parse(fs.readFileSync(configFile, 'utf8')); } catch {}
const updated = { ...existing, setupCompleted: new Date().toISOString(), setupVersion: '4.9.3' };
fs.writeFileSync(configFile, JSON.stringify(updated, null, 2));
console.log('완료 처리됨');
"
```

**원인 3: Plugin NOT found 오탐**

`setup-claude-md.sh` 실행 시 "Plugin NOT found" 메시지가 나와도
실제로는 `.claude/settings.json`의 `enabledPlugins`에
`"oh-my-claudecode@omc": true`가 있으면 플러그인은 정상 활성화 상태입니다.
글로벌 `~/.claude/settings.json`에 플러그인 항목이 없어서 발생하는 오탐입니다.

**확인 방법**:
```bash
# 로컬 settings.json에서 확인
grep "oh-my-claudecode" .claude/settings.json
# → "oh-my-claudecode@omc": true 이면 정상
```

**원인 4: OMC 플러그인 캐시 빌드 손상**

플러그인 업데이트 후 HUD가 표시되지 않거나 오작동할 때,
플러그인 캐시 디렉터리의 빌드 산출물이 누락/손상된 경우입니다.

**해결책**: 플러그인 캐시 디렉터리에서 재빌드:
```bash
# 버전 확인 (설치된 버전으로 경로 조정)
ls "C:\Users\oaiskoo\.claude\plugins\cache\omc\oh-my-claudecode\"

# 해당 버전 디렉터리에서 재빌드
cd "C:\Users\oaiskoo\.claude\plugins\cache\omc\oh-my-claudecode\<버전>" && npm install && npm run build
```

**예시 (v4.11.2)**:
```bash
cd "C:\Users\oaiskoo\.claude\plugins\cache\omc\oh-my-claudecode\4.11.2" && npm install && npm run build
```

빌드 성공 시 아래 파일들이 생성됩니다:
- `dist/hooks/skill-bridge.cjs`
- `bridge/mcp-server.cjs`, `bridge/team-bridge.cjs`
- `bridge/runtime-cli.cjs`, `bridge/team-mcp.cjs`, `bridge/cli.cjs`, `bridge/team.js`

빌드 후 Claude Code를 재시작하면 HUD가 정상 작동합니다.

#### OMC HUD 동작 원리

1. Claude Code가 `statusLine.command`를 주기적으로 실행
2. Claude Code가 세션 JSON 데이터(cwd, model, context_window 등)를 stdin으로 파이프
3. HUD 스크립트(`omc-hud.mjs`)가 stdin을 읽어(`readStdin()`) 상태 표시줄 출력
4. `process.stdin.isTTY === true`이면 stdin 미수신으로 판단 → 오류 메시지 출력

#### HUD 정상 작동 확인

```bash
# stdin JSON 데이터를 직접 주입하여 테스트
echo '{"cwd":"/test","model":{"id":"claude-sonnet-4-6"},"context_window":{"used_percentage":20}}' \
  | node ~/.claude/hud/omc-hud.mjs

# combined-statusline.js 테스트 (위와 동일한 방법)
echo '{"cwd":"/test","model":{"id":"claude-sonnet-4-6"},"context_window":{"used_percentage":20}}' \
  | node .claude/hooks/combined-statusline.js
```

정상 출력 예: `[OMC#4.9.3] | ctx:20%`

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/ooenv/SKILL.md | 스킬 명세 |
| 00_doc/sp00/d0009_env.md | 환경 리포트 (자동 생성) |
| 00_doc/d{SP}0004_todo.md | 환경 이슈 추적 |
| .claude/skills/oostart/SKILL.md | 세션 시작 |
| .claude/skills/oocheck/SKILL.md | 코드 품질 체크 |

**에이전트**: Explore, ooqa, task-executor
**도구**: Sequential MCP

**d0009_env.md 주요 섹션**:
1. 시스템 환경 (Python, UV, Node.js, Git 버전)
2. MCP 서버 (설치/미설치 상태)
3. Claude 플러그인 (O/X)
4. 스킬 현황 (4.1 Claude 공식 스킬 O/X, 4.2 oo 프로젝트 스킬)
5. 에이전트 현황 (사용/미사용 O/X)
6. 커맨드 현황 (사용/미사용 O/X)
7. Python 패키지 (패키지 수, PyTorch, CUDA)
8. 검증 결과 (발견/수정/남은 이슈)
