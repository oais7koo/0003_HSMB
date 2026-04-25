# gglib_guide - Copilot용 oo 모듈 수정/최적화 가이드

oolib(oo 모듈 수정/최적화) 스킬의 방법론(How)을 Copilot 환경에서 최대한 활용할 수 있도록 요약/가이드화한 버전입니다.

## 문서 목적

- oo/\*.py 모듈의 문제점 분석/기록/수정/검증/문서화 전체 워크플로우, 명령어, 출력 구조를 Copilot에서 문서로 안내
- 자동화 불가(직접 실행/제어 등) 부분은 명확히 표시, 수동 실행 절차 안내

## Copilot 환경 안내

- oo 모듈 분석/수정/이슈 이동/문서화 자동화는 Copilot에서 직접 실행 불가
- 명령어/분석/수정/이슈 기록/문서화 등은 Copilot에서 문서로 안내 가능

## 수동 워크플로우 요약

- 분석: `pylint -E oo/`, `uv run python -m py_compile oo/*.py`
- 이슈 기록: 00_doc/d{SP}0004_todo.md에 [FIX] 태그로 등록
- 수정: 각 파일별/이슈별로 직접 코드 수정
- 검증: py_compile, pytest 등 수동 실행
- 문서화: d0005_lib.md 직접 업데이트

## 참고

- 주요 에러 유형, 분석/수정 절차, 병렬 처리 등은 oolib의 guide.md 참고
- Copilot에서는 자동 실행/제어 불가, 반드시 수동 실행 필요
