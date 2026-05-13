# ggbatch 스킬 (Copilot용 oobatch 변환)

---

## 목적

- oobatch(oo\* 스킬 일괄 실행) 스킬을 Copilot 환경(.github/skills/ggbatch)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- 모든 gg\* 스킬에 동일한 서브명령어 일괄 실행(이론적)
- SKILL.md 스캔, 서브명령어 탐지, 일괄 실행 가이드

## Copilot 환경 변환 원칙

- 자동화/외부 명령(일괄 실행, 스크립트 실행 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- SKILL.md, 서브명령어 목록 등은 Copilot에서 직접 편집/참조 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggbatch 스킬은 gg\* 스킬의 서브명령어 목록/구조 관리, 일괄 실행 가이드에 집중
- 실제 일괄 실행/자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggbatch/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oobatch의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 일괄 실행 방법론은 references/guide.md를 참고하세요.
