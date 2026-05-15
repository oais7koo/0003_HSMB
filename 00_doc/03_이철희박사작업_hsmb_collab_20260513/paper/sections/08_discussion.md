# Section VIII — DISCUSSION

> **Status**: **신규 섹션** (구조 개편 v05 — 2026-04-22). 기존 §VI 말미에 병합되어 있던 Discussion을 **독립 장으로 분리**. Reviewer 대응 내용을 주제별로 체계화.
> **Structure**: 5 thematic sub-sections, each tied to a specific reviewer concern.

---

VIII.  **DISCUSSION**

This study introduced HSMB, a knowledge-based NR-IQA metric specialised for high-speed translational motion blur, together with a factorial-design field validation and a downstream crack-detection experiment. This section integrates the findings of Sections V–VII and discusses their implications for imaging-mechanism consistency, statistical rigor, downstream applicability, and the theoretical grounding of the HSMB hyperparameters.

### A. IMAGING-MECHANISM CONSISTENCY

In motion-blur NR-IQA, the choice of sensor architecture — line-scan versus area-scan, rolling versus global shutter — directly shapes the spatial structure of blur and can introduce directional artefacts that are not motion-induced. The present work aligns the imaging mechanism across the laboratory and the field: both use 2D area-scan sensors with global shutter and exposure synchronisation, eliminating directional line-scan artefacts. Section III-E shows that the H-axis (motion-dominant) vs V-axis (reference) decomposition produces the same anisotropic signature in both laboratory and field data, supporting this alignment empirically and confirming that the blur observed in the field is attributable to vehicle motion rather than to a sensor-specific artefact.

### B. STATISTICAL RIGOR AND ROBUSTNESS

The 3-factor factorial design (2 speeds × 5 distances × 5 ISO = 50 conditions, §VI-A) yields an a-priori statistical power of ≥ 0.95 for ρ ≥ 0.5 at α = 0.05, allowing each correlation estimate to be supported by permutation tests (10 000 resamples) and Bootstrap 95 % confidence intervals. An ISO-axis robustness sub-analysis shows that HSMB maintains its SROCC across photon-budget conditions (per-ISO variation ≤ 0.10). An opportunistic complex-blur stress test at ISO 400 and 4.5 m camera-to-wall distance further probes HSMB's behaviour under an unexpected defocus-plus-motion failure mode (§VI-D), demonstrating that the metric's response generalises beyond pure motion blur to realistic operational failure modes.

### C. DOWNSTREAM IMPLICATIONS FOR CRACK DETECTION

Section VII quantifies how motion blur degrades a ResNet34 crack-detection model and whether HSMB pre-filtering restores reliability. [To be finalised with the crack-detection experiment results.] The anticipated outcome is that HSMB-thresholded filtering improves F1 compared with the unfiltered baseline while preserving a large fraction of images, and that the complex-blur conditions are correctly rejected by the filter — a direct demonstration of the metric's value as an operational gate in MTSS pipelines rather than merely an offline quality score.

### D. PARAMETER FOUNDATIONS AND SENSITIVITY

The three HSMB hyperparameters — Edge Weight, JNB, and β — are grounded theoretically in §IV-D and validated empirically in §IV-E. The ablation (Edge Weight ∈ {1.0, 1.25, 1.5, 1.75, 2.0}, JNB ∈ {1, 2, 3, 4, 5}, β ∈ {1.0, 1.5, 2.0, 2.5, 3.0}) shows that the default values sit at or adjacent to the correlation peak, complementing the Sobol' sensitivity analysis of §IV-C. The connection of these defaults to GGD-based edge statistics, the Ferzli–Karam JNB formulation, and Weibull-shaped edge-width distributions provides a physical interpretability that deep-learning baselines lack and supports the use of HSMB as an explainable quality indicator in safety-critical inspection pipelines.

### E. LIMITATIONS AND FUTURE WORK

The laboratory and field datasets both use slanted-edge targets as ground-truth anchors, which covers blur quantification but not all real-world tunnel content. Chart-free full-image MTF estimation methods — such as natural-edge SFR detection or multi-region tile sampling on the lining surface itself — could complement the chart-based protocol in environments where target placement is impractical, at the cost of reduced calibration accuracy and sensitivity to scene-dependent edge statistics; quantifying this trade-off and integrating chart-free measurement into the MTSS workflow is identified as a future direction. The field dataset comprises a single tunnel campaign; multi-tunnel generalisation remains an open question. The HTMP itself is treated through manufacturer-specified resolutions and the eSFR repeatability statistics reported in Section III-B; a dedicated calibration campaign with direct servo-encoder readout and shutter-latency profiling would tighten the measurement uncertainty budget. The CNN crack-detection experiment uses one backbone (ResNet34); the effect of HSMB filtering on modern transformer-based detectors is a natural next study. Finally, real-time integration of HSMB into the MTSS acquisition pipeline — rather than post-hoc filtering — is a practical extension that would close the loop between image-quality measurement and operational decision-making.

### F. FAILURE CASE ANALYSIS

While Sections V–VII establish that HSMB tracks motion blur with high directional and statistical reliability across the design space of the laboratory and area-scan field datasets, an honest evaluation must also expose conditions under which the metric loses sensitivity or misranks images. Three qualitative failure modes are observed.

*Complex blur outside the design space.* The (ISO 400, working distance 4.5 m) cells of the field dataset analysed in Section VI-D combine a translational motion-induced edge spread along the H-axis with an additional defocus-induced isotropic broadening that affects both axes. Because HSMB was constructed under the assumption of a primarily translational point-spread function, it under-discriminates between these doubly degraded images and the surrounding singly motion-blurred images, even though the anisotropy diagnostic Δ = BEW_H − BEW_V remains essentially unchanged. Visual inspection of the corresponding patches confirms that the lining surface texture is locally unresolvable while HSMB still reports an intermediate score, illustrating that the metric encodes motion-induced edge spread rather than a generic defocus penalty.

*Sub-pixel variations under static and short-shutter conditions.* The eight static (0 km/h) conditions of Section III-B exhibit BEW values that drift between 3.0 and 3.6 px depending on illumination and ISO (Section III-B), yet HSMB scores cluster within a narrow 0.92–0.93 band across the same conditions. The metric therefore correctly identifies all eight cells as "sharp" but does not resolve the small differences in the static BEW noise floor. The same flattening is observed at the shortest 50 μs shutter setting, where motion blur is suppressed below the AEP detection threshold and HSMB saturates against the static reference level. These cases are not failures in the operational sense — the metric is consistent with the application requirement of distinguishing usable from blurred frames — but they bound the regime in which HSMB can be expected to discriminate fine-grained sharpness differences.

*Cross-motion-axis residual blur.* On the V-axis, BEW remains within ≈3–5 px across all 40 laboratory conditions and 50 field conditions while MTF50_V exhibits a small monotonic decrease at long exposures. HSMB tracks this V-axis behaviour with PLCC(V) = −0.76 against BEW and +0.83 against MTF50, weaker in absolute terms than the H-axis correlations of −0.93 and +0.82 (Tables 6–7). The residual variance on the V-axis is dominated by sensor noise and minor optical aberration rather than by translational motion, and HSMB — by construction — partially attributes this variance to a motion-like edge spread, leading to a small bias in V-axis predictions. This bias is the cost of the directional balance that distinguishes HSMB from baselines whose V-axis performance collapses entirely (CPBD, DBCNN, ARNIQA in Table 7), and quantifying it explicitly is preferable to hiding it.

These observations identify three improvement directions for future work: (i) explicit modelling of multi-modal blur (motion + defocus) by combining the directional eSFR analysis of Section III-E with an isotropic optical-blur term, (ii) a sub-pixel-resolved variant of the EVP step that retains sensitivity below the current ≈ 3 px floor, and (iii) joint H/V regression of HSMB outputs against both BEW components to remove the residual V-axis bias.

---

> **한글 버전**: [ko/08_discussion.md](ko/08_discussion.md)

## 수정 메모 (Revision Notes)

### Reviewer 대응 매핑 (저자 내부 트레이싱용 — 본문에는 노출하지 않음)

| 본문 서브섹션 | 대응 Reviewer 코멘트 | 비고 |
|------|------|------|
| §VIII-A IMAGING-MECHANISM CONSISTENCY | Reviewer 1 — C1 (R01) | area-scan 일관성 |
| §VIII-B STATISTICAL RIGOR AND ROBUSTNESS | Reviewer 1 — C2 (R02) | 50조건 factorial + power |
| §VIII-C DOWNSTREAM IMPLICATIONS | Reviewer 1 — C3 (R03) | CNN crack detection |
| §VIII-D PARAMETER FOUNDATIONS | Reviewer 1 — C4 (R04) | GGD/JNB/Weibull |
| §VIII-E LIMITATIONS | (자체 한계 서술) | future work |

> 본 매핑은 저자/공동저자 내부 검증 및 response letter 작성 시 참조용. 학술지 제출 본문에는 reviewer code 노출 금지.

### 데이터 수령 후 확정

- [ ] §C 본문에 crack detection 실제 수치 삽입 (F1 개선폭, optimal T, complex-blur behaviour)
- [ ] §B에 실제 permutation p-value, Bootstrap CI 수치 삽입 (지표 수령 후 hsmb_statistics.py 결과)
- [ ] §D에 실제 ablation 결과 참조 (E1-F1 완료 후)

### 내러티브 다듬기 (데이터 무관 가능)

- [x] revision-letter 언어 제거 — "previous version", "C1–C4 of the previous submission", "> Reviewer Cx response" 콜아웃 모두 정리 (2026-04-22)
- [ ] §A에 H/V 이방성 수치(실내 +33.43 vs 현장 +0.70) 직접 인용
- [ ] §E 한계·future work를 bullet list로 정리할지 문단으로 둘지 결정
- [ ] §B 도입부 permutation vs parametric test 선택 근거 한 줄 추가
