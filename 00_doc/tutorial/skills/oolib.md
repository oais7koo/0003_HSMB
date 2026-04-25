# oolib Tutorial

> oais 모듈 최적화 및 병렬 분석 | 버전: v03 | 카테고리: doc-env

## 1. 이 스킬은 왜 필요한가?


**이런 상황에서 사용합니다:**
- **컨텍스트**: `--sp N` 또는 `oocontext N`
- **에러/이슈**: d{SP}0004_todo.md | **신규 개발**: d{SP}0002_plan.md
- **워크플로우**: Phase 1(분석->d0004 기록) -> Phase 2(수정->해결 이동)
- **완료**: d0004에 oo 미해결 이슈 0개

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oolib run

# 상태 확인
oolib status

# 도움말
oolib help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oolib help` | 서브명령어 목록 표시 |
| `oolib version` | 스킬 버전 정보 (v01) |
| `oolib status` | 서브명령어 리스트, 상태/미해결 이슈 |
| `oolib check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oolib show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oolib add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oolib run` | Phase 1+2 (분석->수정->문서) |
| `oolib update` | 현행화 — 모듈 현황 재스캔 → 라이브러리 문서 갱신 | d0005_lib.md |
| `oolib update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| **`oolib run this`** | **직전 작업 모듈 최적화** (→ common_guide.md §9) |
| `oolib optimize` | run + 최적화 |
| `oolib doc` | d0005_lib.md 문서화만 |
| `oolib cleanup [대상]` | 코드/import/파일 정리 (cleanup 흡수) |

옵션: `--module [name]`, `--dry-run`, `--interactive`, `--report`
cleanup 옵션: `--type code\|imports\|files\|all`, `--safe`, `--aggressive`

실행: `uv run python .claude/skills/oolib/scripts/oolib_run.py [args]`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | oo 공통 모듈(oo/) 문제 발견→기록→수정 2단계 워크플로우 |
| **하는 것** | oo 모듈 분석, 이슈 d{SP}0004 등록, 수정 후 해결 이동 |
| **하지 않는 것** | 서브프로젝트 코드 수정(→oofix), DB 수정(→oodb), 성능 최적화(→ooopti) |
| **참조 범위** | 현재 프로젝트 내부 `oo/` 모듈만 / 외부 라이브러리 자동 포함 안 함 |
| **수정 대상** | `oo/*.py`, `d{SP}0004_todo.md`, `d{SP}0010_history.md` |
| **실행 레벨** | [자동] — Phase 1(분석) → Phase 2(수정) 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 환경 자동 사용 / 다른 에이전트: 분석·수정 단계를 수동 실행 |

### 병렬 처리

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

### d0004 연동

### 이슈 범위

| 경로 | 포함 |
|------|------|
| oo/*.py, oo/**/*.py | O |
| 02_1st_server/* (oo import) | O |
| tests/test_oo*.py | O |

### ID 규칙

- 기존: A001, A002... | 신규: L prefix + [FIX]/[OPT]
- 예: `| L001 | 2026-01-02 | [FIX] oo/config.py - 중복 | 높음 | 대기 |`

### 최적화 체크리스트

- **코드**: 중복제거, 미사용 import/함수 삭제, 타입힌트
- **성능**: 루프/메모리/I/O 최적화
- **구조**: 모듈분리, 순환의존성 제거

### 완료 조건

### run

| 조건 | 검증 |
|------|------|
| 미해결 이슈 0개 | d{SP}0004 "현재 이슈" 확인 |
| 구문 오류 없음 | `uv run python -m py_compile oo/*.py` |
| 테스트 통과 | `uv run pytest tests/` |
| 문서 업데이트 | d0005, d{SP}0010 반영 |

### optimize

run 조건 + [OPT] 0개 + pytest 전체 통과

### 컴팩트 생성 원칙 (--compact)

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

## 5. 워크플로우

### 4.1 run

**Phase 1**: pylint -E, py_compile 분석 -> d0004 기록 -> 병렬 계획
**Phase 2**: 병렬 수정 -> py_compile 검증 -> 결과 수집 -> d0004 이동 -> pytest

### 4.2 optimize

run + Phase 3: 중복/미사용/성능 분석 -> [OPT] 등록 -> 병렬 최적화 -> d0005 반영

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oolib run
```

### 서브명령어 활용
```bash
oolib run  # Phase 1+2 (분석->수정->문서)
oolib update  # 현행화 — 모듈 현황 재스캔 → 라이브러리 문서 갱신
oolib run this
oolib optimize  # run + 최적화
oolib doc  # d0005_lib.md 문서화만
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/oolib/scripts/oolib_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

(서브에이전트 정보 없음)

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 | ootutorial v03
