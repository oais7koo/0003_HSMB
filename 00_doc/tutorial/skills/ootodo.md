# ootodo Tutorial

> TODO 자동 처리 스킬 | 버전: v10 | 카테고리: doc-env

## 1. 이 스킬은 왜 필요한가?


**이런 상황에서 사용합니다:**
- **ootodo**: d0004의 "커스텀 Todo" 섹션을 관리. 사용자가 직접 추가한 할 일을 처리하며, 코딩(oodev 위임)과 비코딩(문서, 분석 등 직접 처리) 모두 대응하는 **범용 할 일 관리자**.
- **oofix**: d0004의 "현재 이슈 (Active Issues)" 섹션을 관리. oocheck가 발견한 코드 에러(S/T/W 이슈)를 서브에이전트 병렬로 자동 수정하는 **코드 이슈 전문 수정기**.
- **공통점**: 둘 다 d0004_todo.md를 읽고, 완료 시 d0010_history.md에 기록.
- **차이점**: 다루는 섹션(커스텀 Todo vs 현재 이슈), 작업 범위(범용 vs 코드 전용), 처리 방식(단순 위임 vs 3단계 병렬 분석/수정/검증)이 다름.

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ootodo run

# 상태 확인
ootodo status

# 도움말
ootodo help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootodo help` | 서브명령어 목록 표시 |
| `ootodo version` | 스킬 버전 정보 (v09) |
| `ootodo "내용"` | **추가 + 즉시 처리** (권장) |
| `ootodo` | 대기 중 업무 전체 처리 |
| `ootodo list` | **전체 서브프로젝트 대기 업무 리스트업** |
| `ootodo status` | 서브명령어 리스트, 대기 목록 표시 |
| `ootodo check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ootodo run` | TODO 처리 실행 |
| `ootodo update` | 현행화 — 현재 코드 스캔 → TODO 목록 갱신 | d{SP}0004_todo.md |
| `ootodo update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| **`ootodo run this`** | **직전 작업 TODO 처리** (→ common_guide.md §9) |
| `ootodo show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ootodo add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ootodo add [text]` | 할 일 추가만 (처리 안함) |
| `ootodo clear` | 완료 항목 -> d0010_history.md 아카이브 |
| **`ootodo validate`** | **등록 이슈 타당성 검토 — 전문 에이전트가 유효성·우선순위·중복 분석 후 의견 제시** |
| `ootodo validate --sp N` | 특정 SP의 이슈만 검토 |
| `ootodo validate --fix` | 검토 결과 기반으로 d{SP}0004 자동 보정 (우선순위 조정·중복 병합) |

실행: `uv run python .claude/skills/ootodo/scripts/ootodo_run.py [args]`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d{SP}0004_todo.md "커스텀 Todo" 섹션 관리 및 할 일 자동 처리 |
| **하는 것** | Todo 추가·즉시처리·일괄처리·상태조회·아카이브 |
| **하지 않는 것** | 코드 에러 이슈 처리(→oofix), 이슈 발견(→oocheck), 이력 아카이브(→oohistory) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `d{SP}0004_todo.md` (커스텀 Todo 섹션만), `d{SP}0010_history.md` |
| **실행 레벨** | [반자동] — 코딩 작업은 oodev 위임, 비코딩 작업은 직접 처리 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

### list 워크플로우 (전체 대기 업무 리스트업)

### 3.0 `ootodo list`

모든 서브프로젝트의 todo 파일을 스캔하여 대기 중인 업무를 통합 표시한다.

**스캔 대상**: `00_doc/d{SP}0004_todo.md` (SP00~SP05)

**추출 섹션**:
1. "커스텀 Todo > 대기 중" 테이블의 `대기` 상태 행
2. "현재 이슈 (Active Issues)" 테이블의 `대기` 상태 행

**출력 형식**:
```markdown
# ootodo list - 전체 대기 업무

| SP | ID | 우선순위 | 내용 (50자 요약) |
|:--:|-----|:-------:|-----------------|
| 00 | T001 | high | ... |
| 01 | I005 | Must | ... |
| 04 | T038 | 높음 | ... |
| 05 | T001 | medium | ... |

총 N건 대기 중 (SP00: X건, SP01: X건, ...)
```

**규칙**:
- 내용은 50자로 요약 (초과 시 `...` 처리)
- 우선순위 높은 순 정렬 (high/Must > medium/Should > low/Could)
- 대기 항목 0건인 SP는 표에서 제외
- `--sp N` 옵션 사용 시 해당 SP만 표시

### 자동 처리 워크플로우

### 4.1 추가+즉시처리 (`ootodo "내용"`)

```
ootodo "버그 수정" 실행
    -> d{SP}0004_todo.md "커스텀 Todo" 섹션에 추가
    -> 즉시 처리 지시 출력
    -> 에이전트가 해당 업무 처리
    -> 완료 시 "완료" 섹션으로 이동
```

### 4.2 일괄 처리 (`ootodo`)

```
ootodo 실행
    -> d{SP}0004_todo.md "커스텀 Todo" 섹션 읽기
    -> 대기 중 항목 없음? -> "처리할 업무가 없습니다" 출력 후 종료
    -> 대기 중 항목 있음:
        각 항목에 대해:
        1. 항목을 "진행 중"으로 이동
        2. oodev run 호출 (자동 처리)
        3. 완료 시 "완료" 섹션으로 이동
    -> 모든 항목 처리 완료까지 반복
```

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

```
[대기 중] -> [진행 중] -> [완료]
              (실패 시) -> [디버깅 섹션에 등록]
```

### 4.5.1 validate 워크플로우 (`ootodo validate`)

> **목적**: 등록된 이슈가 여전히 유효하고 올바르게 분류되었는지 전문 에이전트가 검토

```
ootodo validate
    1. d{SP}0004_todo.md 로드 (디버깅·커스텀 Todo 전체)
    2. Explore(haiku) — 관련 코드 현재 상태 스캔 (병렬)
    3. ooqa(sonnet) — 이슈 품질·중복·우선순위 분석 (병렬)
    4. python-code-reviewer(sonnet) — 코드 이슈 유효성 검증 (병렬)
    5. 이슈별 검토 의견 출력
    6. 권장 액션 제시
```

**검토 항목**:

| 검토 차원 | 내용 | 담당 에이전트 |
|----------|------|-------------|
| 유효성 | 이슈가 실제 코드에서 여전히 존재하는가 | Explore + python-code-reviewer |
| 우선순위 적절성 | CRITICAL/ERROR/WARNING/INFO 분류가 맞는가 | ooqa |
| 중복 감지 | 동일하거나 유사한 이슈가 이미 등록되어 있는가 | ooqa |
| 해결 가능성 | 이슈 설명이 충분하여 수정이 가능한가 | ooqa |
| 이미 해결 여부 | d0010_history.md에 동일 이슈가 해결 기록으로 있는가 | Explore |

**출력 형식**:

```markdown

### ootodo validate 결과 — sp{n} (2026-04-06)

| ID | 내용 요약 | 현재 우선순위 | 검토 의견 | 권장 액션 |
|----|---------|:----------:|---------|---------|
| T001 | datasets.py getitem 예외 | ERROR | 코드에서 이미 수정됨 (2026-03-18) | 🗑 삭제 |
| T002 | api.py 플랫폼 모킹 | WARNING | 유효. 우선순위 낮춤 권장 | ↓ INFO로 변경 |
| C001 | 논문 분석 품질 개선 | medium | 유사 항목 C003과 통합 가능 | 🔀 C003과 병합 |
| C005 | Flutter 넘버링 | medium | 유효. 현재 상태 확인 필요 | ✅ 유지 |

소계: 삭제 권장 1건 | 우선순위 조정 1건 | 병합 1건 | 유지 2건
```

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

### 4.6 완료 항목 아카이브 (`ootodo clear`)

완료된 이슈를 d0010_history.md로 이동하여 d0004_todo.md를 정리한다.

**권장 주기**: 1~2주마다 실행

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 서브프로젝트 지정 (d{SP}0004 사용) | 00 |
| `--priority [high\|medium\|low]` | 우선순위 지정 (add 시) | medium |
| `--note [text]` | 비고 추가 (add 시) | - |
| `--dry-run` | 실제 처리 없이 계획만 표시 | false |
| `--max-items N` | 최대 처리 항목 수 | 전체 |

### 서브프로젝트 지원

| SP | Todo 문서 |
|:--:|----------|
| 00 | 00_doc/sp00/d0004_todo.md |
| 01 | 00_doc/sp01/d10004_todo.md |
| 02 | 00_doc/sp02/d20004_todo.md |
| 03 | 00_doc/sp03/d30004_todo.md |
| 04 | 00_doc/sp04/d40004_todo.md |
| 05 | 00_doc/sp05/d50004_todo.md |

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ootodo run
```

### 서브명령어 활용
```bash
ootodo list  # **전체 서브프로젝트 대기 업무 리스트업**
ootodo run  # TODO 처리 실행
ootodo update  # 현행화 — 현재 코드 스캔 → TODO 목록 갱신
ootodo run this
ootodo clear  # 완료 항목 -> d0010_history.md 아카이브
```

### 옵션
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 서브프로젝트 지정 (d{SP}0004 사용) | 00 |
| `--priority [high\|medium\|low]` | 우선순위 지정 (add 시) | medium |
| `--note [text]` | 비고 추가 (add 시) | - |
| `--dry-run` | 실제 처리 없이 계획만 표시 | false |
| `--max-items N` | 최대 처리 항목 수 | 전체 |

### 스크립트 직접 실행
```bash
uv run python .claude/skills/ootodo/scripts/ootodo_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

> explore(haiku) 스캔 → task-executor(sonnet) 처리 → task-checker(sonnet) 검증 순서로 위임할 것.

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 스캔 | Explore | haiku | 관련 파일 탐색 | O |
| 처리 | task-executor | sonnet | Todo 항목 처리 | O |
| 검증 | task-checker | sonnet | 완료 검증 | - |
| **validate: 코드 스캔** | **Explore** | **haiku** | **이슈 관련 코드 현재 상태 탐색** | **O** |
| **validate: 품질 분석** | **ooqa** | **sonnet** | **중복·우선순위·해결가능성 분석** | **O** |
| **validate: 코드 검증** | **python-code-reviewer** | **sonnet** | **코드 이슈 유효성 확인** | **O** |
| **validate: 보정** | **task-executor** | **sonnet** | **--fix 옵션 시 d{SP}0004 자동 반영** | **-** |

> **관련 문서**: `.claude/skills/ootodo/references/guide.md` | `.claude/skills/ootodo/templates/ootodo_template.md` | `.claude/skills/oodev/SKILL.md` | `.claude/skills/oohistory/SKILL.md` | `00_doc/d{SP}0004_todo.md` 외

> **관련 명령어**: `.claude/commands/sc/task.md` | `.claude/commands/sc/implement.md`

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
