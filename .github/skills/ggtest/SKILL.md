# ggtest 스킬 (Copilot용 ootest 변환)

---

## 목적

- ootest(통합 테스트) 스킬을 Copilot 환경(.github/skills/ggtest)에서 최대한 활용 가능하도록 변환/요약
- Copilot에서 직접 실행 불가한 부분은 명확히 안내/가이드 제공

## 핵심 역할

- TDD RED 단계: 테스트 코드(TC) 작성 및 pytest 반복 실행(통과 시까지)
- 테스트 시나리오/체크리스트 관리(d{SP}0003_test.md)
- tests/TC\*.py 파일 관리

## Copilot 환경 변환 원칙

- pytest 등 외부 명령 직접 실행 불가 → "테스트 실행은 터미널에서 `uv run pytest`로 수동 실행" 안내
- d{SP}0003_test.md, tests/TC\*.py 등은 Copilot에서 직접 편집/생성 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggtest 스킬은 Copilot 환경에서 테스트 코드 작성, 시나리오 관리, 체크리스트 편집에 집중
- 실제 테스트 실행은 반드시 터미널에서 `uv run pytest` 명령으로 수동 수행
- oo스킬의 guide.md(How)는 ggtest/references/guide.md로 제공

## 참고

- oo스킬의 Part D/E 등 자동화 기능은 Copilot 환경에서는 수동으로 처리해야 함
- Copilot에서 직접 실행 불가한 부분은 명확히 안내/가이드로 대체

---

> 본 스킬은 oo스킬(ootest)의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 테스트 방법론은 references/guide.md를 참고하세요.
