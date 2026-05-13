# 세션/인증 패턴

## 인증 흐름

```
login.py
  ↓ authenticate_user(id, pw)
    ↓ bcrypt 검증 (common_user 테이블)
    ↓ st.session_state["logged_in"] = True
    ↓ session_state에 사용자 정보 저장
  ↓ st.rerun()
pages/*.py
  ↓ check_login_status()  ← 모든 페이지 필수
    ↓ logged_in == False → login.py 리다이렉트
    ↓ logged_in == True  → 통과
```

## session_state 키 목록

| 키 | 타입 | 내용 |
|----|------|------|
| `logged_in` | bool | 로그인 여부 |
| `user_id` | str | 로그인 ID |
| `user_name` | str | 사용자명 |
| `user_grade` | str | 등급 ("관리자"\|"개발자"\|"사용자") |
| `company_name` | str | 소속 업체명 |
| `team_name` | str | 팀명 |
| `scheduler_started` | bool | 배치 스케줄러 시작 여부 |

## 인증 코드 패턴

```python
from oais.auth import authenticate_user, check_login_status

# 로그인 폼
with st.form("login"):
    user_id = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.form_submit_button("로그인"):
        success = authenticate_user(user_id, password)
        if success:
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 틀렸습니다.")
```

## 사용자 테이블 (common_user)

```sql
CREATE TABLE common_user (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    UNIQUE NOT NULL,      -- 로그인 ID
    password    TEXT    NOT NULL,             -- bcrypt 해시
    user_name   TEXT    NOT NULL,
    user_grade  TEXT    DEFAULT '사용자',     -- 관리자|개발자|사용자
    company_id  INTEGER,
    team_name   TEXT,
    phone       TEXT,
    is_active   INTEGER DEFAULT 1,
    created_at  DATETIME DEFAULT (datetime('now'))
);
```

## 비밀번호 해시

```python
import bcrypt

# 해싱 (저장 시)
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# 검증 (로그인 시)
ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
```

> **레거시 호환**: SHA256 해시 → bcrypt 자동 마이그레이션 (`oais.auth` 내부 처리)

## 권한 등급

| 등급 | 접근 범위 |
|------|----------|
| 관리자 | 전체 (사용자관리, 설정 포함) |
| 개발자 | 대부분 (사용자관리 제외 일부) |
| 사용자 | 일반 수집/조회 페이지만 |

## 개발 모드 자동 로그인

```python
# config.py
"auto_login_enabled": os.getenv("DEV_AUTO_LOGIN", "false").lower() == "true"

# login.py
if cfg.should_auto_login():
    creds = cfg.get_auto_login_credentials()
    authenticate_user(creds["user"], creds["password"])
```

> **운영 환경**: `auto_login_enabled = False` 강제 (포트 8022 자동 감지)
