---
name: ccskill
description: "공통: `.claude/guides/common_guide.md` | 에이전트 참조: `agents.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

# ccskill - 스킬 최적화 검증

> 공통: `.claude/guides/common_guide.md` | 에이전트 참조: `agents.md`

## 문서 이력 관리
- v04 2026-04-19 — validate/validate-checklist → check/check --checklist 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | oo 스킬 파일들의 서브에이전트·명령어 활용 최적화 검증 및 개선 |
| **하는 것** | SKILL.md 검증, 서브에이전트 위임 최적화, 스킬 문서 이력 자동 추가 |
| **하지 않는 것** | 코드 구현(→oodev), 환경 점검(→ooenv), 스킬 직접 실행 |
| **참조 범위** | `.claude/skills/oo*/SKILL.md` 파일들 / 외부 스킬 저장소 자동 포함 안 함 |
| **수정 대상** | `.claude/skills/oo*/SKILL.md` |
| **실행 레벨** | [반자동] — 검증 결과 확인 후 수정 적용 |
| **에이전트 호환** | Claude Code 권장 — Agent 도구로 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

## 개요

> ⚠️ **필수**: run/check 명령 시 반드시 Agent 도구로
> explore(haiku) 스킬 파일 스캔 → executor(sonnet) 검증 및 수정 순서로 위임할 것.
> 53개 스킬 파일 직접 스캔 금지 — 메인 컨텍스트 보호.

`.claude/skills/oo*/SKILL.md` 스킬 파일들이 서브에이전트 위임 및 명령어 활용을 최적화하고 있는지 검증/개선하는 스킬.

> **바이브셋**: oosync로 동기화 관리하는 바이브 코딩 환경 파일 일체. `.claude/skills/`(스킬)은 바이브셋의 핵심 구성 요소이며, ooskill은 바이브셋 중 스킬 파트의 품질을 관리한다.

**검증 항목**:
1. `.claude/agents/` 서브에이전트 적절한 활용 여부
2. `.claude/commands/sc/` 명령어 적절한 활용 여부

## 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ccskill help` | 서브명령어 목록 표시 | 터미널 |
| `ccskill version` | 스킬 버전 정보 (v04) | 터미널 |
| `ccskill status` | 서브명령어 목록, 스킬 현황, 최적화 요약 | - |
| `ccskill check` | 현재 상황 검토 후 최적안 제안 (구 `validate`) | 개선 권장사항 |
| `ccskill check --checklist` | 모든 oo* 스킬 checklist.md 표준 포맷 검증 (구 `validate-checklist`) | 터미널 |
| `ccskill show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ccskill add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ccskill run` | 스킬 파일 배치 실행 (SKILL.md 자동 수정) | 수정된 스킬 파일 |
| `ccskill run --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| `ccskill run [스킬명]` | 특정 스킬만 배치 실행 | 수정된 스킬 파일 |
| `ccskill update` | 등록된 모든 현행화 타겟 일괄 실행 (catalog + run-update-ref + gemma) | 수정된 파일 |
| `ccskill update <타겟>` | 특정 타겟만 현행화 (예: `ccskill update catalog`) | 수정된 파일 |
| `ccskill update <타겟> --dry-run` | 변경 예정 내용만 출력 | 터미널 |
| `ccskill backup` | ~~제거~~ → `oosync backup` 사용 | - |

### run과 update 역할 분리 원칙

| 명령어 | 역할 | 성격 |
|--------|------|------|
| `run` | **배치 실행** — 그 스킬의 핵심 동작 또는 구체적 서브커맨드 실행 | 일회성·실행 |
| `update` | **현행화** — 최상의 상태로 유지되어야 하는 모든 상태·설정 갱신 | 멱등·유지보수 |

> 예시: `ccskill run`은 스킬 파일 자동 수정(배치), `ccskill update`는 CLAUDE.md 카탈로그 + Gemma 참조 등 현행화 전용.
> 이 원칙은 **모든 oo* 스킬**에 동일하게 적용되어야 한다.

### update 타겟 레지스트리

| 타겟 | 설명 | 구현 |
|------|------|------|
| `catalog` | CLAUDE.md 스킬 카탈로그 현행화 (alias 섹션 포함, 스킬 추가/삭제 반영) | `cmd_update()` 함수 |
| `run-update-ref` | 모든 oo* 스킬에 run/update 분리 원칙 참조 블록(`<!-- RUN-UPDATE-REF:START/END -->`) 삽입/갱신 | `scripts/ooskill_run_update_ref.py` |
| `gemma` | 모든 oo* 스킬에 Gemma 위임 참조 블록(`<!-- GEMMA-REF:START/END -->`) 삽입/갱신 | `scripts/ooskill_gemma_ref.py` |

> 새 타겟 추가 시 `ooskill_run.py`의 `UPDATE_TARGETS` 딕셔너리에 `{kind, call|script, desc}` 추가

## help 서브명령어 표준

> **모든 oo* 스킬의 필수 표준**: `oo* help`는 **파이썬 스크립트를 실행**하여 서브명령어 목록을 출력한다.

### 실행 방법

```
uv run python .claude/skills/{스킬명}/scripts/{스킬명}_run.py help
```

> Claude가 `oo* help` 요청을 받으면 위 명령을 **직접 실행**하고 그 출력을 보여준다. SKILL.md를 직접 읽어 출력하는 것은 C14 위반.

> 코드 예시: references/guide.md 참조

> **핵심**: `scripts/*_run.py`가 SKILL.md 서브명령어 섹션 테이블을 파싱하여 출력 (단일 진실 공급원)

### 규칙

| 항목 | 기준 |
|------|------|
| 헤더 | `` `[스킬명] help` 서브명령어 목록: `` |
| 테이블 | SKILL.md 서브명령어 섹션 테이블 그대로 (스크립트가 파싱) |
| 스크립트 필수 | `scripts/*_run.py`에 `_print_skill_help()` 호출 분기 있어야 함 |
| AI 실행 필수 | Claude가 `oo* help` 받으면 반드시 스크립트 실행 (`uv run python ... help`) |
| 검증 | `ccskill run`이 미구현 시 자동 추가 |

---

## check --checklist 서브명령어

> 모든 oo* 스킬의 `references/checklist.md`가 표준 포맷을 준수하는지 검증한다.
> 템플릿: `.claude/templates/oo_checklist_template.md`

### 검증 항목

| 항목 | 검증 내용 | 결과 |
|------|----------|------|
| 파일 존재 | `references/checklist.md` 존재 여부 | FAIL: 미존재 |
| C01 존재 | 공통 항목 C01(필수 파일 존재) 포함 | FAIL: 미포함 |
| C02 존재 | 공통 항목 C02(버전 일치) 포함 | FAIL: 미포함 |
| 테이블 포맷 | `| ID | 항목 | 검증 내용 | 심각도 |` 테이블 구조 | WARN: 구형 포맷 |
| 심각도 값 | CRITICAL/ERROR/WARNING/INFO 중 하나 | WARN: 비표준 값 |
| 항목 수 | 5~10개 범위 | INFO: 범위 밖 |

### 출력 형식

> 코드 예시: references/guide.md 참조

### 워크플로우

> 코드 예시: references/guide.md 참조

---

## version 서브명령어 표준

> **모든 oo* 스킬의 필수 표준**: `oo* version`은 스킬 버전 정보를 출력해야 한다.

### 형식 규칙

| 항목 | 기준 | 예시 |
|------|------|------|
| 백틱 | 명령어 전체를 백틱으로 감쌀 것 | `` `ccskill version` `` |
| 버전 번호 | `(vXX)` 형식으로 포함 | `(v01)`, `(v12)` |
| 위치 | 서브명령어 테이블에서 `help` 행 바로 다음 | 두 번째 행 |
| 출력 | 스킬 이름 + 버전 번호 표시 | `ccskill v01` |

### 출력 형식

> 코드 예시: references/guide.md 참조

### 규칙

| 항목 | 기준 |
|------|------|
| 위치 | 서브명령어 테이블 두 번째 행 (help 다음) |
| 버전 번호 | metadata version 필드와 일치 |
| 스크립트 불필요 | AI가 SKILL.md metadata를 읽어 직접 출력 |
| 검증 | `ccskill run`이 미준수 시 자동 수정 |

---

## 검증 기준

### skill-creator 구조 검증 (통합)

> 기준: `skill-creator` SKILL.md (Claude 공식 스킬 표준)

| 항목 | 기준 | 심각도 |
|------|------|--------|
| YAML frontmatter | `name` + `description` 필수 존재 | CRITICAL |
| description 품질 | 트리거 조건 + 사용 시점 포함 여부 | WARNING |
| SKILL.md 크기 | 500줄 이내 (초과 시 references/ 분리 권장) | WARNING |
| scripts/ 실체 | SKILL.md가 스크립트 실행 언급 시 scripts/*.py 존재 확인 | CRITICAL |
| references/ 분리 | 상세 내용이 SKILL.md에 inline → references/ 분리 권장 | INFO |
| 불필요 문서 금지 | README.md, CHANGELOG.md 등 보조 문서 없어야 함 | WARNING |
| 버전 일치 | metadata `version:` 과 서브명령어 테이블 `(vXX)` 일치 | ERROR |
| 이력 테이블 순수성 | 이력 테이블에 명령어 행 혼입 금지 | ERROR |
| category 정확성 | metadata category가 실제 역할과 일치 | WARNING |

### 서브에이전트 위임 검증

**원칙**: 단일 에이전트 작업보다 멀티 에이전트 병렬 처리 우선

| 체크 | 기준 | 권장 |
|------|------|------|
| 병렬 처리 | 독립 작업이 2개 이상인가? | `Task(run_in_background=true)` 활용 |
| 적절한 위임 | 작업 유형에 맞는 에이전트 사용? | 매핑 테이블 참조 |
| 과도한 위임 | 단순 작업에 불필요한 위임? | 직접 처리 권장 |

**작업-에이전트 매핑**:

| 작업 유형 | 권장 에이전트 |
|----------|-------------|
| 코드 구현/수정 | `task-executor` |
| Python 리뷰 | `python-code-reviewer` |
| 구현 검증 | `task-checker` |
| 품질/중복 분석 | `ooqa` |
| 에러 분석 | `code-error-checker` |
| E2E 웹 테스트 | `oo-web-test-orchestrator` |
| 데이터 분석 | `data-analyst` |
| 학술 연구 | `academic-researcher` |

### 명령어 활용 검증

**원칙**: `.claude/commands/sc/` 명령어로 표준화된 워크플로우 활용

| 명령어 | 용도 | 연관 스킬 |
|--------|------|----------|
| `analyze` | 코드 분석 | oocheck, oolib |
| `build` | 프로젝트 빌드 | oodev |
| `implement` | 구현 | oodev |
| `improve` | 개선 | oofix |
| `test` | 테스트 | oocheck |
| `troubleshoot` | 트러블슈팅 | oocheck, oofix |

### oo 스킬 룰셋 검증 (R01-R10)

> `ccskill check` 실행 시 자동 포함.

| 코드 | 항목 | 심각도 | 패턴 |
|------|------|--------|------|
| R01 | 문서 이력 섹션 | ERROR | `## 문서 이력 관리` 존재 |
| R02 | 버전 형식 | ERROR | `\| vXX \|` 형식 |
| R03 | 날짜 형식 | WARNING | `YYYY-MM-DD` 형식 |
| R04 | status 명령어 | ERROR | `` `oo* status` `` 존재 |
| R05 | version 명령어 | WARNING | `` `oo* version` `` 존재 |
| R06 | 참조 인용 블록 | INFO | `> 참조\|공통\|ref` |
| R07 | 서브에이전트 테이블 | INFO | `\| 단계 \| 에이전트 \|` 존재 |
| R08 | 관련 문서 섹션 | WARNING | `## 관련 문서\|경로\|명령어` |
| R09 | 실행 스크립트 | INFO | `uv run python .claude/skills/oo` |
| R10 | 명령어 테이블 | ERROR | `\| 명령어 \| 설명 \|` 존재 |

## 워크플로우

### check 워크플로우

> 코드 예시: references/guide.md 참조

### run 워크플로우

> 코드 예시: references/guide.md 참조

## 서브에이전트 활용

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 스킬 분석 | `Explore` | haiku | 파일 탐색, 패턴 추출 | O |
| 최적화 검토 | `ooqa` | sonnet | 중복/누락 분석 | O |
| 파일 수정 | `task-executor` | sonnet | 스킬 파일 수정 | O |
| 검증 | `task-checker` | sonnet | 수정 결과 검증 | - |

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

## 관련 문서

| 문서 | 용도 |
|------|------|
| `agents.md` | 에이전트 검색 경로, 역할, 위임 규칙 |
| `.claude/agents/*.md` | 서브에이전트 정의 |
| `.claude/commands/sc/*.md` | 명령어 정의 |
| `.claude/guides/common_guide.md` | 에이전트 활용 원칙 |
| `skill-creator` (Claude 공식) | skill-creator 스킬 구조 표준 참조 |
