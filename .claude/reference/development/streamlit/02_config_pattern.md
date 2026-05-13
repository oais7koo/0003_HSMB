# Streamlit 설정 패턴

## 구조

```python
# 04_backoffice/config.py
from oais.base_config import BaseConfig

class Config(BaseConfig):
    PROJECT_NAME = "백오피스"
    SERVER_ROOT = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BaseConfig.PROJECT_ROOT, "db", "silver.sqlite")

    def __init__(self):
        self.config_file = os.path.join(self.SERVER_ROOT, "config.json")
        super().__init__()

    def _detect_environment(self) -> str:
        """포트 기반 환경 자동 감지"""
        if self.current_port == 8501:
            return "development"
        return "production"  # 8022 또는 기타

    def _load_config(self) -> dict:
        config = super()._load_config()

        env_configs = {
            "development": {
                "auto_login_enabled": os.getenv("DEV_AUTO_LOGIN", "false").lower() == "true",
                "auto_login_user": os.getenv("DEV_USER_ID", "admin"),
                "auto_login_password": os.getenv("DEV_USER_PASSWORD", ""),
                "show_test_data": True,
                "server_name": os.getenv("DEV_SERVER_NAME", "백오피스 (개발)"),
            },
            "production": {
                "auto_login_enabled": False,   # 운영은 자동 로그인 금지
                "show_test_data": False,
                "server_name": os.getenv("PROD_SERVER_NAME", "백오피스"),
            },
        }

        config.update(env_configs.get(self.environment, env_configs["production"]))

        # config.json 최종 오버라이드 (최우선)
        if os.path.exists(self.config_file):
            with open(self.config_file, encoding="utf-8") as f:
                file_cfg = json.load(f)
                if self.environment in file_cfg:
                    config.update(file_cfg[self.environment])

        return config


# 싱글톤
_config_instance = None

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
```

## 우선순위 (낮음 → 높음)

```
BaseConfig 기본값
    ↓
Config 클래스 환경변수 (DEV_* / PROD_*)
    ↓
config.json 파일 (개발 로컬 오버라이드)
```

## .env 설정 예시

```bash
# 개발
APP_ENVIRONMENT=development
DEV_AUTO_LOGIN=true
DEV_USER_ID=admin
DEV_USER_PASSWORD=q1w2e3r4@@
DEV_SHOW_TEST_DATA=true

# API 키
YOUTUBE_API_KEY=your-key
DATA_GO_KR_SENURI_KEY=your-key
OPENAI_API_KEY=your-key
```

## 페이지에서 설정 사용

```python
from config import get_config

cfg = get_config()

# 환경 확인
if cfg.environment == "development":
    st.write("개발 환경")

# 자동 로그인 여부
if cfg.should_auto_login():
    ...

# DB 경로
db_path = cfg.DB_PATH
```
