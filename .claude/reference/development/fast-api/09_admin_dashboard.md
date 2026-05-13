# FastAPI 관리자 대시보드 패턴

## 구조

```
admin/
├── __init__.py
├── routes.py          # 라우트 정의
├── nav_items.py       # 네비게이션 메뉴
├── templates/         # Jinja2 템플릿
│   ├── base.html      # 공통 레이아웃 (nav + content)
│   ├── dashboard.html # 대시보드 (통계)
│   ├── overview.html  # 서버 개요
│   ├── tasks.html     # 작업 목록
│   └── task_detail.html
└── static/            # CSS, JS (선택)
```

## 라우터 설정

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="admin/templates")
```

## 네비게이션 메뉴 (nav_items.py)

```python
NAV_ITEMS = [
    {"url": "/admin/", "label": "대시보드", "key": "dashboard"},
    {"url": "/admin/overview", "label": "서버개요", "key": "overview"},
    {"url": "/admin/tasks", "label": "작업관리", "key": "tasks"},
    {"url": "/admin/docs", "label": "설계문서", "key": "docs"},
    {"url": "/docs", "label": "API문서", "key": "apidocs"},
]
```

## 라우트 패턴

```python
@router.get("/")
async def dashboard(request: Request):
    stats = get_task_stats()  # DB에서 통계 조회
    recent = get_recent_tasks(limit=10)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "nav_items": NAV_ITEMS,
        "current": "dashboard",
        "stats": stats,
        "recent_tasks": recent,
    })

@router.get("/tasks")
async def task_list(request: Request, status: str = None, task_type: str = None):
    tasks = get_tasks(status=status, task_type=task_type)
    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "nav_items": NAV_ITEMS,
        "current": "tasks",
        "tasks": tasks,
        "filter_status": status,
        "filter_type": task_type,
    })
```

## base.html 템플릿

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title | default("API Admin") }}</title>
    <style>
        /* 최소 CSS — 외부 프레임워크 불필요 */
        nav { display: flex; gap: 1rem; padding: 1rem; background: #f5f5f5; }
        nav a { text-decoration: none; padding: 0.5rem 1rem; }
        nav a.active { font-weight: bold; border-bottom: 2px solid #333; }
        .content { padding: 2rem; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <nav>
        {% for item in nav_items %}
        <a href="{{ item.url }}"
           class="{{ 'active' if current == item.key else '' }}">
            {{ item.label }}
        </a>
        {% endfor %}
    </nav>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

## Swagger UI 커스터마이징

```python
# main.py에서 /docs 커스터마이징
@app.get("/docs", include_in_schema=False)
async def custom_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API 문서",
    )
```

## 설계문서 뷰어 (선택)

```python
@router.get("/docs")
async def docs_list(request: Request):
    """00_doc/sp{N}/ 마크다운 문서 목록"""
    docs = glob.glob("00_doc/sp04/d4*.md")
    return templates.TemplateResponse("docs_list.html", {
        "request": request,
        "docs": sorted(docs),
    })

@router.get("/docs/{filename}")
async def docs_view(request: Request, filename: str):
    """마크다운 → HTML 렌더링"""
    content = Path(f"00_doc/sp04/{filename}").read_text(encoding="utf-8")
    html = markdown.markdown(content, extensions=["tables", "fenced_code"])
    return templates.TemplateResponse("docs_view.html", {
        "request": request,
        "content": html,
    })
```
