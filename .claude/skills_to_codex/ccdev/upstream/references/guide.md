# oodev_guide - TDD 기반 개발 가이드

## 문서 이력 관리
- v07 2026-04-02 — --framework 옵션, GSD 연계 추가
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oodev/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oodev는 TDD(Test-Driven Development) 기반으로 ooplan의 Task를 구현하는 스킬입니다. Red-Green-Refactor-Verify 사이클을 통해 품질 높은 코드를 생산하며, 첫 실행 시 테스트 문서를 자동 생성합니다.

### 1.1 핵심 역할

- **TDD 사이클 실행**: RED(실패 테스트) → GREEN(최소 구현) → REFACTOR(품질 개선) → VERIFY(런타임 검증)
- **테스트 문서 생성**: 첫 실행 시 `d{SP}0003_test.md` 자동 생성
- **Task 기반 개발**: ooplan의 Task를 단위로 개발
- **품질 보증**: 정적 분석 + 런타임 검증 의무화

### 1.2 출력 문서

| 문서 | 역할 | 생성 시점 |
|------|------|----------|
| `d{SP}0003_test.md` | 테스트 케이스 관리 | 첫 실행 시 자동 생성 |
| `tests/TC*.py` | 단위 테스트 파일 | RED 단계 |
| `src/`, `pages/` | 구현 코드 | GREEN 단계 |

### 1.3 TDD 사이클

```
INIT → RED → GREEN → REFACTOR → VERIFY → COMPLETE
```

| 단계 | 작업 | 산출물 |
|------|------|--------|
| INIT | 테스트 문서 생성 | d{SP}0003_test.md (첫 실행 시만) |
| RED | 실패 테스트 작성 | tests/TC*.py, d{SP}0003 Part C 등록 |
| GREEN | 최소 구현 | 테스트 통과 코드 |
| REFACTOR | 품질 개선 | lint/type check 통과 |
| VERIFY | 런타임 검증 | import 테스트 통과 |
| COMPLETE | 문서 갱신 | d{SP}0003 상태 [x] |

## 2. 워크플로우

### 2.1 전체 흐름도

```
┌─────────────────────────────────────────────┐
│ 0. 사전 조건                                 │
│    - d{SP}0002_plan.md 존재 (ooplan 완료) │
│    - Task 세분화 완료 (F002-1.1 등)          │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼──────────────────────────────┐
│ 1. oodev 실행                             │
│    - run / run [ID] / queue 선택            │
└─────────────┬──────────────────────────────┘
              │
              ├── INIT (첫 실행 시만) ────────┐
              │                               │
              │   d{SP}0003_test.md 존재?     │
              │   └─ 없음 → 자동 생성         │
              │       ├─ Part A: 에러체크     │
              │       ├─ Part B: 시나리오     │
              │       ├─ Part C: 단위 테스트  │
              │       ├─ Part D: oo 모듈    │
              │       └─ Part E: 런타임 검증  │
              │                               │
              ├── RED ──────────────────────┐│
              │   (실패 테스트 작성)         ││
              │   ├─ Task 분석               ││
              │   ├─ TC 파일 생성            ││
              │   ├─ Arrange-Act-Assert      ││
              │   ├─ pytest 실행 (FAIL)      ││
              │   └─ d{SP}0003 Part C 등록   ││
              │                              ││
              ├── GREEN ────────────────────┤│
              │   (최소 구현)                ││
              │   ├─ 테스트 통과 코드 작성   ││
              │   ├─ pytest 실행 (PASS)      ││
              │   └─ 과도한 구현 지양        ││
              │                              ││
              ├── REFACTOR ─────────────────┤│
              │   (품질 개선)                ││
              │   ├─ 중복 제거               ││
              │   ├─ 명확한 네이밍           ││
              │   ├─ 함수 분리               ││
              │   ├─ pylint 검증             ││
              │   └─ mypy 타입 체크          ││
              │                              ││
              ├── VERIFY ───────────────────┤│
              │   (런타임 검증, 필수)        ││
              │   ├─ test_page_import.py     ││
              │   ├─ import 테스트           ││
              │   ├─ DuplicateKey 감지       ││
              │   └─ 실패 시 GREEN 재수정    ││
              │                              ││
              └── COMPLETE ─────────────────┘│
                  (문서 갱신)                 │
                  ├─ d{SP}0003 상태 [x]       │
                  └─ d{SP}0002 상태 "완료"    │
                                              │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ 2. 반복 및 에스컬레이션                     │
│    - 최대 반복: 10회 (--max-iterations)     │
│    - 에스컬레이션: 복잡한 이슈 → 사용자 개입│
└─────────────────────────────────────────────┘
```

### 2.2 INIT 단계 (테스트 문서 생성)

```
oodev run (첫 실행)
    │
    ├─► 1. d{SP}0003_test.md 존재 확인
    │      └─ 없음 → 자동 생성 시작
    │
    ├─► 2. PRD 로드
    │      └─ 00_doc/d{SP}0001_prd.md
    │
    ├─► 3. Part A 생성 (에러체크)
    │      ├─ 고정 항목
    │      │  ├─ py_compile
    │      │  ├─ pylint
    │      │  ├─ mypy
    │      │  └─ 용어체크
    │      └─ 결과 테이블 (빈 상태)
    │
    ├─► 4. Part B 생성 (시나리오 테스트)
    │      ├─ PRD 4. 기능 요구사항 분석
    │      ├─ 시나리오 도출
    │      │  ├─ Must → P0
    │      │  ├─ Should → P1
    │      │  ├─ Could → P2
    │      │  └─ Won't → 제외
    │      ├─ 시나리오 테이블 생성
    │      └─ 결과 테이블 (빈 상태)
    │
    ├─► 5. Part C 생성 (단위 테스트)
    │      └─ 빈 테이블 (TDD RED에서 등록)
    │
    ├─► 6. Part D 생성 (oo 모듈)
    │      ├─ SP=00: oo/*.py 스캔
    │      │  ├─ Grep: "^def [a-z]"
    │      │  ├─ 11개 카테고리 분류
    │      │  └─ 모듈 테이블 생성
    │      │
    │      └─ SP≠00: 참조 링크만
    │         └─ "d0003_test.md Part D 참조"
    │
    ├─► 7. Part E 생성 (런타임 검증)
    │      └─ 빈 테이블 (VERIFY에서 업데이트)
    │
    └─► 8. 템플릿 적용 및 저장
           ├─ .claude/skills/ootest/templates/test/common_test_template.md
           └─ 00_doc/d{SP}0003_test.md 생성
```

**oo 모듈 카테고리 (Part D)**:

| 카테고리 | 모듈 예시 |
|----------|----------|
| Core | db.py, auth.py, session.py, admin.py |
| Config | config.py, config_helper.py |
| Entity | user.py, company.py, agent.py |
| Task | task_core.py, task_query.py |
| Data | column.py, system_code.py |
| Application | application.py, business_registration.py |
| File | file_operations.py, file_upload.py, ocr.py |
| External | hyphen_api.py, news_api.py |
| Document | pdf_handler.py, receipt.py |
| Utility | utils.py, date_utils.py, excel.py |
| UI | ui.py, mobile_css.py |

### 2.3 RED 단계 (실패 테스트 작성)

```
RED 단계 시작 (Task: F002-1.1)
    │
    ├─► 1. Task 분석
    │      ├─ d{SP}0002_plan.md에서 Task 로드
    │      │  └─ F002-1.1: 보건복지부 탭
    │      ├─ 개발기획 로드 (있는 경우)
    │      │  └─ d21720_앱_시니어복지_단위개발.md
    │      └─ 요구사항 파악
    │
    ├─► 2. TC 파일 생성
    │      ├─ 네이밍: TC002-1.1_보건복지부탭.py
    │      ├─ 위치: tests/
    │      └─ Task ↔ TC 1:1 매핑
    │
    ├─► 3. 테스트 코드 작성 (Arrange-Act-Assert)
    │      ```python
    │      """
    │      TC002-1.1_보건복지부탭.py - 보건복지부 탭 테스트
    │
    │      TC ID: TC002-1.1
    │      Task ID: F002-1.1
    │      Feature: F002-1 중앙정부 정책
    │      """
    │      import pytest
    │
    │      class TestTC002_1_1_보건복지부탭:
    │          """TC002-1.1: 보건복지부 탭 테스트"""
    │
    │          def test_tab_renders_correctly(self):
    │              """보건복지부 탭 정상 렌더링"""
    │              # Arrange
    │              # (테스트 데이터 준비)
    │
    │              # Act
    │              # (기능 실행 - 아직 구현 안 됨)
    │
    │              # Assert
    │              assert False, "구현 필요"
    │      ```
    │
    ├─► 4. pytest 실행 (FAIL 확인)
    │      ```bash
    │      uv run pytest tests/TC002-1.1_보건복지부탭.py -v
    │      ```
    │      └─ FAILED (예상된 실패)
    │
    └─► 5. d{SP}0003 Part C 등록
           ```markdown
           ### E002: 정책정보

           | TC ID | Task ID | 테스트명 | 파일 | 상태 |
           |-------|---------|----------|------|------|
           | TC002-1.1 | F002-1.1 | 보건복지부 탭 | tests/TC002-1.1_보건복지부탭.py | [ ] |
           ```
```

**TC 네이밍 규칙**:

| 레벨 | 형식 | 예시 |
|------|------|------|
| Epic | `E{순번}` | E002 |
| Feature | `F{Epic}-{순번}` | F002-1 |
| Task | `F{Epic}-{Feature}.{순번}` | F002-1.1 |
| TC | `TC{Epic}-{Feature}.{Task}` | TC002-1.1 |

**Task ↔ TC 1:1 매핑**:
- Task: `F002-1.1` (보건복지부 탭)
- TC 파일: `TC002-1.1_보건복지부탭.py`
- TC 클래스: `TestTC002_1_1_보건복지부탭`

### 2.4 GREEN 단계 (최소 구현)

```
GREEN 단계 시작
    │
    ├─► 1. 테스트 통과를 위한 최소 코드 작성
    │      ├─ 과도한 구현 지양
    │      ├─ YAGNI (You Aren't Gonna Need It)
    │      └─ 예시:
    │         ```python
    │         def render_welfare_tab():
    │             """보건복지부 탭 렌더링 (최소 구현)"""
    │             return True  # 일단 통과만
    │         ```
    │
    ├─► 2. pytest 실행 (PASS 확인)
    │      ```bash
    │      uv run pytest tests/TC002-1.1_보건복지부탭.py -v
    │      ```
    │      └─ PASSED ✓
    │
    └─► 3. 점진적 기능 추가
           ├─ 테스트 추가 → 구현 추가 반복
           └─ 모든 테스트 PASS 확인
```

**최소 구현 예시 (Streamlit 페이지)**:

```python
# pages/7_72_앱_시니어복지.py

import streamlit as st

def main():
    """보건복지부 탭 메인"""
    st.title("시니어 복지")

    # 최소 구현: 탭 렌더링만
    tab1, tab2, tab3 = st.tabs(["보건복지부", "고용노동부", "여성가족부"])

    with tab1:
        st.write("보건복지부 정책 표시")  # 일단 통과

    with tab2:
        st.write("고용노동부 정책 표시")

    with tab3:
        st.write("여성가족부 정책 표시")

if __name__ == "__main__":
    main()
```

### 2.5 REFACTOR 단계 (품질 개선)

```
REFACTOR 단계 시작
    │
    ├─► 1. 코드 정리
    │      ├─ 중복 제거 (DRY)
    │      ├─ 명확한 네이밍
    │      ├─ 함수 분리 (Single Responsibility)
    │      └─ 주석 추가
    │
    ├─► 2. 정적 분석
    │      ├─ pylint
    │      │  ```bash
    │      │  uv run pylint pages/7_72_앱_시니어복지.py
    │      │  ```
    │      │  └─ 0 errors 목표
    │      │
    │      └─ mypy (타입 체크)
    │         ```bash
    │         uv run mypy pages/7_72_앱_시니어복지.py
    │         ```
    │         └─ 타입 힌트 추가
    │
    ├─► 3. 테스트 재실행
    │      └─ pytest 여전히 PASS 확인
    │
    └─► 4. REFACTOR 완료
           └─ VERIFY 단계로 이동
```

**REFACTOR 후 코드 예시**:

```python
# pages/7_72_앱_시니어복지.py

"""
시니어 복지 페이지

보건복지부, 고용노동부, 여성가족부 정책 정보 표시
"""

import streamlit as st
import pandas as pd
from typing import List, Dict

def get_welfare_policies(department: str) -> pd.DataFrame:
    """부처별 복지 정책 조회

    Args:
        department: 부처명 (보건복지부, 고용노동부, 여성가족부)

    Returns:
        정책 데이터프레임
    """
    # DB 조회 로직
    pass

def render_policy_tab(department: str) -> None:
    """부처별 정책 탭 렌더링

    Args:
        department: 부처명
    """
    st.subheader(f"{department} 정책")
    policies = get_welfare_policies(department)
    st.dataframe(policies)

def main() -> None:
    """메인 함수"""
    st.title("시니어 복지")

    departments = ["보건복지부", "고용노동부", "여성가족부"]
    tabs = st.tabs(departments)

    for tab, dept in zip(tabs, departments):
        with tab:
            render_policy_tab(dept)

if __name__ == "__main__":
    main()
```

### 2.6 VERIFY 단계 (런타임 검증, 필수)

```
VERIFY 단계 시작 (필수)
    │
    ├─► 1. test_page_import.py 확인
    │      ├─ 파일 존재: tests/test_page_import.py
    │      └─ 없으면 템플릿에서 생성
    │         └─ .claude/skills/ootest/templates/test_page_import_template.py
    │
    ├─► 2. import 테스트 실행
    │      ```bash
    │      uv run pytest tests/test_page_import.py -v
    │      ```
    │      ├─ 모든 pages/*.py import
    │      ├─ Streamlit 위젯 key 중복 감지
    │      └─ 런타임 초기화 에러 감지
    │
    ├─► 3. 결과 판단
    │      ├─ PASS → COMPLETE 단계로 이동
    │      └─ FAIL → GREEN 단계로 돌아가 수정
    │
    └─► 4. d{SP}0003 Part E 업데이트
           ```markdown
           | 실행일 | 대상 | 전체 | 통과 | 실패 | 비고 |
           |--------|------|:----:|:----:|:----:|------|
           | 2026-02-05 | pages/*.py (50개) | 50 | 50 | 0 | 전체 통과 |
           ```
```

**런타임 에러 유형**:

| 에러 | 원인 | 감지 방법 |
|------|------|----------|
| StreamlitDuplicateElementKey | 동일 key 중복 | used_keys 추적 |
| ImportError (조건부) | if문 내 import | import 테스트 |
| AttributeError | 런타임 객체 접근 | 모킹 환경 import |
| TypeError | 런타임 타입 불일치 | 함수 호출 테스트 |

**Streamlit key 중복 주의사항**:

```python
# ❌ 잘못된 예 (DuplicateKey 발생)
for item in items:
    st.button("Click", key="btn")  # 루프 내 동일 key

with tab1:
    st.button("Submit", key="submit")  # 탭 간 동일 key
with tab2:
    st.button("Submit", key="submit")  # 중복!

# ✅ 올바른 예
for i, item in enumerate(items):
    st.button("Click", key=f"btn_{i}")  # 고유 key

with tab1:
    st.button("Submit", key="tab1_submit")  # 탭별 고유 key
with tab2:
    st.button("Submit", key="tab2_submit")
```

### 2.7 COMPLETE 단계 (문서 갱신)

```
COMPLETE 단계
    │
    ├─► 1. d{SP}0003 Part C 상태 업데이트
    │      ```markdown
    │      | TC ID | Task ID | 테스트명 | 파일 | 상태 |
    │      |-------|---------|----------|------|------|
    │      | TC002-1.1 | F002-1.1 | 보건복지부 탭 | tests/TC002-1.1_보건복지부탭.py | [x] |
    │      ```
    │
    ├─► 2. d{SP}0002 Plan 상태 업데이트
    │      ```markdown
    │      #### F002-1.1: 보건복지부 탭
    │      - **상태**: 완료 ✓
    │      ```
    │
    └─► 3. 다음 Task로 이동
           └─ F002-1.2: 고용노동부 탭
```

## 3. 상세 사용법

### 3.1 서브명령어

#### 3.1.1 oodev status

서브명령어 리스트 및 진행 상태

```bash
oodev status
```

**출력 예시**:
```
=== oodev 서브명령어 ===
- run: 미완료 Feature 전체 구현
- run [ID]: 특정 Feature 구현
- queue: 대기 큐 처리
- optimize: 코드 최적화
- version: v06

=== 진행 상태 ===
- Plan: 00_doc/sp00/d0002_plan.md
- 전체 Task: 24개
- 완료: 15개 (62.5%)
- 진행 중: F002-1.2
- 대기: 8개
```

#### 3.1.2 oodev run [ID]

Feature/Task 구현

```bash
# 미완료 전체 구현
oodev run

# 특정 Feature 구현
oodev run F002-1

# 특정 Task 구현
oodev run F002-1.1

# 서브프로젝트 지정
oodev run F002-1 --sp 02
```

**개발 대상 조건**:
1. d{SP}0002_plan.md에 Task 세분화 완료
2. 상태가 "완료"가 아님
3. PRD 5.1 페이지 개요에서 `진행=예`

#### 3.1.3 oodev queue

대기 큐 처리 (ooplan detail에서 추가된 Task)

```bash
oodev queue
```

#### 3.1.4 oodev optimize

코드 최적화

```bash
oodev optimize                          # 전체
oodev optimize pages/7_72_앱_시니어복지.py  # 특정 파일
oodev optimize --dry-run                # 분석만
```

### 3.2 옵션

| 옵션 | 설명 |
|------|------|
| `--max-iterations N` | 최대 반복 횟수 (기본 10) |
| `--timeout M` | 타임아웃 (초) |
| `--interactive` | 단계별 확인 |
| `--skip-refactor` | REFACTOR 생략 |
| `--sp N` | 서브프로젝트 번호 |
| `--framework NAME` | 프레임워크 명시 (streamlit, django 등) |

**프레임워크 자동 감지**:

| 조건 | 감지 결과 | 참조 가이드 |
|------|----------|-----------|
| `pages/*.py` 존재 or `import streamlit` 검출 | Streamlit | `references/streamlit_guide.md` |
| `--framework streamlit` 명시 | Streamlit (강제) | `references/streamlit_guide.md` |
| 감지 없음 | 일반 TDD 모드 | - |

> `--framework` 명시가 자동 감지보다 우선. 새 프로젝트 시작 시 명시 지정 권장.

### 3.3 TDD 체크리스트

#### RED (실패 테스트)
- [ ] Task 요구사항 명확히 이해
- [ ] TC 파일 네이밍 규칙 준수
- [ ] Arrange-Act-Assert 구조
- [ ] pytest 실행 FAIL 확인
- [ ] d{SP}0003 Part C 등록

#### GREEN (최소 구현)
- [ ] 테스트 통과를 위한 최소 코드
- [ ] YAGNI 원칙 준수
- [ ] pytest 실행 PASS 확인
- [ ] 과도한 구현 지양

#### REFACTOR (품질 개선)
- [ ] 중복 제거 (DRY)
- [ ] 명확한 네이밍
- [ ] 함수 분리 (SRP)
- [ ] pylint 0 errors
- [ ] mypy 타입 체크
- [ ] pytest 여전히 PASS

#### VERIFY (런타임 검증)
- [ ] test_page_import.py 실행
- [ ] import 테스트 PASS
- [ ] DuplicateKey 없음
- [ ] 런타임 에러 없음
- [ ] d{SP}0003 Part E 업데이트

#### COMPLETE (문서 갱신)
- [ ] d{SP}0003 Part C 상태 [x]
- [ ] d{SP}0002 Plan 상태 "완료"
- [ ] 다음 Task 진행

## 4. 사용 예시

### 4.1 첫 실행 (테스트 문서 생성)

**시나리오**: 새 프로젝트에서 oodev 첫 실행

```bash
# 1. Plan 준비 확인
ls 00_doc/sp00/d0002_plan.md
# → 존재 (ooplan 완료)

# 2. oodev 첫 실행
oodev run

# === INIT 단계 시작 ===
# d0003_test.md 없음 → 자동 생성

# PRD 로드: 00_doc/sp00/d0001_prd.md
# Part A 생성: 에러체크 항목
# Part B 생성: 15개 시나리오 도출 (PRD 기반)
# Part C 생성: 빈 테이블
# Part D 생성: 43개 oo 모듈 스캔
# Part E 생성: 런타임 검증 템플릿

# → 00_doc/sp00/d0003_test.md 생성 완료

# === TDD 사이클 시작 ===
# Task: F001-1.1 로그인 UI
# ...
```

### 4.2 TDD 사이클 실행

**시나리오**: Feature F002-1 구현

```bash
# 1. Feature 실행
oodev run F002-1

# === RED 단계 ===
# Task: F002-1.1 보건복지부 탭
# TC 파일 생성: tests/TC002-1.1_보건복지부탭.py
# pytest 실행: FAILED (예상됨)
# d0003 Part C 등록: TC002-1.1 [ ]

# === GREEN 단계 ===
# 최소 구현: pages/7_72_앱_시니어복지.py
# pytest 실행: PASSED ✓

# === REFACTOR 단계 ===
# 코드 정리: 함수 분리, 네이밍 개선
# pylint: 0 errors ✓
# mypy: 타입 체크 통과 ✓
# pytest 재실행: PASSED ✓

# === VERIFY 단계 ===
# pytest tests/test_page_import.py -v
# pages/7_72_앱_시니어복지.py: PASSED ✓
# DuplicateKey 없음 ✓
# d0003 Part E 업데이트

# === COMPLETE ===
# d0003 Part C 상태: [x]
# d0002 Plan 상태: 완료
# 다음 Task: F002-1.2

# === 총 3개 Task 완료 ===
# F002-1.1, F002-1.2, F002-1.3
```

### 4.3 런타임 에러 수정

**시나리오**: VERIFY 단계에서 DuplicateKey 발견

```bash
# VERIFY 단계
uv run pytest tests/test_page_import.py -k "7_72" -v

# FAILED: DuplicateElementKey: Duplicate key 'btn'
# pages/7_72_앱_시니어복지.py:45

# → GREEN 단계로 돌아가 수정

# 수정 전:
# for item in items:
#     st.button("Click", key="btn")  # 중복!

# 수정 후:
# for i, item in enumerate(items):
#     st.button("Click", key=f"btn_{i}")  # 고유 key

# 재실행
uv run pytest tests/test_page_import.py -k "7_72" -v
# PASSED ✓

# COMPLETE 단계로 이동
```

### 4.4 특정 Task만 구현

**시나리오**: Task F002-1.1만 단독 구현

```bash
oodev run F002-1.1

# RED → GREEN → REFACTOR → VERIFY → COMPLETE
# 1개 Task 완료
```

### 4.5 코드 최적화

**시나리오**: 구현 완료 후 전체 코드 최적화

```bash
oodev optimize

# === 최적화 분석 ===
# - 중복 함수 3개 발견 → 통합 권장
# - 복잡도 높은 함수 2개 → 분리 권장
# - 타입 힌트 누락 5개 → 추가 권장

# 승인 (y 입력)

# === 최적화 완료 ===
# - 중복 제거: 3건
# - 함수 분리: 2건
# - 타입 힌트 추가: 5건
# pytest 재실행: 전체 PASS ✓
```

## 4.5 dXXXX 모드 워크플로우

```
dXXXX 지정
    ↓
00_doc/ 하위에서 dXXXX_*.md 자동 탐색
    ↓
[단계 감지]
  상세기획 단계 → 차단: "설계 미완료. `oofeature next dXXXX`로 설계 전환 후 설계를 완료하세요"
  상세설계 단계 → 파일명 rename (설계→개발) 후 계속
  상세개발 단계 → 계속 (이미 개발 단계)
  상세검증/완료  → 안내: "이미 검증/완료 단계. `oocheck run dXXXX` 실행"
    ↓
문서에서 개발 스펙 추출 (Feature/Task 단위)
    ↓
문서 내 Task 구조 없을 경우:
  → 문서 내용 분석 → Feature/Task 자동 분해
    ↓
ootest write (RED: TC 코드 작성 → 반드시 실패 확인)
    ↓
TDD 사이클 실행 (GREEN→REFACTOR→VERIFY)
    ↓
완료 상태를 해당 문서에 기록 (d{SP}0003_test.md 연동)
```

## 4.6 GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 페이즈 실행 (TDD) | `oodev run` | `/gsd:execute-phase [N]` |
| 자연어 작업 라우팅 | 직접 명령 | `/gsd:do "작업 설명"` |
| 빠른 단일 작업 | `oodev run [ID]` | `/gsd:quick "작업"` |
| 자율 실행 (무인) | `oodev run` | `/gsd:autonomous` |

**차이점**:
- `oodev run` → TDD 사이클(Red→Green→Refactor), d{SP}0003 테스트 문서 연동
- `/gsd:execute-phase` → gsd-executor 에이전트, 원자적 커밋, 체크포인트 프로토콜

**조합 패턴**:

```
/gsd:plan-phase 1         # GSD 계획 생성
  ↓
oodev run                 # TDD 사이클 구현 + OAIS 문서 갱신
  OR
/gsd:execute-phase 1      # GSD 방식 페이즈 실행
  ↓
oocheck run               # 코드 품질 검증
```

## 5. 관련 문서

### 5.1 스킬 및 명령어

| 문서 | 역할 |
|------|------|
| `.claude/skills/oodev/SKILL.md` | 본 스킬 정의 |
| `.claude/skills/ooplan/SKILL.md` | 구현 계획 (선행) |
| `.claude/skills/ootest/SKILL.md` | 테스트 실행 (연계) |
| `.claude/skills/oocheck/SKILL.md` | 코드 체크 (연계) |
| `.claude/commands/sc/implement.md` | 구현 명령어 |
| `.claude/commands/sc/build.md` | 빌드 명령어 |
| `.claude/commands/sc/test.md` | 테스트 명령어 |

### 5.2 템플릿

| 파일 | 용도 |
|------|------|
| `.claude/skills/ootest/templates/test/common_test_template.md` | d0003 테스트 문서 템플릿 |
| `.claude/skills/ootest/templates/test_page_import_template.py` | 런타임 검증 템플릿 |

### 5.3 핵심 문서

| 문서 | 역할 |
|------|------|
| `00_doc/d{SP}0002_plan.md` | 구현 계획 (입력) |
| `00_doc/d{SP}0003_test.md` | 테스트 문서 (출력) |
| `00_doc/d{SP}0004_todo.md` | 이슈 등록 |
| `tests/TC*.py` | 단위 테스트 파일 |
| `tests/test_page_import.py` | 런타임 검증 (필수) |

### 5.4 공통 가이드

| 문서 | 역할 |
|------|------|
| `.claude/guides/common_guide.md` | 프로젝트 공통 개발 표준 |
| `.claude/skills/ootest/references/guide.md` | 테스트 방법론 |
| `.claude/skills/ooplan/references/guide.md` | 구현 계획 가이드 |
