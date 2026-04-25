---
name: oofeature
description: "기능별 상세 문서(상세기획/설계/구현/검증/완료) 생성·단계 전환·현황 관리 스킬. 'oofeature', '상세기획', '상세설계', '상세구현', '상세검증', '상세완료', '기능 문서', '상세기획 필요' 등의 키워드로 트리거된다"
model: opus
metadata:
  version: v20
  category: core-dev
---

> 공통 가이드: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md
> 연동: ooplan (plan.md 8.2절) | oodev (상세 문서 기반 개발) | oocheck (검증)

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 기능별 상세 문서를 기획→설계→구현→검증→완료 5단계로 생명주기 관리 |
| **하는 것** | 상세기획/설계/구현/검증/완료 문서 생성, 파일명 rename으로 단계 전환, 미착수 Feature 리스트업 |
| **하지 않는 것** | 코드 구현(→oodev), 테스트 실행(→ootest), 코드 체크(→oocheck) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (`00_doc/sp{N}/dXXXX_*.md`) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/dXXXX_상세*.md` (파일명 rename 포함) |
| **실행 레벨** | [반자동] — 단계 전환 전 현재 단계 확인 후 실행 |
| **에이전트 호환** | Claude Code 권장 — Agent 도구로 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

## 문서 이력 관리
- v21 2026-04-21 — §A 상세설계 표준 구조 추가 — A.1 구현 코드 구조·파일 위치 테이블 필수화 (workflow-detail.md §5.5)
- v20 2026-04-19 — §3 번호 고정 원칙 명시 — 단계 전환 시 문서번호 불변, 파일명 rename만 허용 (에이전트 오해 방지)
- v19 2026-04-19 — validate → check 통합
- v17 2026-04-18 — rmdup 서브명령어 추가 — 같은 번호 복수 단계 파일 정리 (`oofeature_rmdup.py`)
- v16 2026-04-16 — 설계→구현 전환 필수 체크리스트 추가 — `oodev run dXXXX` 건너뜀 방지 경고 (§4.2)
- v15 2026-04-14 — 상세완료 단계 추가 — 검증 후 명시적 완료 단계 (파일명: `_상세완료_`, 이모지: ✅)
- v14 2026-04-14 — Streamlit 템플릿 추가 — `상세기획_template_streamlit.md` (SP04 백오피스 전용, RBAC 탭 패턴 포함)
- v13 2026-04-14 — 템플릿 다원화 — 공통(상세기획_template.md) + 기술스펙별(fastapi) 구조 가이드 §5 추가, `--framework` 옵션 문서화
- v12 2026-04-14 — §3.4 번호 부여 규칙 추가 — 상세 문서 1000번대~, 천단위 카테고리, 십단위 세부 번호
- v11 2026-04-10 — issue 추가 — 상세 문서 ## 이슈 섹션에 이슈 추가/해결 (🔴 미해결 / ✅ 해결)
- v10 2026-04-08 — note 추가 — 상세 문서에 메모 추가 (타임스탬프 + ## 메모 섹션 자동 생성)
- v09 2026-04-08 — update 단순화 — 인자 없이 자동 감지 → 상세기획 롤백 (--apply/--force/--dry)
- v08 2026-04-08 — update --from-doc 강화 — 구현 단계 문서 변경 감지 → oocheck 자동 실행 → 이슈 발견 시 기획 단계 롤백 제안
- v07 2026-04-08 — update --from-doc 추가 — 상세 문서 내용 변경 감지 → 기획 단계 자동 롤백

---

## 1. 개요

> ⚠️ **필수**: next/run 명령 시 반드시 Agent 도구로
> executor(opus) 상세 문서 읽기 및 생성 순서로 위임할 것.
> 상세 문서 직접 읽기 금지 — 메인 컨텍스트 보호.

기능별 상세 문서를 **기획 → 설계 → 구현 → 검증 → 완료** 5단계로 관리하는 스킬.

**핵심 원칙**: 단계가 파일명에 포함됨 → 파일명만 보면 현재 단계 즉시 파악 가능.

> **⚠️ 이슈 우선 원칙**: 모든 작업 전 대상 상세 문서(dXXXX)를 확인하여 미해결 이슈(TODO, FIXME, 검증 실패 항목 등)가 있으면 **해당 이슈 해결에 집중**한다. 새 기능 진행보다 기존 이슈 해소가 우선이다.

> **⚠️ 단계별 수정 범위 원칙 (Stage-Scoped Edit Rule)**: 현재 파일명 단계에 해당하는 섹션만 수정한다. 다른 단계의 섹션을 미리 작성하거나 수정하는 것은 금지. `next`로 단계를 올린 후 해당 섹션을 작성할 것.
>
> | 현재 단계 | 수정 허용 섹션 | 금지 섹션 |
> |----------|--------------|---------|
> | ⚪ 기획 (`_상세기획_`) | §1~§8 (개요·요구사항·UI·제약·이슈) | §A §B §C §D |
> | 🔵 설계 (`_상세설계_`) | §A (아키텍처·DB·API 설계) | §B §C §D |
> | 🟡 구현 (`_상세구현_`) | §B (Task 체크리스트·구현 노트) | §C §D |
> | 🟢 검증 (`_상세검증_`) | §C (검증 결과·TC 통과 현황) | §D |
> | ✅ 완료 (`_상세완료_`) | §D (완료 확인·서명) | — |
>
> **예외**: 어느 단계에서도 §8 이슈 섹션(`## 8. 이슈`)에 이슈 추가/해결은 허용.
> **롤백 시**: 롤백 목적 단계의 섹션만 수정. 예) 완료→기획 롤백 시 §1~§8만 수정, §A 수정은 설계 단계에서.

```
d41001_상세기획_데이터수집소스.md   ← 기획 단계
d41001_상세설계_데이터수집소스.md   ← 설계 단계 (파일 rename)
d41001_상세구현_데이터수집소스.md   ← 구현 단계 (파일 rename)
d41001_상세검증_데이터수집소스.md   ← 검증 단계 (파일 rename)
d41001_상세완료_데이터수집소스.md   ← 완료 단계 (파일 rename)
```

**연동**:
- `ooplan sync` → plan.md 8.2절 자동 갱신 (상세 파일 스캔)
- `oodev run dXXXX` → 상세 문서 기반 구현 실행 (설계→구현 단계전환 자동 포함)
- `oocheck run dXXXX` → 상세 문서 기반 검증 실행 (구현→검증 단계전환 자동 포함)

**표준 개발 플로우** (Feature 1개 기준):
```
oofeature next dXXXX           # 상세기획 생성 (파일 없으면 자동 생성, plan.md 기능명 조회)
oofeature next dXXXX           # 기획→설계 (의도적 게이트, 설계 작성)
oofeature next dXXXX           # 설계→구현 전환 + oodev run 자동 연계 (TC/코딩)
oofeature next dXXXX           # 구현→검증 전환 + oocheck run 자동 연계 (코드 체크)
[oofix run]                    # 이슈 수정 (필요시)
```

---

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `oofeature help` | 서브명령어 목록 표시 | 터미널 |
| `oofeature version` | 스킬 버전 정보 (v08) | 터미널 |
| `oofeature status` | 서브명령어 리스트, 현재 SP 상세 문서 현황 | 터미널 |
| `oofeature new dXXXX "기능명"` | 상세기획 문서 생성 | `dXXXX_상세기획_기능명.md` |
| `oofeature new dXXXX "기능명" --stage 설계` | 특정 단계로 생성 | `dXXXX_상세설계_기능명.md` |
| `oofeature next dXXXX` | 다음 단계로 파일명 변경 + 연계 스킬 실행 | 파일 rename |
| **`oofeature next this`** | **직전 작업 상세 문서 다음 단계** (→ common_guide.md §9) | 파일 rename |
| `oofeature stage dXXXX 단계` | 단계 수동 변경 (파일 rename만) | 파일 rename |
| `oofeature list` | 현재 SP 상세 문서 목록 + 단계 현황 | 터미널 |
| **`oofeature needed`** | **plan.md Feature 교차 비교 → 상세기획 미착수 Feature 리스트업** | 터미널 |
| `oofeature needed --sp N` | 특정 SP의 미착수 Feature 리스트업 | 터미널 |
| `oofeature sync` | plan.md 8.2절 강제 갱신 | plan.md |
| `oofeature update` | plan.md + 상세 문서 변경 자동 감지 → 상세기획 롤백 후보 표시 | 터미널 |
| `oofeature update --apply` | 변경 감지 → 상세기획 롤백 실행 | 파일 rename |
| `oofeature update --force` | `--apply` 와 동일 (별칭) | 파일 rename |
| `oofeature update --dry` | 롤백 미리보기 (실제 수정 안 함) | 터미널 |
| `oofeature update --from-plan` | (하위 호환) plan.md 변경 기반 이전 단계 롤백 | 터미널 |
| `oofeature update --from-doc` | (하위 호환) 상세구현 문서 변경 + oocheck 기반 롤백 | 터미널 |
| `oofeature note dXXXX "내용"` | 상세 문서 ## 메모 섹션에 날짜+내용 추가 | 파일 수정 |
| `oofeature note dXXXX "내용" --sp N` | 특정 SP 상세 문서에 메모 추가 | 파일 수정 |
| `oofeature issue dXXXX "이슈내용"` | 상세 문서 ## 이슈 섹션에 이슈 추가 (🔴 미해결) | 파일 수정 |
| `oofeature issue dXXXX "이슈내용" --sp N` | 특정 SP 상세 문서에 이슈 추가 | 파일 수정 |
| `oofeature issue dXXXX --resolve` | 최신 미해결 이슈 → ✅ 해결 처리 | 파일 수정 |
| `oofeature check` | 상세 문서 정합성 검증 (V01~V08) | 터미널 |
| `oofeature check --sp N` | 특정 SP 상세 문서 검증 | 터미널 |
| `oofeature check --verbose` | 상세 메시지 포함 출력 | 터미널 |
| `oofeature check --dry-run` | 검증 대상 목록만 출력 | 터미널 |
| `oofeature check --checklist` | references/checklist.md 기반 체크 | 터미널 |
| `oofeature rmdup [--sp N] [--all] [--dry-run]` | 같은 번호 복수 단계 파일 감지 → 최신 단계만 유지, 나머지 삭제 | 파일 삭제 |

실행(check): `uv run python .claude/skills/oofeature/scripts/oofeature_validate.py [--sp N] [--verbose] [--dry-run]`

---

## 3. 파일명 규칙

파일명 형식: `d{SP번호}{기능번호}_상세{단계}_{기능명}.md`

단계 순서: `⚪ 상세기획 → 🔵 상세설계 → 🟡 상세구현 → 🟢 상세검증 → ✅ 상세완료`

### ⛔ 번호 고정 원칙 (에이전트 필독)

**단계가 바뀌어도 문서번호(dXXXX)는 절대 변경하지 않는다. 파일명 rename만 허용.**

```
✅ 올바른 예 — 번호 d42230 고정, 단계 키워드만 변경:
  d42230_상세기획_기능명.md  →(rename)→
  d42230_상세설계_기능명.md  →(rename)→
  d42230_상세구현_기능명.md  →(rename)→
  d42230_상세검증_기능명.md  →(rename)→
  d42230_상세완료_기능명.md

❌ 잘못된 예 — 단계마다 새 번호 부여 (절대 금지):
  d42230_상세기획_기능명.md
  d42231_상세설계_기능명.md  ← 번호 변경 금지!
  d42232_상세구현_기능명.md  ← 번호 변경 금지!
```

번호 범위: `d{SP}0001~0999` 공통 문서 예약 / **`d{SP}1000~9999`** 상세 문서 전용 (천번대 카테고리, 10단위 세부)

> 상세: `.claude/skills/oofeature/references/workflow-detail.md §3` 참조

---

## 4. 워크플로우

### 4.1 new
템플릿 선택(공통/fastapi/streamlit) → `00_doc/sp{N}/dXXXX_상세기획_기능명.md` 저장 → `ooplan sync`

### 4.2 next
파일 없으면 상세기획 자동 생성 / 있으면 단계 감지 → 파일명 rename → 연계 스킬 실행 → `ooplan sync`

> **⚠️ 설계→구현 전환 필수**: rename 직후 즉시 `oodev run dXXXX` Skill 도구로 실행 — 건너뛰면 TDD 사이클 누락

### 4.3 needed
`plan.md` Feature 목록 추출 → 상세 문서 스캔 → 교차 비교 → 미착수 Feature 우선순위 순 출력

### 4.5 note
스크립트로 파일 탐색 → Read 툴로 문서 읽기 → 섹션 판단 → Edit 통합 → 메모 이력 기록

### 4.6 list
현재 SP 스캔 → 문서번호/기능명/단계/파일 테이블 출력 + 단계별 집계

### 4.7 issue
이슈 추가: `## 이슈` 섹션에 `🔴 미해결` 행 추가 / `--resolve`: 최신 미해결 → `✅ 해결` 변경

스크립트: `uv run python .claude/skills/oofeature/scripts/oofeature_issue.py`

> 상세 워크플로우: `.claude/skills/oofeature/references/workflow-detail.md §4` 참조

---

## 5. 상세기획 문서 표준 구조

| 구분 | 파일 | 사용 조건 |
|------|------|---------|
| 공통 | `templates/상세기획_template.md` | 기본값 |
| Streamlit | `templates/상세기획_template_streamlit.md` | `--framework streamlit` / SP04 자동 감지 |
| FastAPI | `templates/상세기획_template_fastapi.md` | `--framework fastapi` / SP05 자동 감지 |

단계 전환 시 공통 추가 섹션: `설계→## A` / `구현→## B` / `검증→## C` / `완료→## D`

> 템플릿 상세 구조: `.claude/skills/oofeature/references/workflow-detail.md §5` 참조

---

## 6. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 문서 생성 | task-executor | sonnet | 템플릿 기반 문서 작성 | - |
| 스캔/분석 | Explore | haiku | 상세 문서 탐색 | - |
| plan.md 갱신 | task-executor | sonnet | 8.2절 업데이트 | - |

---

## 7. 프레임워크 레퍼런스 참조

> 상세기획/설계 문서 작성 시, 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.claude/reference/development/{framework}/` 문서를 참조하여 설계 품질을 높인다.

| 프레임워크 | 감지 조건 | 참조 경로 | 설계 참조 항목 |
|-----------|----------|----------|--------------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | 라우터 설계, DB 스키마, 배치 패턴, 외부 연동 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 구조, UI 패턴 |

## 8. 관련 문서

| 문서/스킬 | 연동 내용 |
|----------|----------|
| `ooplan` | plan.md 8.2절 상세 문서 현황 갱신 |
| `oodev` | `oodev run dXXXX` — 상세 문서 기반 개발 |
| `oocheck` | `oocheck run dXXXX` — 상세 문서 기반 검증 |
| `d{SP}0002_plan.md` | 8.2절: 상세 문서 현황 테이블 |
| `templates/상세기획_template.md` | 공통 문서 생성 템플릿 (기본) |
| `templates/상세기획_template_streamlit.md` | Streamlit 전용 템플릿 (`--framework streamlit`, SP04 자동 감지) |
| `templates/상세기획_template_fastapi.md` | FastAPI 전용 문서 생성 템플릿 (`--framework fastapi`, SP05 자동 감지) |

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

