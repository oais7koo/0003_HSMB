# CLAUDE.md - 프로젝트 설정 (최소화)

## 필수 규칙

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

## 글로벌 참조 (중복 방지)

- **OMC 설정**: `~/.claude/CLAUDE.md`
- **프로젝트 가이드**: `.claude/guides/common_guide.md`
- **스킬/에이전트 카탈로그**: `.claude/CLAUDE.md`

## 필수 문서 (Auto-load)

> 다음 2개만 항상 로드됨 (context 효율성 위해 최소화)

| 문서 | 용도 |
|------|------|
| @00_doc/sp00/d0001_prd.md | PRD - 프로젝트 요구사항 |
| @00_doc/sp00/d0004_todo.md | TODO/디버깅 - 이슈 추적 |

## 참고 문서 (On-demand)

> 필요할 때 Read 도구로 명시적 로드

| 문서 | 용도 | 로드 방법 |
|------|------|---------|
| d0010_history.md | 변경 이력 | `Read("00_doc/sp00/d0010_history.md")` |
| d0003_test.md | 테스트 시나리오 | `Read("00_doc/sp00/d0003_test.md")` |
| d0002_plan.md | 구현 계획 | `Read("00_doc/sp00/d0002_plan.md")` |
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

### TEMP/TMP 경로 불일치 문제
- **증상**: Bash exit code 1, `/d/1_oo/tmp/...` 오류
- **원인**: TEMP/TMP 환경변수가 이전 경로(`D:\1_oo\tmp`) 가리킴
- **대응**: 명령 실행 결과(stdout)를 확인하여 실제 성공 여부 판단

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

## Task Master AI

**자세한 설명**: `.taskmaster/CLAUDE.md`

핵심 명령어:
- `task-master init` - 초기화
- `task-master next` - 다음 작업
- `task-master show <id>` - 상세 정보
