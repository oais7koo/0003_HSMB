# FastAPI DB 스키마 + Pydantic 모델

## DB 초기화 패턴 (database.py)

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "api.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")      # 동시성 개선
    conn.execute("PRAGMA busy_timeout=5000")      # 락 대기 5초
    return conn

def init_api_tables():
    """앱 시작 시 테이블 생성 (없으면 생성, 있으면 무시)"""
    conn = get_db_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
```

## 핵심 테이블 3개

### 1. 작업 큐 (task_queue)

```sql
CREATE TABLE IF NOT EXISTS api_task_queue (
    task_id          TEXT PRIMARY KEY,        -- UUID
    identifier       TEXT NOT NULL,           -- 외부 시스템 요청 ID
    task_type        TEXT NOT NULL,           -- 업무 유형
    status           TEXT DEFAULT 'pending',  -- pending→processing→done/failed
    priority         TEXT DEFAULT 'normal',   -- high, normal
    params           TEXT,                    -- JSON (추가 파라미터)
    input_file_path  TEXT,                    -- 입력 파일 경로
    output_file_path TEXT,                    -- 결과 파일 경로
    retry_count      INTEGER DEFAULT 0,       -- 인프라 재시도 횟수
    error_message    TEXT,                    -- 실패 사유
    created_at       TEXT NOT NULL,           -- ISO 8601
    started_at       TEXT,                    -- 처리 시작
    completed_at     TEXT                     -- 완료/실패
);

CREATE INDEX IF NOT EXISTS idx_tq_status ON api_task_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_tq_priority ON api_task_queue(priority, status);
CREATE INDEX IF NOT EXISTS idx_tq_identifier ON api_task_queue(identifier);
```

### 2. 처리 결과 (task_result)

```sql
CREATE TABLE IF NOT EXISTS api_task_result (
    task_id          TEXT PRIMARY KEY,
    result_json      TEXT,                    -- 처리 결과 데이터 (JSON)
    output_filename  TEXT,                    -- 결과 파일명
    scp_status       TEXT DEFAULT 'pending',  -- pending/sent/failed/not_required
    scp_sent_at      TEXT                     -- SCP 전송 시각
);
```

### 3. 요청 로그 (request_log)

```sql
CREATE TABLE IF NOT EXISTS api_request_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    method          TEXT,
    path            TEXT,
    status_code     INTEGER,
    elapsed_ms      REAL,
    client_ip       TEXT,
    apl_id          TEXT,
    request_params  TEXT,                    -- JSON
    error_detail    TEXT,                    -- JSON
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rl_created ON api_request_log(created_at);
CREATE INDEX IF NOT EXISTS idx_rl_status ON api_request_log(status_code);
```

## 상태 전이

```
pending → processing → done
                    → file_generated → done (SCP 전송 후)
                    → failed (비즈니스 에러, 재시도 안함)
         ← pending (인프라 에러, retry_count < 3)
                    → failed (retry_count >= 3)
```

## Pydantic 스키마 (schemas.py)

```python
from pydantic import BaseModel
from typing import Optional, Any

class TaskCreateResponse(BaseModel):
    task_id: str
    identifier: str
    task_type: str
    status: str
    created_at: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    result: Optional[Any] = None

class ErrorResponse(BaseModel):
    error: str          # 에러 코드 (INVALID_FILE 등)
    message: str        # 사용자 메시지 (한국어)
    detail: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
```

## 마이그레이션 패턴

```python
def _migrate_add_column(conn, table, column, col_type, default=None):
    """컬럼 없으면 추가 (ALTER TABLE)"""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    if column not in columns:
        default_clause = f"DEFAULT '{default}'" if default else ""
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} {default_clause}")
```
