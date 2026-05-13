# FastAPI 프레임워크 레퍼런스 — Overview

> 기준 프로젝트: SP04 (04_api_server) | 작성일: 2026-04-11

## 언제 이 패턴을 쓰는가

- 외부 시스템(Spring, Java 등)과 연동하는 **비동기 작업 처리 API**
- 파일 업로드 → 가공 → 결과 다운로드 패턴
- 우선순위 기반 **작업 큐** + **배치 엔진** 필요
- SCP/SFTP 등 파일 전송 연동
- 관리자 대시보드(백오피스) 포함

## 핵심 아키텍처 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | FastAPI | 비동기 네이티브, 자동 Swagger, Pydantic 검증 |
| DB | SQLite (WAL 모드) | 단일 서버, 운영 간편, 동시성 충분 |
| 배치 처리 | 이벤트 + 폴링 폴백 | 즉시 반응 + 누락 방지 |
| 파일 전송 | Paramiko (SCP/SFTP) | Python 네이티브, SSH 기반 |
| Rate Limit | slowapi | FastAPI 네이티브 통합 |
| 관리자 UI | Jinja2 템플릿 | 별도 프론트엔드 불필요 |
| 테스트 | pytest + TestClient | FastAPI 공식 권장 |

## 전체 데이터 흐름

```
외부 시스템 (POST /api/v1/tasks/xxx)
    ↓
[라우터] 요청 검증 → 파일 저장 → DB 큐 등록 → 이벤트 발신
    ↓ (비동기)
[배치 엔진] 선점 → SCP 다운로드 → 핸들러 호출 → 결과 저장 → SCP 업로드 → 상태 동기화
    ↓
[조회] GET /status → GET /file (결과 다운로드)
```

## 레퍼런스 문서 목록

| # | 문서 | 내용 |
|---|------|------|
| 01 | directory_structure | 표준 디렉토리 구조 |
| 02 | config_pattern | 환경별 설정 분기 |
| 03 | main_app | lifespan, 미들웨어, 라우터 등록 |
| 04 | routers | 엔드포인트 설계 패턴 |
| 05 | models_schemas | DB 스키마 + Pydantic |
| 06 | batch_engine | 이벤트+폴링 배치 |
| 07 | error_handling | 3계층 에러 핸들링 |
| 08 | testing | 테스트 구조 및 fixture |
| 09 | admin_dashboard | Jinja2 백오피스 |
| 10 | external_integration | SCP, 외부 DB 연동 |
