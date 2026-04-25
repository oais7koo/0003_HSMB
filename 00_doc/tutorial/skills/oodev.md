# oodev Tutorial

> TDD 개발: RED→GREEN→REFACTOR 사이클 자동화 | 버전: v08 | 카테고리: core-dev

## §1 이유 (Reason)

Test-Driven Development (TDD) 사이클을 자동화하여 안정적인 코드 개발을 보장합니다.

## §2 빠른 시작 (Quick Start)

```bash
oodev run
```

첫 실행: d{SP}0003_test.md 자동 생성 → RED 상태에서 시작

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oodev run` | TDD 사이클 실행 |
| `oodev test` | 테스트만 실행 |
| `oodev {dXXXX}` | 상세문서 기반 개발 |
| `oodev refactor` | 리팩토링 모드 |

## §4 권장 흐름 (Recommended Flow)

**RED (ootest):**
1. 테스트 작성
2. FAIL 확인

**GREEN (oodev):**
1. 최소 구현
2. PASS 확인

**REFACTOR (oodev):**
1. 코드 정리
2. PASS 유지

## §5 전체 명령어 (All Commands)

```
oodev help
oodev version
oodev run [OPTIONS]
oodev test
oodev {dXXXX} [OPTIONS]
oodev refactor
oodev coverage
```

## §6 상세 사용법 (Detailed Usage)

**프로젝트 타입 자동 감지:**
- Streamlit: {project}/pages/*.py
- Django: 03_{server}/apps/*/models.py
- FastAPI: 04_api_server/main.py
- General: 01_algorithm/*.py

## §7 실전 예시 (Real Examples)

```bash
cd {project}/pages
oodev run

cd 04_api_server
oodev d40341

oodev refactor --target card_processor.py
oodev coverage
```

## §8 입출력 (Input/Output)

**입력:** 테스트 파일, 상세문서
**출력:** 구현 코드, 테스트 리포트

## §9 FAQ

**Q: 테스트가 없으면?**
A: 첫 실행에서 d{SP}0003_test.md 자동 생성.

**Q: 기존 코드에 적용 가능?**
A: 네, `oodev refactor` 로 점진적 개선.

## §10 서브에이전트 (Sub-agents)

- streamlit-implementer, api-developer, test-writer, refactorer

## §11 관련 스킬 (Related Skills)

- `ootest`, `oocheck`, `oofix`, `oocommit`

---

**버전**: v08 | **카테고리**: core-dev | **업데이트**: 2026-04-14
