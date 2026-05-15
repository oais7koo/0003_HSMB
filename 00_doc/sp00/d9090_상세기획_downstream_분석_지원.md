# downstream 분석 지원 (C3 대응) 상세기획

> 문서번호: d4010 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F004-1 | plan.md §3 E004 | **외부 트리거 대기 (blocked)**

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
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
| 버전 | v01 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

협업자(KICT)가 수행한 **Task B (CNN crack detection)** 결과 데이터를 수령·검증하고, **HSMB threshold pre-filtering이 downstream 검출 성능을 개선하는지** 분석하여 Reviewer C3 지적에 대응. F002-3(자체 E2)와 비교 보강.

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

- PRD: `00_doc/d0001_prd.md` §3 RQ3·RQ4, §5 F07
- 계획: `00_doc/d0002_plan.md` E004, S6 (trigger)
- 협업: KICT Chulhee Lee, `data/02_260422_HSMB논문 수정안/`

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
| 2026-04-26 | Task B 결과 수령 양식(R01) KICT와 사전 협의 필요 | 🔴 미해결 |
