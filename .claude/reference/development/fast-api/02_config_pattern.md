# FastAPI 설정 패턴

## 설정 클래스 구조

```python
class ApiServerConfig:
    # === 환경 ===
    ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "test")
    PORT = 8007

    # === 경로 ===
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(PROJECT_ROOT, "file", "input")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "file", "output")
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

    # === 배치 ===
    BATCH_POLL_INTERVAL = 10        # 폴링 간격 (초)
    BATCH_MAX_RETRY = 3             # 인프라 재시도 횟수
    BATCH_PROCESSING_TIMEOUT = 300  # 처리 타임아웃 (초)
    FILE_CLEANUP_DAYS = 7           # 파일 보관 기간

    # === 외부 연동 ===
    SCP_HOST = "..."
    SCP_PORT = 22
    SCP_TIMEOUT = 60

    # === Rate Limit ===
    RATE_LIMIT_PER_MINUTE = 60

    # === 업무 타입 ===
    ALLOWED_TASK_TYPES = [...]

    # === 우선순위 ===
    TASK_PRIORITY = {
        "type_a": "high",
        "type_b": "normal",
    }
```

## 환경별 설정 분기

```python
# 환경 변수 우선순위: {ENV}_{KEY} > {KEY} > 기본값
# 예: APP_ENVIRONMENT=dev → DEV_SCP_HOST 먼저, 없으면 SCP_HOST

@classmethod
def get_env(cls, key, default=None):
    env_key = f"{cls.ENVIRONMENT.upper()}_{key}"
    return os.getenv(env_key) or os.getenv(key) or default
```

## 환경 구분

| 환경 | APP_ENVIRONMENT | 용도 |
|------|----------------|------|
| test | `test` (기본) | 로컬 개발/테스트 |
| dev | `dev` | 개발 서버 |
| prod | `prod` | 운영 서버 |

## .env 파일 관리

```env
# .env (git 미추적)
APP_ENVIRONMENT=dev
SCP_USERNAME=user
SCP_PASSWORD=pass
SPRING_DB_PASSWORD=pass

# 환경별 오버라이드
DEV_SCP_HOST=192.168.1.100
PROD_SCP_HOST=172.30.1.63
```

## 튜닝 포인트

| 항목 | 기본값 | 고려사항 |
|------|--------|---------|
| BATCH_POLL_INTERVAL | 10초 | 작을수록 응답성 ↑, CPU ↑ |
| BATCH_MAX_RETRY | 3 | 높을수록 복원력 ↑, 처리시간 ↑ |
| BATCH_PROCESSING_TIMEOUT | 300초 | 길수록 대용량 처리 가능, 좀비 위험 ↑ |
| FILE_CLEANUP_DAYS | 7 | 길수록 저장공간 ↑ |
| RATE_LIMIT_PER_MINUTE | 60 | 낮을수록 보호 ↑, UX ↓ |
