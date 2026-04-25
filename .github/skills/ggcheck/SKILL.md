# ggcheck 스킬 (Copilot용 oocheck 변환)

---

## 목적

- oocheck(코드 품질 체크) 스킬을 Copilot 환경(.github/skills/ggcheck)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(정적 분석, 자동화 등)은 명확히 안내/가이드 제공

## 핵심 역할

- 코드 정적 분석 및 품질 체크(파이썬/플러터)
- py_compile, pylint, mypy, pytest 등 품질 검증 루틴 안내
- d{SP}0004_todo.md 이슈 등록/관리

## Copilot 환경 변환 원칙

- 정적 분석/자동화 명령(py_compile, pylint 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 실행" 안내
- d{SP}0004_todo.md 등 문서 편집/이슈 관리 기능은 Copilot에서 직접 활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggcheck 스킬은 코드 품질 체크, 이슈 등록/관리, 체크리스트 편집에 집중
- 실제 정적 분석/품질 검증은 반드시 터미널에서 수동 실행
- oo스킬의 guide.md(How)는 ggcheck/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oocheck의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 품질 체크 방법론은 references/guide.md를 참고하세요.
