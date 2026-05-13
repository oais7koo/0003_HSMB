# ootest Streamlit 프레임워크 참조 가이드

## 문서 이력 관리
- v01 2026-03-01 — 초기 생성 (oostreamlit Phase 6 통합)

---

> 이 파일은 Streamlit 프레임워크 감지 시 ootest가 자동 참조하는 가이드입니다.
> 범용 테스트 가이드: `.claude/skills/ootest/references/guide.md`

## 1. Streamlit 검증 특화

### 1.1 검증 워크플로우

```
코드 리뷰 → 품질 분석 → 에러 체크 → E2E 테스트 → 완료 검증
```

### 1.2 TDD 사이클 (Streamlit 특화)

| 단계 | 내용 | Streamlit 특화 |
|------|------|--------------|
| Part A | 정적 분석 | python-code-reviewer + ooqa 병렬 |
| Part B | E2E/UI | oo-web-test-orchestrator (Playwright) |
| Part C | 단위 테스트 | pytest - oo 모듈 연동 확인 |
| Part E | 런타임 검증 | `test_page_import.py` import 테스트 **필수** |

---

## 2. 서브에이전트 검증 패턴

### 2.1 코드 리뷰 (Part A - 병렬)

```
Task(subagent_type="python-code-reviewer",
  prompt="Streamlit 페이지 코드 리뷰: oo 모듈 활용 여부, 패턴 준수,
  세션 상태 관리, 가독성, try-except 금지 규칙 준수 확인")
```

```
Task(subagent_type="ooqa",
  prompt="품질 분석: 중복 코드 검출, oo 모듈 기능 중복 구현 여부,
  순환 참조, DuplicateElementKey, 복잡도 측정")
```

```
Task(subagent_type="code-error-checker",
  prompt="에러 체크: import 오류, 런타임 에러, 타입 불일치,
  Streamlit API 오용 감지")
```

### 2.2 E2E 테스트 (Part B - 순차)

```
Task(subagent_type="oo-web-test-orchestrator",
  prompt="E2E 테스트 수행:
  1. 페이지 로딩 확인
  2. 사이드바 필터 동작 확인
  3. 데이터 표시 정확성
  4. CRUD 기능 (등록/수정/삭제) 동작
  5. 오류 메시지 처리
  6. 스크린샷 저장 (tmp/test_screenshots/)")
```

### 2.3 완료 검증 (Part E)

```
Task(subagent_type="task-checker",
  prompt="완료 검증:
  - 설계 문서(섹션 4) 요구사항 충족 여부
  - UI 설계(와이어프레임) 반영 여부
  - 데이터 연동 완료 여부
  - oo 모듈 활용 계획 이행 여부
  - 코드 품질 기준 충족 여부")
```

---

## 3. 병렬 검증 실행 패턴

```python
# 1단계: 병렬 실행 (상호 독립)
Task(subagent_type="ooqa", ...)           # 품질 분석
Task(subagent_type="python-code-reviewer", ...)  # 코드 리뷰
Task(subagent_type="code-error-checker", ...)    # 에러 체크

# 2단계: 1단계 완료 후 실행
Task(subagent_type="oo-web-test-orchestrator", ...)  # E2E
Task(subagent_type="task-checker", ...)                # 완료 검증
```

---

## 4. Streamlit 런타임 검증 (Part E) - 필수

### 4.1 import 테스트

```python
# tests/test_page_import.py
import importlib
import pytest

PAGES = [
    "pages.10_10_페이지명",
    "pages.20_20_다른페이지",
]

@pytest.mark.parametrize("page_module", PAGES)
def test_page_imports(page_module):
    """모든 페이지가 import 오류 없이 로드되는지 검증"""
    module = importlib.import_module(page_module)
    assert module is not None
```

실행:
```bash
uv run pytest tests/test_page_import.py -v
```

### 4.2 DuplicateElementKey 감지

Streamlit 위젯에 동일한 `key` 값이 중복 사용되면 런타임 오류 발생.

```bash
# 중복 key 탐지
grep -r 'key="[^"]*"' pages/ | awk -F'key="' '{print $2}' | sort | uniq -d
```

### 4.3 E2E 렌더링 테스트 (Playwright) — 정적 분석 보완 필수

> **목적**: pylint/mypy로 잡을 수 없는 Streamlit API 런타임 오용 감지
> 예: `st.data_editor(column_options=...)` — 렌더링 시에만 TypeError 발생
> import 테스트는 권한 체크 조기 종료로 실제 렌더링 경로에 미도달 → E2E 필수

**전제 조건**:

| 항목 | 명령 / 설정 |
|------|------------|
| Playwright 설치 | `uv add playwright && playwright install chromium` (v1.57.0+) |
| 서버 실행 | `run02_poc_dev.bat` → localhost:8001 |
| 관리자 계정 | `.env` → `TEST_USER_ID` / `TEST_USER_PASSWORD` |

**실행**:

```bash
uv run pytest tests/sp02/e2e/ -v              # 전체 E2E
uv run pytest tests/sp02/e2e/ -v -k 권한관리  # 특정 페이지
```

**import 테스트 vs E2E 비교**:

| 오류 유형 | import 테스트 | E2E 렌더링 |
|----------|:-----------:|:----------:|
| `st.*` 잘못된 파라미터 (`column_options` 등) | ✗ | ✅ |
| 권한 체크 뒤 코드의 UnboundLocalError | ✗ | ✅ |
| 위젯 key 중복 (DuplicateElementKey) | △ | ✅ |
| 렌더링 경로의 AttributeError / TypeError | ✗ | ✅ |
| module-level 구문 오류 | ✅ | ✅ |

**테스트 구조**: `tests/sp02/e2e/test_pages_render.py`
- 페이지 접속 후 `[data-testid="stException"]` 감지 → FAIL
- 서버 미실행 시 자동 SKIP (connection 체크)
- 새 페이지 추가 시 `_PAGES` 리스트에 `(label, url_path)` 추가

### 4.4 감지 가능 런타임 에러 종합

| 에러 유형 | 원인 | import 테스트 | E2E |
|----------|------|:-----------:|:---:|
| StreamlitDuplicateElementKey | 위젯 key 중복 | △ | ✅ |
| ImportError (조건부) | if문 내 import | O | ✅ |
| AttributeError | 런타임 객체 접근 | ✗ | ✅ |
| TypeError (API 오용) | st.* 잘못된 파라미터 | ✗ | ✅ |
| ModuleNotFoundError | 누락된 패키지 | O | ✅ |

---

## 5. 검증 결과 기록

### 5.1 개발서 섹션 6 업데이트

```markdown
### 6.1 코드 리뷰 결과
- python-code-reviewer: [통과/이슈 N건]
- 주요 발견사항: ...

### 6.2 품질 분석 결과
- ooqa: [통과/이슈 N건]
- DuplicateKey: 없음/있음

### 6.3 E2E 테스트 결과
- 페이지 로딩: [통과/실패]
- CRUD 기능: [통과/실패]
- 스크린샷: tmp/test_screenshots/페이지명_*.png

### 6.4 완료 검증
- 요구사항 충족: [O/X]
- 설계 반영: [O/X]
- 최종 품질 점수: N/10
```

### 5.2 문서 연동

| 문서 | 기록 내용 |
|------|----------|
| 개발서 섹션 6 | 검증 체크리스트 결과 상세 |
| d{SP}0003_test.md | 테스트 결과 요약, 시나리오별 통과/실패 |
| d{SP}0004_todo.md | 검증 중 발견된 이슈 등록 |
| d{SP}0010_history.md | 구현 완료 이력 기록 |

---

## 6. Streamlit 코드 리뷰 출력 형식

```
STREAMLIT 코드 리뷰 보고서
─────────────────────────────
치명적 문제 (즉시 수정 필요)
  - [없음 / 상세 내용]

Session State 이슈
  - [없음 / 상세 내용]

캐싱 최적화
  - [없음 / 상세 내용]

잘된 점
  - [내용]

요약: 전체 품질 점수 N/10
```

---

## 7. 페이지 완료 체크리스트

### Part A: 플랜
- [ ] PRD 페이지 기획 분석 완료
- [ ] 필요 모듈/데이터 식별 완료
- [ ] 구현 계획서(개발서 섹션 3) 작성 완료

### Part B: 설계
- [ ] 레이아웃 와이어프레임 작성 (개발서 섹션 4.1)
- [ ] 컴포넌트 매핑 완료 (개발서 섹션 4.2)
- [ ] DB 스키마 설계 완료 (개발서 섹션 4.3)
- [ ] 상호작용 흐름 정의 (개발서 섹션 4.4~4.5)

### Part C: 구현
- [ ] 페이지 기본 구조 완성
- [ ] 사이드바 필터/검색 구현
- [ ] 메인 영역 기능 구현
- [ ] 데이터 연동 완료
- [ ] oo 모듈 활용 확인
- [ ] try-except 구문 없음
- [ ] 세션 상태 상단 초기화
- [ ] 상태 변경 후 st.rerun() 호출

### Part D: 검증
- [ ] 코드 리뷰 통과 (python-code-reviewer)
- [ ] 품질 분석 통과 (ooqa)
- [ ] 에러 체크 통과 (code-error-checker)
- [ ] import 테스트 통과 (test_page_import.py)
- [ ] DuplicateElementKey 없음
- [ ] E2E 테스트 통과 (oo-web-test-orchestrator)
- [ ] 완료 검증 통과 (task-checker)
- [ ] 검증 결과 문서화 완료

---

## 8. 관련 문서

| 문서 | 역할 |
|------|------|
| `ootest/references/guide.md` | 범용 테스트 가이드 |
| `ooplan/references/streamlit_guide.md` | 계획/설계 특화 가이드 |
| `oodev/references/streamlit_guide.md` | 구현 특화 가이드 |
| `oostreamlit/references/workflow.md` | 전체 6단계 워크플로우 원본 |
| `ootest/templates/test_page_import_template.py` | import 테스트 템플릿 |
