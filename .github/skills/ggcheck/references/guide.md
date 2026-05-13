# ggcheck_guide - Copilot용 코드 품질 체크 가이드

oocheck(코드 품질 체크) 스킬의 방법론(How)을 Copilot 환경에서 최대한 활용할 수 있도록 요약/가이드화한 버전입니다.

## 문서 목적

- 코드 정적 분석(py_compile, pylint, mypy, pytest 등) 루틴 안내
- d{SP}0004_todo.md 이슈 등록/관리
- 체크리스트 관리

## Copilot 환경 안내

- 정적 분석/자동화 명령은 Copilot에서 직접 실행 불가 → 반드시 터미널에서 실행
- 문서 편집/이슈 관리/체크리스트 등은 Copilot에서 직접 편집 가능

## 워크플로우 요약

1. d{SP}0004_todo.md(이슈/체크리스트) 작성/편집
2. 코드 품질 체크(py_compile, pylint, mypy, pytest 등)는 터미널에서 수동 실행
3. 결과를 문서에 반영/관리

## 참고

- 자세한 품질 체크 방법론, 예시 등은 oo스킬의 guide.md를 참조
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리
