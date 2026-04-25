# Task B — CNN Crack Detection Downstream Analysis

현장 area-scan 이미지에 ResNet34 crack detection 적용 → 블러와 F1-score 관계 + HSMB pre-filtering 효과 정량 검증 (Reviewer C3 대응)

---

## 1. 배경과 목적

**Reviewer C3 원문 요약**: "논문은 모션블러가 defect 검출 신뢰성을 저하시킨다고 주장하나, 실제 downstream task 실험이 없다."

**우리 대응 전략**:
1. **RQ1** — 블러 수준이 증가할수록 crack detection F1이 얼마나 감소하는가?
2. **RQ2** — HSMB score threshold 기반 pre-filtering이 F1을 얼마나 개선하는가?

두 질문에 정량 답변 = Reviewer C3 정면 대응.

**우선순위**: **현장 블러 이미지** 분석이 먼저. 합성 블러는 시간 여유가 있을 때 보조.

## 2. 필요 자산

| 항목 | 담당 | 비고 |
|------|------|------|
| ResNet34 crack detection 가중치 | **협업자 보유** | pretrained on 협업자 dataset |
| 균열 데이터셋 (이미지 + 라벨) | **협업자 보유** | 합성 블러 실험용 (RQ1 precision test) |
| 현장 area-scan 이미지 1,500장 | 사용자 전달 (Task A와 공용) | **RQ1, RQ2 주실험** |
| HSMB score | Task A 산출물 재사용 | threshold sweep 기반 |

## 3. 작업 단계

### Step 1: Baseline (sharp) F1 측정 — 참고용

협업자 보유 clean/sharp crack 이미지에 ResNet34 → baseline P/R/F1 확인 (이미 측정되어 있다면 재활용).

### Step 2: 현장 블러 이미지에서 F1 측정 — **주 실험 (RQ1)**

1,500장 현장 이미지에 ResNet34 적용 → 이미지별 Precision/Recall/F1.

**중요**: 현장 이미지가 **균열 라벨을 갖고 있는 영역** 기반이어야 F1 계산 가능합니다. 실험 Setup:

- **옵션 A** (권장): 현장 이미지 중 균열이 존재하는 영역을 **협업자가 수동 라벨링** (또는 기존 라벨이 있다면 그대로 활용)
- **옵션 B**: 현장 이미지에 **합성 crack overlay** (인쇄된 crack chart 같은 것이 이미 있는지 확인)
- **옵션 C**: 현장 이미지 대신 합성 블러 이미지로 우선 진행 → 현장 이미지는 RQ2에만 사용

협업자 판단에 맡깁니다. 가능한 옵션을 먼저 메일로 알려주시면 확정하겠습니다.

### Step 3: 블러 수준 ↔ F1 관계 (RQ1 정량화)

이미지별 BEW (ground_truth_frame.csv에서 제공) 또는 HSMB (Task A 산출값) 기준 **블러 구간별 F1 집계**:

| 블러 구간 | BEW 범위 (px) | 이미지 수 | F1 (mean ± sd) |
|---|---|---|---|
| Low | < 4 | N1 | — |
| Mid | 4-5.5 | N2 | — |
| High | > 5.5 | N3 | — |

(구간 분할은 협업자 재량. 3~5 bin 권장)

### Step 4: HSMB threshold Pre-filtering (RQ2)

HSMB threshold T ∈ {0.1, 0.2, ..., 0.9} 로 sweep:

- 각 T에서 HSMB > T인 이미지만 통과시킴 (pass_ratio 기록)
- 통과 이미지 부분집합에서 F1 재계산
- **Optimal T** = F1 극대화 + pass_ratio 유지 사이 절충점

**대조군**:
- Unfiltered baseline F1 (전체 1,500장)
- 기존 논문의 P_jnb = **0.63** threshold 적용 결과

### Step 5: HSMB vs F1 이미지 단위 scatter

(HSMB_i, F1_i) 또는 (HSMB_i, correct/incorrect) pair 저장 → 논문용 scatter plot 데이터.

### Step 6: 시각적 예시 3쌍

블러 전후 predicted mask overlay PNG 3~5 쌍. 논문 Figure 후보.

## 4. 반환 포맷

**필수 CSV 3~4개** (스키마는 `OUTPUT_FORMAT.md` 참고):

1. `task_B_crack_detection_per_image.csv` — 이미지별 P/R/F1, HSMB score join 가능하도록 frame 키 유지
2. `task_B_crack_detection_by_blur_bin.csv` — RQ1 요약 테이블
3. `task_B_threshold_sweep.csv` — RQ2 T-F1 curve
4. `task_B_filtering_comparison.csv` — unfiltered vs {0.63, optimal} threshold 비교 (3 행)

**권장 추가 산출물**:
- 예시 overlay PNG 3~5쌍 (논문 Figure)
- `crack_detection_exp.py` (실행 코드)
- `requirements.txt`
- `run.log`

## 5. 주의 사항

### 5.1 라벨 형식 통일

- Pixel-level segmentation → F1 = 2·TP / (2·TP + FP + FN)
- Bounding box detection → IoU ≥ 0.5 기준 TP/FP/FN
- 협업자 기존 pipeline 그대로 사용하시되, F1 계산 정의를 CSV note에 기록

### 5.2 Complex-blur 조건 특별 처리 (선택)

(ISO=400, d=4.5 m) 두 조건은 extreme blur이므로 F1이 가장 낮게 나올 것으로 예상됩니다. 이 조건의 F1 값이 HSMB threshold 기반 filtering에서 배제되는지 여부가 **논문의 핵심 포인트**입니다. 결과에서 이 조건을 별도 표시(예: flag column)하면 우리 측 분석이 수월해집니다. 별도 처리가 어렵다면 없어도 됩니다.

### 5.3 HSMB score 의존성

Task B Step 4는 Task A의 HSMB 결과를 입력으로 사용합니다. 따라서:
- **Task A를 먼저 수행하거나 병행하여 HSMB score 확보**
- Task A와 Task B의 이미지 세트는 동일해야 join 가능

## 6. 실행 예시

`scripts/example_run_crack.py`에 skeleton 있습니다. 협업자의 ResNet34 inference 로직을 삽입하시면 됩니다.

```bash
python scripts/example_run_crack.py \
  --model /path/to/resnet34.pth \
  --images /path/to/field_images \
  --hsmb_scores task_A_metrics_per_frame.csv \
  --out task_B_crack_detection_per_image.csv
```

## 7. 협업 흐름

```
1. 이 브리프 + Section V 배경 검토
2. 라벨 확보 방안 결정 (옵션 A/B/C) → 우리 측 회신
3. Task A와 병행 실행 가능
4. 결과 CSV + 예시 overlay 3~5쌍 회신
```

## 8. 우리 측 후처리 예고

협업자 반환 CSV로 우리가 수행할 것:
- Section V-E 신규 서브섹션 "Impact of Motion Blur on Crack Detection" 작성
- F1 vs BEW scatter plot 및 테이블 생성
- HSMB filtering 효과 논의
- Complex-blur 조건에서의 응답 분석
