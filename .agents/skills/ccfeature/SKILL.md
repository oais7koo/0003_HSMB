---
name: ccfeature
description: "공통 가이드: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

> 공통 가이드: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md

> 연동: ooplan (plan.md 8.2절) | oodev (상세 문서 기반 개발) | oocheck (검증)



## 0. 스킬 요약



| 항목 | 내용 |

|------|------|

| **역할** | 상세 문서 5단계(기획→설계→구현→검증→완료) 생명주기 관리 |

| **하는 것** | 문서 생성·rename 단계 전환·미착수 Feature 리스트업 |

| **하지 않는 것** | 코드 구현(→oodev) / 테스트(→ootest) / 체크(→oocheck) |

| **대상** | `00_doc/sp{N}/dXXXX_상세*.md` |

| **실행 레벨** | [반자동] — Agent 도구 위임 필수 |



## 문서 이력 관리

- v21 2026-04-21 — §A 상세설계 표준 구조 추가 — A.1 구현 코드 구조·파일 위치 테이블 필수화 (workflow-detail.md §5.5)

- v20 2026-04-19 — §3 번호 고정 원칙 명시 — 단계 전환 시 문서번호 불변, 파일명 rename만 허용

- v19 2026-04-19 — validate → check 통합

- v17 2026-04-18 — rmdup 서브명령어 추가 — 같은 번호 복수 단계 파일 정리 (`oofeature_rmdup.py`)

- v16 2026-04-16 — 설계→구현 전환 필수 체크리스트 추가 — `oodev run dXXXX` 건너뜀 방지 경고



> 이전 이력(v07~v15): `references/guide.md §8` 참조



---



## 1. 개요



상세 문서 5단계(기획→설계→구현→검증→완료) 관리. 단계가 파일명에 포함됨. 워크플로우·Stage-Scoped Edit 규칙·연동: `references/guide.md §2`.



## 2. 서브명령어



| 명령어 | 설명 |

|--------|------|

| `ccfeature help` / `version` / `status` | 도움말 / 버전 / 현재 SP 현황 |

| `ccfeature new dXXXX "기능명" [--stage 단계]` | 상세 문서 생성 (`--stage` 미지정 시 기획) |

| `ccfeature next dXXXX` / `next this` | 다음 단계 rename + 연계 스킬 실행 (`this`=직전 작업, common_guide §9) |

| `ccfeature stage dXXXX 단계` | 단계 수동 변경 (rename만) |

| `ccfeature list` | 현재 SP 상세 문서 목록 + 단계 현황 |

| `ccfeature needed [--sp N]` | plan.md Feature ↔ 상세 문서 교차 비교 → 미착수 리스트업 |

| `ccfeature sync` | plan.md 8.2절 강제 갱신 |

| `ccfeature update <doc_id> [--sp N]` | **문서↔코드 비교 → 현행화 → 미구현 배치** (oocommit 연동) |
| `ccfeature update` | 변경 감지 → 상세기획 롤백 후보 표시 |

| `ccfeature update --apply` / `--force` | 롤백 실행 (`--force`=`--apply` 별칭) |

| `ccfeature update --dry` | 롤백 미리보기 |

| `ccfeature update --from-plan` / `--from-doc` | (하위 호환) plan.md / 상세구현+oocheck 기반 롤백 |

| `ccfeature note dXXXX "내용" [--sp N]` | ## 메모 섹션에 날짜+내용 추가 |

| `ccfeature issue dXXXX "이슈내용" [--sp N]` | ## 이슈 섹션에 추가 (🔴 미해결) |

| `ccfeature issue dXXXX --resolve` | 최신 미해결 이슈 → ✅ 해결 |

| `ccfeature check [--sp N] [--verbose] [--dry-run] [--checklist]` | 정합성 검증 (V01~V08) |

| `ccfeature rmdup [--sp N] [--all] [--dry-run]` | 같은 번호 복수 단계 파일 → 최신만 유지 |



실행(check): `uv run python .claude/skills/ccfeature/scripts/oofeature_validate.py [--sp N] [--verbose] [--dry-run]`



---



## 3. 파일명 규칙



`d{SP}{기능번호}_상세{단계}_{기능명}.md` — 단계: `⚪ 상세기획→🔵 상세설계→🟡 상세구현→🟢 상세검증→✅ 상세완료`. **⛔ 번호 고정**: 단계 바뀌어도 dXXXX 불변, rename만. 범위: `0001~0999` 공통 / `1000~9999` 상세.



> 예시·금지 패턴: `references/guide.md §3`, `references/workflow-detail.md §3`



---



## 4. 워크플로우



| 명령 | 동작 요약 |

|------|---------|

| `new` | 템플릿 선택(공통/fastapi/streamlit) → 저장 → `ooplan sync` |

| `next` | 파일 없으면 기획 생성 / 있으면 단계 감지 → rename → 연계 스킬 실행 |

| `needed` | plan.md Feature ↔ 상세 문서 교차 비교 → 미착수 출력 |

| `note` | 파일 탐색 → Read → 섹션 판단 → Edit → 이력 기록 |

| `list` | SP 스캔 → 문서번호/기능명/단계 테이블 + 집계 |

| `issue` | `## 이슈` 섹션 추가/해결 (🔴/✅) |



> ⚠️ 설계→구현 전환 직후 즉시 `oodev run dXXXX` 실행 필수 — 건너뛰면 TDD 사이클 누락

> 단계별 상세 워크플로우: `references/guide.md §4`, `references/workflow-detail.md §4` 참조



---



## 5. 상세기획 문서 표준 구조



| 구분 | 파일 | 사용 조건 |

|------|------|---------|

| 공통 | `templates/상세기획_template.md` | 기본값 |

| Streamlit | `templates/상세기획_template_streamlit.md` | `--framework streamlit` / SP04 자동 감지 |

| FastAPI | `templates/상세기획_template_fastapi.md` | `--framework fastapi` / SP05 자동 감지 |



단계 전환 시 공통 추가 섹션: `설계→## A` / `구현→## B` / `검증→## C` / `완료→## D`



> 템플릿 상세 구조: `references/workflow-detail.md §5` 참조



---



## 6. 서브에이전트



| 단계 | 에이전트 / 모델 | 역할 | 병렬 |

|------|----------------|------|:----:|

| 문서 생성·plan.md 갱신 | task-executor / sonnet | 템플릿 기반 작성·8.2절 업데이트 | - |

| 스캔/분석 | Explore / haiku | 상세 문서 탐색 | - |



---



## 7. 프레임워크 레퍼런스 / 관련 문서



| 프레임워크 | 감지 조건 | 참조 |

|-----------|----------|------|

| FastAPI | `from fastapi import` 또는 `main.py`+`routers/` | `fast-api/` |

| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` |



연동 스킬: `ooplan`(plan.md 8.2절) · `oodev run dXXXX` · `oocheck run dXXXX` · `d{SP}0002_plan.md` 8.2절 테이블. 템플릿은 §5 표 참조.



<!-- RUN-UPDATE-REF:START -->



## run과 update 분리 원칙



> `.claude/guides/run_update_separation.md` 준수. `run`=일회성 배치 실행 / `update`=상태·설정 현행화(멱등). `run`이 `update`를 자동 호출하지 않음.



<!-- RUN-UPDATE-REF:END -->



<!-- KARPATHY-REF:START -->



## Karpathy 코딩 가이드라인 (필수 준수)



> 이 스킬은 코딩 작업 수행 시 `.claude/rules/karpathy-guidelines.md`의 4원칙(Think Before Coding · Simplicity First · Surgical Changes · Goal-Driven Execution)을 준수한다. 속도보다 신중함.



<!-- KARPATHY-REF:END -->



<!-- GEMMA-REF:START -->



## Gemma 위임 (로컬 LLM)



> 단순/반복 작업(번역·요약·분류·Rephrase·포맷 변환)은 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰 절감. 위임 기준은 `.claude/guides/gemma_delegation.md`, 실행은 `uv run python .claude/skills/gemma/scripts/gemma_run.py`, 서버 미가동 시 Claude 본체로 폴백.



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

