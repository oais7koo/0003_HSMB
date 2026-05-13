# oorun_guide - TDD 기반 자율 실행 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oorun/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oorun은 프로젝트의 **시공자(Builder)** 역할로, `ooplan`이 수립한 실행 계획을 받아 자율적인 TDD 사이클을 수행합니다.

### 1.1 핵심 개념

- **Architect vs Builder**
  - Architect (`ooplan`): 무엇을 어떻게 만들지 결정 (상세 설계)
  - Builder (`oorun`): 실행 큐의 작업을 자율 수행

- **TDD 사이클**: RED → GREEN → REFACTOR 반복
- **자동 검증**: 테스트 통과 및 코드 품질 기준 충족 시까지 반복

### 1.2 입출력

**입력**:
- 실행 큐 (Execution Queue) from `ooplan detail`
- `00_doc/sp00/d0002_plan.md` 참조

**출력**:
- 구현된 소스 코드
- 통과된 테스트 코드
- 업데이트된 문서 (`00_doc/sp00/d0004_todo.md`, `00_doc/sp00/d0010_history.md`)

---

## 2. 워크플로우

### 2.1 전체 흐름

```
실행 큐 확인 (ooplan detail 산출물)
    ↓
태스크 선택 (우선순위/의존성 기반)
    ↓
TDD 사이클 실행 (RED → GREEN → REFACTOR)
    ↓
검증 (테스트 통과, 품질 기준 충족)
    ↓
문서 업데이트 (d0004, d0010)
    ↓
다음 태스크로 이동
```

### 2.2 TDD 사이클 상세

```
┌─────────────────────────────────────────────────────────────┐
│                    TDD 자율 실행 루프                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. RED (테스트 작성)                                       │
│     - 입력: 태스크 요구사항                                  │
│     - 행동: 실패하는 테스트 코드 작성 (pytest)               │
│     - 검증: 테스트가 실패하는지 확인                         │
│                                                             │
│  2. GREEN (구현)                                            │
│     - 입력: 실패하는 테스트                                  │
│     - 행동: 테스트를 통과하는 최소한의 코드 작성             │
│     - 검증: 테스트가 통과하는지 확인                         │
│                                                             │
│  3. REFACTOR (개선)                                         │
│     - 입력: 통과한 코드                                      │
│     - 행동: 중복 제거, 가독성 향상, 주석 추가                │
│     - 검증: 테스트 통과 유지, Lint/Type Check 통과           │
│                                                             │
│  4. COMPLETE (완료 처리)                                    │
│     - 행동: 문서 업데이트, 커밋, 다음 태스크로 이동          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 서브에이전트 활용

| TDD 단계 | 서브에이전트 | 용도 |
|----------|--------------|------|
| 사전 분석 (선택) | `codebase-investigator` | 복잡한 구현 전 의존성/영향 분석 |
| RED | `task-executor` | 실패하는 테스트 코드 작성 |
| GREEN | `task-executor` | 테스트 통과를 위한 최소 구현 |
| REFACTOR | `python-code-reviewer` | 코드 품질 리뷰 및 개선 제안 |
| 검증 | `task-checker` | 태스크 완료 여부 검증 |
| 품질 보증 | `ooqa` | 중복 검사, 의존성 분석 |
| 에스컬레이션 분석 | `codebase-investigator` | TDD 실패 시 근본 원인 분석 |

---

## 3. 상세 사용법

### 3.1 기본 명령어

| 명령어 | 설명 | 사용 시점 |
|--------|------|----------|
| `oorun` | 대기 중인 실행 큐 처리 (기본) | 구현 시작 |
| `oorun execute [ID]` | 특정 태스크 즉시 실행 | 단일 태스크 처리 |
| `oorun all` | 프로젝트 전체 점검 | 유지보수 |
| `oorun status` | 현재 진행 상태 및 큐 확인 | 모니터링 |
| `oorun resume` | 중단된 작업 재개 | 실행 재개 |
| `oorun version` | 스킬 버전 정보 (v02) | 버전 확인 |

### 3.2 실행 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--max-iterations N` | TDD 반복 최대 횟수 | 10 |
| `--timeout M` | 태스크당 최대 시간(분) | 30 |
| `--interactive` | 각 단계마다 사용자 승인 대기 | false |
| `--skip-refactor` | Refactor 단계 건너뛰기 | false |
| `--report` | 실행 리포트 생성 (`tmp/oorun_report.md`) | false |

### 3.3 단계별 성공 기준

#### RED (Clean Fail)
- 테스트 코드가 문법적으로 올바름
- 실행 시 `ImportError` 또는 `AssertionError`로 명확히 실패
- 기존 테스트를 깨뜨리지 않음

#### GREEN (Clean Pass)
- 작성된 테스트가 통과
- 기존 모든 테스트가 여전히 통과 (회귀 없음)

#### REFACTOR (Clean Code)
- `pylint`, `flake8` 검사 통과
- `mypy` 타입 체크 통과
- `.claude/guides/common_guide.md` 코딩 컨벤션 준수

---

## 4. 사용 예시

### 4.1 기본 실행

```bash
# 실행 큐 확인
oorun status

# 대기 중인 태스크 자동 처리
oorun

# 특정 태스크 실행
oorun execute F002-1.1
```

### 4.2 옵션 활용

```bash
# 인터랙티브 모드 (각 단계 확인)
oorun --interactive

# 빠른 프로토타이핑 (Refactor 생략)
oorun --skip-refactor

# 실행 리포트 생성
oorun --report

# 반복 횟수 제한 (5회)
oorun --max-iterations 5
```

### 4.3 프로젝트 전체 점검

```bash
# oocheck + ootest + oolib + oodb 통합 실행
oorun all
```

**실행 순서**:
1. `oocheck`: 정적 분석 및 에러 체크
2. `oofix run`: 발견된 단순 에러 자동 수정
3. `ootest`: 전체 테스트 스위트 실행
4. `oolib`: 모듈 문서 현행화
5. `oodb`: DB 스키마 문서 현행화

### 4.4 병렬 처리

| 조건 | 병렬 실행 방식 | 효과 |
|------|----------------|------|
| 복잡한 태스크 사전 분석 | `codebase-investigator` + `Explore` | 아키텍처 분석과 패턴 탐색 동시 수행 |
| 독립된 태스크 다수 | 여러 `task-executor` 동시 실행 | TDD 사이클 처리 시간 단축 |
| REFACTOR 단계 | `python-code-reviewer` + `ooqa` | 코드 리뷰와 품질 분석 동시 수행 |
| 전체 점검 (all) | 각 스킬별 에이전트 병렬 | 통합 점검 시간 단축 |
| 에스컬레이션 분석 | `codebase-investigator` + `python-code-reviewer` | 근본 원인 분석과 코드 품질 검토 동시 |

### 4.5 에스컬레이션 처리

**자동 에스컬레이션 조건**:
1. 반복 횟수 초과 (10회 이상 시도해도 테스트 통과 실패)
2. 모호한 요구사항 (`ooplan` 정보로 구현 불가)
3. 환경 문제 (패키지 설치 실패, API 연결 불가 등)

**에스컬레이션 시 행동**:
```python
# 심층 분석을 위한 코드베이스 조사
Task(
    subagent_type="codebase-investigator",
    prompt="""
    TDD 실패 근본 원인 분석:

    실패 정보:
    - 태스크: {task_id}
    - 반복 횟수: {iteration_count}
    - 마지막 에러: {last_error}

    분석 항목:
    1. 관련 코드의 의존성 체인 추적
    2. 유사한 구현 패턴 및 성공 사례 탐색
    3. 잠재적 충돌 또는 Side Effect 식별
    4. 구체적 해결 방안 및 우회책 제시

    --depth deep --format markdown --lang ko
    """
)
```

---

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/oorun/SKILL.md` | 스킬 정의 |
| `.claude/skills/ooplan/SKILL.md` | Architect - 상세 설계 및 태스크 공급 |
| `.claude/skills/oocheck/SKILL.md` | 코드 품질 기준 정의 |
| `.claude/skills/ootest/SKILL.md` | 테스트 실행 가이드 |
| `00_doc/sp00/d0002_plan.md` | 전체 구현 계획 |
| `00_doc/sp00/d0004_todo.md` | 이슈 및 완료 처리 |
| `.claude/guides/common_guide.md` | 공통 개발 표준 |
