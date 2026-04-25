# FastAPI 에러 핸들링 — 3계층

## 계층 구조

```
Layer 1: 요청 검증 (422)     — FastAPI/Pydantic 자동
Layer 2: 비즈니스 로직 (4xx)  — HTTPException + ErrorResponse
Layer 3: 인프라 에러           — 재시도 + 복구
```

## Layer 1: 요청 검증 에러 (422)

FastAPI가 Form/Query/Path 파라미터 검증 실패 시 자동 발생.

```python
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # 요청 로그 DB에 기록
    apl_id = extract_apl_id(request)
    log_to_db(
        method=request.method,
        path=str(request.url.path),
        status_code=422,
        apl_id=apl_id,
        error_detail=json.dumps(exc.errors(), ensure_ascii=False),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
```

## Layer 2: 비즈니스 로직 에러 (4xx)

```python
# 표준 에러 응답 모델
class ErrorResponse(BaseModel):
    error: str          # 코드: INVALID_FILE, TASK_NOT_FOUND 등
    message: str        # 사용자 메시지 (한국어)
    detail: Optional[str] = None

# 사용 패턴
raise HTTPException(
    status_code=400,
    detail=ErrorResponse(
        error="INVALID_FILE",
        message="PDF 파일만 업로드 가능합니다",
    ).model_dump()
)
```

### 표준 에러 코드

| 코드 | HTTP | 상황 |
|------|------|------|
| INVALID_INPUT | 400 | 필수 파라미터 누락 |
| INVALID_FILE | 400 | 파일 형식 불일치 |
| TASK_NOT_FOUND | 404 | 존재하지 않는 task_id |
| DUPLICATE_TASK | 409 | 동일 apl_id 중복 요청 |
| TASK_NOT_DONE | 400 | 미완료 작업 파일 다운로드 시도 |

## Layer 3: 인프라 에러 (배치 내부)

비즈니스 로직 외부에서 발생하는 인프라 장애.

```python
# 재시도 가능한 인프라 에러
RETRIABLE_ERRORS = (
    ConnectionError,      # SCP 연결 실패
    TimeoutError,         # 네트워크 타임아웃
    IOError,              # 파일 I/O 에러
    paramiko.SSHException,  # SSH 에러
)

# 재시도 불가능 (비즈니스 에러)
NON_RETRIABLE = (
    ValueError,           # 데이터 형식 에러
    KeyError,             # 필수 키 누락
)
```

### 재시도 정책

```
인프라 에러 발생
    ↓
retry_count 확인
    ├─ < MAX_RETRY(3): status → pending (자동 재시도)
    └─ >= MAX_RETRY:   status → failed (최종 실패)
```

## 로깅 전략

| 레벨 | 대상 | 저장 위치 |
|------|------|----------|
| INFO | 정상 요청/응답 | 로그 파일 |
| WARNING | 재시도 발생 | 로그 파일 + DB |
| ERROR | 최종 실패 | 로그 파일 + DB + 외부 DB |

```python
# 미들웨어 로깅 (모든 요청)
logger.info(f"{method} {path} → {status} ({elapsed}ms)")

# 배치 에러 로깅
logger.error(f"[{task_id}] 처리 실패: {error_msg} (retry: {retry_count})")

# DB 로깅 (4xx/5xx)
insert_request_log(method, path, status_code, elapsed, client_ip, apl_id, error)
```
