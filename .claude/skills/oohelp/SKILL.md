---
name: oohelp
description: "명령어/스킬 도움말 스킬 'oohelp', '도움말', '명령어 목록', '스킬 목록' 등을 요청할 때 트리거된다"
metadata:
  version: "v02"
  category: "meta-util"
---

# oohelp - 명령어/스킬 도움말

> 공통 가이드: `.claude/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | oo 스킬·명령어 목록 및 도움말 표시 |
| **하는 것** | 스킬 목록 출력, 명령어 설명 표시, 카테고리별 안내 |
| **하지 않는 것** | 스킬 실행, 파일 수정, 환경 변경 |
| **참조 범위** | `.claude/skills/` 스킬 파일 목록 / 외부 문서 자동 포함 안 함 |
| **수정 대상** | 없음 (출력만) |
| **실행 레벨** | [수동] — 도움말 출력만 |
| **에이전트 호환** | 범용 — 스킬 목록 파일 읽기 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v03 2026-04-07 — 마스터 문서 d0007 → .claude/CLAUDE.md 스킬 카탈로그로 변경
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 개요

**역할**: `.claude/CLAUDE.md` OAIS 스킬 카탈로그 표시

CLAUDE.md의 "OAIS 스킬 및 에이전트 카탈로그" 섹션이 모든 스킬·에이전트 정보의 SSOT입니다.  
세션마다 자동 로드되므로 항상 최신 상태가 유지됩니다.

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oohelp help` | 서브명령어 목록 표시 |
| `oohelp version` | 스킬 버전 정보 (v03) |
| `oohelp status` | 서브명령어 리스트, 현재 상태 |
| `oohelp check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oohelp run` | 도움말 생성 |
| `oohelp show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oohelp add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oohelp` | CLAUDE.md 스킬 카탈로그 전체 표시 |
| `oohelp [카테고리]` | 특정 카테고리만 표시 (예: oo, agent, command) |
| `oohelp [스킬명]` | 특정 스킬 상세 (.claude/skills/oo*/SKILL.md 참조) |

## CLAUDE.md 카탈로그 구조

| 섹션 | 내용 |
|------|------|
| oo 스킬 | 카테고리별 47개 스킬 (core-dev / doc-env / meta-util / content) |
| 범용 명령어 | sc/ 명령어 (analyze, build, implement 등) |
| 에이전트 | .claude/agents/ 전문 서브에이전트 |

## 실행

```bash
# CLAUDE.md 스킬 카탈로그 전체 표시
oohelp

# 특정 카테고리
oohelp oo       # OAIS 스킬만
oohelp agent    # 에이전트만
oohelp command  # 범용 명령어만

# 특정 스킬 상세
oohelp oodev    # .claude/skills/oodev/SKILL.md 내용 표시
```

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
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

## 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/CLAUDE.md` | OAIS 스킬 및 에이전트 카탈로그 (SSOT) |
| `.claude/skills/oo*/SKILL.md` | 개별 스킬 상세 정의 |
| `.claude/guides/common_guide.md` | 공통 가이드라인 |
