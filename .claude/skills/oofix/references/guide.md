# oofix_guide - 코드 오류 자동 개선 가이드

## 문서 이력 관리
- v02 2026-03-29 — Flutter/Dart 지원 추가 — 프로젝트 감지, 분석 도구, 에러 패턴, 수정 전략
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oofix/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oofix는 `d{SP}0004_todo.md`에 등록된 이슈를 서브에이전트 병렬 처리로 자동 수정하는 스킬입니다. 3단계 워크플로우를 통해 안전하고 효율적으로 코드 품질을 개선합니다.

### 1.1 핵심 역할

- **자동 수정**: todo 이슈를 분석하여 자동 수정
- **병렬 처리**: 서브에이전트 활용으로 수정 시간 75분 → 30-35분 단축
- **False Positive 필터**: 불필요한 수정 방지
- **검증 의무화**: py_compile 검증 필수

### 1.2 출력 문서

| 문서 | 역할 | 비고 |
|------|------|------|
| `d{SP}0004_todo.md` | 이슈 업데이트 (상태 변경) | 주 출력 |
| `d{SP}0010_history.md` | 변경 이력 기록 | 부 출력 |

> **병행 처리**: SP≠00일 때 **d0004 AND d{SP}0004** 모두 확인/수정

### 1.3 3단계 워크플로우

| Phase | 역할 | 주체 |
|-------|------|------|
| Phase 1 | 분석 (이슈 파싱, 우선순위, 계획) | 메인 에이전트 |
| Phase 2 | 병렬 수정 (영역별 독립 수정) | 서브에이전트 1~3 |
| Phase 3 | 검증/문서 (검증, todo 업데이트, 이력 기록) | 메인 에이전트 |

## 2. 워크플로우

### 2.1 전체 흐름도

```
┌─────────────────────────────────────────────┐
│ Phase 1: 분석 (메인 에이전트)                │
└─────────────┬───────────────────────────────┘
              │
              ├─► 1. todo 파싱
              │      ├─ d0004_todo.md 읽기 (SP=00)
              │      ├─ d{SP}0004_todo.md 읽기 (SP≠00)
              │      └─ 이슈 목록 추출
              │
              ├─► 2. False Positive 필터
              │      ├─ 오탐 패턴 확인
              │      └─ 실제 에러만 남김
              │
              ├─► 3. 우선순위 정렬
              │      ├─ CRITICAL → ERROR → WARNING
              │      ├─ E0611, E0102 우선
              │      └─ 순차/병렬 구분
              │
              └─► 4. 병렬 계획 수립
                     ├─ 우선 순차: E0611 (export), E0102 (중복)
                     ├─ 병렬 그룹: 영역별 (1~3)
                     └─ Agent 할당
                                                │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ Phase 2: 병렬 수정 (서브에이전트 1~3)        │
└─────────────┬──────────────────────────────┘
              │
              ├─► 우선 순차 처리
              │   ├─ E0611: oo/__init__.py export 추가
              │   └─ E0102: 중복 정의 제거
              │
              └─► 병렬 처리 (Task run_in_background=true)
                  │
                  ├─► Agent 1: 영역 A 수정
                  │      ├─ E0606 (변수 미할당)
                  │      ├─ E1101 (멤버 누락)
                  │      └─ py_compile 검증
                  │
                  ├─► Agent 2: 영역 B 수정
                  │      ├─ E0704 (raise 오류)
                  │      ├─ W0611 (미사용 import)
                  │      └─ py_compile 검증
                  │
                  └─► Agent 3: 영역 C 수정
                         ├─ W0612 (미사용 변수)
                         ├─ 기타 WARNING
                         └─ py_compile 검증
                                                │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ Phase 3: 검증/문서 (메인 에이전트)           │
└─────────────┬──────────────────────────────┘
              │
              ├─► 1. 전체 검증
              │      ├─ py_compile (필수)
              │      ├─ pytest (권장)
              │      └─ 실패 시 롤백
              │
              ├─► 2. d{SP}0004_todo.md 업데이트
              │      ├─ 해결된 이슈: 상태 "해결"
              │      ├─ 미해결: 상세 추가
              │      └─ SP≠00: d0004, d{SP}0004 양쪽 업데이트
              │
              ├─► 3. d{SP}0010_history.md 기록
              │      ├─ 날짜, 태그, 내용
              │      ├─ 수정된 파일 목록
              │      └─ SP≠00: d0010, d{SP}0010 양쪽 기록
              │
              └─► 4. 완료 리포트
                     ├─ 해결: N건
                     ├─ 미해결: M건
                     └─ 처리 시간
```

### 2.2 Phase 1: 분석

```
Phase 1 시작
    │
    ├─► 1. todo 파싱
    │      ├─ SP=00: d0004_todo.md만
    │      ├─ SP≠00: d0004 + d{SP}0004 모두
    │      └─ 이슈 추출
    │         ```markdown
    │         | ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
    │         | T100 | 2026-02-05 | [ERR] | E0611: oo.db export 누락 | 높음 | 대기 |
    │         ```
    │
    ├─► 2. False Positive 필터
    │      ├─ 오탐 패턴 확인 (.claude/guides/debugging_guide.md 참조)
    │      │  ├─ E1101: st.session_state (Streamlit 오탐)
    │      │  ├─ E1101: pd.DataFrame (Pandas 오탐)
    │      │  └─ W0621: 함수 파라미터 (일반 패턴)
    │      └─ 필터링 결과: 12건 → 9건 (3건 오탐 제외)
    │
    ├─► 3. 우선순위 정렬
    │      ├─ CRITICAL (즉시)
    │      ├─ ERROR (24h)
    │      └─ WARNING (1주)
    │
    ├─► 4. 순차/병렬 구분
    │      ├─ 우선 순차:
    │      │  ├─ E0611: oo/__init__.py export (전역 영향)
    │      │  └─ E0102: 중복 정의 (파일 내 충돌)
    │      │
    │      └─ 병렬 가능:
    │         ├─ E0606, E1101, E0704 (파일별 독립)
    │         └─ W0611, W0612 (영향 범위 작음)
    │
    └─► 5. Agent 할당
           ├─ Agent 1: oo/db.py, oo/user.py (영역 A)
           ├─ Agent 2: src/policy/*.py (영역 B)
           └─ Agent 3: pages/*.py (영역 C)
```

**병렬화 기준**:

| 병렬화 | 이슈 | 이유 |
|--------|------|------|
| 낮음 | E0611 (export), E0102 (중복) | 전역 영향, 순차 필수 |
| 높음 | E0606, E1101, E0704, W0612 | 파일별 독립, 동시 수정 가능 |

### 2.3 Phase 2: 병렬 수정

```
Phase 2 시작
    │
    ├─► 우선 순차 처리
    │   │
    │   ├─► E0611: oo/__init__.py export 추가
    │   │      ```python
    │   │      # oo/__init__.py
    │   │      from oo.db import get_db_connection  # 추가
    │   │      from oo.user import get_user_info    # 추가
    │   │      ```
    │   │      └─ py_compile 검증 ✓
    │   │
    │   └─► E0102: 중복 정의 제거
    │          ```python
    │          # oo/utils.py:120 (중복)
    │          # def format_date():  # 삭제 (이미 50라인에 정의)
    │          ```
    │          └─ py_compile 검증 ✓
    │
    └─► 병렬 처리 시작
           │
           ├─► Agent 1 (영역 A: oo/)
           │      Task(
           │        subagent_type="task-executor",
           │        prompt="oo/db.py, oo/user.py 수정
           │        - E0606: 변수 초기화
           │        - E1101: 올바른 멤버명",
           │        run_in_background=true
           │      )
           │      ├─ E0606 수정: result = None (초기화)
           │      ├─ E1101 수정: df.columns → df.columns.tolist()
           │      └─ py_compile 검증 ✓
           │
           ├─► Agent 2 (영역 B: src/policy/)
           │      Task(
           │        subagent_type="task-executor",
           │        prompt="src/policy/*.py 수정
           │        - E0704: raise 블록 이동
           │        - W0611: 미사용 import 삭제",
           │        run_in_background=true
           │      )
           │      ├─ E0704 수정: raise → except 블록 내로
           │      ├─ W0611 수정: import 삭제
           │      └─ py_compile 검증 ✓
           │
           └─► Agent 3 (영역 C: pages/)
                  Task(
                    subagent_type="task-executor",
                    prompt="pages/*.py 수정
                    - W0612: 미사용 변수 삭제",
                    run_in_background=true
                  )
                  ├─ W0612 수정: 변수 삭제 또는 _prefix
                  └─ py_compile 검증 ✓

    ← 병렬 대기 (3개 Agent 완료 시까지)
```

**처리 시간 비교**:

| 구분 | 순차 | 병렬 |
|------|------|------|
| Phase 1 | 5분 | 5분 |
| Phase 2 | 60분+ | **15-20분** |
| Phase 3 | 10분 | 10분 |
| **총계** | 75분+ | **30-35분** |

### 2.4 Phase 3: 검증/문서

```
Phase 3 시작 (Agent 1~3 완료 후)
    │
    ├─► 1. 전체 검증
    │      ├─ py_compile (필수)
    │      │  ```bash
    │      │  uv run python -m py_compile oo/*.py
    │      │  uv run python -m py_compile src/**/*.py
    │      │  uv run python -m py_compile pages/*.py
    │      │  ```
    │      │  └─ 모두 통과 ✓
    │      │
    │      ├─ pytest (권장)
    │      │  ```bash
    │      │  uv run pytest tests/ -v
    │      │  ```
    │      │  └─ 통과 ✓
    │      │
    │      └─ 실패 시 롤백
    │
    ├─► 2. d{SP}0004_todo.md 업데이트
    │      ```markdown
    │      # 해결된 이슈
    │      | ID | 발생일 | 분류 | 내용 | 해결일 | 해결방법 |
    │      | T100 | 2026-02-05 | [ERR] | E0611: oo.db export | 2026-02-05 | __init__.py import 추가 |
    │      | T101 | 2026-02-05 | [ERR] | E0102: 중복 정의 | 2026-02-05 | 120라인 중복 삭제 |
    │      ```
    │      └─ SP≠00: d0004, d{SP}0004 양쪽 업데이트
    │
    ├─► 3. d{SP}0010_history.md 기록
    │      ```markdown
    │      ### [2026-02-05] [BUGFIX] oo 모듈 에러 9건 수정
    │
    │      **수정 내용**:
    │      - E0611: oo/__init__.py export 추가 (2건)
    │      - E0102: oo/utils.py 중복 정의 제거 (1건)
    │      - E0606: 변수 초기화 (3건)
    │      - W0612: 미사용 변수 삭제 (3건)
    │
    │      **수정 파일**:
    │      - oo/__init__.py
    │      - oo/db.py
    │      - oo/user.py
    │      - oo/utils.py
    │      - src/policy/query.py
    │      - pages/7_72_앱_시니어복지.py
    │      ```
    │      └─ SP≠00: d0010, d{SP}0010 양쪽 기록
    │
    └─► 4. 완료 리포트
           ```
           === oofix 완료 ===
           해결: 9건
           미해결: 0건
           처리 시간: 32분
           ```
```

## 3. 상세 사용법

### 3.1 서브명령어

#### 3.1.1 oofix status

서브명령어 리스트 및 이슈 상태

```bash
oofix status
```

**출력 예시**:
```
=== oofix 서브명령어 ===
- run: 이슈 자동 수정 (병렬)
- run [대상]: 특정 이슈/파일/카테고리
- preview: 수정 미리보기
- test: 테스트 실행
- verify: 수정 검증
- rollback: 롤백
- version: v01

=== 이슈 상태 ===
- 전체: 12건
- 대기: 9건 (CRITICAL: 1, ERROR: 5, WARNING: 3)
- 해결: 3건
- False Positive: 3건
```

#### 3.1.2 oofix run

전체 이슈 자동 수정

```bash
oofix run                               # 전체
oofix run --sp 02                       # 서브프로젝트 02
oofix run --interactive                 # 단계별 확인
oofix run --sequential                  # 순차 처리 (병렬 X)
```

#### 3.1.3 oofix run [대상]

특정 이슈/파일/카테고리 수정

```bash
oofix run T100                          # 특정 이슈
oofix run E0611                         # 에러 코드별
oofix run oo/                         # 디렉토리별
oofix run [CRITICAL]                    # 분류별
```

#### 3.1.4 oofix preview

수정 미리보기 (실제 수정 없음)

```bash
oofix preview
```

**출력 예시**:
```
=== 수정 미리보기 ===

[T100] E0611: oo.db export 누락
파일: oo/__init__.py
변경:
  + from oo.db import get_db_connection

[T101] E0102: 중복 정의
파일: oo/utils.py:120
변경:
  - def format_date():  # 삭제 (50라인에 이미 정의)

...

총 9건 수정 예정
승인하시겠습니까? (y/n):
```

#### 3.1.5 oofix test

테스트 실행 (수정 없이 검증만)

```bash
oofix test
```

#### 3.1.6 oofix verify

수정 검증 (수정 후 실행)

```bash
oofix verify
```

#### 3.1.7 oofix rollback

수정 롤백

```bash
oofix rollback
oofix rollback T100                     # 특정 이슈만
```

### 3.2 옵션

| 옵션 | 설명 |
|------|------|
| `--interactive` | 단계별 확인 (각 수정 전 승인) |
| `--force` | 강제 실행 (확인 생략) |
| `--no-history` | 이력 기록 생략 |
| `--sequential` | 순차 처리 (병렬 X) |
| `--sp N` | 서브프로젝트 번호 |

### 3.3 이슈별 수정 전략

| 코드 | 이슈 | 수정 방법 |
|------|------|----------|
| E0611 | export 누락 | `oo/__init__.py`에 import 추가 |
| E0102 | 중복 정의 | 첫 번째 정의만 유지, 나머지 삭제 |
| E0606 | 변수 미할당 | 초기화 또는 로직 수정 |
| E1101 | 멤버 누락 | 올바른 멤버명으로 수정 |
| E0704 | raise 오류 | except 블록 내로 이동 |
| W0611 | 미사용 import | 삭제 |
| W0612 | 미사용 변수 | 삭제 또는 `_` prefix |

### 3.4 False Positive 필터링

**오탐 패턴** (`.claude/guides/debugging_guide.md` 섹션 4):

| 에러 코드 | 패턴 | 이유 |
|----------|------|------|
| E1101 | `st.session_state.xxx` | Streamlit 동적 속성 |
| E1101 | `pd.DataFrame.xxx` | Pandas 메서드 |
| W0621 | 함수 파라미터 | 일반적인 파라미터명 (df, conn) |
| E0401 | `from oo import xxx` | oo 모듈 정상 |

**필터링 예시**:

```bash
# 원본 이슈: 12건
# E1101: st.session_state.user_id (오탐) ← 필터
# E1101: st.session_state.company (오탐) ← 필터
# E1101: pd.DataFrame.columns (오탐) ← 필터

# 필터 후: 9건 (실제 에러만)
```

### 3.5 완료 조건

| 조건 | 검증 방법 |
|------|----------|
| 이슈 해결 | **d0004 AND d{SP}0004** "현재 이슈" 비움 (SP≠00) |
| 구문 정상 | py_compile 통과 |
| 테스트 통과 | pytest 성공 |
| 문서 기록 | **d0010 AND d{SP}0010** history (SP≠00) |

## 4. 사용 예시

### 4.1 전체 이슈 자동 수정

**시나리오**: oocheck 후 발견된 9건 이슈 일괄 수정

```bash
# 1. 이슈 확인
oocheck
# → d0004_todo.md에 9건 등록

# 2. 수정 미리보기
oofix preview

# === 수정 미리보기 ===
# [T100] E0611: oo.db export
# [T101] E0102: 중복 정의
# ...
# 총 9건 수정 예정

# 3. 자동 수정 실행
oofix run

# === Phase 1: 분석 ===
# False Positive 필터: 12건 → 9건
# 우선순위 정렬: E0611(2), E0102(1), E0606(3), W0612(3)
# 병렬 계획: Agent 1~3 할당

# === Phase 2: 병렬 수정 ===
# Agent 1: oo/ 수정 중...
# Agent 2: src/policy/ 수정 중...
# Agent 3: pages/ 수정 중...
# (병렬 대기 20분)

# === Phase 3: 검증/문서 ===
# py_compile: 전체 통과 ✓
# pytest: 전체 통과 ✓
# d0004_todo.md 업데이트 ✓
# d0010_history.md 기록 ✓

# === 완료 ===
# 해결: 9건
# 처리 시간: 32분
```

### 4.2 특정 이슈만 수정

**시나리오**: E0611 export 누락만 수정

```bash
oofix run E0611

# === Phase 1: 분석 ===
# E0611 이슈: 2건
#   - T100: oo.db export
#   - T103: oo.user export

# === Phase 2: 수정 ===
# oo/__init__.py에 import 추가
#   + from oo.db import get_db_connection
#   + from oo.user import get_user_info

# === Phase 3: 검증 ===
# py_compile: 통과 ✓

# === 완료 ===
# 해결: 2건
```

### 4.3 인터랙티브 모드

**시나리오**: 단계별 확인하며 수정

```bash
oofix run --interactive

# === T100: E0611 oo.db export ===
# 수정 계획:
#   파일: oo/__init__.py
#   변경: + from oo.db import get_db_connection
# 승인하시겠습니까? (y/n/s=skip): y

# 수정 완료 ✓

# === T101: E0102 중복 정의 ===
# 수정 계획:
#   파일: oo/utils.py:120
#   변경: - def format_date(): (삭제)
# 승인하시겠습니까? (y/n/s): y

# ...
```

### 4.4 롤백 시나리오

**시나리오**: 수정 후 문제 발견, 롤백

```bash
# 1. 수정 실행
oofix run

# === 완료 ===
# 해결: 9건

# 2. 문제 발견 (예: 테스트 실패)
uv run pytest tests/
# FAILED: tests/test_db.py

# 3. 롤백
oofix rollback

# === 롤백 완료 ===
# 원본 복원: 9개 파일
# d0004_todo.md 복원
# d0010_history.md 롤백 기록

# 4. 재확인
cat 00_doc/sp00/d0004_todo.md
# → 9건 이슈 다시 "대기" 상태
```

### 4.5 서브프로젝트 수정 (병행 처리)

**시나리오**: SP=02 이슈 수정 시 병행 업데이트

```bash
# 1. 컨텍스트 설정
oocontext 02

# 2. 수정 실행
oofix run

# === Phase 1: 분석 ===
# d0004_todo.md: 3건 (공통)
# d20004_todo.md: 3건 (SP=02)

# === Phase 2~3: 수정 및 검증 ===
# ...

# === Phase 3: 문서 업데이트 (병행) ===
# d0004_todo.md 업데이트 ✓ (공통)
# d20004_todo.md 업데이트 ✓ (SP=02)
# d0010_history.md 기록 ✓ (공통)
# d20010_history.md 기록 ✓ (SP=02)

# === 완료 ===
# 해결: 3건 (양쪽 문서 모두 업데이트됨)
```

## 5. Flutter/Dart 지원

### 5.1 프로젝트 자동 감지

oofix는 SP 디렉토리 내 파일 구성으로 프로젝트 유형을 자동 감지합니다.

| 감지 기준 | 프로젝트 유형 |
|----------|-------------|
| `pubspec.yaml` 존재 | Flutter/Dart |
| `pyproject.toml` 또는 `*.py` 존재 | Python |
| 둘 다 존재 | SP 컨텍스트 기준 판단 |

### 5.2 Dart 분석 도구

| 도구 | 용도 | 명령어 |
|------|------|--------|
| `dart analyze` | 정적 분석 (error/warning/info) | `dart analyze lib/` |
| `dart fix --apply` | 자동 수정 가능 이슈 일괄 적용 | `dart fix --apply` |
| `dart format` | 코드 포맷팅 검증 | `dart format --set-exit-if-changed lib/` |
| `flutter test` | 테스트 실행 | `flutter test` |
| `flutter analyze` | Flutter 전용 분석 | `flutter analyze` |

### 5.3 Dart 에러 심각도 매핑

`dart analyze` 출력을 oofix 심각도로 매핑:

| dart analyze 심각도 | oofix 심각도 | 처리 우선순위 |
|-------------------|------------|-------------|
| error | CRITICAL/ERROR | 즉시 |
| warning | WARNING | 24h |
| info | INFO | 1주 |

### 5.4 Dart False Positive 패턴

| 파일 패턴 | 이유 | 처리 |
|----------|------|------|
| `*.g.dart` | build_runner 코드 생성 파일 | 무시 |
| `*.freezed.dart` | Freezed 코드 생성 파일 | 무시 |
| `firebase_options.dart` | Firebase CLI 자동 생성 | 무시 |
| `*.mocks.dart` | Mockito 생성 파일 | 무시 |
| `build/` 디렉토리 | 빌드 아티팩트 | 무시 |

### 5.5 Dart 이슈별 수정 전략

#### 자동 수정 가능 (`dart fix --apply` 대상)

| 이슈 | 수정 방법 |
|------|----------|
| `prefer_const_constructors` | `const` 키워드 추가 |
| `prefer_final_fields` | `final` 키워드 추가 |
| `unnecessary_this` | `this.` 제거 |
| `unnecessary_new` | `new` 키워드 제거 |
| `prefer_is_empty` | `.length == 0` → `.isEmpty` |
| `prefer_is_not_empty` | `.length != 0` → `.isNotEmpty` |

#### 에이전트 수정 필요

| 이슈 | 수정 방법 |
|------|----------|
| `unused_import` | import 문 삭제 |
| `unused_local_variable` | 변수 삭제 또는 `_` prefix |
| `unused_field` | 필드 삭제 또는 `_` prefix |
| `dead_code` | 도달 불가 코드 삭제 |
| `undefined_identifier` | import 추가 또는 선언 |
| `invalid_assignment` | 타입 캐스팅 또는 수정 |
| `missing_return` | return 문 추가 |
| `avoid_print` | `debugPrint()` 또는 logger 전환 |

### 5.6 Flutter 프로젝트 워크플로우 예시

```
# 1. dart analyze로 이슈 확인
dart analyze lib/

# 출력 예시:
#   info - lib/screens/home_page.dart:5:8 - Unused import - unused_import
#   warning - lib/providers/auth_provider.dart:42:5 - Dead code - dead_code
#   error - lib/repository/article/article_repository_impl.dart:15:3 - Missing return - missing_return

# 2. dart fix로 자동 수정 가능 이슈 먼저 처리
dart fix --apply

# 3. 남은 이슈 → oofix 에이전트가 수정
oofix run  # → Phase 1~3 워크플로우 실행

# 4. 검증
dart analyze lib/   # → 0 issues
flutter test        # → All tests passed
```

### 5.7 `dart analyze` 출력 파싱

```
# dart analyze 출력 형식:
#   severity - file:line:column - message - rule_name
# 예:
#   info - lib/main.dart:3:8 - Unused import: 'dart:math'. - unused_import
#   warning - lib/app.dart:15:5 - Dead code. - dead_code
#   error - lib/repo.dart:22:3 - The body might complete normally. - missing_return

# 파싱 정규식:
#   r"^\s*(error|warning|info)\s+-\s+(.+?):(\d+):(\d+)\s+-\s+(.+?)\s+-\s+(\w+)\s*$"
```

## 6. 관련 문서

### 5.1 스킬 및 명령어

| 문서 | 역할 |
|------|------|
| `.claude/skills/oofix/SKILL.md` | 본 스킬 정의 |
| `.claude/skills/oocheck/SKILL.md` | 코드 체크 (선행) |
| `.claude/skills/oolib/SKILL.md` | oo 모듈 수정 |
| `.claude/guides/debugging_guide.md` | 디버깅 가이드 (False Positive) |
| `.claude/commands/sc/improve.md` | 코드 개선 명령어 |
| `.claude/commands/sc/cleanup.md` | 정리 명령어 |
| `.claude/commands/sc/troubleshoot.md` | 트러블슈팅 명령어 |

### 5.2 핵심 문서

| 문서 | 역할 |
|------|------|
| `00_doc/sp00/d0004_todo.md` | 공통 이슈 (입력) |
| `00_doc/d{SP}0004_todo.md` | 서브프로젝트 이슈 (입력) |
| `00_doc/sp00/d0010_history.md` | 공통 이력 (출력) |
| `00_doc/d{SP}0010_history.md` | 서브프로젝트 이력 (출력) |

### 5.3 공통 가이드

| 문서 | 역할 |
|------|------|
| `.claude/guides/common_guide.md` | 프로젝트 공통 개발 표준 |
| `.claude/guides/debugging_guide.md` | 디버깅 방법론 (False Positive 패턴) |
