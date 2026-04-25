# FastAPI 테스트 구조

## 테스트 분류

| 분류 | 파일 패턴 | 대상 |
|------|----------|------|
| 엔드포인트 | `test_task_*.py`, `test_endpoint_*.py` | API 요청/응답 |
| 배치 처리 | `test_event_*.py`, `test_*_logic.py` | 배치 엔진, 핸들러 |
| 외부 연동 | `test_scp_*.py`, `test_spring_*.py` | SCP, 외부 DB |
| 인프라 | `test_rate_limit.py`, `test_env_*.py` | Rate Limit, 환경 |
| 관리자 | `test_admin.py` | 백오피스 UI |
| E2E | `ts{번호}_*.py` | 전체 흐름 테스트 |

## conftest.py — 핵심 Fixtures

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def test_db(tmp_path):
    """임시 SQLite DB"""
    db_path = tmp_path / "test_api.sqlite"
    # 테이블 초기화
    init_tables(str(db_path))
    yield str(db_path)
    # 자동 정리 (tmp_path)

@pytest.fixture
def client(test_db, monkeypatch):
    """FastAPI TestClient"""
    monkeypatch.setattr("models.database.DB_PATH", test_db)
    from main import app
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_pdf(tmp_path):
    """최소 유효 PDF 파일"""
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<< >>\nendobj\n%%EOF")
    return str(pdf)

@pytest.fixture
def sample_excel(tmp_path):
    """테스트용 Excel 파일"""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["col1", "col2"])
    ws.append(["data1", "data2"])
    path = tmp_path / "test.xlsx"
    wb.save(str(path))
    return str(path)

@pytest.fixture
def db_conn(test_db):
    """테스트 DB 연결"""
    import sqlite3
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
```

## SFTP 테스트 서버 (로컬)

```python
@pytest.fixture(scope="session")
def sftp_server():
    """로컬 SFTP 서버 (paramiko 기반)"""
    import paramiko
    import threading

    class StubSFTPServer(paramiko.SFTPServerInterface):
        ROOT = tempfile.mkdtemp()
        # ... stat, open, list_folder 구현

    server_thread = threading.Thread(target=_run_sftp_server, daemon=True)
    server_thread.start()
    yield {"host": "127.0.0.1", "port": 2222, "user": "test", "pass": "test"}
```

## 테스트 패턴

### 엔드포인트 테스트

```python
def test_create_task_with_file(client, sample_pdf):
    """파일 업로드로 작업 생성"""
    with open(sample_pdf, "rb") as f:
        response = client.post(
            "/api/v1/tasks/coupang-excel",
            data={"apl_id": "TEST-001"},
            files={"file": ("test.pdf", f, "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["task_type"] == "coupang_excel"

def test_create_task_no_input(client):
    """파일/경로 없이 요청 → 400"""
    response = client.post(
        "/api/v1/tasks/coupang-excel",
        data={"apl_id": "TEST-002"},
    )
    assert response.status_code == 400

def test_task_status(client, db_conn):
    """작업 상태 조회"""
    # 테스트 데이터 삽입
    db_conn.execute("INSERT INTO api_task_queue ...")
    db_conn.commit()

    response = client.get(f"/api/v1/tasks/{task_id}/status")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
```

### 배치 처리 테스트

```python
def test_priority_order(db_conn):
    """high 우선순위가 먼저 선점됨"""
    # normal 먼저 등록
    insert_task(db_conn, priority="normal", created_at="2026-01-01T00:00:00")
    # high 나중 등록
    insert_task(db_conn, priority="high", created_at="2026-01-01T00:01:00")

    task = claim_next_task("high")
    assert task is not None
    assert task["priority"] == "high"
```

### 외부 연동 테스트 (실서버)

```python
@pytest.mark.skipif(not os.getenv("SCP_HOST"), reason="SCP 환경 없음")
def test_scp_real_transfer():
    """실제 SCP 서버 전송 테스트"""
    result = scp_transfer("test_file.txt", "/remote/path/")
    assert result is True
```

## 실행 명령어

```bash
# 전체 테스트
uv run pytest 04_api_server/tests/ -v

# 특정 분류
uv run pytest 04_api_server/tests/test_task_create.py -v

# 실서버 포함
uv run pytest 04_api_server/tests/ -v --no-header

# 커버리지
uv run pytest 04_api_server/tests/ --cov=04_api_server --cov-report=term
```
