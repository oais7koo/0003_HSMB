# ooopti Tutorial

> 알고리즘 및 코드 최적화 스킬. | 버전: v01 | 카테고리: core-dev

## 1. 이 스킬은 왜 필요한가?

알고리즘 및 코드 최적화 스킬.

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ooopti run

# 상태 확인
ooopti status

# 도움말
ooopti help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ooopti help` | 서브명령어 목록 표시 |
| `ooopti version` | 스킬 버전 정보 (v01) |
| `ooopti status` | 서브명령어 리스트, 현재 상태 |
| `ooopti check` | references/checklist.md 기반 체크 및 리포팅 |
| `ooopti show checklist` | 역할 수행 체크리스트 표시 |
| `ooopti add checklist "항목"` | 체크리스트 항목 추가 |
| `ooopti run [대상]` | 대상 파일/모듈 최적화 분석 + 개선 실행 |
| **`ooopti run this`** | **직전 작업 파일 최적화** (→ common_guide.md §9) |
| `ooopti profile [대상]` | 프로파일링 (cProfile/line_profiler) |
| `ooopti complexity [대상]` | 시간/공간 복잡도 분석 |
| `ooopti benchmark [대상]` | 최적화 전후 벤치마크 비교 |
| `ooopti report` | 최적화 리포트 생성 (d{SP}0012_optimization.md) |

실행: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py [subcommand] [args]`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 알고리즘 분석 및 코드 성능 최적화 (시간복잡도·메모리·병목 제거) |
| **하는 것** | 성능 프로파일링, 알고리즘 개선, 병목 분석, 최적화 코드 적용 |
| **하지 않는 것** | GPU 딥러닝 최적화(→oodeep), 코드 에러 수정(→oofix), 코드 품질 체크(→oocheck) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 벤치마크 자동 포함 안 함 |
| **수정 대상** | 최적화 대상 코드 파일 |
| **실행 레벨** | [반자동] — 프로파일링 결과 확인 후 최적화 적용 |
| **에이전트 호환** | 범용 — 코드 분석·수정 중심으로 모든 에이전트 처리 가능 |

### 최적화 전략 (우선순위 순)

| 순위 | 전략 | 효과 | 예시 |
|:----:|------|------|------|
| 1 | 알고리즘 교체 | 복잡도 클래스 변경 | 버블정렬→팀정렬, 선형탐색→이진탐색 |
| 2 | 자료구조 변경 | 연산 복잡도 감소 | list→set(탐색), dict→defaultdict |
| 3 | 캐싱/메모이제이션 | 중복 연산 제거 | @lru_cache, 결과 딕셔너리 |
| 4 | I/O 최적화 | 대기 시간 감소 | 배치 읽기, 비동기 I/O, 버퍼링 |
| 5 | 벡터화 | 루프 제거 | numpy 연산, pandas vectorized |
| 6 | 병렬화 | 처리량 증가 | multiprocessing, concurrent.futures |
| 7 | Python 관용구 | 상수배 개선 | 컴프리헨션, 제너레이터, __slots__ |

### 최적화 규칙

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

### 프로파일링 도구

| 도구 | 용도 | 명령어 |
|------|------|--------|
| cProfile | 함수별 호출/시간 | `python -m cProfile -s cumulative script.py` |
| line_profiler | 라인별 시간 | `@profile` 데코레이터 + `kernprof` |
| tracemalloc | 메모리 추적 | `tracemalloc.start()` |
| timeit | 마이크로 벤치마크 | `python -m timeit "expr"` |
| memory_profiler | 메모리 라인별 | `@profile` + `mprof run` |

### 리포트 형식

`00_doc/d{SP}0012_optimization.md`:

```markdown
# 최적화 리포트

### 대상: {파일/함수명}

- 일시: YYYY-MM-DD
- 프로파일링: cProfile

## 5. 워크플로우

### `ooopti run` 전체 실행

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

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ooopti run
```

### 서브명령어 활용
```bash
ooopti run this
ooopti report  # 최적화 리포트 생성 (d{SP}0012_optimization.md)
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/ooopti/scripts/ooopti_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | oo-python-algorithm-expert | sonnet | 알고리즘 복잡도 분석 | - |
| 프로파일 | task-executor | sonnet | 프로파일링 실행 | - |
| 최적화 | task-executor | sonnet | 코드 수정 | - |
| 검증 | task-checker | sonnet | 테스트 통과 확인 | - |

## 10. 관련 스킬

`.claude/skills/oocheck/SKILL.md` | `.claude/skills/oodev/SKILL.md` | `.claude/skills/oodeep/SKILL.md`

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
