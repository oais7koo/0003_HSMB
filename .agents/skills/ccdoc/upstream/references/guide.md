# oodoc_guide - 문서 생성 통합 가이드

## 문서 이력 관리
- v05 2026-05-17 — §13 d0007_data 행 추가 + DOC_SKILL_MAPPING/SP_DOC_DEFINITIONS에서 d0007 제거 (d0007 = data/oodata 확정, 구 oohelp/command 매핑 정리)
- v04 2026-05-17 — §6.4 추가: run 스킬 실행 하이브리드(oohistory 스크립트 직접 실행 / 그 외 LLM 위임)
- v03 2026-05-17 — §6.3 SP 스코프 추가: oodoc run 기본=현재 컨텍스트, --all=전체 SP
- v02 2026-04-26 — SKILL.md 축소를 위한 상세 워크플로우/코드 예시 통합 (§6~§14 추가)
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oodoc/SKILL.md` | 공통: `.claude/guides/common_guide.md`

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
```

**의존 관계**:
- d{SP}0001_prd → d{SP}0002_plan, d{SP}0003_test
- d{SP}0004_todo → d{SP}0010_history
- d0006_db → d{SP}0003_test

### 2.2 문서 검증 (validate)

```
문서 이력 검증 → 필수 섹션 확인 → 참조 링크 검증 → 마크다운 검증 → 스킬 정합성 → 보고서 출력
```

### 2.3 스킬 최적화 (optimize)

```
.claude/skills/oo*/SKILL.md 스캔 → 병렬 에이전트 할당 → 내용 최적화 → 용량 최적화 → 검증/저장
```

## 3. 상세 사용법

### 3.1 전체 문서 생성

```bash
# d0001~d0010 전체 생성/업데이트
uv run python .claude/skills/oodoc/scripts/oodoc_run.py run

# 필수 문서만
uv run python .claude/skills/oodoc/scripts/oodoc_run.py run --required-only

# 특정 문서만
uv run python .claude/skills/oodoc/scripts/oodoc_run.py run --doc d0004_todo

# 드라이런
uv run python .claude/skills/oodoc/scripts/oodoc_run.py run --dry-run
```

### 3.2 문서 검증

```bash
# 전체 검증
uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate

# 스킬 정합성만
uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate --skill

# 문서만
uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate --doc

# 자동 수정
uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate --fix
```

**검증 항목**:
| 카테고리 | 검증 내용 |
|----------|----------|
| 이력 | 이력 테이블 존재, 5개 제한 규칙 |
| 필수섹션 | 문서별 필수 섹션 |
| 참조 | [[링크]] 유효성 |
| 마크다운 | 테이블/코드블록 깨짐 |
| 스킬정합성 | oo*.md 간 참조, 관련 파일 누락 |

### 3.3 스킬 최적화

```bash
uv run python .claude/skills/oodoc/scripts/oodoc_run.py optimize
uv run python .claude/skills/oodoc/scripts/oodoc_run.py optimize oocheck
uv run python .claude/skills/oodoc/scripts/oodoc_run.py optimize --content
uv run python .claude/skills/oodoc/scripts/oodoc_run.py optimize --size
```

**최적화 규칙**:
- 삭제: 템플릿 섹션, 반복 가이드, 과도한 예제, 이모지
- 문체: 경어체→단답형, 장황→핵심
- 통합: 공통 패턴 → common_guide.md 참조

## 4. 사용 예시

### 4.1 프로젝트 초기화

```bash
mkdir -p doc v/{command,agent,template}
uv run python .claude/skills/ooprd/scripts/ooprd_run.py create
uv run python .claude/skills/ooplan/scripts/ooplan_run.py create
uv run python .claude/skills/oohistory/scripts/oohistory_run.py create
uv run python .claude/skills/oodoc/scripts/oodoc_run.py run
```

### 4.2 스킬 정합성 검증

```bash
uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate --skill
# → .claude/skills/ooflow/SKILL.md
#     스킬 참조: oodev, oocheck... (9개 유효)
```

### 4.3 문서 이력 관리

```bash
uv run python .claude/skills/oodoc/scripts/oodoc_run.py validate --fix
# 자동 수정: 오래된 이력 삭제, 최근 5개 유지
```

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oodoc/SKILL.md | 스킬 명세 |
| .claude/guides/common_guide.md | 공통 가이드라인 |
| CLAUDE.md | MIR 참조 |
| 00_doc/sp00/d0001~d0010 | 핵심 문서 |
| .claude/skills/oo*/SKILL.md | 스킬 문서 |

**에이전트**: Explore, task-executor, task-checker
**연동 스킬**: ooprd, ooplan, oocheck, oohistory, oolib, oodb, ootest

**문서 번호 체계**:
| 범위 | 용도 |
|------|------|
| d0001~d0010 | 공통 핵심 문서 |
| d10000~d19999 | SP 01 |
| d20000~d29999 | SP 02 |

---

## 6. oodoc run 상세 (SKILL.md §5에서 이동)

### 6.1 실행 순서

1. d{SP}0004_todo (oocheck)
2. d{SP}0010_history (oohistory)
3. d0005_lib, d0006_db, d{SP}0003_test (병렬 가능)
4. d{SP}0001_prd, d{SP}0002_plan

### 6.2 병렬 실행

독립적 스킬 병렬 호출:
- Phase 3: oolib, oodb, ootest
- Phase 4: ooprd

### 6.3 SP 스코프

`oodoc run`은 **현재 oocontext SP만** 처리한다. SP 번호 결정 우선순위:

| 우선순위 | 기준 |
|:--------:|------|
| 1 | `--sp N` 명시 |
| 2 | oocontext 상태 (`.omc/state/context.json`) |
| 3 | CWD 경로의 `0N_*` 패턴 |
| 4 | 기본값 SP00 |

| 옵션 | 처리 범위 |
|------|----------|
| (기본) | 현재 컨텍스트 SP의 d{SP}0001~d{SP}0010 |
| `--sp N` | 지정한 SP만 |
| `--all` | `00_doc/sp*` 전체 SP 순회 처리 |

> `--all`은 `00_doc/` 아래 `sp??` 디렉토리를 스캔(SP00 항상 포함)하여 각 SP를 순차 처리한다.

### 6.4 스킬 실행 방식 (하이브리드)

`oodoc run`은 9개 매핑 스킬을 `execute_skill()`에서 두 방식으로 처리한다:

| 방식 | 대상 | 동작 |
|------|------|------|
| 스크립트 직접 실행 | `oohistory sync` | subprocess로 즉시 실행 (완료 TODO → 이력 이동) |
| LLM 위임 | ooprd·ooplan·oolib·oodb·oocheck·ootest 등 | 문서 *내용* 생성에 LLM 추론 필요 → 계획만 출력, Claude가 처리 |

- 스크립트 직접 실행 대상은 `SCRIPT_EXECUTABLE` 딕셔너리에 등록된 명령에 한한다.
- 직접 실행 시 `--sp`·`--dry-run`이 하위 스크립트로 그대로 전달된다.
- 신규 등록 조건: 해당 스킬 명령이 LLM 추론 없이 스크립트만으로 대상 문서를 완결 갱신할 수 있어야 한다.

## 7. oodoc check --fix 상세 (SKILL.md §6에서 이동)

`00_doc/` 문서(d0001~d0010) 최적화 (품질 + 용량) — 구 `oodoc optimize`

| 유형 | 작업 |
|------|------|
| 내용 | 모호 표현 수정, 누락 섹션 보완, 일관성 확보 |
| 용량 | 중복 내용 제거, 과도한 예제 축약, 이력 초과 행 정리 |

**삭제**: 빈 섹션, 플레이스홀더(`(작성 예정)`, `TBD`), 중복 내용
**형식**: 깨진 테이블/코드블록 수정, 헤더 레벨 정규화
**이력**: 5개 초과 시 오래된 항목 제거 (= `oodoc clear` 통합, 단 clear는 d0010 이후 상세문서까지 포함한 전체 `d*.md` 대상)

## 8. oodoc check --quality 상세 (SKILL.md §7에서 이동)

### 8.1 검증 항목

| 카테고리 | 검증 항목 | 설명 |
|----------|----------|------|
| 이력 | 이력 테이블 존재 | 문서 상단 버전/날짜/변경내용 |
| 필수섹션 | 문서별 필수 섹션 | PRD: 요구사항, Plan: 태스크 등 |
| 참조 | [[링크]] 유효성 | 참조 문서 존재 여부 |
| 마크다운 | 테이블/코드블록 | 깨진 형식 감지 |
| 스킬정합성 | 스킬 간 참조 | oo*.md 간 상호 참조 유효성 |
| 스킬정합성 | 관련 파일 누락 | agent/, script/, template/ 파일 |

### 8.2 자동 수정 (--fix)

| 이슈 유형 | 자동 수정 |
|----------|----------|
| 이력 5개 초과 | 오래된 이력 삭제 |
| 이력 테이블 누락 | 템플릿 추가 |
| 깨진 참조 링크 | 리포트만 |
| 누락 파일 | 리포트만 (수동 생성 권장) |

## 9. oodoc check --integrity 상세 (SKILL.md §9에서 이동)

### 9.1 목적

두 가지 검사를 통합 실행 (`oodoc check` 기본 또는 `--integrity`):
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

## 10. oodoc numbering 워크플로우 (SKILL.md §10.1에서 이동)

```
oodoc numbering
    → doc_numbering.md 전체 내용 출력 (번호 할당표 포함)

oodoc numbering add [번호] [파일명패턴] [용도] [생성스킬]
    → doc_numbering.md 해당 범위 테이블에 행 추가
    → 예: oodoc numbering add 0030 d{SP}0030_benchmark.md 성능벤치마크 ootest

oodoc numbering remove [번호]
    → 해당 번호 행 삭제 (예약 번호 0001~0019 삭제 시 경고)

oodoc numbering edit
    → SSOT 파일 경로 출력: .claude/skills/oodoc/references/doc_numbering.md
    → "직접 편집 후 oosync run으로 동기화 권장" 안내
```

### 10.1 add 규칙

| 조건 | 처리 |
|------|------|
| 예약 범위(0001~0019)에 추가 시도 | 경고 후 확인 요청 |
| 이미 존재하는 번호 | 기존 내용 표시 후 덮어쓰기 확인 |
| 생성스킬 생략 | `수동` 으로 기록 |

## 11. oodoc update 상세 (SKILL.md §11에서 이동)

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

## 12. 히스토리 아카이브

SKILL.md에서 5개 초과로 외부화된 옛 이력:

- v10 2026-03-02 — validate + check 통합: oodoc check [--quality --integrity] 단일 명령어

## 13. 문서-스킬 매핑 (SKILL.md §3에서 이동)

| 00_doc/ 문서 | 용도 | 생성 방법 | 필수 |
|-----------|------|----------|:----:|
| d0000_list.md | 00_doc 문서 링크 인덱스 | oodoc run/update | - |
| d0001_prd.md | PRD | ooprd run | O |
| d0002_plan.md | 개발 계획 | ooplan run | O |
| d0003_test.md | 테스트 케이스 | ootest run | O |
| d0004_todo.md | TODO/디버깅 | oocheck | O |
| d0005_lib.md | 라이브러리 | oolib run | - |
| d0006_db.md | DB 구조 | oodb run | - |
| d0007_data.md | data/ 폴더 구조·설명 (SP 공통, oodata 전용) | oodata run | - |
| d0008_checklist.md | 프로젝트 체크리스트 | oocheck add / oocheck run | - |
| d0009_env.md | 환경/명령어 집계 | ooenv run | - |
| d0010_history.md | 변경 이력 | oohistory run | O |
| d0020_연구노트.md | 연구노트 | oonote run | - |
| d0110_survey.md | 서베이 | oosurvey run | - |
| d0120_기술연구.md | 기술연구 | ooresearch run | - |
| d0200_프로젝트소개PPT.md/.pptx | 프로젝트소개PPT — 결과/제품/기술 중심 (과정X) | ooppt run --intro | - |
| d{SP}1000_상세문서인덱스.md | 상세문서 번호체계 인덱스 (1001~9999 목록) | oodoc create 1000 | O |
