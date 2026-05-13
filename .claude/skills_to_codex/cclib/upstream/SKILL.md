---
name: oolib
description: "oo 모듈 수정/최적화 스킬 'oolib', 'oo 모듈', '라이브러리 수정', '모듈 최적화' 등을 요청할 때 사용한다"
metadata:
  version: "v02"
  category: "doc-env"
---

# oolib - oo 모듈 수정/최적화

> 공통: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 문서 이력 관리
- v02 2026-04-19 — optimize → check --fix 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | oo 공통 모듈(oo/) 문제 발견→기록→수정 2단계 워크플로우 |
| **하는 것** | oo 모듈 분석, 이슈 d{SP}0004 등록, 수정 후 해결 이동 |
| **하지 않는 것** | 서브프로젝트 코드 수정(→oofix), DB 수정(→oodb), 성능 최적화(→ooopti) |
| **참조 범위** | 현재 프로젝트 내부 `oo/` 모듈만 / 외부 라이브러리 자동 포함 안 함 |
| **수정 대상** | `oo/*.py`, `d{SP}0004_todo.md`, `d{SP}0010_history.md` |
| **실행 레벨** | [자동] — Phase 1(분석) → Phase 2(수정) 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 환경 자동 사용 / 다른 에이전트: 분석·수정 단계를 수동 실행 |

## 1. 개요

oo 모듈 문제점 발견/수정 2단계 워크플로우.

- **컨텍스트**: `--sp N` 또는 `oocontext N`
- **에러/이슈**: d{SP}0004_todo.md | **신규 개발**: d{SP}0002_plan.md
- **워크플로우**: Phase 1(분석->d0004 기록) -> Phase 2(수정->해결 이동)
- **완료**: d0004에 oo 미해결 이슈 0개

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oolib help` | 서브명령어 목록 표시 |
| `oolib version` | 스킬 버전 정보 (v01) |
| `oolib status` | 서브명령어 리스트, 상태/미해결 이슈 |
| `oolib check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oolib show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oolib add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oolib run` | Phase 1+2 (분석->수정->문서) |
| **`oolib run this`** | **직전 작업 모듈 최적화** (→ common_guide.md §9) |
| `oolib check --fix` | run + 최적화 (구 `optimize`) |
| `oolib doc` | d0005_lib.md 문서화만 |
| `oolib cleanup [대상]` | 코드/import/파일 정리 (cleanup 흡수) |

옵션: `--module [name]`, `--dry-run`, `--interactive`, `--report`
cleanup 옵션: `--type code\|imports\|files\|all`, `--safe`, `--aggressive`

실행: `uv run python .claude/skills/oolib/scripts/oolib_run.py [args]`

## 3. 병렬 처리

### 3.1 아키텍처

```
메인 에이전트 (분석 + 조율 + 검증)
    +----+----+----+
Agent1  Agent2  Agent3  Agent4
core    bizreg  기타    pages
```

### 3.2 역할 분배

| 에이전트 | 담당 | 역할 |
|---------|------|------|
| Agent 1 | __init__.py, config_helper.py | export/중복 |
| Agent 2 | bizreg.py, seal.py, ocr.py | 변수/멤버 |
| Agent 3 | oo 나머지 | 기타 이슈 |
| Agent 4 | 02_1st_server/pages/* | import |

### 3.3 서브에이전트 매핑

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|------|
| 분석 | Explore, python-code-reviewer | haiku / sonnet | O |
| 수정 | task-executor | sonnet | O |
| 최적화 | python-code-reviewer | sonnet | O |
| 검증 | task-checker | sonnet | - |
| 품질 | ooqa | sonnet | O |

### 3.4 병렬화 전략

| 이슈 | 병렬화 | 비고 |
|------|--------|------|
| E0611 (export) | 낮음 | __init__.py 먼저 |
| E0606 (미할당) | 높음 | 파일별 독립 |
| E1101 (멤버) | 높음 | 파일별 독립 |

## 4. 워크플로우

### 4.1 run

**Phase 1**: pylint -E, py_compile 분석 -> d0004 기록 -> 병렬 계획
**Phase 2**: 병렬 수정 -> py_compile 검증 -> 결과 수집 -> d0004 이동 -> pytest

### 4.2 check --fix

run + Phase 3: 중복/미사용/성능 분석 -> [OPT] 등록 -> 병렬 최적화 -> d0005 반영

## 5. d0004 연동

### 이슈 범위

| 경로 | 포함 |
|------|------|
| oo/*.py, oo/**/*.py | O |
| 02_1st_server/* (oo import) | O |
| tests/test_oo*.py | O |

### ID 규칙

- 기존: A001, A002... | 신규: L prefix + [FIX]/[OPT]
- 예: `| L001 | 2026-01-02 | [FIX] oo/config.py - 중복 | 높음 | 대기 |`

## 6. 최적화 체크리스트

- **코드**: 중복제거, 미사용 import/함수 삭제, 타입힌트
- **성능**: 루프/메모리/I/O 최적화
- **구조**: 모듈분리, 순환의존성 제거

## 7. 완료 조건

### run

| 조건 | 검증 |
|------|------|
| 미해결 이슈 0개 | d{SP}0004 "현재 이슈" 확인 |
| 구문 오류 없음 | `uv run python -m py_compile oo/*.py` |
| 테스트 통과 | `uv run pytest tests/` |
| 문서 업데이트 | d0005, d{SP}0010 반영 |

### check --fix

run 조건 + [OPT] 0개 + pytest 전체 통과

## 컴팩트 생성 원칙 (--compact)

`oolib doc --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

> **관련 문서**: `.claude/guides/debugging_guide.md` | `00_doc/d{SP}0004_todo.md` | `00_doc/sp00/d0005_lib.md`

> **관련 명령어**: `.claude/commands/sc/index.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.claude/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |
| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |
| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |
| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |

**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.

<!-- KARPATHY-REF:END -->

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

