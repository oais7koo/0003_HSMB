# ootest Tutorial

> 통합 테스트 스킬 | 버전: v08 | 카테고리: core-dev

## 1. 이 스킬은 왜 필요한가?

통합 테스트 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ootest run

# 상태 확인
ootest status

# 도움말
ootest help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootest status` | 서브명령어 리스트, 현재 상태 |
| `ootest check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ootest run` | 테스트 실행 | 터미널 |
| `ootest update` | 현행화 — 현재 코드 스캔 → 테스트 케이스 문서 갱신 | d{SP}0003_test.md |
| `ootest update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| `ootest show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ootest add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| **write [ID]** | **TC 코드 생성 (TDD RED) + d{SP}0003 Part C 등록** |
| **write --all** | **미등록 TC 전체 코드 생성** |
| run | 전체 테스트 (Part D 재스캔 자동 선행) |
| **run this** | **직전 작업 파일 관련 TC 실행** (→ common_guide.md §9) |
| run --unit | Part C pytest (반복 루프 포함) |
| run --e2e | Part B 시나리오 |
| run --module | Part D oo 모듈 (재스캔 자동 선행) |
| run --runtime | Part E 런타임 검증 (import 테스트) |
| run [ID] | 특정 TC 실행 (실패 시 자동 재시도) |
| run [P0-P3] | 우선순위별 |
| preview | 계획 출력 |
| checklist [domain] | 요구사항 품질 체크리스트 생성 |
| **result** | **테스트 결과를 d{SP}0003 Part C 결과 테이블·요약에 기록** |

옵션: --screenshot --fail-fast --verbose --max-retries N

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | TDD RED 단계 — TC 코드 작성 및 테스트 반복 실행 (PASS까지) |
| **하는 것** | tests/ TC 파일 생성, d{SP}0003 Part C 등록, pytest 반복 실행 |
| **하지 않는 것** | 구현 코드 작성(→oodev/GREEN), 정적 분석(→oocheck), 이슈 수정(→oofix) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `tests/TC*.py`, `d{SP}0003_test.md` Part C |
| **실행 레벨** | [자동] — TC 작성 후 pytest 반복 실행 (PASS까지) |
| **에이전트 호환** | Claude Code 권장 — `uv run pytest` 직접 실행 / 다른 에이전트: pytest 명령을 수동 실행하거나 별도 터미널에서 실행 |

### 가이드

**통합 가이드**: .claude/skills/ootest/references/guide.md (방법론 How)

| 파트 | 내용 |
|------|------|
| 공통 | 우선순위/상태/에러분류 |
| A | 정적분석, 용어체크 |
| B | E2E/UI, Playwright |
| C | pytest, TDD |
| D | oo 모듈 전체 검증 |
| E | 런타임 검증 (import 테스트) - 필수 |

**Streamlit 프레임워크**: `pages/*.py` 존재 시 → `.claude/skills/ootest/references/streamlit_guide.md` 자동 참조

### 에이전트 매핑

| 유형 | 에이전트 | 모델 | 병렬 |
|------|----------|------|:----:|
| **TC 코드 생성 (RED)** | **test-engineer** | **sonnet** | **O** |
| Part A 정적 | python-code-reviewer | sonnet | O |
| Part A 품질 | ooqa | sonnet | O |
| Part B E2E | web-test-orchestrator | sonnet | - |
| Part C 단위 | task-executor | sonnet | - |
| Part D oo | task-executor | sonnet | - |
| Part E 런타임 | task-executor | sonnet | - |
| **result 기록** | **task-executor** | **sonnet** | **-** |

병렬: RED(test-engineer, run_in_background=true) | A(reviewer+qa) | B설계(qa+Explore, run_in_background=true)

### 컴팩트 생성 원칙 (--compact)

> `ootest run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

### 프레임워크 레퍼런스 참조

> 테스트 작성 시, 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 `.claude/reference/development/{framework}/` 문서를 참조하여 테스트 구조를 맞춘다.

| 프레임워크 | 감지 조건 | 참조 경로 | 테스트 참조 항목 |
|-----------|----------|----------|----------------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` | `fast-api/` | conftest fixture, TestClient, SFTP 서버, 테스트 분류 |
| Streamlit | `import streamlit` 또는 `pages/*.py` | `references/streamlit_guide.md` | 페이지 테스트 |

### 관련문서

ootest_guide.md(통합가이드) | oodev.md(TDD) | oocheck.md(Part A) | d{SP}0003(항목) | d{SP}0004(이슈)

> **관련 명령어**: `.claude/commands/sc/test.md` | `.claude/commands/sc/analyze.md`

## 5. 워크플로우

### 5.0 TDD RED (write)

**TC 코드 저장 경로**: `tests/TC[번호]_[모듈].py`

```
ootest write [ID]
    1. d{SP}0003 시나리오 로드 (Part B)
    2. test-engineer → TC 코드 생성 (pytest/playwright)
    3. tests/ 폴더에 저장 (TC[번호]_[모듈].py)
    4. 실행 → 반드시 실패 확인 (pass 시 TC 재작성)
    5. d{SP}0003 Part C 등록
    6. oodev에 GREEN 신호 전달
```

**tests/ 폴더 구조:**
```
tests/
├── sp00/                        # SP00 공통 테스트
│   ├── TC001-1.1_기능명.py
│   └── test_page_import.py
├── sp04/                        # SP04 전용 테스트
│   └── TC002-2.1_시나리오명.py
└── sp05/                        # SP05 전용 테스트
    └── TC003-3.1_시나리오명.py
```

> SP별 서브폴더 규칙: `tests/sp{SP번호}/` (2자리, 예: sp00, sp04)
> SP 미지정(공통) 테스트는 `tests/sp00/`에 저장

반복 루프 (run [ID]):
```
실행 → 실패 → 원인 분석 → oodev에 수정 요청 → 재실행
→ pass까지 반복 (최대 --max-retries N, 기본 5)
→ pass → d{SP}0003 상태 갱신 → COMPLETE
```

### 5.0.1 실행 정책

> **기본 원칙**: `ootest run`은 실서버 연결 테스트를 포함한 **모든 테스트를 실행**한다.
> - `--ignore` 없이 전체 실행이 기본값
> - 실서버 테스트(scp_real, E2E 등) 실패 시에도 나머지 테스트는 계속 실행
> - 실서버 미연결로 인한 실패는 결과 리포트에 별도 표기 (SKIP이 아닌 FAIL로 기록)
> - 특정 테스트만 제외하려면 명시적으로 `--exclude` 옵션 사용

### 5.1 전체 (run)
가이드->Part D 재스캔->Part A->B->C->D->E->d{SP}0003->d{SP}0004

### 5.2 단위 (--unit)
d{SP}0003 Part C->TC매칭->pytest->실패 시 반복 루프->상태갱신

TC규칙: TC[번호]_[모듈].py

### 5.3 E2E (--e2e)
d{SP}0003 Part B->Playwright->상태갱신->스크린샷(tmp/test_screenshots/)

### 5.4 oo 모듈 (--module)

목적: oo 모듈 기능 전체 검증. 대상: oo/*.py 전체 함수

```
1. oo/*.py 재스캔 -> d{SP}0003 Part D 목록 갱신
2. 모듈별 함수 추출 (11개 카테고리, 43개 모듈)
3. TC 존재 확인 -> 실행 -> 오류 발견
4. 실패 시 d{SP}0004에 MODULE_ERROR 등록
```

**카테고리:**
- Core (5): db, auth, session, admin, check_admin
- Config (2): base_config, config_helper
- Entity (5): user, company, agent, customer, community
- Task (5): task_core, task_query, task_attachment, task_mgmt, chuck_task
- Data (4): columns, sys_code, db_meta, data_processing
- Application (3): application, bizreg, bizreg_data
- File (5): file_ops, file_upload, file_manager, ocr, seal
- External (3): hyphen_api, news_api, services
- Document (4): pdf_parser, receipt_parser, card_processor, book_summary
- Utility (5): utils, date_utils, excel_utils, validation, financial
- UI (2): ui, mobile_css

커버리지: 전체 함수 80% | DB 함수 100% | 유틸리티 70%

### 5.5 런타임 검증 (Part E) - 필수

py_compile/pylint로 감지 불가능한 런타임 에러 검증

| 에러 유형 | 원인 | Part E 감지 |
|----------|------|:-----------:|
| StreamlitDuplicateElementKey | 위젯 key 중복 | O |
| ImportError (조건부) | if문 내 import | O |
| AttributeError | 런타임 객체 접근 | O |
| TypeError | 런타임 타입 불일치 | O |

```bash
ootest run --runtime       # Part E만 실행
uv run pytest tests/test_page_import.py -v
```

### 5.6 checklist (요구사항 품질 검증)

체크리스트는 "요구사항을 위한 유닛테스트" - 구현이 아닌 요구사항 자체의 품질 검증

**검증 차원**:

| 차원 | 검증 내용 |
|------|----------|
| 완전성 | 필요한 모든 요구사항이 문서화되었는가? |
| 명확성 | 요구사항이 구체적이고 모호하지 않은가? |
| 일관성 | 요구사항 간 충돌이 없는가? |
| 측정가능성 | 성공 기준이 객관적으로 검증 가능한가? |
| 커버리지 | 모든 흐름/케이스가 정의되었는가? |

**도메인별 체크리스트**:

| 도메인 | 파일명 | 주요 검증 항목 |
|--------|--------|---------------|
| ux | ux.md | 시각 계층, 상호작용 상태, 접근성 |
| api | api.md | 에러 응답, 인증, 버저닝 |
| performance | performance.md | 성능 지표, 부하 조건 |
| security | security.md | 인증/인가, 데이터 보호, 위협 모델 |

**체크리스트 항목 형식**:
```markdown
- [ ] CHK001 - [영역별] 요구사항 품질 질문? [품질차원, Spec N.M]
```

**워크플로우**:
```
ootest checklist [domain]
    |
    |-> 1. 문서 로드 (d{SP}0001, d{SP}0002, d{SP}0003)
    |-> 2. 도메인 분석 (키워드 추출, 위험 지표 식별)
    |-> 3. 체크리스트 생성 (00_doc/checklists/[domain].md)
    |-> 4. 리포트 출력
```

```bash
ootest checklist ux           # UX 요구사항 품질 체크리스트
ootest checklist api          # API 요구사항 품질 체크리스트
ootest checklist security     # 보안 요구사항 품질 체크리스트
ootest checklist              # 대화형으로 도메인 선택
```

### 5.7 result (최종 테스트 결과 기록)

```
ootest result
    1. 현재 SP의 d{SP}0003_test.md 로드
    2. pytest 결과 파싱 (가장 최근 실행 결과 또는 재실행)
    3. Part C "최종 테스트 결과" 테이블 갱신
       - 결과: ✅ PASS / ❌ FAIL / ⏭ SKIP
       - 실패 원인: pytest 에러 메시지 요약 (첫 줄)
       - 최종 실행일: 오늘 날짜
    4. "최종 결과 요약" 테이블 갱신 (Part별 집계)
    5. 갱신 내용 출력
```

**결과 테이블 형식** (Part C 하단):

```markdown
| TC ID | 기능명 | 결과 | 실패 원인 | 최종 실행일 |
|-------|--------|:----:|----------|:----------:|
| TC002-1.1 | 보건복지부탭 | ✅ PASS | - | 2026-04-06 |
| TC002-1.2 | 환경부탭 | ❌ FAIL | KeyError: 'tab_id' (test_tab.py:42) | 2026-04-06 |
| TC003-2.1 | 데이터수집 | ⏭ SKIP | real_server 마커 — 네트워크 필요 | 2026-04-06 |
```

**요약 테이블 갱신 규칙**:
- PASS: pytest `passed` 카운트
- FAIL: pytest `failed` 카운트 (실패 원인 첫 줄 추출)
- SKIP: `skipped` 카운트 (마커/조건 명시)

---

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ootest run
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

(서브에이전트 정보 없음)

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
