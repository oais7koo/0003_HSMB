---
name: ccs
description: "**관련 명령어**: analyze, implement (`.claude/commands/sc/`)"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

이 스킬은 **`oostart`의 약어 alias**입니다.

전달된 인자(`$ARGUMENTS`)를 그대로 유지하여 **즉시 `oostart` 스킬을 실행**하세요.
Skill 도구로 `oostart`를 호출하고 `$ARGUMENTS`를 args로 전달합니다.

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)


## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | `oostart` 스킬의 약어 alias — 세션 시작 워크플로우 |
| **하는 것** | `oostart` 스킬 실행 + 완료 후 SP 선택 프롬프트 |
| **하지 않는 것** | 파일 수정, 코드 실행 |
| **에이전트 호환** | 범용 — `oostart`을 직접 호출하는 것으로 대체 가능 |

## 실행 후 처리 (필수)

`oostart` 스크립트 실행이 완료되면 **반드시** 아래 순서로 처리하세요:

1. 스크립트 출력 결과를 간략히 요약 표시
2. 스크립트 출력의 "0-1. Subproject Status" 섹션을 파싱하여 **실제 존재하는 SP(Active 상태)** 목록을 추출:
   - `Active` 상태인 SP만 테이블에 표시 (SP00 공통은 항상 포함)
   - 서브프로젝트가 하나도 없으면 ("Active: 0") SP 선택 테이블을 생략하고 "서브프로젝트 없음" 안내
   - 예시 형식:
     ```
     | 번호 | SP   | 폴더           |
     |------|------|----------------|
     | 0    | SP00 | 공통           |
     | 1    | SP01 | 01_obsidian    |  ← Active인 경우만
     ```
3. Active SP가 있는 경우에만: "**작업할 서브프로젝트 번호를 선택하세요 (Enter=현재 유지):**" 질문
4. 사용자 입력값 N을 받아 즉시 `oocontext N` 실행 (Skill 도구로 `oocontext` 호출, args=N)
5. Enter(빈 입력) 또는 Active SP 없음 → 현재 컨텍스트 유지 (oocontext 호출 생략)

