# ggdb 스킬 (Copilot용 oodb 변환)

---

## 목적

- oodb(DB 수정 및 최적화) 스킬을 Copilot 환경(.github/skills/ggdb)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(DB 마이그레이션, 쿼리 실행 등)은 명확히 안내/가이드 제공

## 핵심 역할

- DB 문제 발견→기록→수정 3단계 워크플로우 안내
- 스키마 검증, 마이그레이션, DB 이슈 관리, d{SP}0004 등록 등 문서화

## Copilot 환경 변환 원칙

- DB 쿼리 실행/마이그레이션 등 자동화는 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- DB 이슈 기록, 스키마 설계, 문서화 등은 Copilot에서 직접 편집/활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggdb 스킬은 DB 이슈 관리, 스키마 설계, 문서화, 체크리스트 관리에 집중
- 실제 쿼리 실행/마이그레이션/자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggdb/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oodb의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 DB 관리/최적화 방법론은 references/guide.md를 참고하세요.
