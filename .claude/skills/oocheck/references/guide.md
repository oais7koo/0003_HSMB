# oocheck_guide - 코드 품질 체크 가이드

## 문서 이력 관리
- v03 2026-04-02 — GSD 연계 추가
- v02 2026-03-29 — Flutter/Dart 지원 추가 — 프로젝트 감지, dart analyze 워크플로우, 체크 대상/제외 패턴
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oocheck/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oocheck는 코드 품질, 에러, 보안, 성능을 검증하는 스킬입니다. 정적 분석과 런타임 검증을 모두 수행하여 코드베이스의 건강성을 유지합니다.

### 1.1 핵심 역할

- **정적 분석**: py_compile, pylint, mypy로 구문/품질/타입 검증
- **런타임 검증**: import 테스트로 DuplicateKey 등 런타임 에러 감지
- **oo 모듈 검증**: oo 모듈 올바른 사용 확인
- **표준용어 검증**: 용어집 기준 명명 일관성
- **순환 참조 감지**: 모듈 간 의존성 분석

### 1.2 출력 문서

| 문서 | 역할 | 비고 |
|------|------|------|
| `d0004_todo.md` | 공통 이슈 등록 | 항상 |
| `d{SP}0004_todo.md` | 서브프로젝트 이슈 등록 | SP≠00일 때 병행 |

> **병행 등록 규칙**: SP≠00일 때 **d0004 AND d{SP}0004** 양쪽 모두 등록

### 1.3 에러 분류

| 분류 | 설명 | 우선순위 | 대응 시간 |
|------|------|----------|----------|
| [CRITICAL] | 시스템 장애, 보안 취약점 | P0 | 즉시 |
| [ERROR] | 기능 오작동, 예외 미처리 | P1 | 24시간 |
| [WARNING] | 잠재적 문제, 성능 이슈 | P2 | 1주일 |
| [INFO] | 코드 스타일, 개선 권장 | P3 | 백로그 |

## 2. 워크플로우

### 2.1 전체 흐름도

```
┌─────────────────────────────────────────────┐
│ 1. oocheck 실행                            │
│    - 체크 대상 선택                          │
│    - 병렬 처리 계획                          │
└─────────────┬───────────────────────────────┘
              │
              ├── 정적 분석 (필수) ────────────┐
              │   (병렬 실행)                   │
              │                                 │
              │   ├─► py_compile (필수)         │
              │   │     └─ 모든 *.py 구문 검증  │
              │   │                             │
              │   ├─► pylint                    │
              │   │     └─ 코드 품질/PEP8       │
              │   │                             │
              │   └─► mypy                      │
              │         └─ 타입 힌트 검증       │
              │                                 │
              ├── 런타임 검증 (필수) ──────────┤
              │   └─► test_page_import.py       │
              │         ├─ import 테스트        │
              │         ├─ DuplicateKey 감지    │
              │         └─ 런타임 초기화 에러   │
              │                                 │
              ├── oo 모듈 검증 ──────────────┤
              │   └─► oo.module.function()    │
              │         형식 확인                │
              │                                 │
              ├── 표준용어 검증 ───────────────┤
              │   └─► 용어집 기준 네이밍       │
              │                                 │
              └── 순환 참조 감지 ──────────────┤
                  └─► 모듈 간 의존성 분석      │
                                                │
              ┌───────────────────────────────┘
              │
┌─────────────▼──────────────────────────────┐
│ 2. 에러 수집 및 분류                        │
│    - CRITICAL / ERROR / WARNING / INFO     │
│    - False Positive 필터링                  │
│    - 우선순위 판단                          │
└─────────────┬──────────────────────────────┘
              │
┌─────────────▼──────────────────────────────┐
│ 3. 결과 기록                                │
│    - 터미널 출력 (요약 + 상세)              │
│    - d0004_todo.md 등록 (공통)              │
│    - d{SP}0004_todo.md 등록 (SP≠00 병행)    │
└─────────────────────────────────────────────┘
```

### 2.2 정적 분석 워크플로우

```
정적 분석 시작
    │
    ├─► 1. 체크 대상 파일 수집
    │      ├─ 포함: src/, oo/, tests/, 04_app/, *.py
    │      └─ 제외: data/, tmp/, db/, .git/, __pycache__/
    │
    ├─► 2. py_compile (필수, 병렬)
    │      ```bash
    │      uv run python -m py_compile <file.py>
    │      ```
    │      ├─ 모든 *.py 구문 검증
    │      ├─ SyntaxError 감지
    │      └─ CRITICAL: 구문 오류
    │
    ├─► 3. pylint (병렬)
    │      ```bash
    │      uv run pylint <file.py>
    │      ```
    │      ├─ PEP8 스타일 검증
    │      ├─ 코드 품질 (복잡도, 중복)
    │      ├─ E0XXX: ERROR
    │      ├─ W0XXX: WARNING
    │      └─ C/R: INFO
    │
    ├─► 4. mypy (병렬)
    │      ```bash
    │      uv run mypy <file.py>
    │      ```
    │      ├─ 타입 힌트 검증
    │      ├─ 타입 불일치 감지
    │      └─ WARNING: 타입 에러
    │
    └─► 5. 에러 수집
           └─ 분류별로 그룹화
```

**체크 대상 패턴**:

| 패턴 | 설명 |
|------|------|
| `src/**/*.py` | 소스 코드 |
| `oo/**/*.py` | oo 모듈 |
| `tests/**/*.py` | 테스트 코드 |
| `04_app/**/*.py` | 앱 코드 (있는 경우) |
| `*.py` (루트) | 루트 Python 스크립트 |

**체크 제외 패턴**:

| 패턴 | 이유 |
|------|------|
| `data/`, `tmp/` | 임시/데이터 파일 |
| `db/` | 데이터베이스 파일 |
| `.git/`, `__pycache__/` | 버전 관리/캐시 |
| `node_modules/` | Node.js 의존성 |

### 2.3 런타임 검증 워크플로우

```
런타임 검증 시작 (oocheck runtime)
    │
    ├─► 1. test_page_import.py 확인
    │      ├─ 파일 존재: tests/test_page_import.py
    │      └─ 없으면 템플릿에서 생성
    │
    ├─► 2. import 테스트 실행
    │      ```bash
    │      uv run pytest tests/test_page_import.py -v
    │      ```
    │      ├─ pages/*.py 전체 import
    │      ├─ Streamlit 모킹
    │      └─ DB 연결 모킹
    │
    ├─► 3. 런타임 에러 감지
    │      ├─ DuplicateElementKey (Streamlit)
    │      ├─ ImportError (조건부 import)
    │      ├─ AttributeError (런타임 객체)
    │      └─ TypeError (런타임 타입)
    │
    ├─► 4. 에러 상세 분석
    │      ├─ 파일명: pages/7_72_앱_시니어복지.py
    │      ├─ 라인: 45
    │      ├─ 에러: DuplicateElementKey: Duplicate key 'btn'
    │      └─ 우선순위: CRITICAL (앱 실행 불가)
    │
    └─► 5. 결과 기록
           └─ d{SP}0004_todo.md 등록
```

**런타임 에러 유형**:

| 에러 유형 | 원인 | py_compile | pylint | pytest import |
|----------|------|:----------:|:------:|:-------------:|
| StreamlitDuplicateElementKey | 위젯 key 중복 | ❌ | ❌ | ✅ |
| ImportError (조건부) | if문 내 import | ❌ | ❌ | ✅ |
| AttributeError | 런타임 객체 접근 | ❌ | ❌ | ✅ |
| TypeError | 런타임 타입 불일치 | ❌ | ❌ | ✅ |

> **중요**: py_compile/pylint로 감지 불가능한 에러를 잡기 위해 런타임 검증 필수

### 2.4 oo 모듈 검증 워크플로우

```
oo 모듈 검증 (oocheck oo)
    │
    ├─► 1. oo 호출 패턴 검색
    │      ```bash
    │      Grep: "from oo" in src/, pages/
    │      ```
    │
    ├─► 2. 올바른 형식 확인
    │      ├─ ✅ 올바른: oo.date_utils.get_date_range()
    │      ├─ ❌ 잘못된: oo.get_date_range()
    │      └─ ❌ 잘못된: from oo import get_date_range
    │
    ├─► 3. 모듈 존재 여부
    │      └─ oo/{module}.py 파일 확인
    │
    └─► 4. 에러 기록
           ├─ [ERROR] oo 모듈 잘못된 호출
           └─ d0004_todo.md 등록
```

**올바른 oo 모듈 사용**:

```python
# ✅ 올바른 예
import oo.date_utils
result = oo.date_utils.get_date_range(start, end)

from oo.date_utils import get_date_range
result = get_date_range(start, end)

# ❌ 잘못된 예
import oo
result = oo.get_date_range(start, end)  # 모듈명 누락

from oo import get_date_range  # 모듈명 누락
```

### 2.5 표준용어 검증 워크플로우

```
표준용어 검증 (oocheck term)
    │
    ├─► 1. 용어집 로드
    │      └─ .claude/skills/oocheck/templates/oocheck_standard_word.md
    │
    ├─► 2. DB 테이블/컬럼명 검증
    │      ├─ PRAGMA table_info(테이블명)
    │      ├─ 용어집과 비교
    │      └─ 불일치 항목 추출
    │
    ├─► 3. 코드 변수명 검증
    │      ├─ Grep: 변수명 패턴
    │      ├─ 용어집과 비교
    │      └─ 불일치 항목 추출
    │
    ├─► 4. 불일치 유형 분류
    │      ├─ 용어 미등록: agent (용어집에 없음)
    │      ├─ 표기 불일치: company vs corp
    │      ├─ 영문/한글 혼용: user_업체
    │      └─ 약어 미정의: biz_no
    │
    └─► 5. 권장 용어 제시
           └─ d0004_todo.md 등록
```

**권장 용어 (예시)**:

| 한글 | 권장 영문 | 비권장 |
|------|----------|--------|
| 업체 | company | corp, firm |
| 사용자 | user | member |
| 사업자번호 | business_number | biz_no |
| 대리인 | agent | proxy |
| 고객 | customer | client |

### 2.6 순환 참조 감지 워크플로우

```
순환 참조 감지 (oocheck circular [모듈])
    │
    ├─► 1. 모듈 의존성 분석
    │      ├─ Grep: "import", "from ... import"
    │      └─ 의존성 그래프 생성
    │
    ├─► 2. 순환 참조 탐지
    │      ├─ DFS (Depth-First Search)
    │      └─ 순환 경로 식별
    │
    ├─► 3. 순환 유형 분류
    │      ├─ __init__.py 포함: CRITICAL
    │      ├─ 직접 순환 (A↔B): ERROR
    │      └─ 간접 순환 (A→B→C→A): WARNING
    │
    ├─► 4. 해결 방안 제시
    │      ├─ 함수 내부 import
    │      ├─ TYPE_CHECKING 활용
    │      └─ 의존성 역전
    │
    └─► 5. 에러 기록
           └─ d0004_todo.md 등록
```

**순환 참조 해결 방법**:

```python
# ❌ 순환 참조 (A ↔ B)

# module_a.py
from module_b import func_b
def func_a():
    return func_b()

# module_b.py
from module_a import func_a
def func_b():
    return func_a()

# ✅ 해결 방법 1: 함수 내부 import

# module_a.py
def func_a():
    from module_b import func_b
    return func_b()

# module_b.py
def func_b():
    from module_a import func_a
    return func_a()

# ✅ 해결 방법 2: TYPE_CHECKING

# module_a.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module_b import func_b

def func_a() -> 'func_b':
    from module_b import func_b
    return func_b()
```

### 2.7 oocheck run dXXXX (상세 문서 기반 체크)

> oofeature 상세개발 또는 상세검증 단계에서 해당 기능 코드만 집중 체크할 때 사용.
> **자동 단계전환**: 상세개발 단계 → 상세검증으로 자동 전환 후 실행.

```
oocheck run d41001
    ↓
[단계 감지]
  상세기획/설계 단계 → ❌ 차단: "개발 미완료. `oodev run dXXXX` 먼저 실행하세요"
  상세개발 단계     → ✅ 파일명 rename (개발→검증) 후 계속
  상세검증 단계     → ✅ 계속 (이미 검증 단계)
    ↓
1. 상세 문서 탐색: 00_doc/sp{N}/d41001_상세*.md 검색
    ↓
2. 문서에서 관련 코드 파일 추출
   - "## 8. 구현 노트" 섹션의 파일 경로
   - 문서 내 코드 블록의 파일명 패턴 (예: `src/crawler.py`, `lib/xxx.dart`)
   - 문서번호와 동일한 패턴의 파일명 (예: d41001_*.py)
   - 추출 불가 시: Explore(haiku)로 관련 파일 탐색
    ↓
3. 해당 파일만 대상으로 품질 체크 실행
   Python: py_compile → pylint → mypy (해당 파일만)
   Flutter: dart analyze (해당 파일만)
    ↓
4. 결과 → d{SP}0004_todo.md 등록
5. 이슈 있음: `oofix run` 실행 권장 | 이슈 없음: ✅ 검증 완료
```

**출력 형식**:
```
[oocheck run d41001] 상세 문서 기반 체크

대상 문서: d41001_상세개발_데이터수집소스.md
체크 대상 파일: src/crawler.py, src/source_manager.py (2개)

결과:
  src/crawler.py — PASS (경고 0건)
  src/source_manager.py — WARNING 1건
    W001 [WARNING] line 45: unused variable 'result'

→ d40004_todo.md에 W001 등록
→ 검증 통과 후 `oofeature next d41001` 실행 권장
```

### 2.8 Import 가용성 체크

각 `.py` 파일의 import 문을 파싱 후 uv 환경에서 실제 가용 여부 확인.

```bash
# 파일에서 import 추출 후 검증
uv run python -c "
import ast, sys
with open('FILE.py') as f:
    tree = ast.parse(f.read())
mods = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            mods.add(alias.name.split('.')[0])
    elif isinstance(node, ast.ImportFrom) and node.module:
        mods.add(node.module.split('.')[0])
failed = []
for m in sorted(mods):
    try:
        __import__(m)
    except ImportError:
        failed.append(m)
if failed:
    print('MISSING:', failed)
    sys.exit(1)
"
```

**분류**: [ERROR] ModuleNotFoundError - 미설치 모듈 import
**주의**: `pythoncom`, `win32api` 등 Windows 전용 모듈은 [WARNING] 플랫폼 의존성으로 추가 분류

## 3. 상세 사용법

### 3.1 서브명령어

#### 3.1.1 oocheck status

서브명령어 리스트 및 체크 현황

```bash
oocheck status
```

**출력 예시**:
```
=== oocheck 서브명령어 ===
- oocheck: 전체 체크
- oocheck [대상]: 특정 파일/디렉토리
- oocheck oo: oo 모듈 검증
- oocheck error: 에러만 체크
- oocheck term: 표준용어 검증
- oocheck debug [에러]: 심층 디버깅
- oocheck circular [모듈]: 순환 참조 감지
- oocheck runtime: 런타임 검증
- version: v02

=== 체크 대상 현황 ===
- 파일 수: 125개 (src: 45, oo: 43, tests: 30, pages: 7)
- 최근 체크: 2026-02-05 10:30
- 이슈: 12건 (CRITICAL: 1, ERROR: 5, WARNING: 6)

=== 최근 이슈 (5건) ===
1. [CRITICAL] SyntaxError: pages/7_72.py:45
2. [ERROR] E0611: oo.db export 누락
3. [ERROR] E0102: 중복 정의 oo/utils.py:120
4. [WARNING] W0612: 미사용 변수 'temp'
5. [WARNING] DuplicateElementKey: pages/7_73.py:33
```

#### 3.1.2 oocheck (전체 체크)

전체 코드베이스 체크

```bash
oocheck                                 # 전체
oocheck --sp 02                         # 서브프로젝트 02
```

#### 3.1.3 oocheck [대상]

특정 파일/디렉토리 체크

```bash
oocheck pages/7_72_앱_시니어복지.py     # 특정 파일
oocheck pages/                          # 디렉토리
oocheck oo/                           # oo 모듈
```

#### 3.1.4 oocheck oo

oo 모듈 호출 검증

```bash
oocheck oo
```

#### 3.1.5 oocheck error

에러만 체크 (WARNING 제외)

```bash
oocheck error
```

#### 3.1.6 oocheck term

표준용어 검증

```bash
oocheck term
```

#### 3.1.7 oocheck debug [에러]

심층 디버깅

```bash
oocheck debug "SyntaxError: invalid syntax"
oocheck debug E0611
```

#### 3.1.8 oocheck circular [모듈]

순환 참조 감지

```bash
oocheck circular                        # 전체
oocheck circular oo.db                # 특정 모듈
```

#### 3.1.9 oocheck runtime

런타임 검증 (import 테스트)

```bash
oocheck runtime
```

### 3.2 병행 등록 규칙 (SP≠00)

**원칙**: SP≠00일 때 에러를 **d0004 AND d{SP}0004** 양쪽에 등록

```bash
# 예시: SP=02 설정 시
oocontext 02
oocheck

# 에러 발견:
# → 00_doc/sp00/d0004_todo.md 에 등록 (공통)
# → 00_doc/sp02/d20004_todo.md 에도 등록 (서브프로젝트)
```

**등록 형식**:

```markdown
# 00_doc/sp00/d0004_todo.md (공통)
| ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
|----|--------|------|------|---------|------|
| T100 | 2026-02-05 | [ERR] | E0611: oo.db export 누락 | 높음 | 대기 |

# 00_doc/sp02/d20004_todo.md (SP=02)
| ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
|----|--------|------|------|---------|------|
| T050 | 2026-02-05 | [ERR] | E0611: oo.db export 누락 (d0004 T100 연동) | 높음 | 대기 |
```

### 3.3 디버깅 체크포인트 (oocheck debug)

| 체크포인트 | 확인 사항 |
|----------|----------|
| 에러 라인 주변 | 전후 5줄 코드 분석 |
| 변수 타입 | 예상 타입 vs 실제 타입 |
| 입력 유효성 | None, 빈 값, 범위 초과 |
| DB 결과 | 쿼리 결과 확인 |
| NULL 처리 | None 체크 누락 |
| 라이브러리 버전 | 호환성 문제 |

**Streamlit 전용 체크포인트**:

| 항목 | 확인 |
|------|------|
| session_state 키 | 초기화 여부, 키 오타 |
| 위젯 key | 중복, 동적 생성 패턴 |
| st.rerun() | 무한 루프 가능성 |
| 컴포넌트 순서 | 조건부 렌더링 시 일관성 |

## 4. 사용 예시

### 4.1 전체 코드베이스 체크

**시나리오**: 커밋 전 전체 코드 검증

```bash
# 1. 전체 체크 실행
oocheck

# === 정적 분석 ===
# py_compile: 125/125 PASS
# pylint: 5 errors, 12 warnings
# mypy: 3 errors

# === 런타임 검증 ===
# test_page_import.py: 1 FAILED
# - pages/7_72_앱_시니어복지.py: DuplicateElementKey

# === 총 이슈: 9건 ===
# CRITICAL: 1
# ERROR: 5
# WARNING: 3

# → d0004_todo.md에 9건 등록

# 2. 이슈 확인
cat 00_doc/sp00/d0004_todo.md

# 3. 수정 후 재검증
oocheck

# === 총 이슈: 0건 ===
# ✓ 전체 통과
```

### 4.2 런타임 에러 감지

**시나리오**: DuplicateKey 에러 발견 및 수정

```bash
# 1. 런타임 검증
oocheck runtime

# FAILED: pages/7_72_앱_시니어복지.py
# DuplicateElementKey: Duplicate key 'btn' at line 45

# 2. 코드 확인
# 라인 45:
# for item in items:
#     st.button("Click", key="btn")  # 중복!

# 3. 수정
# for i, item in enumerate(items):
#     st.button("Click", key=f"btn_{i}")

# 4. 재검증
oocheck runtime
# PASSED ✓
```

### 4.3 oo 모듈 검증

**시나리오**: oo 모듈 잘못된 호출 수정

```bash
# 1. oo 모듈 체크
oocheck oo

# === oo 모듈 검증 ===
# [ERROR] 잘못된 호출: src/policy/query.py:15
#   - 현재: oo.get_date_range()
#   - 권장: oo.date_utils.get_date_range()

# 2. 수정
# import oo  # ❌
# result = oo.get_date_range()

# import oo.date_utils  # ✅
# result = oo.date_utils.get_date_range()

# 3. 재검증
oocheck oo
# ✓ 전체 통과
```

### 4.4 순환 참조 해결

**시나리오**: 모듈 간 순환 참조 발견

```bash
# 1. 순환 참조 감지
oocheck circular

# === 순환 참조 발견 ===
# [ERROR] 직접 순환: oo.db ↔ oo.user
#   - oo/db.py:10: from oo.user import get_user
#   - oo/user.py:5: from oo.db import get_db_connection

# 해결 방안:
#   1. 함수 내부 import
#   2. oo.db에서 get_user 제거

# 2. 수정 (함수 내부 import)
# oo/db.py:
# def check_user_access():
#     from oo.user import get_user  # 함수 내부로 이동
#     ...

# 3. 재검증
oocheck circular
# ✓ 순환 참조 없음
```

### 4.5 서브프로젝트 체크 (병행 등록)

**시나리오**: SP=02 체크 시 병행 등록

```bash
# 1. 컨텍스트 설정
oocontext 02

# 2. 체크 실행
oocheck

# === 이슈 발견: 3건 ===
# T100: [ERR] E0611: oo.db export 누락
# T101: [ERR] E0102: 중복 정의
# T102: [WARNING] W0612: 미사용 변수

# === 병행 등록 ===
# → 00_doc/sp00/d0004_todo.md 등록 (T100, T101, T102)
# → 00_doc/sp02/d20004_todo.md 등록 (T050, T051, T052)

# 3. 양쪽 문서 확인
cat 00_doc/sp00/d0004_todo.md
cat 00_doc/sp02/d20004_todo.md
```

## 5. Flutter/Dart 지원

### 5.1 프로젝트 자동 감지

oocheck는 SP 디렉토리 내 `pubspec.yaml` 존재 여부로 Flutter 프로젝트를 자동 감지합니다.

| 감지 기준 | 프로젝트 유형 | 체크 체인 |
|----------|-------------|----------|
| `pubspec.yaml` 존재 | Flutter/Dart | dart analyze → flutter test |
| `pyproject.toml` 존재 | Python | py_compile → pylint → mypy → pytest |

### 5.2 Flutter 체크 대상/제외

**체크 대상**:

| 패턴 | 설명 |
|------|------|
| `lib/**/*.dart` | 앱 소스 코드 |
| `test/**/*.dart` | 테스트 코드 |

**체크 제외**:

| 패턴 | 이유 |
|------|------|
| `build/` | 빌드 아티팩트 |
| `.dart_tool/` | Dart 도구 캐시 |
| `*.g.dart` | build_runner 생성 파일 |
| `*.freezed.dart` | Freezed 생성 파일 |
| `*.mocks.dart` | Mockito 생성 파일 |
| `firebase_options.dart` | Firebase CLI 생성 |

### 5.3 Flutter 체크 워크플로우

```
Flutter/Dart 체크 (oocheck run, SP=08 등)
    │
    ├─► 1. 프로젝트 감지
    │      └─ pubspec.yaml 존재 → Flutter 모드
    │
    ├─► 2. dart analyze (필수)
    │      ├─ dart analyze lib/
    │      ├─ error/warning/info 분류
    │      └─ False Positive 필터 (*.g.dart 등)
    │
    ├─► 3. dart fix --dry-run (선택)
    │      └─ 자동 수정 가능 이슈 건수 보고
    │
    ├─► 4. flutter test (권장)
    │      └─ 테스트 실행 및 결과
    │
    └─► 5. 결과 기록
           ├─ 터미널 요약 출력
           └─ d{SP}0004_todo.md 등록
```

### 5.4 dart analyze 심각도 매핑

| dart analyze | oocheck 분류 | 대응 시간 |
|-------------|-------------|----------|
| error | CRITICAL/ERROR | 즉시/24h |
| warning | WARNING | 1주 |
| info | INFO | 백로그 |

### 5.5 Flutter 체크 사용 예시

```bash
# SP=08 (Flutter 앱) 컨텍스트에서 체크
oocontext 08
oocheck run

# === Flutter/Dart 프로젝트 감지 ===
# dart analyze lib/
#   error: 8건
#   warning: 4건
#   info: 7건
#   False Positive: 0건
#
# dart fix --dry-run:
#   자동 수정 가능: 3건
#
# flutter test:
#   1 test passed
#
# === Summary ===
#   ERROR: 8건
#   WARNING: 4건
#   INFO: 7건
# → d80004_todo.md에 12건 등록 (INFO 제외)
```

## 5.5 GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 코드 품질 체크 | `oocheck run` | - |
| 페이즈 완료 검증 | `oocheck run` | `/gsd:validate-phase [N]` |
| 작업 완료 확인 | `oocheck run` | `/gsd:verify-work` |
| 디버깅 | `oocheck debug` | `/gsd:debug` |
| 전체 건강 상태 | `ooenv run` | `/gsd:health` |
| 법의학적 버그 추적 | `oocheck debug --trace` | `/gsd:forensics` |

**조합 패턴**:
```
oodev run → oocheck run → /gsd:verify-work (GSD 기준 완료 검증)
```

## 6. 관련 문서

### 6.1 스킬 및 명령어

| 문서 | 역할 |
|------|------|
| `.claude/skills/oocheck/SKILL.md` | 본 스킬 정의 |
| `.claude/skills/oofix/SKILL.md` | 코드 오류 수정 (후행) |
| `.claude/skills/oodev/SKILL.md` | TDD 개발 (REFACTOR 단계) |
| `.claude/guides/debugging_guide.md` | 디버깅 가이드 |
| `.claude/commands/sc/analyze.md` | 분석 명령어 |
| `.claude/commands/sc/test.md` | 테스트 명령어 |
| `.claude/commands/sc/troubleshoot.md` | 트러블슈팅 명령어 |

### 5.2 템플릿

| 파일 | 용도 |
|------|------|
| `.claude/skills/oocheck/templates/oocheck_standard_word.md` | 표준용어집 |
| `.claude/skills/ootest/templates/test_page_import_template.py` | 런타임 검증 템플릿 |

### 5.3 핵심 문서

| 문서 | 역할 |
|------|------|
| `00_doc/sp00/d0004_todo.md` | 공통 이슈 등록 |
| `00_doc/d{SP}0004_todo.md` | 서브프로젝트 이슈 등록 |
| `00_doc/d{SP}0010_history.md` | 변경 이력 |

### 5.4 공통 가이드

| 문서 | 역할 |
|------|------|
| `.claude/guides/common_guide.md` | 프로젝트 공통 개발 표준 |
| `.claude/guides/debugging_guide.md` | 디버깅 방법론 |
