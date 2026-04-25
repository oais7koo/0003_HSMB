# 결과물 CSV 스키마 명세

본 문서는 협업자 반환 파일의 **정확한 포맷**을 정의합니다. 파일명, 컬럼 순서, 데이터 타입을 가능한 한 그대로 지켜주시면 우리 측 후처리가 자동화됩니다.

`results_expected/` 디렉토리에 각 파일의 **빈 템플릿 CSV**가 있습니다.

---

## Task A — NR-IQA 결과

### A-1. `task_A_metrics_per_frame.csv`

**행 수**: 1,500 (frame 단위)

| 컬럼 | 타입 | 단위 | 비고 |
|------|------|------|------|
| `speed_kmh` | int | km/h | 60 or 80 |
| `iso` | int | — | 100 / 200 / 400 / 800 / 1600 |
| `distance_m` | float | m | 2.5 / 3.5 / 4.5 / 5.5 / 6.5 |
| `frame` | str | — | e.g. `frame_000154.png` |
| `hsmb` | float | [0, 1] | HSMB 스코어 |
| `cpbd` | float | — | CPBD 스코어 |
| `niqe` | float | — | NIQE 스코어 |
| `piqe` | float | — | PIQE 스코어 |
| `brisque` | float | — | BRISQUE 스코어 |
| `dbcnn` | float | — | DBCNN 스코어 |
| `arniqa` | float | — | ARNIQA 스코어 |

**예시 row**:
```
60,100,2.5,frame_000154.png,0.6234,0.2144,4.3208,31.5958,43.3911,0.3118,0.4020
```

### A-2. `task_A_metrics_per_condition.csv`

**행 수**: 350 (50 conditions × 7 metrics)

Long format 권장:

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `speed_kmh` | int | |
| `iso` | int | |
| `distance_m` | float | |
| `metric` | str | hsmb / cpbd / niqe / piqe / brisque / dbcnn / arniqa |
| `mean` | float | 조건 내 frame 평균 |
| `sd` | float | 조건 내 frame 표준편차 |
| `n_frames` | int | 조건당 프레임 수 (7~13) |

**예시 row**:
```
60,100,2.5,hsmb,0.6234,0.0412,10
60,100,2.5,cpbd,0.2144,0.0321,10
```

### A-3. `runtime.csv` (권장)

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `metric` | str | hsmb / cpbd / ... |
| `mean_ms_per_image` | float | |
| `n_samples` | int | 측정 표본 수 |
| `hardware` | str | e.g. "Intel i9-13900K / RTX 4090" |

---

## Task B — CNN Crack Detection 결과

### B-1. `task_B_crack_detection_per_image.csv`

**행 수**: 이미지 수 (1,500 또는 subset)

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `speed_kmh` | int | |
| `iso` | int | |
| `distance_m` | float | |
| `frame` | str | Task A와 동일한 key 사용 |
| `hsmb` | float | Task A에서 복사 또는 join 후 기재 |
| `bew_ref` | float | ground_truth_frame.csv의 bew_px (참고) |
| `mtf50_ref` | float | 참고 |
| `tp` | int | True positive count |
| `fp` | int | False positive count |
| `fn` | int | False negative count |
| `precision` | float | |
| `recall` | float | |
| `f1` | float | |
| `complex_blur_flag` | int | (선택) 1 if (iso=400 and d=4.5m) else 0 |

**F1 계산 정의를 파일 상단 comment 또는 별도 `task_B_notes.md`에 기록 부탁**.

### B-2. `task_B_crack_detection_by_blur_bin.csv`

**행 수**: 블러 bin 수 × (옵션: speed 그룹)

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `bin` | str | e.g. "Low", "Mid", "High" |
| `bew_low` | float | bin 하한 |
| `bew_high` | float | bin 상한 |
| `n_images` | int | bin 내 이미지 수 |
| `precision_mean` | float | |
| `recall_mean` | float | |
| `f1_mean` | float | |
| `f1_sd` | float | |

### B-3. `task_B_threshold_sweep.csv`

**행 수**: T sweep 포인트 수 (≥9 권장, T ∈ [0.1, 0.9])

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `hsmb_threshold` | float | pass 조건: hsmb >= T |
| `n_passed` | int | 통과 이미지 수 |
| `pass_ratio` | float | n_passed / total |
| `precision_passed` | float | |
| `recall_passed` | float | |
| `f1_passed` | float | |

### B-4. `task_B_filtering_comparison.csv`

**행 수**: 3 (unfiltered / T=0.63 / T=optimal)

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `scheme` | str | "unfiltered" / "T=0.63" / "T=optimal" |
| `threshold` | float | NaN / 0.63 / {추정값} |
| `n_images` | int | 통과 이미지 |
| `pass_ratio` | float | |
| `precision` | float | |
| `recall` | float | |
| `f1` | float | |

---

## 공통 규칙

### 인코딩 & 구분자

- UTF-8
- 쉼표 구분 (표준 CSV)
- 헤더 필수
- 소수점 `.` 사용, 소수 자릿수 최소 4자리 권장 (`.4f`)
- 결측은 `NaN` (숫자) 또는 빈 문자열 (string)

### 파일명 규칙

- 소문자 + 언더스코어
- 버전 필요 시 suffix `_v2.csv`

### 반환 ZIP 구조 권장

```
hsmb_results_<YYYYMMDD>.zip
├── task_A_metrics_per_frame.csv
├── task_A_metrics_per_condition.csv
├── task_B_crack_detection_per_image.csv
├── task_B_crack_detection_by_blur_bin.csv
├── task_B_threshold_sweep.csv
├── task_B_filtering_comparison.csv
├── runtime.csv
├── task_B_overlays/  (예시 3~5쌍)
├── run.log
├── requirements.txt
├── compute_metrics.py
├── crack_detection_exp.py
└── README.md   (간단 sanity-check 보고)
```

---

## 문의 사항

- 포맷이 일부 호환 안 되면 **그대로 반환하시고 메일에 차이점 메모**를 남겨주시면 우리 측에서 변환하겠습니다.
- 추가 컬럼은 OK (뒤에 붙이세요). 순서는 지키되 뒤쪽 추가는 환영합니다.
