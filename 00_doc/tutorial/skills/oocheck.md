# oocheck Tutorial

> Python/Flutter 자동 검증 및 이슈 등록 | 버전: v05 | 카테고리: core-dev

## §1 이유 (Reason)

코드 품질을 py_compile→pylint→mypy→pytest 검증 체인으로 자동 확인하고, 발견된 이슈를 d{SP}0004_todo.md에 자동 등록합니다.

## §2 빠른 시작 (Quick Start)

```bash
oocheck run
```

자동 감지: Python/Flutter 프로젝트 타입 인식 → 검증 체인 실행 → 이슈 등록

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oocheck run` | 전체 검증 실행 |
| `oocheck python` | Python 전용 |
| `oocheck flutter` | Flutter/Dart |
| `oocheck {dXXXX}` | 상세 문서 기반 |
| `oocheck fix` | 자동 수정 |

## §4 권장 흐름 (Recommended Flow)

1. 코드 작성 완료
2. `oocheck run` 실행 → 이슈 수집
3. d{SP}0004_todo.md 검토
4. `oocheck fix` → 자동 수정 가능 항목 처리
5. 다시 `oocheck run` → 확인

## §5 전체 명령어 (All Commands)

```
oocheck help
oocheck version
oocheck run [OPTIONS]
oocheck python [PATH]
oocheck flutter [PATH]
oocheck {dXXXX} [OPTIONS]
oocheck fix [ISSUE_ID]
```

## §6 상세 사용법 (Detailed Usage)

**검증 체인:**
1. py_compile → 구문 오류
2. pylint → 코드 스타일
3. mypy → 타입 힌트
4. pytest → 단위 테스트

## §7 실전 예시 (Real Examples)

```bash
oocheck run
oocheck d22034
oocheck fix W001
```

## §8 입출력 (Input/Output)

**입력:** Python/Dart 소스코드
**출력:** d{SP}0004에 이슈 등록

## §9 FAQ

**Q: 자동 수정이 안 되는 이슈는?**
A: ERROR/WARNING은 수동 검토 필요.

## §10 서브에이전트 (Sub-agents)

- code-error-checker, python-code-reviewer, flutter-analyzer

## §11 관련 스킬 (Related Skills)

- `oofix`, `oodev`, `ootest`, `ootodo`

---

**버전**: v05 | **카테고리**: core-dev | **업데이트**: 2026-04-14
