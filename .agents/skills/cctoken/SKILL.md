---
name: cctoken
description: "**반드시 스크립트를 직접 실행하여 결과를 그대로 출력할 것. 수동 계산 금지.**"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# cctoken - 토큰 사용량 모니터링

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 토큰 사용량 모니터링 및 리밋 도달 예측 표시 |
| **하는 것** | 5시간·주간 사용률 표시, 리밋 예측, 모델 헤더 표시 |
| **하지 않는 것** | 토큰 절약 최적화, 모델 변경, 세션 종료(→ccstop) |
| **참조 범위** | OMC HUD 캐시 파일 (`~/.codex/plugins/.usage-cache.json`) |
| **수정 대상** | 없음 (읽기·출력만) |
| **실행 레벨** | [수동] — 캐시 읽기 후 표시만 |
| **에이전트 호환** | Codex 전용 — OMC HUD 캐시 의존 / 다른 에이전트: 해당 캐시 파일이 없으면 동작 안 함 |

## 문서 이력 관리
- v02 2026-04-07 — 출력 형식 명시 및 실행 방법 추가
- v01 2026-04-03 — 최초 생성: 5시간/주간/Sonnet 사용률 표시 + 리밋 도달 예측

## 개요

OMC HUD 캐시(`~/.codex/plugins/oh-my-claudecode/.usage-cache.json`)를 읽어  
현재 토큰 사용률과 리셋 시각을 표시하고, 현재 소비 패턴 기준으로  
이번 윈도우 안에 제한에 걸릴지 예측한다.

## 실행 방법

> **반드시 스크립트를 직접 실행하여 결과를 그대로 출력할 것. 수동 계산 금지.**

```bash
uv run python .agents/skills/cctoken/scripts/ootoken_run.py status
```

## 출력 형식

스크립트 실행 결과를 그대로 마크다운으로 출력한다.

```
## cctoken — {모델명}

| 구분 | 사용률 | 여유(+) / 초과(-) |
|------|--------|-----------------|
| 5시간 | N% | ±00d00h |
| 주간 | N% | ±00d00h |
| Sonnet 주간 | N% | ±00d00h |
```

- **모델명**: `~/.codex/.omc/model-cache.json`에서 읽음 (없으면 `unknown`)
- **여유(+)**: 리셋 후에야 100% 도달 → 이번 윈도우 안전
- **초과(-)**: 리셋 전 100% 도달 예상 → 제한 위험

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `cctoken` | 현재 사용률 + 리셋 시각 + 제한 예측 |
| `cctoken status` | 동일 (status 별칭) |
| `cctoken version` | 스킬 버전 정보 (v02) |
| `cctoken help` | 도움말 |

## 예측 알고리즘

1. `fiveHourResetsAt` - 5h = 윈도우 시작 시각
2. 경과 시간 = now - 윈도우 시작
3. 소비율 = 현재% / 경과시간(h) → %/h
4. 100% 도달 예상 = now + (100 - 현재%) / 소비율
5. 도달 예상 < 리셋 시각 → 초과(-) 표시

## 데이터 소스

- **캐시 파일**: `~/.codex/plugins/oh-my-claudecode/.usage-cache.json`
- **원본 API**: `api.anthropic.com/api/oauth/usage`
- **캐시 주기**: OMC HUD 폴링 간격에 따라 수분 단위 갱신

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 관련

- OMC HUD: `oh-my-claudecode:hud`
- 환경 현황: `ccenv`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

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
| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.agents/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

