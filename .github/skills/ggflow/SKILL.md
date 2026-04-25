# ggflow 스킬 (Copilot용 ooflow 변환)

---

## 목적

- ooflow(전체 SW 개발 워크플로우 오케스트레이터) 스킬을 Copilot 환경(.github/skills/ggflow)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(단계별 자동 위임, 전체 파이프라인 자동화 등)은 명확히 안내/가이드 제공

## 핵심 역할

- SW 개발 전체 워크플로우(기획→설계→개발→검증→커밋) 오케스트레이션 워크플로우 안내
- 각 단계별 위임 스킬(oofeature, oodev, ootest, oocheck 등) 연계, 전체 흐름 문서화

## Copilot 환경 변환 원칙

- 단계별 자동 위임, 전체 파이프라인 자동화 등은 Copilot에서 직접 실행 불가 → "터미널/에이전트에서 수동 처리" 안내
- 각 단계별 워크플로우 설계, 문서화, 체크리스트 등은 Copilot에서 직접 편집/활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggflow 스킬은 전체 워크플로우 설계/문서화/체크리스트 관리에 집중
- 실제 단계별 자동 위임/전체 파이프라인 자동화 등은 반드시 터미널/에이전트에서 수동 수행
- oo스킬의 guide.md(How)는 ggflow/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 ooflow의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 전체 SW 개발 워크플로우/오케스트레이션 방법론은 references/guide.md를 참고하세요.
