# FastAPI 메뉴 구성도

> 전체 URL 맵을 한눈에 파악하기 위한 문서. 새 프로젝트 시 이 구조를 기준으로 엔드포인트를 설계한다.

## 전체 구성

```
/                               → /admin/overview 리다이렉트
│
├── /health                     [GET]  서버 상태 확인
├── /version                    [GET]  API 버전 정보
├── /docs                       [GET]  Swagger UI (커스터마이징)
│
├── /api/v1/tasks/              ─── API 엔드포인트 (외부 시스템 연동)
│   ├── 업무별 접수 (POST)
│   │   ├── /coupang-excel      쿠팡 전표 PDF → Excel
│   │   ├── /naver-excel        네이버 전표 PDF → Excel
│   │   ├── /card-mapping       카드전표 매핑
│   │   ├── /card-history       카드내역 정리
│   │   ├── /cms-view           CMS 파일 검증 + 미리보기
│   │   ├── /cms                CMS 통장정리
│   │   ├── /withholding-tax    원천세 계산
│   │   ├── /remap-card         카드번호 리매핑
│   │   └── /tasks              통합 접수 (deprecated)
│   │
│   └── 공통 조회 (GET)
│       ├── /{task_id}/status   작업 상태 조회
│       └── /{task_id}/file     결과 파일 다운로드
│
└── /admin/                     ─── 관리자 백오피스 (Jinja2)
    ├── /                       대시보드 (작업 통계, 최근 작업)
    ├── /overview               서버 개요 (아키텍처, task_type별 통계)
    ├── /tasks                  작업 목록 (필터링)
    ├── /tasks/{task_id}        작업 상세
    ├── /spring-db              Spring DB 상태 확인
    ├── /spring-db/delete/{id}  [POST] Spring DB 레코드 삭제
    ├── /scp                    SCP 이력
    ├── /docs                   설계문서 목록
    ├── /docs/{doc_path}        설계문서 뷰어 (마크다운 → HTML)
    ├── /docs/prd               PRD 문서
    └── /docs/api-design        API 설계 문서
```

## API 엔드포인트 상세

### 업무별 접수 (POST /api/v1/tasks/*)

| 엔드포인트 | 태그 | 입력 | 우선순위 | 파일 필수 |
|-----------|------|------|---------|----------|
| `coupang-excel` | 쿠팡 | PDF (전표) | normal | Y (file or SCP) |
| `naver-excel` | 네이버 | PDF (전표) | normal | Y (file or SCP) |
| `card-mapping` | 카드 | Excel (거래내역) | high | Y |
| `card-history` | 카드 | Excel (카드내역) | high | Y |
| `cms-view` | CMS | SCP 경로 | - | N (SCP만) |
| `cms` | CMS | SCP 경로 | normal | N (SCP만) |
| `withholding-tax` | 원천세 | JSON params | high | N |
| `remap-card` | 공통 | Excel or source_apl_id | normal | 조건부 |

### 공통 입력 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `apl_id` | Form(str) | Y | 외부 시스템 요청 ID |
| `file` | UploadFile | 택1 | 직접 업로드 파일 |
| `remote_file_path` | Form(str) | 택1 | SCP 원격 경로 |
| `params` | Form(str) | N | 추가 파라미터 (JSON) |

### 공통 조회 (GET /api/v1/tasks/*)

| 엔드포인트 | 응답 | 조건 |
|-----------|------|------|
| `/{task_id}/status` | TaskStatusResponse | - |
| `/{task_id}/file` | FileResponse | status == 'done' |

## 관리자 백오피스 상세

### 네비게이션 — 필수/선택/확장 구분

> `ooref run` 비교 시 **필수** 항목만 불일치로 보고. **선택/확장**은 INFO로 표시.

#### 필수 메뉴 (모든 FastAPI 프로젝트)

| key | label | URL | 용도 |
|-----|-------|-----|------|
| `dashboard` | 대시보드 | `/admin/` | 작업 통계 + 최근 활동 타임라인 |
| `docs` | 설계문서 | `/admin/docs` | SP 문서 마크다운 렌더링 |
| `apidocs` | API엔드포인트 | `/docs` | Swagger UI |

#### 선택 메뉴 (권장, 프로젝트 상황에 따라)

| key | label | URL | 용도 | 조건 |
|-----|-------|-----|------|------|
| `overview` | 서버개요 | `/admin/overview` | 아키텍처 + task_type별 통계 | 업무 유형 2개 이상 |
| `tasks` | 작업관리 | `/admin/tasks` | 작업 목록 필터링 | 대시보드와 분리 필요 시 |
| `monitoring` | 모니터링 | `/admin/monitoring` | 실시간 로그, 성능 지표 | 운영 환경 |

#### 프로젝트별 확장 메뉴 (SP마다 다름)

| key | label | URL | 용도 | 해당 SP |
|-----|-------|-----|------|---------|
| `spring-db` | Spring DB | `/admin/spring-db` | 외부 DB 상태 확인 | SP04 (Spring 연동) |
| `design-system` | 디자인시스템 | `/admin/design-system` | 디자인 토큰/컴포넌트 | SP05 등 |
| `notices` | 공지사항 | `/admin/notices` | 공지 관리 | 커뮤니티 기능 |
| `devboard` | 개발자게시판 | `/admin/devboard` | 개발 이슈 공유 | 팀 협업 기능 |

> **확장 시 규칙**: `nav_items.py`에 추가 + `routes.py`에 라우트 등록 + `templates/`에 템플릿 생성

### 네비게이션 코드 패턴

```python
# nav_items.py
NAV_ITEMS = [
    # === 필수 ===
    {"url": "/admin/",       "label": "대시보드",      "key": "dashboard"},
    {"url": "/admin/docs",   "label": "설계문서",      "key": "docs"},
    {"url": "/docs",         "label": "API엔드포인트", "key": "apidocs"},
    # === 선택 (프로젝트에 따라 추가/제거) ===
    {"url": "/admin/overview","label": "서버개요",      "key": "overview"},
    # === 확장 (SP별 고유) ===
    # {"url": "/admin/spring-db","label": "Spring DB",  "key": "spring-db"},
]
BRAND = {"url": "/admin/", "label": "{프로젝트명} API 백오피스"}
```

### 페이지별 역할

#### 필수 페이지

| 페이지 | URL | 데이터 소스 | 용도 |
|--------|-----|-----------|------|
| 대시보드 | `/admin/` | task_queue GROUP BY status | 통계 카드 + 통합 타임라인 |
| 작업상세 | `/admin/tasks/{id}` | 단일 작업 + 결과 | 처리 흐름, 에러 분석 |
| 설계문서 | `/admin/docs` | `00_doc/sp{N}/*.md` | 마크다운 → HTML |
| API문서 | `/docs` | OpenAPI spec | Swagger UI |

#### 선택/확장 페이지

| 페이지 | URL | 데이터 소스 | 용도 | 구분 |
|--------|-----|-----------|------|------|
| 서버개요 | `/admin/overview` | task_type별 상태 | 아키텍처 + 현황 | 선택 |
| 작업목록 | `/admin/tasks` | task_queue + result JOIN | 필터링 목록 | 선택 |
| Spring DB | `/admin/spring-db` | tn_svc_apl (PostgreSQL) | 외부 DB 상태 | 확장 |
| 모니터링 | `/admin/monitoring` | 로그, 메트릭 | 실시간 감시 | 확장 |
| 디자인시스템 | `/admin/design-system` | 토큰, 컴포넌트 | 디자인 관리 | 확장 |

### ooref 비교 시 판정 기준

| 구분 | 레퍼런스에 있음 + SP에 없음 | 레퍼런스에 없음 + SP에 있음 |
|------|--------------------------|--------------------------|
| **필수** | ERROR — 구현 필요 | - |
| **선택** | INFO — 검토 권장 | INFO — SP 고유 확장 |
| **확장** | 무시 (SP별 다름) | INFO — SP 고유 확장 |

## 새 업무 추가 시 체크리스트

새 task_type을 추가할 때 변경해야 하는 위치:

| # | 위치 | 변경 내용 |
|---|------|----------|
| 1 | `api_config.py` | `ALLOWED_TASK_TYPES`에 추가 |
| 2 | `api_config.py` | `TASK_PRIORITY`에 우선순위 설정 |
| 3 | `routers/tasks.py` | 전용 POST 엔드포인트 추가 |
| 4 | `batch/handlers.py` | `HANDLER_MAP`에 핸들러 등록 |
| 5 | `batch/handlers.py` | `handle_{type}()` 함수 구현 |
| 6 | `tests/` | `test_endpoint_{type}.py` 작성 |
| 7 | (선택) `batch/scp.py` | SCP 경로 매핑 추가 |
| 8 | (선택) `admin/routes.py` | 관리자 필터 옵션 추가 |
