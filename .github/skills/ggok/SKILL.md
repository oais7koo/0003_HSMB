# ggok - Copilot용 ggcheck(=oocheck) alias 스킬

> ook(oocheck alias) 스킬을 Copilot 환경에서 ggcheck(=oocheck) alias로 변환

## 0. 스킬 요약

| 항목              | 내용                                                             |
| ----------------- | ---------------------------------------------------------------- |
| **핵심 역할**     | ggcheck(=oocheck) 스킬의 약어 alias — 코드 품질 체크             |
| **하는 것**       | ggcheck(=oocheck) 스킬과 동일, 전달 인자를 그대로 ggcheck에 전달 |
| **하지 않는 것**  | alias 스킬 자체는 추가 로직 없음                                 |
| **에이전트 호환** | Copilot: ggcheck를 직접 호출하는 것으로 대체 가능                |

## 1. Copilot 환경 안내

- ggok는 ggcheck(=oocheck) 스킬의 alias로, Copilot에서는 별도 로직 없이 ggcheck를 직접 호출하면 동일하게 동작
- 전달 인자 그대로 ggcheck에 전달

## 2. 사용법

- ggok [args...] → ggcheck [args...]

## 3. 참고

- oo스킬의 alias 구조와 동일하게 Copilot에서도 alias는 별도 로직 없이 원본 스킬 호출로 대체
