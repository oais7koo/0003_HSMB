# gghwp_guide - Copilot용 한글(HWPX) 문서 생성/편집 가이드

oohwp(한글 HWPX) 스킬의 방법론(How)을 Copilot 환경에서 최대한 활용할 수 있도록 요약/가이드화한 버전입니다.

## 문서 목적

- 한글(HWPX) 문서 생성/편집/추출/검증/분석/변환 전체 워크플로우, 명령어, 출력 구조를 Copilot에서 문서로 안내
- 자동화 불가(직접 실행/제어 등) 부분은 명확히 표시, 수동 실행 절차 안내

## Copilot 환경 안내

- HWPX 생성/편집/추출/검증/분석/변환 자동화는 Copilot에서 직접 실행 불가
- 명령어/옵션/출력 구조 등은 Copilot에서 문서로 안내 가능

## 수동 워크플로우 요약

- 신규 문서 생성: `uv run --with lxml python .claude/skills/oohwp/scripts/build_hwpx.py --template gonmun ...`
- 텍스트 추출: `uv run --with lxml python .claude/skills/oohwp/scripts/text_extract.py document.hwpx [--include-tables]`
- 구조 검증: `uv run --with lxml python .claude/skills/oohwp/scripts/validate.py document.hwpx`
- 문서 분석: `uv run --with lxml python .claude/skills/oohwp/scripts/analyze_template.py document.hwpx`
- 문서 편집: unpack → XML 수정 → pack
- HWP → HWPX 변환: (Windows+한글 필요)

## 참고

- 템플릿, 옵션, 상세 예시는 oo스킬의 guide.md 참고
- Copilot에서는 자동 실행/제어 불가, 반드시 수동 실행 필요
