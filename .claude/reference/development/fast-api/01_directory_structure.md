# FastAPI 표준 디렉토리 구조

## 디렉토리 트리

```
{project_name}/
├── main.py                 # FastAPI 앱 초기화 + lifespan + 미들웨어
├── {project}_config.py     # 설정 (포트, 경로, DB, 외부 연동, 우선순위)
├── rate_limiter.py         # Rate Limiting (slowapi)
│
├── routers/                # API 엔드포인트
│   ├── __init__.py
│   ├── health.py           # GET /health, /version
│   └── tasks.py            # POST /api/v1/tasks/* (업무별 엔드포인트)
│
├── models/                 # DB + Pydantic 스키마
│   ├── __init__.py
│   ├── database.py         # SQLite 초기화, 테이블 DDL, 마이그레이션
│   └── schemas.py          # 요청/응답 Pydantic 모델
│
├── batch/                  # 배치 처리 엔진
│   ├── __init__.py
│   ├── engine.py           # 비동기 루프 (이벤트 + 폴링)
│   ├── handlers.py         # task_type별 핸들러 디스패치
│   ├── scp.py              # SCP/SFTP 파일 전송
│   └── spring_db.py        # 외부 DB 상태 동기화 (선택)
│
├── admin/                  # 관리자 백오피스
│   ├── __init__.py
│   ├── routes.py           # 대시보드, 작업관리, 문서뷰어
│   ├── nav_items.py        # 네비게이션 메뉴 정의
│   ├── templates/          # Jinja2 템플릿
│   │   ├── base.html       # 공통 레이아웃
│   │   ├── dashboard.html  # 대시보드
│   │   ├── tasks.html      # 작업 목록
│   │   └── task_detail.html
│   └── static/             # CSS, JS (선택)
│
├── tests/                  # pytest 테스트
│   ├── __init__.py
│   ├── conftest.py         # Fixtures (TestClient, 테스트 DB, SFTP 서버)
│   ├── test_task_create.py # 엔드포인트 테스트
│   ├── test_endpoint_*.py  # 업무별 테스트
│   └── test_scp_*.py       # 외부 연동 테스트
│
├── db/                     # SQLite DB (런타임 생성)
├── file/                   # 파일 저장
│   ├── input/              # 업로드/다운로드 입력
│   └── output/             # 처리 결과
└── logs/                   # 로그 파일
```

## 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 설정 파일 | `{project}_config.py` | `api_config.py` |
| 라우터 | 기능 단위 분리 | `health.py`, `tasks.py` |
| 핸들러 | `handle_{task_type}` | `handle_coupang_excel` |
| 테스트 | `test_{대상}.py` | `test_task_create.py` |
| 템플릿 | `{기능}.html` | `dashboard.html` |

## 파일 크기 가이드

| 파일 | 권장 | 초과 시 |
|------|------|---------|
| main.py | ~150줄 | 미들웨어/핸들러 분리 |
| routers/*.py | ~300줄 | 업무별 라우터 분리 |
| handlers.py | ~500줄 | 핸들러별 모듈 분리 |
| conftest.py | ~300줄 | fixture 모듈 분리 |
