# HSMB 논문 수정 TODO

## 프로젝트 정보
- **논문**: No-Reference Image Quality Assessment for High-Speed Motion Blur Database in Tunnel Inspection
- **상태 (v16, 2026-05-01 D33)**: **분기 투고 전략 + 시각 자료 우선 진행** — 버전 A 자체 작업 순서: (a) §V-A picked image → (b) §VIII-F Cases 2·3 시각 보강 → (c) §I SR 톤 정렬 → (d) §IX Conclusion 갱신 → (e) SR 가이드라인 수집. **버전 A = Scientific Reports 신규 투고** (Response Letter 불필요), **버전 B = IEEE Access 재투고** (Response Letter 9 코멘트 매핑 표 필수). 협업자 의뢰 6건 재배치: ③⑥ + 현장 area-scan 이미지 = 버전 A 필수, ①②④⑤ = 버전 B 전용
- **원본**: /Users/lch/home/db/submission_0729.docx
- **외부 리뷰 (3 라운드, 같은 원고)**:
  - **Scientific Reports (1명, 4건 S1.1~S1.4)** = R01~R04 라벨 원천: area-scan/line-scan, 통계 유의성, downstream CNN, 파라미터 근거. 원본: /Users/lch/home/db/Reviewer 1.docx (D30 정정)
  - **IVC**: Desk reject (CV/IQA pure 저널 응용 측면 평가 부적합, 후보 제외)
  - **IEEE Access (2명, 9건 C1.1~C2.5)**:
    - Reviewer 1 (C1.1~C1.4): dataset/4-speed instability, parameter optimization, DL fine-tuning + FISH/LPC-SI + FLOPs, field validation/full-image MTF
    - Reviewer 2 (C2.1~C2.5): GoPro/NfS 차별성, HTMP calibration, HSMB 수학 formulation, defect detection 통합, ablation 엄격성
    - 원본: /Users/lch/Downloads/IEEE ACCESS_REVIEW.docx
- **외부 의견 일관성**: SR 리뷰어와 IEEE Access Reviewer 1이 4개 약점을 독립적으로 동일 지적 → Response Letter 외부 신호로 활용 가능
- **PRD**: d0001_prd.md (v14, 2026-05-01)
- **Plan**: d0002_plan.md (v14, 2026-05-01)
- **논문 워크스페이스**: paper/sections/ 영문 + paper/sections/ko/ 한글 (각 9개)
- **현장 데이터 소스**: `/Users/lch/home/code/tunnelscanning/01_tunnelscanning/03_src/data/raw/cam1/` (50 CSV)
- **실내 데이터 소스**: `/Volumes/외장하드1/2026/1. 토탈케어/SCI/5. T-CPBD/실내실험 데이터/` → `data/lab/` (40 CSV 복사 완료, 2026-04-22)
- **실내 NR-IQA 지표**: `/Users/lch/home/db/01_전체데이터_2604281234.xlsx` (470 rows, 본 연구 사용 9-지표 추출 완료, 2026-04-29)

## 완료된 작업 (2026-04-06)

- [x] PRD 생성 (d0001_prd.md) — R01~R04 요구사항 정의
- [x] 구현 계획 생성 (d0002_plan.md) — Epic 4개, Phase 3단계
- [x] Response Letter 초안 (response_letter.md)
- [x] HSMB 메트릭 구현 (scripts/hsmb_metric.py)
- [x] Ablation study 스크립트 (scripts/ablation_study.py) — demo 검증 완료
- [x] 파라미터 이론적 근거 초안 (parameter_justification.md)
- [x] 저널 후보 조사 (Q1: NDT&E Int., Measurement, Optics & Lasers 등)

## 완료된 작업 (2026-04-21)

- [x] PRD v02 업데이트 — 현장 조건 확장 (10→50조건, 300→1,500장, ISO 축 추가)
- [x] Plan v02 업데이트 — E2 세부 태스크 갱신
- [x] **논문 원본 확보** (Revision_0224.docx) — paper/original/
- [x] docx → markdown 변환 (pandoc, 969줄) — paper/full_manuscript.md
- [x] 섹션별 편집 파일 분리 (9개) — paper/sections/
  - 00_frontmatter, 01_introduction, 02_related_research, 03_hsmb_dataset
  - 04_proposed_nr_iqa (R04), 05_experimental (R03), 06_field_validation (R01/R02)
  - 07_conclusion, 99_references
- [x] 이미지 추출 — paper/media/
- [x] References 번호 오류 발견 및 기록 ([72], [73] 공백)
- [x] PRD v03, Plan v03 업데이트 — 워크스페이스 반영
- [x] 현장 데이터 소스 확정 — tunnelscanning/cam1 (50조건 × 7~13장 = 약 500장)
- [x] 검정력 분석 수행 — N=50 조건 주 분석 power ≥ 0.95 (ρ≥0.5)
- [x] PRD v04, Plan v04 업데이트 — 실제 데이터 구조 및 통계 분석 이원화 반영
- [x] Cam1 CSV 취합 스크립트 (scripts/aggregate_field_gt.py) 작성 및 실행
- [x] Ground truth 통합 산출 — `data/field/ground_truth{_raw,_frame,}.csv` (50 조건, 491 프레임, 1,792 ROI)
- [x] Section VI 재작성 초안 v02 (paper/sections/06_field_validation.md) — Table 9/10 실측값 반영
- [x] 이상치 (iso=400, d=4.5m) 해석 — autofocus defocus + motion blur 복합 조건으로 규명, complex-blur stress test 프레임워크 추가
- [x] **Imatest 엣지 방향(H/V) 분리 분석** — aggregate 스크립트에 axis 분류 추가, 조건별 BEW/MTF50을 Horizontal(motion-dominant)/Vertical(reference)로 분리 집계
- [x] Table 9~12 (H/V 축 × BEW/MTF50) + Table 13 (이방성 diagnostic BEW_H − BEW_V) 초안 작성
- [x] Complex-blur 조건의 **3가지 물리적 증거** 체계화: (1) 양 속도 대칭 발생, (2) 양축 감쇠, (3) 이방성 보존 → autofocus defocus 가설 뒷받침
- [x] **Figure 18 히트맵 4장 생성** (scripts/plot_field_heatmaps.py) — BEW H/V, MTF50 H/V, 이방성 diagnostic, 속도별 이방성 bar → `results/field/figures/fig18[a-d].png`
- [x] Section VI 재작성 초안에 Figure 18 4장 삽입 완료 (각 figure별 caption + 물리적 해석)
- [x] **외부 협업 패키지 생성** — `share_package/hsmb_collab_20260421.zip` (1.0MB)
  - Task A (NR-IQA 스코어 7종) + Task B (CNN crack detection downstream) 두 작업 명세
  - scripts, data (50조건 GT), docs (Section 05/06 draft, Figure 18), results_expected 템플릿 7종
  - 메일 첨부 전송용

## 다음 세션 작업 (데이터 필요)

### E1: Ablation Study + 실내 H/V 분석 [R04]
- [x] **실내 SFR_cypx.csv 40조건 복사** — 외장하드 → data/lab/ (2026-04-22)
- [x] **aggregate_lab_gt.py 작성·실행** — BEW/MTF50 H/V 분리, 이방성 diagnostic (2026-04-22)
- [x] **실내 히트맵 4장 생성** (labFig_bew/mtf50/anisotropy/speed) — 이방성 +33.43 px 시각 증명 (2026-04-22)
- [x] **원본 논문 Table 4/5 재검증** — H축 단독 보고 확인 (5자리 소수점까지 일치)
- [x] **실내 NR-IQA 지표 값 수령 (2026-04-29)** — `/Users/lch/home/db/01_전체데이터_2604281234.xlsx` (470 rows × 34 cols, 9개 지표 본 연구 사용분 + 25개 미사용분)
- [x] **hsmb_statistics.py 프레임워크 작성 (2026-04-23)** — PLCC/SROCC/KRCC × 9 메트릭 × H/V 축 × BEW/MTF50 + Permutation(N=10k) + Bootstrap 95% CI, 25μs/90km/h 필터 내장, 40조건 일치 검증 완료. 데이터 재수령 즉시 재실행 가능
- [x] **HSMB v1/v2 구현 비교 (2026-04-25)** — 외장하드 `MTF(15000)-IQA 지표.xlsx` (v1) vs `_0715.xlsx` (v2) 비교. v1 PLCC(BEW) = −0.953 (1위), v2 = −0.763 (4위). 어제 분석은 v2 구현 사용으로 인해 저성능. **v1을 표준으로 채택 (D21)**
- [x] **9-지표 추출·집계 스크립트 (2026-04-29)** — `scripts/aggregate_lab_iqa.py` 작성. 본 연구 사용 9-지표(SSIM/PSNR/CPBD/BRISQUE/NIQE/PIQE/DBCNN/ARNIQA/HSMB)만 추출, 25μs·90km/h 필터링 → 400 images / 40 conditions, GT × IQA inner join 완료
- [x] **hsmb_statistics.py 재실행 (2026-04-29)** — 36 rows = 9 metrics × 2 axes × 2 targets, 입력 경로 + KEYS(iso 제거) + hsmb_v1→hsmb 정규화 패치 후 실행. 결과: HSMB BEW(H) PLCC=−0.932\*\*, BEW(V) −0.764\*\*, MTF50(V) +0.833\*\* (모두 NR-IQA 1위). MTF50(H)는 CPBD가 +0.938로 1위. 산출물: `data/lab/iqa_filtered.csv`, `iqa_condition_means.csv`, `results/lab/correlations_all.csv`, `results/lab/tables/table6_bew_correlations.md`, `table7_mtf50_correlations.md`, `results/lab/figures/scatter_*.png` × 18장
- [x] **§V-B 본문 재작성 (2026-04-29)** — Table 6/7 v03 (H/V 분리 + 통계검증), 본문 5 paragraph (BEW/MTF50/Directional balance/NSS·PIQE/FR) 영문·한글 동기화 완료. 핵심 메시지: HSMB의 V/H ≈ 1.02 directional balance가 motion-blur 도메인 특화의 정량 증거
- [x] **§V-A Tables 4/5 H/V 통합표 재구성 (2026-04-29)** — 4행 H 단독 → 8행 H/V 통합표(셔터 × 축 × 속도). H축은 원본 논문 수치 재현, V축 데이터 신규 추가. 본문 해석 단락 재구성 + 이방성 진단 단락 신설. 영문·한글 동기화
- [x] **§V-C 산점도 분석 섹션 신설 (2026-04-29)** — H/V 축별 본문 4 paragraph + Figure 12/13 (scatter_hsmb_bew_mean.png, scatter_hsmb_mtf50_mean.png) 채택. 기존 §V-C(공개 데이터셋)을 §V-D로 번호 조정. 영문·한글 동기화
- [x] **§V-D 공개 데이터셋 본문 보강 (2026-04-29)** — 인트로 paragraph 신설 + 3 paragraph 결과 해석(TID/CID2013, MMP-2K, 종합 generalisation profile)으로 §V-B 결과(PLCC −0.932)와 인과 연결. FR baseline 제외 사유 명시. 영문·한글 동기화
- [x] **PRD v07 / Plan v07 / TODO 동기화 (2026-04-29)** — D23 의사결정(재투고→신규 투고 전환), Response Letter 보류, 신규 Epic 5(저널 선정·포맷 정렬·Cover Letter) 추가, Q3 우선순위 격상
- [ ] **HSMB 코드 감사** — `scripts/hsmb_metric.py` 현재 구현이 v1 (원본) 인지 v2 (0715) 인지 확인, v2면 v1로 복원
- [ ] **40000 lux 포함 n=40 비교 데이터 확보** — 외장하드 `MTF 통합-IQA 지표_0716.xlsx` 등 후보 검토 (현재 01_전체데이터_2604281234.xlsx에 15000+40000 lx 모두 포함됨 — 추가 확보 필요성 재검토 가능)
- [ ] HSMB 데이터셋 원본 이미지 경로 확인 (파라미터 ablation·HSMB 재계산용)
- [ ] 실데이터로 ablation 수행 (Edge Weight, JNB, β)
- [ ] 논문용 Figure 생성 (파라미터 sensitivity curves)
- [ ] Section IV 서브섹션 영문 초안 작성 (파라미터 이론 근거)

### E2: 현장 데이터 교체 [R01, R02] — **소스 확정됨 (tunnelscanning/cam1)**
- [x] 데이터 소스 확정: tunnelscanning/cam1 50조건 (2속도 × 5거리 × 5ISO) — 2026-04-21
- [x] 검정력 분석: N=50 조건 주 분석에서 power ≥ 0.95 (ρ≥0.5) 확인 — 2026-04-21
- [ ] tunnelscanning/cam1 Imatest CSV(50개) 취합 → 통합 BEW/MTF50 테이블 생성
- [ ] 현장 area-scan 원본 이미지 수령 (약 500장, 조건당 7~13장 가변)
- [ ] HSMB + NR-IQA 메트릭 산출 (이미지 수령 후)
- [ ] 상관분석 (조건 N=50 주 + 이미지 N≈500 보조)
- [ ] 통계적 유의성 검증 (permutation test + Bootstrap 95% CI)
- [ ] ISO 축 메트릭 강건성 분석 (ISO별 SROCC 변동 ≤ 0.10 + 연속 회귀)
- [ ] **Complex-blur stress test** — (iso=400, d=4.5m) 2조건의 defocus+motion 복합 블러에 대한 HSMB 응답성 분석 (leave-two-out N=48 비교, 이웃 셀 대비 monotonic response 확인)
- [ ] Section 6 전면 재작성 (Table IX~XII, Figure 14~17 교체)

### E3: CNN Crack Detection [R03] — ResNet34 모델/데이터 확인 후
- [ ] ResNet34 가중치 + 균열 데이터셋 경로 확인
- [ ] 블러 수준별 detection 성능 측정 스크립트 작성
- [ ] HSMB 필터링 전/후 F1-score 비교
- [ ] 논문 서브섹션 + Table + Figure 작성

### E4: 논문 통합 수정 [R01~R04 + C1.1~C2.5] — E1~E3 완료 후
- [ ] Abstract, Section 4, 5, 6, 7, 8 수정
- [ ] **Response Letter 작성 (부활, v08 D25)** — 9 코멘트(C1.1~C2.5)별 변경사항 매핑 표 + 정당화 가능 항목(CycleGAN, vibration table 등) 학술 사유 + IEEE Access cover letter 통합
- [ ] References 추가 (FISH, LPC-SI 등 신규 베이스라인 인용)
- [ ] 최종 검토 + submission_v2.docx 생성 (IEEEtran 포맷)

### E5 (재정의 v08): IEEE Access 재투고 보강 작업
- [x] **저널 결정 (Q3 해소, 2026-04-29, D24+D25)** — IEEE Access 재투고 (resubmit), 12종 후보 비교 후 결정
- [ ] **E5-F3: IEEE 가이드라인 수집** — IEEEtran LaTeX 템플릿, 분량/그림/표 가이드, IEEE reference style, IEEE Author Center 체크리스트 → docs/journal_guidelines.md
- [ ] **E5-F4: 본문 톤·키워드 정렬** — Engineering·CS specialists readership 미세 조정 (현재 학술 톤 fit)
- [ ] **E5-F5: IEEEtran 포맷 적용** — 템플릿 이식, 그림 300 dpi 변환, 분량 검사
- [ ] **E5-F6: Cover Letter (= E4-F2 통합)** — Editor 메시지 + 9 코멘트 응답 + 변경 요약 + suggested reviewers

### Phase A (즉시 처리): IEEE 9 코멘트 즉시 대응 5건 [v08 D25] — **4/5 완료 (2026-04-29)**
- [x] **C2.1: GoPro·Need for Speed 데이터셋 차별성 (2026-04-29)** — §II-E 신규 sub-section 신설 + Table 1 (6 데이터셋 비교, 영문/한글). §V-D 인트로에 GoPro/NfS 제외 사유 인용. 어조 정정 + 연도 컬럼 제거 + Imatest 제거 + 한글 영어 단어 한글화 + 40조건 명확화 (5 속도 × 4 셔터 × 2 조명) 모두 반영
- [x] **C2.2: HTMP 장비 calibration·error margin (2026-04-29)** — §III-B 끝에 paragraph 추가 (HTMP servo/PLC 명목 사양 + Phantom VEO4K 글로벌 셔터 + Imatest eSFR ISO 12233 protocol + 정지 8조건 BEW 3.33 ± 0.14 px / 반복 sd 0.15 px / MTF50 0.163 ± 0.006 cy/px noise floor). §VIII-E에 dedicated calibration campaign future work 1 문장 추가
- [x] **부가: §III-C 산술 정정 (2026-04-29)** — 320 → 400 images (5 × 4 × 2 × 10) + "각 이미지 4 슬랜트 엣지 = 1,600 ROI" 명시 → §III-E 방향성 분해 narrative 강화
- [x] **C2.3: HSMB 수학 formulation 보강 (2026-04-29)** — §IV-B에 Eq. (1) T = w_e·⟨G⟩, Eq. (2) Weibull/Rayleigh P_blur, Eq. (3) F(P_jnb) 본문 명시 (이전 (2)/(3) 비어있던 자리 채움). Algorithm 1 pseudocode 박스 (20 lines) 추가 + scripts/hsmb_metric.py reference 인용. **A3 검증 중 Eq. (3) 정정 — F^(-1)(P_jnb) (quantile 잘못) → F(P_jnb) (CDF 평가, 코드 일치). HSMB ∈ [0, 1] (higher = sharper) 명시**
- [ ] **C1.3-2: FLOPs / inference time 측정** — **🚨 협업자 측정 의뢰 필요** (외부 자료 대기, D27 결정으로 자체 측정 폐기). HSMB v1 + 8 baseline 모두 협업자 컴퓨터/환경에서 측정 → 결과 수령 후 §V에 표 추가
- [x] **C1.4-1: Failure case 정성 예시 (2026-04-29)** — §VIII-F "FAILURE CASE ANALYSIS" 신규 sub-section 신설 (영문/한글) — 3개 케이스 분석: (i) 설계 영역 밖 복합 블러(motion+defocus, §VI-D), (ii) 정지·짧은 셔터의 sub-pixel 변동(BEW 3.0~3.6 px → HSMB 0.92~0.93 평탄화), (iii) V축 잔여 블러 PLCC(V) = −0.76 < H축 −0.93 (방향성 균형의 trade-off). 종합 paragraph: 3가지 개선 방향(multi-modal blur, sub-pixel EVP, H/V joint regression)

### Phase B (단기 처리, 2~5일): 코드/실험 필요 3건
- [ ] **C1.3-1: FISH·LPC-SI 베이스라인 추가** — Python 구현/변환, 9-지표 → 11-지표 확장, hsmb_statistics.py 재실행 (HSMB 원본 이미지 도착 시)
- [ ] **C1.2 + C2.5: 파라미터 grid search + noise sensitivity** — Edge Weight × β × Pjnb × JNB grid, Gaussian/S&P noise 합성, §IV-E ablation 결과 채우기 (v1 코드 + 원본 이미지 도착 시)
- [x] **C1.4-2: Full-image MTF estimation 정당화 (2026-04-29)** — §VIII-E LIMITATIONS에 1 문장 추가 (영문/한글) — chart-free full-image MTF 방법(natural-edge SFR, multi-region tile sampling)의 trade-off(교정 정확도 ↓ + 장면 의존 엣지 통계 민감도 ↑)와 MTSS 워크플로우 통합을 future work으로 frame. C1.4 모든 sub-항목 완전 응답

### Phase C (외부 자료 대기): 데이터/협업자 결과 의존 3건
- [ ] **C1.3-3: DL fine-tuning** — DBCNN, ARNIQA를 HSMB 일부로 fine-tune (HSMB 원본 이미지 + GPU 시간 필요)
- [ ] **C2.4: Task B downstream defect detection** — 외부 협업자 CNN crack detection 결과 수령
- [ ] **C1.1-2: 다중 터널 / 다양한 chart** — 추가 현장 촬영 또는 정당화로 대체

### Phase D — 버전 B 전용 (Response Letter 작성, 1~2일, IEEE Access 재투고용)

> *D32(2026-05-01)에 의해 버전 B 전용으로 재분류. 버전 A(SR 신규 투고)에서는 Response Letter 불필요.*

- [ ] **9 코멘트 매핑 표 작성** — C1.1~C2.5 각각의 변경사항 + 본문 line numbers + 새 Tables/Figures 인용
- [ ] **정당화 가능 항목 학술 사유** — CycleGAN(future work), vibration shaker(complex-blur stress test가 proxy), 다중 터널(추가 촬영 vs 통계검정력)
- [ ] **IEEE Access cover letter 통합** — Editor 메시지 + 9 코멘트 응답 + 변경 요약 + suggested reviewers 3명

## 완료된 작업 (2026-04-23)

- [x] **§II-D 신규 소절 추가** — "MTSS Imaging and Downstream Defect Detection" (영문 + 한글, 2문단)
  - 문단 1: line-scan [69] vs area-scan [9,10,16] 이미징 메커니즘 대비 → **R01 scholarly anchor**
  - 문단 2: CNN 균열 검출 [7,8,10-12,14,16] + Liu et al. [15] 한계 지적 → gap statement → §VII 연결 → **R03 scholarly anchor**
  - 기존 참조만 재사용 (신규 추가 없음), 지면 부담 최소화
  - §II-A/B/C FR→RR→NR 흐름 보존, §II-D는 "IQA 기법론" → "응용 맥락" 자연 확장
  - `paper/sections/02_related_research.md` + `ko/02_related_research.md` 수정 메모 갱신

## 완료된 작업 (2026-04-22)

- [x] 실내 실험 데이터 소스 확정 — 외장하드 `/Volumes/외장하드1/.../ps1040_kict_std_img_2nd_rename/`
- [x] 40조건 SFR_cypx.csv 복사 (`data/lab/lab_v??_s???_lx?????.csv`) — 25μs·90km/h 제외
- [x] `scripts/aggregate_lab_gt.py` 작성 → H/V 축 분리 + 이방성 diagnostic
- [x] 집계 산출: `data/lab/ground_truth{,_raw,_frame,_by_axis,_anisotropy}.csv` (5종)
- [x] 원본 논문 Table 4/5 재검증 — H축 단독 보고였음을 소수점 일치로 확인
- [x] `scripts/plot_lab_heatmaps.py` 작성 → 히트맵 4장 생성
  - BEW H/V heatmap, MTF50 H/V heatmap, 이방성 heatmap, 속도·셔터 bar
- [x] 실내 이방성 최대 **+33.43 px** (500μs × 70 km/h) — motion blur 방향성 법칙 시각 증명
- [x] PRD v05, Plan v05 업데이트 — 실내 분석 반영
- [x] **논문 구조 개편 (v05 후반)** — §VII CNN Crack Detection 신규 장 추가, §VIII Discussion 독립 분리, §IX Conclusion 재번호
  - [x] `paper/sections/07_crack_detection.md` (영문 + ko/) 신규 작성
  - [x] `paper/sections/08_discussion.md` (영문 + ko/) 신규 작성 — 주제별 A~E
  - [x] `07_conclusion.md` → `09_conclusion.md` 리네임 (영문 + ko/)
  - [x] Section I roadmap 문장을 9-섹션 구조로 업데이트 (영문 + 한글)
  - [x] `paper/INDEX.md` 전체 구조 갱신
  - [x] PRD §4.1/4.2, §10 관련 문서 갱신
  - [x] Plan E4 태스크 재번호, D14 의사결정 추가
- [x] **본문 작성 진전 (v06)**
  - [x] §I 재작성 v02 — area-scan 4K(실내)/8K(현장) + 0.3 mm/px GSD + downstream task 언급 (영·한)
  - [x] §III-E 신규 — H/V 분해 *방법론* (Δ diagnostic 정의, 결과는 §V/§VI에서 보고) (영·한)
  - [x] §IV-D 신규 — 파라미터 이론 근거 (GGD/JNB/Weibull) + Table 3 (영·한)
  - [x] §IV-E 신규 — Ablation study 프레임워크 + 결과 placeholder (영·한)
  - [x] §V-A에 H/V 결과 통합 (V축 ≈ 3.6 px, H축 속도×노출 비례, Δ peak +33.4 px) (영·한)
  - [x] References [75] Sharifi & Leon-Garcia (1995, GGD), [76] Geusebroek & Smeulders (2005, Weibull) 추가
  - [x] 모든 본문에서 revision-letter 언어 제거 (§VI, §VIII 영·한 — "previous version", "Reviewer Cx response", "(R0x)" 태그 제거)
  - [x] §VIII에 Reviewer 매핑 표를 수정 메모로 이동 (저자 내부 트레이싱)
  - [x] §II 추가 문단 폐기 → §IV-D로 일원화 (옵션 A: D15 결정)
  - [x] §III-E *방법론*만, Finding은 §V-A로 이동 (옵션 A: D16 결정)
  - [x] PRD v06, Plan v06 동기화

## 미결 사항

### ✅ 해소
- [x] **Q3 해소 (2026-04-29, D24): IEEE Access 채택** — Q1 (CS, Information Systems), IF ~3.4, acceptance ~30%, 심사 3~6 mo, APC $1,750, 분량 무제한, IEEE 위상 + novelty 평가. 12종 비교 후 결정

### 🚨 외부 자료 수령 대기 (사용자 행동)
- [x] **HSMB v1 소스 코드 수령 (2026-04-30, D27)** — `/Users/lch/home/db/ps2020_hsmb_v1.py` 수령 + `scripts/hsmb_metric.py`로 교체 완료. 기존 v2 구현은 `scripts/_internal_archive/`로 archive
- [x] **HSMB 실내 원본 이미지 수령 (2026-04-30, D28)** — 외장하드 → `data/lab/images/` (470 PNG, 2.7 GB). 본문 §III-B 해상도 정정 완료
- [x] **HSMB v1 sanity check 실행 + 결과 분석 (2026-04-30, D29)** — 460/460 매칭, **mean diff −0.332, Pearson 0.705, exact match 0건**. 자체 계산 ≠ 외부 결과 (systematic offset). 자체 sanity 자료 `_internal_archive/`로 폐기
- [ ] **🚨 협업자 의뢰 종합 (D27 + D29 통합)** — 모든 정량 측정을 협업자 환경에서 통일하여 의뢰:
  - ① **v1 inference time / FLOPs** (D27, HSMB v1 + 8 baseline 모두)
  - ② **v1 sanity 환경 정보** (D29, PNG 변환 방식·native vs ROI·v1 코드 정확 버전)
  - ③ **C1.2/C2.5 ablation grid search** (D29, 파라미터 sensitivity 정량 결과)
  - ④ **C1.3-1 FISH/LPC-SI 베이스라인** (D29, 11-지표 확장)
  - ⑤ **C1.3-3 DL fine-tuning** (D29, DBCNN/ARNIQA on HSMB)
  - ⑥ Task B CNN crack detection (C2.4, 기존)
- [ ] **🚨 현장 area-scan 원본 이미지** (50조건, 약 500장 — 현재 GT만 보유)
- [ ] **🚨 Task B 외부 협업자 결과 수령** (CNN crack detection downstream — C2.4)
- [ ] ResNet34 가중치 + 균열 데이터셋 경로 확인 (E3, Task B 의존)

### ⏳ v1 코드 도착 시 일괄 작업 (D21 코드 감사)
1. v1 ↔ 현재 `scripts/hsmb_metric.py` diff
2. **Q2 §IV-B EVP 정의 본문 정정** (코드 일치)
3. Eq. (1)/(2)/(3) v1 코드 검증
4. **A4 FLOPs/inference time** v1 코드 기준 측정 + §V-B 새 표
5. 필요시 `hsmb_metric.py`를 v1으로 교체
6. 외부 v1 결과(xlsx) sanity check

## 다음 세션 즉시 시작 가능 작업 (분기 전략 — 버전 A 우선)

### 🥇 1순위 — 버전 A 시각 자료 (이미지만, 측정값 없음)

> *D33(2026-05-01) 결정: 시각 자료를 narrative보다 먼저 확정하여 §I/§IX 서술이 figure를 일관되게 참조하도록 함.*

- [ ] **(a) §V-A picked image 갱신 (30분~1시간)** — 셔터·속도별 대표 ROI 이미지 채택, `data/lab/images/` 470 PNG에서 선정. 측정값은 외부 표준 그대로
- [ ] **(b) §VIII-F Cases 2·3 시각 보강 (1~2시간)** — Case 2: 정지(0 km/h)·50 μs ROI (sub-pixel 변동, BEW 3.0~3.6 → HSMB 0.92~0.93). Case 3: 70 km/h·500 μs H/V ROI 비교 (이방성 +33.43 px peak)
- [ ] **(b-1) §VIII-F Case 1 placeholder** — caption + "[현장 이미지 도착 시 추가]" 표기. **현장 area-scan 이미지 의존, 도착 후 보강**

### 🥈 2순위 — 버전 A narrative + 메타

- [ ] **(c) §I Introduction SR 톤 정렬 (1~2시간)** — Scientific Reports 일반 독자 관점 (이전 IEEE Access Engineering·CS specialist 톤에서 미세 조정)
- [ ] **(d) §IX Conclusion 갱신 (1~2시간)** — Phase A 결과 (directional balance V/H ≈ 1.02, 9-지표 통계 결과) 통합
- [ ] **(e) Scientific Reports 가이드라인 수집 (1~2시간)** — Nature Portfolio 양식, 분량/Figure DPI/Reference style/Author Center 체크리스트 → `docs/sr_guidelines.md`

### 🥉 3순위 — 버전 A 다듬기

- [ ] References 일관성 검증 (Table/Figure 번호 + 인용 순서)
- [ ] 영문/한글 본문 일관성 점검
- [ ] §VII CNN crack detection 본문 골격 강화 (Task B 결과 placeholder 명확화)

## 외부 자료 도착 시 작업 (분기 전략)

### 버전 A 필수 (SR 신규 투고 전 도착 권장)

- [ ] **③ §IV-E ablation 결과 (협업자)** → §IV-E 결과 채우기 (Edge Weight × β × Pjnb × JNB grid search) → S1.4/R04 정량 답변 완성
- [ ] **⑥ Task B CNN crack detection (협업자)** → §VII Tables 14/15/16 + Figures 19/20 + 본문 paragraph → S1.3/R03 정량 답변 완성
- [ ] **현장 area-scan 원본 이미지** → §VI Tables 9~13 정량 + Figure 18 갱신 → S1.1/R01 완성
- [ ] 위 3건 도착 → SR 양식 변환 (Nature Portfolio 템플릿) → Cover Letter (일반 신규 투고용) 작성 → 그림 ≥ 300 dpi 변환 → Final PDF 검토 → Editorial Manager 제출

### 버전 B 추가 (SR 투고 후 협업자 결과 누적 시)

- [ ] **① v1 inference time/FLOPs (협업자)** → §V 새 표 (HSMB v1 + 8 baseline) → C1.3-2 응답
- [ ] **② v1 sanity 환경 정보 (협업자)** → 본문 Methods §IV reference 환경 명시 강화
- [ ] **④ FISH·LPC-SI 결과 (협업자)** → 9-지표 → 11-지표 확장, §V-B Tables 6/7 갱신 → C1.3-1 응답
- [ ] **⑤ DBCNN, ARNIQA fine-tune (협업자)** → §V 새 표 (pre-trained vs fine-tuned) → C1.3-3 응답
- [ ] 위 4건 + 버전 A 도착분 → IEEEtran 포맷 변환 → 버전 B Response Letter (IEEE 9 코멘트 매핑) → IEEE Access 재투고

## 디버깅 섹션
(없음)
