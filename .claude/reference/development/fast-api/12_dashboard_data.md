# FastAPI 대시보드 데이터 표시 및 정리 패턴

> 관리자 백오피스에서 API 요청/작업을 어떻게 수집, 표시, 정리하는지 정의한다.

## 데이터 흐름 개요

```
API 요청 (POST /api/v1/tasks/*)
    ↓
┌─ 검증 성공 → api_task_queue (작업 등록)
│                 ↓ (배치 처리 후)
│              api_task_result (결과 등록)
│
└─ 검증 실패 (422/400) → api_request_log (실패 기록)
    ↓
[대시보드] 두 소스를 시간순 통합 → 통합 타임라인
```

## 1. 대시보드 (/) — 전체 현황

### 상단 통계 카드 (5개)

| 카드 | 데이터 소스 | 쿼리 |
|------|-----------|------|
| 요청실패 (4xx) | `api_request_log` | `COUNT(*)` (전체) |
| 대기 (Pending) | `api_task_queue` | `COUNT(*) WHERE status='pending'` |
| 처리중 | `api_task_queue` | `COUNT(*) WHERE status IN ('processing','file_generated')` |
| 완료 (Done) | `api_task_queue` | `COUNT(*) WHERE status='done'` |
| 실패 (Failed) | `api_task_queue` | `COUNT(*) WHERE status='failed'` |

```python
def _get_task_counts():
    """상태별 건수"""
    cursor.execute("""
        SELECT status, COUNT(*) as cnt
        FROM api_task_queue GROUP BY status
    """)
    return {row["status"]: row["cnt"] for row in cursor.fetchall()}
```

### 시스템 정보 + 바로가기

| 항목 | 값 |
|------|-----|
| 현재 시각 | `datetime.now()` |
| 출력 폴더 용량 | output/ 디렉토리 전체 파일 크기 합산 (MB) |
| 배치 폴링 주기 | config 값 |
| 최대 재시도 | config 값 |
| 바로가기 | PRD, 상세설계, 구현계획, Swagger UI |

### 통합 타임라인 (핵심)

**두 가지 소스**를 시간순으로 합쳐 하나의 테이블로 표시:

| 소스 | 출처 테이블 | 구분 표시 |
|------|-----------|----------|
| **작업** (task) | `api_task_queue LEFT JOIN api_task_result` | badge: 작업 |
| **요청실패** (rejected) | `api_request_log` (4xx/5xx) | badge: 요청실패 (빨간 배경) |

```python
def _get_unified_timeline(limit=20):
    """작업 + 실패 요청을 시간순 통합"""
    tasks = _get_recent_tasks(limit)
    failed = _get_failed_requests(limit)

    timeline = []
    for t in tasks:
        timeline.append({
            "source": "task",
            "time": t["created_at"],
            "identifier": t["identifier"],
            "type": t["task_type"],
            "status": t["status"],
            "detail": t.get("error_message") or "",
            "retry": t["retry_count"],
            # 아코디언 상세
            "started_at": ..., "completed_at": ...,
            "input_file": ..., "output_file": ...,
            "scp_status": ..., "params": ...,
        })
    for r in failed:
        timeline.append({
            "source": "rejected",
            "time": r["created_at"],
            "identifier": r.get("apl_id") or r.get("client_ip") or "-",
            "type": path에서 추출,
            "status": str(r["status_code"]),
            "detail": r.get("error_detail") or "",
            # 아코디언 상세
            "req_method": ..., "req_path": ...,
            "client_ip": ..., "elapsed_ms": ...,
            "request_params": ...,
        })

    timeline.sort(key=lambda x: x["time"], reverse=True)
    return timeline[:limit]
```

### 타임라인 테이블 컬럼 상세

| # | 컬럼명 | 작업 (source=task) | 요청실패 (source=rejected) |
|---|--------|-------------------|--------------------------|
| 1 | **시각** | `created_at[:19]` — 작업 접수 시각 | `created_at[:19]` — API 요청 시각 |
| 2 | **구분** | badge "작업" (기본 색상) | badge "요청실패" (빨간 배경 `#fff5f5`) |
| 3 | **식별자** | `identifier` — Spring apl_id (외부 요청 ID) | `apl_id` (있으면) 또는 `client_ip` 또는 "-" |
| 4 | **업무종류** | `task_type` — 등록된 업무 코드 | URL 마지막 세그먼트 (`/tasks/xxx` → `xxx`) |
| 5 | **상태** | badge: pending/processing/done/failed | badge: HTTP 상태 코드 (400, 422 등) |
| 6 | **상세** | `error_message` (실패 시만 표시) | `error_detail` (검증 에러 JSON) |
| 7 | **재시도** | `retry_count` (숫자: 0~3) | "-" (해당 없음) |

#### 컬럼별 세부 규격

**1. 시각**
- 형식: `YYYY-MM-DD HH:MM:SS` (ISO 8601에서 앞 19자 잘라냄)
- 소스: 작업 → `api_task_queue.created_at`, 실패 → `api_request_log.created_at`
- 정렬: 이 컬럼 기준 내림차순 (최신이 위)
- 예시: `2026-04-11 14:32:05`

**2. 구분**
- 작업: `<span class="badge badge-{status}">작업</span>` — 상태에 따라 색상 변경
- 요청실패: `<span class="badge badge-failed">요청실패</span>` — 항상 빨간색
- 행 배경: 요청실패 행은 `background:#fff5f5` (연한 빨강)

**3. 식별자**
- 스타일: `color:#0984e3; font-weight:500` (파란색 볼드)
- 작업: Spring 서버가 보낸 `apl_id` (예: `1234567890`)
- 요청실패: `apl_id` 추출 가능하면 사용, 불가하면 `client_ip` (예: `172.30.1.63`), 둘 다 없으면 `-`
- 용도: 외부 시스템과 대조하는 핵심 키

**4. 업무종류**
- 작업: DB에 저장된 `task_type` 그대로 (예: `coupang_excel`, `card_mapping`, `withholding_tax`)
- 요청실패: 요청 URL에서 추출 — `/api/v1/tasks/coupang-excel` → `coupang-excel`
- 주의: 작업은 underscore (`coupang_excel`), 실패는 kebab-case (`coupang-excel`)일 수 있음

**5. 상태**
- 작업 badge 색상 매핑:
  - `pending` → 회색 (대기)
  - `processing` → 파란색 (처리중)
  - `file_generated` → 파란색 (처리중, processing과 동일 표시)
  - `done` → 녹색 (완료)
  - `failed` → 빨간색 (실패)
- 요청실패: HTTP 상태 코드를 badge로 표시 (항상 빨간색)
  - `400` — 필수 파라미터 누락, 파일 형식 불일치
  - `422` — FastAPI 요청 검증 실패
  - `404` — 존재하지 않는 리소스
  - `429` — Rate Limit 초과

**6. 상세**
- 최대 표시: 80자 (`t.detail[:80]`), 초과 시 말줄임
- 작업: `error_message` — 배치 처리 중 발생한 에러 (성공 시 `-`)
  - 예: `"PDF 파일이 아닙니다"`, `"SCP 전송 실패: Connection refused"`
- 요청실패: `error_detail` — FastAPI 검증 에러 JSON
  - 예: `[{"loc":["body","apl_id"],"msg":"field required","type":"missing"}]`
- 전체 내용은 아코디언 펼침 시 코드 블록으로 표시

**7. 재시도**
- 작업: `retry_count` 숫자 (0=첫 시도, 1~2=재시도, 3=최종 실패)
- 요청실패: `-` (재시도 개념 없음, API 레벨에서 즉시 거부)

#### badge CSS 클래스 매핑

```css
.badge-pending    { background: #dfe6e9; color: #2d3436; }
.badge-processing { background: #74b9ff; color: #fff; }
.badge-done       { background: #55efc4; color: #00695c; }
.badge-failed     { background: #ff7675; color: #fff; }
.badge-sent       { background: #55efc4; color: #00695c; }
.badge-not_required { background: #dfe6e9; color: #636e72; }
```

### 아코디언 상세 (행 클릭 시 펼침)

**작업 (task)**:
- 시작/완료 시각, SCP 상태
- 입력/출력 파일 경로
- 요청 파라미터 (JSON, 코드 블록)
- 에러 메시지 (실패 시, 빨간 박스)

**요청실패 (rejected)**:
- HTTP 메서드 + 경로, 클라이언트 IP
- 응답 시간 (ms)
- 요청 파라미터 (JSON, 코드 블록)
- 에러 응답 (JSON, 빨간 코드 블록)

### 필터링 + 페이지네이션

```
필터 탭: [전체] [요청실패] [대기] [처리중] [완료] [실패]
URL: /admin/?filter=rejected&page=2
페이지 크기: 20건
```

## 2. 서버 개요 (/overview)

### 표시 내용

| 섹션 | 데이터 | 소스 |
|------|--------|------|
| 아키텍처 다이어그램 | Spring↔API 서버 흐름 | 정적 ASCII art |
| 연결 상태 | API 서버, SQLite, Spring DB, SCP | 실시간 연결 체크 |
| 서버 설정 | 포트, 환경, 배치 주기 등 | config 값 |
| task_type별 통계 | 업무별 상태 분포 | `GROUP BY task_type, status` |

```python
# task_type별 통계 쿼리
cursor.execute("""
    SELECT task_type, status, COUNT(*) as cnt
    FROM api_task_queue
    GROUP BY task_type, status
    ORDER BY task_type, status
""")
# → {"coupang_excel": {"pending": 2, "done": 15, "total": 17}, ...}
```

### Spring DB 연결 상태

```python
spring_ok = False
spring_count = 0
try:
    sconn = get_spring_db_connection()
    scur = sconn.cursor()
    scur.execute("SELECT COUNT(*) FROM tn_svc_apl")
    spring_count = scur.fetchone()[0]
    spring_ok = True
except Exception:
    pass
# → 연결 성공: 녹색 dot + 건수 / 실패: 빨간 dot + FAIL
```

## 3. 작업 상세 (/tasks/{task_id})

### 표시 카드 4개

| 카드 | 표시 항목 |
|------|----------|
| **기본 정보** | 식별자, 업무종류, 상태(badge), 우선순위, 접수/시작/완료 시각, 소요시간, 재시도 횟수 |
| **처리 흐름** | 파이프라인 시각화: `접수 → SCP다운 → 처리 → SCP업로드 → 완료` (각 단계 성공/실패 표시) |
| **입력** | 입력파일 경로, 원격파일 경로, CMS파일 목록, 카드컬럼, 직원데이터 수 |
| **출력** (성공 시) | 결과파일 경로, 파일명, SCP 전송 상태 + 시각 |
| **에러** (실패 시) | 에러메시지, 재시도 횟수/3, 마지막 시도 시각 |

### 처리 흐름 파이프라인

```python
pipeline = [
    {"step": "접수", "ok": True},
    {"step": "SCP다운", "ok": task.input_file_path is not None},
    {"step": "처리", "ok": task.status in ("done", "file_generated")},
    {"step": "SCP업로드", "ok": result.scp_status == "sent"},
    {"step": "완료", "ok": task.status == "done"},
]
```

시각화: `[✓ 접수] → [✓ SCP다운] → [✓ 처리] → [✗ SCP업로드] → [ 완료]`
- 성공: 녹색 배경
- 실패: 빨간 배경

### 요청실패 상세 (mode == "rejected")

| 항목 | 내용 |
|------|------|
| 요청 | HTTP 메서드 + 경로 |
| HTTP 상태 | 상태 코드 (badge) |
| 식별자 | apl_id |
| 클라이언트 | IP 주소 |
| 응답시간 | ms |
| 에러 상세 | JSON (코드 블록) |

## 4. 데이터 수집 체계

### 어디서 기록되는가

| 이벤트 | 기록 위치 | 기록 시점 |
|--------|----------|----------|
| API 요청 성공 | `api_task_queue` | 라우터 (POST /tasks/*) |
| API 요청 실패 (422) | `api_request_log` | 예외 핸들러 (validation_error_handler) |
| API 요청 실패 (4xx) | `api_request_log` | 라우터 (_log_request_failure) |
| 배치 처리 시작 | `api_task_queue.started_at` | 배치 엔진 (claim_next_task) |
| 배치 처리 완료 | `api_task_queue.completed_at` + `api_task_result` | 배치 엔진 (mark_done) |
| 배치 처리 실패 | `api_task_queue.error_message` | 배치 엔진 (mark_failed) |
| SCP 전송 완료 | `api_task_result.scp_status/scp_sent_at` | 배치 엔진 |
| HTTP 요청 로그 | 로그 파일 (log_requests 미들웨어) | 미들웨어 |

### 실패 요청 기록 패턴

```python
# 1. FastAPI 자동 검증 실패 (422)
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    log_to_db(status_code=422, error_detail=json.dumps(exc.errors()))

# 2. 비즈니스 검증 실패 (400/404/409)
def _log_request_failure(request, status_code, apl_id, error_detail):
    """라우터에서 HTTPException 발생 전 호출"""
    conn.execute("INSERT INTO api_request_log ...")
```

## 5. 파일 정리 정책

| 대상 | 주기 | 조건 | 처리 |
|------|------|------|------|
| input/ 파일 | 1시간마다 | done 상태 + 7일 경과 | 삭제 |
| output/ 파일 | 1시간마다 | done 상태 + 7일 경과 | 삭제 |
| api_task_queue | 수동 | - | 보관 (삭제 안함) |
| api_request_log | 수동 | - | 보관 (삭제 안함) |

```python
# 배치 엔진에서 자동 실행 (1시간마다)
def cleanup_old_files():
    cutoff = (datetime.now() - timedelta(days=FILE_CLEANUP_DAYS)).isoformat()
    rows = conn.execute("""
        SELECT input_file_path, output_file_path
        FROM api_task_queue
        WHERE status = 'done' AND completed_at < ?
    """, (cutoff,)).fetchall()
    for row in rows:
        if row["input_file_path"]: os.remove(...)
        if row["output_file_path"]: os.remove(...)
```

## 6. 새 프로젝트에서 재활용 시 커스터마이징 포인트

| 항목 | 변경 위치 | 내용 |
|------|----------|------|
| 통계 카드 | `dashboard.html` grid-5 | 상태 종류에 맞게 카드 추가/삭제 |
| 타임라인 컬럼 | `_get_unified_timeline()` | 소스/필드 추가 |
| 아코디언 상세 | `dashboard.html` tl-detail | 업무별 상세 필드 |
| 필터 탭 | `dashboard.html` filters | 상태값에 맞게 변경 |
| 처리 흐름 파이프라인 | `task_detail` route | 단계 정의 수정 |
| 연결 상태 | `overview.html` | 외부 시스템에 맞게 변경 |
| 파일 정리 주기 | `api_config.py` | FILE_CLEANUP_DAYS 조정 |
