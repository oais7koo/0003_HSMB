# oofix Tutorial

> d{SP}0004_todo.md 이슈 자동 수정 (병렬 처리) | 버전: v01 | 카테고리: core-dev

## §1 이유 (Reason)

d{SP}0004_todo.md의 "현재 이슈" 섹션을 분석하고 자동 수정 가능한 항목을 병렬로 처리하여 빠르게 이슈를 해결합니다.

## §2 빠른 시작 (Quick Start)

```bash
oofix run
```

자동 감지: d{SP}0004 "현재 이슈" → 병렬 수정 → 검증

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oofix run` | 전체 이슈 자동 수정 |
| `oofix {ISSUE_ID}` | 특정 이슈만 수정 |
| `oofix preview` | 수정 내용 미리보기 |
| `oofix rollback` | 이전 상태 복원 |

## §4 권장 흐름 (Recommended Flow)

**Phase 1: 메인 (분석)**
1. d{SP}0004 읽기
2. "현재 이슈" 파싱
3. 자동 수정 가능 여부 판정

**Phase 2: 서브에이전트 (병렬 수정)**
- 최대 7개 동시 처리

**Phase 3: 메인 (검증)**
1. 수정 내용 검증
2. oocheck 재실행
3. 결과 업데이트

## §5 전체 명령어 (All Commands)

```
oofix help
oofix version
oofix run [OPTIONS]
oofix {ISSUE_ID}
oofix preview
oofix rollback
oofix status
```

## §6 상세 사용법 (Detailed Usage)

**자동 수정 가능 항목:**
- 미사용 import 제거
- 문법 오류 수정
- 간단한 타입 힌트 추가

**수동 검토 필요:**
- 논리 오류
- 보안 이슈
- 아키텍처 결정

## §7 실전 예시 (Real Examples)

```bash
oocontext set 02
oofix run
oofix R001
oofix preview
oofix status
oofix rollback
```

## §8 입출력 (Input/Output)

**입력:** d{SP}0004, 소스코드
**출력:** 수정된 코드, 로그, 리포트

## §9 FAQ

**Q: 자동 수정 실패 시?**
A: oofix와 ootodo의 역할 구분. 자동 수정 불가는 수동 검토.

**Q: 여러 이슈 동시 수정 시 충돌?**
A: 파일 잠금으로 충돌 방지.

## §10 서브에이전트 (Sub-agents)

- code-error-fixer, python-code-reviewer, flutter-analyzer, validation-specialist

## §11 관련 스킬 (Related Skills)

- `oocheck`, `oodev`, `ootodo`, `oocommit`

---

**버전**: v01 | **카테고리**: core-dev | **업데이트**: 2026-04-14
