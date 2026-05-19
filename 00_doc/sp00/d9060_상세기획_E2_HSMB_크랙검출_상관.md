# E2 HSMB-크랙검출 상관 분석 상세기획

> 문서번호: d2060 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F002-3 | plan.md §3 E002

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v02 | 2026-05-19 | d9020(downstream task 실험 개념 설명서) 내용 흡수 — 별도 문서 폐지 |
| v01 | 2026-04-26 | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d2060` |
| 대상 기능 | `F002-3 HSMB-크랙검출 상관성 분석` |
| Reviewer 대응 | C3 (CNN crack detection downstream) — 자체 보강 증거 |
| 버전 | v02 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

보유 중인 DL 기반 crack detection 모델로 샘플 이미지를 추론하여 **이미지별 F1-score**를 산출하고, 동일 이미지의 HSMB 스코어와의 **상관성**을 분석. 협업자 Task B(C3 본격 대응)와 별개로 자체 증거를 마련하여 §V-E 초안 기반 자료로 활용.

### 2.1 실험 목적

| 목적 | 설명 |
|------|------|
| Reviewer C3 대응 | HSMB가 실제 응용 작업인 CNN crack detection 성능과 연결되는지 검증 — C3 지적에 대한 자체 보강 증거 확보 |
| HSMB 실용성 검증 | HSMB score가 낮은 이미지에서 crack detection 성능도 함께 낮아지는지 확인 → 현장 품질관리 지표 유효성 입증 |
| Pre-filtering 효과 확인 | HSMB threshold로 품질 낮은 이미지를 사전 필터링 시 crack detection 평균 품질 개선 여부 검증 |

### 2.2 핵심 연구 질문

| ID | 질문 | 확인 방법 |
|----|------|----------|
| RQ1 | 블러 수준이 증가하면 crack detection F1-score가 감소하는가? | BEW 또는 HSMB 구간별 F1 비교 |
| RQ2 | HSMB score와 이미지별 F1-score 사이에 상관성이 있는가? | HSMB × F1 scatter, PLCC/SROCC |
| RQ3 | HSMB threshold 기반 pre-filtering이 평균 F1을 개선하는가? | threshold sweep |
| RQ4 | HSMB가 downstream 품질관리 기준으로 사용할 수 있는가? | 성능 저하 구간과 threshold 안정성 확인 |

## 3. 분석 방법론

### 3.1 이미지별 F1-score 산출

각 이미지에 crack detection 모델을 적용하고 예측 mask를 생성한다. 예측 mask와 GT mask를 비교해 precision, recall, F1-score를 계산한다. F1-score는 precision과 recall의 조화평균으로, 오검출과 미검출을 함께 반영하는 지표이다. GT mask가 없는 이미지는 정량 분석에서 제외하거나 별도 라벨링 후보로 관리한다.

### 3.2 블러 구간별 성능 비교

BEW 또는 HSMB 기준으로 이미지를 Low, Mid, High blur 구간으로 나누고 각 구간의 평균 F1-score를 비교한다. 블러가 심한 구간에서 F1-score가 낮아지면 모션블러가 crack detection 성능을 저하시킨다는 근거가 된다.

### 3.3 HSMB × F1 상관분석

이미지별 HSMB score와 F1-score를 scatter plot으로 시각화하고 PLCC/SROCC를 계산한다. HSMB가 높을수록 이미지가 선명하고 F1-score도 높아지는 경향이 나타나면, HSMB가 downstream 성능을 설명하는 품질 지표로 해석될 수 있다.

### 3.4 Threshold Sweep

HSMB threshold `T`를 여러 값으로 바꾸면서 `HSMB >= T`인 이미지만 유지한다. 각 threshold에서 유지 이미지 비율과 평균 F1-score를 계산한다.

| 항목 | 의미 |
|------|------|
| threshold T | 품질 필터 기준 |
| retained ratio | 필터 후 남는 이미지 비율 |
| mean F1 | 필터 후 평균 검출 성능 |

Threshold가 높아질수록 평균 F1이 개선되지만 retained ratio가 지나치게 낮아질 수 있다. 품질 개선과 데이터 손실 사이의 trade-off를 함께 해석해야 한다.

### 3.5 결과 해석 기준

**긍정적 결과 (HSMB 유효성 인정):**
- BEW가 커질수록 F1-score가 감소한다.
- HSMB score가 낮을수록 F1-score가 감소한다.
- HSMB threshold pre-filtering 후 평균 F1-score가 개선된다.
- Low/Mid/High blur 구간 간 성능 차이가 일관되게 나타난다.

**부정적 또는 혼합 결과 처리:** HSMB와 F1-score의 상관성이 약하거나 threshold filtering 효과가 없을 경우, HSMB는 블러 정량화에는 유효하지만 특정 crack detection 모델의 성능을 직접 예측하는 지표로는 제한적이라고 보고한다.

---

## 4. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | 보유 DL crack detection 모델 환경 구성 (PyTorch + 가중치) | Must | PRD F15 |
| R02 | 샘플 이미지 선정 — 모션블러 수준 다양화 (HSMB 스펙트럼 커버) | Must | PRD F15 |
| R03 | 이미지별 inference → F1-score 산출 (GT mask 필요) | Must | PRD F15 |
| R04 | HSMB × F1 scatter + PLCC, SROCC 산출 | Must | PRD F15 |
| R05 | RQ8 (HSMB ↔ F1 상관성 수준) 정량 답 도출 | Must | PRD §3 |

## 5. 입출력 정의

### 5.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| DL crack model 가중치 | .pt/.pth | 보유 중 (위치 확인 필요) | Y |
| 샘플 이미지 + GT mask | folder | 모션블러 수준 다양화 | Y |
| `src/hsmb/v1.py` | Python | HSMB 산출 | Y |

### 5.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `src/crack_detector/` | Python module | 모델 래퍼 + 추론 진입점 |
| `data/exp/e2_crack_f1.csv` | CSV | 이미지별 HSMB, F1, GT crack 통계 |
| `figures/e2_scatter_hsmb_f1.png` | PNG | scatter (논문용) |
| `00_doc/sp00/d0042_e2_correlation.md` | MD | 분석 리포트 |

## 6. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| GT mask 없는 이미지 | 분석 제외 + 리스트화 (Task B 협업자에게 요청 후보) |
| 모델 가중치 위치 불명 | F001-1 인벤토리 작업 시 함께 식별 |
| F1 산출 시 임계값 의존성 | IoU 0.5 기준 + threshold sweep 보조 |
| Task B 결과와 중복/충돌 | 자체 분석은 §V-E 보조 자료로 한정, 본문은 Task B 우선 |

## 7. 관련 Feature (plan.md 연결)

- 연결 Feature: `F002-3` — E2 HSMB-크랙검출 상관
- 의존 Feature: F001-1 (모델 위치 식별)
- 후속 의존: F004-2 (§V-E 작성 보조 자료)

## 8. 참고 자료

- PRD: `00_doc/sp00/d0001_prd.md` §3 RQ8, §5 F15
- 계획: `00_doc/sp00/d0002_plan.md` E002, S3
- 협업: KICT Task B 결과는 별도 (`d9090_상세기획_downstream_분석_지원.md`, F004-1)
- BEW 기준값: `00_doc/sp00/d9010_bew.md`

> 자체 E2(본 문서)는 §V-E 초안 및 보조 증거 산출이 목적이며, Reviewer C3 본 대응 근거는 협업 Task B(d9090)가 담당한다. 두 결과가 같은 방향을 보이면 HSMB의 downstream 설명력이 더 강하게 뒷받침된다.

## 9. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
