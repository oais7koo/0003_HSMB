# Frontmatter — Title, Authors, Abstract, Keywords

> **Source**: `paper/original/Revision_0224.docx`
> **Revision date**: 2026-02-24
> **Mapping**: `full_manuscript.md` lines 1–16
> **Status**: 원본 (수정 대기)

---

**No-Reference Image Quality Assessment for High-Speed Motion Blur Database in Tunnel Inspection**

**Chulhee Lee^1^,** **Donggyou Kim^1\*^,** **Dongku Kim^1^, and** **Junbeom** **An^1^**

^1^Department of Geotechnical Engineering Research, Korea Institute of Civil Engineering and Building Technology (KICT), Gyeonggi-Do, 10223, Republic of Korea

\*Corresponding author: Donggyou Kim (e-mail: dgkim2004@kict.re.kr).

This work was supported in part by the Korea Agency for Infrastructure Technology Advancement under Grant RS-2022-00142566.

**ABSTRACT**

Mobile Tunnel Scanning System (MTSS) enhances the efficiency of structural health monitoring. However, motion blur (MB) caused by high-speed movement remains a major technical challenge that reduces the reliability of automated defect detection algorithms. We propose a framework to quantitatively evaluate high-speed motion blur and manage image quality in real time. A custom-built High-Speed Translational Motion Panel (HTMP) was developed to simulate MTSS operating conditions at speeds up to 110 km/h and to construct a High-Speed Motion Blur (HSMB) benchmark dataset. Based on this dataset, we introduce a no-reference image quality assessment (NR-IQA) metric, the HSMB metric, which is computationally efficient and interpretable. Performance was validated through correlation analysis with blurred edge width (BEW) and modulation transfer function at 50% contrast (MTF50). The HSMB metric achieved the highest linear correlation with BEW in laboratory settings (Pearson linear correlation coefficient \[PLCC\] = 0.9354) and strong rank-order correlation in real-world tunnel tests (Spearman rank-order correlation coefficient \[SROCC\] = 0.8000), comparable to state-of-the-art metrics. These results confirm the robustness and applicability of the method under complex conditions. The HSMB metric enables real-time filtering of low-quality motion-blurred images, improving the reliability of automated structural health evaluations.

**KEYWORDS:** High-Speed Motion Blur (HSMB) Metric, Mobile Tunnel Scanning System (MTSS), No-Reference Image Quality Assessment (NR-IQA), Motion Blur (MB), Modulation Transfer Function (MTF)

---

> **한글 버전**: [ko/00_frontmatter.md](ko/00_frontmatter.md)

## 수정 메모 (Revision Notes)

- [ ] Abstract — 현장 검증 결과 수치 업데이트 필요 (Reviewer C1, C2 반영)
- [ ] Abstract — CNN crack detection downstream 결과 언급 추가 (Reviewer C3)
- [ ] Abstract — 현장 factorial 50조건 + 방향성(H/V) 분석 + complex-blur stress test 한 문장 추가 (Section VI 발견 연결)
- [ ] Keywords — 필요 시 "Ablation Study", "ISO Robustness", "Anisotropic Motion Blur" 키워드 검토
