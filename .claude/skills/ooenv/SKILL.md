---
name: ooenv
description: "개발 환경 및 스킬 정합성 검증 스킬 'ooenv', '환경 점검', '환경 검증', 'UV 의존성', '컨텍스트 관리' 등을 요청할 때 사용한다"
model: opus
metadata:
  version: "v19"
  category: "doc-env"
---

# ooenv - 개발 환경 및 스킬 정합성 검증

> 공통: `.claude/guides/common_guide.md` 참조

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 개발 환경(플러그인·Python 의존성·스킬 정합성) 일괄 점검 및 수정 |
| **하는 것** | uv 의존성 확인, 플러그인 상태 점검, d0009_env.md 현행화, 스킬 alias 관리 |
| **하지 않는 것** | 코드 품질 체크(→oocheck), 패키지 업데이트(→oouv) |
| **참조 범위** | 현재 프로젝트 + 로컬 환경 설정 파일 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp00/d0009_env.md` |
| **실행 레벨** | [자동] — 환경 스캔 후 d0009 자동 생성/갱신 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 스크립트 및 플러그인 시스템 사용 / 다른 에이전트: uv 명령 수동 실행 후 결과를 d0009에 직접 기록 |

## 문서 이력 관리
- v19 2026-04-19 — context validate → context check 통합
- v18 2026-04-18 — VS Code 워크스페이스 설정 동기화 주의사항 추가 — markdown preview 자동 설정 제거
- v17 2026-04-17 — 필수 플러그인 `andrej-karpathy-skills` 등록 — Karpathy LLM 코딩 가이드라인 (CLAUDE.md 기반)
- v16 2026-04-16 — settings.local.json 설정 분리 패턴 추가 — 프로젝트별 설정 관리 방법
- v15 2026-04-16 — machines.json alias 필드 전체 삭제 — hostname이 식별자, alias 불필요. 등록 가이드에 alias 미사용 명시

---

## 1. 개요

개발 전 환경 점검 통합 스킬 - 플러그인, Python 의존성, 스킬 정합성 일괄 점검/수정

> **바이브셋**: oosync로 동기화 관리하는 바이브 코딩 환경 파일 일체 (`.claude/`, `CLAUDE.md`, `.mcp.json`, `.claudeignore` 등). ooenv는 바이브셋의 상태를 점검·관리한다.

**관련:** `.claude/skills/oostart/SKILL.md`, `.claude/skills/oocheck/SKILL.md`, `.claude/guides/common_guide.md`

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooenv help` | 서브명령어 목록 표시 | 터미널 |
| `ooenv version` | 스킬 버전 정보 (v08) | 터미널 |
| `ooenv status` | 서브명령어 리스트, 상태 요약 | 터미널 |
| `ooenv standard` | 표준 스펙(d0012)과 현재 환경 비교 (PASS/FAIL) | 터미널 |
| `ooenv standard --fix` | 비교 후 자동 수정 (플러그인 추가 + 수동항목 안내) | 터미널 |
| `ooenv run` | 통합 점검 + 자동 수정 + 상세 출력 | **d0009_env.md** + 터미널 |
| `ooenv run --dry-run` | 점검만 (수정 안 함) | 터미널 |
| `ooenv plugin` | 플러그인 상태 확인 | 설치 가이드 |
| `ooenv check` | 스킬 정합성 검증 | d{SP}0004 업데이트 |
| `ooenv show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooenv add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ooenv check --full` | oo*.md 전체 스캔 - 에이전트/커맨드/MCP 참조 검증 | 터미널 + d{SP}0004 |
| `ooenv agent` | 에이전트 경로 검증 | 터미널 + d{SP}0004 |
| `ooenv structure` | 문서 구조 검증 | 터미널 |
| `ooenv reflect` | 설정 파일 반영 검증 | 터미널 + d{SP}0004 |
| `ooenv command` | .claude/commands/sc/ 연동 검증 | 터미널 + d{SP}0004 |
| `ooenv uv check` | UV 의존성 상태 체크 | 터미널 + d{SP}0004 |
| `ooenv uv update` | UV 의존성 업데이트 | 패키지 업데이트 |
| `ooenv uv cleanup` | 미사용 패키지 탐지 및 삭제 | 터미널 (대화형) |
| `ooenv cli` | CLI 도구 현황 확인 (npm global, uv tools) | 터미널 |
| `ooenv cli check` | CLI 설치 상태 및 버전 확인 | 터미널 |
| `ooenv cli update` | CLI 도구 업데이트 | 터미널 |
| `ooenv cli add <pkg>` | CLI 도구 설치 | 터미널 |
| `ooenv cli remove <pkg>` | CLI 도구 제거 | 터미널 |
| `ooenv mcp` | MCP 서버 현황 확인 (필수/선택 상태) | 터미널 |
| `ooenv mcp check` | MCP 설치/등록 상태 확인 | 터미널 |
| `ooenv mcp add <srv>` | MCP 서버 npm 설치 | 터미널 |
| `ooenv mcp remove <srv>` | MCP 서버 npm 제거 | 터미널 |
| `ooenv context status` | 컨텍스트 전체 상태 | 터미널 |
| `ooenv context token` | 토큰 사용량 추정 | 터미널 |
| `ooenv context files` | 컨텍스트 파일 목록 | 터미널 |
| `ooenv context size` | 파일별 토큰 크기 | 터미널 |
| `ooenv context check` | 컨텍스트 파일 검증 | 터미널 |
| `ooenv context save "msg"` | 메모리에 정보 저장 | tmp/context_memory.json |
| `ooenv context load` | 메모리에서 로드 | 터미널 |
| `ooenv context list` | 저장된 엔티티 목록 | 터미널 |
| `ooenv context clear` | 메모리 초기화 | 터미널 |
| `ooenv gpu` | GPU 환경 테스트 (NVIDIA 드라이버/CUDA/PyTorch GPU) | 터미널 |
| `ooenv kill <target>` | 좀비 프로세스 탐지 및 종료 (node/python/chrome/edge) | 터미널 |
| `ooenv kill <target> --dry-run` | 프로세스 목록만 표시 (종료 안 함) | 터미널 |
| `ooenv kill <target> --force` | 강제 종료 (/F) | 터미널 |
| `ooenv kill --list` | 지원 프로세스 별칭 목록 | 터미널 |
| `ooenv alias` | 등록된 스킬 약어 목록 표시 | 터미널 |
| `ooenv alias list` | 약어 목록 (약어 → 원본 스킬) | 터미널 |
| `ooenv alias add <약어> <스킬>` | 새 약어 등록 (SKILL.md 자동 생성) | `.claude/skills/<약어>/` |
| `ooenv alias remove <약어>` | 약어 삭제 (폴더 제거) | 터미널 |
| `ooenv alias check` | 약어 파일 정합성 검증 (원본 스킬 존재 확인) | 터미널 |
| `ooenv opti` | 컨텍스트 최적화 전체 스캔 + 리포트 (dry-run 기본) | 터미널 |
| `ooenv opti --fix` | 자동 수정 가능 항목 최적화 (.claudeignore 추가, oodoc clear) | 파일 수정 |
| `ooenv opti memory` | 메모리 파일(CLAUDE.md 계층) 토큰 크기 분석 | 터미널 |
| `ooenv opti skills` | 스킬 파일 크기 점검 (3KB 초과 탐지) | 터미널 |
| `ooenv opti docs` | Auto-load 문서 최적화 점검 (이력 행 수, 파일 크기) | 터미널 |
| `ooenv opti agents` | 에이전트 미사용 현황 분석 | 터미널 |
| `ooenv opti ignore` | .claudeignore 누락 항목 점검 | 터미널 |
| `ooenv opti mcp` | 미사용 MCP 서버 등록 점검 | 터미널 |

실행: `uv run python .claude/skills/ooenv/scripts/ooenv_run.py [args]`

> 서브명령어 상세: `.claude/skills/ooenv/references/commands-detail.md` 참조

## 3. 에이전트 활용

| 단계 | 작업 | 에이전트 | 모델 | 병렬 |
|------|------|----------|------|:----:|
| 1 | 환경 구조 탐색 | Explore (내장) | haiku | - |
| 2 | 정합성 분석 | ooqa | sonnet | - |
| 3-4 | 동기화/기록 | task-executor | sonnet | - |

## 4. 핵심 워크플로우

### ooenv run 흐름

```
ooenv run
  1. 플러그인 -> [ENV]
  2. UV 의존성 -> [DEP]
  3. 정합성 -> [VALIDATION]
  4. 환경 리포트 생성 -> 00_doc/sp00/d0009_env.md
  5. 리포팅/수정
```

### d0009_env.md 리포트 섹션

| 섹션 | 내용 |
|------|------|
| 1. 시스템 환경 | Python, UV, Node.js, npm, Git, gh (GitHub CLI + 인증), Pandoc 버전 |
| 2. MCP 서버 | 설치/미설치 상태, 설치 방법 |
| 3. Claude 플러그인 | 설치/미설치 상태 (O/X) |
| 4. 스킬 현황 | 4.1 Claude 공식 스킬 (O/X), 4.2 oo 프로젝트 스킬 목록 |
| 5. 에이전트 현황 | 사용/미사용 상태 (O/X) |
| 6. 커맨드 현황 | 활성/비활성 상태 (O/X), sc/ 전체 목록 |
| 7. Python 패키지 | 패키지 수, PyTorch 버전, CUDA 상태 |
| 8. 명령어 집계 | oo 스킬 전체 서브명령어 목록 (.claude/CLAUDE.md 카탈로그) |
| 9. 검증 결과 | 발견/수정/남은 이슈 |

## 5. 관련 문서

- `.claude/skills/oostart/SKILL.md` - 세션 시작
- `.claude/skills/oocheck/SKILL.md` - 코드 품질 체크
- `.claude/guides/common_guide.md` - 공통 가이드라인
- `00_doc/sp00/d0009_env.md` - 환경 리포트 (자동 생성)
- `.claude/skills/ooenv/references/commands-detail.md` - 서브명령어 상세

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

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
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->
