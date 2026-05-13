# FastAPI 앱 초기화 패턴

## main.py 구조

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 관리"""
    # === Startup ===
    init_db_tables()                              # DB 테이블 초기화
    app.state.task_event = asyncio.Event()        # 배치 트리거 이벤트
    batch_task = asyncio.create_task(             # 배치 엔진 시작
        start_batch_loop(app.state.task_event)
    )
    yield
    # === Shutdown (Graceful) ===
    batch_task.cancel()
    try:
        await asyncio.wait_for(batch_task, timeout=30)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass

app = FastAPI(
    title="API Server",
    version="1.0.0",
    lifespan=lifespan,
)
```

## 미들웨어 스택 (순서 중요)

```python
# 1. Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 운영: 도메인 제한
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. HTTP 로깅
@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.0f}ms)")
    return response
```

**미들웨어 실행 순서**: SlowAPI → CORS → log_requests → 라우터

## 라우터 등록

```python
from routers.health import router as health_router
from routers.tasks import router as tasks_router
from admin.routes import router as admin_router

app.include_router(health_router)
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(admin_router)
```

## 루트 리다이렉트

```python
@app.get("/")
async def root():
    return RedirectResponse(url="/admin/overview")
```

## 예외 핸들러

```python
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    # 요청 로그 DB에 기록 (apl_id, 파라미터, 에러 상세)
    log_request_error(request, exc)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
```

## Lifespan 체크리스트

| 단계 | 항목 | 필수 |
|------|------|------|
| Startup | DB 테이블 초기화 | Y |
| Startup | 배치 이벤트 생성 | Y (배치 사용 시) |
| Startup | 배치 루프 시작 | Y (배치 사용 시) |
| Startup | 로그 디렉토리 생성 | Y |
| Shutdown | 배치 태스크 취소 | Y |
| Shutdown | Graceful 대기 (30초) | Y |
| Shutdown | DB 연결 정리 | 선택 |
