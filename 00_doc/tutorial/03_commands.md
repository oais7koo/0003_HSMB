# 범용 명령어 (sc/) 사용법

> `ooenv tutorial --update`로 현행화 | 소스: `.claude/commands/sc/*.md`

## 개요

SuperClaude 범용 명령어. MCP 서버(Sequential/Context7/Magic/Playwright)와 페르소나 자동 연동.
oo 스킬이 프로젝트 특화라면, sc/ 명령어는 **범용 개발 작업**에 사용.

## 명령어 목록

### 분석

| 명령 | 용도 | 연관 oo |
|------|------|---------|
| `/analyze [대상]` | 코드/시스템 분석 | oocheck |
| `/troubleshoot [증상]` | 문제 원인 추적 | oocheck, oofix |
| `/explain [주제]` | 코드/개념 설명 | - |

```bash
/analyze src/api.py --focus security
/troubleshoot "ImportError: no module named X"
/explain "이 함수의 동작 원리를 설명해줘"
```

### 개발

| 명령 | 용도 | 연관 oo |
|------|------|---------|
| `/implement [기능]` | 기능 구현 | oodev |
| `/build [대상]` | 프로젝트 빌드 | oodev, oorun |
| `/design [도메인]` | 시스템 설계 | ooprd, ooplan |

```bash
/implement "사용자 인증 API" --type api
/build --framework fastapi
/design "추천 시스템 아키텍처"
```

### 품질

| 명령 | 용도 | 연관 oo |
|------|------|---------|
| `/improve [대상]` | 코드 개선 | oofix |
| `/cleanup [대상]` | 코드/프로젝트 정리 | oolib |
| `/test [타입]` | 테스트 실행/생성 | ootest |

```bash
/improve src/ --focus performance
/cleanup --scope project
/test e2e --playwright
```

### 문서/관리

| 명령 | 용도 | 연관 oo |
|------|------|---------|
| `/document [대상]` | 문서화 | oodoc |
| `/git [작업]` | Git 작업 | oocommit |
| `/estimate [대상]` | 개발 추정 | - |
| `/task [작업]` | 태스크 관리 | ootodo, ooplan |

```bash
/document src/api.py
/git commit --message "feat: 인증 기능 추가"
/estimate "결제 모듈 구현"
```

### 오케스트레이션

| 명령 | 용도 |
|------|------|
| `/spawn [모드]` | 서브에이전트 생성/위임 |
| `/load [경로]` | 프로젝트 컨텍스트 로드 |
| `/index [쿼리]` | 명령어 카탈로그 탐색 |

## 플래그 (Flags)

| 플래그 | 효과 |
|--------|------|
| `--think` | 심층 분석 (~4K 토큰) |
| `--think-hard` | 시스템 분석 (~10K 토큰) |
| `--uc` | 토큰 압축 (30~50% 절감) |
| `--validate` | 실행 전 검증 |
| `--focus security` | 보안 중점 |
| `--focus performance` | 성능 중점 |
| `--seq` | Sequential MCP 활성화 |
| `--c7` | Context7 (라이브러리 문서) |
| `--loop` | 반복 개선 모드 |
| `--delegate auto` | 서브에이전트 자동 위임 |

## OMC (oh-my-claudecode) 명령어

| 명령 | 용도 |
|------|------|
| `/oh-my-claudecode:autopilot` | 완전 자율 실행 |
| `/oh-my-claudecode:ralph` | 완료까지 반복 실행 |
| `/oh-my-claudecode:ultrawork` | 병렬 최대 처리 |
| `/oh-my-claudecode:team N:executor "작업"` | N개 에이전트 팀 |
| `/oh-my-claudecode:plan` | 전략 계획 |
| `/oh-my-claudecode:trace` | 증거 기반 추적 |
| `/oh-my-claudecode:hud` | HUD 설정 |

```bash
/oh-my-claudecode:autopilot "결제 시스템 구현해줘"
/oh-my-claudecode:team 3:executor "API 리팩토링"
```

## oo 스킬 vs sc/ 명령어 선택 기준

| 상황 | 권장 |
|------|------|
| OAIS 문서(d0001~d0010) 연동 필요 | **oo 스킬** |
| SP 컨텍스트 기반 작업 | **oo 스킬** |
| 일반 코드 분석/개선 | **sc/ 명령어** |
| 빠른 단발성 작업 | **sc/ 명령어** |
| 자율 복잡 작업 | **OMC 명령어** |
