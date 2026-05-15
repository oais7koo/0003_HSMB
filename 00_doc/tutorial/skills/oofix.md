# oofix Tutorial

> d{SP}0004_todo.md 이슈 자동 수정 (병렬 처리) | 최종 업데이트: 2026-04-29

## 개요

`d{SP}0004_todo.md`의 "현재 이슈" 섹션(S/T/W 이슈)을 서브에이전트 병렬 처리로 자동 수정하는 스킬. 3단계(분석→병렬수정→검증) 자동 실행. 수정 완료 이슈는 `d{SP}0010_history.md`로 이동. Python + Flutter/Dart 다중 언어 지원.

**oofix vs ootodo 구분**: oofix는 oocheck가 발견한 코드 에러(S/T/W)를 처리 / ootodo는 사용자 커스텀 Todo를 처리.

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oofix run` | 전체 이슈 자동 수정 (병렬) |
| `oofix run this` | 직전 작업 파일 이슈 수정 |
| `oofix run [대상]` | 특정 이슈/파일/카테고리 수정 |
| `oofix improve [대상]` | d0004 이슈 없이 품질/성능/보안 개선 |
| `oofix preview` | 수정 미리보기 |
| `oofix verify` | 수정 검증 |
| `oofix rollback` | 롤백 |
| `oofix status` | 이슈 현황 |

## 주요 사용 예시

```bash
# 전체 이슈 자동 수정
oofix run

# 직전 작업 파일만 수정
oofix run this

# 수정 전 미리보기
oofix preview

# 품질/성능 개선 (이슈 없어도 실행 가능)
oofix improve --focus quality
oofix improve --focus performance
oofix improve --focus security
```

## 워크플로우

```
Phase 1 (메인 — 분석):
  d{SP}0004 파싱 → False Positive 필터 → 우선순위 정렬 → 병렬 계획

Phase 2 (서브에이전트 — 병렬 수정):
  우선: oo/__init__.py export, E0102 중복 정의 (순차)
  병렬: Agent 1~3 영역별 수정 → py_compile 검증

Phase 3 (메인 — 검증):
  수정 검증 → d{SP}0004 업데이트 → d{SP}0010 이력 기록
```

**Python 주요 이슈 코드**:
| 코드 | 이슈 | 수정 방향 |
|------|------|----------|
| E0611 | export 누락 | `__init__.py` import 추가 |
| E0102 | 중복 정의 | 첫 번째만 유지 |
| E0606 | 변수 미할당 | 초기화/로직 수정 |
| W0611/W0612 | 미사용 import/변수 | 삭제 또는 `_` prefix |

**동적 sys.path [WARNING]**: `sys.path.insert/append` 패턴 발견 시 [WARNING] 등록 후 정적 import 마이그레이션 권장. 수정 후 반드시 `ootest run --runtime`으로 import 검증.

**검증**: Python → `uv run python -m py_compile <파일>` / Flutter → `dart analyze`

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oocheck` | 이슈 발견 (oofix의 입력) |
| `ootodo` | 커스텀 Todo 처리 |
| `ootest` | 수정 후 테스트 검증 |
| `oocommit` | 수정 완료 후 커밋 |
