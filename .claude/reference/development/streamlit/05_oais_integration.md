# oais 모듈 연동

> SP04에서 사용하는 oais 공용 모듈 목록과 패턴.

## 모듈 목록

| 모듈 | 주요 함수 | 용도 |
|------|---------|------|
| `oais.auth` | `authenticate_user()`, `check_login_status()`, `hash_password()`, `verify_password()` | 인증 (bcrypt) |
| `oais.session` | `init_session()`, `get_user_id()`, `get_user_grade()`, `get_company_name()` | 세션 SSOT |
| `oais.ui` | `display_user_info_header()`, `render_user_info_bar()`, `safe_switch_page()` | UI 컴포넌트 |
| `oais.db` | `get_db_connection()`, `exec_cud_query()`, `exec_r_query()`, `table2df()` | DB 접근 |
| `oais.user` | `get_user_companies()` | 사용자 업체 조회 |
| `oais.community` | `get_posts()`, `BOARD_TYPE_EMOJI`, `BOARD_TYPE_LABELS` | 게시판 |
| `oais.batch` | `init_scheduler()`, `start_scheduler()` | 배치 스케줄러 |
| `oais.news_crawl` | `get_active_sites()`, `run_news_pipeline()` | 뉴스 수집 |
| `oais.district_loader` | `resolve_district()` | 행정구역 |
| `oais.job_loader` | `save_job_api_fields()` | 일자리 API |
| `oais.thumbnail` | `ThumbnailGenerator` | 썸네일 생성 |
| `oais.base_config` | `BaseConfig` | 기본 설정 클래스 |

## DB 연결 패턴

### 방법 1: oais.db 모듈 (권장)

```python
from oais.db import get_db_connection
import pandas as pd

conn = get_db_connection()
try:
    df = pd.read_sql_query("SELECT * FROM table WHERE id = ?", conn, params=[id])
finally:
    conn.close()
```

### 방법 2: sqlite3 직접 (페이지 내 헬퍼)

```python
import sqlite3
from config import get_config

def _get_conn():
    conn = sqlite3.connect(get_config().DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _safe_df(sql: str, params: list | None = None) -> pd.DataFrame:
    try:
        conn = _get_conn()
        df = pd.read_sql_query(sql, conn, params=params or [])
        conn.close()
        return df
    except Exception as e:
        st.warning(f"DB 오류: {e}")
        return pd.DataFrame()
```

## 인증/세션 패턴

```python
from oais.auth import check_login_status, require_admin_permission
from oais import session

# 페이지 진입 시 (필수)
check_login_status()  # 미로그인 → login.py 리다이렉트

# 관리자만 허용
require_admin_permission()  # 미충족 → st.error() + st.stop()

# 세션 정보 조회
user_id = session.get_user_id()
user_grade = session.get_user_grade()    # "관리자" | "개발자" | "사용자"
company = session.get_company_name()
```

## 헤더 컴포넌트

```python
from oais.ui import display_user_info_header

display_user_info_header()
# → 👤 ID | 👨 이름 | 🏢 회사 | 👥 팀 | 📱 연락처 | 👤 등급 [새로고침] [로그아웃]
```

## 배치 스케줄러

```python
from oais.batch import init_scheduler, start_scheduler, add_job

# 앱 시작 시 1회 초기화
if "scheduler_started" not in st.session_state:
    init_scheduler()
    start_scheduler()
    st.session_state["scheduler_started"] = True

# 작업 등록 (cron 방식)
add_job(func=crawl_news, trigger="cron", hour=6, minute=0, id="news_daily")
```
