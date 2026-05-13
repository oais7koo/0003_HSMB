# Streamlit 백오피스 개요

> SP04(04_backoffice) 기준 레퍼런스. Streamlit 기반 내부 관리자 도구 패턴.

## 기술 스택

| 항목 | 내용 |
|------|------|
| 프레임워크 | Streamlit (2.24+) |
| 언어 | Python 3.13+ |
| 패키지 관리 | uv |
| DB | SQLite (oais.db 모듈) |
| 인증 | bcrypt + session_state |
| 공용 모듈 | oais/ (프로젝트 루트) |

## 서브프로젝트 목록

| SP | 디렉토리 | 역할 | 포트 |
|----|----------|------|------|
| SP04 | `04_backoffice/` | 데이터 수집/관리 백오피스 | 8501(개발) / 8022(운영) |

## 핵심 설계 원칙

1. **pages/ 자동 네비게이션**: 파일명 규칙으로 사이드바 자동 생성
2. **oais 공용 모듈**: 인증·DB·UI를 oais 모듈로 통일
3. **session_state 상태 머신**: 장시간 작업(배치/크롤링) 상태 관리
4. **환경 분리**: 포트 기반 개발/운영 자동 감지
5. **권한 체크**: 모든 페이지 진입부에서 즉시 검증

## 문서 목록

| 파일 | 내용 |
|------|------|
| `01_app_structure.md` | 디렉토리 구조, 진입점 |
| `02_config_pattern.md` | 설정 패턴 (BaseConfig, 환경 분리) |
| `03_page_patterns.md` | 페이지 표준 패턴 (탭, CRUD, 폼, 권한) |
| `04_navigation.md` | 네비게이션/메뉴 구조 |
| `05_oais_integration.md` | oais 모듈 연동 |
| `06_session_auth.md` | 세션/인증 패턴 |
| `07_batch_state.md` | 배치/상태 머신 패턴 |
