# Streamlit 페이지 표준 패턴

## 페이지 기본 골격

```python
import streamlit as st
from oais.auth import check_login_status
from oais.ui import display_user_info_header

# [1] 페이지 설정
st.set_page_config(page_title="페이지명 - 백오피스", layout="wide")

# [2] 로그인 체크 (미로그인 시 자동 리다이렉트)
check_login_status()

# [3] 헤더
display_user_info_header()
st.title("페이지 제목")

# [4] 본문
```

## 패턴 A: 메트릭 + 필터 + 데이터 그리드

```python
# 메트릭 카드
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체", f"{total}건")
col2.metric("활성", f"{active}건")
col3.metric("오늘 수집", f"{today}건")
col4.metric("오류", f"{errors}건", delta=f"{delta}건", delta_color="inverse")

st.divider()

# 필터
fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
with fcol1:
    search = st.text_input("키워드 검색", placeholder="제목, 내용 검색")
with fcol2:
    filter_type = st.selectbox("타입", ["전체", "타입A", "타입B"])
with fcol3:
    filter_date = st.date_input("날짜")

# 데이터 로드 및 표시
df = _load_data(search=search, filter_type=filter_type)
st.dataframe(df, use_container_width=True, hide_index=True)
```

## 패턴 B: 탭 기반 레이아웃

```python
tab_list, tab_add, tab_stats, tab_help = st.tabs(["목록", "추가", "통계", "도움말"])

with tab_list:
    # 데이터 그리드
    ...

with tab_add:
    # 추가 폼
    ...

with tab_stats:
    # 차트/통계
    ...
```

## 패턴 C: CRUD 폼

```python
# 목록 표시
df = _safe_df("SELECT id, name, status FROM table ORDER BY id DESC")
st.dataframe(df, use_container_width=True)

# 수정/삭제 행 선택
selected_id = st.selectbox("수정할 항목", df["id"].tolist())
row = _safe_df(f"SELECT * FROM table WHERE id = {selected_id}").iloc[0]

# 편집 폼
with st.form("edit_form"):
    name = st.text_input("이름", value=str(row["name"]))
    status = st.selectbox("상태", ["활성", "비활성"],
                          index=0 if row["status"] == "활성" else 1)

    col_save, col_del = st.columns(2)
    with col_save:
        if st.form_submit_button("저장", type="primary"):
            _execute("UPDATE table SET name=?, status=? WHERE id=?",
                     [name, status, selected_id])
            st.success("저장됨")
            st.rerun()
    with col_del:
        if st.form_submit_button("삭제", type="secondary"):
            _execute("DELETE FROM table WHERE id=?", [selected_id])
            st.warning("삭제됨")
            st.rerun()
```

## 패턴 D: 권한 체크

```python
from oais.auth import require_admin_permission, require_developer_or_admin_permission
from oais import session

# 관리자만 접근 가능
require_admin_permission()   # 미충족 시 st.error() + st.stop()

# 개발자 또는 관리자
require_developer_or_admin_permission()

# 조건부 UI 표시
if session.get_user_grade() in ("관리자", "개발자"):
    st.button("관리자 전용 버튼")
```

## 패턴 E: DB 헬퍼 함수 (페이지 내 정의)

```python
import sqlite3
from config import get_config

def _get_conn():
    return sqlite3.connect(get_config().DB_PATH)

def _safe_df(sql: str, params: list | None = None) -> pd.DataFrame:
    """쿼리 실패 시 빈 DataFrame 반환"""
    try:
        conn = _get_conn()
        df = pd.read_sql_query(sql, conn, params=params or [])
        conn.close()
        return df
    except Exception as e:
        st.warning(f"DB 조회 오류: {e}")
        return pd.DataFrame()

def _execute(sql: str, params: list | None = None) -> bool:
    """INSERT/UPDATE/DELETE 실행"""
    try:
        conn = _get_conn()
        conn.execute(sql, params or [])
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"DB 오류: {e}")
        return False
```

## 패턴 F: 섹션 허브 페이지 (=== 페이지)

```python
# 1_10_대시보드===.py
import streamlit as st
from oais.auth import check_login_status
from oais.ui import display_user_info_header

st.set_page_config(page_title="대시보드 - 백오피스", layout="wide")
check_login_status()
display_user_info_header()

st.title("대시보드")
st.info("왼쪽 메뉴에서 항목을 선택하세요.")

# 하위 메뉴 카드 안내
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("데이터소스관리")
    st.write("외부 API 연결 상태 확인")
with col2:
    st.subheader("통계대시보드")
    st.write("수집/활용 통계 시각화")
with col3:
    st.subheader("배치관리")
    st.write("스케줄 및 실행 이력")
```
