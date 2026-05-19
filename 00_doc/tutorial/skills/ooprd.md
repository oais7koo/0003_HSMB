# ooprd Tutorial

> PRD 생성·현행화·코드/문서 정합성 검증 스킬 | 최종 업데이트: 2026-04-29

## 개요

`d{SP}0001_prd.md`를 신규 생성하거나 현행화하고, 코드·문서 간 정합성을 검증하는 스킬. PRD가 없으면 템플릿 기반 신규 생성, 있으면 정합성 검증 모드로 동작. 발견된 불일치는 `d{SP}0004_todo.md`에 자동 등록.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ooprd run` | PRD 생성(없음) 또는 정합성 검증(있음) |
| `ooprd run this` | 직전 작업 관련 PRD 섹션 갱신 |
| `ooprd run --template [type]` | 템플릿 지정 생성 (streamlit/algorithm/agent) |
| `ooprd run --with-update` | PRD 생성 후 현행화 연속 실행 |
| `ooprd update` | 코드/현황 스캔 → PRD 변경분 반영 |
| `ooprd update --dry-run` | 변경 예정 내용 미리 출력 |
| `ooprd check` | checklist.md 기반 체크 |
| `ooprd check --fix` | PRD 최적화 (구 optimize) |
| `ooprd check --structure` | 구조 검증 (구 validate) |
| `ooprd clarify` | PRD 모호성 해소 (최대 5개 질문) |
| `ooprd section [N]` | 특정 섹션만 갱신 |
| `ooprd unitdev` | 전체 단위개발문서 현행화 |
| `ooprd unitdev [문서명]` | 특정 단위개발문서 현행화 |
| `ooprd template` | 템플릿 목록 조회 |
| `ooprd status` | 현재 상태 요약 |

## 주요 사용 예시

```bash
# 신규 PRD 생성 (없을 때)
ooprd run

# Streamlit 웹앱 전용 템플릿으로 생성
ooprd run --template streamlit

# 코드 변경 후 PRD 현행화
ooprd update this

# 모호한 요구사항 해소 (최대 5개 질문)
ooprd clarify

# PRD 구조 최적화
ooprd check --fix

# 단위개발문서 정합성 현행화
ooprd unitdev
```

## 워크플로우

**신규 생성 (PRD 없음)**:
1. 컨텍스트·코드베이스에서 파악 가능한 정보 추출
2. Must 섹션 누락 확인 → 1개씩 순차 질문 (skip 가능)
3. 템플릿 선택 → 초안 생성 → `d{SP}0001_prd.md` 저장

**정합성 검증 (PRD 있음)**:
1. PRD 로드 → 코드베이스·d0002·d0003·d0005·d0006 비교
2. 불일치 항목 → `d{SP}0004_todo.md` 자동 등록

**템플릿 종류**:
| 템플릿 | 용도 |
|--------|------|
| common (기본) | 범용 PRD |
| streamlit | Streamlit 웹앱 |
| algorithm | 알고리즘/ML 분석 |
| agent | 에이전트/CLI |

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `ooplan` | PRD → 구현 계획 생성 |
| `oodev` | 코드 구현 |
| `oofix` | 발견된 이슈 수정 |
| `oodoc` | 전체 문서 일괄 관리 |
