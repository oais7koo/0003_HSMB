# oonext Tutorial

> 다음 작업 추천 스킬 | 버전: v01 | 카테고리: meta-util

## 1. 이 스킬은 왜 필요한가?

다음 작업 추천 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oonext run

# 상태 확인
oonext status

# 도움말
oonext help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oonext help` | 서브명령어 목록 표시 |
| `oonext version` | 스킬 버전 정보 (v01) |
| `oonext status` | 서브명령어 리스트, 스킬 상태 |
| `oonext check` | references/checklist.md 기반 체크 및 리포팅 |
| `oonext show checklist` | 역할 수행 체크리스트 표시 |
| `oonext add checklist "항목"` | 체크리스트 항목 추가 |
| `oonext run` | **현재 컨텍스트 기준 다음 작업 추천 실행 (기본)** |
| **`oonext run this`** | **last_target 기반 다음 작업 추천** (→ common_guide.md §9) |
| `oonext run --sp N` | 특정 서브프로젝트 대상으로 추천 |
| `oonext run --all-sps` | 전체 서브프로젝트 대상으로 추천 |
| `oonext run --top N` | 상위 N개만 표시 (기본: 5) |

실행: `uv run python .claude/skills/oonext/scripts/oonext_run.py [args]`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | PRD·Plan·Todo 문서를 분석하여 다음에 진행할 작업 우선순위 추천 |
| **하는 것** | 미완료 Feature/이슈 분석, 우선순위 정렬, 다음 작업 추천 목록 출력 |
| **하지 않는 것** | 작업 실행(→ooflow/oodev), 이슈 수정(→oofix), 문서 수정(→oodoc) |
| **참조 범위** | 현재 프로젝트 내부 문서 파일만 (d{SP}0001~0004) / 외부 시스템 자동 포함 안 함 |
| **수정 대상** | 없음 (읽기·분석·출력만) |
| **실행 레벨** | [수동] — 분석 결과 출력만, 파일 수정 없음 |
| **에이전트 호환** | 범용 — 파일 읽기 기반 분석으로 모든 에이전트 처리 가능 |

### 추천 작업 (상위 5개)

| 순위 | 점수 | 출처 | SP | 내용 |
|:----:|:----:|------|:--:|------|
| 1 | 100 | todo/이슈 | 05 | [CRITICAL] ... |
| 2 | 80 | todo/이슈 | 00 | [ERROR] ... |
| 3 | 70 | todo/커스텀 | 02 | ... |
| 4 | 60 | plan | 00 | 불필요 스크립트 정리 |
| 5 | 55 | plan/부채 | 00 | TD-01: oostart 스크립트 경로 수정 |

### 요약

- 활성 이슈: N건 (CRITICAL: X, ERROR: Y, WARNING: Z)
- 대기 Todo: N건
- 계획 항목: N건
- 기술 부채: N건
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 특정 서브프로젝트만 분석 | 현재 컨텍스트 |
| `--all-sps` | 전체 서브프로젝트 분석 | false |
| `--top N` | 상위 N개 표시 | 5 |
| `--all` | 모든 항목 표시 (점수순 정렬) | false |
| `--source [todo\|plan\|prd]` | 특정 출처만 분석 | 전체 |

### 서브프로젝트 지원

| SP | PRD | Plan | Todo |
|:--:|-----|------|------|
| 00 | d0001_prd.md | d0002_plan.md | d0004_todo.md |
| 01~10 | d{N}0001_prd.md | d{N}0002_plan.md | d{N}0004_todo.md |

## 5. 워크플로우

**문서 수집** → **항목 추출** → **우선순위 점수 산정** → **추천 리스트 출력**

### 1. 문서 수집

| 문서 | 추출 대상 | 점수 가중치 |
|------|----------|------------|
| d{SP}0004_todo.md | Active Issues (CRITICAL/ERROR/WARNING) | 최고 |
| d{SP}0004_todo.md | 커스텀 Todo (대기 중) | 높음 |
| d{SP}0002_plan.md | 향후 계획 (Phase 2+), 기술 부채 | 중간 |
| d{SP}0001_prd.md | 미구현 요구사항 | 참고 |

### 2. 우선순위 점수 산정

| 요소 | 점수 | 설명 |
|------|------|------|
| CRITICAL 이슈 | 100 | 즉시 대응 필요 |
| ERROR 이슈 | 80 | 24시간 내 대응 |
| WARNING 이슈 | 40 | 1주일 내 대응 |
| 커스텀 Todo (high) | 70 | 사용자 지정 높음 |
| 커스텀 Todo (medium) | 50 | 사용자 지정 보통 |
| 커스텀 Todo (low) | 30 | 사용자 지정 낮음 |
| Plan 항목 (High) | 60 | 계획 우선순위 높음 |
| Plan 항목 (Medium) | 40 | 계획 우선순위 보통 |
| Plan 항목 (Low) | 20 | 계획 우선순위 낮음 |
| 기술 부채 (P1) | 55 | 긴급 기술 부채 |
| 기술 부채 (P2) | 35 | 일반 기술 부채 |

### 3. 출력 형식

```markdown
# oonext - 다음 작업 추천

현재 컨텍스트: SP07
분석 문서: d70001_prd.md, d70002_plan.md, d70004_todo.md

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oonext run
```

### 서브명령어 활용
```bash
oonext run  # **현재 컨텍스트 기준 다음 작업 추천 실행 (기본)**
oonext run this
```

### 옵션
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 특정 서브프로젝트만 분석 | 현재 컨텍스트 |
| `--all-sps` | 전체 서브프로젝트 분석 | false |
| `--top N` | 상위 N개 표시 | 5 |
| `--all` | 모든 항목 표시 (점수순 정렬) | false |
| `--source [todo\|plan\|prd]` | 특정 출처만 분석 | 전체 |

### 스크립트 직접 실행
```bash
uv run python .claude/skills/oonext/scripts/oonext_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 스캔 | Explore | haiku | 문서 파일 탐색 (병렬) |

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 10. 관련 스킬

`.claude/skills/ootodo/SKILL.md` | `.claude/skills/ooplan/SKILL.md` | `.claude/skills/ooprd/SKILL.md` | `00_doc/d{SP}0004_todo.md`

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
