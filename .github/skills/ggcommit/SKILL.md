# ggcommit 스킬 (Copilot용 oocommit 변환)

---

## 목적

- oocommit(Git 커밋 및 이력 정리) 스킬을 Copilot 환경(.github/skills/ggcommit)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- Git 커밋 실행 + d{SP}0004 완료 항목 → d{SP}0010 이력 이동 통합
- git commit, push, d{SP}0004/d{SP}0010 문서 관리

## Copilot 환경 변환 원칙

- 자동화/외부 명령(git 커밋/푸시, MCP 연동 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- d{SP}0004, d{SP}0010 등 문서 편집/이력 관리 기능은 Copilot에서 직접 활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggcommit 스킬은 커밋 메시지/이력 관리, 문서 편집, 체크리스트 관리에 집중
- 실제 커밋/푸시/자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggcommit/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oocommit의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 커밋/이력 관리 방법론은 references/guide.md를 참고하세요.
