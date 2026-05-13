---
name: oodb
description: "DB 수정 및 최적화 스킬 'oodb', 'DB 검증', 'DB 설계', '마이그레이션', '스키마' 등을 요청할 때 사용한다"
metadata:
  version: "v05"
  category: "doc-env"
---

# oodb - DB 수정 및 최적화 스킬

> 공통 원칙: `.claude/guides/common_guide.md` 참조

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | DB 문제 발견→기록→수정 3단계 워크플로우 (Python/Flutter 지원) |
| **하는 것** | 스키마 검증, 마이그레이션 생성, DB 이슈 수정, d{SP}0004 등록 |
| **하지 않는 것** | 코드 로직 수정(→oofix), oo 모듈 수정(→oolib), 의존성 관리(→oouv) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (DB 파일, 마이그레이션) / 외부 DB 서버 자동 접속 안 함 |
| **수정 대상** | DB 스키마 파일, 마이그레이션 파일, `d{SP}0004_todo.md` |
| **실행 레벨** | [반자동] — 스키마 변경 확인 후 실행 |
| **에이전트 호환** | 범용 — 파일 기반 마이그레이션 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v05 2026-04-19 — validate/optimize → check/check --fix 통합
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 개요

DB 문제점 발견 -> 기록 -> 수정하는 3-Phase 워크플로우.

| 구분 | 문서 | 용도 |
|------|------|------|
| `oodb help` | 서브명령어 목록 표시 | 터미널 |
| `oodb version` | 스킬 버전 정보 (v04) |
| 에러/이슈 | d{SP}0004_todo.md | 이 스킬이 처리 |
| 신규 개발 | d{SP}0002_plan.md | 스키마 확장 |

**Phase 흐름**: check(코드-DB) -> 분석(DB) -> d0004 기록 -> 수정 -> 해결 이동 -> 미해결 0개 확인

**DB 유형**: SQLite, PostgreSQL, MySQL | **위치**: `db/*.db`

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oodb status` | 서브명령어 리스트, DB 상태/미해결 이슈 |
| `oodb check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oodb show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oodb add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oodb run` | **check + 분석 + 수정** (3-Phase 통합) |
| **`oodb run this`** | **직전 작업 DB 분석** (→ common_guide.md §9) |
| `oodb check` | SQL 쿼리 스키마 검증만 (EXPLAIN) |
| `oodb check --fix` | run + 최적화 |
| `oodb doc` | d0006_db.md 문서화 |
| `oodb design` | **DB 설계**: PRD/Plan 기반 테이블/컬럼 설계 |
| `oodb dev` | **DB 개발**: 설계된 스키마 마이그레이션 (백업 필수) |

**옵션**: `--db [path]`, `--table [name]`, `--dry-run`, `--path [code_path]`, `--sp [num]`

실행: `uv run python .claude/skills/oodb/scripts/oodb_run.py [args]`

## 3. 서브프로젝트 DB 문서 규칙

**DB는 공통 사용** -> 모든 SP에서 전체 DB를 분석하되, SP별 사용 현황을 명시

| SP | 출력 문서 | 내용 |
|----|----------|------|
| 00 | d0006_db.md | 전체 스키마, ERD, 모든 테이블/컬럼 |
| !=00 | d{SP}0006_db.md | 전체 스키마 + SP별 사용 현황 표기 |

### 사용 판정 기준

| 판정 | 조건 |
|------|------|
| 사용 | SP 코드에서 SELECT/INSERT/UPDATE/DELETE 참조 |
| 미사용 | SP 코드에서 참조 없음 (다른 SP 전용) |
| 간접 | FK 관계로 간접 참조 (JOIN 등) |

## 4. 병렬 처리

| Agent | 영역 | 에이전트 | 모델 |
|-------|------|----------|------|
| 1 | 스키마/FK | task-executor | sonnet |
| 2 | 인덱스 | data-analyst | sonnet |
| 3 | 쿼리 | task-executor | sonnet |
| 4 | 데이터 | data-analyst | sonnet |

**병렬화 기준**: INTEGRITY 순차 (의존성), FK/INDEX/QUERY/DATA 병렬 (테이블별 독립)

## 5. 워크플로우

### 5.1 run (3-Phase 통합)

**Phase 1 - check**:
- Python 코드 내 SQL 쿼리 추출 -> EXPLAIN 스키마 검증 -> 오류 시 d0004 등록

| 오류 유형 | 심각도 |
|----------|--------|
| 테이블 없음 | CRITICAL |
| 컬럼 없음 | CRITICAL |
| 조인 오류 | CRITICAL |
| 타입 불일치 | WARNING |

**Phase 2 - 분석**: PRAGMA integrity_check -> foreign_key_check -> 스키마/인덱스 분석

**Phase 3 - 수정**: 에이전트 병렬 수정 -> 검증 및 문서 반영

### 5.2 design (DB 설계)

PRD/Plan 문서와 코드를 분석하여 DB 스키마를 설계하고 문서화한다.

**워크플로우**: 문서 분석 -> 스키마 설계 -> 문서 출력

**설계 테이블 표기 규칙**:
| 구분 | 표기 | 설명 |
|------|------|------|
| 구현 완료 | (없음) | 실제 DB에 존재 |
| 설계 중 | `(설계)` | 미구현, 마이그레이션 필요 |
| 삭제 예정 | `(삭제예정)` | 향후 제거 대상 |

### 5.3 dev (DB 마이그레이션)

설계된 스키마를 실제 DB에 반영한다. 데이터 보존을 위해 백업 필수.

**백업 정책**:
| 항목 | 규칙 |
|------|------|
| 위치 | `db/backup_YYYYMMDD-HHMM.db` |
| 보관 | 최근 5개 유지 (자동 정리) |
| 복원 | `oodb restore --backup [filename]` |

### 5.4 check --fix

run + 인덱스/쿼리/정규화 최적화 -> `[OPT]` 태그로 d0004 등록

## 6. d0004 연동

**이슈 범위**: `db/*.db`, 스키마/쿼리 관련만
**ID 규칙**: `D` prefix + `[FIX]`/`[OPT]` 태그
**흐름**: 발견 -> d0004(대기) -> 수정(진행중) -> 해결 이동

## 7. 최적화 체크리스트

| 영역 | 항목 |
|------|------|
| 인덱스 | 조회 컬럼, 복합, 미사용 제거 |
| 쿼리 | N+1, JOIN, SELECT *, EXPLAIN |
| 스키마 | 정규화, 타입, NULL, FK |
| 데이터 | 미사용, 고아, 중복 |

## 8. 완료 조건

**run**: 미해결 0개 + `PRAGMA integrity_check` ok + `foreign_key_check` 통과 + 문서 반영
**check --fix**: run 조건 + `[OPT]` 0개

## 9. SQL 템플릿

```sql
SELECT name FROM sqlite_master WHERE type='table';
SELECT name, tbl_name FROM sqlite_master WHERE type='index';
PRAGMA integrity_check; PRAGMA foreign_key_check;
```

## 10. 관련 문서

00_doc/d{SP}0004_todo.md (이슈), 00_doc/sp00/d0006_db.md (DB 구조)

> **관련 명령어**: `.claude/commands/sc/analyze.md` | `.claude/commands/sc/improve.md`

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 스키마 분석 | `Explore` | haiku | O |
| 마이그레이션 | `task-executor` | sonnet | O |
| DB 검증 | `task-checker` | sonnet | - |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

