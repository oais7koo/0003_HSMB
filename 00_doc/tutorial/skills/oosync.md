# oosync Tutorial

> Vibe 환경 동기화 스킬 | 버전: v14 | 카테고리: meta-util

## 1. 이 스킬은 왜 필요한가?

Vibe 환경 동기화 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oosync run

# 상태 확인
oosync status

# 도움말
oosync help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oosync help` | 서브명령어 목록 표시 |
| `oosync version` | 스킬 버전 정보 (v13) |
| `oosync status` | 서브명령어 리스트, 동기화 대상 현황 |
| `oosync check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oosync run` | 동기화 실행 |
| `oosync show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oosync add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oosync list` | 동기화 가능한 프로젝트 목록 조회 |
| `oosync files` | 동기화 대상 파일/폴더 목록 |
| `oosync view [project]` | 대상 프로젝트와 차이점 비교 (읽기 전용) |
| `oosync diff [project] [file]` | 특정 파일 내용 비교 (unified diff) |
| `oosync merge [project] [file]` | 양쪽 파일 병합 |
| `oosync run [project]` | 동기화 실행 (대화형) |
| `oosync run --push-only` | push만 필요한 모든 프로젝트 일괄 동기화 |
| `oosync run --push-only --add` | push 동기화 + 대상에만 있는 파일 삭제 없이 유지 |
| `oosync pipeline` | 표준 검증(ooenv standard) → 배포(run --push-only) 파이프라인 |
| `oosync pipeline --dry-run` | 표준 검증 후 동기화 미리보기 (실제 배포 안 함) |
| `oosync pipeline --force` | 표준 검증 실패해도 배포 강행 |
| `oosync pipeline --skip-standard` | 표준 검증 건너뛰고 바로 배포 |
| `oosync backup` | Claude 환경 파일을 data/04_claude_backup/YYMMDD-HHMMSS.zip으로 백업 |
| `oosync restore` | 백업 목록 조회 |
| `oosync restore YYMMDD-HHMMSS` | 특정 백업에서 복원 (예: `oosync restore 260323-085605`) |
| `oosync reset` | 소스/대상 프로젝트 동기화 설정 표시 |
| `oosync reset --targets /path1 /path2` | 대상 프로젝트 설정 (하나 이상, references/sync_config.json 저장) |
| `oosync reset --add /path` | 대상 프로젝트 추가 |
| `oosync reset --remove /path` | 대상 프로젝트 제거 |
| `oosync reset --clear` | 대상 프로젝트 전체 제거 |

실행: `uv run python .claude/skills/oosync/scripts/oosync_run.py [subcommand] [args]`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | OAIS 프로젝트와 3_code/ 독립 프로젝트 간 vibe 파일 동기화 |
| **하는 것** | .claude/ 파일 비교·복사, .claudeignore 적용, 동기화 결과 보고 |
| **하지 않는 것** | 코드 수정(→oodev), Git 커밋(→oocommit), 환경 점검(→ooenv) |
| **참조 범위** | 현재 프로젝트 + `OAIS_SYNC_TARGET` 환경변수 경로 (기본: `3_code/`) |
| **수정 대상** | 대상 프로젝트의 `.claude/` 관련 파일 |
| **실행 레벨** | [반자동] — 동기화 대상 확인 후 실행 |
| **에이전트 호환** | 범용 — 파일 복사 작업 중심 / `OAIS_SYNC_TARGET` 환경변수 필요 |

### ftp 동기화 (oosync ftp)

> SP별 FTP 서버와 로컬 폴더 간 동기화 | 설정: `references/ftp_config.json`

### FTP 명령어

| 명령어 | 설명 |
|--------|------|
| `oosync ftp help` | FTP 서브커맨드 도움말 |
| `oosync ftp status [SP]` | 접속 테스트 + 프로필 요약 |
| `oosync ftp list [SP]` | 리모트 파일 목록 조회 |
| `oosync ftp diff [SP]` | 로컬 vs 리모트 파일 비교 |
| `oosync ftp push [SP]` | 로컬 → 리모트 업로드 (삭제 후 전체 업로드) |
| `oosync ftp push [SP] --dry-run` | 업로드 미리보기 (실제 전송 안 함) |
| `oosync ftp pull [SP]` | 리모트 → 로컬 다운로드 |
| `oosync ftp pull [SP] --dry-run` | 다운로드 미리보기 |

실행: `uv run python .claude/skills/oosync/scripts/oosync_ftp.py [command] [SP] [--dry-run]`

### FTP 프로필 (SP별 매핑)

| SP | 이름 | 호스트 | 로컬 | 리모트 | 대상 |
|----|------|--------|------|--------|------|
| SP06 | 시니어세상 | seniorworld.co.kr | 06_SSweb/ | /www | css, index.html |
| SP07 | 케이웍스 | kworksk.co.kr | 07_KWweb/03_upload/ | /www | css, images, js, index.html |

### FTP 설정

- **비밀번호**: `.env`의 `FTP_PASS` (프로필별 개별 설정 가능: `password_env` 필드)
- **설정 파일**: `.claude/skills/oosync/references/ftp_config.json`
- **프로필 추가**: config에 SP 키 추가로 확장 가능

### 백업 대상 (oosync backup)

| 대상 | 설명 |
|------|------|
| `.claude/` | 폴더 통째로 (skills, agents, guides, templates, settings 등) |
| `CLAUDE.md` | 프로젝트 루트 설정 파일 |
| `.mcp.json` | MCP 서버 설정 파일 |
| `.omc/project-memory.json` | OMC 프로젝트 메모리 (세션 간 누적) |
| `pyproject.toml` | uv 의존성/프로젝트 설정 |
| `00_doc/tutorial/` | 튜토리얼 문서 (ootutorial 생성) |
| `cclaude.bat` | Windows Claude 실행 스크립트 |
| `cclaude.sh` | Linux/Mac Claude 실행 스크립트 |
| `qqlaude.bat` | Windows Ollama qwen3.5 Claude 실행 스크립트 |
| `gemma.ps1` | Windows Ollama gemma4:e4b 실행 스크립트 (PowerShell) |
| `gemma.sh` | Linux/Mac Ollama gemma4:e4b 실행 스크립트 |
| `.github/` | GitHub Actions, Dependabot 등 GitHub 설정 |
| `.claudeignore` | Claude Code 컨텍스트 제외 설정 (토큰 절감) |
| `~/.claude/.omc/hud-config.json` | HUD 표준 설정 (글로벌, `_home/` 아래 저장) |

**zip 구조**: 원본 경로 구조 그대로 유지 (HOME 기준 파일은 `_home/` 아래)

```
YYMMDD-HHMMSS.zip
├── .claude/          # 폴더 통째로
│   ├── skills/
│   ├── agents/
│   ├── guides/
│   ├── templates/
│   ├── CLAUDE.md
│   └── settings.json
├── CLAUDE.md         # 루트 설정 파일
├── .omc/project-memory.json  # OMC 프로젝트 메모리
├── .mcp.json         # MCP 서버 설정
├── pyproject.toml    # uv 의존성/프로젝트 설정
├── cclaude.bat       # Windows 실행 스크립트
├── cclaude.sh        # Linux/Mac 실행 스크립트
├── gemma.ps1         # Windows Ollama gemma4 실행 스크립트 (PowerShell)
├── gemma.sh          # Linux/Mac Ollama gemma4 실행 스크립트
└── _home/            # HOME 기준 글로벌 파일
    └── .claude/.omc/hud-config.json  # HUD 표준 설정
```

**저장 위치**: `data/04_claude_backup/`
**제외**: `__pycache__/`, `data/` (백업 폴더 자체 제외)

### 동기화 대상

**.claude/**: *.md, settings.json, commands/, skills/, agents/, guides/

**루트 설정**: CLAUDE.md, .mcp.json, .claudeignore, cclaude.bat, cclaude.sh

**문서**: 00_doc/tutorial/

**참고**: `v/`는 레거시 폴더로, 최초 삭제 후 동기화 대상에서 제외

### 비교 기준

| 상태 | 설명 | 표시 |
|------|------|------|
| ONLY_SOURCE | 현재 프로젝트에만 존재 | `->` |
| ONLY_TARGET | 대상 프로젝트에만 존재 | `<-` |
| NEWER_SOURCE | 현재 프로젝트가 최신 | `>>` |
| NEWER_TARGET | 대상 프로젝트가 최신 | `<<` |
| SAME | 동일 | `==` |

### 병합 규칙

1. **문서 이력 관리**: 양쪽 이력 통합 + 병합 버전 추가
2. **서브명령어 표**: 양쪽 명령어 합집합
3. **섹션**: 한쪽에만 있으면 추가, 양쪽 있으면 최신 버전
4. **의존성**: 양쪽 패키지 합집합

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oosync run
```

### 서브명령어 활용
```bash
oosync run  # 동기화 실행
oosync list  # 동기화 가능한 프로젝트 목록 조회
oosync files  # 동기화 대상 파일/폴더 목록
oosync pipeline  # 표준 검증(ooenv standard) → 배포(run --push-only) 파이프라인
oosync backup  # Claude 환경 파일을 data/04_claude_backup/YYMMDD-HHMMSS.zip으로 백업
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/oosync/scripts/oosync_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 스캔 | Explore | haiku | 프로젝트 구조 탐색 | O |
| 동기화 | task-executor | sonnet | 파일 복사/동기화 실행 | O |
| 검증 | task-checker | sonnet | 동기화 결과 검증 | - |

<!-- RUN-UPDATE-REF:START -->

## 10. 관련 스킬

`.claude/skills/oostart/SKILL.md` | `.claude/skills/ooenv/SKILL.md` | `.claude/guides/common_guide.md`

---

> 생성일: 2026-04-17 19:50 | ootutorial v02
