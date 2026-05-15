# ootest Tutorial

> TDD RED — TC 코드 작성·반복 실행(PASS까지) 통합 테스트 스킬 | 최종 업데이트: 2026-04-29

## 개요

TDD RED 단계를 담당하는 스킬. TC 코드를 작성하고 pytest를 PASS까지 반복 실행하며, 결과를 `d{SP}0003_test.md`에 자동 등록한다. 5개 파트(A 정적분석/B E2E/C pytest/D oo모듈/E 런타임) 체계로 구성되며, Part E(런타임 검증)는 필수.

수정 대상: `tests/TC*.py`, `d{SP}0003_test.md` Part C

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ootest write [ID]` | TC 코드 생성(TDD RED) + d{SP}0003 Part C 등록 |
| `ootest write --all` | 미등록 TC 전체 코드 생성 |
| `ootest run` | 전체 테스트 (Part D 재스캔 자동 선행) |
| `ootest run this` | 직전 작업 파일 관련 TC 실행 |
| `ootest run --unit` | Part C pytest 반복 루프 |
| `ootest run --e2e` | Part B E2E 시나리오 (Playwright) |
| `ootest run --module` | Part D oo 모듈 전체 검증 |
| `ootest run --runtime` | Part E 런타임 검증 (import 테스트) — 필수 |
| `ootest run [ID]` | 특정 TC 실행 (실패 시 자동 재시도) |
| `ootest run [P0-P3]` | 우선순위별 실행 |
| `ootest checklist [domain]` | 요구사항 품질 체크리스트 생성 (ux/api/performance/security) |
| `ootest preview` | 테스트 계획 출력 |
| `ootest status` | 현재 상태 및 서브명령어 목록 |

## 주요 사용 예시

```bash
# TDD RED — TC 코드 작성 후 실패 확인
ootest write TC002-1.1

# 전체 테스트 실행
ootest run

# 단위 테스트만 (pytest 반복 루프)
ootest run --unit

# 런타임 에러 검증 (필수 — py_compile이 못 잡는 에러)
ootest run --runtime

# 직전 작업 파일 TC만 실행
ootest run this

# UX 요구사항 품질 체크리스트 생성
ootest checklist ux
```

## 워크플로우

**TDD RED (write)**:
```
1. d{SP}0003 시나리오 로드 (Part B)
2. test-engineer → TC 코드 생성 (pytest/playwright)
3. tests/sp{N}/TC[번호]_[모듈].py 저장
4. 실행 → 반드시 실패 확인 (pass 시 TC 재작성)
5. d{SP}0003 Part C 등록
6. oodev에 GREEN 신호 전달
```

**Part E 런타임 검증 (필수)**: py_compile·pylint가 감지 못하는 에러 검증
- StreamlitDuplicateElementKey (위젯 key 중복)
- ImportError (조건부 import)
- AttributeError (런타임 객체 접근)
- UnboundLocalError 위험 패턴 (→ oocheck로 대체 감지)

**완료 기준**: Part C 통과만으로 완료 아님 — A/B/C/D/E + 성능·보안 체크리스트 모두 필수.

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oodev` | TDD GREEN/REFACTOR 담당 |
| `oocheck` | Part A 정적분석 |
| `oofix` | 테스트 실패 이슈 수정 |
| `oofeature` | 단계 전환 연계 |
