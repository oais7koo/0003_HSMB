# ooflow 가이드

## 문서 이력 관리
- v02 2026-05-17 — todo 게이트 방식 명세(run 게이트·plan 추가·개발단계 todo적재후 자동fix)
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**ooflow**: 전체 SW 개발 워크플로우(기획→설계→개발→검증) 자동 오케스트레이터.

- **참조**: SKILL.md (서브명령어·워크플로우)
- **이 문서**: 방법론(How) — 실행 패턴, 입력/출력 형식, 사용 가이드

ooflow는 **todo 게이트 방식**으로 동작한다. 검증·설계 단계에서 발견된 문제를
`d{SP}0004_todo.md`에 적재하고, 미해결 todo가 있으면 상세설계 단계에서 멈춘다.
todo가 0건일 때만 개발·검증·완료 단계로 진입한다.

---

## 2. 기본 사용법

### 2.1 서브명령어 요약

| 명령어 | 동작 |
|--------|------|
| `ooflow run` | 사전 todo 점검 → 검증·설계(탐지) → 상세설계 게이트 → todo 0건 시 개발·검증·완료 |
| `ooflow plan` | 사전 todo 점검 + 검증·기획·설계까지만 전반 검토 (항상 상세설계에서 멈춤) |
| `ooflow status` | 현재 SP 워크플로우 진행 현황 |
| `ooflow check` | references/checklist.md 기반 체크 |
| `ooflow version` | 스킬 버전 정보 (v04) |
| `ooflow help` | 서브명령어 목록 표시 |

실행: `uv run python .claude/skills/ooflow/scripts/ooflow_run.py [subcommand] [args]`

### 2.2 run vs plan 선택

| 상황 | 사용 명령 |
|------|----------|
| 기획·설계 검토만 하고 싶다 | `ooflow plan` |
| 설계 완료 후 개발까지 진행하고 싶다 | `ooflow run` |
| 실행 전 계획만 확인 | `ooflow run --dry-run` / `ooflow plan --dry-run` |

`ooflow plan`은 검토·계획 전용 모드다. 게이트 통과 여부와 무관하게 **항상**
상세설계 단계에서 멈추며, 개발 단계로 진행하지 않는다.

---

## 3. 워크플로우

### 3.1 ooflow run — todo 게이트

```
[Step 0] 사전 todo 점검
   d{SP}0004_todo.md를 스캔해 미해결 todo 개수 확인
   ├─ 미해결 todo ≥ 1건 → 진행 보류
   │     "기존 todo를 먼저 처리한 후 ooflow를 실행하세요" 안내
   │     미해결 todo를 하나씩 보여주며 처리 여부 문의
   └─ 미해결 todo 0건 → Step 1
   ↓
[Step 1] 검증·기획·설계 (탐지 모드)
   ooprd run / ooplan run 정합성 검증 + oofeature next(기획·설계)
   ※ 자동 수정하지 않음 — 발견된 정합성/설계 문제를
     전부 d{SP}0004_todo.md에 적재
   ↓
[Step 2] 상세설계 게이트
   ├─ Step 1에서 신규 todo 적재됨 → 상세설계에서 중단
   │     "발생한 todo를 전부 해결한 후 ooflow를 다시 실행하세요" 안내
   │     발생한 todo를 하나씩 보여주며 처리 문의
   │     (개발·검증으로 진행하지 않음)
   └─ 신규 todo 0건 → Step 3
   ↓
[Step 3] 개발·검증·완료 (todo 0건일 때만)
   Feature별: ootest write(RED) → oodev run(GREEN) → ootest run
              → oocheck run → ooreview run → 완료 처리 → oocommit
   ※ 개발 단계 이슈(oocheck/ooreview) 발견 시:
     d{SP}0004_todo.md 적재 → oofix 자동 실행 → 재검증 (계속 진행)
   ↓
[Step 4] 마무리
   oodoc run → oohistory run → oocommit run(최종)
```

### 3.2 ooflow plan — 검토·계획 전용

```
[Step 0] 사전 todo 점검
   ↓
[Step 1] 검증·기획·설계 — 전반적으로 검토하며 진행
   ↓
상세설계 단계에서 종료
   게이트 통과 여부와 무관하게 항상 멈춤 (개발로 진행 안 함)
```

### 3.3 단계별 이슈 처리 — 설계 vs 개발

ooflow는 이슈가 발견된 단계에 따라 처리 방식이 다르다.

| 구분 | 설계 단계 (Step 1~2) | 개발 단계 (Step 3) |
|------|----------------------|--------------------|
| 대상 | ooprd/ooplan 정합성, oofeature 설계 문제 | oocheck/ooreview 이슈 |
| 처리 | `d{SP}0004_todo.md` **적재만** | `d{SP}0004_todo.md` **적재 후 oofix 자동수정** |
| 흐름 | 신규 todo 있으면 **상세설계에서 중단** | **중단하지 않고** 재검증 후 계속 진행 |
| 반복 | 사용자가 todo 해결 후 ooflow 재실행 | oofix→재검증 최대 3회(oocheck)/2회(ooreview) |

**설계 단계**: 정합성·설계 문제는 사람이 검토·결정해야 하므로 자동 수정하지
않고 todo로 적재만 한 뒤 게이트에서 멈춘다.

**개발 단계**: 코드 레벨 이슈는 oofix로 안전하게 자동 수정 가능하므로,
todo에 적재한 뒤 oofix를 자동 실행하고 재검증 루프를 돌린다.

---

## 4. 입출력 형식

| 항목 | 내용 |
|------|------|
| 입력 | 서브명령어 인자 또는 현재 SP 컨텍스트 |
| 출력 | 터미널 출력 (실행 지시) 또는 각 위임 스킬 산출물 |
| 게이트 입력 | `d{SP}0004_todo.md` 미해결 todo (`| ID | ... | 상태 |` 형식, 상태=대기/pending/진행중) |
| 로그 | 검증·설계 문제 및 개발 단계 이슈 → d{SP}0004_todo.md 등록 |

todo 행 판정: 테이블 행(`|`로 시작)에서 마지막 셀(상태)이
대기/pending/진행중 등 미해결 키워드를 포함하면 미해결 todo로 집계한다.
`d{SP}0004_todo.md` 파일이 없거나 미해결 todo가 0건이면 게이트를 통과한다.

---

## 5. 주의사항

- SP 컨텍스트 확인 후 실행 (CWD 자동 감지 또는 `--sp N`).
- 사전 todo 점검을 통과하지 못하면 `ooflow run`은 진행을 보류한다 —
  기존 todo부터 처리할 것.
- 상세설계 게이트에서 중단된 경우, 발생한 todo를 전부 해결한 뒤
  `ooflow run`을 다시 실행해야 개발 단계로 진입한다.
- 설계 단계 이슈는 자동 수정되지 않는다 (todo 적재만). 개발 단계 이슈만
  oofix로 자동 수정된다.
- 상세 서브명령어·옵션은 SKILL.md 참조.
