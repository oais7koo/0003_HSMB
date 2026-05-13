# d9020_downstream task 실험.md - Downstream Task 실험 설명

## 문서이력관리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-05-13 | 초기 작성 |

---

## 1. 개요

Downstream task 실험은 이미지 품질 지표가 실제 후속 작업 성능과 어떤 관계를 갖는지 확인하는 실험이다. 본 프로젝트에서는 HSMB가 단순히 블러 정도를 수치화하는 데 그치지 않고, 터널 균열 검출 성능 저하를 설명할 수 있는지 확인하기 위해 downstream task 실험을 수행한다.

본 프로젝트의 downstream task는 CNN 기반 crack detection이다. 즉, 이미지의 모션블러 수준이 증가할 때 균열 검출 모델의 precision, recall, F1-score가 어떻게 변하는지 분석한다.

## 2. 실험 목적

### 2.1 Reviewer C3 대응

Reviewer C3의 핵심 지적은 HSMB가 실제 응용 작업인 CNN crack detection 성능과 연결되는지 검증이 부족하다는 점이다. Downstream task 실험은 이 지적에 대응하기 위한 핵심 실험이다.

### 2.2 HSMB의 실용성 검증

HSMB가 BEW와 높은 상관성을 갖는 것만으로는 실제 현장 활용성을 충분히 설명하기 어렵다. Downstream task 실험은 HSMB score가 낮은 이미지에서 crack detection 성능도 함께 낮아지는지 확인함으로써, HSMB가 현장 품질관리 지표로 유용한지 검증한다.

### 2.3 Pre-filtering 효과 확인

HSMB threshold를 이용해 품질이 낮은 이미지를 사전에 걸러내면 crack detection 결과의 평균 품질이 개선될 수 있다. 이를 확인하기 위해 여러 HSMB threshold에서 필터링 전후 F1-score 변화를 비교한다.

## 3. 핵심 연구 질문

| ID | 질문 | 확인 방법 |
|----|------|----------|
| RQ1 | 블러 수준이 증가하면 crack detection F1-score가 감소하는가? | BEW 또는 HSMB 구간별 F1 비교 |
| RQ2 | HSMB score와 이미지별 F1-score 사이에 상관성이 있는가? | HSMB × F1 scatter, PLCC/SROCC |
| RQ3 | HSMB threshold 기반 pre-filtering이 평균 F1을 개선하는가? | threshold sweep |
| RQ4 | HSMB가 downstream 품질관리 기준으로 사용할 수 있는가? | 성능 저하 구간과 threshold 안정성 확인 |

## 4. 실험 구성

### 4.1 입력 데이터

Downstream task 실험에는 다음 입력이 필요하다.

| 입력 | 설명 |
|------|------|
| 터널 이미지 | 다양한 블러 수준을 포함한 평가 이미지 |
| GT mask 또는 annotation | crack detection F1-score 계산 기준 |
| HSMB score | 이미지별 품질 점수 |
| BEW 또는 MTF50 | 블러 수준 기준값 |
| crack detection model | ResNet34 등 보유 CNN 기반 균열 검출 모델 |

GT mask가 없는 이미지는 F1-score 계산이 불가능하므로 정량 분석에서 제외하거나 별도 라벨링 후보로 관리한다.

### 4.2 출력 데이터

| 출력 | 설명 |
|------|------|
| 이미지별 성능표 | image_id, HSMB, BEW, precision, recall, F1 |
| 블러 구간별 요약표 | Low/Mid/High blur 구간별 평균 F1 |
| threshold sweep 결과 | HSMB threshold별 retained ratio, 평균 F1 |
| scatter plot | HSMB × F1, BEW × F1 관계 시각화 |
| overlay 이미지 | 예측 mask와 GT mask 비교 사례 |

## 5. 분석 방법

### 5.1 이미지별 F1-score 산출

각 이미지에 crack detection 모델을 적용하고 예측 mask를 생성한다. 예측 mask와 GT mask를 비교해 precision, recall, F1-score를 계산한다.

F1-score는 precision과 recall의 조화평균으로, 균열 검출에서 오검출과 미검출을 함께 반영하는 지표이다.

### 5.2 블러 구간별 성능 비교

BEW 또는 HSMB 기준으로 이미지를 Low, Mid, High blur 구간으로 나누고 각 구간의 평균 F1-score를 비교한다. 블러가 심한 구간에서 F1-score가 낮아지면 모션블러가 crack detection 성능을 저하시킨다는 근거가 된다.

### 5.3 HSMB와 F1의 상관분석

이미지별 HSMB score와 F1-score를 scatter plot으로 시각화하고 PLCC/SROCC를 계산한다. HSMB가 높을수록 이미지가 선명하고 F1-score도 높아지는 경향이 나타나면, HSMB가 downstream 성능을 설명하는 품질 지표로 해석될 수 있다.

### 5.4 Threshold Sweep

HSMB threshold `T`를 여러 값으로 바꾸면서 `HSMB >= T`인 이미지만 유지한다. 각 threshold에서 유지 이미지 비율과 평균 F1-score를 계산한다.

| 항목 | 의미 |
|------|------|
| threshold T | 품질 필터 기준 |
| retained ratio | 필터 후 남는 이미지 비율 |
| mean F1 | 필터 후 평균 검출 성능 |

Threshold가 높아질수록 평균 F1이 개선되지만 retained ratio가 지나치게 낮아질 수 있다. 따라서 품질 개선과 데이터 손실 사이의 trade-off를 함께 해석해야 한다.

## 6. 자체 E2와 협업 Task B의 구분

본 프로젝트에는 downstream 관련 실험이 두 종류로 나뉜다.

| 구분 | 목적 | 역할 |
|------|------|------|
| 자체 E2 | 보유 모델로 HSMB × F1 상관성 자체 확인 | §V-E 초안 및 보조 증거 |
| 협업 Task B | KICT 협업자가 수행하는 본격 CNN crack detection 실험 | Reviewer C3 본 대응 근거 |

자체 E2는 빠르게 근거를 확보하기 위한 보조 실험이고, 논문 본문에서는 협업 Task B 결과를 우선 사용한다. 두 결과가 같은 방향을 보이면 HSMB의 downstream 설명력이 더 강하게 뒷받침된다.

## 7. 결과 해석 기준

### 7.1 긍정적 결과

다음 경향이 확인되면 HSMB가 downstream 품질 지표로 유효하다고 해석할 수 있다.

- BEW가 커질수록 F1-score가 감소한다.
- HSMB score가 낮을수록 F1-score가 감소한다.
- HSMB threshold pre-filtering 후 평균 F1-score가 개선된다.
- Low/Mid/High blur 구간 간 성능 차이가 일관되게 나타난다.

### 7.2 부정적 또는 혼합 결과

HSMB와 F1-score의 상관성이 약하거나 threshold filtering 효과가 없을 수도 있다. 이 경우 HSMB는 블러 정량화에는 유효하지만, 특정 crack detection 모델의 성능을 직접 예측하는 지표로는 제한적이라고 보고해야 한다.

### 7.3 해석 시 주의사항

Crack detection 성능은 블러 외에도 균열 두께, 조명, 배경 복잡도, 라벨 품질, 모델 threshold에 영향을 받는다. 따라서 downstream task 실험에서는 HSMB 하나만으로 F1 변화를 설명하지 않고, BEW, 이미지 조건, crack 통계와 함께 해석해야 한다.

## 8. 관련 문서

| 문서 | 내용 |
|------|------|
| `00_doc/sp00/d0001_prd.md` | RQ3, RQ4, RQ8 및 F07, F15 정의 |
| `00_doc/sp00/d2060_상세기획_E2_HSMB_크랙검출_상관.md` | 자체 E2 실험 상세기획 |
| `00_doc/sp00/d4010_상세기획_downstream_분석_지원.md` | 협업 Task B 분석 지원 상세기획 |
| `00_doc/sp00/d9010_bew.md` | BEW 기준값 설명 |
