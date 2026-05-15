# oocheck Tutorial

> Python/Flutter 코드 정적 분석·품질 체크·이슈 자동 등록 | 최종 업데이트: 2026-04-29

## 개요

py_compile→import 가용성→AST 스캔→pylint→mypy→pytest 검증 체인을 실행하고, 발견된 이슈를 `d{SP}0004_todo.md`에 자동 등록하는 스킬. 코드 수정 없이 이슈 등록만 담당(수정은 oofix). Python/Flutter 프로젝트 자동 감지.

**Streamlit 특이사항**: `pages/*.py`에서 `st.*` API 오용(잘못된 파라미터 등)은 pylint/mypy로 감지 불가 → Playwright E2E 렌더링으로만 감지 → `oocheck run` 시 E2E 추가 실행.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oocheck run` | 전체 코드 품질 분석 실행 |
| `oocheck run dXXXX` | 상세 문서 기반 관련 코드만 체크 (oofeature 연동) |
| `oocheck run this` | 직전 작업 파일만 체크 |
| `oocheck update` | d0004_todo.md / d0010_history.md 정리·동기화 |
| `oocheck oo` | oo 모듈 전용 체크 |
| `oocheck error` | 에러 전용 체크 |
| `oocheck term` | 표준용어 체크 |
| `oocheck debug [에러]` | 심층 디버깅 |
| `oocheck debug --trace` | 실행 추적 활성화 |
| `oocheck debug --fix` | 디버깅 후 자동 수정 시도 |
| `oocheck circular [모듈]` | 순환 참조 감지 |
| `oocheck status` | 체크 대상 현황 및 최근 이슈 |

## 주요 사용 예시

```bash
# 전체 코드 체크 후 이슈 d0004에 등록
oocheck run

# 특정 상세 문서 기반 코드만 체크 (개발→검증 단계 전환 시)
oocheck run d41010

# 직전 수정 파일만 체크
oocheck run this

# 순환 참조 감지
oocheck circular

# 심층 디버깅
oocheck debug "AttributeError: 'NoneType' object has no attribute 'run'"
```

## 워크플로우

**Python 검증 체인**:
```
py_compile [필수]
  → import 가용성 확인 (ModuleNotFoundError 감지)
  → AST 스캔 (함수 내부 import 스코프 오류 — UnboundLocalError 위험 패턴)
  → 동적 sys.path 파일 별도 subprocess 실행 검증
  → pylint && mypy
  → pytest
  → Streamlit pages 포함 시: E2E 렌더링 (Playwright)
  → 이슈 → d{SP}0004_todo.md 등록
```

**함수 내부 import 스코프 오류 감지**: 함수 내부에 `import module`이 있고 그 위에 `module.*` 사용 시 런타임 UnboundLocalError 발생 — AST로 탐지하여 [ERROR]로 등록.

**이슈 분류**: [CRITICAL] 즉시 / [ERROR] 24h / [WARNING] 1주 / [INFO] 백로그

**체크 제외 경로**: data/, tmp/, db/, .git/, `__pycache__/`, node_modules/, `*.g.dart`, `*.freezed.dart`

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oofix` | 발견된 이슈 자동 수정 |
| `ootest` | 테스트 실행 (Part A 정적분석 연계) |
| `oofeature` | `oocheck run dXXXX`으로 단계 연동 |
| `ootodo` | 이슈 등록된 d0004 관리 |
