# oocontext_guide - 서브프로젝트 컨텍스트 관리 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oocontext/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

서브프로젝트별 문서 컨텍스트를 설정하여 모든 oo 스킬이 적절한 SP 문서를 참조하도록 하는 가이드입니다.

**목적**: SP별 문서 범위 분리, 컨텍스트 자동 감지
**대상**: 00_doc/d{SP}0001~d{SP}0010 문서
**출력**: 세션 컨텍스트 설정 (SP 번호)

**SP 번호 체계**:
- SP=00: 공통 (d0001~d9999)
- SP=01: 01_algorithm (d10001~d19999)
- SP=02: plan_srv (d20001~d29999)
- SP=03~05: 예약 (d30001~d59999)

## 2. 워크플로우

### 2.1 컨텍스트 설정

```
컨텍스트 결정 (우선순위)
    ↓
1. --sp N 옵션 (최우선)
    ↓
2. 세션 컨텍스트 (oocontext N)
    ↓
3. CWD 감지 (폴더명 패턴)
    ├─ */01_*/* 또는 01_* → SP=01
    ├─ */02_*/* 또는 02_* → SP=02
    └─ 그 외 → SP=00 (기본)
    ↓
문서 범위 결정
    ├─ SP=00: d0001~d9999
    ├─ SP=01: d10001~d19999
    └─ SP=02: d20001~d29999
```

### 2.2 문서 등록 규칙

```
oo 스킬 실행 (oocheck, oodev 등)
    ↓
현재 SP 확인
    ├─ SP=00: d0004_todo.md에만 등록
    └─ SP≠00: d{SP}0004_todo.md에만 등록
    ↓
oofix 예외
    └─ SP≠00: d{SP}0004 + d0004 둘 다 확인/수정
```

## 3. 상세 사용법

### 3.1 컨텍스트 조회 및 설정

```bash
# 현재 컨텍스트 확인
uv run python .claude/skills/oocontext/scripts/oocontext_run.py

# SP 02로 설정
uv run python .claude/skills/oocontext/scripts/oocontext_run.py 02

# 공통(00) 초기화
uv run python .claude/skills/oocontext/scripts/oocontext_run.py clear

# SP 목록 표시
uv run python .claude/skills/oocontext/scripts/oocontext_run.py list
```

### 3.2 일회성 옵션 (--sp)

```bash
# 일회성 SP 01 사용 (세션 컨텍스트 유지)
uv run python .claude/skills/oocheck/scripts/oocheck_run.py --sp 01

# SP 02 임시 적용
uv run python .claude/skills/oodev/scripts/oodev_run.py --sp 02
```

### 3.3 문서 번호 매핑

```
문서번호 = SP × 10000 + 기본번호

예시:
- SP=00: d0001_prd.md
- SP=02: d20001_prd.md (d0001 + 20000)
```

## 4. 사용 예시

### 예시 1: SP 전환

```bash
# 1. 공통 작업 (SP=00)
uv run python .claude/skills/oocontext/scripts/oocontext_run.py clear
uv run python .claude/skills/oocheck/scripts/oocheck_run.py
# → d0004_todo.md에 이슈 등록

# 2. SP 02로 전환
uv run python .claude/skills/oocontext/scripts/oocontext_run.py 02

# 3. SP 02 작업
uv run python .claude/skills/oocheck/scripts/oocheck_run.py
# → d20004_todo.md에 이슈 등록

# 4. 확인
uv run python .claude/skills/oocontext/scripts/oocontext_run.py
# 출력: 현재 SP=02
```

### 예시 2: 일회성 옵션

```bash
# 세션 컨텍스트는 SP=00이지만 일회성 SP=01 사용
uv run python .claude/skills/oocontext/scripts/oocontext_run.py clear
uv run python .claude/skills/oodev/scripts/oodev_run.py --sp 01
# → d10004_todo.md 사전 검토, d10002_plan.md 참조

# 다음 명령은 다시 SP=00
uv run python .claude/skills/oocheck/scripts/oocheck_run.py
# → d0004_todo.md에 등록
```

### 예시 3: CWD 자동 감지

```bash
# 1. plan_srv 폴더로 이동
cd plan_srv

# 2. 컨텍스트 확인 (자동 감지)
uv run python .claude/skills/oocontext/scripts/oocontext_run.py
# 출력: 현재 SP=02 (CWD 자동 감지)

# 3. oocheck 실행
uv run python .claude/skills/oocheck/scripts/oocheck_run.py
# → d20004_todo.md에 등록 (자동)
```

### 예시 4: oofix 병행 처리 (예외)

```bash
# SP=02 설정
uv run python .claude/skills/oocontext/scripts/oocontext_run.py 02

# oofix 실행
uv run python .claude/skills/oofix/scripts/oofix_run.py

# 처리 대상:
# - d20004_todo.md: SP=02 이슈
# - d0004_todo.md: 공통 oo 모듈 이슈 (병행)
```

## 5. 문서 등록 규칙 상세

### 5.1 기본 규칙

| 조건 | 등록 대상 |
|------|----------|
| oocontext 미지정 (SP=00) | d0004_todo.md에만 등록 |
| oocontext [N] 지정 (SP≠00) | d{SP}0004_todo.md에만 등록 |

### 5.2 적용 스킬

| 스킬 | 처리 방식 |
|------|----------|
| oocheck | 현재 SP의 todo 문서에 에러 등록 |
| oofix | SP≠00: d{SP}0004 + d0004 둘 다 확인/수정 |
| oodev | 현재 SP의 todo 문서 사전 검토 |
| oohistory | 현재 SP의 todo → history 아카이브 |

### 5.3 oofix 예외 이유

수정 작업은 공통 모듈(oo)에도 영향을 줄 수 있으므로 d0004도 함께 처리

**예시**:
```
SP=02 설정 시:
- oocheck: d20004에만 등록
- oofix: d20004 + d0004 둘 다 처리
```

### 5.4 파일 자동 생성

d{SP}0004 파일이 없으면 즉시 자동 생성

```bash
# SP=02 설정 시 d20004_todo.md 없으면 자동 생성
uv run python .claude/skills/oocontext/scripts/oocontext_run.py 02
uv run python .claude/skills/oocheck/scripts/oocheck_run.py
# → d20004_todo.md 자동 생성 후 이슈 등록
```

## 6. 우선순위 및 주의사항

### 6.1 우선순위

```
--sp N (최우선)
    ↓
세션 컨텍스트 (oocontext N)
    ↓
CWD 감지 (폴더명 패턴)
    ↓
기본값 (00)
```

### 6.2 주의사항

- **context 전환 시**: 이전 SP 이슈는 해당 SP 문서에서만 관리
- **공통 oo 모듈 이슈**: context 미지정 상태에서 d0004에 등록 권장
- **oofix 병행**: SP≠00일 때 d{SP}0004와 d0004 둘 다 확인/수정

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oocontext/SKILL.md | 스킬 명세 |
| .claude/guides/common_guide.md | 공통 가이드라인 |
| CLAUDE.md | MIR 참조 |
| 00_doc/d{SP}0004_todo.md | SP별 TODO 문서 |

**연동 스킬**: oocheck, oofix, oodev, oohistory

**SP 목록**:
| SP | 폴더 | 문서 범위 |
|:--:|------|----------|
| 00 | (공통) | d0001~d9999 |
| 01 | 01_algorithm | d10001~d19999 |
| 02 | plan_srv | d20001~d29999 |
| 03~05 | 03~05_reserved | d30001~d59999 |
