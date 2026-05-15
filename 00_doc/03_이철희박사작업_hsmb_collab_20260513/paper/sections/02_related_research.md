# Section II — RELATED RESEARCH

> **Source**: `paper/original/Revision_0224.docx`
> **Revision date**: 2026-02-24
> **Mapping**: `full_manuscript.md` lines 29–61
> **Status**: 원본 (수정 대기) — §II-C 파라미터 이론 근거 문단은 §IV-D로 이동됨 (2026-04-22)

---

II. **RELATED RESEARCH**

<!-- -->

A.  ***FULL-REFERENCE IMAGE QUALITY ASSESSMENT (FR-IQA)***

In IQA, mean squared error (MSE) was historically widely used to evaluate image restoration performance. However, it has been criticized as an objective metric because it does not adequately reflect human perceptual quality, as different images can share the same MSE value yet be perceived differently \[28\]. To overcome this limitation, peak signal-to-noise ratio (PSNR) and structural similarity index metric (SSIM) \[29\] were introduced and have become two of the most widely adopted metrics in image deblurring research.

PSNR measures similarity between original and restored images by calculating the ratio of maximum signal power to noise power based on MSE. It is primarily used to assess degradation caused by noise \[30\] and is more sensitive to noise reduction and Gaussian blur than SSIM \[31\]. In contrast, SSIM evaluates image similarity by comparing luminance, contrast, and structural components. It is particularly responsive to variations in brightness and contrast and has been shown to be more sensitive than PSNR to degradation caused by JPEG and JPEG2000 compression artifacts \[32\]. Because PSNR and SSIM respond to different distortion types, they are often used together.

Several FR-IQA methods have been developed based on SSIM, including multi-scale SSIM (MS-SSIM) \[33\] and complex wavelet-based SSIM (CW-SSIM) \[34\]. MS-SSIM is widely applied in display technology but is not specifically optimized for MB assessment. CW-SSIM improves structural similarity evaluation in blurred images by reducing sensitivity to small pixel shifts and rotations; however, it is not directly designed to quantify MB. To address this limitation, Abdullah-Al-Mamun et al. \[35\] proposed the blur level (BL) metric, which captures blur induced by pixel shifts and rotations, factors not fully addressed by CW-SSIM. Although BL demonstrates improved performance over SSIM and PSNR in representing MB and sharpness, especially in low-light or low-texture images, it does not provide directional information about blur.

A fundamental limitation of FR-IQA methods is their reliance on undistorted reference images. In tunnel inspection scenarios involving MTSS, high-speed movement prevents acquisition of clear reference images, limiting the feasibility of physically grounded blur evaluation.

B.  ***REDUCED-REFERENCE IMAGE QUALITY ASSESSMENT (RR-IQA)***

The MTF is widely used to assess image sharpness in vision-based camera systems \[36\]. It quantifies the frequency-domain response of imaging systems, including microscopy, radiography, and remote sensing applications \[37-40\], and is defined as the Fourier transform of the point spread function (PSF), which characterizes blur. Therefore, spatial resolution can be evaluated through the high-frequency behavior of the MTF \[41\].

Several studies have experimentally examined MB by analyzing variations in MTF. Dinh et al. \[36\] developed an indoor rotational testing device to investigate MB induced by rotational motion and demonstrated that longer exposure times lead to flatter PSF slopes and reduced MTF values. Luo et al. \[42\] reported similar findings by recording video with a mobile phone moving linearly at 1 m/s, observing PSF broadening and MTF reduction as speed increased.

However, MTF measurement requires specialized test charts and does not readily capture directional MB, which limits its applicability in deep learning environments that rely on natural images or publicly available datasets \[35\]. This limitation becomes more pronounced in high-speed translational motion environments such as MTSS, where conventional MTF-based methods struggle to represent real MB characteristics. To address this challenge, a tunnel-simulated indoor experimental environment is required to enable controlled acquisition of MB image data by adjusting parameters such as camera motion, exposure settings, and illumination, thereby allowing accurate capture of PSF-related information.

C.  ***NO-REFERENCE IMAGE QUALITY ASSESSMENT (NR-IQA)***

NR-IQA methods estimate the degree of image degradation by analyzing distorted images without requiring a reference image, making them practical and efficient for real-world applications \[26,42\]. These approaches are generally categorized into spatial-domain and spectral-domain methods. Spatial-domain techniques use gradient and edge information for rapid evaluation but are often sensitive to noise \[27\]. In contrast, spectral-domain methods analyze frequency characteristics to assess distortions such as MB, although they are typically computationally intensive \[43\].

Recently, deep learning-based approaches have become prominent in NR-IQA research. Architectures such as Swin Transformers demonstrate high accuracy by capturing global image features effectively \[44,45,46\]. In addition, meta-learning and few-shot learning strategies have improved performance by reducing reliance on large-scale labeled datasets \[47,48\].

Despite the strong performance of deep learning-based NR-IQA methods, this study adopts a knowledge-based approach to prioritize applicability in MTSS field environments. State-of-the-art models such as the Swin Transformer require substantial computational resources, making real-time processing challenging in MTSS systems that generate large volumes of high-speed images. Furthermore, deep learning models depend on large labeled datasets tailored to specific MB characteristics, which are currently unavailable for MTSS. These models also operate as \"black boxes,\" limiting interpretability of quality score derivation. In contrast, knowledge-based methods provide clearer interpretability by directly linking measurable outcomes to physical phenomena such as edge blurring. This transparency strengthens both reliability and explanatory value. Accordingly, this study develops a lightweight algorithm that operates efficiently under constrained computational resources while accurately characterizing specific distortion types.

To evaluate NR-IQA algorithm performance, several standard image databases are commonly used, including the Laboratory for Image and Video Engineering (LIVE) \[49\], Categorical Subjective Image Quality (CSIQ) \[50\], Tampere Image Database 2008 (TID2008) \[51\], Tampere Image Database 2013 (TID2013) \[52\], the Blurred Image Dataset (BID) \[53\], and the University of Helsinki CID2013 \[54\]. These databases provide subjective quality scores obtained under standardized conditions. Image quality is expressed using MOS or differential mean opinion score (DMOS). Performance is typically assessed by analyzing correlations with MOS using metrics such as Pearson linear correlation coefficient (PLCC), Spearman rank-order correlation coefficient (SROCC), Kendall rank-order correlation coefficient (KRCC), and root MSE (RMSE) \[55\].

However, the NR-IQA proposed in this study is specifically designed to evaluate motion-blurred images in MTSS environments, which makes validation using conventional MOS-based methods challenging. Existing public datasets lack physical information, such as PSF, and do not adequately represent the non-uniform MB and camera exposure conditions characteristic of MTSS environments. To address this limitation, we propose a validation framework based on the HSMB dataset, constructed to simulate MTSS conditions, and evaluate correlations with objective MTF-based ground-truth values. This approach improves the reliability of MB assessment in real-world applications.

D.  ***MTSS IMAGING AND DOWNSTREAM DEFECT DETECTION***

Automated tunnel inspection has progressively shifted from discrete hand-held or cart-based surveys toward continuously moving camera platforms. Early MTSS installations commonly relied on line-scan cameras mounted on trolleys or vehicles \[69\], exploiting the one-dimensional sensor geometry and strobed illumination to produce seamless longitudinal mosaics of the lining surface. Line-scan acquisition, however, accumulates blur in a fundamentally different manner from two-dimensional sensors: each scan line is exposed sequentially, so inter-line registration errors and along-track smearing coexist and depend non-linearly on both vehicle velocity and line-rate synchronization. More recent MTSS deployments adopt high-resolution area-scan (global-shutter) cameras paired with synchronized strobe lighting \[9,10,16\], in which the entire field of view is recorded within a single short exposure. Under area-scan acquisition, translational motion blur reduces to a spatially uniform one-dimensional PSF whose length is determined by the product of travel speed and exposure time. This regime is precisely the one targeted by the HSMB dataset constructed in this study and by the area-scan field validation reported in Section VI, and it is the regime in which a physics-grounded NR-IQA metric can be directly calibrated against MTF-derived ground truth.

Convolutional neural networks (CNNs) have become the dominant framework for pixel-level and patch-level crack detection on concrete surfaces \[7,8\], and analogous CNN-based pipelines have been widely applied to tunnel-lining defect recognition \[10-12,14,16\]. The sensitivity of these detectors to acquisition-induced degradations has been studied predominantly for illumination inconsistency and compression artifacts, whereas the impact of real motion blur remains comparatively underexplored. Liu et al. \[15\] explicitly addressed blur in the context of unmanned-aerial-vehicle concrete crack imaging and proposed a deblurring-based enhancement network, but their analysis focused on restoration quality rather than on a principled image-quality gate placed upstream of the detector. To the best of our knowledge, no prior study reports a quantitative coupling between a physically grounded NR-IQA metric and CNN crack-detection performance under MTSS-relevant translational blur. The present work closes this gap: Section VII applies a ResNet-based crack detector to the 50-condition area-scan field dataset of Section VI and quantifies how HSMB-based pre-filtering modifies detection F1 as a function of threshold, thereby linking the proposed image-quality metric to a concrete downstream inspection outcome.

E.  ***EXISTING MOTION-BLUR DATASETS AND THEIR IQA SUITABILITY***

Several public datasets are widely used in the motion-blur and IQA literatures; each was constructed for a specific evaluation objective and presents the following scope and ground-truth characteristics when considered for MTSS-relevant IQA validation. The **GoPro dataset** \[21\] supplies blurry/sharp image pairs synthesised by averaging 7–13 consecutive frames captured at 240 fps with a handheld GoPro Hero camera; the dataset addresses image-deblurring evaluation, its motion source combines handheld camera shake with general vehicle motion rather than controlled high-speed translation, and its ground truth is a synthetically generated sharp reference in place of an objective physical image-quality measurement. The **Need for Speed (NfS) benchmark** \[19\] consists of 100 240-fps video sequences captured for object tracking; its motion blur arises from handheld camera dynamics across diverse scenes, and its ground-truth annotation is limited to per-frame bounding boxes, which do not directly support IQA metric validation. General-purpose IQA databases (TID2013 \[51\], CID2013 \[54\], MMP-2K \[68\]) provide perceptual MOS scores but do not include objective physical ground truth (BEW or MTF50), and contain little controlled high-speed translational motion blur. Table 1 summarises these scope and ground-truth differences. To complement the existing datasets and enable direct objective IQA validation under MTSS-relevant motion, a dedicated HSMB dataset is constructed in Section III-C, providing (i) controlled translational motion at calibrated speeds from 0 to 110 km/h, (ii) objective BEW and MTF50 ground truth, (iii) a 40-condition factorial design (5 panel speeds × 4 shutter speeds × 2 illuminance levels) supporting analysis-of-variance and statistical testing, and (iv) a tunnel-inspection acquisition geometry that mirrors the deployment conditions of the proposed metric.

Table 1: Comparison of motion-blur and IQA datasets relevant to MTSS evaluation.

| Dataset | Motion source | Application target | Ground-truth type | High-speed translational | Objective IQA-grade GT |
|---------|---------------|--------------------|-------------------|:------------------------:|:----------------------:|
| GoPro \[21\] | Handheld + general vehicle | Image deblurring | Synthetic sharp reference | Limited | No |
| Need for Speed \[19\] | Handheld | Object tracking | Bounding-box annotation | No | No |
| TID2013 \[51\] | Synthetic distortions | General-purpose IQA | MOS (subjective) | No | Subjective only |
| CID2013 \[54\] | Mixed (camera + display) | General-purpose IQA | MOS (subjective) | No | Subjective only |
| MMP-2K \[68\] | Macro defocus blur | Real-world IQA | MOS (subjective) | No | Subjective only |
| **HSMB (this work)** | **HTMP translational (0–110 km/h)** | **MTSS pre-filter + motion-blur IQA** | **BEW + MTF50** | **Yes** | **Yes (objective)** |

> **한글 버전**: [ko/02_related_research.md](ko/02_related_research.md)

## 수정 메모 (Revision Notes)

> Reviewer 코멘트 직접 관련 낮음. Related Research는 주로 유지, 필요 시 최신 문헌 보강.

### 재배치 기록 (2026-04-22)

- [x] **§II-C 말미에 추가되었던 HSMB 파라미터 이론 근거 문단은 §IV-D로 이동됨** — R04 대응의 정식 자리는 Section IV-D (Parameter Selection and Theoretical Basis). §II는 선행 기술 리뷰 역할에 집중
- [x] 신규 참조 [75] Sharifi & Leon-Garcia (1995, GGD), [76] Geusebroek & Smeulders (2005, Weibull)는 **99_references.md에 유지** — §IV-D에서 인용 예정
- [x] 본 파일 v02 블록 제거 및 원본 구조 복구 완료 (영문·한글, 2026-04-22)

### 신규 소절 추가 (2026-04-23)

- [x] **§II-D *MTSS IMAGING AND DOWNSTREAM DEFECT DETECTION*** 신규 추가 — 2문단 구성
  - 문단 1: line-scan [69] vs area-scan [9,10,16] MTSS 이미징 메커니즘 대비 → **R01 scholarly anchor**
  - 문단 2: CNN 기반 균열 검출 [7,8,10-12,14,16] + Liu et al. [15] (MB + UAV crack)의 한계 지적 → gap statement → §VII로 연결 → **R03 scholarly anchor**
- [x] 기존 [7-16, 69] 재사용만 사용, 신규 참조 추가 없음 — 지면 부담 최소화
- [x] 기존 §II-A/B/C FR→RR→NR 흐름 보존, §II-D는 "IQA 기법론" → "응용 맥락" 자연 확장

### 기타 (보류)

- [ ] Deep learning NR-IQA 최신 레퍼런스 검토 (2025 이후 논문 추가 여부) — 보류
- [x] area-scan vs line-scan 블러 메커니즘 차이 관련 선행연구 추가 여부 (R01 맥락) — **§II-D 문단 1에 반영 완료 (2026-04-23)**
