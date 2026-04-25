# 38. Gemma 스킬 설정 및 사용법

> 로컬 Gemma4 SLM을 활용한 무료 AI 추론 환경 | 버전: v02 | 2026-04-17

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v02 | 2026-04-17 | 호출 로그 시스템(§5) 추가: `gemma log`, caller 추적, 호스트·월별 JSONL 샤딩 |
| v01 | 2026-04-15 | 최초 작성 |

---

## 1. 개요

`gemma` 스킬은 맥북(Apple Silicon)에서 실행 중인 **mlx-lm 로컬 서버**에 연결하여 Gemma4 모델을 사용하는 스킬이다. Claude API 호출 없이 텍스트 요약·번역·분류·Q&A 등을 무료로 처리할 수 있다.

| 항목 | 내용 |
|------|------|
| 서버 | `http://localhost:8080/v1` (OpenAI 호환 API) |
| 프레임워크 | mlx-lm (Apple MLX, Mac 전용) |
| 주요 용도 | 단일 추론, 인터랙티브 채팅, 대량 배치 처리 |
| 실행 위치 | Windows(Claude Code) → Mac(mlx-lm 서버) 원격 연결 |

---

## 2. 사전 준비 (설정 환경)

gemma 스킬은 **서버**와 **클라이언트** 두 부분으로 구성된다.

```
┌─────────────────────────────────────────────────────┐
│  서버 (추론 담당)         클라이언트 (호출 담당)      │
│  ┌──────────────┐         ┌─────────────────────┐   │
│  │ Mac          │         │ Claude Code (공통)   │   │
│  │ mlx-lm 서버  │ ←─────→ │ gemma_run.py        │   │
│  ├──────────────┤  :8080  │ gemma_batch.py      │   │
│  │ Windows      │         └─────────────────────┘   │
│  │ Ollama 서버  │                                    │
│  └──────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

> **서버는 Mac 또는 Windows 중 하나**만 실행하면 된다.  
> **클라이언트 설정은 Mac/Windows 동일**하다.

---

### 2.1 서버 환경

#### Mac 서버 — mlx-lm (Apple Silicon 전용)

```bash
# mlx-lm 설치
pip install mlx-lm

# 서버 실행 (포트 8080 고정)
mlx_lm.server --model mlx-community/gemma-4-e4b-it-4bit --port 8080   # 고품질
mlx_lm.server --model mlx-community/gemma-4-e2b-it-4bit --port 8080   # 경량·빠름
```

| 모델 | 크기 | 특징 |
|------|------|------|
| `gemma-4-e4b-it-4bit` | ~4GB | 고품질, 느림 |
| `gemma-4-e2b-it-4bit` | ~2GB | 경량, 빠름 |

---

#### Windows 서버 — Ollama (`gemma.ps1`)

`gemma.ps1`을 실행하면 Ollama 설치·모델 다운로드·서버 시작을 **자동으로** 처리한다.

```powershell
# PowerShell에서 실행
.\gemma.ps1
```

**자동 처리 순서:**

| 단계 | 내용 |
|------|------|
| 1. 모델 선택 | e2b / e4b / 26b / 31b 중 선택 (이전 선택 기억) |
| 2. Ollama 확인 | 미설치 시 `winget`으로 자동 설치 |
| 3. 포트 확인 | 8080 충돌 시 프로세스 종료·포트 변경·연결 선택 |
| 4. 모델 확인 | 로컬에 없으면 `ollama pull` 자동 다운로드 |
| 5. 서버 실행 | `ollama serve` + `ollama run $MODEL` |

**Ollama 지원 모델:**

| 모델 ID | 설명 | 상태 |
|---------|------|------|
| `gemma4:e2b` | Gemma4 5.1B Q4_K_M (경량·빠름) | 설치됨 |
| `gemma4:e4b` | Gemma4 8B Q4_K_M (기본) | 설치됨 |
| `gemma4:26b` | Gemma4 26B | 미설치 |
| `gemma4:31b` | Gemma4 31B | 미설치 |

---

### 2.2 클라이언트 환경 (Mac / Windows 공통)

서버가 준비된 후 Claude Code(클라이언트)를 설정한다. **Mac/Windows 동일.**

#### openai 패키지 설치

```bash
uv add openai
```

> 미설치 시 `[ERROR] openai 패키지 미설치` 오류 발생

#### 모델 선택 (`last_model.json`)

사용할 모델은 **컴퓨터별로** 자동 저장된다.

**파일 위치**: `.claude/skills/gemma/references/last_model.json`

```json
{
  "OAISBLACK": "gemma4:e2b"
}
```

- `gemma.ps1` 실행 시 선택한 모델이 자동 저장됨
- 수동 변경 시 파일을 직접 편집

> 미설정 시 기본값: `gemma4:e4b`

#### 서버 연결 확인

```bash
gemma status
# [gemma status]
#   엔드포인트: http://localhost:8080/v1
#   모델: gemma4:e2b
#   서버 상태: OK
#   사용 가능한 모델: gemma4:e2b, gemma4:e4b, qwen3.5:latest, bge-m3:latest
```

---

## 3. 기본 사용법 (gemma_run.py)

### 3.1 서브명령어 목록

```bash
gemma help          # 서브명령어 목록
gemma version       # 버전 정보 (v02)
gemma status        # 서버 연결 상태 확인
gemma models        # 사용 가능한 모델 목록
gemma run           # 인터랙티브 채팅 모드
gemma run "질문"    # 단일 추론 후 종료
gemma log           # 전체 호출 로그 집계 (caller·모델·호스트별)
gemma log <skill>   # 특정 스킬의 최근 20건 표시
gemma check         # 체크리스트 확인
```

### 3.2 단일 추론 모드

```bash
# 명시적 run
gemma run "파이썬 리스트 컴프리헨션 예시 3개"

# run 생략 가능 (프롬프트 직접 전달)
gemma "transformer attention mechanism을 한국어로 설명해줘"
```

**출력 예시**:
```
[gemma] 단일 추론 모드
[You] transformer attention mechanism을 한국어로 설명해줘

[Gemma4] Attention Mechanism은 입력 시퀀스의 각 토큰이...
```

### 3.3 인터랙티브 채팅 모드

```bash
gemma run
# → [gemma] 인터랙티브 채팅 모드 (종료: 'exit' 또는 Ctrl+C)
# → 모델: gemma4:e2b @ http://localhost:8080/v1
# ──────────────────────────────────────────────────
# [You] 안녕하세요
# [Gemma4] 안녕하세요! 무엇을 도와드릴까요?
# [You] clear      ← 대화 이력 초기화
# [You] exit       ← 채팅 종료
```

**채팅 특수 명령어**:

| 입력 | 동작 |
|------|------|
| `exit` / `quit` / `종료` / `q` | 채팅 종료 |
| `clear` / `초기화` | 대화 이력 초기화 |
| Ctrl+C | 강제 종료 |

### 3.4 스펙

| 항목 | 값 |
|------|----|
| 스트리밍 | 지원 (stream=True, 실시간 출력) |
| 온도 | 0.7 |
| 최대 토큰 | 2048 |
| 시스템 프롬프트 | 한국어 질문 → 한국어 답변 |
| 대화 이력 | 인터랙티브 모드에서 유지 |

---

## 4. 배치 처리 (gemma_batch.py)

대량 데이터를 자동으로 처리하는 배치 스크립트. API 비용 없이 수백~수천 건을 처리할 수 있다.

### 4.1 기본 실행 형식

```bash
uv run python .claude/skills/gemma/scripts/gemma_batch.py <입력파일> [옵션]
```

### 4.2 옵션 목록

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--task` | `summarize` | 처리 태스크 선택 |
| `--prompt` | - | 커스텀 프롬프트 (`{text}` 자리표시자) |
| `--output` | `<입력>_<task>.json` | 결과 저장 경로 |
| `--max-tokens` | `512` | 최대 출력 토큰 |
| `--delay` | `0.0` | 요청 간 딜레이(초) |
| `--limit` | - | 처리 최대 건수 (테스트용) |

### 4.3 태스크별 사용법

| 태스크 | 설명 | 권장 max-tokens |
|--------|------|----------------|
| `summarize` | 텍스트 2~3문장 요약 | 256 |
| `classify` | 카테고리 분류 (과학/기술/사회/경제/문화/의학/공학/기타) | 32 |
| `extract_keywords` | 핵심 키워드 5개 추출 (JSON 배열) | 128 |
| `translate_ko` | 영→한 번역 | 512 |
| `translate_en` | 한→영 번역 | 512 |
| `sentiment` | 긍정/부정/중립 감성 분석 | 16 |
| `qa` | 커스텀 프롬프트 사용 | 512 |

### 4.4 입력 파일 형식

| 형식 | 처리 방식 |
|------|----------|
| `.txt` | 줄별로 처리 (빈 줄 제외) |
| `.jsonl` | 각 줄: `{"id": ..., "text": ...}` |
| `.json` | 배열: `["text1", "text2"]` 또는 `[{"id": ..., "text": ...}]` |

> JSONL의 경우 `text`, `abstract`, `content` 필드 자동 인식

### 4.5 사용 예시

```bash
# 텍스트 파일 요약
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  input.txt --task summarize

# JSONL 키워드 추출 + 결과 저장
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  papers.jsonl --task extract_keywords --output results.json

# 커스텀 프롬프트 (RAG 청크 품질 필터)
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  08_RRag/chunks.jsonl \
  --prompt "다음 텍스트가 의미있는 정보를 포함하면 'pass', 노이즈면 'fail'로만 답하세요:\n\n{text}\n\n결과:" \
  --max-tokens 8

# 테스트 실행 (5개만)
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  input.txt --task summarize --limit 5
```

### 4.6 결과 JSON 형식

```json
{
  "meta": {
    "task": "summarize",
    "model": "mlx-community/gemma-4-e4b-it-4bit",
    "total": 100,
    "success": 98,
    "failed": 2,
    "elapsed_total_s": 245.3,
    "avg_elapsed_s": 2.45
  },
  "results": [
    {
      "id": 0,
      "input_preview": "텍스트 앞 80자...",
      "output": "요약 결과",
      "task": "summarize",
      "elapsed_s": 2.1
    }
  ]
}
```

---

## 5. 호출 로그 시스템 (gemma_log.py)

다른 oo 스킬이 gemma 스킬에 작업을 위임할 때, **누가 / 언제 / 어떤 모델로 / 무엇을 요청했는지**를 기록한다. API 비용 절감 효과를 추적하고, 위임 패턴을 분석하기 위한 인프라.

### 5.1 저장 위치 및 포맷

```
.claude/.omc/gemma-usage/{HOSTNAME}-{YYYYMM}.jsonl
```

| 항목 | 값 |
|------|----|
| 형식 | JSONL (1 호출 = 1 줄) |
| 샤딩 | 호스트별 + 월별 분리 |
| 이유 | Resilio 동기화 시 동시 쓰기 충돌 회피 |
| 예시 파일명 | `KOODESK-202604.jsonl`, `OAISBLACK-202604.jsonl` |

### 5.2 로그 항목 구조

```json
{
  "ts": "2026-04-17T19:00:00",
  "host": "KOODESK",
  "caller": "oopaper",
  "model": "gemma4:e2b",
  "prompt_head": "다음 초록을 3문장으로 요약: ...",
  "response_head": "이 논문은 ... 를 제안한다 ...",
  "elapsed_ms": 1240
}
```

| 필드 | 설명 |
|------|------|
| `ts` | 호출 시각 (ISO 8601) |
| `host` | 실행 호스트명 |
| `caller` | 위임한 스킬명 (예: `oopaper`, `ooscrap`) — 없으면 `direct` |
| `model` | 사용한 Gemma 모델 |
| `prompt_head` / `response_head` | 앞 120자 프리뷰 |
| `elapsed_ms` | 응답 소요 시간 |

### 5.3 명령어

```bash
# 전체 집계 (caller·모델·호스트별)
gemma log

# [gemma log] 총 42건
#   로그 디렉토리: .../gemma-usage
#
# 호출 스킬(caller)별:
#   oopaper                    20
#   ooscrap                    15
#   direct                      7
#
# 모델별:
#   gemma4:e2b                 30
#   gemma4:e4b                 12
#
# 호스트별:
#   KOODESK                    25
#   OAISBLACK                  17

# 특정 스킬 최근 20건
gemma log oopaper

# [gemma log] caller=oopaper 최근 20건
# TS                   HOST          MODEL                         PROMPT
# ...
```

### 5.4 다른 스킬에서 위임 호출 시 caller 기록

```bash
uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트" --caller oopaper
```

`--caller <스킬명>` 옵션으로 호출 스킬을 명시하면 로그에 자동 기록된다. 옵션을 생략하면 `direct`로 분류된다.

### 5.5 현재 한계 및 후속 검토

| 항목 | 현 상태 | 검토 사항 |
|------|---------|----------|
| 출력 형식 | JSONL (기계 친화) | 사람이 읽는 `gemma.md` 마크다운 리포트 추가 검토 |
| 본문 보존 | 앞 120자만 (`_head`) | 전문 보존 옵션(`--full-log`) 검토 |
| 비용 환산 | 미지원 | Claude API 대체 시 절감액 추정 출력 검토 |

---

## 6. SP별 활용 예시

### SP03 논문 (369편) — 초록 요약 / 키워드 추출

```bash
# 초록 요약
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  D:/resilio/1_oais/03_paper/abstracts.jsonl --task summarize --limit 10

# 키워드 추출
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  D:/resilio/1_oais/03_paper/abstracts.jsonl --task extract_keywords \
  --output D:/resilio/1_oais/03_paper/keywords.json
```

### SP04 스크래핑 — 텍스트 분류

```bash
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  04_scraping/texts.txt --task classify \
  --output 04_scraping/classified.json
```

### SP08 RAG — 청크 품질 필터

```bash
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  08_RRag/chunks.jsonl \
  --prompt "다음 텍스트가 의미있는 정보를 포함하면 'pass', 노이즈면 'fail'로만 답하세요:\n\n{text}\n\n결과:" \
  --max-tokens 8 --output 08_RRag/chunk_filter.json
```

---

## 7. 워크플로우

```
[단일 추론]
사용자 입력 → gemma_run.py → OpenAI 클라이언트 초기화
  → Chat Completions API (stream=True) → 실시간 출력

[배치 처리]
입력 파일(.txt/.json/.jsonl) → load_inputs() → 항목별 순차 처리
  → call_gemma() (stream=False, temperature=0.3) → 결과 JSON 저장
```

---

## 8. 오류 처리

| 오류 메시지 | 원인 | 해결 방법 |
|------------|------|----------|
| `Connection refused` | mlx-lm 서버 미실행 | 맥북에서 서버 시작 |
| `openai 패키지 미설치` | 의존성 없음 | `uv add openai` |
| `서버 상태: ERROR` | 포트 불일치 | `--port 8080` 확인 |
| 응답 없음 / 느림 | 모델 로딩 중 또는 e4b 사용 | 잠시 대기 또는 e2b로 변경 |
| `[ERROR] 파일 없음` | 배치 입력 파일 경로 오류 | 절대 경로 또는 현재 디렉토리 확인 |

---

## 9. 할 수 있는 것 / 없는 것

| 할 수 있는 것 | 할 수 없는 것 |
|--------------|--------------|
| 텍스트 요약·번역·분류·Q&A | 이미지/멀티모달 처리 |
| 인터랙티브 채팅 (이력 유지) | 파일 읽기/쓰기 직접 처리 |
| 대량 배치 처리 (무료) | 모델 설치/다운로드 (→ `ooenv`) |
| 오프라인 동작 (로컬 서버) | Windows 로컬 실행 (Mac 전용) |
| 커스텀 프롬프트 배치 | 코드 구현/수정 (→ `oodev`) |

---

## 10. 관련 스킬

```
gemma (로컬 Gemma4 추론)
  ├─ ooscrap   콘텐츠 수집 후 Gemma 후처리
  ├─ ooenv     mlx-lm 설치/환경 확인
  └─ oodev     코드 구현은 Claude 직접
```

---

**다음 단계**: `gemma status` → 서버 확인 → `gemma run "질문"` 실행
