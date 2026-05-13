# oosota 논문 품질 체크리스트

> `oosota check` 실행 시 참조하는 기준 문서.
> 각 항목은 **Critical / Warning / Info** 3등급으로 분류된다.

---

## 1. 섹션 구조 (Section Structure)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| S01 | Critical | 상위 섹션(###)은 하위 섹션(####) 나열 전 5문장 이내의 도입문을 포함해야 한다 |
| S02 | Critical | 표(Table)나 수식만 단독으로 등장하는 섹션은 허용하지 않는다. 반드시 도입 문장이 선행되어야 한다 |
| S03 | Warning | 각 섹션은 해당 섹션에서 무엇을 다루는지, 왜 중요한지를 독자에게 안내해야 한다 |
| S04 | Warning | 결과 섹션은 단순 수치 나열이 아닌 해석(interpretation)을 포함해야 한다 |
| S05 | Info | 섹션 말미에 다음 섹션으로의 전환 문장이 있으면 가독성이 향상된다 |

---

## 2. 내부 마커 잔존 (Internal Markers)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| M01 | Critical | ps 코드(ps3110, ps4194 등 실험 스크립트 식별자)가 본문에 노출되어 있지 않아야 한다 |
| M02 | Critical | 타임스탬프(2512082132 형식 등)가 섹션 제목이나 본문에 남아 있지 않아야 한다 |
| M03 | Critical | ✅ ❌ 🔮 ⭐ 등 이모지가 본문에 포함되어 있지 않아야 한다 |
| M04 | Critical | "V1", "V2" 등 내부 버전 레이블이 설명 없이 독립적으로 사용되고 있지 않아야 한다 |
| M05 | Warning | "실험설정", "결과", "분석" 등 실험노트 스타일의 소제목이 논문 형식으로 대체되었는지 확인 |
| M06 | Warning | 실험 스크립트 파일명(ps*.py)이 본문에 직접 언급되지 않아야 한다 |

---

## 3. 수치 일관성 (Numerical Consistency)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| N01 | Critical | Abstract의 핵심 수치가 본문 및 테이블 수치와 일치해야 한다 |
| N02 | Critical | 동일 실험 결과가 본문 여러 곳에서 다르게 표기되지 않아야 한다 |
| N03 | Warning | 비교 대상(SOTA, baseline) 수치가 출처(논문/테이블)와 일치해야 한다 |
| N04 | Warning | %p(퍼센트포인트)와 %(퍼센트) 표기가 문맥에 맞게 구분되어야 한다 |
| N05 | Info | 소수점 자릿수가 테이블 내에서 통일되어야 한다 |

---

## 4. Abstract 품질 (Abstract Quality)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| A01 | Critical | 문제 정의, 제안 방법, 실험 결과, 기여점 4요소가 모두 포함되어야 한다 |
| A02 | Critical | 핵심 정량 결과(mIoU 등 주요 수치)가 명시되어야 한다 |
| A03 | Warning | 미설명 약어나 내부 용어가 초록에 등장하지 않아야 한다 |
| A04 | Warning | 결과에 대한 해석(의미, 시사점)이 포함되어야 한다 |

---

## 5. 기여점 및 논리 흐름 (Contribution & Flow)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| C01 | Critical | 기여점이 3개 이상, 구체적 수치로 명시되어야 한다 |
| C02 | Warning | 서론의 기여점 목록이 실험 결과 섹션과 대응되어야 한다 |
| C03 | Warning | Abstract → Introduction → Conclusion의 핵심 주장이 일관되어야 한다 |
| C04 | Info | Negative Result가 있을 경우 그 의미가 명확히 기술되어야 한다 |

## 5-1. 기승전결 논리성 (Argumentative Logic)

> 논문 전체가 하나의 논증 흐름을 형성하는지 검사한다.

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| L01 | Critical | **기(起)**: 서론에서 제기한 문제(이미지 품질 변동, 선형 구조 등)가 방법론 섹션에서 실제로 해결되는지 대응 관계가 명확해야 한다 |
| L02 | Critical | **승(承)**: 방법론의 각 구성요소(DBCAFM, LPFM, 적응형 학습 등)가 해결하려는 문제와 1:1로 연결되어야 한다 |
| L03 | Critical | **전(轉)**: 실험 결과가 방법론의 주장을 뒷받침해야 한다. 주장한 구성요소가 실제로 성능에 기여함을 Ablation으로 증명해야 한다 |
| L04 | Critical | **결(結)**: 결론이 서론의 문제 제기에 정확히 답해야 한다. "우리가 제기한 문제 X를 방법 Y로 해결하여 결과 Z를 얻었다" 구조여야 한다 |
| L05 | Warning | 서론에서 언급된 도전과제(4가지)가 실험 결과/Discussion에서 각각 다루어져야 한다 |
| L06 | Warning | 실험 결과에서 예상과 다른 결과(IQA 실패, Standard Aug 저하 등)는 Discussion에서 원인 분석이 제시되어야 한다 |
| L07 | Warning | 한계점(Limitation) 기술이 서론의 문제 범위와 연결되어야 한다 (해결 못한 문제가 솔직히 기술되어야 함) |
| L08 | Info | 논문 전체에서 동일 개념을 지칭하는 용어가 일관되게 사용되어야 한다 (예: "균열"과 "크랙" 혼용 금지) |

---

## 6. 참고문헌 (References)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| R01 | Warning | 본문 인용([1], [2] 등)이 참고문헌 목록에 모두 존재해야 한다 |
| R02 | Warning | 참고문헌이 20개 이상이어야 한다 |
| R03 | Info | 최신 3년 이내(2022~2025) 논문이 포함되어야 한다 |
| R04 | Critical | 참고문헌은 **IEEE 스타일 번호 리스트** 형식으로 작성해야 한다. 테이블 형식 금지. 형식: `[N] Author(s), "Title," Journal/Conference, vol. X, no. Y, pp. Z–W, Year.` 필수 요소: 저자, 제목, 게재처(저널명 또는 학회명), 연도. 권장 요소: 볼륨, 페이지, DOI |
| R05 | Warning | 참고문헌 내 저널명과 학회명 표기가 전체적으로 통일되어야 한다 (약어 vs 풀네임 혼용 금지) |

---

## 7. 테이블 품질 (Table Quality)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| T01 | Critical | 모든 테이블에 캡션(Table N. 제목)이 있어야 한다 |
| T02 | Critical | 테이블 수치는 실험 문서에서 직접 추출되어야 한다 (추정/임의 생성 금지) |
| T03 | Warning | 본문에서 테이블을 명시적으로 참조(Table N 참조)해야 한다 |
| T04 | Warning | 비교 테이블에는 제안 모델과 베이스라인이 명확히 구분되어야 한다 |

---

## 8. 용어 정의 (Terminology Definition)

> ooreport review P08~P10 통합

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| D01 | Critical | 수식에 등장하는 기호가 본문에서 정의되었는지 확인 (ooreport P08) |
| D02 | Warning | 약어가 최초 등장 시 원어를 병기하였는지. 예: "ASPP (Atrous Spatial Pyramid Pooling)" (ooreport P09) |
| D03 | Warning | 갑자기 새로운 용어가 사전 설명 없이 등장하지 않는지 확인 (ooreport P10) |

---

## 9. 교차 섹션 정합성 (Cross-Section Consistency)

> ooreport review P01~P04, P11~P12 통합

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| X01 | Critical | 기준 섹션(방법론) 대비 전체 섹션의 용어·모듈명 일치 여부 (ooreport P01) |
| X02 | Critical | 동일 파라미터(T_max, batch_size 등)가 여러 섹션에 기재된 경우 수치 일치 (ooreport P02) |
| X03 | Critical | 본문 내 Table 참조 번호가 실제 테이블과 일치하는지 (ooreport P03) |
| X04 | Critical | 데이터셋명, 모델명이 전 섹션에서 동일하게 사용되는지 (ooreport P04) |
| X05 | Critical | 핵심 방법론 섹션 기술 내용과 Abstract·Introduction·Conclusion 일치 여부 (ooreport P11) |
| X06 | Critical | Ablation Study에서 실제 실험한 모듈 목록이 전 섹션에서 동일하게 기술되는지 (ooreport P12) |

---

## 10. 제안 모델 표기 (Proposed Model Identity)

> ooreport review P15~P17 통합

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| PI01 | Warning | 제안 모델 약어가 Abstract 하단 Keywords 목록에 포함되어 있는지 (ooreport P15) |
| PI02 | Critical | Abstract 또는 §1에서 제안 모델명이 최초 등장할 때 "ModelName (Full Name)" 형식으로 풀네임을 병기하였는지 (ooreport P16) |
| PI03 | Critical | 성능·실험 결과 문장에서 "Dual-Branch 모델", "제안 방법" 등 모호한 주어 대신 제안 모델명을 일관 사용하는지 (ooreport P17) |

---

## 11. 문서 구조 고급 (Advanced Structure)

> ooreport review P13~P14, P18~P21 통합

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| H01 | Warning | 내용이 너무 적은 섹션(2~3문장 이하)은 상위 섹션에 통합. 부모 섹션 안에 서브섹션이 1개뿐인 경우도 통합. **적용 범위**: ### 헤딩뿐 아니라 볼드 텍스트 번호(`**X.Y.Z ...**`) 형태의 서브섹션에도 동일 기준 적용. 특히 Related Work에서 논문 1편당 서브섹션 1개를 부여하는 패턴은 과분화에 해당 (ooreport P13) |
| H02 | Warning | 문장이 5개 이하인 짧은 문단은 가급적 인접 문단과 합쳐 문단 밀도를 높임 (ooreport P14) |
| H03 | Critical | 학술 논문은 ### (h3, X.Y) 까지만 사용. #### (h4, X.Y.Z) 레벨 서브섹션은 상위 레벨로 승격. **모든 형태의 pseudo-heading**도 실질적 서브섹션이므로 동일 기준 적용: (a) 번호형 `**X.Y.Z 제목**`, (b) 비번호형 `**제목.**` 또는 `**제목:**` (예: `**차등 학습률.**`, `**Cross-Attention 메커니즘.**`). 검색 패턴: `^\*\*.*\.\*\*` 에서 Table 캡션을 제외한 항목 (ooreport P19) |
| H04 | Warning | "논문 구성(Paper Organization)" 등 관례적 섹션이 단일 문단(5문장 이하)으로 빈약한 경우, 내용 보완으로 섹션 밀도 확보 (ooreport P20) |
| H05 | Warning | 하위 서브섹션을 가진 부모 섹션의 고유 도입 텍스트가 1~2문장에 불과하여 서브섹션 내용의 단순 요약·나열에 그치는 경우. (1) 도입부를 확장하여 설계 동기·서브섹션 간 관계를 설명하거나, (2) 도입 문장을 첫 번째 서브섹션에 흡수할 것 (ooreport P21) |
| H06 | Critical | Related Work, Method, Discussion 섹션에서 불릿 포인트(-, •) 및 개조식 표현 대신 연속 서술문으로 구성 (ooreport P18) |

---

## 12. 내부 정보 노출 제거 (Internal Info Exposure)

> ooreport review P05~P07 통합 (기존 M01~M06과 보완)

| ID | 등급 | 체크 항목 |
|:---|:---:|:---|
| E01 | Critical | ps3510, ps4194 등 내부 스크립트 번호 노출 여부 (ooreport P05, M01 보완) |
| E02 | Critical | Phase 6.1, Phase 19 등 내부 개발 단계 번호 노출 여부 (ooreport P06) |
| E03 | Warning | 개발 중 임시 메모·주석성 표현("TODO", "TBD", "Note:" 등)이 본문에 남아있는지 (ooreport P07) |

---

## oosota check 출력 형식

```
[oosota check] 품질 체크리스트 점검 결과
================================================
Critical: N건  |  Warning: N건  |  Info: N건
------------------------------------------------
[Critical] S01 - §4.3.2: 하위 섹션 도입문 누락
[Critical] M03 - §3.2: 이모지(✅) 잔존
[Warning]  N04 - §4.5: %p/%% 혼용 표기
[Info]     R03 - 2022년 이후 논문 비율 확인 권장
------------------------------------------------
수정 우선순위: Critical 항목 → Warning 항목 순으로 처리
```
