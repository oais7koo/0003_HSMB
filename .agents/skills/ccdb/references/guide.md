# oodb_guide - DB 수정 및 최적화 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oodb/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

데이터베이스 문제 발견, 기록, 수정을 3-Phase로 처리하는 워크플로우 가이드입니다.

**목적**: DB 무결성 검증, 스키마 정합성 확보, 쿼리 최적화
**대상**: db/*.db (SQLite, PostgreSQL, MySQL 지원)
**출력**: 00_doc/d{SP}0004_todo.md (이슈), 00_doc/sp00/d0006_db.md (DB 구조)

## 2. 워크플로우

### 2.1 Phase 1: validate (코드-DB 정합성)

```
Python 코드에서 SQL 쿼리 추출
    ↓
EXPLAIN 쿼리로 스키마 검증
    ↓
오류 발견 시 d{SP}0004 등록 (CRITICAL)
```

**검증 오류 유형**:
| 유형 | 심각도 | 예시 |
|------|--------|------|
| 테이블 없음 | CRITICAL | `no such table: community_posts` |
| 컬럼 없음 | CRITICAL | `no such column: user_id` |
| 조인 오류 | CRITICAL | FK 불일치 |
| 타입 불일치 | WARNING | INT vs TEXT |

### 2.2 Phase 2: 분석

```
PRAGMA integrity_check (DB 무결성)
    ↓
PRAGMA foreign_key_check (FK 검증)
    ↓
스키마/인덱스 분석
    ↓
d{SP}0004 등록 → 병렬 처리 계획
```

### 2.3 Phase 3: 수정

```
병렬 에이전트 할당 (테이블별/이슈별)
    ↓
수정 실행
    ↓
재검증 (integrity_check, foreign_key_check)
    ↓
d{SP}0004 이동 (대기→해결)
    ↓
d0006_db.md 업데이트
```

## 3. 상세 사용법

### 3.1 기본 검증

```bash
# Phase 1~3 통합 실행
uv run python .claude/skills/oodb/scripts/oodb_run.py run

# 코드-DB 정합성만 검증 (수정 없음)
uv run python .claude/skills/oodb/scripts/oodb_run.py validate

# 특정 테이블만
uv run python .claude/skills/oodb/scripts/oodb_run.py run --table users
```

### 3.2 DB 설계

```bash
# PRD/Plan 기반 스키마 설계
uv run python .claude/skills/oodb/scripts/oodb_run.py design

# 서브프로젝트 지정
uv run python .claude/skills/oodb/scripts/oodb_run.py design --sp 02
```

**설계 출력**: d{SP}0006_db.md에 (설계) 꼬리표 포함 테이블 추가

### 3.3 DB 마이그레이션

```bash
# 설계된 스키마 반영 (백업 자동)
uv run python .claude/skills/oodb/scripts/oodb_run.py dev

# 특정 테이블만
uv run python .claude/skills/oodb/scripts/oodb_run.py dev --table posts

# 드라이런 (미리보기)
uv run python .claude/skills/oodb/scripts/oodb_run.py dev --db db/main.db --dry-run
```

**백업 위치**: `db/backup_YYYYMMDD-HHMM.db` (최근 5개 유지)

### 3.4 최적화

```bash
# run + 인덱스/쿼리 최적화
uv run python .claude/skills/oodb/scripts/oodb_run.py optimize
```

**최적화 항목**:
- 인덱스: 조회 컬럼, 복합 인덱스, 미사용 인덱스 제거
- 쿼리: N+1 문제, JOIN 최적화, SELECT * 제거
- 스키마: 정규화, 타입 최적화, NULL 처리, FK 정리
- 데이터: 미사용/고아 레코드 삭제, 중복 제거

## 4. 사용 예시

### 예시 1: 코드-DB 정합성 검증

```bash
# 코드 내 SQL 쿼리 검증
uv run python .claude/skills/oodb/scripts/oodb_run.py validate --path 02_1st_server/pages

# 결과: 테이블/컬럼 누락 감지 → d20004 등록
```

### 예시 2: DB 설계 및 마이그레이션

```bash
# 1. PRD 기반 스키마 설계
uv run python .claude/skills/oodb/scripts/oodb_run.py design --sp 02

# 2. d20006_db.md 확인 (posts 테이블 (설계) 꼬리표)

# 3. 마이그레이션 실행
uv run python .claude/skills/oodb/scripts/oodb_run.py dev --table posts

# 백업: db/backup_20260205-1430.db
# 완료: (설계) 꼬리표 제거
```

### 예시 3: SP별 DB 문서화

```bash
# SP=00: 전체 DB 스키마
uv run python .claude/skills/oodb/scripts/oodb_run.py doc
# → d0006_db.md: 전체 테이블/컬럼

# SP=02: 전체 DB + 사용 현황 표시
uv run python .claude/skills/oodb/scripts/oodb_run.py doc --sp 02
# → d20006_db.md: 전체 스키마 + ✅사용/❌미사용 표기
```

**사용 현황 표기**:
```markdown
| 테이블명 | SP 사용 | 설명 |
|----------|---------|------|
| senior_users | ✅ 사용 | 회원 정보 |
| admin_logs | ❌ 미사용 | 관리자 로그 (SP=00 전용) |
```

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oodb/SKILL.md | 스킬 명세 |
| 00_doc/d{SP}0004_todo.md | DB 이슈 추적 |
| 00_doc/sp00/d0006_db.md | DB 구조 문서 |
| 00_doc/d{SP}0006_db.md | SP별 DB 문서 |
| .claude/skills/oolib/SKILL.md | 코드 수정 스킬 |

**에이전트**: task-executor, data-analyst, task-checker
**도구**: sqlite3, PRAGMA, EXPLAIN, Sequential MCP

**SQL 참조**:
```sql
-- 테이블 목록
SELECT name FROM sqlite_master WHERE type='table';

-- 인덱스 목록
SELECT name, tbl_name FROM sqlite_master WHERE type='index';

-- 무결성 검증
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```
