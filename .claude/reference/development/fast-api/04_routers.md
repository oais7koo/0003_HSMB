# FastAPI 라우터 설계 패턴

## 라우터 분리 원칙

| 라우터 | 역할 | Prefix |
|--------|------|--------|
| health.py | 상태 확인, 버전 | `/` |
| tasks.py | 업무 처리 API | `/api/v1` |
| admin/routes.py | 관리자 백오피스 | `/admin` |

## health.py — 상태 체크

```python
router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@router.get("/version")
async def version():
    return {"version": "1.0.0", "server": "API Server", "framework": "FastAPI"}
```

## tasks.py — 업무별 엔드포인트 패턴

### 엔드포인트 설계 원칙

1. **업무별 전용 엔드포인트**: `/api/v1/tasks/{task-type}` (kebab-case)
2. **Form + File**: multipart/form-data (apl_id + file + params)
3. **즉시 응답**: 큐 등록 후 task_id 반환 (비동기 처리)
4. **이벤트 발신**: 배치 엔진 즉시 깨우기

### 엔드포인트 템플릿

```python
router = APIRouter(tags=["Tasks"])

@router.post("/tasks/{task-type}", response_model=TaskCreateResponse)
async def create_task(
    request: Request,
    apl_id: str = Form(..., description="외부 시스템 요청 ID"),
    file: UploadFile = File(None, description="입력 파일"),
    remote_file_path: str = Form(None, description="SCP 원격 경로"),
    params: str = Form(None, description="추가 파라미터 (JSON)"),
):
    # 1. 입력 검증
    if not file and not remote_file_path:
        raise HTTPException(400, detail=ErrorResponse(
            error="INVALID_INPUT",
            message="file 또는 remote_file_path 필수",
        ).model_dump())

    # 2. 파일 저장 (업로드된 경우)
    if file:
        input_path = save_upload_file(file, config.INPUT_DIR)

    # 3. DB 큐 등록
    task_id = str(uuid.uuid4())
    insert_task(task_id, apl_id, task_type, input_path, params)

    # 4. 배치 이벤트 발신
    request.app.state.task_event.set()

    # 5. 즉시 응답
    return TaskCreateResponse(
        task_id=task_id,
        identifier=apl_id,
        task_type=task_type,
        status="pending",
    )
```

### 상태 조회 / 파일 다운로드

```python
@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(404, detail="작업을 찾을 수 없습니다")
    return TaskStatusResponse(**task)

@router.get("/tasks/{task_id}/file")
async def download_file(task_id: str):
    task = get_task_by_id(task_id)
    if task["status"] != "done":
        raise HTTPException(400, detail="처리 완료 후 다운로드 가능")
    return FileResponse(task["output_file_path"])
```

## 엔드포인트별 상세 (설명 + curl 예시)

> 새 프로젝트에서 업무별 엔드포인트를 만들 때, 아래 형식으로 각 엔드포인트의 **설명 + 파일 전달 방식 + curl 예시**를 문서화한다.

---

### POST /tasks/coupang-excel — 쿠팡 전표 엑셀화

쿠팡 매출전표 PDF → 카드별 분리 Excel 변환

파일 전달 (택 1): `file` (PDF 직접 업로드) 또는 `remote_file_path` (SCP 경로)

```bash
# SCP 경로로 요청
curl -X POST http://host:8007/api/v1/tasks/coupang-excel \
  -F 'apl_id=1001' \
  -F 'remote_file_path=d:/storage/api_data/input/33a/coupang_sample.pdf'

# 파일 직접 업로드
curl -X POST http://host:8007/api/v1/tasks/coupang-excel \
  -F 'apl_id=1001' \
  -F 'file=@/path/to/coupang.pdf'
```

---

### POST /tasks/naver-excel — 네이버 전표 엑셀화

네이버 매출전표 PDF → 카드별 분리 Excel 변환

파일 전달 (택 1): `file` (PDF 직접 업로드) 또는 `remote_file_path` (SCP 경로)

```bash
curl -X POST http://host:8007/api/v1/tasks/naver-excel \
  -F 'apl_id=1002' \
  -F 'remote_file_path=d:/storage/api_data/input/33b/naver_sample.pdf'
```

---

### POST /tasks/card-mapping — 카드전표 매핑

카드 거래내역 Excel → 카드번호별 분리 Excel

파일 전달: `file` (Excel 필수)

```bash
curl -X POST http://host:8007/api/v1/tasks/card-mapping \
  -F 'apl_id=1003' \
  -F 'file=@/path/to/card_transactions.xlsx'
```

---

### POST /tasks/card-history — 카드내역 정리

카드내역 데이터 Excel → 정리된 Excel (마스킹 해제, 컬럼 정규화)

파일 전달: `file` (Excel 필수)

```bash
curl -X POST http://host:8007/api/v1/tasks/card-history \
  -F 'apl_id=1004' \
  -F 'file=@/path/to/card_history.xlsx'
```

---

### POST /tasks/cms-view — CMS 파일 검증 + 미리보기

CMS 파일을 SCP에서 가져와 검증만 수행 (처리 안 함). 미리보기 용도.

파일 전달: `remote_file_path` (SCP 경로, 복수 파일은 `cms_remote_files` 쉼표 구분)

```bash
curl -X POST http://host:8007/api/v1/tasks/cms-view \
  -F 'apl_id=1005' \
  -F 'remote_file_path=d:/storage/api_data/input/32a/bank_2026.csv' \
  -F 'params={"cms_remote_files": "d:/storage/.../cms1.csv,d:/storage/.../cms2.csv"}'
```

---

### POST /tasks/cms — CMS 통장정리

CMS 원장 + 통장 데이터 → 자동 매칭 정리 Excel

파일 전달: SCP 경로 (통장 파일 + CMS 파일 목록)

```bash
curl -X POST http://host:8007/api/v1/tasks/cms \
  -F 'apl_id=1006' \
  -F 'remote_file_path=d:/storage/api_data/input/32a/bank_2026.csv' \
  -F 'params={"cms_remote_files": "d:/storage/.../cms1.csv,d:/storage/.../cms2.csv"}'
```

---

### POST /tasks/withholding-tax — 원천세 계산

급여/4대보험/소득세 계산. 파일 불필요 — JSON params로 직원 데이터 전달.

```bash
curl -X POST http://host:8007/api/v1/tasks/withholding-tax \
  -F 'apl_id=1007' \
  -F 'params={"employee_data": [{"name": "홍길동", "salary": 3000000, "dependents": 2}]}'
```

---

### POST /tasks/remap-card — 카드번호 리매핑

기존 Excel의 마스킹된 카드번호를 매핑 테이블로 치환.

파일 전달: `file` (Excel) 또는 `source_apl_id` (이전 작업 결과 참조)

```bash
# 파일 직접
curl -X POST http://host:8007/api/v1/tasks/remap-card \
  -F 'apl_id=1008' \
  -F 'file=@/path/to/masked_data.xlsx' \
  -F 'params={"card_mapping": {"1234-****-****-5678": "1234-5678-9012-5678"}}'

# 이전 작업 결과 참조
curl -X POST http://host:8007/api/v1/tasks/remap-card \
  -F 'apl_id=1009' \
  -F 'params={"source_apl_id": "1003"}'
```

---

### GET /tasks/{task_id}/status — 작업 상태 조회

```bash
curl http://host:8007/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/status
```

응답 예시:
```json
{
  "task_id": "550e8400-...",
  "status": "done",
  "started_at": "2026-04-11T14:32:05",
  "completed_at": "2026-04-11T14:32:18",
  "error_message": null,
  "retry_count": 0,
  "result": {"employee_count": 5}
}
```

---

### GET /tasks/{task_id}/file — 결과 파일 다운로드

```bash
# status == "done" 일 때만 가능
curl -O http://host:8007/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/file
```

---

### 엔드포인트 문서화 템플릿

새 업무 추가 시 아래 형식으로 작성:

```markdown
### POST /tasks/{task-type} — {한글 요약}

{한 줄 설명}: {입력} → {출력}

파일 전달 (택 1): `file` ({형식}) 또는 `remote_file_path` (SCP)

\`\`\`bash
curl -X POST http://host:{port}/api/v1/tasks/{task-type} \
  -F 'apl_id={예시ID}' \
  -F 'file=@/path/to/file.{ext}'
\`\`\`
```

---

## 파일 전달 방식 (택 1)

| 방식 | 파라미터 | 용도 |
|------|---------|------|
| 직접 업로드 | `file: UploadFile` | 클라이언트가 파일 보유 |
| SCP 경로 | `remote_file_path: str` | 파일이 원격 서버에 존재 |
| 복수 SCP | `remote_files: str` (쉼표구분) | 여러 파일 필요 |

## Rate Limiting 적용

```python
from rate_limiter import limiter

@router.post("/tasks/xxx")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def create_xxx(request: Request, ...):
    ...
```
