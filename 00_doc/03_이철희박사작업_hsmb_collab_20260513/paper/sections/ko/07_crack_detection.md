# Section VII — 모션블러가 균열 검출에 미치는 영향 (한글 버전)

> **Source**: `../07_crack_detection.md` (영문)
> **Status**: 저자 내부 검토용 | 신규 섹션 (구조 개편 v05)

---

### VII. 모션블러가 균열 검출에 미치는 영향 — *Task B 결과 대기 중*

> Reviewer C3 (R03) 정면 대응용 신규 섹션. 외부 협업자의 ResNet34 균열 검출 실험 결과(`share_package/` Task B 브리프)를 수령한 후 수치 반영.

#### A. 실험 Setup

- 모델: ResNet34 (협업자 보유 균열 데이터셋으로 사전학습)
- 평가 이미지: 50조건 현장 area-scan (§VI에서 사전 등록된 세트)
- Ground truth: pixel-level 또는 bounding-box 라벨 (협업자 제공)
- 평가 지표: Precision, Recall, F1-score (가능 시 IoU/Dice 추가)
- 블러 bin 후보: BEW < 4 (Low), 4–5.5 (Mid), ≥ 5.5 (High)
- HSMB 필터 threshold sweep: T ∈ {0.1, …, 0.9}; 논문 P_jnb 값 T = 0.63 별도 보고

#### B. 블러 수준별 검출 성능 (대기)

*Table 14 (신규)*: 블러 bin별 F1 평균 ± SD (50 조건)

**예상**: BEW 증가에 따라 F1이 단조 감소 → "motion blur가 CNN 균열 검출 신뢰성을 저하시킨다"는 원고의 질적 주장이 **정량적으로 뒷받침**됨.

#### C. HSMB threshold 기반 사전 필터링 (대기)

*Table 15 (신규)*: threshold sweep 결과 (T, pass ratio, P/R/F1)
*Figure 19 (신규)*: T–F1 곡선 + 운용 최적점 표시

#### D. 필터 적용 전후 비교 (대기)

*Table 16 (신규)*: 3행 — unfiltered baseline, T = 0.63, T = optimal

#### E. Complex-blur 조건에서의 행동 (대기)

ISO 400 / 거리 4.5 m 조건에서 검출 F1 값을 별도 보고.

**예상**: HSMB 필터가 해당 이미지를 자연스럽게 배제 (defocus+motion이 HSMB와 F1 모두 하락) → 설계 범위 밖의 실제 운용 실패 모드에서도 일반화됨을 증명.

#### F. 예측 오버레이 예시 (대기)

*Figure 20 (신규)*: 블러 전후 예측 마스크 3~5 쌍 (Low/Mid/High + complex-blur)

---

## 데이터 수령 후 작업

- [ ] §A 실험 setup 본문 최종화 (라벨 정의·bin 기준)
- [ ] §B~F 결과 본문 작성 및 수치 삽입
- [ ] Discussion(§VIII-C)과 연계 서술 반영
