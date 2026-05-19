# ootest_guide - 테스트 통합 가이드

## 문서 이력 관리
- v11 2026-04-21 — 섹션 12 추가: 기능 기반 테스트 리스트 작성 & 코드 생성 (UI 포함)
- v10 2026-03-30 — 섹션 11 추가: 외부 시스템 부수효과(Side Effect) 검증 — 3단계 검증 모델(L1/L2/L3)
- v09 2026-01-25 — 파일명 변경: test_guide.md → ootest_guide.md (네이밍 규칙 통일)
- v08 2026-01-05 — Part D 정합성: 43개 모듈, 11개 카테고리 (Config 추가)
- v07 2026-01-05 — Part E 런타임 검증 섹션 추가 (섹션 7)

---

## 1. 개요

### 1.1 문서 목적

테스트 **방법론(How)**을 정의하는 통합 가이드입니다.

### 1.2 역할 분리

| 문서 유형 | 역할 | 예시 |
|----------|------|------|
| `d*003_test.md` | **무엇을(What)** 테스트할 것인가 | TC 목록, 체크리스트, 시나리오 항목 |
| `.claude/skills/ootest/references/guide.md` | **어떻게(How)** 테스트할 것인가 | 방법론, 워크플로우, 도구 사용법 |
| `.claude/skills/ootest/SKILL.md` | 테스트 실행 스킬 | 명령어, 자동화 |
| `.claude/skills/oodev/SKILL.md` | 테스트 문서 생성 | 개발 첫 실행 시 d0003 자동 생성 |

### 1.2.1 문서 생성 워크플로우

> **컨텍스트 적용**: `oocontext.md` 규칙에 따라 SP별 문서 생성
> - SP=00: `d0003_test.md` ← `d0001_prd.md`
> - SP=02: `d20003_test.md` ← `d20001_prd.md`

```
ooprd run (신규 프로젝트)
    ↓
d{SP}0001_prd.md 생성
    ↓
oodev run (첫 실행)
    ↓
d{SP}0003_test.md 존재? → 없음: 자동 생성
    ├── Part A: 공통 에러체크 (고정 항목)
    ├── Part B: PRD 기능에서 시나리오 도출
    ├── Part C: 빈 테이블 (TDD RED에서 등록)
    └── Part D: oo 모듈 스캔하여 자동 생성
    ↓
TDD 사이클 시작 (RED → GREEN → REFACTOR)
```

**스킬별 d0003 조작:**

| 스킬 | 역할 | Part |
|------|------|------|
| oodev | **생성** | 전체 (첫 실행 시) |
| oodev | **등록** | Part C (TDD RED) |
| ootest | **갱신** | 실행 결과 테이블 |
| ootest refresh | **재스캔** | Part D 모듈 목록 |

### 1.3 테스트 구조 (5 Part)

| Part | 이름 | 목적 | 주요 도구 |
|------|------|------|----------|
| A | 에러체크 | 정적 분석, 코드 품질 | pylint, mypy |
| B | 시나리오 테스트 | E2E/UI 검증 | Playwright MCP |
| C | 단위 테스트 | TDD 기반 함수/클래스 검증 | pytest |
| D | oo 모듈 테스트 | oo 모듈 전체 검증 | pytest |
| **E** | **런타임 검증** | **import 시 런타임 에러 감지** | **pytest (필수)** |

---

## 2. 공통 정의

### 2.1 우선순위

| 우선순위 | 설명 | 테스트 시점 |
|----------|------|-------------|
| P0-Critical | 핵심 기능, 시스템 장애 유발 가능 | 즉시/매 빌드 |
| P1-High | 주요 기능, 사용자 영향 큼 | 24시간 내/매일 |
| P2-Medium | 일반 기능, 사용자 영향 보통 | 1주일 내/주간 |
| P3-Low | 부가 기능, 사용자 영향 적음 | 백로그/릴리스 전 |

### 2.2 상태 표기

| 상태 | 설명 | 표기 |
|------|------|------|
| 대기 | 테스트 미실행 | `[ ]` |
| 진행중 | 테스트 실행 중 | `[~]` |
| 통과 | 테스트 성공 | `[x]` |
| 실패 | 테스트 실패 | `[!]` |
| 스킵 | 테스트 건너뜀 | `[-]` |

### 2.3 에러 분류 체계

| 분류 | 설명 | 우선순위 | 이력 태그 |
|------|------|----------|----------|
| [CRITICAL] | 시스템 장애, 보안 취약점 | P0 - 즉시 | [HOTFIX] |
| [ERROR] | 기능 오작동, 예외 미처리 | P1 - 24시간 | [BUGFIX] |
| [WARNING] | 잠재적 문제, 성능 이슈 | P2 - 1주일 | [IMPROVE] |
| [INFO] | 코드 스타일, 개선 권장 | P3 - 백로그 | [ENHANCE] |

### 2.4 커버리지 목표

| 유형 | 목표 |
|------|------|
| Unit Test | 80% |
| Integration | 70% |
| E2E Critical Path | 100% |

---

## 3. Part A: 에러체크

정적 분석 기반 코드 품질/보안/성능 검증

> **검사 기준**: `.claude/guides/common_guide.md` (코드 품질, 보안, 성능 표준)
> **결과 기록**: `d*003_test.md` Part A 테이블에 실행 결과만 기록

### 3.1 워크플로우

```
검사 실행 (oocheck / pylint / flake8 / mypy)
    ↓
결과 기록 (d0003_test.md Part A 테이블)
    ↓
이슈 발견 시 → d0004_todo.md 등록
    ↓
수정 및 재검사
```

### 3.2 결과 기록 형식

```markdown
| 실행일 | 도구 | 대상 | 결과 | 비고 |
|--------|------|------|------|------|
| 2026-01-03 | py_compile | src/ (43개) | PASS | 전체 통과 |
| 2026-01-03 | pylint | src/ | 0 errors | W0621 다수 |
```

### 3.3 도구 및 명령어

**Bash 도구:**
```bash
python -m py_compile <file.py>  # 문법 체크
pylint <file.py>                # 린터
flake8 <file.py>                # 린터
mypy <file.py>                  # 타입 체크
```

### 3.4 서브에이전트 호출

**정적 분석 (python-code-reviewer)**
```
Task(
  subagent_type="python-code-reviewer",
  prompt="oo/ 모듈 정적 분석: 타입 힌트, 미사용 import, 예외 처리, PEP8"
)
```

**품질 분석 (ooqa)**
```
Task(
  subagent_type="ooqa",
  prompt="oo/ 모듈 분석: 중복 정의, 순환 참조, 복잡도, 리팩토링 영역"
)
```

### 3.5 용어체크

표준용어집(`00_doc/기획/TErm/`) 기준 DB/코드 명명 일관성 검증

**불일치 유형:**
| 유형 | 설명 | 예시 |
|------|------|------|
| 용어 미등록 | 용어집에 없음 | `agent` (용어집: 대리인) |
| 표기 불일치 | 다르게 표기 | `company` vs `corp` |
| 영문/한글 혼용 | 일관성 없음 | `user_업체` |
| 약어 미정의 | 정의 없는 약어 | `biz_no` |

**권장 용어:**
| 한글 | 권장 영문 | 비권장 |
|------|----------|--------|
| 업체 | company | corp, firm |
| 사용자 | user | member |
| 사업자번호 | business_number | biz_no |

---

## 4. Part B: 시나리오 테스트

사용자 관점 E2E/UI/통합 테스트

> **시나리오 항목**: PRD(`d*001_prd.md`) 기능 목록에서 도출
> **결과 기록**: `d*003_test.md` Part B 테이블에 실행 결과만 기록

### 4.1 테스트 유형

| 유형 | 목적 | 도구 | 자동화 |
|------|------|------|--------|
| E2E | 전체 흐름 검증 | Playwright | 권장 |
| UI | 화면/인터페이스 | Playwright | 부분 |
| 통합 | 모듈 간 상호작용 | pytest | 권장 |
| 회귀 | 기존 기능 확인 | 기존 스위트 | 필수 |

### 4.2 워크플로우

```
PRD 기능 목록에서 시나리오 도출
    ↓
테스트 실행 (Playwright MCP / 수동)
    ↓
결과 기록 (d0003_test.md Part B 테이블)
    ↓
실패 시 → d0004_todo.md 등록
```

### 4.3 항목 + 결과 구조

**테스트 항목** (PRD 기반, 변경 적음):
```markdown
| ID | 시나리오 | 우선순위 |
|----|----------|:--------:|
| B1-1 | 정상 로그인 | P0 |
| B1-2 | 로그인 실패 | P1 |
```

**실행 결과** (테스트 시마다 추가):
```markdown
| 실행일 | ID | 결과 | 비고 |
|--------|-----|:----:|------|
| 2026-01-03 | B1-1 | PASS | - |
| 2026-01-03 | B1-2 | FAIL | d20004 등록 |
```

### 4.4 Playwright MCP

| 도구 | 용도 |
|------|------|
| `browser_navigate` | URL 이동 |
| `browser_snapshot` | 페이지 스냅샷 |
| `browser_take_screenshot` | 스크린샷 캡처 |
| `browser_click` | 요소 클릭 |
| `browser_type` | 텍스트 입력 |
| `browser_fill_form` | 폼 전체 입력 |
| `browser_wait_for` | 대기 |

**기본 흐름:** `navigate → snapshot → click/type → screenshot → 검증`

**스크린샷 저장:**
- 경로: `tmp/test_screenshots/`
- 네이밍: `[시나리오ID]_[단계]_[YYYYMMDD_HHMMSS].png`

### 4.5 서브에이전트 호출

**E2E 웹 테스트 (web-test-orchestrator)**
```
Task(
  subagent_type="web-test-orchestrator",
  prompt="plan_srv E2E 테스트: 로그인, 핵심 기능, 에러 상황"
)
```

### 4.6 테스트 환경 설정

```env
AUTOLOGIN=true  # E2E 테스트용
```

| 환경 | AUTOLOGIN | 용도 |
|------|-----------|------|
| 테스트 | true | E2E/UI 자동화 |
| 개발 | true/false | 편의에 따라 |
| 운영 | false | 실제 로그인 |

---

## 5. Part C: 단위 테스트 (TDD)

TDD(Test-Driven Development) 기반 단위 테스트

### 5.1 TDD 워크플로우

```
oodev run [태스크]
    ↓
RED: 테스트 작성 → d0003 Part C 등록
    ↓
GREEN: 구현 → 테스트 통과
    ↓
d0003 Part C 상태 업데이트 ([x])
    ↓
REFACTOR: 코드 정리
```

### 5.2 TC 네이밍 규칙

| 레벨 | 형식 | 예시 |
|------|------|------|
| Epic | `E{순번}` | E002 |
| Feature | `F{Epic}-{순번}` | F002-1 |
| Task | `F{Epic}-{Feature}.{순번}` | F002-1.1 |
| TC | `TC{Epic}-{Feature}.{Task}` | TC002-1.1 |

**Task ↔ TC 1:1 매핑:**
```
Task:  F002-1.1 (보건복지부 탭)
TC:   TC002-1.1_보건복지부탭.py
```

### 5.3 테스트 파일 구조

```
tests/
├── conftest.py                      # 공통 fixture
├── TC001-1.1_로그인성공.py          # F001-1.1
├── TC001-1.2_로그인실패.py          # F001-1.2
├── TC002-1.1_보건복지부탭.py        # F002-1.1
└── TC002-1.2_고용노동부탭.py        # F002-1.2
```

### 5.4 테스트 파일 템플릿

```python
"""
TC002-1.1_보건복지부탭.py - 보건복지부 탭 테스트

TC ID: TC002-1.1
Task ID: F002-1.1
Feature: F002-1 중앙정부 정책
"""
import pytest


class TestTC002_1_1_보건복지부탭:
    """TC002-1.1: 보건복지부 탭 테스트"""

    def test_tab_renders_correctly(self):
        """보건복지부 탭 정상 렌더링"""
        # Arrange
        # Act
        # Assert
        assert True
```

### 5.5 TC 코드 작성 가이드

#### 5.5.1 AAA 패턴 (Arrange / Act / Assert)

모든 테스트 메서드는 AAA 3단계로 작성한다.

```python
def test_로그인_성공(self):
    # Arrange: 전제 조건·입력값 준비
    username = "admin"
    password = "correct_pw"

    # Act: 테스트 대상 실행
    result = login(username, password)

    # Assert: 결과 검증
    assert result["success"] is True
    assert result["token"] is not None
```

**원칙**:
- Arrange가 길면 fixture로 분리
- Act는 1줄 (함수 1번 호출)
- Assert는 검증 목적별로 1개씩 (`assert` 여러 줄 허용, 단 한 메서드에 여러 관심사 혼합 금지)

---

#### 5.5.2 테스트 케이스 유형

| 유형 | 설명 | 우선순위 |
|------|------|:-------:|
| **정상(Happy Path)** | 올바른 입력 → 기대 결과 | P0 |
| **예외(Error Path)** | 잘못된 입력 → 에러/거부 | P1 |
| **경계값(Boundary)** | min/max, 빈값, None | P1 |
| **부수효과(Side Effect)** | DB저장·파일생성 등 외부 반영 확인 | P1 |

**각 TC당 최소 3케이스**: 정상 1개 + 예외 1개 + 경계값 1개

```python
class TestTC001_1_1_로그인:

    def test_정상_로그인(self):          # Happy Path
        ...

    def test_비밀번호_틀림(self):        # Error Path
        ...

    def test_빈_아이디(self):            # Boundary
        ...
```

---

#### 5.5.3 fixture / conftest.py

**공통 fixture는 `tests/conftest.py`에 정의:**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def db():
    """인메모리 DB 연결 (테스트 격리)"""
    conn = sqlite3.connect(":memory:")
    init_schema(conn)
    yield conn
    conn.close()

@pytest.fixture
def auth_user():
    """인증된 사용자 세션"""
    return {"user_id": "test_user", "role": "admin"}
```

**TC 파일에서 fixture 사용:**

```python
def test_사용자_조회(self, db, auth_user):
    result = get_user(db, auth_user["user_id"])
    assert result is not None
```

**fixture 범위(scope):**

| scope | 재생성 시점 | 용도 |
|-------|------------|------|
| `function` (기본) | 테스트마다 | 격리 필요한 상태 |
| `class` | 클래스마다 | 클래스 공유 설정 |
| `module` | 파일마다 | DB 초기화 등 비용 큰 작업 |
| `session` | 전체 1회 | 서버 연결 등 |

---

#### 5.5.4 mock / patch

외부 의존성(DB, API, 파일시스템)을 격리할 때 사용.

```python
from unittest.mock import patch, MagicMock

def test_외부API_호출(self):
    with patch("oo.services.requests.get") as mock_get:
        # 가짜 응답 설정
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "ok"}

        result = fetch_external_data("https://api.example.com")

        # 호출 여부·인자 검증
        mock_get.assert_called_once_with("https://api.example.com")
        assert result["data"] == "ok"
```

**데코레이터 방식 (메서드 전체 모킹):**

```python
@patch("oo.db.get_connection")
def test_DB_연결_실패(self, mock_conn):
    mock_conn.side_effect = ConnectionError("DB 연결 불가")
    with pytest.raises(ConnectionError):
        get_user("user1")
```

**모킹 대상 경칙**: 테스트 대상 모듈 기준 경로 사용
- `oo.services.requests.get` (O) — 실제 import 위치
- `requests.get` (X) — 원본 위치

---

#### 5.5.5 parametrize (다중 케이스)

동일 로직을 여러 입력값으로 반복 검증할 때 사용.

```python
@pytest.mark.parametrize("input_val, expected", [
    ("123-45-67890", True),   # 정상
    ("000-00-00000", False),  # 무효
    ("",             False),  # 빈값
    (None,           False),  # None
])
def test_사업자번호_검증(self, input_val, expected):
    assert validate_business_number(input_val) == expected
```

---

#### 5.5.6 assert 작성 원칙

| 상황 | 권장 assert |
|------|------------|
| 값 일치 | `assert result == expected` |
| None 확인 | `assert result is not None` |
| 타입 확인 | `assert isinstance(result, list)` |
| 예외 발생 | `with pytest.raises(ValueError):` |
| 포함 확인 | `assert "keyword" in result` |
| 길이 확인 | `assert len(result) > 0` |
| 호출 확인 | `mock.assert_called_once_with(arg)` |

**실패 메시지 명시 (디버깅 용이):**

```python
assert result["status"] == "OK", f"기대: OK, 실제: {result['status']}"
```

---

### 5.6 d0003 Part C 등록 형식

```markdown
## C2. 등록된 단위 테스트

### E001: 인증/권한 시스템

| TC ID | Task ID | 테스트명 | 파일 | 상태 |
|-------|---------|----------|------|------|
| TC001-1.1 | F001-1.1 | 로그인 성공 | tests/TC001-1.1_로그인성공.py | [x] |
| TC001-1.2 | F001-1.2 | 로그인 실패 | tests/TC001-1.2_로그인실패.py | [ ] |
```

### 5.7 서브에이전트 호출

**TDD 개발 (task-executor)**
```
Task(
  subagent_type="task-executor",
  prompt="TDD 구현: F002-1.1 보건복지부 탭
  1. RED: TC002-1.1 테스트 작성
  2. d0003 Part C 등록
  3. GREEN: 최소 구현
  4. REFACTOR: 정리"
)
```

---

## 6. Part D: oo 모듈 테스트

oo/*.py 전체 모듈 기능 검증 (43개 모듈, 11개 카테고리)

### 6.0 SP별 Part D 처리 (중복 방지)

> oo 모듈은 공통이므로 **d0003에서만 관리**, 서브프로젝트는 참조

| SP | Part D 처리 |
|:--:|------------|
| 00 | oo 모듈 스캔하여 직접 생성 (`d0003_test.md`) |
| ≠00 | `"d0003_test.md Part D 참조"` 링크만 추가 |

**d20003_test.md Part D 예시:**
```markdown
## Part D: oo 모듈 테스트

> **참조**: `d0003_test.md` Part D 참조
> oo 모듈은 공통이므로 d0003에서 통합 관리합니다.
```

### 6.1 테스트 대상

| 카테고리 | 모듈 수 | 함수 수 | 검증 내용 |
|----------|:-------:|:-------:|----------|
| Core | 5 | - | DB 연결, 인증, 세션, 관리자 |
| Config | 2 | - | 기본 설정, 설정 헬퍼 |
| Entity | 5 | - | 사용자, 업체, 대리인, 고객, 커뮤니티 |
| Task | 5 | - | 업무 핵심, 조회, 첨부, 관리 |
| Data | 4 | - | 컬럼, 시스템 코드, DB 메타, 데이터 처리 |
| Application | 3 | - | 신청, 사업자등록, 사업자 데이터 |
| File | 5 | - | 파일 연산, 업로드, 관리, OCR, 도장 |
| External | 3 | - | 하이픈 API, 뉴스 API, 서비스 |
| Document | 4 | - | PDF, 영수증, 카드, 도서 요약 |
| Utility | 5 | - | 유틸리티, 날짜, 엑셀, 검증, 재무 |
| UI | 2 | - | UI 렌더링, 모바일 CSS |

### 6.2 테스트 패턴

**DB 함수 테스트:**
```python
import pytest
from oo.db import get_db_connection

@pytest.fixture
def test_db():
    """테스트용 DB 연결"""
    conn = get_db_connection(":memory:")
    yield conn
    conn.close()

def test_get_user_companies(test_db):
    """사용자 업체 조회 테스트"""
    from oo.user import get_user_companies
    result = get_user_companies("test_user")
    assert isinstance(result, pd.DataFrame)
```

**유틸리티 함수 테스트:**
```python
def test_validate_business_number():
    """사업자번호 검증 테스트"""
    from oo.validation import validate_business_number
    assert validate_business_number("123-45-67890") == True
    assert validate_business_number("invalid") == False
```

**UI 함수 테스트:**
```python
def test_render_sidebar():
    """사이드바 렌더링 테스트"""
    from oo.ui import render_sidebar
    result = render_sidebar()
    assert result is not None
```

---

## 7. Part E: 런타임 검증 (필수)

페이지 import 시 발생하는 런타임 에러 사전 감지

> **필수 테스트**: py_compile/pylint로 감지 불가능한 런타임 에러 검증
> **결과 기록**: `d*003_test.md` Part E 테이블에 실행 결과 기록

### 7.1 테스트 목적

정적 분석(Part A)으로 감지할 수 없는 런타임 에러를 사전에 발견합니다.

| 에러 유형 | 원인 | py_compile | pylint | Part E |
|----------|------|:----------:|:------:|:------:|
| StreamlitDuplicateElementKey | 위젯 key 중복 | ❌ | ❌ | ✅ |
| ImportError (조건부) | if문 내 import | ❌ | ❌ | ✅ |
| AttributeError | 런타임 객체 접근 | ❌ | ❌ | ✅ |
| TypeError | 런타임 타입 불일치 | ❌ | ❌ | ✅ |
| NameError (동적) | 동적 변수 참조 | ❌ | ❌ | ✅ |

### 7.2 워크플로우

```
Part A~D 완료
    ↓
Part E: test_page_import.py 실행
    ↓
pages/*.py 동적 import (모킹 환경)
    ↓
런타임 에러 감지 (DuplicateKey, ImportError 등)
    ↓
실패 시 → d{SP}0004 등록
```

### 7.3 테스트 파일 구조

```
tests/
├── test_page_import.py    ← [필수] Part E 런타임 검증
└── conftest.py            ← 공통 fixture
```

**테스트 대상**: `{서브프로젝트}/pages/*.py` 전체

### 7.4 도구 및 명령어

```bash
# Part E만 실행
ootest run --runtime

# pytest 직접 실행
uv run pytest tests/test_page_import.py -v

# 특정 페이지만 테스트
uv run pytest tests/test_page_import.py -k "7_74" -v
```

### 7.5 테스트 핵심 기능

**test_page_import.py 주요 모킹:**

| 모킹 대상 | 목적 | 구현 |
|----------|------|------|
| Streamlit 위젯 | UI 함수 호출 허용 | MockSessionState, MockContextManager |
| 위젯 key 추적 | 중복 key 감지 | used_keys set + DuplicateElementKey 예외 |
| DB 연결 | 순수 코드 검증 | sqlite3.connect 모킹 |
| 세션 상태 | st.session_state 접근 | dict 기반 모킹 |

### 7.6 테스트 패턴

**기본 import 테스트:**
```python
import importlib.util
import sys

def test_page_import(page_file):
    """페이지 파일 import 테스트"""
    spec = importlib.util.spec_from_file_location("page_module", page_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules["page_module"] = module

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        pytest.fail(f"Import failed: {page_file} - {e}")
```

**DuplicateElementKey 감지:**
```python
class MockStreamlit:
    used_keys = set()

    def _check_key(self, key):
        if key in self.used_keys:
            raise DuplicateElementKey(f"Duplicate key: {key}")
        self.used_keys.add(key)
```

### 7.7 결과 기록 형식

```markdown
## Part E: 런타임 검증 결과

| 실행일 | 대상 | 전체 | 통과 | 실패 | 비고 |
|--------|------|:----:|:----:|:----:|------|
| 2026-01-05 | pages/*.py (49개) | 49 | 49 | 0 | 전체 통과 |
```

### 7.8 실패 시 처리

```markdown
# d{SP}0004_todo.md 등록 예시

| ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
|----|--------|------|------|---------|------|
| T030 | 2026-01-05 | [RUNTIME] | 7_74_앱_시니어복지.py DuplicateElementKey | 높음 | 대기 |
```

> **템플릿**: `.claude/skills/ootest/templates/test_page_import_template.py`

---

## 8. 에이전트/도구 매핑

### 8.1 단계별 권장 에이전트

| 단계 | 작업 유형 | 권장 에이전트 | 도구 |
|------|----------|--------------|------|
| Part A 정적 분석 | 코드 분석 | `python-code-reviewer` | pylint, Grep |
| Part A 품질 분석 | 중복/의존성 | `ooqa` | Grep, AST |
| Part B 시나리오 | E2E 웹 테스트 | `web-test-orchestrator` | Playwright MCP |
| Part B 설계 | 테스트 시나리오 | `qa` | Sequential MCP |
| Part C 단위 | TDD 개발 | `task-executor` | pytest |
| Part D oo 모듈 | 모듈 전체 검증 | `task-executor` | pytest |
| **Part E 런타임** | **import 검증** | `task-executor` | **pytest** |
| 결과 검증 | 문서화 | `task-executor` | - |
| 코드 탐색 | 구조 파악 | `Explore` | - |

### 8.2 병렬/순차 실행 가이드

**병렬 실행 (의존성 없음):**
- `python-code-reviewer` + `ooqa` (Part A)
- 여러 모듈 독립 테스트

**순차 실행 (의존성 있음):**
1. Part A 에러체크 → 수정
2. Part A 완료 → Part B 시나리오
3. 결과 → 문서 업데이트

---

## 9. 결과 기록

### 9.1 테스트 사이클 기록

```markdown
### 테스트 사이클: 2026-01-03
**실행자**: [이름] | **대상**: Part A + WEB-1ST-010~030 | **결과**: 25/30 (83%)

**실패**: 에러체크-보안-03, WEB-1ST-010-02 → d0004_todo.md 등록
**스킵**: 호환성-03 (별도 스프린트)
```

### 9.2 테스트 결과 리포트

```
=== 테스트 결과 ===
서버: [URL] | 일시: YYYY-MM-DD HH:MM:SS
총: XX개 | 통과: XX (XX%) | 실패: XX (XX%) | 스킵: XX (XX%)

| 카테고리 | 전체 | 통과 | 실패 |
|----------|------|------|------|
| 에러체크 | 15 | 14 | 1 |
| 로그인 | 5 | 4 | 1 |

실패: [P0] 에러체크-보안-03, [P1] UI-LOGIN-002
→ X개 이슈 d0004_todo.md 등록
```

### 9.3 에러 결과 기록 (d0004_todo.md)

```markdown
| ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
|----|--------|------|------|---------|------|
| T020 | 2026-01-03 | [TEST] | test_login.py::test_invalid FAILED | 중간 | 대기 |
| T021 | 2026-01-03 | [ERR] | conftest.py:23 - fixture 'db' not found | 높음 | 대기 |
```

---

## 10. 명령어 참조

### 10.1 ootest 명령어

| 명령어 | 설명 |
|--------|------|
| `ootest run` | 전체 테스트 실행 |
| `ootest run --unit` | Part C 단위 테스트만 |
| `ootest run --e2e` | Part B 시나리오만 |
| `ootest run --module` | Part D oo 모듈만 |
| `ootest run [시나리오ID]` | 특정 시나리오 |
| `ootest run [P0]` | 우선순위별 |
| `ootest preview` | 테스트 계획만 출력 |

### 10.2 옵션

| 옵션 | 설명 |
|------|------|
| `--screenshot` | 각 단계 스크린샷 |
| `--fail-fast` | 첫 실패 시 중단 |
| `--verbose` | 상세 로그 |

---

## 11. 외부 시스템 부수효과(Side Effect) 검증

### 11.1 개요

비즈니스 로직이 외부 시스템(DB, SCP, API, 웹훅 등)에 결과를 반영하는 경우, **단위 테스트만으로는 실제 반영 여부를 보장할 수 없다.** 3단계 검증 모델을 적용하여 누락 없이 검증한다.

### 11.2 3단계 검증 모델

| 레벨 | 검증 대상 | 질문 | 방법 |
|:----:|----------|------|------|
| **L1** | 단위 모듈 | 함수가 정상 동작하나? | 유효/무효 입력, 연결 실패 등 경계값 테스트 |
| **L2** | 통합 배선 | 메인 로직이 그 함수를 **호출하나?** | mock으로 호출 여부·인자값 assert |
| **L3** | 실제 반영 | 외부 시스템에 **실제로 기록되었나?** | 외부 시스템 직접 조회하여 상태 변경 확인 |

**흔한 함정:** L1만 통과하면 "기능이 된다"고 착각하기 쉽다. L1 통과 ≠ 메인 로직에서 호출됨 ≠ 외부 시스템에 반영됨.

### 11.3 적용 대상

외부 시스템과 연동하는 모든 기능:

| 연동 유형 | L1 예시 | L2 예시 | L3 예시 |
|----------|---------|---------|---------|
| 외부 DB 업데이트 | 함수 단독 호출 테스트 | 배치 엔진이 update 호출하는지 mock 검증 | 외부 DB SELECT로 상태 변경 확인 |
| SCP 파일 전송 | scp_transfer 함수 테스트 | 배치 완료 후 scp_transfer 호출 mock 검증 | 원격 서버에서 파일 존재 확인 |
| 외부 API 콜백 | HTTP 클라이언트 테스트 | 처리 완료 후 콜백 호출 mock 검증 | 외부 API 로그/상태 조회 |
| 이메일/웹훅 발송 | 발송 함수 테스트 | 이벤트 발생 시 발송 호출 mock 검증 | 수신 확인 (메일함, 웹훅 로그) |

### 11.4 검증 필수 경로

각 레벨에서 **3가지 경로**를 모두 검증:

| 경로 | 설명 | L2 assert 예시 |
|------|------|---------------|
| **성공** | 정상 완료 → 외부 반영 | `mock_success.assert_called_once()` |
| **실패** | 비즈니스/인프라 실패 → 외부에 실패 기록 | `mock_fail.assert_called_once()` |
| **스킵** | 조건 미충족 → 외부 호출 안 함 | `mock_process.assert_not_called()` |

### 11.5 테스트 작성 패턴

```python
# L2 통합 배선 테스트 (mock 기반)
with patch("module.update_external") as mock_update:
    run_business_logic(task)
    mock_update.assert_called_once_with(expected_id, expected_data)

# L3 실제 반영 테스트 (외부 시스템 조회)
run_business_logic(task)
conn = get_external_db_connection()
row = conn.execute("SELECT status FROM table WHERE id = ?", (task_id,))
assert row["status"] == "SUCCESS"
```

### 11.6 체크리스트

외부 연동 기능 개발/리뷰 시 확인:

- [ ] L1: 연동 함수 단위 테스트 존재하는가?
- [ ] L2: 메인 로직에서 연동 함수 호출을 mock으로 검증하는가?
- [ ] L2: 모든 task_type/엔드포인트에 대해 검증하는가?
- [ ] L2: 성공/실패/스킵 3가지 경로 모두 검증하는가?
- [ ] L3: 외부 시스템에서 실제 상태 변경을 직접 조회하는가?

---

## 12. 기능 기반 테스트 리스트 작성 & 코드 생성

### 12.1 기능 → 테스트 리스트 도출 원칙

PRD(`d{SP}0001_prd.md`) 또는 계획(`d{SP}0002_plan.md`)에서 기능을 추출해 테스트 리스트를 작성한다.

**도출 공식**: 기능 1개 → 테스트 케이스 최소 4개

| 케이스 유형 | 질문 | 예시 (로그인 기능) |
|------------|------|-----------------|
| 정상(Happy Path) | 올바른 입력이면? | 유효 아이디/비밀번호 → 성공 |
| 예외(Error Path) | 잘못된 입력이면? | 틀린 비밀번호 → 에러 메시지 |
| 경계값(Boundary) | 극단값이면? | 빈 아이디, 최대 길이 초과 |
| UI 상태(UI State) | 화면이 올바른가? | 폼 렌더링, 버튼 활성화 상태 |

### 12.2 전체 워크플로우

```
1. PRD/plan에서 기능 목록 추출
       ↓
2. 각 기능별 4가지 케이스 유형 도출
       ↓
3. UI 기능 → Part B(E2E) + Part C(Unit) 테스트 리스트 추가
   비UI 기능 → Part C(Unit) + Part D(Module) 테스트 리스트 추가
       ↓
4. TC ID 부여 & d{SP}0003_test.md 등록
       ↓
5. 테스트 코드 파일 일괄 생성
       ↓
6. pytest --collect-only 로 수집 확인 → RED 확인
```

### 12.3 UI / 비UI 기능 분류

| 분류 | 기준 | 테스트 Part |
|------|------|------------|
| UI 기능 | 화면 렌더링, 위젯 상호작용, 화면 전환 | Part B(E2E) + Part C(Unit) |
| 비UI 기능 | 데이터 처리, DB 조작, API 호출 | Part C(Unit) + Part D(Module) |

### 12.4 UI 테스트 리스트 작성 (Streamlit 기준)

Streamlit UI 기능에 대해 다음 4가지 항목을 항상 도출한다:

| 항목 유형 | 테스트 대상 | 검증 방법 |
|----------|------------|----------|
| **렌더링** | 컴포넌트가 존재하는가? | `render_*()` 반환값 assert |
| **입력 처리** | 입력값이 올바르게 처리되는가? | 함수 직접 호출 + 반환값 검증 |
| **상태 변화** | `st.session_state`가 변경되는가? | 모킹된 session_state 검증 |
| **E2E 흐름** | 전체 UI 흐름이 동작하는가? | Playwright MCP |

**UI 기능별 테스트 리스트 도출 예시 (대시보드 기능):**

```markdown
| TC ID | 테스트 항목 | 유형 | Part |
|-------|------------|------|------|
| TC002-1.1 | 사이드바 정상 렌더링 | UI-렌더링 | C |
| TC002-1.2 | 선택 없을 때 기본 상태 표시 | UI-상태 | C |
| TC002-1.3 | 탭 클릭 시 컨텐츠 변경 | UI-E2E | B |
| TC002-1.4 | 빈 데이터일 때 안내 메시지 | UI-경계값 | C |
```

### 12.5 테스트 리스트 → 코드 생성

**Step 1: d{SP}0003_test.md Part C 리스트 작성**

```markdown
## Part C: 단위 테스트 목록

| TC ID | 기능 | 테스트명 | 유형 | 우선순위 |
|-------|------|---------|------|---------|
| TC002-1.1 | 대시보드 | 사이드바 정상 렌더링 | UI-렌더링 | P0 |
| TC002-1.2 | 대시보드 | 빈 데이터 안내 메시지 | UI-경계값 | P1 |
| TC003-1.1 | 검색 | 키워드 검색 성공 | 정상 | P0 |
| TC003-1.2 | 검색 | 빈 키워드 검색 | 경계값 | P1 |
```

**Step 2: TC 파일 생성 (UI 기능)**

```python
# tests/TC002-1.1_사이드바렌더링.py
"""
TC002-1.1 - 사이드바 정상 렌더링

TC ID: TC002-1.1
Task ID: F002-1.1
Feature: F002 대시보드
유형: UI-렌더링
"""
import pytest
from unittest.mock import patch, MagicMock


class TestTC002_1_1_사이드바렌더링:

    def test_정상_렌더링(self):
        """[Happy Path] 사이드바가 정상 렌더링된다"""
        # Arrange
        # Act
        from oo.ui import render_sidebar
        result = render_sidebar()
        # Assert
        assert result is not None

    def test_빈_데이터_렌더링(self):
        """[Boundary] 데이터 없을 때 에러 없이 렌더링된다"""
        # Arrange
        empty_data = []
        # Act
        from oo.ui import render_sidebar
        result = render_sidebar(data=empty_data)
        # Assert
        assert result is not None

    def test_잘못된_입력_처리(self):
        """[Error Path] 잘못된 입력 시 적절한 에러를 반환한다"""
        # Arrange / Act / Assert
        from oo.ui import render_sidebar
        with pytest.raises((TypeError, ValueError)):
            render_sidebar(data="invalid_type")
```

**Step 3: TC 파일 생성 (비UI 기능)**

```python
# tests/TC003-1.1_키워드검색성공.py
"""
TC003-1.1 - 키워드 검색 성공

TC ID: TC003-1.1
Task ID: F003-1.1
Feature: F003 데이터 검색
유형: 정상/예외/경계값
"""
import pytest
from unittest.mock import patch


class TestTC003_1_1_키워드검색:

    def test_정상_검색(self, db):
        """[Happy Path] 유효한 키워드로 결과 반환"""
        # Arrange
        keyword = "복지"
        # Act
        from oo.search import search_data
        result = search_data(db, keyword)
        # Assert
        assert isinstance(result, list)
        assert len(result) > 0

    def test_빈_키워드(self, db):
        """[Boundary] 빈 키워드 입력 시 빈 리스트 반환"""
        from oo.search import search_data
        result = search_data(db, "")
        assert result == []

    def test_존재하지_않는_키워드(self, db):
        """[Error Path] 매칭 없을 때 빈 리스트 반환"""
        from oo.search import search_data
        result = search_data(db, "XXXXNONEXISTENT")
        assert result == []
```

**Step 4: conftest.py UI fixture 추가**

```python
# tests/conftest.py (UI fixture 추가)
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_st():
    """Streamlit 전체 모킹"""
    with patch("streamlit") as mock:
        mock.session_state = {}
        mock.sidebar = MagicMock()
        mock.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        yield mock

@pytest.fixture
def mock_session_state():
    """st.session_state 모킹 (dict 기반)"""
    state = {}
    with patch("streamlit.session_state", state):
        yield state
```

### 12.6 일괄 코드 생성 요청 프롬프트

테스트 리스트 완성 후 일괄 생성 요청 표준 프롬프트:

```
d{SP}0003_test.md Part C 테스트 리스트를 기반으로 아래 작업을 수행하세요:

1. 리스트의 모든 TC에 대해 tests/ 폴더에 파일 생성
   - 네이밍: TC{Epic}-{Feature}.{Task}_{테스트명}.py
2. 각 파일: 정상/예외/경계값 최소 3개 테스트 메서드 포함 (AAA 패턴)
3. UI 기능 TC: mock_st / mock_session_state fixture 사용
4. conftest.py: 필요한 공통 fixture 추가
5. 생성 후 `uv run pytest --collect-only` 로 TC 수집 확인
6. 모든 TC가 FAILED(RED) 상태인지 확인
```

### 12.7 테스트 리스트 완성도 체크리스트

- [ ] 모든 PRD 기능에 TC ID가 부여되었는가?
- [ ] UI 기능에 렌더링/입력처리/상태변화/E2E 4가지 항목이 있는가?
- [ ] 비UI 기능에 정상/예외/경계값 3가지 항목이 있는가?
- [ ] Part B(E2E) 시나리오와 Part C(Unit) 목록이 연결되는가?
- [ ] 모든 TC에 대해 코드 파일이 생성되었는가?
- [ ] `pytest --collect-only` 실행 시 모든 TC가 수집되는가?
- [ ] RED 단계 확인 후 d{SP}0003_test.md Part C에 상태 `[ ]` 등록 완료인가?

---

## 13. 테스트 파일 구조 & d0003 문서 관리

### 13.1 테스트 코드 파일 구조 원칙

**원칙 1: 기능별 파일 분리** — 1 기능 = 1 TC 파일. 여러 기능을 한 파일에 묶지 않는다.

**원칙 2: SP별 폴더 분리** — `00_doc/sp{N}/` 구조와 동일하게 `tests/sp{N}/`로 분리

```
tests/
├── conftest.py          # 공통 fixture (프로젝트 루트)
├── sp02/                # 02_pycode (oais 모듈 테스트)
│   ├── conftest.py      # SP02 전용 fixture
│   ├── TC001-1.1_*.py
│   └── TC001-1.2_*.py
├── sp05/                # 05_youtube_graphRAG
│   ├── conftest.py
│   └── TC*.py
├── sp06/                # 06_oohwp_skill
├── sp08/                # 08_RRag
│   ├── conftest.py
│   ├── TC*.py
│   └── integration/     # 통합 테스트 (선택)
│       └── test_*.py
└── sp09/                # 09_ooppt
```

**SP별 TC 파일 네이밍**: `TC{Epic}-{Feature}.{Task}_{테스트명}.py`

```
tests/sp08/
├── TC001-1.1_모델초기화.py
├── TC001-1.2_모델로딩실패.py
├── TC002-1.1_RAG파이프라인정상.py
└── TC002-1.2_RAG빈쿼리.py
```

### 13.2 d0003 문서 관리 체계

| 문서 | 위치 | 역할 |
|------|------|------|
| `d0003_test.md` | `00_doc/sp00/` | **대시보드** — 전체 SP 테스트 현황 집계 |
| `d{SP}0003_test.md` | `00_doc/sp{N}/` | **SP별 상세** — 해당 SP 테스트 목록·결과 |

**대시보드(SP00 d0003) 역할**:
- 각 SP의 TC 수·통과율·최종 실행일 집계
- 전체 프로젝트 테스트 상태 한눈에 파악
- SP별 `d{SP}0003` 문서 링크 제공

**SP별 d0003 역할**:
- Part A~E 실제 테스트 항목·결과 기록
- `tests/sp{N}/` 내 TC 파일 목록 현행화
- 코드 파일 경로 직접 참조

### 13.3 d0003 현행화 규칙

d0003은 **항상 실제 `tests/sp{N}/` 폴더와 일치**해야 한다.

| 이벤트 | 현행화 작업 |
|--------|------------|
| TC 파일 추가 | Part C 테이블에 TC ID + 파일 경로 추가 |
| TC 파일 삭제·이동 | Part C 테이블에서 행 제거·수정 |
| 테스트 실행 | 실행 결과 테이블 업데이트 (날짜, PASS/FAIL) |
| 기능 추가/변경 | Part B 시나리오 항목 추가/수정 |
| SP00 대시보드 | SP별 현황 테이블 집계 업데이트 |

**현행화 확인 커맨드:**
```bash
# 실제 TC 파일 목록 (SP08 예시)
find tests/sp08/ -name "TC*.py" | sort

# pytest 수집 확인 (d0003 Part C와 대조)
uv run pytest tests/sp08/ --collect-only -q
```

### 13.4 d0003 표준 템플릿

> SP별 상세 문서: `.claude/skills/ootest/templates/d0003_sp_template.md`
> SP00 대시보드: `.claude/skills/ootest/templates/d0003_dashboard_template.md`

**SP별 문서 구조 (필수 Part):**

```
d{SP}0003_test.md
├── 문서이력관리
├── 개요 (SP 설명, tests/ 경로, 관련 문서)
├── Part A: 에러체크 (항목 테이블 + 실행 결과 테이블)
├── Part B: 시나리오 테스트 (항목 테이블 + 실행 결과 테이블)
├── Part C: 단위 테스트 (TC ID + 파일 경로 테이블 + 실행 결과)
├── Part D: oo 모듈 테스트 (모듈 목록 + 실행 결과)
├── Part E: 런타임 검증 (실행 결과)
└── 관련 문서
```

**SP00 대시보드 구조 (필수 섹션):**

```
d0003_test.md
├── 문서이력관리
├── 1. SP별 테스트 구조 (디렉토리 규칙)
├── 2. SP별 현황 테이블 (집계: TC수/통과율/최종실행일)
├── 3. conftest.py 표준 템플릿
└── SP별 상세 문서 링크
```

### 13.5 d0003 SP별 현황 집계 형식 (대시보드)

SP00 d0003의 현황 테이블 표준 형식:

```markdown
| SP | 폴더 | TC 수 | 통과 | 실패 | 통과율 | 최종 실행일 | 상세 문서 |
|----|------|:----:|:----:|:----:|:------:|------------|----------|
| SP02 | 02_pycode | 18 | 15 | 3 | 83% | 2026-04-01 | [d20003](../sp02/d20003_test.md) |
| SP05 | 05_youtube_graphRAG | 52 | 52 | 0 | 100% | 2026-04-06 | [d50003](../sp05/d50003_test.md) |
| SP08 | 08_RRag | 5 | 4 | 1 | 80% | 2026-04-10 | [d80003](../sp08/d80003_test.md) |
```

---

## 14. checklist 워크플로우 & result 기록 패턴

### 14.1 checklist 워크플로우

```
ootest checklist [domain]
    |
    |-> 1. 문서 로드 (d{SP}0001, d{SP}0002, d{SP}0003)
    |-> 2. 도메인 분석 (키워드 추출, 위험 지표 식별)
    |-> 3. 체크리스트 생성 (00_doc/checklists/[domain].md)
    |-> 4. 리포트 출력
```

**체크리스트 항목 형식:**

```markdown
- [ ] CHK001 - [영역별] 요구사항 품질 질문? [품질차원, Spec N.M]
```

### 14.2 run 실행 후 d0003 자동 갱신 워크플로우

> `ootest result` 서브명령어는 제거됨. `ootest run` 실행 시 자동으로 d0003 갱신.

```
ootest run (또는 run --unit / run [ID] 등)
    ...테스트 실행...
    [자동] d{SP}0003_test.md 갱신:
        1. pytest 결과 파싱
        2. Part C "최종 테스트 결과" 테이블 갱신
           - 결과: ✅ PASS / ❌ FAIL / ⏭ SKIP
           - 실패 원인: pytest 에러 메시지 요약 (첫 줄)
           - 최종 실행일: 오늘 날짜
        3. "최종 결과 요약" 테이블 갱신 (Part별 집계)
        4. 갱신 내용 출력
```

**결과 테이블 형식** (Part C 하단):

```markdown
| TC ID | 기능명 | 결과 | 실패 원인 | 최종 실행일 |
|-------|--------|:----:|----------|:----------:|
| TC002-1.1 | 보건복지부탭 | ✅ PASS | - | 2026-04-06 |
| TC002-1.2 | 환경부탭 | ❌ FAIL | KeyError: 'tab_id' (test_tab.py:42) | 2026-04-06 |
| TC003-2.1 | 데이터수집 | ⏭ SKIP | real_server 마커 — 네트워크 필요 | 2026-04-06 |
```

**요약 테이블 갱신 규칙:**
- PASS: pytest `passed` 카운트
- FAIL: pytest `failed` 카운트 (실패 원인 첫 줄 추출)
- SKIP: `skipped` 카운트 (마커/조건 명시)

### 14.3 TDD RED 반복 루프

```
ootest run [ID]
실행 → 실패 → 원인 분석 → oodev에 수정 요청 → 재실행
→ pass까지 반복 (최대 --max-retries N, 기본 5)
→ pass → d{SP}0003 상태 갱신 → COMPLETE
```

---

## 15. 관련 문서

| 문서 | 용도 |
|------|------|
| d0003_test.md | 공통 테스트 항목 (What) |
| d20003_test.md | plan_srv 테스트 항목 (What) |
| .claude/skills/ootest/SKILL.md | 테스트 실행 스킬 |
| .claude/skills/oodev/SKILL.md | TDD 개발 스킬 |
| .claude/skills/oocheck/SKILL.md | 코드 체크 스킬 |
| d0004_todo.md | 이슈 등록/추적 |
| d0010_history.md | 변경 이력 |

---

## 16. 완료 기준 (Definition of Done) — SKILL.md §5.0.2 상세

> Part C(단위) 통과만으로는 완료가 아니다. 단위 테스트 통과 ≠ 실제 화면 동작.

| 파트 | 통과 필수 | 이유 |
|------|:--------:|------|
| Part C (pytest 단위) | 필수 | 로직 정확성 |
| Part B (E2E/Playwright) | 필수 | 실제 브라우저 화면 동작 검증 |
| Part D (모듈 연동) | 필수 | 모듈 간 통합 오류 감지 |
| Part E (런타임 검증) | 필수 | import 오류·위젯 충돌 등 런타임 에러 감지 |
| Part A (정적 분석) | 필수 | 코드 품질 |
| 성능 체크리스트 | 필수 | 응답시간·부하 기준 충족 (`ootest checklist performance`) |
| 보안 체크리스트 | 필수 | 인증·XSS·SQL인젝션 등 (`ootest checklist security`) |

- E2E 미작성 시: `ootest run` 완료 후 "Part B TC 없음 — E2E 테스트 작성 필요" 경고 출력.
- 모듈 TC 미작성 시: "Part D TC 없음 — `ootest run --module`로 스캔 필요" 경고 출력.
- 실제 웹 동작 ≠ 단위 통과: mock 기반 단위 테스트만으로 기능 완료 선언 금지.
- 조건 미충족 시 처리 원칙: Part B/D/E 실행 전 전제 조건을 먼저 확인. 미충족 시 사용자에게 조건 갖추도록 요청 후 중단. 조건 갖춘 후 재실행해야 완료로 인정.

---

## 17. E2E 전제 조건 미충족 메시지 — SKILL.md §5.3 상세

| 조건 | 미충족 시 안내 메시지 |
|------|--------------------|
| Playwright 설치 | "playwright 미설치. `uv add playwright && playwright install` 실행 후 재시도해주세요." 안내 후 중단 |
| 웹 서버 실행 중 | "앱 서버가 실행되지 않았습니다. `streamlit run app.py` (또는 해당 실행 명령)로 서버를 먼저 실행해주세요." 안내 후 중단 |
| Part B TC 존재 | "E2E TC가 없습니다. `ootest write --e2e`로 먼저 TC를 작성해주세요." 안내 후 중단 |

조건 모두 충족 시: Part B → Playwright → 상태갱신 → 스크린샷(tmp/test_screenshots/) → d{SP}0003 갱신.

---

## 18. 런타임 검증 (Part E) 상세 — SKILL.md §5.5 상세

py_compile/pylint로 감지 불가능한 런타임 에러 검증.

| 에러 유형 | 원인 | Part E 감지 |
|----------|------|:-----------:|
| StreamlitDuplicateElementKey | 위젯 key 중복 | O |
| ImportError (조건부) | if문 내 import | O |
| ImportError (동적 sys.path) | sys.path.insert 후 존재하지 않는 모듈 import | O |
| AttributeError | 런타임 객체 접근 | O |
| TypeError | 런타임 타입 불일치 | O |
| UnboundLocalError (함수 내부 import) | 함수 내 `import module` 이전에 같은 이름 사용 | △ |

> UnboundLocalError 한계: 권한 체크(require_admin 등) 조기 종료로 문제 함수가 실행되지 않으면 import 테스트로 감지 불가.
> → oocheck `함수 내부 import 스코프 오류 감지` 룰로 AST 정적 분석 대체. `oocheck run` 선행 필수.

```bash
ootest run --runtime       # Part E만 실행
uv run pytest tests/test_page_import.py -v
```

### Streamlit 프로젝트 Part E 자동 표준 TC

> `pages/*.py` 가 존재하는 SP에서 `ootest run --runtime` 실행 시,
> `tests/sp{N}/test_page_import.py` 가 없으면 자동 생성 후 실행한다.

- 자동 생성 TC 내용: 모든 `pages/*.py` 파일을 subprocess로 import 시도 → ImportError/ModuleNotFoundError를 FAIL로 기록.
- 목적: 동적 sys.path + 삭제된 모듈 조합으로 pylint가 놓친 import 오류를 런타임에서 반드시 감지.

---

## 19. checklist 검증 차원/도메인 — SKILL.md §5.6 상세

체크리스트는 "요구사항을 위한 유닛테스트" — 구현이 아닌 요구사항 자체의 품질 검증.

검증 차원:

| 차원 | 검증 내용 |
|------|----------|
| 완전성 | 필요한 모든 요구사항이 문서화되었는가? |
| 명확성 | 요구사항이 구체적이고 모호하지 않은가? |
| 일관성 | 요구사항 간 충돌이 없는가? |
| 측정가능성 | 성공 기준이 객관적으로 검증 가능한가? |
| 커버리지 | 모든 흐름/케이스가 정의되었는가? |

도메인별 체크리스트:

| 도메인 | 파일명 | 주요 검증 항목 |
|--------|--------|---------------|
| ux | ux.md | 시각 계층, 상호작용 상태, 접근성 |
| api | api.md | 에러 응답, 인증, 버저닝 |
| performance | performance.md | 성능 지표, 부하 조건 |
| security | security.md | 인증/인가, 데이터 보호, 위협 모델 |

```bash
ootest checklist ux           # UX 요구사항 품질 체크리스트
ootest checklist api          # API 요구사항 품질 체크리스트
ootest checklist security     # 보안 요구사항 품질 체크리스트
ootest checklist              # 대화형으로 도메인 선택
```

---

## 20. --compact 생성 원칙 — SKILL.md §6 상세

> `ootest run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선.

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

---

## 21. 프레임워크 레퍼런스 참조 — SKILL.md §7 상세

> 테스트 작성 시, 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.claude/reference/development/{framework}/` 문서를 참조하여 테스트 구조를 맞춘다.

| 프레임워크 | 감지 조건 | 참조 경로 | 테스트 참조 항목 |
|-----------|----------|----------|----------------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | conftest fixture, TestClient, SFTP 서버, 테스트 분류 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 테스트 |

