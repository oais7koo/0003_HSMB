# CLAUDE.md - 프로젝트 설정 (최소화)

## 필수 규칙

> **[최우선 원칙] 의도 파악 먼저**: 사용자의 의도가 불분명하면 작업 전에 반드시 질문할 것. 100번이라도 질문을 던져서 정확한 의도를 파악한 후 실행한다. 추측으로 진행하지 않는다.

> **[지식기반] oowiki 활용**: 작업 전·중에 관련 지식이 필요하면 반드시 `oowiki` 스킬을 통해 지식기반을 먼저 조회하고 활용한다.

> **언어**: 항상 한국어로 답변

> **세션 시작 시 필수**: 첫 메시지에 반드시 `oostart run` 실행

> **[Bash 도구 사용 정책]**
> - **경로에 `home` 없음** (현재: `C:\Users\ookoo\doom\1_oo`): **Bash 도구 우선 사용**
> - **경로에 `home` 포함** 시: Bash 도구 사용 금지 → `mcp__desktop-commander__start_process` 사용
>
> ⚠️ **주의**: Bash exit code 1 오류가 발생해도 실제 명령 실행 결과를 확인할 것 (TEMP/TMP 경로 불일치로 인한 오탐 가능)
>
> **`home` 포함 경로 사용 시 형식:**
> ```
> cmd /c "cd /d C:\Users\ookoo\home\1_oo && [명령어]"
> ```

## 행동 원칙

> **명확한 지시는 끝까지 완료**: 범위가 명확한 작업(넘버링, 포맷 통일 등)은 전체 처리 후 결과만 보고. 중간에 "X도 할까요?" 확인 질문 금지.

## ccporting 운영 규칙

- `ccporting` 포팅/업데이트 기본 경로는 `.agents/skills/`를 사용한다.
- `.claude/skills_to_codex/`는 권한/환경 이슈 시에만 임시 우회 경로로 사용한다.
- 포팅 후 확인/검토/검증 기준 경로는 `.agents/skills/`로 고정한다.

## 문서 규칙

> **표준넘버링**: md 문서의 섹션 제목에 `1`, `1.1`, `1.1.1` 형태로 번호를 부여하는 것. **모든 md 문서는 표준넘버링을 원칙으로 한다.**
>
> 예) `## 1. 개요` / `### 1.1 배경` / `#### 1.1.1 현황`

## 글로벌 참조 (중복 방지)

- **OMC 설정**: `~/.claude/CLAUDE.md`
- **프로젝트 가이드**: `.claude/guides/common_guide.md`
- **스킬/에이전트 카탈로그**: `.claude/CLAUDE.md`

## 필수 문서 (Auto-load)

> 다음 3개만 항상 로드됨 (context 효율성 위해 최소화)

| 문서 | 용도 |
|------|------|
| @00_doc/sp00/d0001_prd.md | PRD - 프로젝트 요구사항 |
| @00_doc/sp00/d0004_todo.md | TODO/디버깅 - 이슈 추적 |
| @00_doc/sp00/d0002_plan.md | 구현 계획 |

## 참고 문서 (On-demand)

> 필요할 때 Read 도구로 명시적 로드

| 문서 | 용도 | 로드 방법 |
|------|------|---------|
| d0010_history.md | 변경 이력 | `Read("00_doc/sp00/d0010_history.md")` |
| d0003_test.md | 테스트 시나리오 | `Read("00_doc/sp00/d0003_test.md")` |
| d0005_lib.md | 라이브러리 정보 | `Read("00_doc/sp00/d0005_lib.md")` |
| d0006_db.md | DB 구조 | `Read("00_doc/sp00/d0006_db.md")` |
| d0009_env.md | 환경 현황 | `Read("00_doc/sp00/d0009_env.md")` |

## 디버깅 규칙

- **에러 발생** → `d0004_todo.md` 디버깅 섹션에 기록
- **해결됨** → `d0010_history.md`로 이동
- **항상** OS 확인 후 해당 명령어 사용

## Windows 환경 주의사항

### Bash 사용 정책

| 조건 | 도구 | 비고 |
|------|------|------|
| 경로에 `home` 없음 (현재) | **Bash 우선 사용** | exit code 1 오탐 주의 |
| 경로에 `home` 포함 | desktop-commander | EPERM 오류 발생 |

### Bash 경로 문제 (home 포함 경로)
- **원인**: Git Bash가 경로 내 `/home`을 특수 경로로 해석 → EPERM 오류
- **근본 해결**: 경로에서 `home` 제거 (현재 `doom`으로 변경 완료)

### HOME/USERPROFILE 경로 불일치 문제
- **증상**: `claude update` 성공 표시되나 `claude --version` 변경 없음
- **원인**: `HOME`(`C:\Users\oaiskoo\home`) ≠ `USERPROFILE`(`C:\Users\oaiskoo`)로 claude.exe가 두 곳에 존재
- **해결**: HOME 쪽 삭제 후 `irm https://cli.anthropic.com/install.ps1 | iex` 재설치
- **체크**: `ooenv check` → "Claude Code 경로 중복 확인" 항목

### TEMP/TMP 경로 불일치 문제 (MinGW git.exe 호환)
- **증상**: `git add` / `git commit` 실행 시 "unable to write new index file" (exit 128)
- **원인**: Git Bash가 `TEMP=/tmp` (Unix 경로)를 설정 → MinGW `git.exe`가 Windows API에 `/tmp` 전달 → `C:\tmp` (존재하지 않음)로 해석 → 실패
- **영구 해결**: `~/.bashrc`에 아래 추가 후 `source ~/.bashrc`
  ```bash
  export TEMP=$(cygpath -m /tmp)
  export TMP=$(cygpath -m /tmp)
  ```
- **임시 우회**: `GIT_TMPDIR=".git" git add ...`
- **자동 감지**: `ooenv check` → "[Git TEMP/TMP Check]" 항목 (미설정 시 ~/.bashrc 자동 추가)

## 모델 캐시 규칙

> **캐시 파일**: `~/.claude/.omc/model-cache.json`
> **형식**: `{"model": "opus-4-6", "updatedAt": "ISO", "source": "oostart|manual"}`

| 시점 | 동작 |
|------|------|
| `oostart run` | 현재 모델 자동 감지 → 캐시 기록 |
| `/model` 변경 후 | `model-cache.json` 즉시 업데이트 |
| `ootoken` | 캐시에서 모델명 읽어 헤더에 표시 |

## HUD 설정

> 프리셋: `minimal` | maxOutputLines: 3
> 설정 파일: `~/.claude/.omc/hud-config.json`
> 표준 레퍼런스: `.claude/skills/ooenv/references/hud-config-default.json`

**활성 요소**: omcLabel, model(short), rateLimits, ralph, contextBar, background, agents, todos

**복원 명령**:
```bash
cp .claude/skills/ooenv/references/hud-config-default.json ~/.claude/.omc/hud-config.json
```
