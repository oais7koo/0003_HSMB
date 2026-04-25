---
name: ooflow
description: "전체 SW 개발 워크플로우(기획→설계→개발→검증) 자동 실행 오케스트레이터. 'ooflow', '전체 워크플로우', '자동 개발', '파이프라인 실행' 등의 키워드로 트리거된다"
metadata:
  version: v03
  category: core-dev
---

> 참조: common_guide.md | 튜토리얼: 00_doc/tutorial/11_SW개발워크플로우.md
> 연동: oofeature · oodev · ootest · oocheck · ooreview · oofix · oodoc · oohistory · oocommit

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | SW 개발 전체 워크플로우(기획→설계→개발→검증→커밋)를 단일 명령으로 오케스트레이션 |
| **하는 것** | oofeature·oodev·ootest·oocheck·ooreview·oofix·oodoc·oocommit 순차 위임 |
| **하지 않는 것** | 각 단계의 직접 구현(스킬 위임만), git push(별도 실행) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | 각 위임 스킬의 산출물 전체 (코드, 00_doc/, git) |
| **실행 레벨** | [반자동] — dry-run 표시 → 확인 1회 → 완전 자동 (`--yes`로 즉시 자동) |
| **에이전트 호환** | Claude Code 권장 — Agent 도구로 각 단계 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

## 문서 이력 관리
- v03 2026-04-08 — ootest TDD 통합 (RED→GREEN→PASS), --ralph 옵션 추가, ralph/ralplan 관련문서 추가
- v02 2026-04-07 — 완전 무인 자동화 기본화 — --interactive 플래그 추가, 강제 중단 조건 명시
- v01 2026-04-07 — 초기 생성 — 전체 SW 개발 워크플로우 오케스트레이터

---

## 1. 개요

> ⚠️ **필수**: run 명령 시 각 단계를 반드시 Agent 도구로
> 각 스킬(oofeature/oodev/ootest 등)을 executor(sonnet) 서브에이전트에 위임할 것.
> 단계별 실행 결과 직접 처리 금지 — 메인 컨텍스트 보호.

`11_SW개발워크플로우.md` 전체 흐름을 **단일 명령**으로 실행하는 오케스트레이터.  
미착수 Feature를 순차 처리하여 모든 상세 문서가 검증 단계까지 완료되도록 한다.

**기본 동작: 확인 후 완전 무인 자동화**
1. 실행 전 `--dry-run` 결과를 자동 출력 (무엇을 할지 간략히 표시)
2. "위 계획으로 실행하시겠습니까? [y/N]" 한 번만 확인
3. 승인 후 사용자 확인 없이 끝까지 자동 실행
4. CRITICAL/ERROR 이슈도 `oofix`로 자동 수정 후 계속 진행

- 확인 없이 즉시 실행: `ooflow run --yes`
- 단계별 확인: `ooflow run --interactive`

**핵심 원칙**:
- 기존 스킬(oofeature/oodev/oocheck 등)을 순차 위임 — 중복 구현 없음
- 각 Feature 완료 후 커밋 → 중단 시 재시작 가능
- `--dry-run`으로 실행 계획 미리 확인

---

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooflow help` | 서브명령어 목록 표시 | 터미널 |
| `ooflow version` | 스킬 버전 정보 (v02) | 터미널 |
| `ooflow status` | 현재 SP 워크플로우 진행 현황 | 터미널 |
| `ooflow check` | references/checklist.md 기반 체크 | 터미널 |
| `ooflow run` | dry-run 미리보기 → 확인 → 완전 무인 자동 실행 | 각 스킬 산출물 |
| `ooflow run --yes` | 확인 생략 후 즉시 자동 실행 | 각 스킬 산출물 |
| `ooflow run --sp N` | 특정 SP 워크플로우 실행 | 각 스킬 산출물 |
| `ooflow run --dry-run` | 실행 계획만 출력 (실제 실행 없음) | 터미널 |
| `ooflow run --interactive` | 단계별 사용자 확인 후 진행 | 각 스킬 산출물 |
| `ooflow run --until 검증` | 검증 단계까지만 실행 (완료 처리 생략) | 각 스킬 산출물 |
| `ooflow run --feature dXXXX` | 특정 Feature 1개만 전체 단계 실행 | 각 스킬 산출물 |
| `ooflow run --ralph` | CRITICAL 실패 시 ralph 루프로 에스컬레이션 (완료 보장) | 각 스킬 산출물 |
| `ooflow run --no-test` | ootest 단계 생략 (빠른 실행 시) | 각 스킬 산출물 |
| `ooflow run --no-review` | ooreview 단계 생략 (빠른 실행 시) | 각 스킬 산출물 |
| `ooflow show checklist` | 역할 수행 체크리스트 표시 | 터미널 |

실행: `uv run python .claude/skills/ooflow/scripts/ooflow_run.py [subcommand] [args]`

---

## 3. 전체 워크플로우

```
ooflow run
    ↓
[1] 컨텍스트 확인 (현재 SP)
    ↓
[2] PRD 확인 → ooprd run (없으면 생성, 있으면 정합성 검증)
    ↓
[3] Plan 확인 → ooplan run (없으면 생성, 있으면 갱신)
    ↓
[4] oofeature needed → 미착수 Feature 목록 추출
    ↓
[5] Feature별 반복 (순차):
    ├─ oofeature next dXXXX      ← 상세기획 생성
    ├─ oofeature next dXXXX      ← 기획→설계 전환
    ├─ ootest write dXXXX        ← TDD RED: TC 코드 작성 (*기본 ON)
    ├─ oodev run dXXXX           ← TDD GREEN: 테스트 통과 최소 구현
    ├─ ootest run dXXXX          ← 테스트 실행 (PASS 확인)
    ├─ [oofix run]               ← 테스트 실패 수정
    ├─ oocheck run dXXXX         ← 정적 분석 (pylint/mypy)
    ├─ [oofix run]               ← oocheck 이슈 수정 (CRITICAL/ERROR)
    ├─ ooreview run dXXXX        ← AI 리뷰 (설계·보안·품질 + Codex 2차) *기본 ON
    ├─ [oofix run]               ← ooreview 이슈 수정 (CRITICAL/ERROR)
    ├─ oofeature next dXXXX      ← 완료 처리
    └─ oocommit run              ← Feature 완료 커밋
    ↓
[6] oodoc run                    ← d{SP}0001~d{SP}0010 일괄 업데이트
    ↓
[7] oohistory run                ← 완료 이슈 아카이브
    ↓
[8] oocommit run                 ← 최종 커밋
```

---

## 4. --dry-run 출력 형식

```
[ooflow dry-run] SP04

실행 예정 단계:
  [1] ooprd run          → PRD 정합성 검증
  [2] ooplan run         → Plan 갱신
  [3] oofeature needed   → 미착수 Feature 확인

미착수 Feature (3개):
  F001-1  데이터수집소스    → 기획→설계→개발→검증→완료
  F001-2  크롤러모듈        → 기획→설계→개발→검증→완료
  F002-1  전처리파이프라인  → 기획→설계→개발→검증→완료

  [4~6] Feature별 순차 실행 (3 × 5단계 = 15 스킬 호출)
  [7] oodoc run
  [8] oohistory run
  [9] oocommit run (최종)

총 예상 스킬 호출: 21회
실제 실행하려면: ooflow run
```

---

## 5. --until 옵션

| 옵션 | 동작 |
|------|------|
| `--until 기획` | 상세기획 생성까지만 |
| `--until 설계` | 설계 전환까지만 |
| `--until 개발` | TDD 개발까지만 |
| `--until 검증` | 검증까지만 (완료 처리·커밋 생략) |
| 미지정 | 완료 처리 + 커밋까지 전체 |

---

## 6. 재시작 처리

중단 후 재실행 시:
- `oofeature list`로 현재 단계 스캔
- 이미 완료된 Feature 건너뜀
- 중간 단계(설계/개발/검증)에 멈춘 Feature는 해당 단계부터 재개

```
[ooflow run] 재시작 감지
  d41001 데이터수집소스  → 🟡개발 단계 → oodev run d41001부터 재개
  d41002 크롤러모듈      → ✅완료 → 건너뜀
```

---

## 7. 이슈 처리 전략 (완전 자동)

`oocheck run dXXXX` 결과에 따른 자동 분기 — 사용자 확인 없이 처리:

| 심각도 | 자동 처리 |
|--------|----------|
**oocheck 결과:**

| 심각도 | 자동 처리 |
|--------|----------|
| CRITICAL | `oofix run` 자동 실행 → `oocheck run` 재검증 → 최대 3회 반복 |
| ERROR | `oofix run` 자동 실행 → 재검증 1회 |
| WARNING | d{SP}0004_todo.md 자동 등록 후 **ooreview 단계로 진행** |
| 없음 | ooreview 단계로 진행 |

**ooreview 결과 (`--no-review` 시 이 단계 생략):**

| 심각도 | 자동 처리 |
|--------|----------|
| CRITICAL/ERROR | `oofix run` 자동 실행 → `ooreview run` 재검증 → 최대 2회 반복 |
| WARNING/INFO | d{SP}0004_todo.md 자동 등록 후 **완료 처리로 진행** |
| 없음 | 완료 처리로 진행 |

> `--interactive` 모드에서는 CRITICAL 발생 시 사용자에게 확인 후 진행

---

## 7-1. 강제 중단 조건

아래 조건에서만 자동 실행이 중단되고 사용자에게 보고:

| 조건 | 설명 |
|------|------|
| CRITICAL 3회 반복 실패 | oofix 3회 시도 후에도 동일 CRITICAL 잔존 → `--ralph` 옵션 시 ralph 루프로 에스컬레이션, 미지정 시 중단 후 보고 |
| 컨텍스트 한도 임박 | 토큰 사용량 85% 초과 시 현재 Feature 완료 후 중단 |
| 파일 시스템 오류 | 파일 쓰기/읽기 실패 등 복구 불가 오류 |
| 명시적 중단 요청 | 사용자가 실행 중 중단 요청 |

중단 시 현재까지 완료된 Feature는 커밋 보존됨. `ooflow run`으로 재시작하면 이어서 진행.

---

## 8. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 상태 스캔 | Explore | haiku | Feature 목록·단계 파악 | - |
| 기획/설계 | task-executor | sonnet | oofeature next 위임 | - |
| TDD RED | task-executor | sonnet | ootest write dXXXX 위임 | - |
| 개발 | task-executor | sonnet | oodev run dXXXX 위임 | - |
| 테스트 실행 | task-checker | sonnet | ootest run dXXXX 위임 | - |
| 정적 분석 | task-checker | sonnet | oocheck run dXXXX 위임 | - |
| AI 리뷰 | code-reviewer + codex:rescue | opus/sonnet | ooreview run dXXXX 위임 | - |
| 이슈 수정 | task-executor | sonnet | oofix run 위임 | - |
| 문서화 | task-executor | sonnet | oodoc run, oohistory run | - |

---

## 9. 관련 문서

| 문서/스킬 | 역할 |
|----------|------|
| `00_doc/tutorial/11_SW개발워크플로우.md` | 이 스킬이 자동화하는 워크플로우 |
| `oofeature` | 상세 문서 생명주기 관리 |
| `oodev` | TDD GREEN: 테스트 통과 최소 구현 |
| `ootest` | TDD RED: TC 코드 작성 + 테스트 실행 |
| `oocheck` | 코드 검증 (정적 분석) |
| `ooreview` | AI 코드 리뷰 (설계·보안·품질 + Codex) |
| `oofix` | 이슈 수정 |
| `oodoc` | 문서 일괄 업데이트 |
| `oohistory` | 이력 아카이브 |
| `oocommit` | Git 커밋 |
| `ralph` (OMC) | CRITICAL 실패 에스컬레이션 루프 (`--ralph` 옵션 활성화 시) |
| `ralplan` (OMC) | 합의 기반 플래닝 루프 (`/plan --consensus` 별칭) |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.claude/rules/karpathy-guidelines.md`

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
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->

