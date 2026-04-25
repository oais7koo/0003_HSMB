# gemma 스킬 체크리스트

## 기본 체크 항목

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/gemma_run.py, scripts/gemma_batch.py 존재 | CRITICAL |
| C02 | 버전 일치 | SKILL.md metadata version == 스크립트 VERSION | ERROR |
| C03 | 서버 연결 | localhost:8080 응답 확인 (`gemma status`) | ERROR |
| C04 | openai 패키지 | `openai` 패키지 설치 여부 (`uv sync`) | ERROR |
| C05 | 모델 가용성 | gemma4 모델 서버에 로드됨 | WARNING |
| C06 | 스트리밍 응답 | stream=True 정상 동작 | WARNING |
| C07 | 인터랙티브 모드 | exit/quit 명령 정상 종료 | INFO |

## 배치 처리 전 체크

- [ ] mlx-lm 서버 실행 중 (`gemma status`)
- [ ] `--limit 5`로 테스트 실행 후 출력 품질 확인
- [ ] 결과 JSON 저장 경로 지정 (`--output`)

## 태스크별 사용 가이드

| 태스크 | 용도 | 권장 max-tokens |
|--------|------|----------------|
| `summarize` | 텍스트 요약 (2~3문장) | 256 |
| `classify` | 카테고리 분류 (한 단어) | 32 |
| `extract_keywords` | 키워드 5개 추출 (JSON) | 128 |
| `translate_ko` | 영→한 번역 | 512 |
| `translate_en` | 한→영 번역 | 512 |
| `sentiment` | 긍정/부정/중립 감성 분석 | 16 |
| `qa` | 커스텀 프롬프트 (`--prompt` 필수) | 512 |

## SP별 활용 예시

### SP03 논문 (369편) — 초록 요약/키워드 추출
```bash
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  {paper_root}/abstracts.jsonl --task summarize --limit 10

uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  {paper_root}/abstracts.jsonl --task extract_keywords --output {paper_root}/keywords.json
```

### SP04 스크래핑 — 텍스트 분류
```bash
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  04_scraping/texts.txt --task classify --output 04_scraping/classified.json
```

### SP08 RAG — 청크 품질 필터
```bash
uv run python .claude/skills/gemma/scripts/gemma_batch.py \
  08_RRag/chunks.jsonl \
  --prompt "다음 텍스트가 의미있는 정보를 포함하면 'pass', 노이즈면 'fail'로만 답하세요:\n\n{text}\n\n결과:" \
  --max-tokens 8
```

## 서버 시작 명령어 (참고)

```bash
# mlx-lm 서버 시작 (Mac/Apple Silicon 필요)
mlx_lm.server --model mlx-community/gemma-4-e4b-it-4bit --port 8080
```
