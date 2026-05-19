# oolib_guide - oo 모듈 수정/최적화 가이드

## 문서 이력 관리
- v02 2026-05-17 — oais 모듈 스킬 반영: §5 d0005 문서 구조 명세, §1.1 적용 범위(3_code 독립 프로젝트는 oais 미수정·common_*.py 사용) 추가, oo/→oais/ 정정
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oolib/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

프로젝트 루트 `oais/` 모듈의 정합화·정리를 자동화하고, 모듈 구조를 d0005에 문서화하는 가이드입니다.

**목적**: oais 모듈의 코드 품질 개선·오류 제거 + 모듈 구조 문서화
**대상**: oais/*.py, oais/**/*.py 및 해당 모듈을 import하는 코드
**출력**: 00_doc/d{SP}0004_todo.md (이슈 관리), 00_doc/sp00/d0005_lib.md (oais 모듈 문서)

### 1.1 적용 범위

oolib는 **OAIS 워크스페이스(1_oais)의 `oais/` 모듈**에만 적용한다.

| 환경 | oais 모듈 | 공통 코드 |
|------|----------|----------|
| OAIS 워크스페이스 (1_oais) | oolib로 관리·수정 | `oais/` 패키지 |
| `3_code/` 독립 프로젝트 | **수정·업데이트 금지** (oosync로 배포만 받음) | `src/common_*.py` 또는 각 서브프로젝트 폴더 내 `common_*.py` |

> 독립 프로젝트에서 공통 코드가 필요하면 `oais`를 건드리지 말고, `src/` 또는 서브프로젝트 폴더에 `common_*.py` 형태의 프로젝트-로컬 공통 모듈을 생성·관리한다. `oais`는 OAIS 공통 패키지이지 독립 프로젝트의 SSOT가 아니다.

## 2. 워크플로우

### 2.1 Phase 1: 분석 및 기록

```
pylint -E 실행
    ↓
py_compile 문법 검증
    ↓
발견된 이슈 분류 (E0611, E0606, E1101 등)
    ↓
d{SP}0004_todo.md 등록 (L prefix + [FIX] 태그)
    ↓
병렬 처리 계획 수립
```

**분석 도구**:
- `pylint -E oais/`: 에러 레벨만 검출
- `uv run python -m py_compile oais/*.py`: 문법 검증

**주요 에러 유형**:
| 코드 | 설명 | 우선순위 |
|------|------|----------|
| E0611 | export 누락 (모듈에서 import 실패) | 높음 |
| E0606 | 변수 미할당 | 중간 |
| E1101 | 멤버 없음 (속성/메서드 참조 오류) | 중간 |
| E0401 | import 오류 | 높음 |

### 2.2 Phase 2: 수정 및 검증

```
병렬 에이전트 할당 (파일별/이슈별)
    ↓
수정 실행 (Agent1~4)
    ↓
py_compile 재검증
    ↓
pytest 실행 (tests/test_oo*.py)
    ↓
d{SP}0004_todo.md 이동 (대기→해결)
    ↓
d0005_lib.md 문서 업데이트
```

**병렬 처리 전략**:
| Agent | 담당 파일 | 주요 이슈 |
|-------|----------|----------|
| Agent 1 | __init__.py, config_helper.py | E0611 (export) |
| Agent 2 | bizreg.py, seal.py, ocr.py | E0606, E1101 |
| Agent 3 | oais 기타 모듈 | 범용 이슈 |
| Agent 4 | 02_1st_server/pages/* | import 오류 |

## 3. 상세 사용법

### 3.1 기본 실행

```bash
# Phase 1+2 전체 실행
uv run python .claude/skills/oolib/scripts/oolib_run.py run

# 특정 모듈만
uv run python .claude/skills/oolib/scripts/oolib_run.py run --module config_helper

# 드라이런 (수정 없이 계획만)
uv run python .claude/skills/oolib/scripts/oolib_run.py run --dry-run
```

### 3.2 최적화 실행

```bash
# run + 최적화 (중복/미사용 제거, 성능 개선)
uv run python .claude/skills/oolib/scripts/oolib_run.py optimize

# 보고서만
uv run python .claude/skills/oolib/scripts/oolib_run.py optimize --report
```

**최적화 항목**:
- 코드: 중복 제거, 미사용 import/함수 삭제, 타입 힌트 추가
- 성능: 루프 최적화, 메모리 누수 제거, I/O 효율화
- 구조: 모듈 분리, 순환 의존성 제거

### 3.3 문서화만 실행

```bash
# d0005_lib.md 업데이트만
uv run python .claude/skills/oolib/scripts/oolib_run.py doc
```

## 4. 사용 예시

### 예시 1: 전체 점검 및 수정

```bash
# 상태 확인
uv run python .claude/skills/oolib/scripts/oolib_run.py status

# 전체 실행
uv run python .claude/skills/oolib/scripts/oolib_run.py run

# 결과:
# - d0004_todo.md: L001~L015 등록 → 해결 이동
# - pytest: tests/test_oo*.py 전체 통과
# - d0005_lib.md: 모듈 목록 업데이트
```

### 예시 2: 특정 에러만 수정

```bash
# E0611 (export) 에러만 수정
uv run python .claude/skills/oolib/scripts/oolib_run.py run --error-code E0611

# config_helper.py 모듈만
uv run python .claude/skills/oolib/scripts/oolib_run.py run --module config_helper
```

### 예시 3: False Positive 처리

```
pylint E1101 발견: "Module 'pd' has no 'DataFrame' member"
    ↓
.claude/guides/debugging_guide.md 섹션 4 참조
    ↓
# pylint: disable=no-member 주석 추가
```

## 5. d0005 문서 구조 (oais 모듈 문서)

`oolib doc`(= `oolib_update.py update`)가 생성하는 `00_doc/sp00/d0005_lib.md`의 표준 구조:

| 섹션 | 내용 |
|------|------|
| 제목·안내 | `oais 모듈 문서`임을 명시 + 의존성은 d0009 참조 |
| 문서이력관리 | 최근 5개 (oolib doc 실행 시 vN.N 자동 증가) |
| §1 oais 모듈 구조 | 모듈별 함수 수·주요 기능 요약 표 |
| §2 함수 상세 | 모듈별 서브섹션(`### 2.N 모듈명`) + 함수 표 (함수·시그니처·설명·출처) |

### 5.1 함수 출처 추적 (하이브리드)

함수는 SP02(`02_pycode/`)에서 개발·검증 후 `oais/`로 함수화된다. d0005 §2의 `출처` 컬럼은 그 SP02 원본 파일을 기록한다.

| 우선순위 | 방식 | 설명 |
|:--------:|------|------|
| 1 | docstring `출처:` 태그 | oais 함수 docstring에 `출처: 02_pycode/dXXXX_*.py` 한 줄 → oolib가 AST로 자동 추출 |
| 2 | d0005 수동 기재 | 태그가 없으면 d0005 §2 표의 출처 칸을 직접 기입 → 재생성 시 보존 |
| 3 | `미기재` | 둘 다 없는 함수 (점진 기재 대상) |

**docstring 태그 예시**:

```python
def my_func(x):
    """함수 설명 첫 줄.

    출처: 02_pycode/d20030_image_filter.py
    """
```

### 5.2 범위 원칙

- 포함: `oais/` 패키지의 모듈·함수 구조 + 함수 출처
- 제외: **Python 의존성(pyproject.toml)** — `d0009_env.md`(ooenv) 관할. d0005에 의존성 목록을 두지 않는다(d0009와 중복 방지).
- 기존 문서의 모듈 설명(§1)·수동 출처(§2)는 재생성 시 보존(큐레이션 유지).

## 6. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oolib/SKILL.md | 스킬 명세 |
| .claude/guides/debugging_guide.md | 디버깅 가이드 (False Positive 처리) |
| 00_doc/d{SP}0004_todo.md | 이슈 추적 |
| 00_doc/sp00/d0005_lib.md | oais 모듈 문서 |
| .claude/skills/oodb/SKILL.md | DB 관련 스킬 |

**에이전트**: Explore, python-code-reviewer, task-executor, task-checker, ooqa
**도구**: pylint, py_compile, pytest
