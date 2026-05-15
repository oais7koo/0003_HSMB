# Complex-blur stress test 상세기획

> 문서번호: d3020 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F003-2 | plan.md §3 E003

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-04-26 | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d3020` |
| 대상 기능 | `F003-2 ISO=400 의도적 defocus 조건 stress test` |
| Reviewer 대응 | 논문 §VI-C 서술 정정 (의도적 defocus) |
| 우선순위 | Should (PRD F11) |
| 버전 | v01 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

ISO=400 조건(설계상 의도적 defocus + motion 복합 블러)에서 HSMB의 응답성과 모노토닉성을 분석하여 **복합 블러 스트레스 테스트** 결과를 도출. 동시에 기존 논문의 "autofocus 수렴 실패 추정" 서술을 **"의도적 defocus 설계 조건"**으로 전면 수정 (PRD §2.6).

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | 47조건 중 ISO=400 조건 별도 subset 분리 | Must | PRD §2.6 |
| R02 | HSMB 응답성 분석 (defocus 강도 vs 스코어) | Must | PRD F11 |
| R03 | 모노토닉성 검증 (motion 강도 단조 증가에 HSMB 단조 반응?) | Must | PRD §4.3 |
| R04 | 이방성(BEW_H − BEW_V) 작음 검증 (E1-2 결과 활용) | Must | PRD §2.6 |
| R05 | `section06_draft.md` §VI-C 서술 정정 (정성→정량 근거 포함) | Must | PRD §2.6 |

## 4. 입출력 정의

### 4.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `data/ps1204_kict_eSFR/*ISO0400*` | folder | ISO=400 조건 폴더만 | Y |
| `data/exp/e1_iqa_scores.csv` | CSV | F002-1 결과 (HSMB 스코어) | Y |
| `data/exp/e1_bew.csv` | CSV | F002-2 결과 (이방성) | Y |
| `260422_HSMB논문 수정안/docs/section06_draft.md` | MD | 수정 대상 | Y |

### 4.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `data/exp/complex_blur_subset/` | folder | ISO=400 결과 분리 저장 |
| `00_doc/sp00/d0050_complex_blur.md` | MD | stress test 분석 리포트 |
| `figures/complex_blur_response.png` | PNG | HSMB 응답 곡선 |
| `260422_HSMB논문 수정안/docs/section06_draft.md` | MD (수정) | §VI-C 서술 정정 |

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| HSMB가 모노토닉하지 않음 | 정직 보고 + complex blur 한계로 §VI-D Discussion에 추가 |
| 이방성이 예상대로 작지 않음 | E1-2 (F002-2) 결과 재검토 + PRD §2.6 가설 재논의 |
| section06_draft.md 협저자 동의 필요 | 수정안 PR/diff 형태로 별도 문서화 후 협의 |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `F003-2` — Complex-blur stress test
- 의존 Feature: F002-1, F002-2 (E1-1, E1-2 완료 후)
- 후속 의존: F005-1 (§VI-C 서술 반영)

## 7. 참고 자료

- PRD: `00_doc/sp00/d0001_prd.md` §2.6 (의도적 defocus), §4.3 (성능 목표 모노토닉)
- 계획: `00_doc/sp00/d0002_plan.md` E003, S5
- 협업 패키지: `data/02_260422_HSMB논문 수정안/`

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
