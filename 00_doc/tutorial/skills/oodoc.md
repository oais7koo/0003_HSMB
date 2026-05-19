# oodoc Tutorial

> d0001~d0010 문서 생성·업데이트·최적화·검증 자동화 | 최종 업데이트: 2026-04-29

## 개요

프로젝트의 핵심 문서(PRD·계획·테스트·TODO·이력 등) d0001~d0010을 체계적으로 생성·현행화·최적화하는 오케스트레이터 스킬. SP별 문서 현황 조회, 이력 초과 행 자동 제거, 정합성 검사까지 포함한다.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oodoc run` | d0001~d0010 문서 생성/업데이트 |
| `oodoc run --doc [문서ID]` | 특정 문서만 생성/업데이트 |
| `oodoc run --dry-run` | 실제 수정 없이 예정 변경 출력 |
| `oodoc create [문서ID]` | 특정 문서 신규 생성 |
| `oodoc update this` | 직전 작업 영향 문서 자동 업데이트 |
| `oodoc update [--scope 범위]` | 코드 작업 후 관련 문서 자동 탐지·업데이트 |
| `oodoc check [SP번호]` | 품질+정합성 통합 검사 |
| `oodoc check --fix [문서ID]` | 문서 최적화 (구 optimize) |
| `oodoc clear` | 이력 초과 행 제거 (기본 5개 유지) |
| `oodoc clear --keep N` | N개 유지하며 이력 정리 |
| `oodoc list [--sp N]` | SP별 문서 현황 조회 (존재/미생성 상태) |
| `oodoc gen [--sp N]` | SP별 미생성 문서를 빈 템플릿으로 일괄 생성 |
| `oodoc numbering` | 문서 번호 체계(SSOT) 조회 |
| `oodoc explain [대상]` | 코드/함수/모듈 설명 생성 |
| `oodoc status` | 서브명령어 리스트 및 현재 상태 |

## 주요 사용 예시

```bash
# 현재 SP의 전체 문서 생성/업데이트
oodoc run

# 코드 변경 후 관련 문서 자동 업데이트
oodoc update this

# 이력 5개 초과 행 정리 (전체 범위: 00_doc + skills + guides)
oodoc clear

# SP04 문서 현황 확인
oodoc list --sp 4

# PRD 문서 품질 최적화
oodoc check --fix d40001

# SP 전체 정합성 검사
oodoc check 4
```

## 워크플로우

1. `oodoc run` — PRD 로드 → 10개 문서 존재 확인 → 없는 것 생성, 있는 것 현행화
2. `oodoc update this` — 직전 수정 파일 감지 → 영향받는 문서 자동 탐지 → 업데이트
3. `oodoc check` — 품질 검사(구조·크기·내용) + 정합성 검사(교차 비교) → 이슈 리포트
4. `oodoc clear` — `00_doc/**/d*.md` + skills + guides 전체에서 이력 5개 초과 행 제거

**관련 문서 9종**: d{SP}0001 PRD / 0002 구현계획 / 0003 테스트 / 0004 TODO / 0005 라이브러리 / 0006 DB / 0009 환경 / 0010 이력

## 관련 스킬

- `ooprd` — PRD 전담 생성/검증
- `ooplan` — 구현 계획 전담
- `ootodo` — TODO 관리
- `oohistory` — 이력 아카이브
- `ooenv` — 환경 현황(d0009)
