---
name: ood
description: "oodev 스킬의 약어 alias. 'ood'로 호출하면 oodev와 동일하게 동작한다"
metadata:
  version: v01
  category: core-dev
---

이 스킬은 **`oodev`의 약어 alias**입니다.

전달된 인자(`$ARGUMENTS`)를 그대로 유지하여 **즉시 `oodev` 스킬을 실행**하세요.
Skill 도구로 `oodev`를 호출하고 `$ARGUMENTS`를 args로 전달합니다.

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)


## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | `oodev` 스킬의 약어 alias — TDD 기반 개발 |
| **하는 것** | `oodev` 스킬과 동일 |
| **하지 않는 것** | alias 스킬 자체는 추가 로직 없음 |
| **에이전트 호환** | 범용 — `oodev`을 직접 호출하는 것으로 대체 가능 |

