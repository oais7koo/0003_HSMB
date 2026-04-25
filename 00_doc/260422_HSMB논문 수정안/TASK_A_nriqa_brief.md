# Task A — NR-IQA 스코어 산출

현장 1,500장 이미지 × HSMB + 비교 NR-IQA 6종 = 7개 메트릭 계산

---

## 1. 입력

| 항목 | 개수 | 경로 |
|------|-----|------|
| 현장 area-scan 이미지 | 1,500장 (50조건 × 평균 10장) | 별도 전달 |
| Ground truth (이미 준비됨) | 50 conditions | `data/ground_truth*.csv` |

### 이미지 파일명 규칙 (권장)

```
cam1_v{60,80}_iso{100,200,400,800,1600}_d{25,35,45,55,65}_frame_{XXXXXX}.png
```

`d25 → 2.5 m`, `d35 → 3.5 m` 등 (1/10배 나눔). 또는 기존 tunnelscanning 프로젝트 디렉토리 구조 유지도 가능합니다. 이미지별 (speed, iso, distance, frame) 추출만 일관되면 됩니다.

## 2. 산출 대상 메트릭 (7종)

| # | Metric | 방향 | 구현/라이브러리 권장 |
|---|--------|------|---------------------|
| 1 | **HSMB (우리 메트릭)** | 낮을수록 블러 | `scripts/hsmb_metric.py` |
| 2 | CPBD | 높을수록 선명 | `cpbd` (Python PyPI) 또는 MATLAB 원본 |
| 3 | NIQE | 낮을수록 선명 | scikit-image `niqe` 또는 MATLAB |
| 4 | PIQE | 낮을수록 선명 | MATLAB built-in (piqe) |
| 5 | BRISQUE | 낮을수록 선명 | `pybrisque` 또는 scikit-image |
| 6 | DBCNN | 높을수록 선명 | 공개 pretrained (`DBCNN` repo) |
| 7 | ARNIQA | 높을수록 선명 | 공개 pretrained (https://arxiv.org/abs/2310.14918) |

### 파라미터 고정

HSMB 파라미터는 **기본값 고정** 사용:
- Edge Weight = **1.5**
- JNB = **3**
- β = **2.0**
- 블록 크기 = 64 × 64 (hsmb_metric.py 기본값)

비교 NR-IQA는 각 구현체의 기본값 사용.

## 3. 산출 단위

- **프레임 단위**: 이미지 1장당 7개 스코어 → 1,500 행
- **조건 단위**: 50 조건 × 7 메트릭의 평균/표준편차 → 집계 CSV

## 4. 런타임 기록 (권장)

논문 §V에서 HSMB의 computational efficiency를 주장하려면 다음이 필요합니다:
- 이미지당 HSMB 계산 평균 시간 (ms)
- 이미지당 비교 NR-IQA 각각의 평균 시간 (ms)
- 하드웨어 사양 (CPU/GPU 모델명)

별도 `runtime.csv`로 제출해주세요. 10장 정도 표본만 측정해도 충분합니다.

## 5. 반환 포맷

**필수 CSV 2개** (상세 스키마는 `OUTPUT_FORMAT.md` 참고):

1. `task_A_metrics_per_frame.csv` — 1,500 rows
2. `task_A_metrics_per_condition.csv` — 50 rows

**권장 추가 산출물**:
- `runtime.csv`
- `compute_metrics.py` (실행 코드)
- `requirements.txt` (의존성)
- `run.log` (실행 로그)
- 간단 sanity-check 1p MD

## 6. 주의 사항

### 6.1 Complex-blur 조건 (반드시 포함)

`(ISO=400, distance=4.5 m, 60/80 km/h)` 두 조건 30장 × 2 ≈ 20~25장 이미지가 심하게 블러링되어 있습니다. 이것은 **autofocus 수렴 실패로 추정되는 defocus + motion 복합 블러**이며, **제외하지 말고** 반드시 스코어 산출 부탁드립니다. 우리 측에서 complex-blur stress test에 활용합니다.

자세한 맥락: [section06_draft.md](docs/section06_draft.md)의 "Complex-blur stress test" 서브섹션 참고.

### 6.2 파일명-조건 매핑 검증

`data/ground_truth_frame.csv`의 frame 이름과 전달받은 이미지 파일명이 정확히 매칭되어야 우리 측에서 join 분석이 가능합니다. 샘플 5장 먼저 sanity-check 부탁드립니다.

### 6.3 축 정보 (H/V)

HSMB 및 비교 NR-IQA는 단일 스칼라 반환이면 OK. 방향별 분해(horizontal/vertical)는 우리가 후처리합니다.

### 6.4 Ground Truth 사용 시 주의

`data/ground_truth.csv` 등은 **BEW/MTF50 참고값**입니다. 협업자는 이 값을 **입력으로 사용하지 않습니다** (NR-IQA는 reference-free). 단지 맥락/sanity-check용으로만 제공됩니다.

## 7. 실행 예시

`scripts/example_run_nriqa.py`에 기본 루프 스켈레톤이 있습니다. HSMB 부분만 실행 가능하며, 나머지 메트릭은 각 라이브러리 설치 후 추가해주시면 됩니다.

```bash
python scripts/example_run_nriqa.py --images /path/to/images --out task_A_metrics_per_frame.csv
```

## 8. 협업 흐름

```
1. 이 브리프 검토 (10 min)
2. 샘플 5장으로 sanity-check (30 min)  → 문제 없으면 우리 측에 회신
3. 전체 1,500장 계산 (runtime 추정: 수 시간 ~ 하루)
4. 결과 CSV 이메일 회신
```
