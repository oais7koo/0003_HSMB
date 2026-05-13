# d{SP}0003_test.md - {SP명} 테스트 케이스

## 문서이력관리
- v01 {날짜} — 초기 생성

---

## 개요

| 항목 | 내용 |
|------|------|
| 서브프로젝트 | SP{NN}: {SP명} |
| 코드 폴더 | `{SP_folder}/` |
| 테스트 폴더 | `tests/sp{NN}/` |
| 테스트 방법론 | `.claude/skills/ootest/references/guide.md` |
| 관련 PRD | `00_doc/sp{NN}/d{SP}0001_prd.md` |
| 관련 TODO | `00_doc/sp{NN}/d{SP}0004_todo.md` |

---

# Part A: 에러체크

> 정적 분석 기반 코드 품질 검증 | 실행: `ootest run --check` 또는 `uv run pylint {SP_folder}/`

## 테스트 항목

| ID | 검사 항목 | 도구 |
|----|----------|------|
| A1 | Python 문법 오류 | `uv run python -m py_compile` |
| A2 | 코드 품질 (PEP8) | `uv run pylint` / `flake8` |
| A3 | 타입 체크 | `uv run mypy` |
| A4 | 보안 취약점 | 코드 리뷰 |
| A5 | import 가능 여부 | import 검사 |

## 실행 결과

| 실행일 | 도구 | 대상 | 결과 | 비고 |
|--------|------|------|:----:|------|
| - | - | - | - | (검사 기록 없음) |

**실패 시**: `d{SP}0004_todo.md`에 [TEST] 분류로 등록

---

# Part B: 시나리오 테스트

> E2E/UI 검증 | 실행: `ootest run --e2e` 또는 Playwright MCP

## 테스트 항목

<!-- PRD d{SP}0001 기능 목록에서 도출 -->

| ID | 시나리오 | 우선순위 |
|----|----------|:--------:|
| B1-1 | {PRD 기능에서 도출} | P0 |

## 실행 결과

| 실행일 | ID | 결과 | 비고 |
|--------|-----|:----:|------|
| - | - | - | (테스트 기록 없음) |

**실패 시**: `d{SP}0004_todo.md`에 등록

---

# Part C: 단위 테스트

> TDD 기반 기능별 단위 테스트 | 위치: `tests/sp{NN}/TC*.py`
> TC 규칙·코드 작성 가이드: `.claude/skills/ootest/references/guide.md` 섹션 5, 12 참조

## 테스트 항목

| TC ID | 기능 | 테스트명 | 파일 | 유형 | 상태 |
|-------|------|---------|------|------|:----:|
| - | - | (등록된 테스트 없음) | - | - | - |

> 파일 경로 형식: `tests/sp{NN}/TC{Epic}-{Feature}.{Task}_{이름}.py`

## 실행 결과

| 실행일 | 전체 | 통과 | 실패 | 비고 |
|--------|:----:|:----:|:----:|------|
| - | - | - | - | (테스트 기록 없음) |

**실패 시**: `d{SP}0004_todo.md`에 등록

---

# Part D: oo 모듈 테스트

> oo/*.py 모듈 전체 기능 검증 | 실행: `ootest run --module`
> SP≠00인 경우 공통 d0003_test.md Part D 참조

## 테스트 항목

> **참조**: `00_doc/sp00/d0003_test.md` Part D 참조
> oo 모듈은 공통이므로 d0003에서 통합 관리합니다.

---

# Part E: 런타임 검증

> pages/*.py import 시 런타임 에러 사전 감지 | 실행: `ootest run --runtime`
> 해당 없으면 "해당 없음 — pages/ 폴더 없음" 기재

## 실행 결과

| 실행일 | 대상 | 전체 | 통과 | 실패 | 비고 |
|--------|------|:----:|:----:|:----:|------|
| - | - | - | - | - | (테스트 기록 없음) |

---

## 관련 문서

| 문서 | 경로 |
|------|------|
| 테스트 방법론 | `.claude/skills/ootest/references/guide.md` |
| PRD | `00_doc/sp{NN}/d{SP}0001_prd.md` |
| TODO | `00_doc/sp{NN}/d{SP}0004_todo.md` |
| 대시보드 | `00_doc/sp00/d0003_test.md` |
