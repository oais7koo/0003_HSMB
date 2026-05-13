---
template: d_{SP}0003_test
purpose: SP별 테스트 케이스 문서 생성용 (d{SP}0003_test.md)
usage: oodev INIT 또는 ootest write 실행 시 자동 생성. {SP}→SP번호(예:50), {SP_NAME}→SP명, {DATE}→오늘날짜 치환
---

# 테스트 문서: {SP_NAME} (SP{SP_FULL})

## 문서이력관리
- v01 {DATE} — 초기 생성 (oodev INIT, PRD/plan 기반)

> 기반: d{SP}0001_prd.md, d{SP}0002_plan.md | 가이드: `d0003_test.md`(공통)

---

## Part A. 정적 분석

> oodev INIT 자동 생성 — 고정 항목 (변경 없음)

| ID | 항목 | 상태 |
|----|------|------|
| A001 | py_compile 오류 없음 | ⬜ |
| A002 | import 순환 참조 없음 | ⬜ |
| A003 | 환경변수 누락 시 ValueError 발생 확인 | ⬜ |

---

## Part B. E2E 시나리오

> PRD Must→P0, Should→P1 기반 도출 | oodev INIT 생성

| ID | 우선순위 | 시나리오 | 상태 |
|----|---------|---------|------|
| B001 | P0 | (시나리오 기술) | ⬜ |

---

## Part C. 단위 테스트 (pytest)

> `ootest write [TC ID]`로 TC 코드 작성 후 등록 (`[x]`→완료)

### TC 목록

| TC ID | Task | 파일 | 설명 | 상태 |
|-------|------|------|------|------|
| - | - | - | (ootest write 실행 시 자동 등록) | ⬜ |

### 최종 테스트 결과

> `ootest result` 실행 시 자동 갱신

| TC ID | 기능명 | 결과 | 실패 원인 | 최종 실행일 |
|-------|--------|:----:|----------|:----------:|
| - | - | - | - | - |

---

## Part D. oo 모듈 검증

> SP{SP_FULL}: d0003_test.md Part D 참조
> (oo 모듈 직접 사용 시 `ootest run --module`로 자동 스캔)

---

## Part E. 런타임 검증 (import 테스트)

> 필수 실행 | `ootest run --runtime`

| ID | 검증 대상 | 상태 |
|----|----------|------|
| E001 | 전체 모듈 import 오류 없음 | ⬜ |
| E002 | StreamlitDuplicateElementKey 없음 (Streamlit 사용 시) | ⬜ |

---

## 최종 결과 요약

> `ootest result` 실행 시 자동 갱신 | 마지막 갱신: -

| Part | 전체 | PASS | FAIL | SKIP | 실행일 |
|------|:----:|:----:|:----:|:----:|:------:|
| A. 정적 분석 | - | - | - | - | - |
| B. E2E 시나리오 | - | - | - | - | - |
| C. 단위 테스트 | - | - | - | - | - |
| D. oo 모듈 | - | - | - | - | - |
| E. 런타임 검증 | - | - | - | - | - |
| **합계** | - | - | - | - | - |
