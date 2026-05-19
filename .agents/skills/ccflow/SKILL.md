---
name: ccflow
description: "참조: common_guide.md | 튜토리얼: .codex/tutorial/11_SW개발워크플로우.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

> 참조: common_guide.md | 튜토리얼: .codex/tutorial/11_SW개발워크플로우.md
> 연동: ccfeature · ccdev · cctest · cccheck · ccreview · ccfix · ccdoc · cchistory · cccommit

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | SW 개발 전체 워크플로우(기획→설계→개발→검증→커밋)를 todo 게이트 방식으로 오케스트레이션 |
| **하는 것** | 사전 todo 점검 → 검증·기획·설계(탐지) → 상세설계 게이트 → todo 0건 시 ccdev·cctest·cccheck·ccreview·ccfix·ccdoc·cccommit 순차 위임 |
| **하지 않는 것** | 각 단계의 직접 구현(스킬 위임만), 설계 단계 이슈 자동 수정(todo 적재만), git push(별도 실행) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | 각 위임 스킬의 산출물 전체 (코드, 00_doc/, git) |
| **실행 레벨** | [todo 게이트] — 사전 todo 점검 → 검증·설계 단계 todo 적재 시 상세설계에서 중단 → todo 0건일 때만 개발·검증 진행 (개발 단계 이슈는 todo 적재 후 ccfix 자동수정) |
| **에이전트 호환** | Codex 권장 — Agent 도구로 각 단계 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

## 문서 이력 관리
- v04 2026-05-17 — todo 게이트 방식 전환: 사전 todo 점검·상세설계 게이트·개발단계 todo적재후 자동fix, ccflow plan 추가
- v03 2026-04-08 — cctest TDD 통합 (RED→GREEN→PASS), --ralph 옵션 추가, ralph/ralplan 관련문서 추가
- v02 2026-04-07 — 완전 무인 자동화 기본화 — --interactive 플래그 추가, 강제 중단 조건 명시
- v01 2026-04-07 — 초기 생성 — 전체 SW 개발 워크플로우 오케스트레이터

---

## 1. 개요

> ⚠️ **필수**: run 명령 시 각 단계를 반드시 Agent 도구로
> 각 스킬(ccfeature/ccdev/cctest 등)을 executor(sonnet) 서브에이전트에 위임할 것.
> 단계별 실행 결과 직접 처리 금지 — 메인 컨텍스트 보호.

`11_SW개발워크플로우.md` 전체 흐름을 **단일 명령**으로 실행하는 오케스트레이터.
미착수 Feature를 순차 처리하되, **todo 게이트**로 검증·설계 문제를 먼저 해소한 뒤 개발에 진입한다.

**기본 동작: todo 게이트 방식**

1. **Step 0 — 사전 todo 점검**: `d{SP}0004_todo.md`에 미해결 todo가 있으면 진행을 보류한다.
   "기존 todo를 먼저 처리한 후 ooflow를 실행하세요" 안내 + 미해결 todo를 **하나씩** 보여주며 처리 여부를 사용자에게 문의.
2. **Step 1 — 검증·기획·설계 (탐지 모드)**: ccprd/ccplan 정합성 검증 + ccfeature next(기획·설계).
   **탐지 위주 — 자동 수정하지 않고** 발견된 정합성/설계 문제를 **전부 `d{SP}0004_todo.md`에 적재**한다.
3. **Step 2 — 상세설계 게이트**: Step 1에서 todo가 적재됐으면 → **상세설계 단계에서 중단**(개발·검증으로 진행하지 않음).
   "발생한 todo를 전부 해결한 후 ooflow를 다시 실행하세요" 안내 + 발생한 todo를 **하나씩** 보여주며 처리 문의.
4. **Step 3 — 개발·검증·완료 (todo 0건일 때만)**: Feature별 cctest write(RED)→ccdev run(GREEN)→cctest run→cccheck run→ccreview run→완료 처리→cccommit.
   **개발 단계 이슈(cccheck/ccreview)**는 발견 시 `d{SP}0004_todo.md`에 **적재 후 ccfix 자동 실행 → 재검증** (중단하지 않고 계속 진행).
5. **Step 4 — 마무리**: ccdoc run → cchistory run → cccommit run(최종).

**핵심 원칙**:
- 설계 단계 이슈 = todo 적재 후 **중단**(자동수정 안 함) / 개발 단계 이슈 = todo 적재 후 **ccfix 자동수정·재검증**
- 기존 스킬(ccfeature/ccdev/cccheck 등)을 순차 위임 — 중복 구현 없음
- 각 Feature 완료 후 커밋 → 중단 시 재시작 가능
- `ccflow plan`은 검토·계획 전용 — 게이트와 무관하게 항상 상세설계에서 멈춤
- `--dry-run`으로 실행 계획 미리 확인

---

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ccflow help` | 서브명령어 목록 표시 | 터미널 |
| `ccflow version` | 스킬 버전 정보 (v04) | 터미널 |
| `ccflow status` | 현재 SP 워크플로우 진행 현황 | 터미널 |
| `ccflow check` | references/checklist.md 기반 체크 | 터미널 |
| `ccflow run` | 사전 todo 점검 → 검증·설계(탐지) → 상세설계 게이트 → todo 0건 시 개발·검증·완료 | 각 스킬 산출물 |
| `ccflow plan` | 사전 todo 점검 + 검증·기획·설계까지만 전반 검토 (항상 상세설계에서 멈춤) | 각 스킬 산출물 |
| `ccflow run --yes` | 확인 생략 후 즉시 실행 지시 출력 | 각 스킬 산출물 |
| `ccflow run --sp N` | 특정 SP 워크플로우 실행 | 각 스킬 산출물 |
| `ccflow run --dry-run` | 실행 계획만 출력 (실제 실행 없음) | 터미널 |
| `ccflow run --interactive` | 단계별 사용자 확인 후 진행 | 각 스킬 산출물 |
| `ccflow run --until 검증` | 검증 단계까지만 실행 (완료 처리 생략) | 각 스킬 산출물 |
| `ccflow run --feature dXXXX` | 특정 Feature 1개만 전체 단계 실행 | 각 스킬 산출물 |
| `ccflow run --ralph` | CRITICAL 실패 시 ralph 루프로 에스컬레이션 (완료 보장) | 각 스킬 산출물 |
| `ccflow run --no-test` | cctest 단계 생략 (빠른 실행 시) | 각 스킬 산출물 |
| `ccflow run --no-review` | ccreview 단계 생략 (빠른 실행 시) | 각 스킬 산출물 |
| `ccflow plan --sp N` | 특정 SP 검토·계획 | 각 스킬 산출물 |
| `ccflow plan --dry-run` | plan 계획만 출력 (실제 실행 없음) | 터미널 |
| `ccflow show checklist` | 역할 수행 체크리스트 표시 | 터미널 |

실행: `uv run python .agents/skills/ccflow/scripts/ooflow_run.py [subcommand] [args]`

---

## 3. 전체 워크플로우

```
ccflow run
    ↓
[Step 0] 사전 todo 점검 — d{SP}0004_todo.md 미해결 todo 스캔
    │
    ├─ 미해결 todo 있음 → 진행 보류
    │     "기존 todo를 먼저 처리한 후 ooflow를 실행하세요"
    │     미해결 todo를 하나씩 보여주며 처리 여부 문의
    │
    └─ 미해결 todo 0건 → 다음 단계
    ↓
[Step 1] 검증·기획·설계 (탐지 모드 — 자동 수정 안 함)
    ├─ ccprd run     ← PRD 정합성 검증 (탐지)
    ├─ ccplan run    ← Plan 정합성 검증 (탐지)
    ├─ ccfeature needed → 미착수 Feature 추출
    └─ Feature별: ccfeature next(상세기획) → ccfeature next(설계 전환)
       └─ 발견된 정합성/설계 문제 전부 d{SP}0004_todo.md 적재
    ↓
[Step 2] 상세설계 게이트
    │
    ├─ Step 1에서 신규 todo 적재됨 → 상세설계에서 중단
    │     "발생한 todo를 전부 해결한 후 ooflow를 다시 실행하세요"
    │     발생한 todo를 하나씩 보여주며 처리 문의
    │     (개발·검증으로 진행하지 않음)
    │
    └─ 신규 todo 0건 → [Step 3] 진행
    ↓
[Step 3] 개발·검증·완료 (todo 0건일 때만)
    Feature별 반복 (순차):
    ├─ cctest write dXXXX     ← TDD RED: TC 코드 작성
    ├─ ccdev run dXXXX        ← TDD GREEN: 테스트 통과 최소 구현
    ├─ cctest run dXXXX       ← 테스트 실행 (PASS 확인)
    ├─ cccheck run dXXXX      ← 정적 분석 (pylint/mypy)
    ├─ ccreview run dXXXX     ← AI 리뷰 (설계·보안·품질 + Codex 2차)
    │   └─ [개발 단계 이슈] cccheck/ccreview 이슈 발견 시:
    │        d{SP}0004_todo.md 적재 → ccfix 자동 실행 → 재검증 (계속 진행)
    ├─ ccfeature next dXXXX   ← 완료 처리
    └─ cccommit run           ← Feature 완료 커밋
    ↓
[Step 4] 마무리
    ├─ ccdoc run       ← d{SP}0001~d{SP}0010 일괄 업데이트
    ├─ cchistory run   ← 완료 이슈 아카이브
    └─ cccommit run    ← 최종 커밋
```

```
ccflow plan   (검토·계획 전용)
    ↓
[Step 0] 사전 todo 점검
    ↓
[Step 1] 검증·기획·설계 — 전반적으로 검토하며 진행
    ↓
상세설계 단계에서 종료 (게이트와 무관하게 항상 멈춤 — 개발로 진행하지 않음)
```

---

## 4. --dry-run 출력 형식

```
[Step 0] 사전 todo 점검
  ✅ 미해결 todo 없음 — 워크플로우 진행 가능

[ccflow dry-run] SP04

실행 예정 단계:
  [1] ccprd run          → PRD 정합성 검증
  [2] ccplan run         → Plan 갱신
  [3] ccfeature needed   → 미착수 Feature 확인

처리 대상 Feature (3개):
  ⬜  d40447   썸네일관리           [기획→설계→개발→검증]
  ...

실제 실행하려면: ccflow run
```

---

## 5. --until 옵션

| 옵션 | 동작 |
|------|------|
| `--until 기획` | 상세기획 생성까지만 |
| `--until 설계` | 설계 전환까지만 (= `ccflow plan`이 고정으로 사용) |
| `--until 개발` | TDD 개발까지만 |
| `--until 검증` | 검증까지만 (완료 처리·커밋 생략) |
| 미지정 | 완료 처리 + 커밋까지 전체 |

---

## 6. 재시작 처리

중단 후 재실행 시:
- Step 0 사전 todo 점검을 먼저 통과해야 한다 (미해결 todo 있으면 재차 보류).
- `ccfeature list`로 현재 단계 스캔, 이미 완료된 Feature 건너뜀.
- 중간 단계(설계/개발/검증)에 멈춘 Feature는 해당 단계부터 재개.

```
[ccflow run] 재시작 감지
  d41001 데이터수집소스  → 🟡개발 단계 → ccdev run d41001부터 재개
  d41002 크롤러모듈      → ✅완료 → 건너뜀
```

---

## 7. 이슈 처리 전략 (단계별 분기)

이슈 처리 방식이 **설계 단계**와 **개발 단계**에서 다르다.

### 7.1 설계 단계 (Step 1~2) — todo 적재 후 중단

검증·기획·설계 단계에서 발견된 문제는 **자동 수정하지 않는다**.

| 단계 | 처리 |
|------|------|
| ccprd run / ccplan run 정합성 문제 | `d{SP}0004_todo.md`에 **적재만** (수정 안 함) |
| ccfeature next(기획·설계) 설계 문제 | `d{SP}0004_todo.md`에 **적재만** (수정 안 함) |
| Step 1 종료 후 신규 todo ≥ 1건 | **상세설계 게이트에서 중단** — 개발·검증으로 진행하지 않음. todo를 하나씩 안내하며 처리 문의 |
| Step 1 종료 후 신규 todo 0건 | Step 3(개발·검증·완료)로 진행 |

### 7.2 개발 단계 (Step 3) — todo 적재 후 ccfix 자동수정·재검증

개발·검증 단계에서 발견된 이슈는 **적재 후 자동 수정**한다 (중단하지 않음).

**cccheck 결과:**

| 심각도 | 자동 처리 |
|--------|----------|
| CRITICAL | `d{SP}0004_todo.md` 적재 → `ccfix run` 자동 실행 → `cccheck run` 재검증 → 최대 3회 반복 |
| ERROR | `d{SP}0004_todo.md` 적재 → `ccfix run` 자동 실행 → 재검증 1회 |
| WARNING | `d{SP}0004_todo.md` 적재 후 **ccreview 단계로 진행** |
| 없음 | ccreview 단계로 진행 |

**ccreview 결과 (`--no-review` 시 이 단계 생략):**

| 심각도 | 자동 처리 |
|--------|----------|
| CRITICAL/ERROR | `d{SP}0004_todo.md` 적재 → `ccfix run` 자동 실행 → `ccreview run` 재검증 → 최대 2회 반복 |
| WARNING/INFO | `d{SP}0004_todo.md` 적재 후 **완료 처리로 진행** |
| 없음 | 완료 처리로 진행 |

> `--interactive` 모드에서는 CRITICAL 발생 시 사용자에게 확인 후 진행.

---

## 7-1. 강제 중단 조건

아래 조건에서 실행이 중단되고 사용자에게 보고된다:

| 조건 | 설명 |
|------|------|
| 사전 todo 미해결 (Step 0) | `d{SP}0004_todo.md`에 미해결 todo 존재 → 진행 보류, todo 처리부터 안내 |
| 상세설계 게이트 (Step 2) | Step 1에서 신규 todo 적재됨 → 상세설계 단계에서 중단, 발생 todo 안내 |
| CRITICAL 3회 반복 실패 | 개발 단계에서 ccfix 3회 후에도 동일 CRITICAL 잔존 → `--ralph` 옵션 시 ralph 루프로 에스컬레이션, 미지정 시 중단 후 보고 |
| 컨텍스트 한도 임박 | 토큰 사용량 85% 초과 시 현재 Feature 완료 후 중단 |
| 파일 시스템 오류 | 파일 쓰기/읽기 실패 등 복구 불가 오류 |
| 명시적 중단 요청 | 사용자가 실행 중 중단 요청 |

중단 시 현재까지 완료된 Feature는 커밋 보존됨. todo 해결 후 `ccflow run`으로 재시작하면 이어서 진행.

---

## 8. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 상태 스캔 | Explore | haiku | Feature 목록·단계 파악 | - |
| 사전 todo 점검 | Explore | haiku | d{SP}0004_todo.md 미해결 todo 스캔 | - |
| 기획/설계 | task-executor | sonnet | ccfeature next 위임 (탐지·todo 적재) | - |
| TDD RED | task-executor | sonnet | cctest write dXXXX 위임 | - |
| 개발 | task-executor | sonnet | ccdev run dXXXX 위임 | - |
| 테스트 실행 | task-checker | sonnet | cctest run dXXXX 위임 | - |
| 정적 분석 | task-checker | sonnet | cccheck run dXXXX 위임 | - |
| AI 리뷰 | code-reviewer + codex:rescue | opus/sonnet | ccreview run dXXXX 위임 | - |
| 이슈 수정 | task-executor | sonnet | ccfix run 위임 (개발 단계만) | - |
| 문서화 | task-executor | sonnet | ccdoc run, cchistory run | - |

---

## 9. 관련 문서

| 문서/스킬 | 역할 |
|----------|------|
| `.codex/tutorial/11_SW개발워크플로우.md` | 이 스킬이 자동화하는 워크플로우 |
| `ccfeature` | 상세 문서 생명주기 관리 |
| `cctodo` | d{SP}0004_todo.md todo 등록·관리 (게이트 대상) |
| `ccdev` | TDD GREEN: 테스트 통과 최소 구현 |
| `cctest` | TDD RED: TC 코드 작성 + 테스트 실행 |
| `cccheck` | 코드 검증 (정적 분석) |
| `ccreview` | AI 코드 리뷰 (설계·보안·품질 + Codex) |
| `ccfix` | 이슈 수정 (개발 단계 자동수정) |
| `ccdoc` | 문서 일괄 업데이트 |
| `cchistory` | 이력 아카이브 |
| `cccommit` | Git 커밋 |
| `ralph` (OMC) | CRITICAL 실패 에스컬레이션 루프 (`--ralph` 옵션 활성화 시) |
| `ralplan` (OMC) | 합의 기반 플래닝 루프 (`/plan --consensus` 별칭) |



<!-- RUN-UPDATE-REF:START -->



## run과 update 분리 원칙



> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.



| 서브커맨드 | 역할 |

|-----------|------|

| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |

| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |



> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.



<!-- RUN-UPDATE-REF:END -->



<!-- KARPATHY-REF:START -->



## Karpathy 코딩 가이드라인 (필수 준수)



> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.

> 로컬 미러: `.codex/rules/karpathy-guidelines.md`



| # | 원칙 | 핵심 규칙 |

|---|------|----------|

| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |

| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |

| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |

| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |



**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.



<!-- KARPATHY-REF:END -->



<!-- GEMMA-REF:START -->



## Gemma 위임 (로컬 LLM)



> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은

> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.



| 항목 | 내용 |

|------|------|

| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |

| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |

| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |

| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |



<!-- GEMMA-REF:END -->

<!-- SAMPLE-REF:START -->



## 샘플 참조 (산출물 품질 향상)



> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.



| 항목 | 내용 |

|------|------|

| 샘플 위치 | `.agents/skills/{스킬명}/samples/` |

| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |

| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |

| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |

| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |



<!-- SAMPLE-REF:END -->



