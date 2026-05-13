# AGENTS.md

이 저장소에서 작업하는 에이전트는 아래 규칙을 따른다.

## 기본 원칙

- 사용자 응답은 항상 한국어로 한다.
- 사용자의 의도가 불분명하면 추측하지 말고 먼저 질문해 범위를 확정한다.
- 범위가 명확한 작업은 중간 확인 질문을 반복하지 말고 끝까지 처리한 뒤 결과를 보고한다.
- 기존 코드와 문서의 구조를 우선 존중하고, 불필요한 광역 변경은 피한다.

## 작업 전 확인 문서

다음 문서를 우선 참고한다.

- `00_doc/sp00/d0001_prd.md`: 프로젝트 요구사항
- `00_doc/sp00/d0004_todo.md`: TODO 및 디버깅 추적

필요할 때만 아래 문서를 추가로 읽는다.

- `00_doc/sp00/d0010_history.md`: 변경 이력
- `00_doc/sp00/d0003_test.md`: 테스트 시나리오
- `00_doc/sp00/d0002_plan.md`: 구현 계획
- `00_doc/sp00/d0005_lib.md`: 라이브러리 정보
- `00_doc/sp00/d0006_db.md`: DB 구조
- `00_doc/sp00/d0009_env.md`: 환경 현황

## 구현 및 디버깅 규칙

- 에러나 재현 가능한 이슈를 발견하면 `00_doc/sp00/d0004_todo.md`의 디버깅 섹션에 먼저 기록하는 것을 우선 검토한다.
- 해결이 끝난 내용은 필요 시 `00_doc/sp00/d0010_history.md`에 반영한다.
- 테스트나 디버깅 명령은 현재 OS와 셸 환경에 맞는 형태로 실행한다.

## Windows 환경 주의사항

- 현재 작업공간은 Windows 기준으로 운영된다.
- 경로, 임시 디렉터리, Git 동작은 Windows 환경 변수와 셸 차이의 영향을 받을 수 있으므로 실패 시 경로 해석 문제를 먼저 의심한다.
- 특히 `TEMP`/`TMP` 설정 차이로 Git 명령이 실패할 수 있으니, 인덱스 파일 작성 오류가 나면 임시 디렉터리 설정을 점검한다.

## 문서화 기준

- 사용자 요청이 문서 변경까지 포함하면, 코드 수정과 함께 관련 문서도 갱신한다.
- 새 규칙이나 반복되는 운영 지식이 생기면 이 파일보다 구체적인 프로젝트 문서에 기록하고, 이 파일은 짧게 유지한다.

## ccporting 운영 규칙

- `ccporting` 스킬의 포팅/업데이트 기본 작업 경로는 `.agents/skills/`를 사용한다.
- `.claude/skills_to_codex/`는 필요 시에만 사용하는 임시 우회 경로로 제한한다.
- 포팅 실행 후 파일 확인/검토/검증 기준 경로는 `.agents/skills/`로 고정한다.

<!-- ccporting:claude-sync:start -->
## CLAUDE.md 동기화 정책 (ccporting 관리)

아래 내용은 `CLAUDE.md`에서 Codex 호환 규칙만 추출한 동기화 블록이다.

### 핵심 규칙
- **[최우선 원칙] 의도 파악 먼저**: 사용자의 의도가 불분명하면 작업 전에 반드시 질문할 것. 100번이라도 질문을 던져서 정확한 의도를 파악한 후 실행한다. 추측으로 진행하지 않는다.
- **[지식기반] oowiki 활용**: 작업 전·중에 관련 지식이 필요하면 반드시 `oowiki` 스킬을 통해 지식기반을 먼저 조회하고 활용한다.
- **언어**: 항상 한국어로 답변
- **세션 시작 시 필수**: 첫 메시지에 반드시 `oostart run` 실행
- **[Bash 도구 사용 정책]**
- **경로에 `home` 없음** (현재: `C:\Users\ookoo\doom\1_oo`): **Bash 도구 우선 사용**
- **경로에 `home` 포함** 시: Bash 도구 사용 금지 → `mcp__desktop-commander__start_process` 사용
- ⚠️ **주의**: Bash exit code 1 오류가 발생해도 실제 명령 실행 결과를 확인할 것 (TEMP/TMP 경로 불일치로 인한 오탐 가능)
- **`home` 포함 경로 사용 시 형식:**
- ```
- cmd /c "cd /d C:\Users\ookoo\home\1_oo && [명령어]"

### 행동 원칙
- **명확한 지시는 끝까지 완료**: 범위가 명확한 작업(넘버링, 포맷 통일 등)은 전체 처리 후 결과만 보고. 중간에 "X도 할까요?" 확인 질문 금지.

### 문서 규칙
- **표준넘버링**: md 문서의 섹션 제목에 `1`, `1.1`, `1.1.1` 형태로 번호를 부여하는 것. **모든 md 문서는 표준넘버링을 원칙으로 한다.**
- 예) `## 1. 개요` / `### 1.1 배경` / `#### 1.1.1 현황`

### 디버깅 규칙
- **에러 발생** → `d0004_todo.md` 디버깅 섹션에 기록
- **해결됨** → `d0010_history.md`로 이동
- **항상** OS 확인 후 해당 명령어 사용

### Windows 주의
- **원인**: Git Bash가 경로 내 `/home`을 특수 경로로 해석 → EPERM 오류
- **근본 해결**: 경로에서 `home` 제거 (현재 `doom`으로 변경 완료)
- **증상**: `claude update` 성공 표시되나 `claude --version` 변경 없음
- **원인**: `HOME`(`C:\Users\oaiskoo\home`) ≠ `USERPROFILE`(`C:\Users\oaiskoo`)로 claude.exe가 두 곳에 존재
- **해결**: HOME 쪽 삭제 후 `irm https://cli.anthropic.com/install.ps1 | iex` 재설치
- **체크**: `ooenv check` → "Claude Code 경로 중복 확인" 항목
- **증상**: `git add` / `git commit` 실행 시 "unable to write new index file" (exit 128)
- **원인**: Git Bash가 `TEMP=/tmp` (Unix 경로)를 설정 → MinGW `git.exe`가 Windows API에 `/tmp` 전달 → `C:\tmp` (존재하지 않음)로 해석 → 실패
- **영구 해결**: `~/.bashrc`에 아래 추가 후 `source ~/.bashrc`
- **임시 우회**: `GIT_TMPDIR=".git" git add ...`
- **자동 감지**: `ooenv check` → "[Git TEMP/TMP Check]" 항목 (미설정 시 ~/.bashrc 자동 추가)

<!-- ccporting:claude-sync:end -->
