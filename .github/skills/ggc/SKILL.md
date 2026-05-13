# ggc 스킬 (Copilot용 ooc 변환)

---

## 목적

- ooc(oocontext alias) 스킬을 Copilot 환경(.github/skills/ggc)에서 최대한 활용 가능하도록 요약/가이드화
- Copilot에서 직접 실행 불가한 부분(자동화, 외부 명령 등)은 명확히 안내/가이드 제공

## 핵심 역할

- oocontext 스킬의 약어 alias — 서브프로젝트 컨텍스트 전환
- 전달된 인자를 그대로 유지하여 oocontext 스킬을 실행

## Copilot 환경 변환 원칙

- alias 스킬 자체는 추가 로직 없음, oocontext 스킬과 동일하게 동작
- Copilot에서는 oocontext 스킬을 직접 호출하거나, 컨텍스트 전환 가이드로 활용

## 사용법

- ggc 스킬은 oocontext 스킬의 alias로, 컨텍스트 전환이 필요할 때 사용
- 실제 컨텍스트 전환/자동화는 반드시 터미널에서 수동 수행

## 참고

- oo스킬의 alias 기능은 Copilot 환경에서는 수동 처리 필요
- Copilot에서 직접 실행 불가한 부분은 반드시 수동 처리

---

> 본 스킬은 ooc(oocontext alias)의 핵심 기능을 Copilot 환경에 맞게 요약/가이드화한 버전입니다. 자세한 컨텍스트 전환 방법론은 oocontext/ggcontext 스킬을 참고하세요.
