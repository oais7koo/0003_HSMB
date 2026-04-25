# Section V — EXPERIMENTAL RESULTS AND ANALYSIS

> **Source**: `paper/original/Revision_0224.docx`
> **Revision date**: 2026-02-24
> **Mapping**: `full_manuscript.md` lines 251–416
> **Status**: 원본 (수정 대기) — **서브섹션 추가 필요 (R03)**

---

V.  **EXPERIMENTAL RESULTS AND ANALYSIS**

This section quantitatively evaluates the performance of the proposed HSMB metric and compares it with existing IQA methods. First, its correlation with physical ground-truth measurements, BEW and MTF50, is analyzed using the custom-built HSMB dataset to demonstrate effectiveness under high-speed motion blur conditions. Second, the generalization capability of the proposed metric is assessed through comparison with state-of-the-art NR-IQA methods across multiple public IQA databases.

A.  ***RESULTS OF HSMB IMAGES CALCULATING MTF AND BEW***

To objectively characterize MB, Imatest® software was used to measure MTF50 and BEW at the center region of the eSFR ISO test chart. BEW is defined as the pixel width of the rising interval between 10% and 90% of the ESF and directly represents MB severity. MTF50 indicates the SFR of the imaging system and is widely applied to evaluate image sharpness.

Tables 4 and 5 show that under both lighting conditions, 15,000 lx and 40,000 lx, increasing panel velocity consistently results in higher BEW values and lower MTF50 values. For example, under 15,000 lx at 70 km/h with a shutter speed of 500 μs, BEW measured 38.28 pixels. When shutter speed was reduced to 50 μs, BEW decreased markedly to 5.32 pixels. At the same time, MTF50 increased from 0.0227 cy/px to 0.0955 cy/px, indicating improved sharpness. These findings confirm that BEW and MTF50 reliably represent the physical behavior of MB in high-speed environments. Accordingly, both metrics are adopted as ground-truth reference indicators for evaluating NR-IQA performance in subsequent analyses.

Table 4: Results of MB images depending on velocity of moving panel and shutter speeds at 15,000 lx illuminance

+---------------+---------------+--------+---------+---------+---------+---------+
| Shutter speed | RR-IQA        | 0 km/h | 10 km/h | 30 km/h | 50 km/h | 70 km/h |
+===============+===============+========+=========+=========+=========+=========+
| 500㎲         | BEW (pixels)  | 3.40   | 6.31    | 16.38   | 27.56   | 38.28   |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1566 | 0.0810  | 0.0375  | 0.0271  | 0.0227  |
+---------------+---------------+--------+---------+---------+---------+---------+
| 250㎲         | BEW (pixels)  | 3.61   | 4.68    | 8.78    | 13.86   | 18.99   |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1485 | 0.1118  | 0.0606  | 0.0423  | 0.0338  |
+---------------+---------------+--------+---------+---------+---------+---------+
| 100㎲         | BEW (pixels)  | 3.56   | 3.86    | 4.73    | 6.33    | 8.47    |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1505 | 0.1445  | 0.1069  | 0.0806  | 0.0626  |
+---------------+---------------+--------+---------+---------+---------+---------+
| 50㎲          | BEW (pixels)  | 3.37   | 3.66    | 3.99    | 4.52    | 5.32    |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1581 | 0.1524  | 0.1337  | 0.1140  | 0.0955  |
+---------------+---------------+--------+---------+---------+---------+---------+

Table 5: Results of MB images depending on velocity of moving panel and shutter speeds at 40,000 lx illuminance

+---------------+---------------+--------+---------+---------+---------+---------+
| Shutter speed | RR-IQA        | 0 km/h | 10 km/h | 30 km/h | 50 km/h | 70 km/h |
+===============+===============+========+=========+=========+=========+=========+
| 500㎲         | BEW (pixels)  | 3.23   | 6.07    | 15.18   | 25.19   | 35.37   |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1692 | 0.0853  | 0.0403  | 0.0295  | 0.0155  |
+---------------+---------------+--------+---------+---------+---------+---------+
| 250㎲         | BEW (pixels)  | 3.52   | 4.39    | 8.29    | 12.83   | 17.44   |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1634 | 0.1172  | 0.0583  | 0.0374  | 0.0277  |
+---------------+---------------+--------+---------+---------+---------+---------+
| 100㎲         | BEW (pixels)  | 3.49   | 3.61    | 4.76    | 6.47    | 8.37    |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1594 | 0.1456  | 0.1041  | 0.0743  | 0.0567  |
+---------------+---------------+--------+---------+---------+---------+---------+
| 50㎲          | BEW (pixels)  | 3.42   | 3.71    | 3.95    | 4.43    | 5.30    |
|               +---------------+--------+---------+---------+---------+---------+
|               | MTF50 (cy/px) | 0.1569 | 0.1432  | 0.1337  | 0.1135  | 0.0897  |
+---------------+---------------+--------+---------+---------+---------+---------+

B.  ***CORRELATION ANALYSIS USING HSMB IMAGES***

This section analyzes correlations between multiple IQA metrics and two physical ground-truth indicators of MB, BEW, and MTF50, using the combined dataset collected under 15,000 lx (Table IV) and 40,000 lx (Table V) lighting conditions. The evaluated metrics include PSNR, SSIM, BRISQUE, NIQE, PIQE, CPBD, Deep Bilinear Convolutional Neural Network (DBCNN) \[71\], leArning distoRtion maNifold for IQA (ARNIQA) \[72\], and the proposed HSMB metric. Correlation was assessed using three statistical measures: PLCC, SROCC, and KRCC, providing complementary perspectives on the relationship between each IQA metric and the ground-truth measures.

Analysis of the combined dataset (Tables 6 and 7) shows that the HSMB metric achieves the strongest linear correlation with BEW (PLCC = 0.9354), which directly reflects physical MB severity. This indicates that HSMB effectively captures blur characteristics produced by high-speed translational motion without requiring a learning process. In relation to MTF50, a sharpness indicator, HSMB also demonstrates strong performance (PLCC = 0.8449, SROCC = 0.8759), comparable to deep learning-based models. These findings suggest that an edge-based algorithm can maintain high consistency with physical sharpness measures without reliance on complex training.

Deep learning-based metrics such as DBCNN and ARNIQA also exhibit consistently high correlations with both BEW and MTF50. DBCNN achieves the highest correlation with MTF50 (PLCC = 0.9088, SROCC = 0.9280), demonstrating its ability to predict degradation in physical resolution represented by MTF, likely owing to large-scale training. However, these models require substantial computational resources and operate as black-box systems, which limits their suitability for real-time, reliability-critical environments such as MTSS. This comparison underscores the value of lightweight, interpretable, knowledge-based metrics such as the proposed HSMB method.

Traditional NR-IQA metrics, including BRISQUE, NIQE, PIQE, and CPBD, show comparatively weaker performance under HSMB conditions. Among them, CPBD achieves the strongest correlations, with PLCC values of 0.5631 (vs. BEW) and 0.7170 (vs. MTF50). In contrast, BRISQUE and NIQE, which are based on NSS, produce inconsistent results. This likely reflects the mismatch between NSS assumptions and the directional, high-speed characteristics of MB. These outcomes highlight the limitations of general-purpose NR-IQA metrics in specialized applications such as MTSS.

Full-reference IQA metrics display divergent behavior. SSIM, which evaluates structural similarity, shows minimal correlation with BEW and MTF50 under all conditions (PLCC \< 0.11 for the combined dataset). This may be explained by the fact that uniform MB does not substantially alter global structure, luminance, or contrast, reducing SSIM sensitivity to blur severity. In contrast, PSNR demonstrates moderately strong correlation with BEW (PLCC = 0.6038) and MTF50 (PLCC = 0.7481). These results suggest that motion blur-induced pixel smoothing affects MSE, allowing PSNR to indirectly reflect blur severity in certain cases.

Table 6: Correlation between BEW and IQA metrics on the combined MB dataset

  ---------------------------------------------------------------------
  IQA                          SROCC          PLCC         KRCC
  ---------------------------- -------------- ------------ ------------
  PSNR                         0.7515         0.6038       0.5683

  SSIM                         0.1197         0.0138       0.0738

  BRISQUE                      0.4618         0.5051       0.3525

  NIQE                         0.3078         0.0977       0.2825

  PIQE                         0.3862         0.4076       0.2459

  CPBD                         0.6931         0.5631       0.5001

  DBCNN                        **0.9244**     0.7349       **0.7911**

  ARNIQA                       0.8774         0.8317       0.746

  HSMB (proposed)              0.8855         **0.9354**   0.7419
  ---------------------------------------------------------------------

Table 7: Correlation between BEW and IQA metrics on the combined MB dataset

  ------------------------------------------------------------------------
  IQA                SROCC             PLCC              KRCC
  ------------------ ----------------- ----------------- -----------------
  PSNR               0.7747            0.7481            0.5929

  SSIM               0.1601            0.1018            0.1066

  BRISQUE            0.4736            0.4957            0.3525

  NIQE               0.339             0.3589            0.3072

  PIQE               0.3634            0.4298            0.2295

  CPBD               0.6747            0.717             0.4755

  DBCNN              **0.928**         **0.9088**        **0.7993**

  ARNIQA             0.8664            0.8644            0.7132

  HSMB (proposed)    0.8759            0.8449            0.7091
  ------------------------------------------------------------------------

C.  ***SCATTER PLOT ANALYSIS OF NR-IQA METRICS USING HSMB IMAGES***

Using the HSMB dataset acquired under high-speed imaging conditions, we evaluated the alignment of various NR-IQA metrics with the physical quality indicators BEW and MTF50. Scatter plots and regression lines were generated for each metric against BEW and MTF50 to visually assess sensitivity and predictive accuracy.

In Fig. 12, which illustrates the relationship with BEW, the proposed HSMB metric shows the most consistent and pronounced negative linear correlation. As HSMB values decrease, BEW values increase markedly, with data points closely distributed along the regression line. This relationship indicates that HSMB responds sensitively to physical blur severity and is well-suited for quantifying MB under high-speed conditions.

Traditional NR-IQA metrics such as BRISQUE, NIQE, and PIQE display general trends with increasing BEW; however, their scatter plots exhibit substantial variance and weak linearity, suggesting limited predictive reliability. NIQE and PIQE in particular show distributions that are largely uncorrelated with BEW, highlighting their limitations in HSMB scenarios. CPBD demonstrates partial linearity, especially within moderate BEW ranges, but exhibits instability and outliers at higher blur levels.

Among deep learning-based methods, DBCNN shows a clear negative correlation with BEW, although its predictive precision does not match that of HSMB. ARNIQA presents a weaker relationship with BEW, with widely dispersed data points that reduce predictive strength.

![](../media/media/image18.png){width="4.815972222222222in" height="8.625in"}

Figure 12: Scatter plots between various NR-IQA and deep learning-based metrics and BEW

Similar patterns appear in Fig. 13, which presents correlations with MTF50. HSMB demonstrates a strong positive linear relationship with MTF50, indicating that increases in image sharpness correspond to increases in HSMB values in a near-linear manner. This finding suggests that HSMB is responsive to both blur severity and sharpness variation. DBCNN also maintains a positive correlation with MTF50, though its sensitivity decreases in higher MTF50 regions.

Other metrics, including CPBD and PSNR, show partial correspondence with MTF50, but clustering around the regression line is less pronounced. BRISQUE and ARNIQA exhibit weak predictive trends. As expected, SSIM, a structure-based metric, shows an almost flat distribution relative to MTF50, reflecting its limited sensitivity to sharpness variation caused by MB.

Overall, these analyses demonstrate that HSMB achieves the strongest alignment with both BEW and MTF50, two independent physical image quality indicators. This supports its reliability and practical applicability as a motion blur-specific NR-IQA model, exceeding the performance of conventional metrics under high-speed conditions. Accordingly, the proposed HSMB metric shows strong potential for real-time deployment in image-based maintenance systems such as MTSS as an effective quality assessment tool.

![](../media/media/image19.png){width="4.729166666666667in" height="8.46875in"}Figure 13: Scatter plots between various NR-IQA and deep learning-based metrics and the MTF at 50% (MTF50).

D.  ***CORRELATION ANALYSIS USING PUBLIC IQA DATABASES***

To examine whether the proposed HSMB metric demonstrates meaningful performance beyond its primary focus on high-speed motion blur, a comparative evaluation was conducted using two synthetic distortion datasets, TID2013 \[51\] and CID2013 \[54\], and one real-world distortion dataset, MMP-2K \[68\]. As shown in Table 8, deep learning-based methods ARNIQA and DBCNN achieved the highest correlation performance across all coefficients on both TID2013 and CID2013. On CID2013, ARNIQA achieved SROCC = 0.7746 and PLCC = 0.7954, while DBCNN achieved SROCC = 0.8087 and PLCC = 0.8127, indicating strong consistency with human perceptual ratings. In contrast, the proposed HSMB metric exhibited comparatively low correlation on these datasets, with SROCC = 0.0913, PLCC = 0.2960, and KRCC = 0.0632 on TID2013. These findings indicate that HSMB is not intended for general-purpose distortion evaluation but is instead tailored to quantify edge diffusion resulting from high-speed translational MB.

In the MMP-2K dataset, which includes real-world distortions such as blur in macro photography, HSMB outperformed all traditional NR-IQA methods. HSMB achieved SROCC = 0.5052, PLCC = 0.5423, and KRCC = 0.3601, exceeding CPBD (SROCC = 0.4209, PLCC = 0.3841), BRISQUE (SROCC = 0.3395, PLCC = 0.3663), and NIQE (SROCC = 0.2810, PLCC = 0.2141). Although deep learning-based methods DBCNN (SROCC = 0.6781) and ARNIQA (SROCC = 0.5693) achieved the highest overall performance, HSMB demonstrated the strongest predictive capability among non-learning-based approaches. The consistent superiority of HSMB over traditional NR-IQA methods across all three correlation measures in the MMP-2K dataset suggests that the proposed metric effectively evaluates MB under real-world conditions.

Overall, while HSMB exhibits limited generalizability across diverse distortion types, it demonstrates strong specialization in MB assessment. This specialization reinforces the practical value of the proposed knowledge-based approach in MTSS environments.

Table 8: Comparison of SROCC, PLCC, and KRCC correlation coefficients for various NR-IQA metrics across 3 IQA datasets: TID2013, CID2013, and MMP-2K.

+-----------------+--------------------------------------+--------------------------------------+--------------------------------------+
| IQA             | TID 2013                             | CID 2013                             | MMP-2K                               |
|                 +------------+------------+------------+------------+------------+------------+------------+------------+------------+
|                 | SROCC      | PLCC       | KRCC       | SROCC      | PLCC       | KRCC       | SROCC      | PLCC       | KRCC       |
+=================+============+============+============+============+============+============+============+============+============+
| BRISQUE         | 0.4319     | 0.4565     | 0.3048     | 0.4951     | 0.5085     | 0.3425     | 0.3395     | 0.3663     | 0.2365     |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
| NIQE            | 0.277      | 0.2433     | 0.1844     | 0.5416     | 0.5549     | 0.3745     | 0.281      | 0.2141     | 0.1937     |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
| PIQE            | 0.3636     | 0.4615     | 0.5554     | 0.0448     | 0.1072     | 0.0394     | 0.2115     | 0.2611     | 0.1453     |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
| CPBD            | 0.1115     | 0.344      | 0.0684     | 0.2586     | 0.2462     | 0.188      | 0.4209     | 0.3841     | 0.2964     |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
| DBCNN           | 0.3855     | 0.5141     | 0.2692     | **0.8087** | **0.8127** | **0.6108** | **0.6781** | **0.7539** | **0.5018** |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
| ARNIQA          | **0.6009** | **0.6398** | **0.4271** | 0.7746     | 0.7954     | 0.5735     | 0.5693     | 0.7085     | 0.4116     |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
| HSMB (proposed) | 0.0913     | 0.296      | 0.0587     | 0.2306     | 0.2106     | 0.169      | 0.5052     | 0.5423     | 0.3586     |
+-----------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+

---

## 수정 메모 (Revision Notes)

> **핵심 수정 구역 — Reviewer C3 대응 (R03)**

### 신규 서브섹션 추가 예정

- [ ] **§V-E. IMPACT OF MOTION BLUR ON CRACK DETECTION** (신규)
  - ResNet34 기반 균열 검출 실험 설계
  - 블러 수준별 Precision/Recall/F1-score 측정 (최소 3개 블러 수준)
  - HSMB 필터링 threshold 적용 전/후 F1-score 비교
  - HSMB score vs Detection F1-score scatter plot
  - 결론: HSMB threshold 기반 pre-filtering이 defect detection 신뢰도 개선 정량 입증

### 기타 경미 수정

- [ ] 도입부에 "downstream task (crack detection)" 언급 추가하여 §V-E로 이어지도록 설계
- [ ] 최종 overall 서술에 HSMB의 pre-filtering 유용성 언급 추가 (R03 연결)
