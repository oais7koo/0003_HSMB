# Streamlit 앱 구조

## 디렉토리 구조

```
04_backoffice/
├── login.py                    # 메인 진입점 (로그인 페이지)
├── config.py                   # 백오피스 설정 관리
├── cert.pem / key.pem          # SSL 인증서 (HTTPS 운영용)
└── pages/                      # Streamlit 자동 네비게이션 폴더
    ├── 0_02_게시판.py
    ├── 1_10_대시보드===.py      # === 접미사 = 섹션 허브
    ├── 1_11_데이터소스관리.py
    ├── 2_20_일간수집===.py
    ├── 2_21_오늘의핫이슈.py
    ├── 2_22_뉴스수집.py
    │   ...
    ├── _news_collection/        # 서브패키지 (대형 페이지 분리)
    │   ├── __init__.py
    │   ├── _constants.py
    │   ├── db.py
    │   ├── render_manage.py
    │   ├── render_settings.py
    │   └── render_stats.py
    └── youtube_collector.py     # 공용 수집 모듈
```

## 파일명 규칙

```
{섹션번호}_{페이지번호}_{페이지명}.py
```

| 섹션 | 번호 | 내용 |
|------|------|------|
| 게시판 | 0 | 커뮤니티 |
| 대시보드 | 1 | 통계, 배치관리 |
| 일간수집 | 2 | 뉴스, 유튜브, 일자리 |
| 월간수집 | 3 | 병원, 약국, 행정구역 |
| 앱관리 | 4 | 사용자, 공지, 이벤트 |
| API모니터링 | 5 | 상태, 로그, 에러 |
| 개발가이드 | 8 | 개발 문서 |
| 설정 | 9 | 시스템, 사용자관리 |

> `===` 접미사: 섹션 허브 페이지 — 하위 메뉴 안내만 표시, 기능 없음

## 진입점 (login.py) 구조

```python
import streamlit as st
from config import get_config
from oais.auth import authenticate_user, check_login_status
from oais.ui import display_user_info_header

# [1] 페이지 설정
st.set_page_config(
    page_title="백오피스 - 로그인",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# [2] 세션 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# [3] 개발 모드 자동 로그인
cfg = get_config()
if cfg.should_auto_login():
    creds = cfg.get_auto_login_credentials()
    authenticate_user(creds["user"], creds["password"])

# [4] 로그인 분기
if not st.session_state.logged_in:
    # 로그인 폼 렌더링
    with st.form("login_form"):
        user_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        if st.form_submit_button("로그인"):
            authenticate_user(user_id, password)
            st.rerun()
else:
    # 로그인 후 안내 페이지
    display_user_info_header()
    tab_news, tab_intro, tab_help = st.tabs(["새소식", "시스템 안내", "도움말"])

# [5] 배치 스케줄러 자동 시작
if "scheduler_started" not in st.session_state:
    try:
        from oais.batch import init_scheduler, start_scheduler
        init_scheduler()
        start_scheduler()
        st.session_state["scheduler_started"] = True
    except Exception as e:
        st.session_state["scheduler_error"] = str(e)
```

## 실행 방법

```bash
# 개발 (포트 8501)
uv run streamlit run 04_backoffice/login.py

# 운영 (포트 8022)
uv run streamlit run 04_backoffice/login.py --server.port 8022

# HTTPS
uv run streamlit run 04_backoffice/login.py \
  --server.port 8022 \
  --server.sslKeyPath=04_backoffice/key.pem \
  --server.sslCertPath=04_backoffice/cert.pem
```
