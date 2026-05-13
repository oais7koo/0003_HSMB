---
name: ootodo
description: "TODO 자동 처리 스킬 'ootodo', 'TODO 관리', '할 일 추가', '할 일 처리' 등을 요청할 때 사용한다"
metadata:
  version: "v13"
  category: "doc-env"
---

# ootodo - Todo 자동 처리 스킬

> 공통 가이드: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d{SP}0004_todo.md "대기 ToDo" 섹션 관리 및 할 일 자동 처리 |
| **하는 것** | Todo 추가·즉시처리·일괄처리·상태조회·아카이브 |
| **하지 않는 것** | 코드 에러 이슈 처리(→oofix), 이슈 발견(→oocheck), 이력 아카이브(→oohistory) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `d{SP}0004_todo.md` (대기 ToDo 섹션만), `d{SP}0010_history.md` |
| **실행 레벨** | [반자동] — 코딩 작업은 oodev 위임, 비코딩 작업은 직접 처리 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v13 2026-04-19 — audit/reopen/history 서브명령어 추가 (완료 항목 검증·아카이브·대기 복원)
- v12 2026-04-19 — validate → check 통합
- v02 2026-04-17 — `ootodo update` 서브명령어 추가 — todo 문서 현행화 기능
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 개요

d{SP}0004_todo.md 문서의 "대기 ToDo" 섹션을 관리하고, 업무를 자동으로 처리한다.

**핵심 기능**:
1. **추가+즉시처리**: `ootodo "내용"` -> 추가 후 바로 처리
2. **일괄 처리**: `ootodo` -> 대기 중 업무 전체 처리
3. **추가만**: `ootodo add "내용"` -> 추가만 하고 나중에 처리
4. **상태 조회**: `ootodo status` -> 대기 목록 표시
5. **아카이브**: `ootodo clear` -> 완료 항목을 d0010_history.md로 이동

**옵션**: `--sp N` (서브프로젝트)

### ootodo vs oofix 역할 구분

- **ootodo**: d0004의 "대기 ToDo" 섹션을 관리. 사용자가 직접 추가한 할 일을 처리하며, 코딩(oodev 위임)과 비코딩(문서, 분석 등 직접 처리) 모두 대응하는 **범용 할 일 관리자**.
- **oofix**: d0004의 "현재 이슈 (Active Issues)" 섹션을 관리. oocheck가 발견한 코드 에러(S/T/W 이슈)를 서브에이전트 병렬로 자동 수정하는 **코드 이슈 전문 수정기**.
- **공통점**: 둘 다 d0004_todo.md를 읽고, 완료 시 d0010_history.md에 기록.
- **차이점**: 다루는 섹션(대기 ToDo vs 현재 이슈), 작업 범위(범용 vs 코드 전용), 처리 방식(단순 위임 vs 3단계 병렬 분석/수정/검증)이 다름.

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootodo help` | 서브명령어 목록 표시 |
| `ootodo version` | 스킬 버전 정보 (v09) |
| `ootodo "내용"` | **추가 + 즉시 처리** (권장) |
| `ootodo` | 대기 중 업무 전체 처리 |
| `ootodo list` | **전체 서브프로젝트 대기 업무 리스트업** |
| `ootodo status` | 서브명령어 리스트, 대기 목록 표시 |
| `ootodo check --checklist` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ootodo run` | TODO 처리 실행 |
| **`ootodo run this`** | **직전 작업 TODO 처리** (→ common_guide.md §9) |
| `ootodo show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ootodo add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ootodo add [text]` | 할 일 추가만 (처리 안함) |
| `ootodo complete [ID]` | 대기 항목 → 완료 ToDo 섹션으로 이동 (완료일 자동 기록) |
| `ootodo clear` | 완료 항목 -> d0010_history.md 아카이브 |
| **`ootodo check`** | **등록 이슈 타당성 검토 — 전문 에이전트가 유효성·우선순위·중복 분석 후 의견 제시** (구 `validate`) |
| `ootodo check --sp N` | 특정 SP의 이슈만 검토 |
| `ootodo check --fix` | 검토 결과 기반으로 d{SP}0004 자동 보정 (우선순위 조정·중복 병합) |
| **`ootodo update`** | **d{SP}0004_todo.md 현행화** — 완료 항목 상태 갱신·문서이력 버전 업데이트·우선순위 재정렬 |
| `ootodo update --message "msg"` | 이력 변경 내용 직접 지정 |
| `ootodo update --no-sort` | 우선순위 재정렬 생략 |
| `ootodo update --dry-run` | 변경사항 미리보기 (파일 수정 안함) |
| **`ootodo audit`** | **완료 항목 검증** — 완료 ToDo 항목별 검증 지침 출력 후 `history`/`reopen`으로 판정 |
| `ootodo audit --sp N` | 특정 SP의 완료 항목만 검증 |
| `ootodo history [ID]` | 완료 항목을 d0010에 단건 아카이브 + d0004에서 제거 |
| `ootodo reopen [ID] "메모"` | 완료 항목을 대기 ToDo로 복원 + 재개 메모 추가 |

실행: `uv run python .claude/skills/ootodo/scripts/ootodo_run.py [args]`

## 2.5 블록 포맷 (표준)

> 코드 예시: references/guide.md §5 참조

**규칙**:
- 헤더(`####`)와 내용 사이 **빈 줄 없음** (내용이 없으면 다음 `####` 바로 이어짐)
- 블록 간 **빈 줄 1개** 유지
- `ootodo add` → 대기 블록 생성, `ootodo complete [ID]` → 완료일 자동 기록 후 완료 섹션으로 이동

## 3. list 워크플로우 (전체 대기 업무 리스트업)

### 3.0 `ootodo list`

모든 서브프로젝트의 todo 파일을 스캔하여 대기 중인 업무를 통합 표시한다.

**스캔 대상**: `00_doc/d{SP}0004_todo.md` (SP00~SP05)

**추출 섹션**:
1. "대기 ToDo" 섹션의 ### C 블록 (섹션 기반 형식)
2. "대기 ToDo" 섹션의 T/A/S/W 접두사 블록

**출력 형식**: 코드 예시: references/guide.md §8.6 참조

**규칙**:
- 내용은 50자로 요약 (초과 시 `...` 처리)
- 우선순위 높은 순 정렬 (high/Must > medium/Should > low/Could)
- 대기 항목 0건인 SP는 표에서 제외
- `--sp N` 옵션 사용 시 해당 SP만 표시

## 4. 자동 처리 워크플로우

### 4.1 추가+즉시처리 (`ootodo "내용"`)

> 코드 예시: references/guide.md §8.1 참조

### 4.2 일괄 처리 (`ootodo`)

> 코드 예시: references/guide.md §8.2 참조

### 4.3 스킬 라우팅 룰셋

> **원칙**: 키워드 매칭 → 가장 특정적인 스킬 우선. 복수 매칭 시 첫 번째 행 우선.

| 우선순위 | 키워드/패턴 | 위임 스킬 | 실행 형식 |
|:-------:|------------|----------|----------|
| 1 | PRD, 요구사항, 기획서 | `ooprd` | `ooprd run` |
| 2 | plan, 계획, WBS, 스프린트, Feature | `ooplan` | `ooplan run` |
| 3 | 상세기획, 상세설계, 기능 문서, d{N}1001 | `oofeature` | `oofeature next dXXXX` |
| 4 | 구현, 개발, 코딩, TDD, 함수, 클래스, API | `oodev` | `oodev run dXXXX` |
| 5 | 버그, 오류, 수정, fix, 에러 | `oofix` | `oofix run` |
| 6 | 테스트, TC, 검증, pytest | `ootest` | `ootest run` |
| 7 | 코드 체크, 품질, pylint, lint | `oocheck` | `oocheck run` |
| 8 | 문서, oodoc, d0001~d0010 | `oodoc` | `oodoc run` |
| 9 | 환경, 패키지, uv, 라이브러리 | `oouv` / `ooenv` | `oouv add` / `ooenv run` |
| 10 | 커밋, git, 이력 | `oocommit` | `oocommit run` |
| 11 | 논문, 스크래핑, 크롤링, 유튜브 | `oopaper` / `ooscrap` | 해당 스킬 `run` |
| 12 | (키워드 미매칭) | 직접 처리 | AI가 내용 보고 판단 |

**스킬 실행 전 확인 사항**:
- `dXXXX` 가 필요한 스킬(oofeature, oodev, oocheck)은 todo 내용에서 문서번호 추출 시도
- 추출 실패 시 사용자에게 문서번호 질문 또는 `oofeature needed`로 파악

### 4.4 비코딩 작업 처리 규칙

| 작업 유형 | 처리 방법 |
|----------|----------|
| 문서 작성/수정 | 해당 문서 읽기 → 내용 추가/수정 → 저장 |
| 설명 추가 | 대상 섹션 확인 → 상세 설명 작성 → 삽입 |
| 분석/검토 | 대상 읽기 → 분석 결과 정리 → 문서화 |
| 정리/구조화 | 현재 상태 확인 → 재구성 → 업데이트 |

### 4.5 상태 전이

> 코드 예시: references/guide.md §8.3 참조

### 4.5.1 check 워크플로우 (`ootodo check`)

> **목적**: 등록된 이슈가 여전히 유효하고 올바르게 분류되었는지 전문 에이전트가 검토

> 코드 예시: references/guide.md §8.4 참조

**검토 항목**:

| 검토 차원 | 내용 | 담당 에이전트 |
|----------|------|-------------|
| 유효성 | 이슈가 실제 코드에서 여전히 존재하는가 | Explore + python-code-reviewer |
| 우선순위 적절성 | CRITICAL/ERROR/WARNING/INFO 분류가 맞는가 | ooqa |
| 중복 감지 | 동일하거나 유사한 이슈가 이미 등록되어 있는가 | ooqa |
| 해결 가능성 | 이슈 설명이 충분하여 수정이 가능한가 | ooqa |
| 이미 해결 여부 | d0010_history.md에 동일 이슈가 해결 기록으로 있는가 | Explore |

**출력 형식**: 코드 예시: references/guide.md §8.4 참조

**권장 액션 종류**:

| 아이콘 | 의미 |
|--------|------|
| ✅ 유지 | 이슈 유효, 현행 유지 |
| 🗑 삭제 | 이미 해결되었거나 무효 |
| ↑ / ↓ | 우선순위 상향/하향 |
| 🔀 병합 | 중복 이슈 통합 |
| ✏ 보완 | 설명 보강 필요 |

`--fix` 옵션: 권장 액션을 사용자 확인 후 d{SP}0004에 자동 반영

---

### 4.6 todo 문서 현행화 (`ootodo update`)

> **목적**: 현재 세션 작업 내역을 d{SP}0004_todo.md에 반영하여 문서를 최신 상태로 유지

> 코드 예시: references/guide.md §8.5 참조

**옵션**:

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--message "msg"` | 이력 변경내용 직접 지정 (자동 생성 대신) | 자동 생성 |
| `--no-sort` | 우선순위 재정렬 생략 | false |
| `--dry-run` | 변경사항 미리보기 (파일 수정 안함) | false |
| `--sp N` | 특정 서브프로젝트만 현행화 | 현재 SP |

**oocommit sync와의 차이**:
- `ootodo update`: d{SP}0004 내부 현행화 (상태·이력·정렬) — **파일 저장만**
- `oocommit sync`: d{SP}0004 완료 항목 → d{SP}0010 이동 — **이력 이동 포함**
- 권장 순서: `ootodo update` → `oocommit run` (커밋 + sync 통합)

---

### 4.7 완료 항목 아카이브 (`ootodo clear`)

완료된 이슈를 d0010_history.md로 이동하여 d0004_todo.md를 정리한다.

**권장 주기**: 1~2주마다 실행

## 5. 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 서브프로젝트 지정 (d{SP}0004 사용) | 00 |
| `--priority [high\|medium\|low]` | 우선순위 지정 (add 시) | medium |
| `--note [text]` | 비고 추가 (add 시) | - |
| `--dry-run` | 실제 처리 없이 계획만 표시 | false |
| `--max-items N` | 최대 처리 항목 수 | 전체 |

## 6. 서브프로젝트 지원

| SP | Todo 문서 |
|:--:|----------|
| 00 | 00_doc/sp00/d0004_todo.md |
| 01 | 00_doc/sp01/d10004_todo.md |
| 02 | 00_doc/sp02/d20004_todo.md |
| 03 | 00_doc/sp03/d30004_todo.md |
| 04 | 00_doc/sp04/d40004_todo.md |
| 05 | 00_doc/sp05/d50004_todo.md |

## 7. 서브에이전트

> explore(haiku) 스캔 → task-executor(sonnet) 처리 → task-checker(sonnet) 검증 순서로 위임할 것.

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 스캔 | Explore | haiku | 관련 파일 탐색 | O |
| 처리 | task-executor | sonnet | Todo 항목 처리 | O |
| 검증 | task-checker | sonnet | 완료 검증 | - |
| **check: 코드 스캔** | **Explore** | **haiku** | **이슈 관련 코드 현재 상태 탐색** | **O** |
| **check: 품질 분석** | **ooqa** | **sonnet** | **중복·우선순위·해결가능성 분석** | **O** |
| **check: 코드 검증** | **python-code-reviewer** | **sonnet** | **코드 이슈 유효성 확인** | **O** |
| **check: 보정** | **task-executor** | **sonnet** | **--fix 옵션 시 d{SP}0004 자동 반영** | **-** |

> **관련 문서**: `.claude/skills/ootodo/references/guide.md` | `.claude/skills/ootodo/templates/ootodo_template.md` | `.claude/skills/oodev/SKILL.md` | `.claude/skills/oohistory/SKILL.md` | `00_doc/d{SP}0004_todo.md` 외

> **관련 명령어**: `.claude/commands/sc/task.md` | `.claude/commands/sc/implement.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

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

