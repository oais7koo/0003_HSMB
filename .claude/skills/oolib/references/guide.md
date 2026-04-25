# oolib_guide - oo 모듈 수정/최적화 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oolib/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oo 모듈의 문제점 발견, 기록, 수정을 자동화하는 2단계 워크플로우 가이드입니다.

**목적**: oo 모듈의 코드 품질 개선 및 오류 제거
**대상**: oo/*.py, oo/**/*.py 및 해당 모듈을 import하는 코드
**출력**: 00_doc/d{SP}0004_todo.md (이슈 관리), 00_doc/sp00/d0005_lib.md (문서화)

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
- `pylint -E oo/`: 에러 레벨만 검출
- `uv run python -m py_compile oo/*.py`: 문법 검증

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
| Agent 3 | oo 기타 모듈 | 범용 이슈 |
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

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oolib/SKILL.md | 스킬 명세 |
| .claude/guides/debugging_guide.md | 디버깅 가이드 (False Positive 처리) |
| 00_doc/d{SP}0004_todo.md | 이슈 추적 |
| 00_doc/sp00/d0005_lib.md | 라이브러리 문서 |
| .claude/skills/oodb/SKILL.md | DB 관련 스킬 |

**에이전트**: Explore, python-code-reviewer, task-executor, task-checker, ooqa
**도구**: pylint, py_compile, pytest
