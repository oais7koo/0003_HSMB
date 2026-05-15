# Section I — INTRODUCTION

> **Source**: `paper/original/Revision_0224.docx`
> **Revision date**: 2026-02-24
> **Mapping**: `full_manuscript.md` lines 17–28
> **Status**: **재작성 초안 v02 (2026-04-22)** — 원본은 하단 "## 원본 (참조용)" 섹션에 보존

---

## 재작성 초안 v02 (2026-04-22)

> 수정 포인트 3건:
> - **Para 3**: area-scan imaging mechanism consistency 명시 (R01 대응 예고) + 실내 4K / 현장 8K / 공통 0.3 mm/px GSD 구체 사양
> - **Para 4**: downstream benefit (CNN crack detection + F1 개선) 언급 추가 (R03 대응 예고)
> - **Para 5 (roadmap)**: 9-섹션 구조 반영 (v05 구조 개편)

### I. INTRODUCTION

Structural health monitoring (SHM) technologies are increasingly important for ensuring the safety and longevity of critical infrastructure such as tunnels and bridges. Advances in computer vision and deep learning have improved automation and efficiency in inspection processes, addressing limitations of traditional contact-based methods \[1-8\]. The Mobile Tunnel Scanning System (MTSS), which uses high-resolution cameras mounted on moving vehicles to detect defects such as cracks on tunnel lining surfaces, has emerged as a promising solution \[9,10\]. However, MTSS performance is significantly constrained by motion blur (MB), an unavoidable artifact caused by high-speed travel. The resulting image degradation reduces the reliability of convolutional neural network (CNN)-based defect detection algorithms, posing a major challenge to automated inspection systems \[11-16\].

Various post-processing techniques, including image deblurring, have been explored to address MB \[17,18\]. However, effective development and evaluation of these methods require benchmark datasets that reflect real-world distortions. Public datasets such as Need for Speed \[19\], DeBlurNet \[20\], GOPRO \[21\], Realistic and Diverse Scenes \[22\], Human-aware Image Deblurring \[23\], and the Real-World Blur Dataset \[24\] typically generate blur through artificial frame averaging from high-speed videos \[25\]. This synthetic approach differs from real-world imaging, where light is continuously recorded during sensor exposure. Consequently, these datasets do not capture the distinct MB characteristics of MTSS environments, in which exposure settings and high-speed translational motion interact. Moreover, the lack of reliable real-time image quality criteria limits the ability to filter degraded data or assess deblurring performance in practice. In such scenarios, where reference images are unavailable, no-reference image quality assessment (NR-IQA) is essential \[26,27\].

This study proposes an integrated framework to physically model and quantitatively evaluate MB in high-speed environments. We developed a High-Speed Translational Motion Panel (HTMP) equipped with a **4K-resolution area-scan CMOS camera** to simulate MTSS operating conditions in a controlled laboratory setting at speeds up to 110 km/h, and constructed a high-speed motion blur dataset under varying speeds, shutter speeds, and lighting conditions. The subsequent field validation is performed with an **8K-resolution area-scan camera**; although the two sensors differ in resolution, both acquisitions share the **same two-dimensional simultaneous-exposure blur formation mechanism** and are operated at a **matched ground sampling distance of 0.3 mm/pixel**, so that the laboratory and field experiments are directly comparable in blur geometry and metric calibration. Instead of relying on subjective measures such as mean opinion score (MOS), we adopted BEW, derived from modulation transfer function (MTF), as an objective physical ground-truth indicator of MB.

To enable real-time deployment in systems such as MTSS, we developed and validated a computationally efficient NR-IQA metric, the HSMB metric, designed specifically for high-speed MB images. We evaluated its generalization performance using public datasets and further verified its applicability with field images acquired from an operational MTSS system. **Building on these physical validations, we additionally quantify the downstream benefit of HSMB-based pre-filtering by applying a CNN-based crack detector to the field dataset and reporting the F1-score improvement as a function of the HSMB filtering threshold, thereby linking the proposed image-quality metric to concrete inspection outcomes.**

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 describes the HTMP design and HSMB dataset construction, including the directional (H/V) analysis of BEW and MTF50. Section 4 presents the HSMB metric algorithm, its parameter selection and theoretical basis, and an ablation study. Section 5 reports experimental results on the laboratory HSMB dataset and public IQA databases. Section 6 provides factorial field validation using an area-scan MTSS, including a complex-blur stress test. Section 7 evaluates the downstream impact on CNN-based crack detection and HSMB-based pre-filtering. Sections 8 and 9 present discussion and conclusions.

---

## 원본 (참조용)

> 아래는 투고 원본(Revision_0224.docx) 내용. 재작성 초안 검증용으로 보존.

I.  **INTRODUCTION**

Structural health monitoring (SHM) technologies are increasingly important for ensuring the safety and longevity of critical infrastructure such as tunnels and bridges. Advances in computer vision and deep learning have improved automation and efficiency in inspection processes, addressing limitations of traditional contact-based methods \[1-8\]. The Mobile Tunnel Scanning System (MTSS), which uses high-resolution cameras mounted on moving vehicles to detect defects such as cracks on tunnel lining surfaces, has emerged as a promising solution \[9,10\]. However, MTSS performance is significantly constrained by motion blur (MB), an unavoidable artifact caused by high-speed travel. The resulting image degradation reduces the reliability of convolutional neural network (CNN)-based defect detection algorithms, posing a major challenge to automated inspection systems \[11-16\].

Various post-processing techniques, including image deblurring, have been explored to address MB \[17,18\]. However, effective development and evaluation of these methods require benchmark datasets that reflect real-world distortions. Public datasets such as Need for Speed \[19\], DeBlurNet \[20\], GOPRO \[21\], Realistic and Diverse Scenes \[22\], Human-aware Image Deblurring \[23\], and the Real-World Blur Dataset \[24\] typically generate blur through artificial frame averaging from high-speed videos \[25\]. This synthetic approach differs from real-world imaging, where light is continuously recorded during sensor exposure. Consequently, these datasets do not capture the distinct MB characteristics of MTSS environments, in which exposure settings and high-speed translational motion interact. Moreover, the lack of reliable real-time image quality criteria limits the ability to filter degraded data or assess deblurring performance in practice. In such scenarios, where reference images are unavailable, no-reference image quality assessment (NR-IQA) is essential \[26,27\].

This study proposes an integrated framework to physically model and quantitatively evaluate MB in high-speed environments. We developed a High-Speed Translational Motion Panel (HTMP) to simulate MTSS operating conditions in a controlled laboratory setting at speeds up to 110 km/h and constructed a high-speed motion blur dataset under varying speeds, shutter speeds, and lighting conditions. Instead of relying on subjective measures such as mean opinion score (MOS), we adopted BEW, derived from modulation transfer function (MTF), as an objective physical ground-truth indicator of MB.

To enable real-time deployment in systems such as MTSS, we developed and validated a computationally efficient NR-IQA metric, the HSMB metric, designed specifically for high-speed MB images. We evaluated its generalization performance using public datasets and further verified its applicability with field images acquired from an operational MTSS system.

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 describes the HTMP design and HSMB dataset construction. Section 4 presents the HSMB metric algorithm. Section 5 reports experimental results. Section 6 provides field validation using MTSS. Sections 7 and 8 present discussion and conclusions.

---

> **한글 버전**: [ko/01_introduction.md](ko/01_introduction.md)

## 수정 메모 (Revision Notes)

> Reviewer 코멘트 직접 관련 없음 (주로 Section 6에 집중). 단, Section 구조 안내문은 수정 후 섹션 번호/내용 반영 필요.

- [x] 마지막 paragraph의 Section roadmap — 9-섹션 구조 반영 (2026-04-22)
- [x] Introduction 말미에 downstream task 언급 추가 — Para 4 끝에 CNN crack detection + F1 개선 문장 (R03, 2026-04-22)
- [x] Area-scan imaging mechanism consistency 명시 — Para 3에 실내 4K / 현장 8K / 공통 0.3 mm/px GSD 추가 (R01, 2026-04-22)
- [x] 한글 버전(ko/01_introduction.md) 동일 수정 반영 (2026-04-22)
