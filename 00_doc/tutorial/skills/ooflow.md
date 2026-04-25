# ooflow 튜토리얼

## § 1. 필요한 이유

SW 개발 워크플로우는 기획→설계→개발→검증→커밋의 반복입니다. 매번 각 단계의 명령을 순서대로 입력하는 것은 번거롭고 실수하기 쉽습니다. 전체 워크플로우를 단일 명령으로 자동화하면 팀 전체가 표준 프로세스를 따를 수 있고, 중단 후 재시작할 때도 현재 위치부터 바로 이어서 진행할 수 있습니다. 이것이 ooflow의 목표입니다.

## § 2. 빠른 시작 (3가지 기본 명령)

```bash
# 1. 실행 계획 미리보기
ooflow run --dry-run

# 2. 확인 후 자동 실행
ooflow run

# 3. 확인 생략하고 즉시 실행
ooflow run --yes
```

## § 3. 자주 쓰는 명령어

| 명령어 | 사용 시점 | 설명 |
|--------|---------|------|
| `ooflow run --dry-run` | 실행 전 계획 확인 | 무엇을 할지 미리 표시 |
| `ooflow run` | 표준 실행 | 확인 1회 → 완전 자동 |
| `ooflow run --yes` | 빠른 실행 | 확인 생략, 즉시 시작 |
| `ooflow status` | 진행 중 상태 | 현재 진행 상황 표시 |
| `ooflow run --until 검증` | 부분 실행 | 검증까지만 실행 (완료 제외) |
| `ooflow run --feature d{}` | 특정 기능만 | 1개 기능만 전체 단계 실행 |

## § 4. 권장 워크플로우

```
[회차 시작]

1. 상태 확인
   ooflow status → 현재 진행 상황 파악

2. 실행 계획 미리보기
   ooflow run --dry-run → 무엇을 할지 확인

3. 확인 후 자동 실행
   ooflow run → 한 번만 확인 후 끝까지 자동

4. 완료 확인
   git log --oneline -10 → 커밋 이력 확인

[진행 중 중단]

5. 중단 지점 저장
   (자동으로 현재 진행 상황 저장됨)

[재시작]

6. 재개 실행
   ooflow run → 중단 지점부터 자동 감지 및 재개
```

## § 5. 전체 명령어 참조

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooflow help` | 서브명령어 목록 | 터미널 |
| `ooflow version` | 스킬 버전 (v03) | 터미널 |
| `ooflow status` | 현재 SP 워크플로우 진행 현황 | 터미널 |
| `ooflow check` | 체크리스트 검증 | 터미널 |
| `ooflow run` | dry-run → 확인 → 자동 실행 | 각 스킬 산출물 |
| `ooflow run --yes` | 확인 생략 후 즉시 자동 실행 | 각 스킬 산출물 |
| `ooflow run --sp N` | 특정 SP 워크플로우 실행 | 각 스킬 산출물 |
| `ooflow run --dry-run` | 실행 계획만 출력 | 터미널 |
| `ooflow run --interactive` | 단계별 사용자 확인 | 각 스킬 산출물 |
| `ooflow run --until 검증` | 검증까지만 실행 | 각 스킬 산출물 |
| `ooflow run --feature d{}` | 특정 기능 1개만 | 각 스킬 산출물 |
| `ooflow run --ralph` | CRITICAL 실패 시 ralph 루프 | 최종 해결 보장 |
| `ooflow run --no-test` | 테스트 단계 생략 | 빠른 실행 |
| `ooflow run --no-review` | 리뷰 단계 생략 | 빠른 실행 |
| `ooflow show checklist` | 체크리스트 표시 | 터미널 |

## § 6. 상세 사용 방법

### 6.1 전체 워크플로우 단계

```
[1] 컨텍스트 확인 (현재 SP)
[2] PRD 확인 → ooprd run
[3] Plan 확인 → ooplan run
[4] oofeature needed → 미착수 Feature 목록 추출
[5] Feature별 반복:
    ├─ oofeature next (상세기획 생성)
    ├─ oofeature next (기획→설계)
    ├─ ootest write (TDD RED)
    ├─ oodev run (TDD GREEN)
    ├─ ootest run (테스트 실행)
    ├─ oocheck run (정적 분석)
    ├─ ooreview run (AI 리뷰)
    ├─ oofeature next (완료)
    └─ oocommit run (커밋)
[6] oodoc run (문서 업데이트)
[7] oohistory run (이력 아카이브)
[8] oocommit run (최종 커밋)
```

### 6.2 이슈 자동 처리

**oocheck 결과**:

| 심각도 | 자동 처리 |
|--------|----------|
| CRITICAL | oofix 3회 반복 |
| ERROR | oofix 1회 실행 |
| WARNING | d{SP}0004.md 등록 후 진행 |

**ooreview 결과**:

| 심각도 | 자동 처리 |
|--------|----------|
| CRITICAL/ERROR | oofix 2회 반복 |
| WARNING/INFO | d{SP}0004.md 등록 후 진행 |

### 6.3 강제 중단 조건

아래 조건에서만 자동 중단:

| 조건 | 설명 |
|------|------|
| CRITICAL 3회 반복 실패 | `--ralph` 미지정 시 중단, 지정 시 ralph 루프 활성화 |
| 컨텍스트 85% 초과 | 현재 Feature 완료 후 중단 |
| 파일 시스템 오류 | 복구 불가 오류 시 중단 |

## § 7. 실전 시나리오

### 7.1 전체 워크플로우 실행

```bash
# 1. 현재 상황 확인
ooflow status

# 2. 실행 계획 미리보기
ooflow run --dry-run

# 3. 확인 후 자동 실행
ooflow run

# 4. 완료 확인
git log --oneline -5
```

### 7.2 특정 기능 1개만 실행

```bash
# 특정 Feature 1개만 기획부터 완료까지 전체 단계 실행
ooflow run --feature d41001

# 또는 확인 생략
ooflow run --feature d41001 --yes
```

### 7.3 검증까지만 실행

```bash
# 개발과 검증까지만 진행, 완료 처리와 커밋은 생략
ooflow run --until 검증
```

### 7.4 테스트/리뷰 단계 생략

```bash
# 빠른 실행: 테스트 단계 생략
ooflow run --no-test

# 빠른 실행: 리뷰 단계 생략
ooflow run --no-review
```

### 7.5 중단 후 재개

```bash
# [실행 중 네트워크 끊김 등으로 중단]

# 몇 시간 후 재실행
ooflow run

# → 자동으로 중단 지점 감지 → 이어서 진행
```

### 7.6 CRITICAL 실패 에스컬레이션

```bash
# ralph 루프 활성화하여 CRITICAL 문제 반드시 해결
ooflow run --ralph
```

## § 8. 입출력 명세

### 8.1 입력 항목

| 항목 | 타입 | 용도 | 필수 |
|------|------|------|:----:|
| --dry-run | 플래그 | 계획 미리보기 | - |
| --yes | 플래그 | 확인 생략 | - |
| --sp N | 숫자 | 특정 SP 지정 | - |
| --until 단계 | 텍스트 | 부분 실행 | - |
| --feature d{} | 문자열 | 특정 기능 1개 | - |
| --ralph | 플래그 | CRITICAL 에스컬레이션 | - |
| --no-test | 플래그 | 테스트 생략 | - |
| --no-review | 플래그 | 리뷰 생략 | - |

### 8.2 출력 항목

| 항목 | 타입 | 용도 |
|------|------|------|
| 상세 문서 | .md 파일 | 각 기능별 상세 기획/설계 |
| 테스트 코드 | .py 파일 | ootest 생성 TC |
| 구현 코드 | .py 파일 | oodev 개발 코드 |
| 검증 결과 | 보고서 | oocheck/ooreview 결과 |
| 커밋 | Git commit | 각 Feature 완료 후 커밋 |
| 문서 업데이트 | d{SP}000X.md | 전체 문서 일괄 업데이트 |

## § 9. FAQ

**Q. 전체 실행 시간은 얼마나 걸리나요?**
A. Feature 개수와 복잡도에 따라 다릅니다. 평균 Feature당 30~60분.

**Q. 중단되었을 때 진행 상황이 어디까지 저장되나요?**
A. 각 Feature 완료 후 자동 커밋되므로 완료된 Feature는 git 이력에 보존됩니다.

**Q. CRITICAL 이슈가 반복되면 어떻게 되나요?**
A. 기본: 3회 후 중단 / `--ralph`: ralph 루프 활성화하여 반드시 해결할 때까지 반복

**Q. 특정 단계(예: 리뷰)만 재실행할 수 있나요?**
A. `ooflow`는 전체 오케스트레이션이므로 단계별 재실행은 직접 스킬 명령으로 실행하세요.

**Q. 테스트 없이 빠르게 진행하고 싶습니다.**
A. `ooflow run --no-test`로 테스트 단계를 생략할 수 있습니다.

## § 10. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 상태 스캔 | Explore | haiku | Feature 목록·단계 파악 | - |
| 기획/설계 | task-executor | sonnet | oofeature 위임 | - |
| TDD RED | task-executor | sonnet | ootest write 위임 | - |
| 개발 | task-executor | sonnet | oodev run 위임 | - |
| 테스트 | task-checker | sonnet | ootest run 위임 | - |
| 정적 분석 | task-checker | sonnet | oocheck run 위임 | - |
| AI 리뷰 | code-reviewer | opus | ooreview run 위임 | - |
| 이슈 수정 | task-executor | sonnet | oofix run 위임 | - |
| 문서화 | task-executor | sonnet | oodoc/oohistory 위임 | - |

## § 11. 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oof` | Feature 생명주기 관리 |
| `oodev` | TDD GREEN: 테스트 통과 최소 구현 |
| `ootest` | TDD RED: TC 코드 작성 + 테스트 실행 |
| `oocheck` | 정적 분석 (pylint/mypy) |
| `ooreview` | AI 코드 리뷰 |
| `oofix` | 이슈 수정 |
| `oodoc` | 문서 일괄 업데이트 |
| `oohistory` | 이력 아카이브 |
| `oocommit` | Git 커밋 |
