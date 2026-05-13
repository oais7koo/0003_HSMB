# ggdeep 스킬 (Copilot용 oodeep 변환)

---

## 목적

- oodeep(딥러닝 GPU 효율성 최적화) 스킬을 Copilot 환경(.github/skills/ggdeep)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(GPU 모니터링, 자동 실행/최적화 등)은 명확히 안내/가이드 제공

## 핵심 역할

- PyTorch 딥러닝 코드 GPU 효율성 모니터링 및 최적화 워크플로우 안내
- 실행→모니터링→판단→최적화→재실행 반복 사이클 문서화

## Copilot 환경 변환 원칙

- GPU 모니터링/자동 실행/최적화 등은 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- 코드 최적화, 워크플로우 설계, 체크리스트 등은 Copilot에서 직접 편집/활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggdeep 스킬은 딥러닝 코드 최적화 워크플로우, 체크리스트, 코드 개선 가이드에 집중
- 실제 실행/모니터링/자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggdeep/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oodeep의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 딥러닝 최적화 방법론은 references/guide.md를 참고하세요.
