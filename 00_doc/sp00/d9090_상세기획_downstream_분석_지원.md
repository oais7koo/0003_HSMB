# downstream 분석 지원 (C3 대응) 상세기획

> 문서번호: d4010 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F004-1 | plan.md §3 E004 | **외부 트리거 대기 (blocked)**

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v02 | 2026-05-19 | d9020(downstream task 실험 개념 설명서) 내용 흡수 — 별도 문서 폐지 |
| v01 | 2026-04-26 | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d4010` |
| 대상 기능 | `F004-1 KICT Task B (CNN crack detection) 결과 통합·분석` |
| Reviewer 대응 | **C3 (CNN crack detection downstream)** — 본 대응 |
| 트리거 | KICT Chulhee Lee Task B 결과 수령 (TBD-5) |
| 상태 | blocked |
| 버전 | v02 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

협업자(KICT)가 수행한 **Task B (CNN crack detection)** 결과 데이터를 수령·검증하고, **HSMB threshold pre-filtering이 downstream 검출 성능을 개선하는지** 분석하여 Reviewer C3 지적에 대응. F002-3(자체 E2)와 비교 보강.

### 2.1 자체 E2 vs 협업 Task B 역할 구분

본 프로젝트의 downstream 관련 실험은 두 종류로 나뉜다.

| 구분 | 담당 문서 | 목적 | 논문 역할 |
|------|----------|------|----------|
| 자체 E2 | `d9060_상세기획_E2_HSMB_크랙검출_상관.md` | 보유 모델로 HSMB × F1 상관성 자체 확인 | §V-E 초안 및 보조 증거 |
| 협업 Task B (본 문서) | `d9090_상세기획_downstream_분석_지원.md` | KICT 협업자가 수행하는 본격 CNN crack detection 실험 | **Reviewer C3 본 대응 근거** |

자체 E2는 빠르게 근거를 확보하기 위한 보조 실험이고, 논문 본문에서는 협업 Task B 결과를 우선 사용한다. 두 결과가 같은 방향을 보이면 HSMB의 downstream 설명력이 더 강하게 뒷받침된다.

---

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | Task B 결과 데이터 수령 양식 정의 (CSV 컬럼, GT mask 포함 여부) | Must | PRD F07 |
| R02 | 결과 검증 (행 수·컬럼·값 범위·중복) | Must | PRD F07 |
| R03 | HSMB threshold sweep × F1-score 분석 (RQ4 답) | Must | PRD §3 RQ4 |
| R04 | pre-filtering 전후 F1 비교 곡선 | Must | 논문 §V-E |
| R05 | F002-3 자체 E2 결과와 cross-validation | Should | 강건성 보강 |

## 4. 입출력 정의

### 4.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| Task B 결과 폴더 | external | KICT 수령 (양식 R01) | Y |
| `data/exp/e2_crack_f1.csv` | CSV | F002-3 자체 E2 (cross-val용) | N |
| `src/hsmb/v1.py` | Python | HSMB 산출 | Y |

### 4.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `data/exp/task_b_crack_results/` | folder | 검증된 Task B 결과 사본 |
| `data/exp/downstream_analysis.csv` | CSV | threshold × F1 매트릭스 |
| `00_doc/d0060_downstream_analysis.md` | MD | C3 대응 분석 리포트 |
| `figures/v_e_threshold_curve.png` | PNG | 논문 §V-E figure |

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| Task B 결과 양식 불일치 | KICT에 재요청 (R01 양식 사전 협의 권장) |
| 결과 수령 지연 (TBD-5) | F002-3 자체 E2로 §V-E 초안 우선 작성, 수령 후 보강 |
| HSMB pre-filtering 효과 negative | 정직 보고 + Discussion에 한계 명시 |
| GT mask 누락 | F1 산출 불가 → 해당 이미지 제외 + 리포트 |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `F004-1` — downstream 분석 지원
- 의존 Feature: 외부 (Task B 수령), F002-3 (cross-val)
- 후속 의존: **F004-2 (§V-E 작성)**, F005-1 (논문 통합)

## 7. 참고 자료

- PRD: `00_doc/sp00/d0001_prd.md` §3 RQ3·RQ4, §5 F07
- 계획: `00_doc/sp00/d0002_plan.md` E004, S6 (trigger)
- 협업: KICT Chulhee Lee, `data/02_260422_HSMB논문 수정안/`
- 자체 E2 실험: `00_doc/sp00/d9060_상세기획_E2_HSMB_크랙검출_상관.md` (F002-3)
- BEW 기준값: `00_doc/sp00/d9010_bew.md`

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
| 2026-04-26 | Task B 결과 수령 양식(R01) KICT와 사전 협의 필요 | 🔴 미해결 |

## 9. 결과 해석 주의사항

Crack detection 성능은 블러 외에도 다음 요인에 영향을 받는다. 협업 Task B 결과 통합·분석 시 HSMB 하나만으로 F1 변화를 설명하지 않고, BEW, 이미지 조건, crack 통계와 함께 복합적으로 해석해야 한다.

| 교란 요인 | 영향 설명 |
|----------|----------|
| 균열 두께 | 폭이 좁은 균열은 블러와 무관하게 검출 난이도 자체가 높음 |
| 조명 조건 | 조도·반사 차이가 crack 대비를 바꿔 F1에 영향 |
| 배경 복잡도 | 배경 texture가 복잡할수록 오검출 증가 |
| 라벨 품질 | GT mask 정밀도에 따라 F1 산출값 자체가 달라짐 |
| 모델 threshold | 검출 모델의 confidence threshold 설정이 precision/recall 균형에 영향 |

HSMB pre-filtering 효과가 부정적(threshold 적용 후 F1 개선 미확인)으로 나타날 경우, HSMB는 블러 정량화에는 유효하지만 해당 crack detection 모델의 성능을 직접 예측하는 지표로는 제한적이라고 정직하게 보고하고 Discussion에 한계를 명시한다.
