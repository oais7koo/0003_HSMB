# HSMB 논문 수정 — 협업 패키지

**버전**: 2026-04-21 (v1)
**보내는 이**: Chulhee Lee (KICT)
**받는 이**: *협업자*
**논문**: No-Reference Image Quality Assessment for High-Speed Motion Blur Database in Tunnel Inspection

---

## 1. 한 줄 요약

투고 원고(Revision_0224.docx)가 Reviewer 1 코멘트로 Reject되었고, 재투고를 위해 **(A) NR-IQA 7종 스코어 산출**과 **(B) CNN Crack Detection downstream 분석** 두 작업을 부탁드립니다.

## 2. 왜 이 작업이 필요한가

Reviewer 1 4개 코멘트:

| ID | 지적 | 해결 담당 |
|----|------|----------|
| C1 | 실험실(area-scan) vs 현장(line-scan) 블러 메커니즘 불일치 | 우리 (area-scan 데이터로 교체 완료) |
| C2 | 4 속도 조건만으로 통계적 유의성 부족 | 우리 (50 조건으로 확충 완료) |
| C3 | CNN crack detection downstream task 실험 부재 | **협업자 — Task B** |
| C4 | Edge Weight / JNB / β 파라미터 이론적 근거 | 우리 (ablation study) |

**협업자가 해줘야 하는 것**:
- Task A — 현장 1,500장 이미지에 **HSMB + 비교 NR-IQA 6종** 스코어 계산
- Task B — ResNet34 기반 **crack detection downstream 실험 + HSMB pre-filtering 효과 검증**

## 3. 패키지 구조

```
hsmb_collab_20260421/
├── README.md                       ← 지금 문서
├── TASK_A_nriqa_brief.md           Task A 상세 명세
├── TASK_B_crack_detection_brief.md Task B 상세 명세
├── OUTPUT_FORMAT.md                결과물 CSV 스키마
├── scripts/
│   ├── hsmb_metric.py              HSMB 구현 (Edge Weight=1.5, JNB=3, β=2 기본값)
│   ├── example_run_nriqa.py        Task A 실행 예시
│   └── example_run_crack.py        Task B 실행 예시 (skeleton)
├── data/
│   ├── ground_truth.csv            50 conditions (BEW/MTF50 mean·sd)
│   ├── ground_truth_by_axis.csv    H/V 축 분리
│   └── ground_truth_frame.csv      frame-level (491 rows)
├── docs/
│   ├── section05_draft.md          Section V (Task B 배경)
│   ├── section06_draft.md          Section VI (Task A 배경, Figure 18 해설)
│   └── figures/
│       ├── fig18a_bew_heatmap.png
│       ├── fig18b_mtf50_heatmap.png
│       ├── fig18c_anisotropy_heatmap.png
│       └── fig18d_speed_anisotropy.png
└── results_expected/
    ├── task_A_metrics_per_frame_template.csv
    ├── task_A_metrics_per_condition_template.csv
    ├── task_B_crack_detection_template.csv
    └── task_B_threshold_sweep_template.csv
```

## 4. 별도 준비 물품

| 항목 | 비고 |
|------|------|
| 현장 area-scan 이미지 1,500장 | 사용자(Chulhee)가 별도 전달 — Task A, B 공용 |
| ResNet34 가중치 | **협업자 보유** |
| 균열 데이터셋 (이미지 + 라벨) | **협업자 보유** |

## 5. 실험 개요 요약

### 현장 실험 조건 (Task A, B 공용)

- **카메라**: 8K area-scan, global shutter, 50 μs 노출
- **조명**: 200 W LED strobe (동기화)
- **렌즈**: 24-85 mm 줌, autofocus로 GSD 0.3 mm/px 유지
- **설계**: 3-factor factorial
  - 속도 2개: 60, 80 km/h
  - 거리 5개: 2.5 / 3.5 / 4.5 / 5.5 / 6.5 m
  - ISO 5개: 100 / 200 / 400 / 800 / 1,600
- **조건 수**: 50 (2 × 5 × 5)
- **조건당 프레임 수**: 7~13장 (mean 9.8)
- **총 이미지**: 약 500장 유효 슬랜트 엣지 + 약 1,000장 일반 영역 = 1,500장

### ⚠️ 특수 조건 주의

(ISO=400, d=4.5 m) 두 조건은 **autofocus 수렴 실패로 추정되는 defocus + motion 복합 블러 조건**입니다. 이상치로 제거하지 마시고, 그대로 스코어를 산출해주세요. 우리 측에서 complex-blur stress test로 활용합니다. 자세한 사항은 [section06_draft.md](docs/section06_draft.md)의 Figure 18 및 이방성 분석 참고.

## 6. 일정

기한·우선순위는 **메일 회신으로 협의 예정**입니다. 병렬 진행 가능합니다 (Task A와 B는 독립).

## 7. 기본 연락

- **통신**: 이메일 회신
- **결과물 반환**: 이메일 첨부 또는 공유 드라이브 링크
- **질문**: 이 패키지 어떤 부분이든 모호하면 바로 문의 부탁드립니다

## 8. 진행 순서 제안

1. 이 README 훑어보기 (5분)
2. **TASK_A_nriqa_brief.md** 읽기 (10분)
3. **TASK_B_crack_detection_brief.md** 읽기 (10분)
4. **OUTPUT_FORMAT.md**에서 반환 CSV 포맷 확인 (5분)
5. `scripts/hsmb_metric.py`와 `example_run_*.py` 실행해 환경 세팅 확인
6. 샘플 이미지 5장 + sanity-check 결과 회신 → 경로 매핑 확인 후 전면 실행

## 9. 감사의 말

논문 Reject 상황에서 단기간 재투고 준비에 도움 주셔서 진심으로 감사드립니다.
