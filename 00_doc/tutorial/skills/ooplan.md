# ooplan Tutorial

> PRD 기반 구현 계획(Epic/Feature/Task) 수립 스킬 | 최종 업데이트: 2026-04-29

## 개요

PRD를 읽어 Epic→Feature→Task로 분해하고 `d{SP}0002_plan.md`를 생성·현행화하는 스킬. 아키텍처·API·DB·워크플로우 설계도 포함. Streamlit 프레임워크 자동 감지 시 3계층(PRD→Plan→단위개발문서) 구조 적용.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ooplan run` | PRD → Task 완전 생성 (기본값) |
| `ooplan run epic` | PRD → Epic까지만 생성 |
| `ooplan run feature` | PRD → Feature까지 생성 |
| `ooplan run task` | PRD → Task까지 생성 (run과 동일) |
| `ooplan run this` | 직전 작업 관련 계획 업데이트 |
| `ooplan update` | 현재 코드/현황 스캔 → Plan 변경분 반영 |
| `ooplan update --dry-run` | 변경 예정 내용 미리 출력 |
| `ooplan check --fix` | Plan 검토·개선 (구 optimize) |
| `ooplan sync` | PRD 변경사항 동기화 |
| `ooplan detail` | 실행 전 상세 설계 (→oodev 연계) |
| `ooplan design [대상]` | 시스템/API/컴포넌트/DB 설계 |
| `ooplan workflow [prd]` | PRD→워크플로우 생성 |
| `ooplan status` | 현재 상태 및 서브명령어 목록 |

## 주요 사용 예시

```bash
# PRD 기반 전체 계획 생성
ooplan run

# Epic만 먼저 생성 후 Feature 추가
ooplan run epic
ooplan run feature

# PRD 변경 후 Plan 동기화
ooplan sync

# 생성된 Plan 검토·최적화
ooplan check --fix

# 코드 변경 후 plan.md 현행화
ooplan update this

# 아키텍처 설계
ooplan design --type architecture
```

## 워크플로우

1. PRD 로드 → Plan 생성에 필요한 항목 추출
2. 누락 정보 1개씩 순차 질문 (skip 입력 시 AI 판단으로 대체)
3. Epic 도출 → Feature 분리 → Task 세분화
4. `d{SP}0002_plan.md` 저장
5. 완료 후 `oofeature needed` 실행 권장 — 미착수 Feature 확인

**Plan 분해 체계**:
```
PRD → Epic(도메인) → Feature(기능) → Task(구현) → TC(테스트)
```

**8절 상세 문서 현황**: `ooplan sync` 또는 `ooplan run` 실행 시 `00_doc/sp{N}/`를 스캔해 plan.md 8.2절 자동 갱신 (패턴: `*_상세기획_*.md` 등).

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `ooprd` | PRD 입력 소스 |
| `oofeature` | 상세 문서 생성·단계 전환 |
| `oodev` | Task 기반 구현 |
| `oocheck` | 코드 검증 |
