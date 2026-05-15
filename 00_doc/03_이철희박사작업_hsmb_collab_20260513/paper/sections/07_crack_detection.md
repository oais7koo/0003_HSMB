# Section VII — IMPACT OF MOTION BLUR ON CRACK DETECTION

> **Status**: **신규 섹션** (구조 개편 v05 — 2026-04-22). Reviewer C3 (R03) 정면 대응.
> **Dependencies**: External collaborator Task B results (ResNet34 crack detection + HSMB filtering)
> **See also**: `share_package/hsmb_collab_20260421/TASK_B_crack_detection_brief.md`

---

VII.  **IMPACT OF MOTION BLUR ON CRACK DETECTION**

> Placeholder. This section will report the downstream task experiment that
> quantifies the degradation of CNN-based crack detection under varying
> motion blur levels, and verifies whether HSMB threshold-based pre-filtering
> restores detection reliability. Content is populated after the external
> collaborator returns ResNet34 detection results on the 50-condition field
> dataset (see `share_package/hsmb_collab_20260421/`).

### A. EXPERIMENTAL SETUP

- Model: ResNet34 pretrained on crack detection dataset (collaborator-provided)
- Evaluation images: 50-condition field area-scan (pre-registered, see §VI)
- Ground truth: pixel-level or bounding-box annotations (collaborator)
- Metrics: Precision, Recall, F1-score (plus IoU/Dice if available)
- Blur bins (candidate): BEW < 4 (Low), 4–5.5 (Mid), ≥ 5.5 (High)
- HSMB filtering thresholds sweep: T ∈ {0.1, 0.2, …, 0.9}; also report T = 0.63 (paper's P_jnb)

### B. DETECTION PERFORMANCE VS BLUR LEVEL  *[pending]*

*Table 14 (new)*: F1-score mean ± SD across blur bins, 50 conditions.

Expected finding: F1 decreases monotonically as BEW grows, confirming that motion blur degrades CNN-based crack detection (the qualitative claim repeatedly made in the original manuscript now becomes quantitatively supported).

### C. HSMB THRESHOLD-BASED PRE-FILTERING  *[pending]*

*Table 15 (new)*: Threshold sweep results (T, pass ratio, P/R/F1).
*Figure 19 (new)*: T–F1 curve with the operational sweet-spot annotated.

### D. UNFILTERED vs FILTERED COMPARISON  *[pending]*

*Table 16 (new)*: Three rows — unfiltered baseline, T = 0.63, T = optimal.

### E. BEHAVIOUR ON THE COMPLEX-BLUR CELLS  *[pending]*

Explicit reporting of detection F1 on the ISO-400/d = 4.5 m conditions. Expected: HSMB filtering naturally excludes these images (defocus + motion degrades both HSMB and F1), demonstrating that the metric generalises beyond pure motion blur to real operational failure modes.

### F. EXAMPLE OVERLAYS  *[pending]*

*Figure 20 (new)*: 3–5 side-by-side pairs of predicted crack masks before and after HSMB filtering, covering Low/Mid/High blur bins and one complex-blur cell.

---

> **한글 버전**: [ko/07_crack_detection.md](ko/07_crack_detection.md)

## 수정 메모 (Revision Notes)

### 대기 중 (외부 협업자 Task B 결과)

- [ ] ResNet34 기반 crack detection 이미지당 P/R/F1 CSV 수령
- [ ] Table 14 (블러 구간별 F1 요약)
- [ ] Table 15 (HSMB threshold sweep)
- [ ] Table 16 (unfiltered vs filtered 비교)
- [ ] Figure 19 (T–F1 곡선)
- [ ] Figure 20 (예측 오버레이 3~5쌍)
- [ ] Complex-blur 조건에서 HSMB filtering 자연적 배제 여부 확인

### 글쓰기 (데이터 수령 후)

- [ ] §A 실험 setup 본문 작성 (라벨 정의, bin 기준 결정)
- [ ] §B~F 결과 본문 작성
- [ ] §VIII Discussion에서 이 섹션 결과를 연계 서술
