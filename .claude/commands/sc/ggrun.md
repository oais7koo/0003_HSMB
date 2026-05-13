---
name: ggrun
aliases: [/ggrun]
description: "ggrun <명령어>를 실행하고, 결과를 00_doc/yyy.md에 기록하는 Copilot 명령어 스킬"
category: util
---

# /ggrun Copilot 명령어

- 사용법: `/ggrun <명령어>`
- 동작: 입력 명령어를 `.claude/skills/ggrun/scripts/ggrun_run.py`로 전달하여 실행, 결과를 00_doc/yyy.md에 기록

## 내부 실행 방식

- 입력 예시: `/ggrun ls -al`
- 실제 실행: `uv run python .claude/skills/ggrun/scripts/ggrun_run.py ls -al`

## 참고
- 위험 명령(삭제 등)은 직접 확인 필요
- 로그는 00_doc/yyy.md에 누적
