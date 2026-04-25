# oohistory_guide - 완료 항목 이력 이동 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oohistory/SKILL.md` | 공통: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 1. 개요

d{SP}0004_todo.md의 완료 항목을 d{SP}0010_history.md로 이동하고 자동 요약하는 가이드입니다.

**목적**: 완료 항목 아카이브, 히스토리 관리, 토큰 최적화
**대상**: 00_doc/d{SP}0004_todo.md (해결된 이슈 섹션)
**출력**: 00_doc/d{SP}0010_history.md

**컨텍스트 적용**:
- SP=00: d0004 → d0010
- SP≠00: d{SP}0004 → d{SP}0010 AND d0004 → d0010 (병행)

## 2. 워크플로우

### 2.1 기본 흐름

```
d{SP}0004_todo.md "해결된 이슈" 스캔
    ↓
태그 추론 (키워드 기반)
    ↓
d{SP}0010_history.md 등록
    ↓
토큰 체크 (>20K시 요약)
    ↓
d{SP}0004에서 삭제
```

### 2.2 자동 요약 (토큰 >20K)

```
현재 토큰: 25,000
    ↓
목표: 10,000
    ↓
FIFO 방식: 오래된 이력부터 1줄 요약
    ↓
"## 아카이브 요약" 섹션으로 이동
```

**보존 규칙**: 최근 30일은 상세 유지

## 3. 상세 사용법

### 3.1 기본 실행

```bash
# 완료 항목 이동
uv run python .claude/skills/oohistory/scripts/oohistory_run.py run

# 서브프로젝트 지정
uv run python .claude/skills/oohistory/scripts/oohistory_run.py run --sp 02

# 상태 조회
uv run python .claude/skills/oohistory/scripts/oohistory_run.py status
```

### 3.2 태그 추론 규칙

| 키워드 | 태그 |
|--------|------|
| error, fix, bug | BUGFIX |
| security, 보안 | HOTFIX |
| update, 버전 | UPDATE |
| feature, 기능 | FEATURE |
| refactor, optimize | IMPROVE |
| doc, 문서 | DOCS |
| (없음) | MISC |

### 3.3 d0010 형식

```markdown
#### YYYY-MM-DD - [태그] [제목]
- 파일: 경로 | 원인: 내용 | 해결: 방법
```

**태그 종류**: HOTFIX, BUGFIX, UPDATE, FEATURE, IMPROVE, DOCS, REFACTOR, CONFIG, MISC

## 4. 사용 예시

### 예시 1: 표준 테이블 형식

**d0004_todo.md 입력**:
```markdown
## 해결된 이슈

| ID | 발생일 | 태그 | 내용 | 해결일 | 해결방법 |
|----|--------|------|------|--------|----------|
| A001 | 2026-02-01 | [BUGFIX] | oo/config.py - 중복 import | 2026-02-03 | import 정리 |
```

**d0010_history.md 출력**:
```markdown
#### 2026-02-03 - [BUGFIX] oo/config.py - 중복 import
- 파일: oo/config.py | 원인: 중복 import | 해결: import 정리
```

### 예시 2: 마크다운 목록 (태그 추론)

**d0004_todo.md 입력**:
```markdown
## 해결된 이슈

- 2026-02-02: bizreg.py 에러 수정 완료 (E0606)
```

**태그 추론**: "에러 수정" → BUGFIX

**d0010_history.md 출력**:
```markdown
#### 2026-02-02 - [BUGFIX] bizreg.py E0606
- 파일: bizreg.py | 원인: 변수 미할당 | 해결: 초기화 추가
```

### 예시 3: 자동 요약 (>20K)

```bash
# 현재 d0010_history.md: 25,000 토큰

uv run python .claude/skills/oohistory/scripts/oohistory_run.py run

# 결과:
# - 오래된 이력 1줄 요약 (2025년 이전)
# - "## 아카이브 요약" 섹션으로 이동
# - 최종: 10,000 토큰
```

**아카이브 요약 예시**:
```markdown
## 아카이브 요약

- 2025-01~06: BUGFIX 15건, FEATURE 8건, IMPROVE 12건
```

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oohistory/SKILL.md | 스킬 명세 |
| 00_doc/d{SP}0004_todo.md | 입력 (해결된 이슈) |
| 00_doc/d{SP}0010_history.md | 출력 (변경 이력) |
| .claude/skills/oocontext/SKILL.md | 컨텍스트 시스템 |
| .claude/skills/ootodo/references/guide.md | TODO 형식 표준 |

**에이전트**: Explore, task-executor, task-checker

**타이밍**: 해결 후 1~2주 안정성 확인 후 이동 권장
