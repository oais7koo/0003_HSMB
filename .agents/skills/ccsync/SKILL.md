---
name: ccsync
description: "프로젝트 간 **바이브셋** 동기화 | ref: `.codex/guides/common_guide.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# ccsync - Vibe 환경 동기화 (바이브셋 동기화)



> 프로젝트 간 **바이브셋** 동기화 | ref: `.codex/guides/common_guide.md`

>

> **바이브셋**: oosync로 동기화 관리하는 바이브 코딩 환경 파일 일체 (`.codex/`, `CLAUDE.md`, `.mcp.json`, `.claudeignore` 등). oosync는 바이브셋을 프로젝트 간에 배포·동기화하는 전담 스킬이다.



## 0. 스킬 요약



| 항목 | 내용 |

|------|------|

| **핵심 역할** | OAIS 프로젝트와 3_code/ 독립 프로젝트 간 vibe 파일 동기화 |

| **하는 것** | .codex/ 파일 비교·복사, .claudeignore 적용, 동기화 결과 보고 |

| **하지 않는 것** | 코드 수정(→ccdev), Git 커밋(→cccommit), 환경 점검(→ooenv) |

| **참조 범위** | 현재 프로젝트 + `OAIS_SYNC_TARGET` 환경변수 경로 (기본: `3_code/`) |

| **수정 대상** | 대상 프로젝트의 `.codex/` 관련 파일 |

| **실행 레벨** | [반자동] — 동기화 대상 확인 후 실행 |

| **에이전트 호환** | 범용 — 파일 복사 작업 중심 / `OAIS_SYNC_TARGET` 환경변수 필요 |



## 개요



현재 프로젝트(1_oo)와 3_code/ 내 프로젝트 간에 vibe 관련 파일/폴더를 비교하고 동기화합니다.



## 명령어



| 명령어 | 설명 |

|--------|------|

| `ccsync help` | 서브명령어 목록 표시 |

| `ccsync version` | 스킬 버전 정보 (v15) |

| `ccsync status` | 서브명령어 리스트, 동기화 대상 현황 |

| `ccsync check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |

| `ccsync run` | 동기화 실행 |

| `ccsync show checklist` | 역할 수행 체크리스트 표시 | 터미널 |

| `ccsync add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |

| `ccsync list` | 동기화 가능한 프로젝트 목록 조회 |

| `ccsync files` | 동기화 대상 파일/폴더 목록 |

| `ccsync view [project]` | 대상 프로젝트와 차이점 비교 (읽기 전용) |

| `ccsync diff [project] [file]` | 특정 파일 내용 비교 (unified diff) |

| `ccsync merge [project] [file]` | 양쪽 파일 병합 |

| `ccsync run [project]` | 동기화 실행 (대화형) |

| `ccsync run --push-only` | push만 필요한 모든 프로젝트 일괄 동기화 (대상 전용 파일은 삭제 여부를 대화형으로 질문) |

| `ccsync run --push-only --add` | push 동기화 + 대상에만 있는 파일을 질문 없이 유지 |

| `ccsync run --push-only --delete` | push 동기화 + 대상에만 있는 파일을 질문 없이 삭제 |

| `ccsync pipeline` | 표준 검증(ooenv standard) → 배포(run --push-only) 파이프라인 |

| `ccsync pipeline --dry-run` | 표준 검증 후 동기화 미리보기 (실제 배포 안 함) |

| `ccsync pipeline --force` | 표준 검증 실패해도 배포 강행 |

| `ccsync pipeline --skip-standard` | 표준 검증 건너뛰고 바로 배포 |

| `ccsync backup` | Codex 환경 파일을 data/04_claude_backup/YYMMDD-HHMMSS.zip으로 백업 |

| `ccsync restore` | 백업 목록 조회 |

| `ccsync restore YYMMDD-HHMMSS` | 특정 백업에서 복원 (예: `ccsync restore 260323-085605`) |

| `ccsync reset` | 소스/대상 프로젝트 동기화 설정 표시 |

| `ccsync reset --targets /path1 /path2` | 대상 프로젝트 설정 (하나 이상, references/sync_config.json 저장) |

| `ccsync reset --add /path` | 대상 프로젝트 추가 |

| `ccsync reset --remove /path` | 대상 프로젝트 제거 |

| `ccsync reset --clear` | 대상 프로젝트 전체 제거 |



실행: `uv run python .agents/skills/ccsync/scripts/oosync_run.py [subcommand] [args]`



## FTP 동기화 (ccsync ftp)



> SP별 FTP 서버와 로컬 폴더 간 동기화 | 설정: `references/ftp_config.json`



### FTP 명령어



| 명령어 | 설명 |

|--------|------|

| `ccsync ftp help` | FTP 서브커맨드 도움말 |

| `ccsync ftp status [SP]` | 접속 테스트 + 프로필 요약 |

| `ccsync ftp list [SP]` | 리모트 파일 목록 조회 |

| `ccsync ftp diff [SP]` | 로컬 vs 리모트 파일 비교 |

| `ccsync ftp push [SP]` | 로컬 → 리모트 업로드 (삭제 후 전체 업로드) |

| `ccsync ftp push [SP] --dry-run` | 업로드 미리보기 (실제 전송 안 함) |

| `ccsync ftp pull [SP]` | 리모트 → 로컬 다운로드 |

| `ccsync ftp pull [SP] --dry-run` | 다운로드 미리보기 |



실행: `uv run python .agents/skills/ccsync/scripts/oosync_ftp.py [command] [SP] [--dry-run]`



### FTP 프로필 (SP별 매핑)



| SP | 이름 | 호스트 | 로컬 | 리모트 | 대상 |

|----|------|--------|------|--------|------|

| SP06 | 시니어세상 | seniorworld.co.kr | 06_SSweb/ | /www | css, index.html |

| SP07 | 케이웍스 | kworksk.co.kr | 07_KWweb/03_upload/ | /www | css, images, js, index.html |



### FTP 설정



- **비밀번호**: `.env`의 `FTP_PASS` (프로필별 개별 설정 가능: `password_env` 필드)

- **설정 파일**: `.agents/skills/ccsync/references/ftp_config.json`

- **프로필 추가**: config에 SP 키 추가로 확장 가능



## 백업 대상 (ccsync backup)



| 대상 | 설명 |

|------|------|

| `.codex/` | 폴더 통째로 (skills, agents, guides, templates, settings 등) |

| `00_doc/tutorial/` | OAIS 튜토리얼 문서 (동기화·백업 대상) |

| `CLAUDE.md` | 프로젝트 루트 설정 파일 |

| `.mcp.json` | MCP 서버 설정 파일 |

| `.omc/project-memory.json` | OMC 프로젝트 메모리 (세션 간 누적) |

| `pyproject.toml` | uv 의존성/프로젝트 설정 |

| `cclaude.bat` | Windows Codex 실행 스크립트 |

| `cclaude.sh` | Linux/Mac Codex 실행 스크립트 |

| `qqlaude.bat` | Windows Ollama qwen3.5 Codex 실행 스크립트 |

| `gemma.ps1` | Windows Ollama gemma4:e4b 실행 스크립트 (PowerShell) |

| `gemma.sh` | Linux/Mac Ollama gemma4:e4b 실행 스크립트 |

| `.github/` | GitHub Actions, Dependabot 등 GitHub 설정 |

| `.agents/` | ccporting 배포 스킬 및 에이전트 설정 |

| `AGENTS.md` | 에이전트 설정 루트 파일 |

| `.claudeignore` | Codex 컨텍스트 제외 설정 (토큰 절감) |

| `~/.codex/.omc/hud-config.json` | HUD 표준 설정 (글로벌, `_home/` 아래 저장) |



**zip 구조**: 원본 경로 구조 그대로 유지 (HOME 기준 파일은 `_home/` 아래)



```

YYMMDD-HHMMSS.zip

├── .codex/          # 폴더 통째로

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

    └── .codex/.omc/hud-config.json  # HUD 표준 설정

```



**저장 위치**: `data/04_claude_backup/`

**제외**: `__pycache__/`, `data/` (백업 폴더 자체 제외)



## 동기화 대상



**.codex/**: *.md, settings.json, commands/, skills/, agents/, guides/



**루트 설정**: CLAUDE.md, AGENTS.md, .mcp.json, .claudeignore, cclaude.bat, cclaude.sh, gemma.ps1, gemma.sh

**Codex/Agents**: .codex/, .agents/, .gemini/

**GitHub**: .github/

**튜토리얼**: 00_doc/tutorial/



**참고**: `v/`는 레거시 폴더로, 최초 삭제 후 동기화 대상에서 제외



## 비교 기준



| 상태 | 설명 | 표시 |

|------|------|------|

| ONLY_SOURCE | 현재 프로젝트에만 존재 | `->` |

| ONLY_TARGET | 대상 프로젝트에만 존재 | `<-` |

| NEWER_SOURCE | 현재 프로젝트가 최신 | `>>` |

| NEWER_TARGET | 대상 프로젝트가 최신 | `<<` |

| SAME | 동일 | `==` |



## 병합 규칙



1. **문서 이력 관리**: 양쪽 이력 통합 + 병합 버전 추가

2. **서브명령어 표**: 양쪽 명령어 합집합

3. **섹션**: 한쪽에만 있으면 추가, 양쪽 있으면 최신 버전

4. **의존성**: 양쪽 패키지 합집합



## 설정 파일 분리 패턴



`settings.json`은 동기화 대상이지만 `settings.local.json`은 제외됩니다. 프로젝트마다 다른 설정은 `settings.local.json`에 작성합니다.



| 파일 | 역할 | ccsync | git |

|------|------|--------|-----|

| `settings.json` | 공통 설정 (훅, 권한, 모델 등) | 동기화 O | 커밋 O |

| `settings.local.json` | 프로젝트별 설정 (플러그인 활성화 등) | 동기화 X | .gitignore 권장 |



**예시** — 특정 프로젝트에서만 obsidian 플러그인 활성화:

```json

{

  "enabledPlugins": {

    "obsidian@obsidian-skills": true,

    "paper-search-tools@codex-settings": true

  }

}

```



## 동기화 제외 대상



`__pycache__/`, `*.pyc`, `.git/`, `tmp/`, `data/`, `.venv/`, `node_modules/`, `worktrees/`, `.codex/settings.local.json`, `scheduled_tasks.lock`



## 에이전트 출력 규칙



| 규칙 | 설명 |

|------|------|

| 스크립트 출력만 표시 | 스크립트가 출력하는 내용 그대로 표시 |

| 별도 요약 금지 | 에이전트가 임의로 요약/통계 추가하지 않음 |

| 템플릿 형식 준수 | 각 명령어별 템플릿(`.agents/skills/ccsync/templates/oosync_*.md`) 형식 따름 |



## 서브에이전트



| 단계 | 에이전트 | 모델 | 역할 | 병렬 |

|------|----------|------|------|:----:|

| 스캔 | Explore | haiku | 프로젝트 구조 탐색 | O |

| 동기화 | task-executor | sonnet | 파일 복사/동기화 실행 | O |

| 검증 | task-checker | sonnet | 동기화 결과 검증 | - |



<!-- RUN-UPDATE-REF:START -->



## run과 update 분리 원칙



> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.



| 서브커맨드 | 역할 |

|-----------|------|

| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |

| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |



> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.



<!-- RUN-UPDATE-REF:END -->



<!-- GEMMA-REF:START -->



## Gemma 위임 (로컬 LLM)



> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은

> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.



| 항목 | 내용 |

|------|------|

| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |

| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |

| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |

| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |



<!-- GEMMA-REF:END -->

<!-- SAMPLE-REF:START -->



## 샘플 참조 (산출물 품질 향상)



> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.



| 항목 | 내용 |

|------|------|

| 샘플 위치 | `.agents/skills/{스킬명}/samples/` |

| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |

| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |

| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |

| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |



<!-- SAMPLE-REF:END -->



## 관련 문서



`.agents/skills/ccstart/SKILL.md` | `.agents/skills/ooenv/SKILL.md` | `.codex/guides/common_guide.md`

