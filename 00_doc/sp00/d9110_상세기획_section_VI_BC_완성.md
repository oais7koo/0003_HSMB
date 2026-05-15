# §VI-B·C 완성 상세기획

> 문서번호: d4030 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F004-3 | plan.md §3 E004 | **외부 트리거 의존 (blocked)**

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-04-26 | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d4030` |
| 대상 기능 | `F004-3 §VI-B (NR-IQA 비교) + §VI-C (BEW 상관) 완성` |
| 의존 | KICT Task A (NR-IQA 7종 스코어), F002-2 (E1-2 BEW 상관), F003-2 (complex-blur) |
| 상태 | blocked (Task A 수령 + F002-2/F003-2 완료 후) |
| 버전 | v01 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

협업자 Task A 결과(NR-IQA 7종 스코어)를 §VI-B에 통합하고, F002-2 E1-2 결과 + F003-2 complex-blur 분석을 §VI-C에 통합하여 논문 §VI 결과 섹션 완성.

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | Task A 결과 수령 양식 정의 (CSV 컬럼·메타) | Must | PRD F09 |
| R02 | Task A 데이터 검증 + §VI-B 비교표 작성 | Must | PRD F09 |
| R03 | F002-2 E1-2 결과 → §VI-C 상관분석 본문 작성 | Must | PRD F09 |
| R04 | F003-2 complex-blur 결과 → §VI-C 의도적 defocus 서술 통합 | Must | PRD §2.6 |
| R05 | Figure·Table 생성 (§VI-B 비교표, §VI-C scatter) | Must | PRD F09 |

## 4. 입출력 정의

### 4.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| Task A 결과 폴더 | external | KICT 수령 (NR-IQA 7종) | Y |
| `00_doc/d0041_e1_correlation.md` | MD | F002-2 산출 | Y |
| `00_doc/d0050_complex_blur.md` | MD | F003-2 산출 | Y |
| `260422_HSMB논문 수정안/docs/section06_draft.md` | MD | 수정 베이스 | Y |

### 4.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `260422_HSMB논문 수정안/docs/section06_draft.md` | MD (갱신) | §VI-B·C 완성판 |
| `figures/vi_b_*.png` | PNG | NR-IQA 비교표 figure |
| `figures/vi_c_*.png` | PNG | BEW 상관 scatter |

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| Task A 결과 양식 불일치 | KICT에 재요청 (R01 사전 협의) |
| Task A 결과 vs F002-1 자체 측정 차이 | 양쪽 모두 보고 + 차이 원인 Discussion |
| 의도적 defocus 서술 협저자 동의 필요 | F003-2 산출물과 함께 일괄 협의 |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `F004-3` — §VI-B·C 완성
- 의존 Feature: **외부 (Task A)**, F002-2, F003-2
- 후속 의존: F005-1 (논문 전체 통합)

## 7. 참고 자료

- PRD: `00_doc/d0001_prd.md` §5 F09, §2.6
- 계획: `00_doc/d0002_plan.md` E004, S6 (trigger)
- 협업: KICT Chulhee Lee Task A

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
| 2026-04-26 | Task A 결과 수령 양식(R01) KICT와 사전 협의 필요 | 🔴 미해결 |
