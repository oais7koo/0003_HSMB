---
name: oodoc
description: "문서 생성 통합 스킬 'oodoc', '문서 생성', '문서 업데이트', '문서 검증', '스킬 최적화', '문서 귀속 검사' 등을 요청할 때 사용한다"
metadata:
  version: "v15"
  category: "doc-env"
---

# oodoc - 문서 생성 통합 스킬

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d0001~d0010 핵심 문서 생성·업데이트·최적화 오케스트레이터 |
| **하는 것** | PRD·Plan·Test·Todo·History·User·Env 문서 일괄 생성/현행화, 문서 정합성 검사 |
| **하지 않는 것** | 코드 수정(→oodev), 이슈 수정(→oofix), 스킬 파일 수정(→ooskill) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (`00_doc/`, `.claude/skills/`) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `run/check --fix`: `d{SP}0001~d{SP}0010_*.md` / `clear`: `00_doc/**/d*.md` + skills + guides (전체) |
| **실행 레벨** | [자동] — 대상 문서 자동 탐지 후 일괄 처리 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v15 2026-04-19 — optimize → check --fix 통합 (check 명령으로 일원화)
- v14 2026-04-11 — std 추가: 문서 번호 체계 조회·편집 서브명령어
- v13 2026-04-04 — update 추가: 코드 작업 후 변경 영향 문서 자동 탐지 및 업데이트
- v12 2026-04-03 — list/gen SP-aware 추가: SP별 문서 현황 조회 및 빈 문서 일괄 생성
- v11 2026-03-02 — optimize 재정의: SKILL.md → 00_doc/ 문서(d0001~d0010) 최적화로 변경
- v10 2026-03-02 — validate + check 통합: oodoc check [--quality --integrity] 단일 명령어

> 공통 가이드라인: `.claude/guides/common_guide.md` 참조

## 1. 개요

d0001~d0010 핵심 문서 생성/업데이트 오케스트레이터.
## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oodoc help` | 서브명령어 목록 표시 |
| `oodoc version` | 스킬 버전 정보 (v12) |
| `oodoc status` | 서브명령어 리스트, 스킬/문서 현재 상태 |
| `oodoc run [--doc 문서\|--required-only\|--dry-run\|--compact]` | d0001~d0010 문서 생성/업데이트 |
| `oodoc create [문서ID]` | 특정 문서 생성 |
| `oodoc explain [대상]` | 코드/함수/모듈/시스템 설명 생성 (explain 흡수) |

explain 옵션: `--level basic\|intermediate\|advanced`, `--format text\|diagram\|examples`
| `oodoc check --fix [문서ID\|--content\|--size]` | 00_doc/ 문서(d0001~d0010) 최적화 (구 `optimize`) |
| `oodoc clear [--keep N\|--scope 범위]` | 이력 초과 행 제거 (기본 5개 유지) — **범위: `00_doc/**/d*.md` 전체 + skills + guides** (d0010 이후 상세문서 포함) |
| `oodoc check [SP번호] [--quality\|--integrity] [--skill\|--doc] [--fix]` | 품질+정합성 통합 검사 (기본: 전체) |
| `oodoc show checklist` | 역할 수행 체크리스트 표시 |
| `oodoc add checklist "항목"` | 체크리스트 항목 추가 |
| `oodoc list [--sp N]` | SP별 문서 현황 조회 (존재/미생성 상태) |
| `oodoc gen [--sp N] [--dry-run]` | SP별 미생성 문서를 빈 템플릿으로 일괄 생성 |
| `oodoc update [--scope 범위] [--commit HEAD~N] [--dry-run]` | 코드 작업 후 관련 문서 자동 업데이트 |
| **`oodoc update this`** | **직전 작업 영향 문서 업데이트** (→ common_guide.md §9) |
| `oodoc manual [--update]` | d0000_manual.md 업데이트 (수동 관리 문서) |
| `oodoc std` | 문서 번호 체계(SSOT) 조회 |
| `oodoc std add [번호] [파일명패턴] [용도] [생성스킬]` | 새 번호 항목 추가 |
| `oodoc std remove [번호]` | 번호 항목 제거 |
| `oodoc std edit` | SSOT 파일 직접 편집 경로 안내 |

실행:
- run/create/check --fix/list/gen: `uv run python .claude/skills/oodoc/scripts/oodoc_run.py [args]`
- clear: `uv run python .claude/skills/oodoc/scripts/oodoc_clear.py [--keep N] [--scope all|00_doc|skills|guides]`
- check (--quality): `uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate [args]`
- check (--integrity): `uv run python .claude/skills/oodoc/scripts/oodoc_check.py [sp번호] [--fix]`
- check (기본): 두 스크립트 순차 실행

## 3. 문서-스킬 매핑

| 00_doc/ 문서 | 용도 | 생성 방법 | 필수 |
|-----------|------|----------|:----:|
| d0000_manual.md | 전체 사용 매뉴얼 | oodoc manual | - |
| d0001_prd.md | PRD | ooprd run | O |
| d0002_plan.md | 개발 계획 | ooplan run | O |
| d0003_test.md | 테스트 케이스 | ootest run | O |
| d0004_todo.md | TODO/디버깅 | oocheck | O |
| d0005_lib.md | 라이브러리 | oolib run | - |
| d0006_db.md | DB 구조 | oodb run | - |
| d0008_user.md | 사용자 가이드 | oouser run | - |
| d0009_env.md | 환경/명령어 집계 | ooenv run | - |
| d0010_history.md | 변경 이력 | oohistory run | O |
| d0020_연구노트.md | 연구노트 | oonote run | - |
| d0110_survey.md | 서베이 | oosurvey run | - |
| d0120_기술연구.md | 기술연구 | ooresearch run | - |
| d0200_프로젝트소개PPT.md/.pptx | 프로젝트소개PPT — 결과/제품/기술 중심 (과정X) | ooppt run --intro | - |
| d{SP}1000_상세문서인덱스.md | 상세문서 번호체계 인덱스 (1001~9999 목록) | oodoc create 1000 | O |

## 4. 문서 생성 순서 및 의존성

### 4.1 Phase별 순서

| Phase | 문서 | 스킬 |
|-------|------|------|
| 1.기획 | d{SP}0001_prd, d{SP}0002_plan | ooprd, ooplan |
| 2.관리 | d{SP}0004_todo, d{SP}0010_history | oocheck, oohistory |
| 3.기술 | d0006_db, d0005_lib, d{SP}0003_test | oodb, oolib, ootest |
| 4.사용자 | d{SP}0008_user | oouser |

### 4.2 의존 관계

- d{SP}0001_prd -> d{SP}0002_plan, d{SP}0003_test, d{SP}0008_user
- d{SP}0004_todo -> d{SP}0010_history
- d0006_db -> d{SP}0003_test

## 5. oodoc run 상세

### 5.1 실행 순서

1. d{SP}0004_todo (oocheck)
2. d{SP}0010_history (oohistory)
3. d0005_lib, d0006_db, d{SP}0003_test (병렬 가능)
4. d{SP}0008_user, d{SP}0001_prd, d{SP}0002_plan

### 5.2 병렬 실행

독립적 스킬 병렬 호출:
- Phase 3: oolib, oodb, ootest
- Phase 4: oouser, ooprd

## 6. oodoc check --fix

`00_doc/` 문서(d0001~d0010) 최적화 (품질 + 용량) — 구 `oodoc optimize`

| 유형 | 작업 |
|------|------|
| 내용 | 모호 표현 수정, 누락 섹션 보완, 일관성 확보 |
| 용량 | 중복 내용 제거, 과도한 예제 축약, 이력 초과 행 정리 |

**삭제**: 빈 섹션, 플레이스홀더(`(작성 예정)`, `TBD`), 중복 내용
**형식**: 깨진 테이블/코드블록 수정, 헤더 레벨 정규화
**이력**: 5개 초과 시 오래된 항목 제거 (= `oodoc clear` 통합, 단 clear는 d0010 이후 상세문서까지 포함한 전체 `d*.md` 대상)

## 7. oodoc check --quality 상세

### 7.1 검증 항목

| 카테고리 | 검증 항목 | 설명 |
|----------|----------|------|
| 이력 | 이력 테이블 존재 | 문서 상단 버전/날짜/변경내용 |
| 필수섹션 | 문서별 필수 섹션 | PRD: 요구사항, Plan: 태스크 등 |
| 참조 | [[링크]] 유효성 | 참조 문서 존재 여부 |
| 마크다운 | 테이블/코드블록 | 깨진 형식 감지 |
| 스킬정합성 | 스킬 간 참조 | oo*.md 간 상호 참조 유효성 |
| 스킬정합성 | 관련 파일 누락 | agent/, script/, template/ 파일 |

### 7.2 자동 수정 (--fix)

| 이슈 유형 | 자동 수정 |
|----------|----------|
| 이력 5개 초과 | 오래된 이력 삭제 |
| 이력 테이블 누락 | 템플릿 추가 |
| 깨진 참조 링크 | 리포트만 |
| 누락 파일 | 리포트만 (수동 생성 권장) |

## 8. 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 분석 | Explore | haiku | O |
| 최적화 | task-executor | sonnet | O |
| 검증 | task-checker | sonnet | - |

## 9. oodoc check --integrity 상세

### 9.1 목적

두 가지 검사를 통합 실행 (`oodoc check` 기본 또는 `--integrity`):
| `oodoc run` | 문서 생성 실행 |
- **Part 1 (교차 정합성)**: d0001~d0010 문서 간 일관성 검증
- **Part 2 (귀속 검사)**: 파일이 올바른 SP 폴더에 있는지 검증

실행: `uv run python .claude/skills/oodoc/scripts/oodoc_check.py [sp번호] [--fix]`

### 9.2 Part 1: 교차 정합성 검사 항목

| 항목 | 내용 |
|------|------|
| 필수 문서 존재 | d0001/d0002/d0004/d0010 존재 여부 |
| 이력 테이블 | 각 문서 이력 섹션 존재, 5개 이내 |
| TODO↔History 동기화 | d0004 해결된 이슈 ID가 d0010에 기록됐는지 |
| 교차 참조 유효성 | 문서 내 `00_doc/*.md` 링크 실존 여부 |

### 9.3 Part 2: SP 귀속 검사 항목

| 항목 | 내용 |
|------|------|
| 파일명 prefix | `d{N}` 첫 숫자 = 폴더 SP 번호 일치 |
| 빈 문서 | 파일 크기 < 300B → WARN |
| 플레이스홀더 | `(작성 예정)`, `TBD` 등 포함 여부 |

### 9.4 리포트 형식

```
== sp00/ 정합성 검사 ==

[Part 1] d0001~d0010 교차 정합성
  [OK]    d0001_prd.md 존재
  [WARN]  d0002_plan.md: 이력 8개 (5개 초과)

[Part 2] SP 폴더 귀속 검사
  [OK]    d0001_prd.md
  [ERROR] d0020_algo.md: prefix d0 ≠ SP02 → 파일명 확인 권고

  소계: OK:X | WARN:X | ERROR:X
```

### 9.5 `--fix` 옵션

ERROR/WARN 항목에 대한 조치 방안만 출력. 자동 수정 없음.

## 10. 문서 번호 체계 (oodoc std)

> SSOT: `.claude/skills/oodoc/references/doc_numbering.md`

| 범위 | 성격 | 규칙 |
|------|------|------|
| 0000~0019 | 예약 (핵심) | 지정 스킬만 생성 |
| 0020~0099 | 선택 (자유) | 스킬 우선, 빈 번호 자유 할당 |
| 0100~0999 | 선택 (스킬 전용) | 해당 스킬 사용 시만 생성 |
| 1001~9999 | 상세 문서 | oofeature 전용 |

### 10.1 oodoc std 워크플로우

```
oodoc std
    → doc_numbering.md 전체 내용 출력 (번호 할당표 포함)

oodoc std add [번호] [파일명패턴] [용도] [생성스킬]
    → doc_numbering.md 해당 범위 테이블에 행 추가
    → 예: oodoc std add 0030 d{SP}0030_benchmark.md 성능벤치마크 ootest

oodoc std remove [번호]
    → 해당 번호 행 삭제 (예약 번호 0001~0019 삭제 시 경고)

oodoc std edit
    → SSOT 파일 경로 출력: .claude/skills/oodoc/references/doc_numbering.md
    → "직접 편집 후 oosync run으로 동기화 권장" 안내
```

### 10.2 add 규칙

| 조건 | 처리 |
|------|------|
| 예약 범위(0001~0019)에 추가 시도 | 경고 후 확인 요청 |
| 이미 존재하는 번호 | 기존 내용 표시 후 덮어쓰기 확인 |
| 생성스킬 생략 | `수동` 으로 기록 |

## 11. oodoc update 상세

코드/디자인/스크립트 작업 후 변경 영향을 받는 문서를 자동 탐지하여 업데이트.

### 11.1 워크플로우

```
oodoc update [--scope auto|--commit HEAD~3] [--dry-run]
        │
        ▼
[1] 변경 탐지
    - git diff --name-only (unstaged) 또는 --commit으로 커밋 범위 지정
    - 변경된 파일 목록 수집
        │
        ▼
[2] 영향 문서 매핑
    - 변경 파일 경로 → SP 번호 추출 (0N_* 패턴)
    - 변경 유형 → 대상 문서 매핑 (아래 테이블 참조)
        │
        ▼
[3] 문서 읽기 + 변경 반영
    - 각 대상 문서를 Read로 로드
    - 변경 내용을 해당 섹션에 반영 (이력 추가, 수치 업데이트 등)
    - 문서 이력 테이블 버전 bump
        │
        ▼
[4] 결과 리포트
    - 업데이트된 문서 목록 + 변경 요약 출력
```

### 11.2 변경 유형 → 문서 매핑

| 변경 유형 | 영향 문서 |
|----------|----------|
| `0N_*/` 코드 변경 | d{SP}0002 (plan 진행률), d{SP}0004 (todo) |
| `.claude/skills/oo*/` 스킬 변경 | `.claude/CLAUDE.md` 카탈로그, SKILL.md 이력 |
| `02_tokens/`, `04_components/` | d{SP}0002 (plan), d{SP}0001 (prd 범위) |
| `scripts/*.py` 변경 | d0005 (lib), d{SP}0002 (plan) |
| `tests/` 변경 | d{SP}0003 (test) |
| `.gitignore`, 환경 설정 | d0009 (env) |

### 11.3 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--scope auto` | git diff 기반 자동 탐지 | auto |
| `--scope all` | 모든 문서 강제 업데이트 | - |
| `--commit HEAD~N` | 최근 N개 커밋 기준 탐지 | - |
| `--dry-run` | 업데이트 대상만 표시, 실제 수정 안 함 | - |
| `--sp N` | 특정 SP 문서만 업데이트 | 현재 컨텍스트 |

### 11.4 run과의 차이

| 항목 | `oodoc run` | `oodoc update` |
|------|-------------|----------------|
| 목적 | 문서 신규 생성/전체 재생성 | 변경분만 반영 |
| 범위 | d0001~d0010 전체 | 영향 받는 문서만 |
| 입력 | 코드 전체 스캔 | git diff (변경분) |
| 실행 | 각 oo스킬 호출 | Claude 직접 Edit |

### 11.5 실행 예시

```bash
# 작업 후 관련 문서 자동 업데이트
oodoc update

# 최근 2개 커밋 기준 업데이트 (dry-run)
oodoc update --commit HEAD~2 --dry-run

# SP07만 업데이트
oodoc update --sp 07
```

---

## 12. 관련 문서

CLAUDE.md, v/*.md, .claude/templates/, .claude/skills/*/templates/, 00_doc/sp00/d0001~d0010

> **관련 명령어**: `.claude/commands/sc/index.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- QMD-REF:START -->

## QMD 마크다운 검색 (문서 내용 탐색 시)

> 마크다운 문서 **내용**을 찾을 때는 Glob/Grep 대신 **`mcp__qmd__query`** 우선 사용.
> qmd 미가동 시 Glob/Grep 폴백. 자세한 기준: `.claude/guides/common_guide.md §10`

| 도구 | 적합한 상황 |
|------|-----------|
| `mcp__qmd__query` (lex) | 키워드·문서번호·용어 검색 |
| `mcp__qmd__query` (vec) | 자연어 의미 검색 |
| `Glob` | 파일 경로 패턴 검색 |
| `Grep` | 코드·특정 문자열 검색 |

**인덱싱**: `oostart run` 시 `qmd update` 자동 실행 / 최초: `qmd collection add . --name {프로젝트명}`

<!-- QMD-REF:END -->

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

