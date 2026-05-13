---
name: gemma
description: "로컬 Gemma4 SLM 에이전트 (mlx-lm, localhost:8080). 'gemma', '로컬 LLM', 'SLM', 'gemma4', '로컬 모델' 키워드 또는 로컬 AI 추론 요청 시 트리거된다."
metadata:
  version: "v03"
  category: "meta-util"
---

# gemma - 로컬 Gemma4 SLM 에이전트

> 공통: `.claude/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 로컬 mlx-lm 서버(localhost:8080)의 Gemma4 SLM을 활용한 일반 에이전트 |
| **하는 것** | 단일 프롬프트 추론, 인터랙티브 채팅, 서버 상태 확인 |
| **하지 않는 것** | 모델 설치/다운로드(→ooenv), 코드 구현(→oodev), 외부 API 호출 |
| **참조 범위** | localhost:8080 (mlx-lm 서버) — 외부 네트워크 없음 |
| **수정 대상** | 없음 (추론 전용) |
| **실행 레벨** | [반자동] — 프롬프트 입력 후 자동 추론 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 스크립트 실행 |

## 문서 이력 관리
- v03 2026-04-17 — oo 스킬 화이트리스트 도입 (`gemma <skill> "프롬프트"`, `gemma whitelist`)
- v02 2026-04-17 — 호출 로그 기능 추가 (`--caller`, `gemma log`, 호스트·월별 샤딩)
- v01 2026-04-15 — 최초 생성 (gemma4, mlx-lm, localhost:8080)

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `gemma help` | 서브명령어 목록 표시 |
| `gemma version` | 스킬 버전 정보 (v03) |
| `gemma status` | mlx-lm 서버 연결 상태 확인 |
| `gemma run` | 인터랙티브 채팅 모드 시작 |
| `gemma run "프롬프트"` | 단일 프롬프트 추론 후 종료 |
| `gemma run --caller <skill> "프롬프트"` | 호출 스킬 기록과 함께 단일 추론 |
| `gemma <skill> "프롬프트"` | **화이트리스트 oo 스킬 위임** (caller 자동 기록) |
| `gemma whitelist` (`gemma wl`) | 위임 허용 oo 스킬 목록 표시 |
| `gemma models` | 서버에서 사용 가능한 모델 목록 조회 |
| `gemma log` | 전체 호출 로그 집계 (caller·모델·호스트별) |
| `gemma log <skill>` | 특정 스킬의 최근 20건 표시 |
| `gemma check` | references/checklist.md 기반 체크 |

### 호출 로그 (v02+)

- 경로: `.claude/.omc/gemma-usage/{HOSTNAME}-{YYYYMM}.jsonl`
- 호스트별·월별 샤딩 → Resilio 동기화 충돌 없음 (각 기기가 자기 파일만 append)
- 기록 항목: ts, host, caller, model, prompt/response head, elapsed_ms
- 다른 스킬에서 호출 시: `--caller <skill>` 인자 또는 환경변수 `GEMMA_CALLER=<skill>` 설정

### 화이트리스트 (v03+)

oo 스킬 중 gemma 위임이 의미 있는 작업(요약/번역/분류/포맷 변환 등)을 명시적으로 등록한다. 등록되지 않은 oo 스킬명으로 호출하면 거부되어, 무의미한 위임을 사전에 차단한다.

| 항목 | 내용 |
|------|------|
| 정의 위치 | `references/skill_whitelist.json` |
| 호출 형식 | `gemma <skill_name> "프롬프트"` (caller 자동 기록) |
| 미등록 시 | `[ERROR] '<name>'는 gemma 화이트리스트에 없습니다.` (exit 2) |
| 우회 | `gemma run --caller <임의명> "프롬프트"` 또는 `gemma "프롬프트"` (caller=direct) |
| 목록 확인 | `gemma whitelist` (`gemma wl`) |

**기본 등록 스킬**: oopaper, ooscrap, oobook, oosurvey, oosota, oonote, oosidi, oodoc, ootutorial, ooppt, oohwp, ooword, ooresearch, oomemo, ootodo

> 추가/제거: `references/skill_whitelist.json`의 `whitelist` 객체 직접 편집

---

## 개요

로컬 [mlx-lm](https://github.com/ml-explore/mlx-examples/tree/main/llms/mlx_lm) 서버가 제공하는 OpenAI 호환 API를 통해 Gemma4 모델을 사용하는 일반 에이전트 스킬.

| 항목 | 값 |
|------|----|
| 엔드포인트 | `http://localhost:8080/v1` |
| 모델 | `mlx-community/gemma-4-e4b-it-4bit` |
| 프레임워크 | mlx-lm (Apple MLX) |
| API 형식 | OpenAI 호환 Chat Completions |

### mlx-lm 서버 시작 방법 (참고)

```bash
# mlx_lm 서버 실행 예시
uv run mlx_lm.server --model mlx-community/gemma-3-4b-it-4bit --port 8080
```

---

## 워크플로우

```
입력(프롬프트 또는 인터랙티브)
  ↓
gemma_run.py 실행
  ↓
OpenAI 클라이언트 초기화 (base_url=http://localhost:8080/v1)
  ↓
Chat Completions API 호출 (model=gemma4, stream=True)
  ↓
스트리밍 응답 출력
```

---

## 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| (없음) | - | - | 직접 실행 스킬 (서브에이전트 불필요) |

---

## 관련 문서

| 문서 | 용도 |
|------|------|
| `scripts/gemma_run.py` | 실행 스크립트 |
| `references/checklist.md` | 체크리스트 |
| `.claude/guides/common_guide.md` | 공통 가이드 |
