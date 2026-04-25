---
name: ccenv
description: "Copilot 환경에서 실제로 사용할 수 있는 도구, 플러그인 대응 기능, 제한 사항을 정리할 때 사용하는 스킬. ooenv 결과를 바탕으로 Copilot 세션 기준 사용 가능/부분 가능/사용 불가를 구분하고 d0009_ccenv.md를 생성한다. 'ccenv run', 'copilot 환경 점검', 'copilot에서 뭐를 쓸 수 있나', 'copilot capability 문서화' 요청에 적합하다."
argument-hint: "run | status | version"
user-invocable: true
---

# ccenv

## What It Does

- `ooenv` 스타일을 참고해 Copilot 세션 기준 환경 점검 결과를 정리한다.
- `00_doc/d0009_env.md`를 입력 기준으로 삼아 Copilot에서 실제로 쓸 수 있는 항목과 아닌 항목을 구분한다.
- 결과를 `00_doc/d0009_ccenv.md`에 기록한다.

## Subcommands

- `run`: Copilot 환경 기준 사용 가능/부분 가능/사용 불가 항목을 분석해 `00_doc/d0009_ccenv.md`를 생성한다.
- `status`: 입력/출력 문서 경로와 스킬 목적을 간단히 표시한다.
- `version`: 스킬 버전 정보를 표시한다.

## When To Use

- 사용자가 "Copilot에서 쓸 수 있는 것 정리해줘"라고 묻는 경우
- 사용자가 "ooenv를 Copilot 기준으로 바꿔줘"라고 요청하는 경우
- 사용자가 "현재 Copilot 환경 capability 문서 만들어줘"라고 요청하는 경우
- `d0009_env.md`는 있는데 Copilot 세션 관점의 문서가 따로 필요할 때

## Procedure

1. 먼저 `00_doc/d0009_env.md`를 기준 문서로 읽는다.
2. Copilot 세션에서 실제로 노출된 도구 계열을 기준 capability로 사용한다.
3. `ooenv` 문서 항목 중 Copilot에서 직접 대응되는 기능이 있는지 교차 판정한다.
4. 플러그인, MCP, 스킬, 보조 기능을 `사용 가능`, `부분 사용 가능`, `사용 불가/미확인`으로 구분한다.
5. 결과를 `00_doc/d0009_ccenv.md`에 Markdown 문서로 저장한다.

## Output Format

- 문서 개요
- Copilot 직접 사용 가능 기능
- `d0009_env.md` 기준 플러그인 교차 판정
- `d0009_env.md` 기준 MCP 교차 판정
- 추가로 확인된 Copilot 전용/확장 기능
- 해석 가이드

## Rules

- `d0009_env.md`의 설치 여부와 현재 Copilot 세션의 실제 사용 가능 여부를 혼동하지 않는다.
- "설치됨"과 "현재 세션에서 호출 가능"을 분리해서 적는다.
- 문서상 X인데 현재 세션에서 대체 기능이 있으면 그 차이를 명시한다.
- 결과 문서는 짧고 실무적으로 읽히게 유지한다.

## Example Prompts

- `/ccenv run`
- `copilot 환경에서 쓸 수 있는 것 정리해줘`
- `ooenv 기반으로 copilot env 문서 만들어줘`
