---
name: ccbatch
description: "**관련 명령어**: analyze, implement (`.claude/commands/sc/`)"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 모든 oo* 스킬에 동일한 서브명령어 일괄 실행 |
| **하는 것** | oo* SKILL.md 스캔 → 서브명령어 보유 스킬 탐지 → 일괄 실행 |
| **하지 않는 것** | 개별 스킬 로직 수정, 코드 변경 |
| **참조 범위** | `.claude/skills/oo*/SKILL.md` 전체 |
| **수정 대상** | 없음 (실행만) |
| **실행 레벨** | [자동] — 스캔 후 일괄 실행 |
| **에이전트 호환** | 범용 |

## 문서 이력 관리
- v01 2026-04-19 — 최초 생성

## 1. 개요

`ccbatch <subcmd>` 형식으로 모든 oo* 스킬 중 해당 서브명령어를 가진 스킬을 자동 탐지하여 일괄 실행한다.

```
ccbatch check        → check 서브명령어가 있는 모든 oo* 스킬에서 check 실행
ccbatch check --fix  → check --fix 서브명령어가 있는 모든 oo* 스킬에서 check --fix 실행
```

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ccbatch <subcmd>` | 해당 서브명령어 보유 스킬 전체 실행 | 터미널 |
| `ccbatch list <subcmd>` | 해당 서브명령어 보유 스킬 목록만 출력 | 터미널 |
| `ccbatch help` | 도움말 | 터미널 |

실행: `uv run python .claude/skills/ccbatch/scripts/oobatch_run.py [subcmd] [args]`

## 3. 실행 방식

1. `.claude/skills/oo*/SKILL.md` 전체 스캔
2. 서브명령어 테이블에서 `<subcmd>` 보유 스킬 탐지
3. 스킬별 스크립트(`{skill}_run.py`) 존재 여부 확인
4. 스크립트 있는 스킬 → `uv run python` 실행
5. 스크립트 없는 스킬 → SKIP 표시 (Claude 오케스트레이션 필요)
6. 결과 요약 리포트

## 4. 결과 상태

| 상태 | 의미 |
|------|------|
| ✅ OK | 정상 실행 완료 |
| ⏭ SKIP | 스크립트 없음 (Claude가 직접 실행 필요) |
| ❌ FAIL | 실행 실패 |
| ⏱ TIMEOUT | 120초 초과 |

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 5. 예시

```bash
# check 서브명령어 일괄 실행
ccbatch check

# check --fix 일괄 실행
ccbatch check --fix

# check 지원 스킬 목록 확인
ccbatch list check
```

<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->
