---
name: ootest
description: "통합 테스트 스킬 'ootest', '테스트', '테스트 코드 작성', '테스트 실행', 'TDD RED', '체크리스트' 등의 키워드로 트리거된다"
metadata:
  version: v09
  category: core-dev
---

> 참조: common_guide.md (에이전트) | oocontext.md (SP) | 상세: `references/guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| 핵심 역할 | TDD RED — TC 작성·반복 실행(PASS까지) |
| 하는 것 | tests/ TC 생성, d{SP}0003 Part C 등록, pytest 반복 |
| 하지 않는 것 | 구현(→oodev), 정적분석(→oocheck), 이슈수정(→oofix) |
| 수정 대상 | `tests/TC*.py`, `d{SP}0003_test.md` Part C |
| 실행 레벨 | [자동] PASS까지 반복 (`uv run pytest`) |

## 1. 개요·가이드

TDD RED + 테스트 작성 + 반복 실행. 컨텍스트: `--sp N` 또는 `oocontext N`. 문서연계: 실패→d{SP}0004 / 개발→d{SP}0002 / 항목→d{SP}0003. 역할분리(oodev=INIT/GREEN/REFACTOR vs ootest=RED/실행/갱신/Part D 재스캔): `references/guide.md` §2.

| 파트 | 내용 |
|------|------|
| 공통 | 우선순위/상태/에러분류 |
| A | 정적분석, 용어체크 |
| B | E2E/UI, Playwright |
| C | pytest, TDD |
| D | oo 모듈 전체 검증 |
| E | 런타임 검증(import) — 필수 |

Streamlit(`pages/*.py`) 시 `references/streamlit_guide.md` 자동 참조.

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootest status` | 서브명령어 리스트, 현재 상태 |
| `ootest check` | references/checklist.md 기반 체크 |
| `ootest run` | 테스트 실행 |
| `ootest show checklist` | 체크리스트 표시 |
| `ootest add checklist "항목"` | 체크리스트 추가 |
| **write [ID]** | **TC 코드 생성(RED) + d{SP}0003 Part C 등록** |
| **write --all** | **미등록 TC 전체 생성** |
| run | 전체 + d{SP}0003 갱신 (Part D 재스캔 선행) |
| **run this** | **직전 작업 파일 관련 TC** (common_guide.md §9) |
| run --unit | Part C pytest 반복 루프 + 갱신 |
| run --e2e | Part B 시나리오 + 갱신 |
| run --module | Part D oo 모듈 + 갱신 |
| run --runtime | Part E 런타임 + 갱신 |
| run [ID] | 특정 TC 실행(자동 재시도) + 갱신 |
| run [P0-P3] | 우선순위별 + 갱신 |
| preview | 계획 출력 |
| checklist [domain] | 요구사항 품질 체크리스트 생성 |

옵션: `--screenshot` `--fail-fast` `--verbose` `--max-retries N`

## 3. 에이전트 매핑

| 유형 | 에이전트 | 모델 | 병렬 |
|------|----------|------|:----:|
| **TC 코드 생성(RED)** | **test-engineer** | **sonnet** | **O** |
| Part A 정적 | python-code-reviewer | sonnet | O |
| Part A 품질 | ooqa | sonnet | O |
| Part B E2E | web-test-orchestrator | sonnet | - |
| Part C 단위 | task-executor | sonnet | - |
| Part D oo | task-executor | sonnet | - |
| Part E 런타임 | task-executor | sonnet | - |
| d0003 갱신 | task-executor | sonnet | - |

병렬: RED(test-engineer, run_in_background=true) | A(reviewer+qa) | B설계(qa+Explore, run_in_background=true)

## 4. 워크플로우

- **5.0 RED (write)**: 경로 `tests/sp{N}/TC[번호]_[모듈].py` (SP00: `tests/`). 흐름: 시나리오 로드 → test-engineer TC 생성 → 저장 → 실패 확인(pass 시 재작성) → Part C 등록 → oodev에 GREEN 신호. 코드 예시: guide §13.1, §14.3.
- **5.0.1 실행 정책**: `run`은 실서버 포함 모든 테스트 실행. `--ignore` 없이 전체 기본. 실패도 계속, FAIL로 기록(SKIP 아님). 제외 시 `--exclude` 명시.
- **5.0.2 완료 기준**: Part C 통과 ≠ 완료. **A/B/C/D/E + 성능·보안 체크리스트 모두 필수**. 상세: guide §16.
- **5.1 run**: 가이드→Part D 재스캔→A→B→C→D→E→d{SP}0003→d{SP}0004
- **5.2 --unit**: Part C → TC매칭 → pytest → 실패 시 반복 루프 → 갱신 (TC규칙: TC[번호]_[모듈].py)
- **5.3 --e2e**: 전제 조건(Playwright/웹서버/Part B TC) 확인. 미충족 시 안내 후 중단(스킵 금지). 충족 시: Part B → Playwright → 갱신 → 스크린샷(tmp/test_screenshots/) → d{SP}0003. 메시지: guide §17.
- **5.4 --module**: oo 모듈 기능 전체 검증(oo/*.py 전체 함수). 카테고리·패턴: guide §6.
- **5.5 --runtime (필수)**: py_compile/pylint 미감지 런타임 에러(StreamlitDuplicateElementKey, ImportError, AttributeError, TypeError) 검증. UnboundLocalError 한계는 oocheck `함수 내부 import 스코프 오류 감지`로 대체 — `oocheck run` 선행 필수. Streamlit `pages/*.py` 시 `tests/sp{N}/test_page_import.py` 자동 생성. 상세: guide §18.
- **5.6 checklist**: 5대 차원(완전성/명확성/일관성/측정가능성/커버리지) × 도메인(ux/api/performance/security). 사용: `ootest checklist [domain]`. 상세: guide §19.

## 5. 컴팩트 (--compact)
3KB·테이블/불릿·이력 3개. 상세: guide §20.

## 6. 프레임워크 레퍼런스
FastAPI/Streamlit 감지 시 `.claude/reference/development/{framework}/` 또는 `references/streamlit_guide.md`. 상세: guide §21.

## 7. 관련문서
guide.md | oodev | oocheck | d{SP}0003 | d{SP}0004 | `.claude/commands/sc/test.md` | `.claude/commands/sc/analyze.md`

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
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->
