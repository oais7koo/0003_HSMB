# §V-E 신규 작성 상세기획

> 문서번호: d4020 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F004-2 | plan.md §3 E004 | **외부 트리거 의존 (blocked)**

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-04-26 | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d4020` |
| 대상 기능 | `F004-2 논문 §V-E (CNN crack detection 실험 결과) 신규 섹션 작성` |
| Reviewer 대응 | C3 (downstream) — 본 섹션 추가가 핵심 응답 |
| 의존 | F004-1 (Task B 분석), F002-3 (자체 E2 보조) |
| 상태 | blocked |
| 버전 | v01 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

F004-1 분석 결과를 바탕으로 논문 §V-E (CNN crack detection downstream) 섹션을 신규 작성. Reviewer C3 핵심 응답 자료. F002-3 자체 E2 결과는 보조 검증용으로 활용.

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | §V-E 섹션 구조 정의 (Setup·Result·Discussion) | Must | PRD F08 |
| R02 | F004-1 분석 결과 기반 본문 초안 | Must | PRD F08 |
| R03 | Figure 생성 (threshold 곡선, F1 비교) | Must | PRD F08 |
| R04 | Table 생성 (메트릭별 pre-filter 효과) | Must | PRD F08 |
| R05 | F002-3 자체 E2와 cross-validation 서술 | Should | 강건성 보강 |

## 4. 입출력 정의

### 4.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `00_doc/d0060_downstream_analysis.md` | MD | F004-1 산출물 | Y |
| `data/exp/downstream_analysis.csv` | CSV | F004-1 데이터 | Y |
| `00_doc/d0042_e2_correlation.md` | MD | F002-3 자체 E2 (보조) | N |

### 4.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `260422_HSMB논문 수정안/docs/section_v_e_draft.md` | MD | §V-E 초안 |
| `figures/v_e_*.png` | PNG | 논문 figure |
| `tables/v_e_*.tex` 또는 `.md` | text | 논문 table |

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| F004-1 결과 부정적 (HSMB pre-filter 효과 미미) | 정직 보고 + Discussion에서 한계·향후 방향 명시 |
| 협저자 검토 의견 충돌 | F005-1 검토 사이클에서 통합 조정 |
| 페이지 제약 | Figure 1개 + Table 1개로 압축 |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `F004-2` — §V-E 신규 작성
- 의존 Feature: **F004-1 (필수)**, F002-3 (보조)
- 후속 의존: F005-1 (논문 전체 통합)

## 7. 참고 자료

- PRD: `00_doc/d0001_prd.md` §5 F08
- 계획: `00_doc/d0002_plan.md` E004, S6 (trigger)
- 협업 패키지: `data/02_260422_HSMB논문 수정안/`

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
