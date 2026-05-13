# FastAPI 외부 시스템 연동 패턴

## SCP/SFTP 파일 전송 (scp.py)

### 업로드

```python
import paramiko

def scp_transfer(local_path, remote_path=None):
    """로컬 파일 → 원격 서버 업로드"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=config.SCP_HOST,
            port=config.SCP_PORT,
            username=config.SCP_USERNAME,
            password=config.SCP_PASSWORD,
            timeout=config.SCP_TIMEOUT,
        )
        sftp = ssh.open_sftp()

        # 원격 디렉토리 재귀 생성
        remote_dir = os.path.dirname(remote_path)
        _mkdir_p(sftp, remote_dir)

        # 파일 전송
        sftp.put(local_path, remote_path)

        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        logger.error(f"SCP 업로드 실패: {e}")
        return False
```

### 다운로드

```python
def scp_download(remote_path, local_dir=None):
    """원격 파일 → 로컬 다운로드"""
    local_dir = local_dir or config.INPUT_DIR
    local_path = os.path.join(local_dir, os.path.basename(remote_path))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(...)
        sftp = ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        ssh.close()
        return local_path
    except Exception as e:
        logger.error(f"SCP 다운로드 실패: {e}")
        return None
```

### 디렉토리 재귀 생성

```python
def _mkdir_p(sftp, remote_dir):
    """원격 디렉토리 재귀 생성"""
    dirs = remote_dir.replace("\\", "/").split("/")
    current = ""
    for d in dirs:
        if not d:
            continue
        current += f"/{d}" if current else d
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)
```

## 외부 DB 연동 (spring_db.py)

### 연결

```python
import psycopg2

def get_external_db_connection():
    """외부 PostgreSQL 연결"""
    return psycopg2.connect(
        host=config.SPRING_DB_HOST,
        port=5432,
        dbname="external_db",
        user=os.getenv("SPRING_DB_USER"),
        password=os.getenv("SPRING_DB_PASSWORD"),
    )
```

### 상태 동기화 패턴

```python
def update_status_process(apl_id):
    """READY → PROCESS"""
    conn = get_external_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tn_svc_apl
                SET status_cd = 'PROCESS', upd_dt = NOW()
                WHERE apl_id = %s AND status_cd = 'READY'
            """, (apl_id,))
        conn.commit()
    finally:
        conn.close()

def update_status_success(apl_id, file_nm, file_path, file_size):
    """PROCESS → SUCCESS + 결과 파일 정보"""
    conn = get_external_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tn_svc_apl
                SET status_cd = 'SUCCESS',
                    rslt_file_nm = %s,
                    rslt_file_path = %s,
                    rslt_file_size = %s,
                    upd_dt = NOW()
                WHERE apl_id = %s AND status_cd = 'PROCESS'
            """, (file_nm, file_path, file_size, apl_id))
        conn.commit()
    finally:
        conn.close()

def update_status_fail(apl_id, error_msg):
    """PROCESS → FAIL"""
    conn = get_external_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tn_svc_apl
                SET status_cd = 'FAIL', err_msg = %s, upd_dt = NOW()
                WHERE apl_id = %s AND status_cd = 'PROCESS'
            """, (error_msg, apl_id))
        conn.commit()
    finally:
        conn.close()
```

## 외부 상태 전이

```
READY → PROCESS → SUCCESS (파일 정보 포함)
                → FAIL (에러 메시지 포함)
```

## 연동 체크리스트

| 항목 | 확인 사항 |
|------|----------|
| SCP | 호스트/포트/인증 정보 .env에 설정 |
| SCP | 원격 디렉토리 쓰기 권한 |
| SCP | 방화벽 포트(22) 오픈 |
| 외부 DB | 호스트/포트/인증 정보 .env에 설정 |
| 외부 DB | 대상 테이블 존재 확인 |
| 외부 DB | apl_id 유효성 검증 (bigint 등) |
| 공통 | 타임아웃 설정 적절성 |
| 공통 | 재시도 정책 확인 |
