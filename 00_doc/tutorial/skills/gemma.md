# gemma 튜토리얼

**생성일**: 2026-04-15 | **버전**: v01 | **카테고리**: meta-util | **ootutorial**: v03

> 로컬 Gemma4 SLM 에이전트 — mlx-lm 서버(localhost:8080)를 통해 API 비용 없이 로컬 추론

---

## 1. 이 스킬은 왜 필요한가?

Claude 등 상용 AI의 API 비용 절감이 목적이다. 단순 반복 작업(요약, 번역, 분류 등)을 로컬 Gemma4 모델에 위임하면 외부 API 호출 없이 처리할 수 있다.

| 상황 | gemma 사용 이유 |
|------|----------------|
| 대량 텍스트 요약 | API 비용 절감 |
| 단순 분류/정리 | 응답 속도 빠름 (로컬) |
| 오프라인 환경 | 외부 네트워크 불필요 |
| 반복 작업 자동화 | Claude 컨텍스트 절약 |

**전제 조건**: 맥북에서 mlx-lm 서버가 실행 중이어야 한다.

---

## 2. 빠른 시작 (5분 가이드)

### Step 1: mlx-lm 서버 시작 (맥북에서)

```bash
# Gemma4 서버 실행
uv run mlx_lm.server --model mlx-community/gemma-4-e4b-it-4bit --port 8080
```

### Step 2: 서버 상태 확인

```bash
gemma status
# → 서버 상태: OK
# → 사용 가능한 모델: mlx-community/gemma-4-e4b-it-4bit
```

### Step 3: 추론 실행

```bash
# 단일 질문
gemma run "파이썬 리스트 컴프리헨션 예시 3개만 알려줘"

# 인터랙티브 채팅
gemma run
```

---

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `gemma help` | 서브명령어 목록 표시 |
| `gemma version` | 스킬 버전 정보 (v01) |
| `gemma status` | mlx-lm 서버 연결 상태 확인 |
| `gemma run` | 인터랙티브 채팅 모드 시작 |
| `gemma run "프롬프트"` | 단일 프롬프트 추론 후 종료 |
| `gemma models` | 서버에서 사용 가능한 모델 목록 조회 |
| `gemma check` | references/checklist.md 기반 체크 |

---

## 4. 상세 사용법

### 단일 프롬프트 모드

```bash
# 명시적 run 서브명령어
gemma run "한국어로 짧게 설명해줘: transformer attention mechanism"

# run 생략 가능 (프롬프트 직접 입력)
gemma "이 코드 리뷰해줘: def add(a,b): return a+b"
```

### 인터랙티브 채팅 모드

```bash
gemma run
# → [gemma] 인터랙티브 채팅 모드 (종료: 'exit' 또는 Ctrl+C)
# → [You] 안녕하세요
# → [Gemma4] 안녕하세요! 무엇을 도와드릴까요?
# → [You] clear   ← 대화 이력 초기화
# → [You] exit    ← 채팅 종료
```

### 모델 목록 조회

```bash
gemma models
# → - mlx-community/gemma-4-e4b-it-4bit
```

---

## 5. 워크플로우

```
사용자 입력 (프롬프트 또는 인터랙티브)
  ↓
gemma_run.py 실행
  ↓
OpenAI 클라이언트 초기화
  base_url = http://localhost:8080/v1
  model = mlx-community/gemma-4-e4b-it-4bit
  ↓
Chat Completions API 호출 (stream=True)
  ↓
스트리밍 응답 실시간 출력
```

---

## 6. 실전 예시

### 예시 1: 유튜브 서머리 후처리

```bash
# ooscrap으로 자막 추출 후 Gemma에게 요약 요청
gemma run "다음 강의 자막을 3줄로 요약해줘: [자막 내용]"
```

### 예시 2: 코드 간단 리뷰

```bash
gemma run "다음 파이썬 코드의 문제점을 찾아줘:
def calc(lst):
    total = 0
    for i in range(len(lst)):
        total = total + lst[i]
    return total"
```

### 예시 3: 대화 이력 유지 채팅

```bash
gemma run
# [You] 파이썬 데코레이터가 뭐야?
# [Gemma4] 데코레이터는 함수를 감싸는 함수입니다...
# [You] 예시 하나만 더 보여줘    ← 이전 맥락 유지
```

---

## 7. 스펙

| 항목 | 값 |
|------|----|
| 엔드포인트 | `http://localhost:8080/v1` |
| 기본 모델 | `mlx-community/gemma-4-e4b-it-4bit` |
| 프레임워크 | mlx-lm (Apple MLX) |
| API 형식 | OpenAI Chat Completions 호환 |
| 스트리밍 | 지원 (stream=True) |
| 온도 | 0.7 (기본값) |
| 최대 토큰 | 2048 |
| 언어 | 한국어 질문 → 한국어 답변 (시스템 프롬프트 설정) |

---

## 8. 할 수 있는 것 / 없는 것

### 할 수 있는 것

| 기능 | 설명 |
|------|------|
| 텍스트 추론 | 요약, 번역, 분류, Q&A |
| 인터랙티브 채팅 | 대화 이력 유지 채팅 |
| 스트리밍 응답 | 실시간 토큰 출력 |
| 오프라인 동작 | 외부 API 없이 로컬 실행 |
| API 비용 절감 | 무료 로컬 추론 |

### 할 수 없는 것

| 기능 | 대안 |
|------|------|
| 모델 설치/다운로드 | `ooenv` |
| 코드 구현/수정 | `oodev`, `oofix` |
| 파일 읽기/쓰기 | Claude 직접 처리 |
| 이미지/멀티모달 | 미지원 (텍스트 전용) |
| Windows 로컬 실행 | mlx-lm은 Apple MLX 전용 |
| 외부 API 호출 | - |

---

## 9. 오류 처리

| 오류 | 원인 | 해결 |
|------|------|------|
| `Connection refused` | 서버 미실행 | 맥북에서 mlx-lm 서버 시작 |
| `openai 패키지 미설치` | 의존성 없음 | `uv add openai` |
| `서버 상태: ERROR` | 포트 불일치 | `--port 8080` 확인 |
| 응답 없음 | 모델 로딩 중 | 서버 로그 확인 후 재시도 |

---

## 10. 서브에이전트

이 스킬은 서브에이전트 없이 직접 실행된다.

| 구성요소 | 역할 |
|----------|------|
| `scripts/gemma_run.py` | 메인 실행 스크립트 |
| `references/checklist.md` | 사전 점검 체크리스트 |

---

## 11. 관련 스킬

```
gemma (로컬 Gemma4 추론)
  ├─ ooscrap (콘텐츠 수집 → Gemma 후처리)
  ├─ ooenv  (mlx-lm 환경 설정/확인)
  └─ oodev  (코드 구현은 Claude 직접)
```

---

**문서 버전**: v01 (2026-04-15 기준)  
**다음 단계**: `gemma status` → 서버 확인 후 `gemma run "질문"` 실행
