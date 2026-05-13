---
name: ccopti
description: "코드 성능 분석, 알고리즘 개선, 병목 제거를 수행한다 | ref: `.claude/guides/common_guide.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

# ccopti - 알고리즘/코드 최적화

> 코드 성능 분석, 알고리즘 개선, 병목 제거를 수행한다 | ref: `.claude/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 알고리즘 분석 및 코드 성능 최적화 (시간복잡도·메모리·병목 제거) |
| **하는 것** | 성능 프로파일링, 알고리즘 개선, 병목 분석, 최적화 코드 적용 |
| **하지 않는 것** | GPU 딥러닝 최적화(→oodeep), 코드 에러 수정(→oofix), 코드 품질 체크(→oocheck) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 벤치마크 자동 포함 안 함 |
| **수정 대상** | 최적화 대상 코드 파일 |
| **실행 레벨** | [반자동] — 프로파일링 결과 확인 후 최적화 적용 |
| **에이전트 호환** | 범용 — 코드 분석·수정 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v01 2026-03-26 — 초기 생성

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ccopti help` | 서브명령어 목록 표시 |
| `ccopti version` | 스킬 버전 정보 (v01) |
| `ccopti status` | 서브명령어 리스트, 현재 상태 |
| `ccopti check` | references/checklist.md 기반 체크 및 리포팅 |
| `ccopti show checklist` | 역할 수행 체크리스트 표시 |
| `ccopti add checklist "항목"` | 체크리스트 항목 추가 |
| `ccopti run [대상]` | 대상 파일/모듈 최적화 분석 + 개선 실행 |
| **`ccopti run this`** | **직전 작업 파일 최적화** (→ common_guide.md §9) |
| `ccopti profile [대상]` | 프로파일링 (cProfile/line_profiler) |
| `ccopti complexity [대상]` | 시간/공간 복잡도 분석 |
| `ccopti benchmark [대상]` | 최적화 전후 벤치마크 비교 |
| `ccopti report` | 최적화 리포트 생성 (d{SP}0012_optimization.md) |

실행: `uv run python .claude/skills/ccopti/scripts/ooopti_run.py [subcommand] [args]`

## 워크플로우

### `ccopti run` 전체 실행

```
1. 대상 식별
  - 파일/모듈/함수 지정 또는 oocheck 결과에서 [WARNING] 성능 이슈 추출
  - SP 컨텍스트 반영 (oocontext N)

2. 프로파일링 (측정 우선)
  - cProfile로 함수별 호출 횟수, 누적 시간 측정
  - 핫스팟 Top 5 식별
  - 메모리 사용량 측정 (tracemalloc)

3. 복잡도 분석
  - 시간 복잡도: O(1) ~ O(n!) 판정
  - 공간 복잡도: 메모리 할당 패턴
  - 개선 가능 복잡도 제안 (예: O(n²) → O(n log n))

4. 최적화 수행
  - 알고리즘 최적화 (자료구조 변경, 알고리즘 교체)
  - 코드 최적화 (불필요 연산 제거, 캐싱, 벡터화)
  - Python 특화 (리스트 컴프리헨션, 제너레이터, __slots__)

5. 벤치마크 검증
  - 최적화 전/후 실행 시간 비교
  - 결과 동일성 검증 (기능 보존 확인)
  - 개선율(%) 산출

6. 리포트 생성
  - d{SP}0012_optimization.md에 결과 기록
  - 핫스팟, 변경 내용, 개선율 테이블
```

## 최적화 전략 (우선순위 순)

| 순위 | 전략 | 효과 | 예시 |
|:----:|------|------|------|
| 1 | 알고리즘 교체 | 복잡도 클래스 변경 | 버블정렬→팀정렬, 선형탐색→이진탐색 |
| 2 | 자료구조 변경 | 연산 복잡도 감소 | list→set(탐색), dict→defaultdict |
| 3 | 캐싱/메모이제이션 | 중복 연산 제거 | @lru_cache, 결과 딕셔너리 |
| 4 | I/O 최적화 | 대기 시간 감소 | 배치 읽기, 비동기 I/O, 버퍼링 |
| 5 | 벡터화 | 루프 제거 | numpy 연산, pandas vectorized |
| 6 | 병렬화 | 처리량 증가 | multiprocessing, concurrent.futures |
| 7 | Python 관용구 | 상수배 개선 | 컴프리헨션, 제너레이터, __slots__ |

## 최적화 규칙

### 필수 원칙

- **측정 우선**: 프로파일링 없이 최적화하지 않는다
- **기능 보존**: 최적화 후 기존 테스트 전부 통과해야 한다
- **가독성 유지**: 10% 미만 개선이면 가독성을 우선한다
- **점진적 적용**: 한 번에 하나의 최적화만 적용하고 벤치마크

### 금지 사항

- 프로파일링 없이 "느릴 것 같아서" 최적화
- 기존 테스트를 깨뜨리는 최적화
- 가독성을 크게 해치는 마이크로 최적화
- 측정 불가능한 개선 주장

## 프로파일링 도구

| 도구 | 용도 | 명령어 |
|------|------|--------|
| cProfile | 함수별 호출/시간 | `python -m cProfile -s cumulative script.py` |
| line_profiler | 라인별 시간 | `@profile` 데코레이터 + `kernprof` |
| tracemalloc | 메모리 추적 | `tracemalloc.start()` |
| timeit | 마이크로 벤치마크 | `python -m timeit "expr"` |
| memory_profiler | 메모리 라인별 | `@profile` + `mprof run` |

## 리포트 형식

`00_doc/d{SP}0012_optimization.md`:

```markdown
# 최적화 리포트

## 대상: {파일/함수명}
- 일시: YYYY-MM-DD
- 프로파일링: cProfile

## 핫스팟

| 순위 | 함수 | 호출수 | 누적시간(s) | 비율 |
|:----:|------|:------:|:----------:|:----:|
| 1 | func_a | 10000 | 2.34 | 45% |

## 최적화 내역

| # | 변경 | 전략 | Before | After | 개선율 |
|---|------|------|--------|-------|:------:|
| 1 | list→set 탐색 | 자료구조 | 2.34s | 0.12s | 94.9% |

## 검증
- [x] 기존 테스트 통과
- [x] 결과 동일성 확인
```

## 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | oo-python-algorithm-expert | sonnet | 알고리즘 복잡도 분석 | - |
| 프로파일 | task-executor | sonnet | 프로파일링 실행 | - |
| 최적화 | task-executor | sonnet | 코드 수정 | - |
| 검증 | task-checker | sonnet | 테스트 통과 확인 | - |

## 관련

`.claude/skills/oocheck/SKILL.md` | `.claude/skills/oodev/SKILL.md` | `.claude/skills/oodeep/SKILL.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.claude/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |
| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |
| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |
| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |

**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.

<!-- KARPATHY-REF:END -->

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

