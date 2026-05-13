# {기능명} 상세기획

> 문서번호: {dXXXX} | 단계: 기획 | SP: {SPNN} | 생성일: {YYYY-MM-DD}
> 연결 Feature: {F_ID} | plan.md 참조
> 프레임워크: FastAPI (`04_api_server/`)

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | {YYYY-MM-DD} | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | {dXXXX} |
| 대상 기능 | {F_ID} {기능명} |
| 원본 페이지 | `{project}/pages/{page}.py` (없으면 삭제) |
| oais 함수 | `oais/{module}.py {function}()` |
| 버전 | v01 |
| 작성일 | {YYYY-MM-DD} |
| 관련 문서 | (없으면 삭제) |
| 페이지 URL | `http://localhost:{PORT}/admin/...` — Admin UI인 경우 (없으면 삭제) |
| **엔드포인트 (1단계)** | `POST /api/v1/tasks/{task_type_1}` — {단계 설명} |
| **엔드포인트 (2단계)** | `POST /api/v1/tasks/{task_type_2}` — {단계 설명} (단일 단계 시 삭제) |

---

## 2. 기능 개요

> 이 API 기능이 무엇을 하는지 1~3문장으로 설명
> 몇 단계 구성인지 명시 (예: 2단계 — view(미리보기) → cal(처리))

### 2.1 엔드포인트

| 단계 | 메서드 | URL | 설명 |
|------|--------|-----|------|
| 1단계 | `POST` | `/api/v1/tasks/{task_type_1}` | {단계 설명} |
| 2단계 | `POST` | `/api/v1/tasks/{task_type_2}` | {단계 설명} |

> 단일 단계 기능이면 1행만 유지. fast-path 있으면 비고 컬럼 추가.

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | | Must | PRD |

## 4. 입출력 정의

### 4.1 입력

#### 4.1.1 작업 접수

```
POST /api/v1/tasks/{task_type}
```

| 파라미터 | 타입 | 설명 | 필수 |
|---------|------|------|------|
| `task_type` | path `str` | 작업 유형 식별자 (예: `card-view`, `card-history`) | ✅ |

**Request Body (JSON)**:

| 필드 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `file_path` | `str` | 처리할 파일 경로 (서버 내) | ✅ |
| `options` | `object` | 작업 옵션 (기능별 상이) | - |

```json
{
  "file_path": "input/{filename}.xlsx",
  "options": {}
}
```

### 4.2 출력

#### 4.2.1 응답 — 작업 접수 성공

```json
{
  "task_id": "20260414-0001",
  "status": "READY",
  "message": "작업이 접수되었습니다."
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `task_id` | `str` | 생성된 작업 ID (YYYYMMDD-NNNN) |
| `status` | `str` | 초기 상태 (`READY`) |
| `message` | `str` | 처리 결과 메시지 |

#### 4.2.2 응답 — 작업 결과 조회

```
GET /api/v1/tasks/{task_id}/result
```

```json
{
  "task_id": "20260414-0001",
  "status": "SUCCESS",
  "output_path": "output/{filename}_result.xlsx",
  "summary": {}
}
```

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| 파일 미존재 | `404 Not Found` + 오류 메시지 반환 |
| 잘못된 파일 형식 | `400 Bad Request` + 검증 오류 상세 반환 |
| 처리 중 오류 | 상태 `FAIL` 로 업데이트 + 오류 내용 저장 |
| 중복 요청 | 기존 task_id 반환 (멱등성 보장) |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `{F_ID}` — {Feature명}
- 의존 Feature: (없으면 생략)
- 연관 task_type: (다른 task_type과 연계 시 명시)

## 7. 참고 자료

- PRD: `d{SP}0001_prd.md`
- 계획: `d{SP}0002_plan.md`
- CMS 2단계 구조 참조: `d43020_상세검증_cms매핑api.md`
- FastAPI 라우터 패턴: `04_api_server/routers/tasks.py`

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|

---

## 9. Spring 연동 흐름 (SCP / apl_id 연계)

> SCP(Spring Batch / 외부 연동)가 있는 경우 기재. 없으면 섹션 삭제.

```
[Spring / 외부 시스템]
    ↓ SCP 파일 다운로드 (apl_id 기반)
[04_api_server batch/]
    ↓ 파일 → input/ 저장
[task_type 처리]
    ↓ 처리 결과 → output/ 저장
[Spring / 외부 시스템]
    ↓ 결과 파일 업로드 (previous_apl_id 연계)
```

| 파라미터 | 설명 |
|---------|------|
| `apl_id` | 신청 ID — SCP 다운로드 키 |
| `previous_apl_id` | 이전 단계 결과 연계 ID (2단계 이상 시 사용) |

## 10. 상태 전이

```
READY → PROCESS → SUCCESS
                ↘ FAIL
```

| 상태 | 설명 | 다음 상태 |
|------|------|---------|
| `READY` | 작업 접수 완료, 처리 대기 | `PROCESS` |
| `PROCESS` | 배치 처리 중 | `SUCCESS` / `FAIL` |
| `SUCCESS` | 처리 완료, 결과 파일 생성됨 | 종료 |
| `FAIL` | 처리 오류 발생 | 재시도 또는 종료 |

> **DB 저장**: `api_task_queue` (접수) + `api_task_result` (결과) — `db/sene.sqlite`
