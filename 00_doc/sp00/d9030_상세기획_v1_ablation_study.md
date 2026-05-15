# v1 ablation study 상세기획 (C4 대응)

> 문서번호: d2030 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F001-3 | plan.md §3 E001

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-04-26 | 초기 작성 |
| v02 | 2026-05-13 | F001-3.2 grid 실행 절차 구체화 — §3 요구사항 5건 추가, §4 CSV 스키마 명시, §5 자원 추정·idempotent 설계, §9 실행 절차 신규 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d2030` |
| 대상 기능 | `F001-3 v1 ablation study` |
| Reviewer 대응 | C4 (파라미터 이론적 근거) |
| 버전 | v01 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

HSMB v1의 3대 파라미터(EdgeWeight=1.5, JNB=3, β=2)에 대한 grid search 기반 민감도 분석을 수행하여 **현재 값의 경험적 최적성을 입증**하고, JNB 원논문 인용으로 이론적 근거를 보강하여 **Reviewer C4 지적**에 대응.

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | 파라미터 grid 정의 (EdgeWeight 5점, JNB 5점, β 5점 = 125 조합) | Must | PRD F03 |
| R02 | 50조건 stratified subset(또는 전체)에 grid 일괄 실행 | Must | plan R04 |
| R03 | 각 조합별 PLCC/SROCC vs BEW 산출 → 매트릭스 저장 | Must | PRD F03 |
| R04 | 민감도 heatmap (3D → 2D 투영) Figure 생성 | Must | 논문 §V-D |
| R05 | 현재 값(1.5, 3, 2) 최적성 입증 + JNB 원논문 인용 | Must | C4 대응 |
| **R06** | **재현성 — random seed 고정·환경 lockfile(`uv.lock`) 첨부·실행 metadata(GPU/CPU/torch ver) 기록** | Must | 학술 재현성 |
| **R07** | **병렬화 — `multiprocessing.Pool`(또는 `joblib.Parallel`), worker 수 환경변수로 조절(기본 4)** | Must | 시간 단축 |
| **R08** | **중간 저장 — 매 조합 완료 시 CSV append, 재시작 시 이미 완료된 (param,condition) 조합 skip** | Must | 장시간 작업 안전성 |
| **R09** | **검증 게이트 — final 파라미터 (1.5, 3, 2.0)에서 50조건 PLCC = 0.9354 ± 0.01 재현 확인 (regression test)** | Must | F001-1.3 모듈화 정합성 |
| **R10** | **CSV 스키마 고정 — 컬럼 명세를 §4.2 표 기준으로 강제 (downstream heatmap·통계 자동화 보장)** | Must | 분석 도구 호환 |

## 4. 입출력 정의

### 4.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `data/exp/gt_50.csv` | CSV | 50조건 ground_truth | Y |
| 50조건 이미지 | folder | 입력 데이터 | Y |
| `src/hsmb/v1.py` | Python | F001-1 산출물 (의존) | Y |

### 4.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `data/exp/ablation_results.csv` | CSV | 125조합 × 50조건 (또는 stratified subset) PLCC/SROCC 매트릭스 |
| `data/exp/ablation_results.meta.json` | JSON | 실행 metadata (seed, GPU/CPU, torch ver, 시작/종료 시각, worker 수) |
| `00_doc/sp00/d0030_ablation_report.md` | MD | 분석 리포트 + heatmap 설명 |
| `figures/ablation_*.png` | PNG | 논문용 figure (3축 heatmap, marginal plot) |

#### 4.2.1 ablation_results.csv 스키마 (R10 강제)

| 컬럼 | 자료형 | 단위/형식 | 설명 |
|------|--------|-----------|------|
| `edge_weight` | float | — | grid 점 (예: 0.5, 1.0, 1.5, 2.0, 2.5) |
| `jnb` | int | px | grid 점 (예: 2, 3, 4, 5, 6) |
| `beta` | float | — | Weibull β grid 점 (예: 1.0, 1.5, 2.0, 2.5, 3.0) |
| `condition_id` | str | — | 50조건 식별자 (예: `low_2.5m_60km_ISO100`) |
| `speed_kmh` | int | km/h | 차량 속도 |
| `distance_m` | float | m | 카메라-벽 거리 |
| `iso` | int | — | ISO 감도 |
| `n_frames` | int | 장 | 해당 조건의 처리 frame 수 |
| `hsmb_mean` | float | [0,1] (.4f) | 조건 내 HSMB score 평균 |
| `hsmb_std` | float | (.4f) | HSMB score 표준편차 |
| `plcc` | float | (.4f) | HSMB vs BEW Pearson 상관 |
| `srocc` | float | (.4f) | HSMB vs BEW Spearman 상관 |
| `plcc_ci_lower` | float | (.4f) | Bootstrap 95% CI 하한 |
| `plcc_ci_upper` | float | (.4f) | Bootstrap 95% CI 상한 |
| `runtime_ms_per_image` | float | ms | 평균 HSMB 산출 시간 |
| `git_commit` | str | sha7 | 실행 시 v1.py git commit (재현성) |

행 수: 125 (param 조합) × N_conditions (50 full 또는 15 stratified) = **6,250 또는 1,875 행**

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| grid 폭발(125조합 × 50조건 = 6,250 실행) | stratified subset(50→15) 또는 `joblib` 4-worker 병렬화 |
| 현재 값이 최적이 아닌 결과 | 정직하게 보고 + v2(Track 2) 개선 방향으로 연결 서술 |
| C4 사후 정당화 위험 (R05) | JNB 원논문(Ferzli & Karam 2009) + Weibull β 일반론 인용 |
| 단일 실행 평균 200ms 가정 시 직렬 소요 | 6,250 × 10 frame × 200ms ≈ **3.5h** → 4-worker 병렬 시 **≈55분** |
| 메모리 부하 | 1 worker ≈ 200MB (8K 이미지 1장 로드 기준). 4-worker 동시 ≈ 800MB (RTX 3070 8GB·RAM 16GB 여유) |
| 중간 실패 / 재시작 | (R08) `ablation_results.csv` 마지막 행 기준 `(edge_weight, jnb, beta, condition_id)` 중복 skip. idempotent 보장 |
| 결과 변동 (랜덤성) | (R06) `numpy/torch random seed = 42` 고정. GPU 비결정성은 metadata.json에 명시 |
| stratified subset 선정 기준 | 거리 5수준 × 속도 2수준 × ISO {100, 400, 1600} = 30 → 단, ISO 400 (complex-blur)·d=4.5m는 필수 포함 |
| 검증 게이트 실패 시 | F001-1.3 v1.py 모듈화 회귀 의심 → 코드 diff 분석 + 원본 스크립트(`data/01_기존/ps5030_hsmb_v12.py`) 재실행 비교 |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `F001-3` — v1 ablation study
- 의존 Feature: F001-1 (v1.py 모듈화 완료 후)
- 후속 의존: F005-1 (§V-D 작성)

## 7. 참고 자료

- PRD: `00_doc/sp00/d0001_prd.md` §4.1 (v1 파라미터)
- 계획: `00_doc/sp00/d0002_plan.md` E001
- 원논문: Ferzli & Karam 2009 (JNB), Weibull CDF 일반론

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|

---

## 9. Grid 실행 절차 (F001-3.2 구체화)

### 9.1 파라미터 grid 정의

```python
# src/hsmb/ablation.py
PARAM_GRID = {
    "edge_weight": [0.5, 1.0, 1.5, 2.0, 2.5],  # 현재 1.5
    "jnb":         [2,   3,   4,   5,   6  ],  # 현재 3
    "beta":        [1.0, 1.5, 2.0, 2.5, 3.0],  # 현재 2.0
}
# 125 조합
```

### 9.2 데이터 분할 (stratified subset)

| 모드 | 조건 수 | 사용 시점 |
|------|--------|----------|
| `quick` | 15 (속도×거리×ISO{100,400,1600}) | 개발·디버깅 |
| `stratified` | 30 (속도×거리×ISO{100,400,1600} + complex-blur 필수) | 1차 실험 |
| `full` | 50 (전체) | 최종 검증·논문 figure |

### 9.3 실행 단계

| Step | 작업 | 출력 | 도구 |
|------|------|------|------|
| 1 | `gt_50.csv` 로드 + frame 경로 검증 | (in-memory) | pandas |
| 2 | grid × condition 조합 생성 (125 × N) | `tasks: list[(ew, jnb, β, cond)]` | itertools.product |
| 3 | 이미 완료된 조합 skip (R08 재시작) | filtered tasks | resume from csv |
| 4 | `joblib.Parallel(n_jobs=4)` 로 `v1.compute_hsmb(...)` 호출 | per-frame HSMB list | joblib |
| 5 | 조건별 PLCC/SROCC 계산 + Bootstrap 95% CI (10,000회) | per-row dict | scipy.stats, numpy |
| 6 | CSV append (잠금 처리) | `ablation_results.csv` row | filelock + pandas |
| 7 | metadata.json 기록 | `ablation_results.meta.json` | json |
| 8 | 검증 게이트 — (1.5, 3, 2.0) 행 PLCC ≥ 0.93 확인 | (assert) | regression test |
| 9 | heatmap·요약 → `d0030_ablation_report.md` 작성 (F001-3.3) | reports + figures | matplotlib |

### 9.4 CLI 사용 예시

```bash
# 빠른 검증 (개발용, ~6분)
uv run python -m src.hsmb.ablation --mode quick --workers 4

# 1차 실험 (~30분)
uv run python -m src.hsmb.ablation --mode stratified --workers 4

# 최종 (~55분)
uv run python -m src.hsmb.ablation --mode full --workers 4 --bootstrap 10000

# 재시작 (이전 csv 이어서)
uv run python -m src.hsmb.ablation --mode full --resume
```

### 9.5 검증·완료 기준 (Definition of Done)

- [ ] `ablation_results.csv` 행 수 = 125 × N_conditions (mode별)
- [ ] 모든 행에 PLCC/SROCC 산출 (NaN 0건)
- [ ] (1.5, 3, 2.0) 조합의 PLCC mean ≥ 0.93 (R09 게이트)
- [ ] `ablation_results.meta.json` 에 seed=42, torch ver, GPU, git commit 기록
- [ ] heatmap 3종(EW×JNB at β=2.0, EW×β at JNB=3, JNB×β at EW=1.5) PNG 생성
- [ ] F001-3.3 입력으로 `d0030_ablation_report.md` 작성 트리거

### 9.6 후속 (F001-3.3 → F005-1)

- 민감도 heatmap·marginal plot 해석을 `d0030_ablation_report.md`에 정리
- 논문 §V-D 표 / Figure 데이터로 변환
- 현재 값이 sub-optimal일 경우 (1) 보고 + (2) v2(Track 2) 개선 방향 연결 서술
