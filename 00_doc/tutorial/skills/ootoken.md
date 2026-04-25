# ootoken Tutorial

> 토큰 사용량 모니터링 및 리밋 도달 예측 | 버전: v03 | 카테고리: meta-util

## 1. 이 스킬은 왜 필요한가?

5시간 윈도우 및 주간 토큰 사용률을 실시간으로 표시하고, 리밋 도달 예상 시각을 계산합니다. 토큰 한도 접근 시 사전에 최적화 방안을 제시합니다.

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ootoken run

# 상태 확인
ootoken status

# 도움말
ootoken help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootoken` | 현재 사용률 + 리셋 시각 + 제한 예측 |
| `ootoken status` | 동일 (status 별칭) |
| `ootoken version` | 스킬 버전 정보 (v02) |
| `ootoken help` | 도움말 |

## 4. 상세 사용법

### 실행 방법

> **반드시 스크립트를 직접 실행하여 결과를 그대로 출력할 것. 수동 계산 금지.**

```bash
uv run python .claude/skills/ootoken/scripts/ootoken_run.py status
```

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 토큰 사용량 모니터링 및 리밋 도달 예측 표시 |
| **하는 것** | 5시간·주간 사용률 표시, 리밋 예측, 모델 헤더 표시 |
| **하지 않는 것** | 토큰 절약 최적화, 모델 변경, 세션 종료(→oostop) |
| **참조 범위** | OMC HUD 캐시 파일 (`~/.claude/plugins/.usage-cache.json`) |
| **수정 대상** | 없음 (읽기·출력만) |
| **실행 레벨** | [수동] — 캐시 읽기 후 표시만 |
| **에이전트 호환** | Claude Code 전용 — OMC HUD 캐시 의존 / 다른 에이전트: 해당 캐시 파일이 없으면 동작 안 함 |

### 출력 형식

스크립트 실행 결과를 그대로 마크다운으로 출력한다.

```

### ootoken — {모델명}

| 구분 | 사용률 | 여유(+) / 초과(-) |
|------|--------|-----------------|
| 5시간 | N% | ±00d00h |
| 주간 | N% | ±00d00h |
| Sonnet 주간 | N% | ±00d00h |
```

- **모델명**: `~/.claude/.omc/model-cache.json`에서 읽음 (없으면 `unknown`)
- **여유(+)**: 리셋 후에야 100% 도달 → 이번 윈도우 안전
- **초과(-)**: 리셋 전 100% 도달 예상 → 제한 위험

### 예측 알고리즘

1. `fiveHourResetsAt` - 5h = 윈도우 시작 시각
2. 경과 시간 = now - 윈도우 시작
3. 소비율 = 현재% / 경과시간(h) → %/h
4. 100% 도달 예상 = now + (100 - 현재%) / 소비율
5. 도달 예상 < 리셋 시각 → 초과(-) 표시

### 데이터 소스

- **캐시 파일**: `~/.claude/plugins/oh-my-claudecode/.usage-cache.json`
- **원본 API**: `api.anthropic.com/api/oauth/usage`
- **캐시 주기**: OMC HUD 폴링 간격에 따라 수분 단위 갱신

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ootoken run
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/ootoken/scripts/ootoken_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

(서브에이전트 정보 없음)

## 10. 관련 스킬

- OMC HUD: `oh-my-claudecode:hud`
- 환경 현황: `ooenv`

---

> 생성일: 2026-04-14 11:32 | ootutorial v03
