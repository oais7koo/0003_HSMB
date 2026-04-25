# oohelp Tutorial

> oo 스킬 카탈로그 및 도움말 조회 | 버전: v02 | 카테고리: meta-util

## §1 이유 (Reason)

47개 이상의 oo 스킬, SC 명령어, 에이전트에 대한 도움말을 빠르게 조회합니다.

## §2 빠른 시작 (Quick Start)

```bash
oohelp show oodev
```

oodev 스킬 상세 정보 표시

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oohelp list` | 전체 스킬 목록 |
| `oohelp show {SKILL}` | 스킬 상세 정보 |
| `oohelp search {KEYWORD}` | 키워드로 검색 |
| `oohelp category {CAT}` | 카테고리별 필터 |

## §4 권장 흐름 (Recommended Flow)

1. 작업 시작 전: `oohelp search {작업종류}`
2. 스킬 미숙할 때: `oohelp show {SKILL}`
3. 카테고리 탐색: `oohelp category core-dev`
4. 전체 도움말: `oohelp list`

## §5 전체 명령어 (All Commands)

```
oohelp help
oohelp version
oohelp list [OPTIONS]
oohelp show {SKILL}
oohelp search {KEYWORD}
oohelp category {CATEGORY}
oohelp command {COMMAND}
```

## §6 상세 사용법 (Detailed Usage)

**스킬 카테고리:**
- `core-dev` — 개발 핵심
- `doc-env` — 문서/환경
- `meta-util` — 메타/유틸
- `content` — 콘텐츠

**검색 예시:**
- "database" → oodb
- "test" → ootest, oocheck
- "git" → oocommit

## §7 실전 예시 (Real Examples)

```bash
oohelp list
oohelp search development
oohelp show oodev
oohelp category core-dev
oohelp command improve
oohelp search python
```

## §8 입출력 (Input/Output)

**입력:** 스킬명 또는 키워드
**출력:** 스킬 목록, 상세 정보, 검색 결과

## §9 FAQ

**Q: 스킬명을 모르면?**
A: `oohelp search {작업}` 로 관련 스킬 검색.

**Q: 모든 oo 스킬을 한번에?**
A: `oohelp list` 실행.

**Q: SC 명령어와 oo 스킬 차이?**
A: SC는 통합 명령, oo는 전문 스킬.

## §10 서브에이전트 (Sub-agents)

- catalog-manager, search-engine

## §11 관련 스킬 (Related Skills)

- `oostart`, `oohelp`, `oocontext`, `oonext`

---

**버전**: v02 | **카테고리**: meta-util | **업데이트**: 2026-04-14
