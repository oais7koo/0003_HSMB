# ggdev 스킬 (Copilot용 oodev 변환)

---

## 목적

- oodev(TDD 기반 개발) 스킬을 Copilot 환경(.github/skills/ggdev)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- TDD GREEN 단계: 테스트 통과 최소 코드 작성 및 리팩터링
- d{SP}0003_test.md 테스트 문서 생성/관리
- 구현 코드 파일 관리

## Copilot 환경 변환 원칙

- 자동화/외부 명령(테스트 자동 실행 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 실행" 안내
- d{SP}0003_test.md 등 문서 편집/테스트 관리 기능은 Copilot에서 직접 활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggdev 스킬은 테스트 문서/구현 코드/리팩터링 관리에 집중
- 실제 테스트 실행 및 자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggdev/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oodev의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 개발 방법론은 references/guide.md를 참고하세요.
