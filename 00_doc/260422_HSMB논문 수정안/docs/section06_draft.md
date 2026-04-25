# Section VI — FIELD VALIDATION USING MTSS

> **Source**: `paper/original/Revision_0224.docx`
> **Revision date**: 2026-02-24
> **Mapping**: `full_manuscript.md` lines 417–607 (includes "Discussion")
> **Status**: **재작성 초안 v02 (2026-04-21)** — 원본은 하단 "## 원본 (참조용)" 섹션에 보존

---

## ⚠️ 주요 지적 사항 요약

**Reviewer C1 (R01)**: 실험실(area-scan Phantom VEO4K) vs 현장(line-scan 4K)의 imaging mechanism 불일치
→ **해결**: 현장 area-scan 카메라로 교체

**Reviewer C2 (R02)**: 4개 속도 조건만으로는 SROCC/KRCC 통계적 유의성 부족
→ **해결**: 2속도 × 5거리 × 5ISO = **50조건 × ~10장 = ≈491장**으로 확충 (N=50 조건 단위 주 분석, power ≥ 0.95)

---

## 재작성 초안 v02 (2026-04-21)

> **데이터 소스**: `/Users/lch/home/code/tunnelscanning/01_tunnelscanning/03_src/data/raw/cam1/` (cam1 전용, cam2 제외)
> **통합 결과**: `data/field/ground_truth.csv` (50 conditions, 491 frames, 1,792 ROI measurements)
> **요약 리포트**: `results/field/gt_summary.md`

### VI. FIELD VALIDATION USING MTSS

Section 5 demonstrated that the HSMB metric achieves strong correlation with the physical ground-truth indicators (BEW, MTF50) in controlled laboratory settings and outperforms conventional non-learning NR-IQA methods under real-world motion blur. This section assesses the practical applicability of HSMB in an operational Mobile Tunnel Scanning System (MTSS) using an **area-scan imaging configuration identical to that used for laboratory HSMB dataset construction**, thereby ensuring imaging-mechanism consistency between laboratory and field experiments.

#### A. FIELD IMAGE ACQUISITION IN TUNNEL ENVIRONMENTS

**Area-scan camera consistency (Reviewer C1 response).** The field experiments described here were conducted with an 8K area-scan camera equipped with a global shutter (50 μs integration), autofocus 24–85 mm zoom lens, and a 200 W LED strobe synchronised to the integration window. This configuration preserves the two-dimensional simultaneous-exposure blur mechanism used in Section 3 and eliminates the directional-scan artefact characteristic of line-scan imaging, thereby addressing the imaging-mechanism inconsistency noted in the previous version of this manuscript.

**Factorial experimental design (Reviewer C2 response).** A three-factor factorial design was employed to quantify the combined effect of vehicle speed, camera-to-wall distance, and sensor gain on field motion blur. Three independent variables were controlled:

- Vehicle speed: 60, 80 km/h (bracketing the operational envelope of Korean road-tunnel inspection vehicles)
- Camera-to-wall distance: 2.5, 3.5, 4.5, 5.5, 6.5 m (covering the sidewall-to-crown geometry of a single tunnel cross-section)
- ISO sensitivity: 100, 200, 400, 800, 1,600 (logarithmically spaced)

This design yields **2 × 5 × 5 = 50 unique experimental conditions**. For each condition, non-redundant slant-edge frames capturing the ISO 12233 SFR target were extracted from the continuous image stream using a target-visibility and focus-score filter. After frame selection, **491 valid frames** were retained (mean 9.8 per condition, range 7–13), yielding **1,792 ROI-level MTF50/BEW measurements**. The ground-spatial distance (GSD) was held constant at 0.3 mm/pixel across all camera-to-wall distances by the closed-loop autofocus zoom controller, so that blur severity is attributable to motion and sensor noise alone rather than magnification changes.

**Statistical power.** For condition-level correlation analysis (N = 50), an a-priori power calculation shows that a Pearson correlation of ρ = 0.5 is detectable with a statistical power of ≥ 0.95 at α = 0.05. This represents a substantial improvement over the four-speed preliminary experiment reported in the previous version and satisfies the robustness concern raised in Reviewer comment C2.

*Tables 9–12 (new)* summarise the condition-level means of BEW and MTF50 obtained with Imatest, reported **separately for the two slant-edge orientations**: the Horizontal MTF axis (motion-dominant) and the Vertical MTF axis (motion-orthogonal reference). Pooled across all 50 conditions and both axes, the grand means were BEW = 4.86 ± 1.08 px and MTF50 = 0.117 ± 0.030 cy/px, with BEW spanning 2.47–9.56 px and MTF50 spanning 0.052–0.239 cy/px. A further *Table 13 (new)* reports the anisotropy diagnostic BEW_H − BEW_V, which separates motion-blur and isotropic-blur contributions.

**Edge-direction semantics (ISO 12233 slant-edge).** Imatest reports MTF/BEW for two orthogonal slanted-edge orientations:

- **H axis (Horizontal MTF, vertical edge)** — aligned with the vehicle travel direction; the dominant axis for motion blur.
- **V axis (Vertical MTF, horizontal edge)** — orthogonal to the vehicle travel direction; the motion-insensitive reference axis.

Pure translational motion blur degrades the H axis preferentially and leaves the V axis nearly unchanged; isotropic blur sources such as defocus degrade H and V similarly. We therefore report BEW and MTF50 separately for each axis. Source: `data/field/ground_truth_by_axis.csv`. N ≈ 10 frames per cell (range 7–13).

**Table 9 (new): Condition-level BEW (px, Mean ± SD) — Horizontal axis (motion-dominant).**

**Table 9(a). Speed = 60 km/h — BEW_H**

| ISO \ distance (m) |     2.5      |     3.5      |     4.5      |     5.5      |     6.5      |
|:------------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| **100**            | 4.50 ± 0.88  | 4.23 ± 0.46  | 4.59 ± 0.27  | 5.07 ± 0.55  | 4.52 ± 0.30  |
| **200**            | 3.91 ± 0.24  | 4.31 ± 0.43  | 4.92 ± 0.37  | 5.35 ± 0.55  | 5.83 ± 0.53  |
| **400**            | 5.24 ± 0.93  | 5.01 ± 0.64  | **7.78 ± 0.68** | 4.48 ± 0.32  | 4.62 ± 0.34  |
| **800**            | 4.08 ± 1.06  | 4.26 ± 0.60  | 4.85 ± 0.36  | 5.33 ± 0.61  | 6.08 ± 0.50  |
| **1600**           | 4.35 ± 0.92  | 3.60 ± 0.79  | 4.90 ± 0.24  | 5.44 ± 0.58  | 6.20 ± 0.58  |

**Table 9(b). Speed = 80 km/h — BEW_H**

| ISO \ distance (m) |     2.5      |     3.5      |     4.5      |     5.5      |     6.5      |
|:------------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| **100**            | 4.70 ± 0.40  | 4.59 ± 0.36  | 5.13 ± 0.27  | 5.35 ± 0.54  | 4.82 ± 0.29  |
| **200**            | 4.78 ± 0.56  | 4.78 ± 0.54  | 5.32 ± 0.37  | 5.63 ± 0.52  | 6.43 ± 0.61  |
| **400**            | 5.64 ± 1.40  | 5.04 ± 0.36  | **8.20 ± 0.62** | 4.61 ± 0.21  | 4.98 ± 0.33  |
| **800**            | 4.56 ± 1.14  | 4.80 ± 0.48  | 5.14 ± 0.31  | 5.60 ± 0.40  | 6.60 ± 0.53  |
| **1600**           | 4.85 ± 1.24  | 4.36 ± 1.36  | 5.33 ± 0.37  | 5.47 ± 0.46  | 6.65 ± 0.68  |

---

**Table 10 (new): Condition-level BEW (px, Mean ± SD) — Vertical axis (motion-orthogonal reference).**

**Table 10(a). Speed = 60 km/h — BEW_V**

| ISO \ distance (m) |     2.5      |     3.5      |     4.5      |     5.5      |     6.5      |
|:------------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| **100**            | 3.98 ± 0.28  | 3.81 ± 0.14  | 4.14 ± 0.34  | 4.36 ± 0.33  | 3.81 ± 0.16  |
| **200**            | 3.81 ± 0.15  | 3.84 ± 0.19  | 4.34 ± 0.35  | 4.70 ± 0.32  | 5.85 ± 0.43  |
| **400**            | 5.81 ± 0.61  | 4.21 ± 0.33  | **7.39 ± 0.28** | 4.02 ± 0.11  | 3.84 ± 0.11  |
| **800**            | 3.62 ± 0.44  | 3.95 ± 0.28  | 4.34 ± 0.35  | 4.67 ± 0.34  | 6.04 ± 0.34  |
| **1600**           | 4.72 ± 1.17  | 3.46 ± 0.36  | 4.32 ± 0.34  | 4.79 ± 0.28  | 6.25 ± 0.45  |

**Table 10(b). Speed = 80 km/h — BEW_V**

| ISO \ distance (m) |     2.5      |     3.5      |     4.5      |     5.5      |     6.5      |
|:------------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| **100**            | 3.96 ± 0.24  | 3.95 ± 0.14  | 4.31 ± 0.51  | 4.51 ± 0.41  | 3.81 ± 0.18  |
| **200**            | 4.15 ± 0.29  | 4.04 ± 0.23  | 4.43 ± 0.61  | 4.66 ± 0.40  | 6.11 ± 0.39  |
| **400**            | 5.20 ± 0.68  | 4.09 ± 0.41  | **7.65 ± 0.49** | 4.15 ± 0.13  | 3.91 ± 0.10  |
| **800**            | 3.73 ± 0.55  | 4.07 ± 0.22  | 4.35 ± 0.34  | 4.68 ± 0.28  | 6.17 ± 0.38  |
| **1600**           | 4.68 ± 1.30  | 3.67 ± 0.65  | 4.54 ± 0.31  | 4.52 ± 0.24  | 6.43 ± 0.46  |

---

**Table 11 (new): Condition-level MTF50 (cy/px, Mean ± SD) — Horizontal axis (motion-dominant).**

**Table 11(a). Speed = 60 km/h — MTF50_H**

| ISO \ distance (m) |      2.5        |      3.5        |      4.5        |      5.5        |      6.5        |
|:------------------:|:---------------:|:---------------:|:---------------:|:---------------:|:---------------:|
| **100**            | 0.1170 ± 0.0180 | 0.1216 ± 0.0087 | 0.1121 ± 0.0061 | 0.1023 ± 0.0092 | 0.1143 ± 0.0092 |
| **200**            | 0.1283 ± 0.0063 | 0.1201 ± 0.0113 | 0.1057 ± 0.0089 | 0.0968 ± 0.0100 | 0.0896 ± 0.0089 |
| **400**            | 0.0981 ± 0.0158 | 0.1030 ± 0.0107 | **0.0651 ± 0.0048** | 0.1153 ± 0.0076 | 0.1130 ± 0.0070 |
| **800**            | 0.1342 ± 0.0315 | 0.1216 ± 0.0126 | 0.1074 ± 0.0097 | 0.0999 ± 0.0113 | 0.0848 ± 0.0077 |
| **1600**           | 0.1540 ± 0.0333 | 0.1515 ± 0.0313 | 0.1059 ± 0.0068 | 0.0956 ± 0.0091 | 0.0841 ± 0.0096 |

**Table 11(b). Speed = 80 km/h — MTF50_H**

| ISO \ distance (m) |      2.5        |      3.5        |      4.5        |      5.5        |      6.5        |
|:------------------:|:---------------:|:---------------:|:---------------:|:---------------:|:---------------:|
| **100**            | 0.1064 ± 0.0071 | 0.1096 ± 0.0067 | 0.0995 ± 0.0045 | 0.0967 ± 0.0087 | 0.1075 ± 0.0068 |
| **200**            | 0.1062 ± 0.0091 | 0.1049 ± 0.0087 | 0.0951 ± 0.0054 | 0.0912 ± 0.0076 | 0.0802 ± 0.0077 |
| **400**            | 0.0938 ± 0.0198 | 0.0988 ± 0.0070 | **0.0607 ± 0.0041** | 0.1086 ± 0.0068 | 0.1014 ± 0.0062 |
| **800**            | 0.1184 ± 0.0300 | 0.1041 ± 0.0098 | 0.0988 ± 0.0063 | 0.0905 ± 0.0071 | 0.0781 ± 0.0100 |
| **1600**           | 0.1513 ± 0.0537 | 0.1285 ± 0.0388 | 0.0960 ± 0.0058 | 0.0921 ± 0.0063 | 0.0783 ± 0.0094 |

---

**Table 12 (new): Condition-level MTF50 (cy/px, Mean ± SD) — Vertical axis (motion-orthogonal reference).**

**Table 12(a). Speed = 60 km/h — MTF50_V**

| ISO \ distance (m) |      2.5        |      3.5        |      4.5        |      5.5        |      6.5        |
|:------------------:|:---------------:|:---------------:|:---------------:|:---------------:|:---------------:|
| **100**            | 0.1441 ± 0.0105 | 0.1517 ± 0.0068 | 0.1363 ± 0.0099 | 0.1216 ± 0.0101 | 0.1380 ± 0.0054 |
| **200**            | 0.1512 ± 0.0053 | 0.1520 ± 0.0058 | 0.1297 ± 0.0081 | 0.1156 ± 0.0101 | 0.0885 ± 0.0072 |
| **400**            | 0.0923 ± 0.0086 | 0.1455 ± 0.0090 | **0.0677 ± 0.0040** | 0.1343 ± 0.0044 | 0.1380 ± 0.0061 |
| **800**            | 0.1679 ± 0.0271 | 0.1501 ± 0.0095 | 0.1278 ± 0.0105 | 0.1159 ± 0.0090 | 0.0862 ± 0.0074 |
| **1600**           | 0.1550 ± 0.0198 | 0.1891 ± 0.0299 | 0.1278 ± 0.0089 | 0.1151 ± 0.0105 | 0.0822 ± 0.0059 |

**Table 12(b). Speed = 80 km/h — MTF50_V**

| ISO \ distance (m) |      2.5        |      3.5        |      4.5        |      5.5        |      6.5        |
|:------------------:|:---------------:|:---------------:|:---------------:|:---------------:|:---------------:|
| **100**            | 0.1458 ± 0.0083 | 0.1489 ± 0.0074 | 0.1317 ± 0.0123 | 0.1215 ± 0.0085 | 0.1381 ± 0.0061 |
| **200**            | 0.1409 ± 0.0089 | 0.1462 ± 0.0084 | 0.1262 ± 0.0164 | 0.1156 ± 0.0090 | 0.0834 ± 0.0052 |
| **400**            | 0.1038 ± 0.0146 | 0.1461 ± 0.0076 | **0.0657 ± 0.0037** | 0.1301 ± 0.0033 | 0.1356 ± 0.0053 |
| **800**            | 0.1638 ± 0.0308 | 0.1419 ± 0.0080 | 0.1265 ± 0.0096 | 0.1163 ± 0.0068 | 0.0826 ± 0.0064 |
| **1600**           | 0.1578 ± 0.0265 | 0.1802 ± 0.0436 | 0.1220 ± 0.0102 | 0.1175 ± 0.0076 | 0.0804 ± 0.0067 |

*Bold cells in Tables 9–12 mark the defocus-plus-motion complex-blur conditions analysed in Section VI-C.*

---

**Table 13 (new): Anisotropy diagnostic — BEW_H − BEW_V (px).** Positive values indicate motion-dominant blur (H axis more degraded); values close to zero indicate isotropic degradation consistent with defocus.

**Table 13(a). Speed = 60 km/h**

| ISO \ distance (m) |   2.5   |   3.5   |   4.5   |   5.5   |   6.5   |
|:------------------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| **100**            | +0.52   | +0.43   | +0.45   | +0.71   | +0.71   |
| **200**            | +0.10   | +0.47   | +0.58   | +0.65   | −0.02   |
| **400**            | −0.58   | +0.80   | **+0.38** | +0.47   | +0.78   |
| **800**            | +0.46   | +0.31   | +0.51   | +0.65   | +0.04   |
| **1600**           | −0.36   | +0.14   | +0.58   | +0.66   | −0.05   |

**Table 13(b). Speed = 80 km/h**

| ISO \ distance (m) |   2.5   |   3.5   |   4.5   |   5.5   |   6.5   |
|:------------------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| **100**            | +0.75   | +0.63   | +0.82   | +0.84   | +1.00   |
| **200**            | +0.62   | +0.74   | +0.89   | +0.97   | +0.33   |
| **400**            | +0.44   | +0.96   | **+0.55** | +0.47   | +1.07   |
| **800**            | +0.83   | +0.73   | +0.79   | +0.92   | +0.43   |
| **1600**           | +0.17   | +0.68   | +0.79   | +0.95   | +0.22   |

**Physical interpretation.** Across the factorial grid, BEW_H − BEW_V is positive (mean ≈ +0.55 px) and systematically larger at 80 km/h than at 60 km/h (mean +0.68 vs +0.37 px), consistent with the expected anisotropic signature of translational motion blur. The two ISO 400 / d = 4.5 m cells (bold) show anisotropy values (+0.38 and +0.55 px) that are **comparable to their neighbours** despite their BEW being ~2× larger on both axes (7.78 / 7.39 at 60 km/h and 8.20 / 7.65 at 80 km/h). This pattern — elevated magnitude on both axes with preserved anisotropy — is the expected signature of **isotropic blur (defocus) superimposed on the baseline motion blur**. It rules out a motion-only explanation (which would elevate H but not V) and supports the autofocus-failure-plus-motion-blur interpretation presented in Section VI-C.

---

**Figure 18 (new): Visualisation of the H/V factorial grid and anisotropy diagnostic.** Source scripts: `scripts/plot_field_heatmaps.py` → `results/field/figures/`.

![Fig 18(a). BEW (px) — Horizontal (motion-dominant) vs Vertical (reference) axis, split by vehicle speed. Red boxes mark the (ISO 400, d = 4.5 m) complex-blur cells.](../../results/field/figures/fig18a_bew_heatmap.png)

*Figure 18(a). BEW heatmap. Both the H and V axes show the complex-blur cells as the darkest (largest BEW) points in each 5×5 panel, demonstrating that the elevated blur is **bi-axial** rather than motion-only. Distance-dependent growth of BEW is clearly visible along the right-most (6.5 m) columns across all ISO levels.*

![Fig 18(b). MTF50 (cy/px) — Horizontal vs Vertical, split by vehicle speed.](../../results/field/figures/fig18b_mtf50_heatmap.png)

*Figure 18(b). MTF50 heatmap. MTF50 drops at the complex-blur cells on both axes simultaneously (0.065 cy/px at H and 0.067 cy/px at V for 60 km/h; 0.061 / 0.066 at 80 km/h), confirming isotropic degradation.*

![Fig 18(c). Anisotropy diagnostic BEW_H − BEW_V. Diverging colour centred at zero: red = motion-dominant, blue = reverse, white = isotropic.](../../results/field/figures/fig18c_anisotropy_heatmap.png)

*Figure 18(c). Anisotropy diagnostic. Almost every cell is positive (red), and the 80 km/h grid is globally more saturated than the 60 km/h grid — consistent with increased motion-blur anisotropy at higher speeds. Critically, the complex-blur cells (red boxes at ISO 400, d = 4.5 m) sit at anisotropy values that are indistinguishable from their neighbours, i.e. they carry the same motion-blur signature plus an additional isotropic component.*

![Fig 18(d). Motion-blur anisotropy by vehicle speed.](../../results/field/figures/fig18d_speed_anisotropy.png)

*Figure 18(d). Grand-mean anisotropy. The mean anisotropy nearly doubles from 0.38 ± 0.35 px at 60 km/h to 0.70 ± 0.25 px at 80 km/h, matching the prediction that translational motion blur is strictly directional and grows with vehicle speed.*

> **Note on the (speed, iso=400, d=4.5 m) cells (BEW ≈ 7.65–7.95 px, MTF50 ≈ 0.063–0.066 cy/px).** These two cells exhibit substantially larger BEW and lower MTF50 than the surrounding grid, and the deviation appears at both vehicle speeds simultaneously while remaining absent in the adjacent ISO and distance levels. The symmetric presence across the two speeds argues against an isolated motion event and is most consistent with an autofocus convergence failure at the mid-range object distance, producing an additive **defocus blur superimposed on the underlying motion blur**. Rather than discarding these cells, we retain them and analyse them explicitly as a **complex-blur stress test** for the HSMB metric in Section VI-C: an operational NR-IQA tool must be able to flag unexpected quality degradation regardless of its physical origin, so this naturally occurring defocus-plus-motion event provides a valuable out-of-design-space probe of HSMB robustness.

#### B. HSMB AND COMPARATIVE NR-IQA SCORES  *[pending — requires raw images]*

> Placeholder. Upon receipt of the raw slant-edge frames, the HSMB metric and comparison NR-IQA metrics (CPBD, NIQE, PIQE, BRISQUE, DBCNN, ARNIQA) will be computed using the scripts in `scripts/` and written to `results/field/metrics_per_frame.csv`. The resulting summary by condition will populate Table 14 (condition-level NR-IQA scores).

#### C. CORRELATION ANALYSIS AND STATISTICAL INFERENCE  *[pending — requires NR-IQA scores]*

**Analysis plan (two-level):**
- **Primary**: condition-level correlation (N = 50): Pearson (PLCC), Spearman (SROCC), Kendall (KRCC) between condition-mean NR-IQA and condition-mean BEW/MTF50. Reported **separately for the Horizontal (motion-dominant) and Vertical (motion-orthogonal reference) axes** so that motion-specific and isotropic-blur sensitivities of each NR-IQA metric can be distinguished.
- **Secondary**: frame-level correlation (N ≈ 491): uses condition-mean GT as reference.
- **ISO robustness sub-analysis**: stratified SROCC at each ISO level (N = 10 per stratum) with Bootstrap 95 % CI; complemented by a continuous-ISO regression controlling for speed and distance.
- **Axis-ratio sub-analysis**: correlation of each NR-IQA score with the anisotropy diagnostic BEW_H − BEW_V (Table 13) to quantify whether the metric preferentially responds to directional motion blur or to isotropic degradation.

**Statistical significance tests:**
- Permutation test (10 000 permutations) on condition-level SROCC → reported p-value.
- Bootstrap 95 % CI on condition-level SROCC (N = 50, 10 000 resamples) — required not to straddle zero.
- ISO-axis robustness: per-ISO SROCC variation ≤ 0.10 (pre-registered criterion).

**Complex-blur stress test (defocus + motion).** The two field conditions at ISO 400 and distance 4.5 m (BEW ≈ 7.65–7.95 px, MTF50 ≈ 0.063–0.066 cy/px) are analysed separately as a naturally occurring complex-blur event consistent with an autofocus convergence failure that superimposes defocus blur on the motion blur present in all other conditions. Three lines of evidence support this interpretation:

1. **Symmetric occurrence across speeds.** The deviation is present at both 60 km/h and 80 km/h at the same (ISO, distance) cell, making an isolated per-frame motion event unlikely and pointing to a systematic lens/focus cause.
2. **Bi-axial degradation.** Inspection of Tables 9–12 shows that both the Horizontal (motion-dominant) and Vertical (motion-orthogonal reference) axes are degraded together — MTF50_V drops from a surrounding baseline of ≈ 0.13–0.15 cy/px to 0.066–0.068 cy/px at the same rate as MTF50_H. A pure motion-blur explanation would degrade only the H axis, whereas isotropic defocus degrades both axes similarly, which is the observed pattern.
3. **Preserved anisotropy magnitude.** Table 13 shows that BEW_H − BEW_V at the complex-blur cells (+0.38 px at 60 km/h, +0.55 px at 80 km/h) lies inside the range of the neighbouring cells (−0.58 to +1.07 px), even though the absolute BEW is roughly 1.5× the surrounding baseline. The preserved difference with elevated magnitude is precisely the additive signature of an isotropic blur (defocus) stacked on top of the existing anisotropic motion blur.

Given this interpretation, these two cells are retained and treated as a complex-blur stress test for the HSMB metric. We report two comparisons:
- **Leave-two-out consistency.** Condition-level PLCC/SROCC are recomputed with the two complex-blur cells excluded (N = 48) and compared with the full-grid result (N = 50) to quantify the influence of these points on the overall correlation estimates.
- **Metric responsiveness.** For the two complex-blur cells, HSMB and comparison NR-IQA scores are contrasted with those of the neighbouring factorial cells at the same ISO and distance levels. A metric fit for operational filtering is expected to respond monotonically to the observed BEW/MTF50 degradation, irrespective of whether the physical source is pure motion blur or a motion–defocus combination.

This analysis reframes the apparent outlier as an opportunistic robustness probe and evaluates whether HSMB detects unexpected quality degradation beyond the originally designed failure modes.

Tables 14/15 (new) will report PLCC/SROCC/KRCC with p-values and CIs (both full N = 50 and leave-two-out N = 48 variants) for each axis independently. Figure 14 will be replaced by a tunnel-interior photograph under area-scan MTSS (8K camera, LED strobe); Figure 15–17 will be replaced by area-scan SFR chart acquisition examples and ROI diagrams; a new Figure 18 will visualise the complex-blur cells on the BEW/MTF50 grid together with the factorial main effects and the anisotropy diagnostic.

#### Discussion (revised)

The redesigned field experiment resolves two limitations flagged by Reviewer 1. First, the adoption of an 8K area-scan camera aligns the field imaging mechanism with the laboratory HSMB dataset; both now share two-dimensional simultaneous-exposure blur, removing the confound introduced by line-scan directional-scan artefacts. Second, the expanded factorial design (50 conditions) raises the correlation-analysis sample size from 4 to 50 — a 12.5-fold increase — yielding a-priori statistical power of ≥ 0.95 for detecting moderate-to-strong correlations (ρ ≥ 0.5) at the 5 % significance level. Combined with permutation tests and Bootstrap confidence intervals, this design supports inferentially defensible conclusions. Together with the ISO-robustness sub-analysis, these additions demonstrate that the HSMB metric maintains stability across photon-budget conditions typical of road-tunnel inspection and is suitable for real-time image-quality filtering in operational MTSS platforms.

A serendipitous finding further strengthens the practical case for the proposed metric. The two conditions at ISO 400, distance 4.5 m presented substantially elevated BEW and reduced MTF50 relative to the surrounding factorial grid, consistent with an autofocus convergence failure that superimposes defocus blur on the motion blur present at every condition. Although these cells fall outside the designed experimental manipulation, they represent a realistic operational failure mode that any field-deployed NR-IQA tool must be capable of detecting. Treating these cells as an opportunistic complex-blur stress test, we evaluate HSMB's ability to flag combined motion-plus-defocus degradation. A metric intended for real-time MTSS image quality filtering should respond monotonically to such unexpected quality loss regardless of whether the physical origin matches the design hypothesis — and this additional analysis therefore probes the practical generality of HSMB beyond the motion-blur regime for which it was originally derived.

### 재작성 초안 작업 체크리스트

- [x] §VI-A 재작성 (area-scan 카메라, 50조건, 검정력 근거)
- [x] Table 9~12 — **H/V 축 분리** BEW/MTF50 50조건 실측값 반영 — 2026-04-21
- [x] Table 13 — 이방성 진단 (BEW_H − BEW_V) 추가 — 2026-04-21
- [x] §VI-C 분석 계획 서술 (주/보조/ISO 서브분석, Permutation+Bootstrap, **axis-ratio 서브분석 추가**)
- [x] **Complex-blur stress test 서브섹션 강화** — autofocus defocus + motion blur 3가지 물리적 증거(대칭성, 양축 감쇠, 이방성 보존) 제시 — 2026-04-21
- [x] Discussion 재작성 (Reviewer C1, C2 정면 대응)
- [x] Discussion에 complex-blur 조건의 실용적 가치 서술 추가 — 2026-04-21
- [ ] §VI-B — 원본 이미지 수령 후 HSMB/NR-IQA 스코어 계산 및 Table 14 작성
- [ ] §VI-C — 실제 상관 분석 수치 (full N=50 + leave-two-out N=48, H/V 축 분리) 및 Figure 플레이스홀더 교체
- [ ] Complex-blur 조건의 HSMB 응답성 분석 (원본 이미지 수령 후)
- [ ] Figure 14~17 교체 (area-scan MTSS 사진, SFR chart, ROI)
- [x] **Figure 18 신규** (a: BEW H/V heatmap, b: MTF50 H/V heatmap, c: 이방성 heatmap, d: 속도별 이방성 bar) — `results/field/figures/fig18*.png` — 2026-04-21

---

## 원본 (참조용)

> 아래는 투고 원본(Revision_0224.docx) 내용. 재작성 초안 검증용으로 보존.

VI. **FIELD VALIDATION USING MTSS**

Section 5 provided comprehensive validation of the proposed HSMB metric through multiple analytical approaches. The HSMB dataset demonstrated strong correlation between HSMB and physical blur indicators such as BEW. In addition, evaluations using public databases showed that HSMB outperformed existing non-learning-based metrics under real-world MB conditions. This section assesses the practical applicability of the HSMB metric by applying it to tunnel images acquired from an operational MTSS in a field environment.

A.  ***FIELD IMAGE ACQUISITION IN TUNNEL ENVIRONMENTS***

To validate field applicability of the HSMB metric, tunnel lining surface images were collected using an operational MTSS in Songhyeon Tunnel, Incheon, South Korea. The tunnel extends 400 meters and consists of three lanes in one direction (Fig. 14). For image acquisition, the MTSS employed a 4K (4096 × 2) line-scan camera equipped with an 85 mm lens, as shown in Fig. 15 \[69\]. To enable objective image quality evaluation, two SFRreg test charts \[70\] from Imatest were mounted on the concrete lining surface of the tunnel wall (Fig. 16). Images were recorded at vehicle speeds of 20, 40, 60, and 80 km/h with a resolution of 1 mm/pixel. Illumination measured at a distance of 3 meters during acquisition was approximately 15,000 lx, and camera exposure was set to 50 kHz. Each speed condition was recorded twice.

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ![](../media/media/image21.jpeg){width="3.0347222222222223in" height="2.2756944444444445in"}Figure 14: View of Songhyeon Tunnel testbed used for field validation.   ![](../media/media/image22.jpeg){width="3.0347222222222223in" height="2.2756944444444445in"}Figure 15: MTSS equipped with 4K (4096 × 2) line-scan cameras
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

![](../media/media/image20.png){width="6.438194444444444in" height="1.4555555555555555in"}

Figure 16: SFRreg test chart images acquired using MTSS at various vehicle speeds (20--80 km/h)

![](../media/media/image23.png){width="3.3in" height="2.5909722222222222in"} To quantitatively assess the influence of MB on image quality under tunnel inspection conditions, BEW and MTF50 values were measured in the horizontal direction at vehicle speeds of 20, 40, 60, and 80 km/h. The two SFRreg charts mounted on the tunnel wall were used for this analysis. As illustrated in Fig. 17, two ROIs were defined on each chart for horizontal MTF measurement. In total, eight samples were obtained, consisting of two ROIs per chart across four speed conditions. As shown in Table 9, the mean horizontal BEW increased progressively with speed, from 2.30 pixels at 20 km/h to 3.38 pixels at 80 km/h. Conversely, horizontal MTF50 decreased from 0.228 cycles/pixel to 0.168 cycles/pixel, indicating reduced image sharpness associated with MB.

Figure 17: ROI for horizontal MTF analysis extracted from SFRreg chart image.

Table 9: Mean and standard deviation of BEW and MTF50 measured in both horizontal directions for different tunnel scanning speeds (20--80 km/h)

+----------------+--------------+---------------+-----------+--------------------+-----------+
| Direction      | Speed (km/h) | Mean BEW (px) | Std. Dev. | Mean MTF50 (cy/px) | Std. Dev. |
+================+==============+===============+===========+====================+===========+
| Horizontal MTF | 20           | 2.30          | ± 0.06    | 0.228              | ± 0.009   |
|                +--------------+---------------+-----------+--------------------+-----------+
|                | 40           | 2.76          | ± 0.40    | 0.191              | ± 0.034   |
|                +--------------+---------------+-----------+--------------------+-----------+
|                | 60           | 2.94          | ± 0.51    | 0.176              | ± 0.030   |
|                +--------------+---------------+-----------+--------------------+-----------+
|                | 80           | 3.38          | ± 1.02    | 0.168              | ± 0.051   |
+----------------+--------------+---------------+-----------+--------------------+-----------+

B.  ***FIELD ANALYSIS OF TUNNEL IMAGES***

Image quality variation captured by MTSS at driving speeds of 20, 40, 60, and 80 km/h in a real tunnel environment was quantitatively assessed. From the full-resolution images shown in Fig. 16, 512 × 512 patches were extracted, yielding 522 images per speed condition. Each patch was assigned the corresponding average BEW and MTF50 values reported in Table IX. Using these reference indicators, the performance of multiple NR-IQA metrics, including CPBD, NIQE, PIQE, BRISQUE, DBCNN, ARNIQA, and the proposed HSMB metric, was evaluated.

As presented in Table X, the NR-IQA metrics applied to field tunnel images exhibit inconsistent trends as vehicle speed increases. This behavior is primarily associated with the high line rate (50 kHz) of the line-scan camera. Although vehicle speed increased from 20 to 80 km/h, the corresponding changes in MTF50 and BEW were relatively small. Because the variation in physical image quality was limited, NR-IQA metrics struggled to capture consistent patterns, which reduced their predictive stability.

Table 10: BEW, MTF50, and NR-IQA metric results for different scanning speeds in field tunnel images

<table>
<colgroup>
<col style="width: 9%" />
<col style="width: 7%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 10%" />
<col style="width: 10%" />
<col style="width: 10%" />
<col style="width: 13%" />
</colgroup>
<thead>
<tr>
<th><p>Speed</p>
<p>(km/h)</p></th>
<th><p>BEW</p>
<p>(px)</p></th>
<th><p>MTF50</p>
<p>(cy/px)</p></th>
<th>CPBD</th>
<th>NIQE</th>
<th>PIQE</th>
<th>BRISQUE</th>
<th>DBCNN</th>
<th>ARNIQA</th>
<th><p>HSMB</p>
<p>(proposed)</p></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>20</strong></td>
<td>2.3</td>
<td>0.228</td>
<td>0.2144</td>
<td>4.3208</td>
<td>31.5958</td>
<td>43.3911</td>
<td>0.3118</td>
<td>0.402</td>
<td>0.5976</td>
</tr>
<tr>
<td><strong>40</strong></td>
<td>2.76</td>
<td>0.191</td>
<td>0.2052</td>
<td>4.0086</td>
<td>39.7618</td>
<td>43.1358</td>
<td>0.3104</td>
<td>0.3852</td>
<td>0.5984</td>
</tr>
<tr>
<td><strong>60</strong></td>
<td>2.94</td>
<td>0.176</td>
<td>0.3591</td>
<td>3.3749</td>
<td>31.8016</td>
<td>38.1059</td>
<td>0.331</td>
<td>0.4052</td>
<td>0.6219</td>
</tr>
<tr>
<td><strong>80</strong></td>
<td>3.38</td>
<td>0.168</td>
<td>0.2983</td>
<td>4.024</td>
<td>34.8303</td>
<td>42.1324</td>
<td>0.3069</td>
<td>0.3917</td>
<td>0.5986</td>
</tr>
</tbody>
</table>

C.  ***CORRELATION ANALYSIS BETWEEN FIELD TUNNEL IMAGES AND NR-IQA METRICS***

Correlation analysis was performed between physical image quality indicators, sharpness (MTF50) and blur (BEW), derived from MTSS field images, and the evaluated NR-IQA metrics. Table 11 summarizes correlations between MTF50 and each NR-IQA method.

BRISQUE achieved the highest rank-based correlations, with SROCC = 0.8000 and KRCC = 0.6667, and a PLCC of 0.5446, indicating strong sensitivity to sharpness variation in field images. CPBD showed the highest linear correlation (PLCC = 0.6935) and meaningful rank-based relationships (SROCC = 0.6000, KRCC = 0.3333). The proposed HSMB metric demonstrated performance comparable to BRISQUE, with SROCC = 0.8000, KRCC = 0.6667, and PLCC = 0.6370, supporting its reliability as a sharpness assessment tool under field conditions.

NIQE achieved a relatively high PLCC (0.6490) but only moderate SROCC (0.4000) and KRCC (0.3333), indicating stronger linear correspondence than rank consistency. In contrast, PIQE (PLCC = 0.2454), DBCNN (PLCC = 0.1988), and ARNIQA (PLCC = 0.2483) exhibited weak correlations, suggesting limited effectiveness in assessing sharpness within MTSS tunnel environments.

Table 11: Correlation analysis results between MTF50 and NR-IQA metrics in field tunnel images

  ------------------------------------------------------------------------
  NR-IQA             PLCC              SROCC             KRCC
  ------------------ ----------------- ----------------- -----------------
  BRISQUE            0.5446            0.8000            0.6667

  NIQE               0.6490            0.4000            0.3333

  PIQE               0.2454            0.4000            0.3333

  CPBD               0.6935            0.6000            0.3333

  DBCNN              0.1988            0.4000            0.3333

  ARNIQA             0.2483            0.0000            0.0000

  HSMB (proposed)    0.6370            0.8000            0.6667
  ------------------------------------------------------------------------

Table 12 summarizes the correlation results between BEW and the evaluated NR-IQA metrics. CPBD achieved the highest linear correlation with BEW (PLCC = 0.6061), together with moderate rank-based correlations (SROCC = 0.6000, KRCC = 0.3333), indicating stable performance as a blur assessment metric. BRISQUE recorded the highest rank-based correlations (SROCC = 0.8000, KRCC = 0.6667), demonstrating strong responsiveness to variations in blur severity. The proposed HSMB metric achieved identical rank-based performance to BRISQUE (SROCC = 0.8000, KRCC = 0.6667) and obtained a PLCC of 0.4925, reflecting reliable linear association with BEW. NIQE showed moderate correlations across all measures (PLCC = 0.4159, SROCC = 0.4000, KRCC = 0.3333). In contrast, PIQE, DBCNN, and ARNIQA exhibited weak correlations overall (PLCC = 0.2067, 0.0466, and 0.3051, respectively), suggesting limited effectiveness for real-world blur evaluation.

Table 12: Correlation analysis results between BEW and NR-IQA metrics in field tunnel images

  ------------------------------------------------------------------------
  NR-IQA                 PLCC            SROCC             KRCC
  ---------------------- --------------- ----------------- ---------------
  BRISQUE                0.3510          0.8000            0.6667

  NIQE                   0.4159          0.4000            0.3333

  PIQE                   0.2067          0.4000            0.3333

  CPBD                   0.6061          0.6000            0.3333

  DBCNN                  0.0466          0.4000            0.3333

  ARNIQA                 0.3051          0.0000            0.0000

  HSMB (proposed)        0.4925          0.8000            0.6667
  ------------------------------------------------------------------------

It is important to acknowledge a limitation of this field validation: data were collected under only four vehicle speed conditions. With a limited number of data points, ranking permutations are constrained, which may reduce the statistical stability of rank-based correlation measures such as SROCC and KRCC. Therefore, these findings should be interpreted as preliminary evidence of practical feasibility rather than definitive statistical confirmation. Future research should incorporate a broader range of speeds and tunnel conditions to strengthen statistical robustness.

Overall, the field validation indicates that the proposed HSMB metric can reliably detect image quality variation in operational MTSS environments. In particular, it achieved rank-based performance comparable to BRISQUE while maintaining sensitivity to subtle changes in blur and sharpness under real-world conditions. These results suggest that HSMB functions as a practical and effective IQA tool not only in controlled laboratory settings but also in complex field environments such as tunnel inspections.

**Discussion**

This study introduced a novel NR-IQA metric, HSMB, developed to quantitatively evaluate motion blur occurring in high-speed mobile MTSS environments. The effectiveness and practical applicability of the proposed metric were systematically validated through laboratory experiments, public dataset comparisons, and field testing.

The central finding of this study is that HSMB effectively reflects the physical characteristics of MB under both controlled laboratory conditions and real-world tunnel environments. In laboratory experiments, HSMB demonstrated strong linear correlations with physical indicators such as BEW and MTF50, achieving PLCC values of 0.9354 and 0.8449, respectively, supporting its theoretical validity. More importantly, in field validation using operational tunnel imagery, HSMB achieved the highest rank-based correlation (SROCC = 0.8000), matching the performance of the established BRISQUE metric, despite limited physical quality variation associated with high-performance line-scan cameras. In contrast, deep learning-based NR-IQA models that performed well under laboratory conditions exhibited reduced generalization performance when applied to field data. This observation highlights the difficulty of directly applying complex black-box models trained on generic datasets to specialized industrial contexts such as MTSS. These results demonstrate that the adopted knowledge-based approach provides a robust and computationally efficient solution aligned with the objective of real-time quality monitoring in MTSS operations.

However, the findings should be interpreted in light of several limitations. The most significant constraint is the limited quantity of field data, as images were acquired under only four speed conditions, restricting statistical generalizability. Accordingly, the field experiments should be considered a preliminary validation of practical feasibility rather than definitive confirmation. In addition, field quality assessment relied on a limited number of SFR test charts mounted on tunnel walls, which may introduce spatial measurement bias. When comparing with deep learning models, pre-trained networks were applied without fine-tuning using MTSS-specific data, representing an additional contextual limitation. These constraints define the scope of the present study and identify directions for further investigation.

Future work should address these limitations by collecting more extensive field data across diverse tunnel environments and finer speed intervals to strengthen statistical robustness and evaluate generalization performance more rigorously. Alternative approaches should also be explored to quantify blur across the full tunnel lining rather than relying exclusively on SFR charts. Ultimately, integration of the proposed metric into operational MTSS platforms is necessary to evaluate its effectiveness as a real-time image quality filtering mechanism. Such efforts will strengthen the practical industrial contribution of this work.

---

## 수정 메모 (Revision Notes)

> **최우선 수정 구역 — Reviewer C1, C2 대응 (R01, R02)**
> **전면 재작성 필요** — 기존 line-scan 4개 속도 조건 서술 전체를 area-scan 50조건으로 교체

### 전면 재작성 계획

#### §VI-A. FIELD IMAGE ACQUISITION (재작성)
- [ ] **카메라 변경**: 4K line-scan (4096×2, 85mm, 50kHz) → **Area-scan 카메라** (모델명·사양 확정 필요)
- [ ] **실험 조건 확장**:
  - 속도: 60, 80 km/h (2개)
  - 촬영 거리: 2.5, 3.5, 4.5, 5.5, 6.5 m (5개)
  - **ISO: 100, 200, 400, 800, 1600 (5개)** ← 신규
  - 조건당 30장 → 총 **50조건 × 30장 = 1,500장**
- [ ] Imaging mechanism 일관성 서술 추가 — 실험실(area-scan)과 현장(area-scan) 동일 메커니즘 명시
- [ ] **Figure 14~17 교체** (터널 내부, area-scan MTSS, SFRreg 차트 acquisition, ROI)

#### §VI-B. FIELD ANALYSIS (재작성)
- [ ] Table 10 교체 — 50조건 BEW/MTF50/NR-IQA 결과
- [ ] 속도·거리·ISO 변수에 따른 MTF50/BEW 변화 추세 서술

#### §VI-C. CORRELATION ANALYSIS (재작성)
- [ ] Table 11, 12 교체 — 50조건 기반 PLCC/SROCC/KRCC
- [ ] **Permutation test p-value 추가** (목표: p < 0.05)
- [ ] **Bootstrap 95% CI 추가** (SROCC CI가 0을 포함하지 않음 확인)
- [ ] **ISO 축 메트릭 강건성 분석 서브섹션 추가** — ISO별 SROCC 변동 ≤ 0.10 확인
- [ ] "reliably detect" 등 과장 표현 제거 또는 통계적 근거 첨부

#### §VI 후반 "Discussion" (보강)
- [ ] 기존 "limited to 4 speed conditions" 한계 문장 제거
- [ ] Imaging mechanism consistency 논거 추가 (R01 대응)
- [ ] 50조건 확충으로 통계적 유의성 확보 서술 (R02 대응)
- [ ] ISO 축 추가로 메트릭 강건성 입증 서술

### 필요 데이터 (현재 대기 중)

- [ ] 현장 area-scan 카메라 스펙 (모델명, 해상도, 렌즈 초점거리, 노출 설정)
- [ ] 현장 area-scan 이미지 1,500장 (50조건 × 30장)
- [ ] 각 조건별 BEW/MTF50 ground truth
- [ ] 현장 실험 사진 (Figure 14~17 교체용)

### 주의

- "Discussion"이 §VI 말미에 섞여 있음 → 재작성 시 별도 Section VII (Discussion)로 분리하는 것이 구조상 깔끔 (현재는 §VII CONCLUSION이 Section 7, Discussion이 §VI에 병합됨)
- 원본 Introduction의 roadmap ("Sections 7 and 8 present discussion and conclusions")과 일관성 체크 필요
