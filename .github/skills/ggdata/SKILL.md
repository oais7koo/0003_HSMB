# ggdata 스킬 (Copilot용 oodata 변환)

---

## 목적

- oodata(data/ 폴더 백업·복원) 스킬을 Copilot 환경(.github/skills/ggdata)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(파일 이동, 외부 경로 복원 등)은 명확히 안내/가이드 제공

## 핵심 역할

- data/ 폴더 내 실험 데이터 백업/복원/현황 조회 안내
- 백업 정책, 마커 폴더, 폴더 구조 등 문서화

## Copilot 환경 변환 원칙

- 파일 이동/복원 등 자동화는 Copilot에서 직접 실행 불가 → "터미널에서 수동 처리" 안내
- 폴더 구조, 마커 정책, 현황 조회 등은 Copilot에서 직접 편집/활용 가능
- oo스킬의 상세 가이드(guide.md)는 Copilot에서 읽기/참조용으로 제공

## 사용법

- ggdata 스킬은 폴더 구조/마커 정책/백업 정책 안내, 현황 조회, 문서 편집에 집중
- 실제 백업/복원/자동화는 반드시 터미널에서 수동 수행
- oo스킬의 guide.md(How)는 ggdata/references/guide.md로 제공

## 참고

- oo스킬의 자동화 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 oodata의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 백업/복원 정책 및 방법론은 references/guide.md를 참고하세요.
