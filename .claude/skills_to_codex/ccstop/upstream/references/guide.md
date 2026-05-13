# oostop_guide - 세션 종료 워크플로우 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oostop/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

### 1.1 목적

세션 종료 시 작업 내역을 정리하고, 프로젝트 문서를 자동 업데이트하며, 다음 세션 준비를 위한 워크플로우입니다.

### 1.2 주요 기능

- **README.md 갱신**: 최근 작업 내역, 다음 작업 요약
- **00_doc/*.md 동기화**: PRD, TODO, HISTORY 등 핵심 문서 현행화
- **변경 검증**: 코드-문서 일관성 체크
- **커밋 준비**: Git 커밋 가이드라인 제공

### 1.3 실행 시점

- 하루 작업 종료 시
- 중요 기능 완료 시
- 팀원에게 작업 인계 전
- Git 커밋 전

---

## 2. 워크플로우

### 2.1 전체 흐름도

```
세션 종료 트리거
    ↓
1단계: README.md 갱신
    ├─ 최근 작업 내역 요약
    ├─ 변경된 파일 목록
    └─ 다음 작업 항목
    ↓
2단계: 00_doc/*.md 동기화
    ├─ d{SP}0004_todo.md (완료/새 이슈)
    ├─ d{SP}0010_history.md (변경 이력)
    ├─ d{SP}0001_prd.md (기능 추가/변경 시)
    └─ d0005_lib.md (라이브러리 추가 시)
    ↓
사전 체크
    ├─ 문법 오류 없음
    ├─ 테스트 통과
    └─ tmp/ 정리
    ↓
커밋 가이드 출력 (선택)
    ↓
세션 종료 완료
```

### 2.2 단계별 상세

#### 1단계: README.md 갱신

**목적**: 프로젝트 개요 및 최근 작업 현행화

**갱신 항목**:
```markdown
## 최근 작업 내역
- 날짜: 2026-02-05
- 작업: 보건복지부 탭 UI 개선
- 변경: pages/7_74_앱_시니어복지.py, oo/ui.py
- 다음: 고용노동부 탭 데이터 연동
```

**서브에이전트**:
```
[task-executor] README.md 갱신
    ├─ Git 변경 이력 스캔 (git log, git diff)
    ├─ 작업 내역 요약 생성
    └─ README.md 업데이트

[task-checker] 검증 (병렬)
    └─ README.md 형식 확인
```

#### 2단계: 00_doc/*.md 동기화

**목적**: 핵심 문서와 코드 동기화

**동기화 대상**:

| 문서 | 조건 | 갱신 항목 |
|------|------|----------|
| `d{SP}0004_todo.md` | 항상 | 완료된 TODO 상태 변경, 새 이슈 등록 |
| `d{SP}0010_history.md` | 항상 | 변경 이력 추가 (날짜, 타입, 내용) |
| `d{SP}0001_prd.md` | 기능 추가/변경 시 | 구현 상태 업데이트 |
| `d0005_lib.md` | 라이브러리 추가 시 | 의존성 목록 갱신 |
| `d{SP}0003_test.md` | 테스트 추가/변경 시 | 테스트 항목 갱신 |

**서브에이전트**:
```
[Explore] 변경 파일 스캔 (병렬)
    ├─ Git 변경 감지
    ├─ 영향받는 문서 식별
    └─ 변경 내용 추출

[task-executor] 문서 갱신 (병렬)
    ├─ d0004_todo.md 업데이트
    ├─ d0010_history.md 추가
    └─ 조건부 문서 갱신

[ooqa] 품질 검증 (병렬)
    └─ 문서-코드 일관성 체크
```

---

## 3. 상세 사용법

### 3.1 기본 실행 (2단계 전체)

```bash
# README.md + 00_doc/*.md 전체 동기화
oostop run

# 또는 단순히
oostop
```

**결과**:
- README.md 갱신
- 00_doc/*.md 동기화 (d0004, d0010, 조건부 d0001/d0005)
- 체크리스트 출력

### 3.2 1단계만 실행

```bash
# README.md만 갱신
oostop readme
```

**사용 케이스**:
- 간단한 작업 후 빠른 종료
- 00_doc/*.md는 이미 수동 갱신됨
- Git 커밋 없이 세션 종료

### 3.3 2단계만 실행

```bash
# 00_doc/*.md만 동기화 (README.md 제외)
oostop sync
```

**사용 케이스**:
- README.md는 변경 불필요
- 문서만 대량 정리 필요
- 주기적 문서 동기화

### 3.4 상태 확인

```bash
# 현재 상태 및 서브명령어 목록
oostop status
```

**출력**:
```
## oostop 상태

스킬: oostop.md (v01)

### 서브명령어
- oostop status  : 상태 확인
- oostop version : 버전 정보
- oostop run     : 2단계 전체 실행 (기본)
- oostop readme  : 1단계 (README.md만)
- oostop sync    : 2단계 (00_doc/*.md만)

### 갱신 대상
- README.md (최근 작업 내역)
- d0004_todo.md (완료/새 이슈)
- d0010_history.md (변경 이력)
- d0001_prd.md (조건부: 기능 변경 시)
- d0005_lib.md (조건부: 라이브러리 추가 시)
```

---

## 4. 사용 예시

### 4.1 일반 작업 종료

**시나리오**: 보건복지부 탭 UI 개선 완료

```bash
$ oostop run
```

**출력**:
```
=== oostop 세션 종료 워크플로우 ===

[1단계] README.md 갱신 중...
✓ 최근 변경 스캔 (3개 파일)
  - pages/7_74_앱_시니어복지.py
  - oo/ui.py
  - tests/TC002-1.1_보건복지부탭.py

✓ README.md 업데이트
  - 작업: 보건복지부 탭 UI 개선
  - 변경: 3개 파일
  - 다음: 고용노동부 탭 데이터 연동

[2단계] 00_doc/*.md 동기화 중...
✓ d0004_todo.md
  - T050 완료 처리 (보건복지부 탭 UI)

✓ d0010_history.md 추가
  - 2026-02-05: FEATURE - 보건복지부 탭 UI 개선

⚠ d0001_prd.md 업데이트 필요
  → 구현 상태 변경 감지 (F002-1.1 완료)

✓ d0001_prd.md 업데이트
  - F002-1.1 상태: 진행중 → 완료

=== 사전 체크리스트 ===
✓ 문법 오류 없음
✓ 테스트 통과 (TC002-1.1)
✓ tmp/ 정리됨

=== Git 커밋 권장 ===
git add pages/7_74_앱_시니어복지.py oo/ui.py tests/TC002-1.1_보건복지부탭.py
git commit -m "feat: 보건복지부 탭 UI 개선

- UI 레이아웃 변경
- 테스트 추가

Generated with Claude Code"

=== 세션 종료 완료 ===
```

### 4.2 README.md만 갱신

**시나리오**: 간단한 버그 수정, 문서는 수동 갱신됨

```bash
$ oostop readme
```

**출력**:
```
=== oostop README.md 갱신 ===

✓ 최근 변경 스캔 (1개 파일)
  - oo/validation.py

✓ README.md 업데이트
  - 작업: 사업자번호 검증 로직 버그 수정
  - 변경: oo/validation.py
  - 다음: 단위 테스트 추가

완료. 00_doc/*.md 동기화가 필요하면 'oostop sync' 실행.
```

### 4.3 문서만 동기화

**시나리오**: 다수 작업 후 문서 일괄 정리

```bash
$ oostop sync
```

**출력**:
```
=== oostop 문서 동기화 ===

✓ 변경 이력 스캔 (5개 커밋)

✓ d0004_todo.md
  - T050 완료 처리
  - T051 완료 처리
  - T055 신규 등록 ([IMPROVE] 쿼리 최적화)

✓ d0010_history.md 추가
  - 2026-02-05: FEATURE - 보건복지부 탭 완료
  - 2026-02-05: FEATURE - 고용노동부 탭 완료
  - 2026-02-05: BUGFIX - 로그인 세션 타임아웃
  - 2026-02-05: IMPROVE - DB 쿼리 최적화
  - 2026-02-05: REFACTOR - oo/ui.py 중복 제거

✓ d0001_prd.md 업데이트
  - F002-1.1 완료
  - F002-1.2 완료

✓ d0005_lib.md 업데이트 불필요

완료. Git 커밋 필요 시 'oocommit' 실행.
```

---

## 5. 체크리스트

### 5.1 세션 종료 전 확인 사항

**필수**:
- [ ] 문법 오류 없음 (pylint, py_compile)
- [ ] 테스트 통과 (변경된 기능)
- [ ] tmp/ 폴더 정리 (임시 파일 제거)

**권장**:
- [ ] 주요 변경사항 커밋 완료
- [ ] 브랜치 상태 확인 (git status)
- [ ] 작업 중인 파일 저장

### 5.2 README.md 확인 항목

- [ ] 최근 작업 내역 정확성
- [ ] 변경된 파일 목록 완전성
- [ ] 다음 작업 명확성

### 5.3 00_doc/*.md 확인 항목

**d0004_todo.md**:
- [ ] 완료된 TODO 상태 변경
- [ ] 새로 발견된 이슈 등록
- [ ] 우선순위 재조정

**d0010_history.md**:
- [ ] 변경 이력 추가 (날짜, 타입, 내용)
- [ ] 태그 일관성 (FEATURE, BUGFIX 등)

**d0001_prd.md** (조건부):
- [ ] 구현 상태 업데이트
- [ ] 변경된 요구사항 반영

---

## 6. 커밋 가이드라인

### 6.1 커밋 메시지 형식

> **참조**: `.claude/guides/common_guide.md` 섹션 3.2

```
<타입>: <제목> (50자 이내)

<본문> (선택, 72자 줄바꿈)
- 변경 사항 1
- 변경 사항 2

Generated with Claude Code
```

### 6.2 타입 분류

| 타입 | 용도 | 예시 |
|------|------|------|
| `feat` | 새 기능 | feat: 보건복지부 탭 구현 |
| `fix` | 버그 수정 | fix: 로그인 세션 타임아웃 |
| `refactor` | 리팩토링 | refactor: oo/ui.py 중복 제거 |
| `docs` | 문서 변경 | docs: README.md 갱신 |
| `test` | 테스트 추가/수정 | test: TC002-1.1 추가 |
| `chore` | 빌드/설정 | chore: pyproject.toml 업데이트 |

### 6.3 oostop 자동 생성 예시

```bash
# oostop run 실행 후 제안된 커밋 명령
git add pages/7_74_앱_시니어복지.py oo/ui.py
git commit -m "feat: 보건복지부 탭 UI 개선

- 레이아웃 변경
- 모바일 반응형 적용

Generated with Claude Code"
```

---

## 7. 서브에이전트 활용

### 7.1 단계별 에이전트

| 단계 | 에이전트 | 역할 | 병렬 |
|------|----------|------|:----:|
| 1단계 검증 | `task-checker` | README.md 형식 확인 | O |
| 2단계 탐색 | `Explore` | 변경 파일 스캔 | O |
| 2단계 갱신 | `task-executor` | 문서 업데이트 | O |
| 2단계 품질 | `ooqa` | 문서-코드 일관성 | O |

### 7.2 병렬 처리 패턴

**1단계 (README.md)**:
```
[task-executor]       README.md 갱신
        +
[task-checker]        README.md 검증 (병렬)
```

**2단계 (00_doc/*.md)**:
```
[Explore]            변경 파일 스캔
        ↓
[task-executor]      d0004, d0010 갱신
        +
[ooqa]             일관성 체크 (병렬)
```

---

## 8. 관련 문서

### 8.1 스킬 파일

| 문서 | 용도 |
|------|------|
| `.claude/skills/oostop/SKILL.md` | 스킬 정의 |
| `.claude/skills/oostop/scripts/oostop_run.py` | 실행 스크립트 (해당 시) |

### 8.2 연관 스킬

| 스킬 | 연동 시점 |
|------|----------|
| `oostart` | 세션 시작 (반대 워크플로우) |
| `oocommit` | Git 커밋 (종료 후) |
| `oohistory` | d0010_history.md 관리 |
| `ootodo` | d0004_todo.md 관리 |

### 8.3 핵심 문서

| 문서 | 역할 |
|------|------|
| `README.md` | 프로젝트 개요 (1단계) |
| `00_doc/d{SP}0004_todo.md` | TODO 관리 (2단계) |
| `00_doc/d{SP}0010_history.md` | 변경 이력 (2단계) |
| `00_doc/d{SP}0001_prd.md` | PRD (조건부) |
| `00_doc/sp00/d0005_lib.md` | 라이브러리 (조건부) |

### 8.4 에이전트

| 에이전트 | 역할 |
|----------|------|
| `Explore` | 변경 파일 스캔 (병렬) |
| `task-executor` | 문서 갱신 (병렬) |
| `task-checker` | 검증 (병렬) |
| `ooqa` | 품질 분석 (병렬) |

---

## 9. 문제 해결

### 9.1 자주 발생하는 문제

| 문제 | 원인 | 해결 |
|------|------|------|
| README.md 갱신 실패 | Git 변경 없음 | 최소 1개 파일 변경 필요 |
| d0004 동기화 오류 | 파일 형식 불일치 | `.claude/skills/ootodo/references/guide.md` 형식 확인 |
| d0010 중복 이력 | 여러 번 실행 | 실행 전 d0010 마지막 이력 확인 |
| tmp/ 정리 경고 | 임시 파일 존재 | 수동 삭제 후 재실행 |

### 9.2 문서 충돌 처리

**시나리오**: d0004_todo.md 수동 편집 후 oostop 실행 시 충돌

**해결**:
1. `oostop`는 기존 내용 보존 (append 방식)
2. 중복 확인 후 수동 병합
3. 필요 시 `git diff`로 변경 확인

---

## 10. 팁 & 주의사항

### 10.1 권장 사항

- **매일 종료 시**: `oostop run` 실행
- **중간 정리**: `oostop readme` (빠른 체크포인트)
- **주간 정리**: `oostop sync` (문서 일괄 동기화)

### 10.2 주의사항

- Git 커밋 전 `oostop` 실행 (문서 현행화)
- README.md 수동 편집 시 충돌 주의
- tmp/ 폴더 정리 확인 (커밋 제외)

### 10.3 워크플로우 체이닝

```bash
# 세션 종료 → Git 커밋
oostop run && oocommit

# 테스트 → 종료 → 커밋
ootest run && oostop run && oocommit
```

---

## 11. FAQ

**Q1. oostop과 oohistory의 차이점은?**

| 스킬 | 목적 | 대상 문서 |
|------|------|----------|
| `oostop` | 세션 종료 문서 전체 동기화 | README, d0004, d0010, d0001, d0005 |
| `oohistory` | d0010_history.md 전문 관리 | d0010만 |

**Q2. 1단계와 2단계를 동시에 실행해야 하나요?**

**권장**: 예, `oostop run`으로 전체 실행
**선택**: 빠른 종료 시 `oostop readme`만 실행 가능

**Q3. 문서가 자동 갱신되지 않아요.**

**확인 사항**:
1. Git 변경 있는지 확인 (`git status`)
2. 서브프로젝트 컨텍스트 올바른지 확인
3. 문서 형식이 표준에 맞는지 확인

**Q4. README.md에 커스텀 섹션을 추가했는데 유지되나요?**

예, `oostop`는 "최근 작업 내역" 섹션만 갱신하고 나머지는 보존합니다.

---

## 12. 관련 워크플로우

### 12.1 일일 워크플로우

```
oostart run (아침)
    ↓
[개발 작업]
    ↓
oostop run (저녁)
    ↓
oocommit (Git 커밋)
```

### 12.2 기능 개발 워크플로우

```
oodev run (TDD 개발)
    ↓
ootest run (테스트)
    ↓
oocheck run (에러 체크)
    ↓
oostop run (문서 동기화)
    ↓
oocommit (커밋)
```

---

**버전**: v01 (2026-02-05)
**스킬 파일**: `.claude/skills/oostop/SKILL.md`
**연관 가이드**: `.claude/skills/oostart/references/guide.md`, `.claude/skills/ootodo/references/guide.md`
