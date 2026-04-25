# ggfix 스킬 (Copilot용 oofix 변환)

---

## 목적

- oofix(코드 오류 자동 개선) 스킬을 Copilot 환경(.github/skills/ggfix)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- d{SP}0004_todo.md의 이슈(Active Issues) 자동/수동 개선
- 코드 오류, 버그, 이슈를 단계별로 분석·수정·검증
- 이슈 해결 후 d{SP}0010_history.md로 이동

## Copilot 환경 변환 원칙

- 자동화/외부 명령(자동 수정, 배치 실행 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- d{SP}0004_todo.md, d{SP}0010_history.md 등 문서 편집/이슈 관리 기능은 Copilot에서 직접 활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggfix 스킬은 이슈/버그/오류 관리, 문서 편집, 개선 내역 기록에 집중
- 실제 자동화/배치 실행은 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggfix/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oofix의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 오류 개선 방법론은 references/guide.md를 참고하세요.
