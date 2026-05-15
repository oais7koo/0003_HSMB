# Section IX — CONCLUSION

> **Source**: `paper/original/Revision_0224.docx`
> **Revision date**: 2026-02-24
> **Mapping**: `full_manuscript.md` lines 608–630
> **Renumbering**: 원본 §VII → 개편안 **§IX** (Discussion/CNN 섹션 삽입 반영, 2026-04-22)
> **Status**: 원본 (수정 대기) — **결과 수치 업데이트 필요**

---

IX. **CONCLUSION**

This study introduced HSMB, a novel NR-IQA metric developed to quantitatively evaluate MB in high-speed imaging environments associated with MTSS. Through ISO 12233-compliant laboratory experiments and multi-speed field data collected from operational tunnels, the results demonstrated that traditional NR-IQA metrics exhibit inconsistent responses to HSMB. In contrast, HSMB consistently showed strong correlations with physical quality indicators, BEW, and MTF50, supporting its effectiveness as a blur-sensitive metric.

HSMB provides high computational efficiency and relies on a formula-based rather than learning-based framework, which enhances its suitability for real-time applications. The metric can be directly integrated into MTSS platforms to detect and filter image quality variations. In laboratory evaluation, HSMB achieved PLCC values of 0.9354 with BEW and 0.8449 with MTF50. In field validation, it achieved rank-based correlations of SROCC = 0.8000 and KRCC = 0.6667, confirming its applicability under real-world conditions.

Overall, HSMB represents a reliable and efficient NR-IQA metric for real-time image quality evaluation in high-speed image acquisition systems such as MTSS. It also offers potential as a pre-filtering mechanism to enhance the accuracy of downstream tasks, including deep learning-based crack detection and structural condition assessment. Future work will focus on broader validation across diverse tunnel environments and imaging configurations and on integration of HSMB into automated quality classification frameworks to support practical real-time deployment.

---

## Backmatter (Author Contributions, Funding, etc.)

**Author Contributions:** Conceptualization, C.L.; Methodology, C.L., D.K. (Donggyou Kim), D.K. (Dongku Kim) and J.A.; Formal analysis, C.L.; Resources, D.K. (Donggyou Kim); Writing---original draft, C.L.; Writing---review and editing, D.K. (Donggyou Kim) and D.K. (Dongku Kim); Supervision, D.K. (Donggyou Kim); Project administration, C.L. and D.K. (Donggyou Kim). All authors have read and agreed to the published version of the manuscript.

**Funding**\
This work was supported in part by the Korea Agency for Infrastructure Technology Advancement under Grant RS-2022-00142566.

**Acknowledgments**\
Research for this paper was conducted under the Development of Advanced Management Technology (Total Care) for infrastructure (project no. RS-2022-00142566) funded by the Korea Agency for Infrastructure Technology Advancement.

**Data Availability**

The datasets generated during and/or analysed during the current study are available from the corresponding author on reasonable request.

**Competing interests**\
The author(s) declare no competing interests.

> **한글 버전**: [ko/07_conclusion.md](ko/07_conclusion.md)

## 수정 메모 (Revision Notes)

> Reviewer C1~C3 대응 결과 반영 필요

### 수치 업데이트 예정

- [ ] 현장 검증 결과 수치 교체 (50조건 기반 SROCC/KRCC/PLCC, H/V 축 분리 보고)
- [ ] Permutation test p-value + Bootstrap 95% CI 결과 한 문장 추가
- [ ] CNN crack detection downstream 결과 한 문장 추가 (R03)
- [ ] area-scan 카메라 사용으로 imaging mechanism 일관성 확보 언급 (R01)
- [ ] **Anisotropy diagnostic 결과 언급** — 이방성 증가(60→80 km/h 0.38→0.70 px)가 translational motion blur 방향성 법칙 확인 (Fig 18d)
- [ ] **Complex-blur stress test 결과 언급** — autofocus 실패로 인한 motion+defocus 복합 조건에서도 HSMB가 품질 저하 감지 (Fig 18a~c)

### 표현 완화 (R02 관련)

- [ ] "rank-based correlations of SROCC = 0.8000 and KRCC = 0.6667, confirming its applicability" → 통계적 유의성 근거 기반 표현으로 수정
- [ ] 과장 표현 제거 및 한계·불확실성 명시

### 저자 기여 (확인 필요)

- [ ] 추가 저자 합류 여부에 따라 Author Contributions 재작성 (Q4)
