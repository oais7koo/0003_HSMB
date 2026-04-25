# ggcapture 스킬 (Copilot용 oocapture 변환)

---

## 목적

- oocapture(앱 화면 캡처) 스킬을 Copilot 환경(.github/skills/ggcapture)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- Flutter/Web 앱을 웹 빌드 후 Playwright로 화면 캡처 (PNG + HTML 저장)
- 캡처 저장 폴더 내 PNG, HTML 파일 관리

## Copilot 환경 변환 원칙

- 자동화/외부 명령(Flutter 빌드, Playwright 실행 등)은 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- 캡처 결과 파일(PNG, HTML 등)은 Copilot에서 직접 편집/활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggcapture 스킬은 캡처 결과 파일 관리, 워크플로우 안내, 옵션 가이드에 집중
- 실제 빌드/캡처/자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggcapture/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oocapture의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 캡처 방법론은 references/guide.md를 참고하세요.
