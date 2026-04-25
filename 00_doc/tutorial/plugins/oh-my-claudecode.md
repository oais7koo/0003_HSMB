# 플러그인: oh-my-claudecode (OMC)

> Claude Code용 멀티에이전트 오케스트레이션 레이어 | 필수 ★

## 개요

oh-my-claudecode(OMC)는 Claude Code에 전문화 에이전트 팀, 고급 워크플로우, 상태 관리를 추가하는 플러그인입니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `oh-my-claudecode` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | ★ 필수 |
| 설치 명령어 | `/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode` → `/plugin install oh-my-claudecode` → `/oh-my-claudecode:omc-setup` |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| 에이전트 오케스트레이션 | `explore`, `executor`, `verifier` 등 전문 에이전트 자동 라우팅 |
| Team 파이프라인 | `plan → prd → exec → verify → fix` 자동화 |
| Wave 모드 | 복잡한 작업을 다단계 파동으로 처리 |
| HUD | 상태바에 현재 작업/토큰 현황 표시 |
| Ralph 모드 | 완료될 때까지 반복 실행 (`--ralph`) |

## 주요 스킬 명령어

| 명령어 | 설명 |
|--------|------|
| `/oh-my-claudecode:autopilot` | 아이디어 → 동작 코드 자동 생성 |
| `/oh-my-claudecode:team` | N개 에이전트 팀 조율 |
| `/oh-my-claudecode:ralph` | 완료 보장 루프 (`"ralph"` 키워드로 트리거) |
| `/oh-my-claudecode:ultrawork` | 최대 병렬 처리 (`"ulw"` 키워드) |
| `/oh-my-claudecode:ralplan` | 합의 기반 계획 수립 |
| `/oh-my-claudecode:omc-help` | OMC 도움말 |
| `/oh-my-claudecode:cancel` | 실행 중인 작업 취소 |

## 에이전트 카탈로그 (주요)

| 에이전트 | 모델 | 용도 |
|---------|------|------|
| `explore` | haiku | 코드베이스 탐색 |
| `executor` | sonnet | 코드 구현/리팩토링 |
| `verifier` | sonnet | 완료 검증 |
| `planner` | opus | 태스크 시퀀싱 |
| `architect` | opus | 시스템 설계 |
| `debugger` | sonnet | 버그 추적 |
| `code-reviewer` | opus | 포괄적 코드 리뷰 |

## 키워드 자동 트리거

| 키워드 | 활성화 스킬 |
|--------|-----------|
| `"autopilot"`, `"build me"` | autopilot |
| `"ralph"`, `"don't stop"` | ralph |
| `"ulw"`, `"ultrawork"` | ultrawork |
| `"ralplan"`, `"consensus plan"` | ralplan |
| `"team"` | team |
| `"cancelomc"` | cancel |

## 사용 예시

```bash
# 1. 자동 실행 (이슈 → 코드 완성)
"새 기능 구현해줘: 사용자 로그인"  # autopilot 트리거

# 2. 팀 모드로 복잡한 리팩토링
/oh-my-claudecode:team "인증 시스템 전면 리팩토링"

# 3. 완료 보장 모드
"이 버그 ralph로 고쳐줘"  # ralph 트리거 → 완료될 때까지 반복

# 4. 계획 수립
/oh-my-claudecode:ralplan  # 플래너/아키텍트/크리틱이 합의 도출

# 5. 상태 확인
/oh-my-claudecode:hud  # 현재 실행 상태 HUD 표시
```

## oo 스킬과 연계

| oo 스킬 | OMC 에이전트 |
|---------|------------|
| `oodev` | executor |
| `oocheck` | code-reviewer |
| `ooplan` | planner + architect |
| `oofix` | debugger + executor |

## 설정 파일

| 파일 | 역할 |
|------|------|
| `~/.claude/.omc/hud-config.json` | HUD 프리셋 설정 |
| `.omc/state/` | 실행 상태 저장 |
| `.omc/notepad.md` | 작업 메모 |
| `.omc/project-memory.json` | 프로젝트 메모리 |

---

> 생성일: 2026-04-02 | ootutorial v01
