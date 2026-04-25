# ggopti - Copilot용 알고리즘/코드 최적화 스킬

> oo 스킬(ooopti) 기반, Copilot 환경에서 가능한 범위로 변환

## 0. 스킬 요약

| 항목              | 내용                                                                                                  |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| **핵심 역할**     | 알고리즘 분석 및 코드 성능 최적화 워크플로우 안내 (자동 실행 불가, 수동 가이드 제공)                  |
| **하는 것**       | 성능 프로파일링, 알고리즘 개선, 병목 분석, 최적화 코드 적용 절차 및 명령어 안내, 수동 워크플로우 안내 |
| **하지 않는 것**  | 직접 코드 자동 분석/최적화/프로파일링/리포트 생성 등 자동화                                           |
| **참조 범위**     | ooopti 워크플로우/명령어/출력 구조를 Copilot에서 문서화                                               |
| **실행 레벨**     | [수동] — 사용자가 직접 파일 분석/수정 또는 터미널 명령 실행                                           |
| **에이전트 호환** | Copilot: 문서/가이드 안내만 가능, 자동 실행 불가                                                      |

## 1. Copilot 환경 안내

- 코드 성능 분석/최적화/프로파일링/리포트 자동화는 Copilot에서 직접 실행 불가
- 전체 워크플로우/명령어/출력 구조를 문서로 안내, 사용자는 직접 파일 분석/수정 또는 터미널 명령 실행 필요
- 분석/개선/리포트 등은 Copilot에서 문서로 확인 가능

## 2. 수동 워크플로우

- 프로파일링: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py profile [대상]`
- 복잡도 분석: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py complexity [대상]`
- 벤치마크: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py benchmark [대상]`
- 최적화 적용: 코드 직접 수정
- 리포트 생성: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py report`

## 3. 참고

- 분석/개선/리포트 등은 oo스킬의 SKILL.md/guide.md 참고
- Copilot에서는 자동 실행/제어 불가, 반드시 수동 실행 필요
