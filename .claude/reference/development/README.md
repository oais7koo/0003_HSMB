# 프레임워크 레퍼런스

개발 시 참고하는 프레임워크별 아키텍처 패턴 및 표준 구조.

## 사용법

- 대상 프로젝트가 알려진 프레임워크를 사용하는 경우 해당 레퍼런스를 사전 로드
- 스킬(ooplan, oodev, oofeature, oocheck, ootest)이 자동 참조

## 프레임워크 목록

| 프레임워크 | 경로 | 기준 프로젝트 | 상태 |
|-----------|------|-------------|------|
| **FastAPI** | `fast-api/` | SP04 (04_api_server) | 활성 |

## 감지 규칙

| 프레임워크 | 감지 조건 |
|-----------|----------|
| FastAPI | `from fastapi import` 또는 `main.py` + `routers/` 존재 |
| Django | `manage.py` + `settings.py` 존재 |
| Streamlit | `import streamlit` 또는 `pages/*.py` 존재 |

## 레퍼런스 문서 구조

각 프레임워크 폴더는 동일한 번호 체계:

```
00_overview.md           # 언제/왜 이 패턴을 쓰는가
01_directory_structure.md # 표준 디렉토리 구조
02_config_pattern.md     # 환경별 설정 분기
03_main_app.md           # 앱 초기화, 미들웨어, 라우터
04_routers.md            # 엔드포인트 설계 패턴
05_models_schemas.md     # DB 스키마 + 데이터 모델
06_batch_engine.md       # 비동기 작업 처리 패턴
07_error_handling.md     # 에러 핸들링 계층
08_testing.md            # 테스트 구조 및 fixture
09_admin_dashboard.md    # 관리자 UI 패턴
10_external_integration.md # 외부 시스템 연동
11_menu_structure.md      # 전체 메뉴 구성도 (URL 맵)
12_dashboard_data.md     # 대시보드 데이터 표시 및 정리
```
