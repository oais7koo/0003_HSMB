# E2 HSMB-크랙검출 상관 분석 상세기획

> 문서번호: d2060 | 단계: 기획 | SP: flat | 생성일: 2026-04-26
> 연결 Feature: F002-3 | plan.md §3 E002

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-04-26 | 초기 작성 |

---

## 1. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d2060` |
| 대상 기능 | `F002-3 HSMB-크랙검출 상관성 분석` |
| Reviewer 대응 | C3 (CNN crack detection downstream) — 자체 보강 증거 |
| 버전 | v01 |
| 작성일 | 2026-04-26 |

---

## 2. 기능 개요

보유 중인 DL 기반 crack detection 모델로 샘플 이미지를 추론하여 **이미지별 F1-score**를 산출하고, 동일 이미지의 HSMB 스코어와의 **상관성**을 분석. 협업자 Task B(C3 본격 대응)와 별개로 자체 증거를 마련하여 §V-E 초안 기반 자료로 활용.

## 3. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | 보유 DL crack detection 모델 환경 구성 (PyTorch + 가중치) | Must | PRD F15 |
| R02 | 샘플 이미지 선정 — 모션블러 수준 다양화 (HSMB 스펙트럼 커버) | Must | PRD F15 |
| R03 | 이미지별 inference → F1-score 산출 (GT mask 필요) | Must | PRD F15 |
| R04 | HSMB × F1 scatter + PLCC, SROCC 산출 | Must | PRD F15 |
| R05 | RQ8 (HSMB ↔ F1 상관성 수준) 정량 답 도출 | Must | PRD §3 |

## 4. 입출력 정의

### 4.1 입력
| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| DL crack model 가중치 | .pt/.pth | 보유 중 (위치 확인 필요) | Y |
| 샘플 이미지 + GT mask | folder | 모션블러 수준 다양화 | Y |
| `src/hsmb/v1.py` | Python | HSMB 산출 | Y |

### 4.2 출력
| 항목 | 타입 | 설명 |
|------|------|------|
| `src/crack_detector/` | Python module | 모델 래퍼 + 추론 진입점 |
| `data/exp/e2_crack_f1.csv` | CSV | 이미지별 HSMB, F1, GT crack 통계 |
| `figures/e2_scatter_hsmb_f1.png` | PNG | scatter (논문용) |
| `00_doc/sp00/d0042_e2_correlation.md` | MD | 분석 리포트 |

## 5. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| GT mask 없는 이미지 | 분석 제외 + 리스트화 (Task B 협업자에게 요청 후보) |
| 모델 가중치 위치 불명 | F001-1 인벤토리 작업 시 함께 식별 |
| F1 산출 시 임계값 의존성 | IoU 0.5 기준 + threshold sweep 보조 |
| Task B 결과와 중복/충돌 | 자체 분석은 §V-E 보조 자료로 한정, 본문은 Task B 우선 |

## 6. 관련 Feature (plan.md 연결)

- 연결 Feature: `F002-3` — E2 HSMB-크랙검출 상관
- 의존 Feature: F001-1 (모델 위치 식별)
- 후속 의존: F004-2 (§V-E 작성 보조 자료)

## 7. 참고 자료

- PRD: `00_doc/sp00/d0001_prd.md` §3 RQ8, §5 F15
- 계획: `00_doc/sp00/d0002_plan.md` E002, S3
- 협업: KICT Task B 결과는 별도 (F004-1)

## 8. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
