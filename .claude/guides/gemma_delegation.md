# Gemma 위임 가이드 (로컬 LLM 활용)

> 모든 oo* 스킬은 자신의 업무 중 **단순/반복적인 부분**은 `gemma` 스킬(로컬 Gemma4 SLM)로 위임하여 처리 비용과 API 호출을 절감한다.

## 1. 위임 원칙

| 원칙 | 설명 |
|------|------|
| **사용자 승인 필수** | 위임 전 반드시 "로컬 Gemma로 처리할까요? (y/n)"로 확인 |
| **실패 시 폴백** | gemma 서버 미가동(`localhost:8080` 응답 없음) → Claude 본체 처리 |
| **결과 검증** | gemma 응답을 Claude가 간단히 스캔 후 사용자 제시 |
| **프라이버시** | 민감 데이터는 로컬 처리가 오히려 안전 (외부 API 전송 없음) |

## 2. Gemma 적합 업무 (위임 대상)

| 카테고리 | 예시 | 해당 스킬 |
|----------|------|----------|
| **번역** | 짧은 문장/단락 번역 (1~2문단) | oopaper, oobook, oohwp |
| **요약** | TL;DR, 한 줄 요약, 단순 정리 | oobook, oopaper, ooresearch |
| **분류/태깅** | 카테고리 분류, 키워드 추출, 태그 제안 | oopaper, oobook, ootodo |
| **Rephrase** | 문장 재작성, 문체 통일, 어조 변경 | ooword, oohwp, ooreport |
| **포맷 변환** | 불릿 ↔ 문단, MD 표 ↔ 리스트 | oodoc, ooreport, ooppt |
| **네이밍 제안** | 변수명/파일명/폴더명 후보 생성 | oolib, oodev, oofeature |
| **정규식 설명** | 간단한 정규식 풀이, 패턴 설명 | oocheck, oofix |
| **데이터 정리** | CSV 컬럼명 제안, JSON 키 표준화 | oodb, oodata |
| **커밋 메시지 초안** | 변경 내용 기반 커밋 메시지 1줄 | oocommit |
| **TODO 초안** | 대화 내용에서 TODO 항목 추출 | ootodo, oonote |

## 3. Gemma 부적합 업무 (Claude 본체 처리)

| 업무 | 이유 |
|------|------|
| 코드 생성/수정 | 품질·정확도 부족, 문법 오류 위험 |
| 코드 리뷰/설계 | 복잡한 추론 필요 |
| 아키텍처 결정 | 시스템 전반 이해 필요 |
| 긴 문서 번역 (10문단+) | 맥락 유지 어려움, 품질 저하 |
| Tool/MCP 사용 필요 작업 | gemma는 도구 호출 불가 |
| 멀티스텝 추론 | 단일 응답 모델의 한계 |
| 보안 분석 | 오탐·미탐 위험 |
| 수치 계산/통계 | LLM 연산 신뢰도 낮음 |

## 4. 위임 워크플로우

### 4.1 표준 확인 패턴

```
[스킬명] 실행 중 단순 업무 감지 시:

💡 이 작업은 [번역/요약/분류/Rephrase]입니다.
   로컬 Gemma로 처리하면 비용/시간 절감 가능합니다.

   대상: <업무 내용 요약>
   예상 토큰: ~N (gemma 처리 시 Claude 토큰 소모 없음)

   로컬 Gemma로 처리할까요? (y/n, 기본: y)
```

### 4.2 실행 방법

```bash
# 단일 프롬프트 처리
uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"

# 서버 상태 확인 (폴백 판단용)
uv run python .claude/skills/gemma/scripts/gemma_run.py status
```

### 4.3 폴백 규칙

```
1. gemma status 확인
   - 서버 응답 OK → gemma run 실행
   - 서버 미가동 → "gemma 서버 미가동. Claude로 진행합니다." 안내 후 본체 처리
2. gemma 응답 품질 체크 (Claude가 스캔)
   - 정상 → 결과 사용
   - 불완전/오류 → Claude 본체로 재처리
```

## 5. 스킬별 적용 예시

### oopaper (논문 관리)
- ✅ 논문 초록 요약 (1~2문단)
- ✅ 카테고리 분류 (예: RAG/LLM/Agent)
- ❌ 전문 번역 (품질 이슈 → Claude 또는 translator 에이전트)

### oobook (도서 요약)
- ✅ 챕터별 한 줄 요약
- ✅ 키워드 추출
- ❌ 전체 도서 요약 (맥락 필요 → Claude)

### oocommit (커밋)
- ✅ 변경 내용 기반 커밋 메시지 1줄 초안
- ❌ 복잡한 conventional commit 분류 판단 (Claude)

### oodoc (문서 자동화)
- ✅ 섹션 제목 통일, 포맷 변환
- ❌ 문서 간 정합성 검증 (Claude)

## 6. 사용자 설정

| 옵션 | 기본값 | 비활성 방법 |
|------|--------|------------|
| Gemma 위임 추천 | ON | 사용자가 "gemma 쓰지마" 요청 시 해당 세션 OFF |
| 자동 승인 | OFF | 사용자가 "앞으로 단순 번역은 자동으로 gemma 써" 요청 시 ON |
| 폴백 동작 | 자동 Claude 전환 | 고정 (변경 불가) |

> 세션 설정은 메모리에 저장되지 않음. 영구 설정은 `~/.claude/CLAUDE.md`에 추가.

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/gemma/SKILL.md` | Gemma 스킬 사양 |
| `.claude/skills/gemma/scripts/gemma_run.py` | 실행 스크립트 |
| `.claude/skills/oopaper/scripts/oopaper_gemma_helper.py` | oopaper용 안전 래퍼 (표준 설정 강제) |
| `gemma.ps1` / `gemma.sh` | Ollama/mlx-lm 서버 기동 스크립트 |

---

## 8. 실전 검증 (2026-04-18, gemma4:26b, Adadelta 논문)

### 8.1 필수 안전 설정 (위반 시 실패)

```python
client.chat.completions.create(
    model="gemma4:26b",
    messages=[...],
    temperature=0.2,          # 0.1~0.4 권장
    max_tokens=6000,          # ≥4000 필수 (reasoning 누수 대비)
    extra_body={
        "reasoning_effort": "none",
        "chat_template_kwargs": {"enable_thinking": False},
    },
)
```

| 설정 누락 시 증상 | 실제 관측 |
|------------------|----------|
| `reasoning_effort=none` 없음 | `content=""` 반환, `reasoning` 필드에 영어 사고 3000자 소비 |
| `max_tokens < 4000` | content가 239자에서 끊김, finish_reason=length |
| `temperature ≤ 0.1` | 같은 헤더 4000 토큰 반복 루프 |
| 페이지 분할 없이 5KB+ | 중간에 관련 연구 섹션 환각 생성 |

### 8.2 작업별 정량 평가

| 작업 | 시간 | 품질 | 상태 |
|------|------|------|------|
| 자유형식 서머리 (1p 논문) | 2-3분 | 90% 정확 | ⭕ 실용 |
| 단일 페이지 번역 (안전설정) | 2-3분/페이지 | 90% 정확 | ⭕ 초안만 |
| 포맷 보정 (복잡 구조) | 5분 | **실패** (루프) | ❌ Claude 필수 |
| 장문 배치 번역 (6p) | 40분+ | 50% (환각) | ❌ 금지 |
| 학술 메타데이터 추출 | - | 혼동 (Adagrad↔Adadelta) | ❌ 금지 |

### 8.3 환각 사례 (실제 발생)

- Adadelta(2012.12) 논문 번역 중 **Adam(2014)**을 "관련 연구"로 삽입 (시간 역전)
- 초록 내용을 페이지 끝에 재요약 섹션으로 중복 생성
- 논문 제목을 "Adagrad"로 혼동 표기

### 8.4 오픈오퍼 --gemma 옵션

`oopaper run --gemma` → env `OOPAPER_USE_GEMMA=1` 설정 → Phase 2(서머리)·Phase 4(번역) 초안을 `oopaper_gemma_helper.task_summary_draft()` / `task_translate_page()`로 위임.

**위임 범위**:
- Phase 2: 서머리 초안 (최종 포맷 Claude)
- Phase 4: 페이지 단위 번역 초안 (최종 검수 Claude)

**금지**:
- Phase 5 참고문헌 매칭
- Phase 6 정밀 분석 (`anal --deep`)
- 메타데이터 추출 (저자/연도/출처)
