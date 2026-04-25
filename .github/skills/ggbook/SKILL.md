# ggbook 스킬 (Copilot용 oobook 변환)

---

## 목적

- oobook(도서 서머리 생성) 스킬을 Copilot 환경(.github/skills/ggbook)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- 도서 내용을 구조화된 서머리 MD 문서로 생성/관리
- 챕터별 요약, 핵심 개념 정리, 서머리 → Word 변환 등

## Copilot 환경 변환 원칙

- 자동화/외부 명령(Agent 위임, Word 변환 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- 서머리 MD 파일 등은 Copilot에서 직접 편집/활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggbook 스킬은 도서 서머리 MD 문서 생성/편집, 챕터별 요약, 체크리스트 관리에 집중
- 실제 Agent 위임, Word 변환 등은 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggbook/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oobook의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 도서 서머리 생성 방법론은 references/guide.md를 참고하세요.
