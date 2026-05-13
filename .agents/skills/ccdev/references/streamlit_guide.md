# oodev Streamlit 프레임워크 참조 가이드

## 문서 이력 관리
- v01 2026-03-01 — 초기 생성 (oostreamlit Phase 5 통합)

---

> 이 파일은 Streamlit 프레임워크 감지 시 oodev가 자동 참조하는 가이드입니다.
> 범용 TDD 개발 가이드: `.claude/skills/oodev/references/guide.md`

## 1. Streamlit 페이지 구현 특화

### 1.1 구현 워크플로우

```
설계 문서 확인 → 필요한 oo 모듈 import → 페이지 기본 구조 작성
→ 사이드바 구현 → 메인 영역 구현 → 데이터 연동 → 상호작용 로직 → 테스트
```

### 1.2 TDD 사이클 (Streamlit 특화)

| 단계 | 내용 | Streamlit 특화 |
|------|------|--------------|
| RED | 테스트 작성 | `test_page_import.py`: import 테스트 |
| GREEN | 최소 구현 | 기본 구조 + 데이터 조회 |
| REFACTOR | 코드 개선 | oo 모듈 활용, 중복 제거 |
| VERIFY | 검증 | streamlit-code-reviewer, ooqa |

---

## 2. 페이지 기본 구조 템플릿

### 2.1 표준 페이지 구조

```python
import streamlit as st
from oo import ui, db, data_processing

# 1. 페이지 설정
ui.setup_page_config(page_title="페이지명")
ui.show_page_header("페이지 제목", "페이지 설명")

# 2. 세션 상태 초기화
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "list"  # list / add / edit

# 3. 사이드바
with st.sidebar:
    search_term = st.text_input("검색", placeholder="검색어 입력")
    filter_status = st.selectbox("상태", ["전체", "활성", "비활성"])
    filter_date = st.date_input("날짜 범위", value=[])

# 4. 데이터 조회
data = db.get_data(search_term, filter_status)

# 5. 메인 영역
if st.session_state.page_mode == "list":
    # 액션 버튼
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("등록"):
            st.session_state.page_mode = "add"
            st.rerun()

    # 데이터 표시
    st.dataframe(data, use_container_width=True)

elif st.session_state.page_mode == "add":
    # 등록 폼
    with st.form("add_form"):
        name = st.text_input("이름")
        submitted = st.form_submit_button("저장")
        if submitted:
            db.insert_data({"name": name})
            st.session_state.page_mode = "list"
            st.rerun()
```

### 2.2 CRUD 완성 패턴

```python
# 등록/수정 폼 (form 사용)
with st.form("crud_form"):
    col1, col2 = st.columns(2)
    with col1:
        field1 = st.text_input("항목1")
        field2 = st.selectbox("항목2", options)
    with col2:
        field3 = st.date_input("날짜")
        field4 = st.number_input("숫자", min_value=0)

    submitted = st.form_submit_button("저장")
    if submitted:
        db.save_data(...)
        st.success("저장 완료")
        st.rerun()

# 삭제 확인 (modal 대체)
if st.button("삭제"):
    st.session_state.confirm_delete = True

if st.session_state.get("confirm_delete"):
    st.warning("삭제하시겠습니까?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("확인"):
            db.delete_data(selected_id)
            st.session_state.confirm_delete = False
            st.rerun()
    with col2:
        if st.button("취소"):
            st.session_state.confirm_delete = False
            st.rerun()
```

### 2.3 대시보드/분석 패턴

```python
# KPI 메트릭
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("총 건수", f"{total:,}", f"+{delta}")
with col2:
    st.metric("완료율", f"{rate:.1f}%")

# 탭 분리
tab1, tab2, tab3 = st.tabs(["요약", "상세", "분석"])
with tab1:
    st.bar_chart(summary_data)
with tab2:
    st.dataframe(detail_data)
with tab3:
    st.line_chart(trend_data)
```

---

## 3. oo 모듈 활용 가이드

### 3.1 핵심 모듈 빠른 참조

| 모듈 | 함수 | 용도 | 예시 |
|------|------|------|------|
| `oo.ui` | `setup_page_config()` | 페이지 설정 | `ui.setup_page_config(page_title="홈")` |
| `oo.ui` | `show_page_header()` | 헤더 표시 | `ui.show_page_header("제목", "설명")` |
| `oo.db` | `get_connection()` | DB 연결 | `conn = db.get_connection()` |
| `oo.db` | `execute_query()` | 쿼리 실행 | `db.execute_query(sql, params)` |
| `oo.data_processing` | `filter_data()` | 데이터 필터링 | `filtered = data_processing.filter_data(df, conditions)` |
| `oo.validation` | `validate_input()` | 입력 검증 | `validation.validate_input(value, rules)` |
| `oo.date_utils` | `format_date()` | 날짜 포맷 | `date_utils.format_date(dt, "%Y-%m-%d")` |
| `oo.file_ops` | `read_file()` | 파일 읽기 | `file_ops.read_file(path)` |

### 3.2 oo 모듈 우선 원칙

1. **oo 모듈 우선**: 직접 구현 전 oo 모듈에 적합한 함수가 있는지 확인
2. **중복 금지**: oo 모듈 기능을 로컬에 재구현하지 않음
3. **확장 시**: oo 모듈에 없으면 oolib을 통해 추가 후 사용

---

## 4. 세션 상태 관리 패턴

### 4.1 초기화 패턴

```python
# 세션 상태 키 목록을 한 곳에서 관리
SESSION_DEFAULTS = {
    "page_mode": "list",       # list / add / edit / view
    "selected_id": None,       # 선택된 항목 ID
    "filter_reset": False,     # 필터 초기화 플래그
    "search_term": "",         # 검색어 유지
}

for key, default in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default
```

### 4.2 페이지 모드 전환

```python
# 모드 전환 후 반드시 st.rerun() 호출
def switch_mode(mode: str, item_id=None):
    st.session_state.page_mode = mode
    st.session_state.selected_id = item_id
    st.rerun()

# 사용
if st.button("수정"):
    switch_mode("edit", selected_id)
```

### 4.3 필터 상태 유지

```python
# 사이드바 필터값 세션으로 유지
with st.sidebar:
    search = st.text_input("검색", value=st.session_state.get("search_term", ""))
    st.session_state.search_term = search
```

---

## 5. Streamlit 구현 규칙

### 5.1 필수 규칙

| 규칙 | 내용 |
|------|------|
| try-except 금지 | 예외 처리 구문 사용 금지 (oo 모듈 내에서 처리) |
| oo 모듈 우선 | 직접 DB/파일 처리 전 oo 모듈 확인 |
| 세션 상태 명시 | 모든 세션 상태 키는 상단에서 초기화 |
| rerun 필수 | 상태 변경 후 반드시 st.rerun() 호출 |
| form 사용 | 입력 폼은 st.form()으로 묶어 일괄 제출 |

### 5.2 성능 최적화

```python
# 캐싱 적용 (DB 조회 등 무거운 연산)
@st.cache_data(ttl=300)  # 5분 캐시
def load_data(filter_key: str):
    return db.get_all_data(filter_key)

# 캐시 무효화 (데이터 변경 후)
st.cache_data.clear()
```

### 5.3 레이아웃 최적화

```python
# 컬럼 비율 활용
col1, col2 = st.columns([3, 1])  # 3:1 비율

# 빈 공간 처리
st.empty()  # 동적 콘텐츠 placeholder

# 컨테이너 활용
with st.container():
    # 그룹화된 콘텐츠
    pass
```

---

## 6. 테스트 패턴

### 6.1 import 테스트 (RED 단계)

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

### 6.2 DuplicateKey 감지

```python
# 같은 key 중복 사용 시 Streamlit 런타임 오류 발생
# 확인 방법:
# grep -r 'key="[^"]*"' pages/ | awk -F'key="' '{print $2}' | sort | uniq -d
```

### 6.3 서브에이전트 구현 호출

```
Task(
  subagent_type="streamlit-implementer",
  prompt="다음 페이지를 구현하라:
  파일: pages/{번호}_{페이지명}.py
  개발서: 00_doc/d{번호}_{페이지명}_단위개발.md (섹션 3.플랜, 4.설계 참조)

  구현 시 준수사항:
  1. oo 모듈 우선 사용 (oo.ui, oo.db, oo.data_processing)
  2. try-except 구문 사용 금지
  3. 기존 pages/ 패턴 참조 (일관성 유지)
  4. 세션 상태 상단에서 초기화
  5. 데이터 변경 후 st.rerun() 호출
  6. st.form()으로 입력 폼 감싸기"
)
```

---

## 7. 자주 발생하는 패턴

### 7.1 데이터 없음 처리

```python
data = db.get_data(filters)
if data.empty:
    st.info("데이터가 없습니다.")
    st.stop()

st.dataframe(data)
```

### 7.2 로딩 상태 표시

```python
with st.spinner("데이터 로딩 중..."):
    data = load_heavy_data()
```

### 7.3 사이드바 필터 → 데이터 연동

```python
# 사이드바에서 필터 수집
with st.sidebar:
    search = st.text_input("검색")
    status = st.selectbox("상태", ["전체", "활성", "비활성"])
    start_date, end_date = st.date_input("기간", value=[date.today() - timedelta(30), date.today()])

# 필터 조건으로 데이터 조회
filters = {
    "search": search,
    "status": None if status == "전체" else status,
    "start_date": start_date,
    "end_date": end_date,
}
data = db.get_filtered_data(**filters)
```

---

## 8. 관련 문서

| 문서 | 역할 |
|------|------|
| `oodev/references/guide.md` | 범용 TDD 개발 가이드 |
| `ooplan/references/streamlit_guide.md` | 계획/설계 특화 가이드 |
| `ootest/references/streamlit_guide.md` | 검증 특화 가이드 |
| `oostreamlit/references/workflow.md` | 전체 6단계 워크플로우 원본 |
| `oostreamlit/templates/streamlit-page.md` | 개발서 템플릿 |
