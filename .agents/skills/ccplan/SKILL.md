---
name: ccplan
description: "공통: .codex/guides/common_guide.md | 상세 가이드: .agents/skills/ccplan/references/guide.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

> 공통: .codex/guides/common_guide.md | 상세 가이드: .agents/skills/ccplan/references/guide.md

## 문서 이력 관리
- v07 2026-04-19 — optimize → check --fix 통합

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| 역할 | PRD→Plan(Epic/Feature/Task) Architect, [반자동] → `00_doc/sp{N}/d{SP}0002_plan.md` |
| Do/Don't | Plan·아키텍처 / PRD(→ccprd)·구현(→ccdev)·이슈(→ccfix). 컨텍스트: `--sp N` 또는 `cccontext N` |

## 2. 서브명령어

> 출력은 `d{SP}0002_plan.md`(설계/워크플로우는 별도 문서) — help/version/status/check/show/add는 터미널.

| 명령어 | 설명 |
|--------|------|
| `help` / `version`(v07) / `status` | 도움말 / 버전 / 상태 |
| `check` | checklist.md 기반 체크 |
| `show checklist` / `add checklist "항목"` | 체크리스트 표시/추가 |
| run | PRD → Task 완전 생성 (= run task) |
| **run this** | **직전 작업 관련 계획 업데이트** (→ common_guide.md §9) |
| run epic / run feature / run task(기본) | PRD → Epic/Feature/Task |
| detail | 실행 전 상세 설계 (→ccdev) |
| check --fix | Plan 검토·개선 (구 `optimize`) |
| sync | PRD 변경 동기화 |
| design [대상] | 시스템/API/컴포넌트/DB 설계 |
| workflow [prd] | PRD→워크플로우 (페르소나/전략/리스크) |

design 옵션: `--type architecture\|api\|component\|database`, `--format diagram\|spec\|code`, `--iterative`
workflow 옵션: `--persona`, `--strategy systematic\|agile\|mvp`, `--output roadmap\|tasks\|detailed`, `--estimate`, `--risks`, `--parallel`

## 3. 서브에이전트

> prefix `oh-my-claudecode:` (모델: explore=haiku, planner/architect/critic=opus)
- 분석(병렬): explore | 계획: planner | 아키텍처: architect | 검토: critic | 문서화/검증: task-executor / task-checker

## 4. Plan 템플릿 (`templates/plan_template.md`)
목차: 문서관리 → 구현개요 → WBS → 스프린트 → 기술설계 → 리스크 → 의사결정 → 진행추적

## 5. 워크플로우 (요약)

> 흐름·정보수집·코드 예시: references/guide.md §2

- run: PRD 로드 → 누락 정보 1개씩 질문 → Epic→Feature→Task 분해 → 저장
- detail: 분석 → 태스크 구체화 → 승인 | sync: PRD 변경 분석 → 업데이트
- check --fix: PRD 정합성 → 구조/일정 최적화 → 리스크
- run 옵션: epic(페이지 개요 5.1, 하위 삭제) / feature(페이지 상세 5.2, Task 삭제) / task(기본, 5.2+상세기획, 전체 업데이트)
- 필터: PRD 5.1 진행=아니오 제외. check: 커버리지 100%·순환의존성 없음·크리티컬 패스 최소·스프린트 균형. 완료 후 `ccfeature needed` 권장

## 6. PRD → Plan 매핑
> references/guide.md §3. 매핑: 비전→목표 / 기능→Epic / 마일스톤→스프린트. 레벨 Epic→Feature→Task. PRD §MoSCoW→Epic / §기능상세→Task / §기술스택→설계

## 7. Streamlit (자동 감지)
- 감지: `pages/*.py` | `import streamlit` | `run.bat`의 streamlit → `references/streamlit_guide.md`
- 3계층: PRD(What) → Plan(Where) → d{SP}1XXX_페이지명_단위개발.md(How)

## 8. 상세 문서 현황 (plan.md 8.2절)

`sync`/`run` 시 `00_doc/sp{N}/` 스캔 → 8.2절 자동 갱신. 패턴 `*_상세{기획,설계,개발,검증}_*.md`. 단계 ⚪기획→🔵설계→🟡개발→🟢검증→✅완료. 연동 `ccfeature`/`ccdev run dXXXX`. 형식: references/guide.md §4.6

## 9. 도구 연동 / 딥러닝 실험

- ccdev: detail→상세 설계→TDD | Task Master: Epic→Task / Feature→Subtask / 스프린트→태그 / 의존성→dependencies
- 매트릭스 컬럼: # / 실험ID / 변경사항 / 하이퍼파라미터 / 상태 / 주요메트릭. 상태: 완료/진행중/실패/대기. 원칙: 원본 기준
> 비교표 예시: references/guide.md §4.6

## 10. Plan 콘텐츠 범위 (중복 방지)
> common_guide.md §6.1.1 / references/guide.md §4.8. Plan="How/When", PRD 복사 금지. 소유=기술스택·폴더·DDL·WBS·리스크·의사결정 / PRD 참조=목적·범위·기능요구·UI·비기능·스토리

## 11. 컴팩트 / 프레임워크 / 관련 / GSD

- `--compact`: 3KB / 테이블·불릿 / 이력 3개 / 예제 제외 (references/guide.md §4.7)
- 프레임워크 감지 → `.codex/reference/development/{framework}/`: FastAPI→`fast-api/`, Streamlit→`references/streamlit_guide.md`
- 입력 `d{SP}0001_prd.md` / 출력 `d{SP}0002_plan.md` / 관련 `ccdev/SKILL.md`·`sc/task.md`·`sc/estimate.md`
- GSD: `ccplan run`↔`/gsd:plan-phase [N]`(옵션 `--research`), `ccprd clarify`↔`/gsd:discuss-phase [N]`, `ccplan check --fix`↔`/gsd:plan-milestone-gaps`. 차이: OAIS는 `d{SP}0002_plan.md` / GSD는 `.planning/phases/N/PLAN.md`. 조합: references/guide.md §4.9

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- QMD-REF:START -->

## QMD 마크다운 검색 (문서 내용 탐색 시)

> 마크다운 문서 **내용**을 찾을 때는 Glob/Grep 대신 **`mcp__qmd__query`** 우선 사용.
> qmd 미가동 시 Glob/Grep 폴백. 자세한 기준: `.codex/guides/common_guide.md §10`

| 도구 | 적합한 상황 |
|------|-----------|
| `mcp__qmd__query` (lex) | 키워드·문서번호·용어 검색 |
| `mcp__qmd__query` (vec) | 자연어 의미 검색 |
| `Glob` | 파일 경로 패턴 검색 |
| `Grep` | 코드·특정 문자열 검색 |

**인덱싱**: `ccstart run` 시 `qmd update` 자동 실행 / 최초: `qmd collection add . --name {프로젝트명}`

<!-- QMD-REF:END -->

> Karpathy 코딩 4원칙 준수: `.codex/rules/karpathy-guidelines.md` (Think Before / Simplicity / Surgical / Goal-Driven)

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
