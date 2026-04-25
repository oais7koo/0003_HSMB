# oodoc_guide - 문서 생성 통합 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oo00_doc/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

프로젝트 핵심 문서(d0001~d0010) 생성 및 업데이트를 오케스트레이션하는 가이드입니다.

**목적**: 문서 자동화, 정합성 검증, 품질 최적화
**대상**: 00_doc/sp00/d0001~d0010 핵심 문서, .claude/skills/oo*/SKILL.md 스킬 문서
**출력**: 문서 생성/업데이트, 검증 리포트

## 2. 워크플로우

### 2.1 문서 생성 순서 (4 Phase)

```
Phase 1: 기획 문서
    d{SP}0001_prd (ooprd)
    d{SP}0002_plan (ooplan)
    ↓
Phase 2: 관리 문서
    d{SP}0004_todo (oocheck)
    d{SP}0010_history (oohistory)
    ↓
Phase 3: 기술 문서 (병렬 가능)
    d0006_db (oodb)
    d0005_lib (oolib)
    d{SP}0003_test (ootest)
    ↓
Phase 4: 사용자 문서
    d{SP}0008_user (oouser)
```

**의존 관계**:
- d{SP}0001_prd → d{SP}0002_plan, d{SP}0003_test, d{SP}0008_user
- d{SP}0004_todo → d{SP}0010_history
- d0006_db → d{SP}0003_test

### 2.2 문서 검증 (validate)

```
문서 이력 검증
    ↓
필수 섹션 확인 (문서별)
    ↓
참조 링크 검증 ([[링크]])
    ↓
마크다운 형식 검증
    ↓
스킬 정합성 검증 (.claude/skills/oo*/SKILL.md)
    ↓
보고서 출력
```

### 2.3 스킬 최적화 (optimize)

```
.claude/skills/oo*/SKILL.md 스캔 (19개 파일)
    ↓
병렬 에이전트 할당
    ↓
내용 최적화 (모호성 제거, 일관성 확보)
    ↓
용량 최적화 (중복 제거, 템플릿→참조)
    ↓
검증 및 저장
```

## 3. 상세 사용법

### 3.1 전체 문서 생성

```bash
# d0001~d0010 전체 생성/업데이트
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py run

# 필수 문서만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py run --required-only

# 특정 문서만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py run --doc d0004_todo

# 드라이런
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py run --dry-run
```

### 3.2 문서 검증

```bash
# 전체 검증
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py validate

# 스킬 정합성만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py validate --skill

# 문서만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py validate --doc

# 자동 수정
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py validate --fix
```

**검증 항목**:
| 카테고리 | 검증 내용 |
|----------|----------|
| 이력 | 이력 테이블 존재, 5개 제한 규칙 |
| 필수섹션 | 문서별 필수 섹션 |
| 참조 | [[링크]] 유효성 |
| 마크다운 | 테이블/코드블록 깨짐 |
| 스킬정합성 | oo*.md 간 참조, 관련 파일 누락 |

### 3.4 스킬 최적화

```bash
# .claude/skills/oo*/SKILL.md 전체 최적화
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py optimize

# 특정 스킬만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py optimize oocheck

# 내용 최적화만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py optimize --content

# 용량 최적화만
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py optimize --size
```

**최적화 규칙**:
- 삭제: 템플릿 섹션, 반복 가이드, 과도한 예제, 이모지
- 문체: 경어체→단답형, 장황→핵심
- 통합: 공통 패턴 → common_guide.md 참조

## 4. 사용 예시

### 예시 1: 프로젝트 초기화

```bash
# 1. 디렉토리 생성
mkdir -p doc v/{command,agent,template}

# 2. 기본 문서 생성
uv run python .claude/skills/ooprd/scripts/ooprd_run.py create
uv run python .claude/skills/ooplan/scripts/ooplan_run.py create
uv run python .claude/skills/oohistory/scripts/oohistory_run.py create

# 3. 전체 문서 생성
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py run
```

### 예시 2: 스킬 정합성 검증

```bash
# 스킬 간 참조 검증
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py validate --skill

# 결과:
# .claude/skills/ooflow/SKILL.md
#   ✅ 스킬 참조: oodev, oocheck... (9개 유효)
```

### 예시 3: 문서 이력 관리

```bash
# 검증 (5개 이력 규칙)
uv run python .claude/skills/oo00_doc/scripts/oodoc_run.py validate --fix

# 자동 수정: 오래된 이력 삭제, 최근 5개 유지
```

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oo00_doc/SKILL.md | 스킬 명세 |
| .claude/guides/common_guide.md | 공통 가이드라인 |
| CLAUDE.md | MIR 참조 |
| 00_doc/sp00/d0001~d0010 | 핵심 문서 |
| .claude/skills/oo*/SKILL.md | 스킬 문서 |

**에이전트**: Explore, task-executor, task-checker
**연동 스킬**: ooprd, ooplan, oocheck, oohistory, oolib, oodb, ootest, oouser

**문서 번호 체계**:
| 범위 | 용도 |
|------|------|
| d0001~d0010 | 공통 핵심 문서 |
| d10000~d19999 | SP 01 |
| d20000~d29999 | SP 02 |
