# HSMB 협업자 Claude 작업 Brief

> **작성일**: 2026-05-13
> **수신자**: 협업자 측 Claude (HSMB 정량 측정 환경 보유)
> **발신자**: 본 저자 측 Claude (논문 본문/분석 환경)
> **단일 표준 정책 (D29, 2026-04-30)**: 자체 환경 sanity check에서 외부 결과 대비 mean −0.332, Pearson 0.705로 systematic offset 발견 → **모든 정량 측정은 협업자 환경 산출물을 단일 표준으로 채택**. 본 brief의 6개 업무 결과가 논문의 모든 정량 표/그림을 채운다.

---

## 1. 논문 배경 (협업자 Claude 컨텍스트용)

- **제목**: No-Reference Image Quality Assessment for High-Speed Motion Blur Database in Tunnel Inspection
- **저자**: Chulhee Lee, Donggyou Kim, Dongku Kim (KICT)
- **HSMB**: High-Speed Motion Blur — area-scan tunnel inspection imagery용 NR-IQA 메트릭 (BEW/MTF50과 강한 상관, V/H directional balance ≈ 1.02)
- **현재 단계 (D31~D33)**: **분기 투고 전략**
  - **버전 A**: Scientific Reports 재투고 (SR 리뷰 4건 S1.1~S1.4 = R01~R04 응답 + 이미 완료한 IEEE 작업 over-deliver)
  - **버전 B**: IEEE Access 재투고 (버전 A + 잔여 IEEE 정량 항목 C1.1~C2.5)
- **외부 리뷰 라벨**:
  - **SR (S1.x)**: 4건 — area-scan 일관성, 통계 유의성, downstream CNN, 파라미터 근거
  - **IEEE Access (C1.x ~ C2.x)**: 9건 — dataset/4-speed, parameter opt, DL fine-tune + FISH/LPC-SI + FLOPs, field validation / GoPro·NfS 차별성, HTMP calibration, HSMB 수학 formulation, defect detection, ablation rigor
  - **통합 라벨**: R01↔S1.1+C1.4 / R02↔S1.2+C1.1 / R03↔S1.3+C2.4 / R04↔S1.4+C1.2+C2.5

---

## 2. 우선순위 요약

| Tier | # | 업무 | 대응 코멘트 | 버전 |
|------|---|------|-----------|------|
| **🥇 P1** | **③** | 파라미터 grid search + noise sensitivity ablation | S1.4 / R04 / C1.2 / C2.5 | A 필수 |
| **🥇 P1** | **⑥** | Task B — CNN crack detection downstream | S1.3 / R03 / C2.4 | A 필수 |
| **🥇 P1** | **현장** | 현장 area-scan 50조건 원본 이미지 + HSMB 산출 | S1.1 / R01 / C1.4 | A 필수 |
| **🥈 P2** | **①** | HSMB v1 + 8 baseline inference time / FLOPs | C1.3-2 | B 전용 |
| **🥈 P2** | **②** | Sanity 환경 정보 명시 (PNG 변환 / native vs ROI / v1 버전) | (D29 후속) | B 전용 |
| **🥈 P2** | **④** | FISH·LPC-SI 베이스라인 11-지표 확장 | C1.3-1 | B 전용 |
| **🥈 P2** | **⑤** | DBCNN, ARNIQA fine-tuning on HSMB | C1.3-3 | B 전용 |

> P1 3건은 **SR 재투고 일정의 critical path**. 협업자 측 일정 가능 일자 우선 회신 요청.

---

## 3. 공통 표준 환경

| 항목 | 값 |
|------|---|
| HSMB 알고리즘 reference 구현 | `scripts/hsmb_metric.py` (v1, 177 lines) — `/Users/lch/home/db/ps2020_hsmb_v1.py` 수령본 |
| HSMB v1 알고리즘 핵심 | monotonicity walk + 3-point parabolic refinement (EVP threshold + linear 보간 v2와 구별) |
| HSMB 범위 | [0, 1], higher = sharper |
| 실내 데이터 | 470 PNG (40조건 × 평균 ~11장), 2331×1643 (4096×2304 native에서 차트 ROI crop) |
| 실내 조건 | 5 속도 × 4 셔터 × 2 조명 (15000/40000 lx) — 25 μs · 90 km/h는 분석 제외 |
| GT (실내) | `data/lab/ground_truth_by_axis.csv` (H/V 분리), `ground_truth_anisotropy.csv` (Δ diagnostic) |
| 비교 NR-IQA 9 지표 | SSIM, PSNR, CPBD, BRISQUE, NIQE, PIQE, DBCNN, ARNIQA, HSMB |
| 통계 메트릭 | PLCC, SROCC, KRCC + Permutation test (N=10k) + Bootstrap 95% CI |
| 분석 단위 | 조건 단위 (이미지 평균 → 조건 평균) |

> ⚠️ **모든 결과는 v1 코드 + 동일 환경(GPU/CPU 사양 + Python·PyTorch 버전 명시)** 에서 산출. ②번 sanity 환경 정보가 모든 P2 항목의 메타로 따라붙어야 함.

---

## 4. 업무 명세

### ③ 파라미터 grid search + noise sensitivity ablation [P1, 버전 A 필수]

**대응**: S1.4 (Edge Weight 1.5 / JNB 3 / β 2 근거 부재) + R04 + C1.2 (parameter optimization) + C2.5 (ablation rigor)

**입력**:
- HSMB v1 코드 (`scripts/hsmb_metric.py`)
- 실내 470 PNG (`data/lab/images/`)
- 실내 GT (`data/lab/ground_truth_by_axis.csv`)

**작업**:
1. **Grid search** — 다음 4 파라미터 grid에 대해 PLCC(BEW, H축) 및 PLCC(MTF50, V축) 최대화 조합 탐색
   - Edge Weight (`w_e`): {1.0, 1.25, **1.5**, 1.75, 2.0}
   - β (Weibull/Rayleigh shape): {1.0, 1.5, **2.0**, 2.5, 3.0}
   - P_jnb: {0.5, 0.63, **0.7**, 0.77, 0.85}
   - JNB threshold: {2, 2.5, **3**, 3.5, 4}
   - default = bold (현재 §IV-D 본문 채택값)
2. **Noise sensitivity** — default 조합에 다음 합성 노이즈 적용 후 PLCC 변동 측정
   - Gaussian: σ ∈ {0.005, 0.01, 0.02, 0.05} (정규화 [0,1] 기준)
   - Salt & Pepper: density ∈ {0.001, 0.005, 0.01, 0.02}
3. **Sensitivity curve** — 각 파라미터를 default 주변 ±50% 범위에서 단변량 sweep, PLCC vs 파라미터 plot

**산출**:
- `ablation_grid.csv` — columns: `w_e, beta, p_jnb, jnb_th, plcc_bew_h, plcc_mtf50_v, srocc_bew_h, srocc_mtf50_v, krcc_bew_h, krcc_mtf50_v`
- `ablation_noise.csv` — columns: `noise_type, level, plcc_bew_h, plcc_mtf50_v, …`
- `sensitivity_curves.csv` — long format: `param_name, param_value, metric, value`
- (선택) `fig_sensitivity.png` 4-panel — 본 저자 측에서 §IV-E Figure로 재가공

---

### ⑥ Task B — CNN crack detection downstream [P1, 버전 A 필수]

**대응**: S1.3 (downstream CNN 부재) + R03 + C2.4 (defect detection 정량)

**입력**: 협업자 측 보유 균열 데이터셋 + ResNet34 사전학습 weights

**작업**:
1. **블러 수준별 detection 성능** — 최소 3개 이상 블러 수준 (예: blur-free / mild / moderate / severe — HSMB 구간으로 정의)
2. **HSMB threshold sweep** — F1-score vs HSMB threshold 곡선, optimal threshold 식별
3. **Unfiltered vs HSMB-filtered 비교** — 동일 test set에 대해 threshold 적용 전/후 F1·Precision·Recall

**산출**:
- `crack_blur_levels.csv` — `level, hsmb_range, n_images, precision, recall, f1`
- `crack_threshold_sweep.csv` — `hsmb_threshold, n_kept, precision, recall, f1`
- `crack_filter_compare.csv` — `condition (unfiltered|filtered), threshold, precision, recall, f1`
- 시각 예시 3~5 쌍 (블러 전/후 예측 mask overlay) — PNG
- 실험 설정 노트 (`crack_setup.md`): 데이터셋 출처, train/val/test split, 모델 변형, 학습 epoch, hardware

**산출 → 논문 §VII** Tables 14/15/16, Figures 19/20 직접 채움.

---

### 현장 (R01 / S1.1 / C1.4) — 현장 area-scan 원본 이미지 + HSMB 산출 [P1, 버전 A 필수]

**현재 상태**: 현장 GT 50조건만 보유 (`data/field/ground_truth.csv`), 원본 이미지 약 500장 미보유

**입력**: tunnelscanning/cam1 area-scan 8K 촬영분 50조건 (2속도 × 5거리 × 5ISO)

**작업**:
1. 현장 area-scan 원본 이미지 50조건 약 500장 (조건당 7~13장) 정리
2. HSMB v1 + 9-지표(가능한 범위) 적용 → 조건 단위 평균
3. PLCC/SROCC/KRCC × (BEW, MTF50) × (H, V) 산출
4. Complex-blur stress test 조건 (ISO 400, d=4.5m) 별도 응답성 분석

**산출**:
- `field_iqa_image.csv` — image-level (N≈500): `condition_id, speed, distance, iso, frame, hsmb, ssim, …`
- `field_iqa_condition.csv` — condition-level (N=50): condition별 평균 + GT 평균
- `field_correlations.csv` — `metric, axis, target, plcc, srocc, krcc, p_perm, ci95_low, ci95_high`
- `field_complex_blur.csv` — leave-two-out (N=48) 비교 + 이상 셀 응답성 분석
- (선택) `field_heatmaps.png` 4-panel — BEW H/V, MTF50 H/V, anisotropy, speed×anisotropy

**산출 → 논문 §VI** Tables 9~13 + Figure 18 직접 채움.

---

### ① HSMB v1 + 8 baseline inference time / FLOPs [P2, 버전 B]

**대응**: C1.3-2

**입력**: HSMB v1 코드 + 비교 8 메트릭 (SSIM, PSNR, CPBD, BRISQUE, NIQE, PIQE, DBCNN, ARNIQA)

**작업**:
1. 동일 환경(GPU/CPU + Python·PyTorch 버전 명시) 에서 각 메트릭의 이미지당 inference time (ms) — 10회 반복 평균 + 표준편차
2. FLOPs (GFLOPs) 측정 — DL 모델은 `thop`/`fvcore`, traditional 메트릭은 이론적 추정 또는 line-profiler 기반
3. 입력 해상도는 실내 표준 (2331×1643) 기준

**산출**:
- `inference_benchmark.csv` — `metric, ms_per_image_mean, ms_per_image_std, gflops, n_repeat, hw_note`
- `benchmark_env.md` — GPU/CPU/RAM, OS, Python, PyTorch, library versions

**산출 → 논문 §V** 신규 표 (NR-IQA 메트릭 vs inference time vs FLOPs).

---

### ② Sanity 환경 정보 명시 [P2, 버전 B — D29 후속]

**대응**: D29 후속 — 자체 측정 vs 외부 xlsx의 systematic −0.332 offset 원인 규명

**작업** — 협업자가 외부 xlsx (`MTF(15000)-IQA 지표.xlsx`) 산출 시 사용한 환경 메모만 제공해도 충분:
1. **PNG 변환 방식** — 원본(.bmp/.tiff?) → PNG 변환 도구, bit depth, colorspace
2. **이미지 사이즈 처리** — native 4096×2304 그대로? 또는 차트 ROI 2331×1643 crop?
3. **v1 코드 버전** — `ps2020_hsmb_v1.py`와 동일한지, 수정/내부 fork 여부
4. **채널 처리** — grayscale 변환 (rec601 / rec709 / luminosity), 또는 채널별 평균?
5. **실험 일자 + 담당자** — 추후 재현/검증 메타

**산출**: `sanity_env.md` (1~2 paragraph + 5 항목 표) — §IV reference 환경 paragraph로 본문 통합

---

### ④ FISH·LPC-SI 베이스라인 11-지표 확장 [P2, 버전 B]

**대응**: C1.3-1

**입력**: 실내 470 PNG

**작업**:
1. FISH (Fast Image SHarpness, Vu & Chandler 2012) Python 구현/변환
2. LPC-SI (Local Phase Coherence – Sharpness Index, Hassen et al. 2013) 변환
3. 실내 470장에 적용 → 조건 단위 평균
4. 기존 9-지표 산출물 (`data/lab/iqa_filtered.csv`)에 2 컬럼 추가

**산출**:
- `lab_iqa_11metric.csv` — 기존 9 컬럼 + `fish, lpc_si`
- `lab_correlations_11metric.csv` — PLCC/SROCC/KRCC × 11 metrics × H/V × BEW/MTF50
- 구현 노트 (`fish_lpcsi_impl.md`): 참고한 reference code, 검증 결과 (벤치마크 이미지 sanity)

**산출 → 논문 §V-B** Tables 6/7 갱신 (9 → 11 지표).

---

### ⑤ DBCNN, ARNIQA fine-tuning on HSMB [P2, 버전 B]

**대응**: C1.3-3

**입력**: 사전학습 weights (DBCNN, ARNIQA 공식 release) + HSMB 데이터셋

**작업**:
1. HSMB train/val split (예: 32/8 condition, image-level stratified) 정의 + 문서화
2. DBCNN, ARNIQA를 BEW(H) 또는 MTF50(V)에 대해 fine-tune (회귀 head 교체)
3. Pre-trained (zero-shot) vs Fine-tuned PLCC/SROCC 비교

**산출**:
- `dl_finetune.csv` — `model, condition (pretrained|finetuned), target (bew_h|mtf50_v), plcc, srocc, krcc, train_loss_final, val_loss_final, epochs`
- `dl_finetune_setup.md` — split 정의, hyperparameter, hardware, 학습 시간

**산출 → 논문 §V** 신규 표 (DL baseline 재학습 효과).

---

## 5. 결과물 회신 방법

1. **CSV 인코딩**: UTF-8, 컬럼명 영문 snake_case
2. **숫자 포맷**: PLCC/SROCC/KRCC 소수점 4자리, FLOPs/inference time 정수 또는 소수점 2자리
3. **결측치**: `NaN` 또는 빈 셀 (Excel `#N/A` 금지)
4. **압축**: 업무별 디렉토리 (`task_03_ablation/`, `task_06_crack/`, …)로 묶어 zip
5. **메타 파일**: 각 디렉토리에 `README.md` (작업 일자, 실행 환경, 산출 컬럼 의미)
6. **반환 경로** (저자 측 수신): `/Users/lch/home/db/collab_return_YYYYMMDD/`

---

## 6. 참고 자료 (협업자 Claude가 필요시 요청)

- 본 brief — 이 파일
- 이전 패키지: `share_package/hsmb_collab_20260421/` (Task A NR-IQA 7-지표 + Task B CNN 명세 v0)
- 논문 본문 (한글/영문 9 섹션): `paper/sections/`, `paper/sections/ko/`
- PRD: `00_doc/sp00/d0001_prd.md` (v16, 2026-05-01)
- TODO: `00_doc/sp00/d0004_todo.md`
- HSMB v1 코드: `scripts/hsmb_metric.py` + 원본 `/Users/lch/home/db/ps2020_hsmb_v1.py`

추가 정보 필요 시: 본 brief의 어느 섹션·항목인지 명시하여 회신 요청.

---

## 7. 즉석 협의 체크리스트 (지금 같이 있을 때)

- [ ] P1 3건 도착 가능 일자 (③ ablation / ⑥ Task B / 현장 이미지) — SR 일정 결정용
- [ ] ② sanity 환경 메모 — 5분이면 작성 가능, 즉석에서 받아두면 모든 P2 메타로 활용
- [ ] HSMB v1 코드 버전 일치 확인 — `/Users/lch/home/db/ps2020_hsmb_v1.py` vs 협업자 외부 xlsx 산출 시 사용본
- [ ] GPU/CPU 환경 명세 — ① benchmark 메타
- [ ] 균열 데이터셋 접근 가능 여부 (⑥) — 사내 정책 / 라이선스 확인
- [ ] 현장 area-scan 원본 이미지 위치 — 협업자가 직접 HSMB 계산 가능? 또는 본 저자 측으로 전달?
