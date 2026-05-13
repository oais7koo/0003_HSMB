# gghwp - Copilot용 한글(HWPX) 문서 생성/편집 스킬

> oo 스킬(oohwp) 기반, Copilot 환경에서 가능한 범위로 변환

## 0. 스킬 요약

| 항목              | 내용                                                                              |
| ----------------- | --------------------------------------------------------------------------------- |
| **핵심 역할**     | 한글(HWPX) 문서 생성·편집·읽기 워크플로우 안내 (자동 실행 불가, 수동 가이드 제공) |
| **하는 것**       | HWPX 생성/편집/추출/검증/분석/변환 절차 및 명령어 안내, 수동 실행법 안내          |
| **하지 않는 것**  | 직접 HWPX 생성/편집/추출/검증/분석/변환 자동화, 한글 앱 직접 제어                 |
| **참조 범위**     | oo스킬의 워크플로우/명령어/출력 구조를 Copilot에서 문서화                         |
| **실행 레벨**     | [수동] — 사용자가 터미널에서 직접 명령 실행                                       |
| **에이전트 호환** | Copilot: 문서/가이드 안내만 가능, 자동 실행 불가                                  |

## 1. Copilot 환경 안내

- HWPX 생성/편집/추출/검증/분석/변환 자동화는 Copilot에서 직접 실행 불가
- 전체 워크플로우/명령어/출력 구조를 문서로 안내, 사용자는 터미널에서 직접 실행 필요
- 템플릿/옵션/출력 구조 등은 Copilot에서 문서로 확인 가능

## 2. 수동 워크플로우

- 신규 문서 생성: `uv run --with lxml python .claude/skills/oohwp/scripts/build_hwpx.py --template gonmun ...`
- 텍스트 추출: `uv run --with lxml python .claude/skills/oohwp/scripts/text_extract.py document.hwpx [--include-tables]`
- 구조 검증: `uv run --with lxml python .claude/skills/oohwp/scripts/validate.py document.hwpx`
- 문서 분석: `uv run --with lxml python .claude/skills/oohwp/scripts/analyze_template.py document.hwpx`
- 문서 편집: unpack → XML 수정 → pack
- HWP → HWPX 변환: (Windows+한글 필요)

## 3. 참고

- 템플릿, 옵션, 상세 예시는 oo스킬의 SKILL.md/guide.md 참고
- Copilot에서는 자동 실행/제어 불가, 반드시 수동 실행 필요
