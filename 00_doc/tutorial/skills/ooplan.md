# ooplan Tutorial

> 구현 계획 및 상세 설계 스킬 | 버전: v06 | 카테고리: core-dev

## 1. 이 스킬은 왜 필요한가?

구현 계획 및 상세 설계 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ooplan run

# 상태 확인
ooplan status

# 도움말
ooplan help
```

## 3. 전체 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooplan help` | 서브명령어 목록 표시 | 터미널 |
| `ooplan version` | 스킬 버전 정보 (v06) | 터미널 |
| `ooplan status` | 서브명령어 리스트, 현재 상태 | 터미널 |
| `ooplan check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ooplan run` | 구현 계획 생성 실행 | 터미널 |
| `ooplan show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooplan add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| run | PRD -> Task까지 완전 생성 (run task와 동일) | d{SP}0002_plan.md |
| `ooplan update` | 현행화 — 현재 코드/현황 스캔 → Plan 문서 변경분 반영 | d{SP}0002_plan.md |
| `ooplan update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| **run this** | **직전 작업 관련 계획 업데이트** (→ common_guide.md §9) | d{SP}0002_plan.md |
| run epic | PRD -> Epic까지 생성 | d{SP}0002_plan.md |
| run feature | PRD -> Feature까지 생성 | d{SP}0002_plan.md |
| run task | PRD -> Task까지 생성 (기본값) | d{SP}0002_plan.md |
| detail | 실행 전 상세 설계 (->oodev) | 실행 큐 |
| optimize | 현재 Plan 검토 및 개선 | d{SP}0002_plan.md |
| sync | PRD 변경사항 동기화 | d{SP}0002_plan.md |
| design [대상] | 시스템/API/컴포넌트/DB 아키텍처 설계 (design 흡수) | 설계 문서 |
| workflow [prd] | PRD→워크플로우 생성, 페르소나/전략/리스크 (workflow 흡수) | 로드맵/태스크 |

design 옵션: `--type architecture\|api\|component\|database`, `--format diagram\|spec\|code`, `--iterative`
workflow 옵션: `--persona architect\|frontend\|backend\|security`, `--strategy systematic\|agile\|mvp`, `--output roadmap\|tasks\|detailed`, `--estimate`, `--risks`, `--parallel`

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | PRD 기반 구현 계획(Epic/Feature/Task) 수립 |
| **하는 것** | d{SP}0002_plan.md 생성/갱신, 아키텍처·API·DB·워크플로우 설계 |
| **하지 않는 것** | PRD 작성(→ooprd), 코드 구현(→oodev), 이슈 수정(→oofix) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (PRD, 코드 구조) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/d{SP}0002_plan.md` |
| **실행 레벨** | [반자동] — 계획 구조 확인 후 실행 |
| **에이전트 호환** | 범용 — Claude Code에서 Explore·task-executor 서브에이전트 자동 활용 |

### plan 템플릿 목차

> 템플릿: `.claude/skills/ooplan/templates/plan_template.md`

1. 문서관리 -> 2. 구현개요 -> 3. WBS(Epic/Feature) -> 4. 스프린트 -> 5. 기술설계 -> 6. 리스크 -> 7. 의사결정 -> 8. 진행추적

### prd -> plan 매핑

### 6.1 계층 매핑
PRD 비전->목표요약 / 기능->Epic / 아키텍처->결정사항 / 마일스톤->스프린트 / 리스크->상세화

### 6.2 분해 체계
```
PRD -> Epic(도메인) -> Feature(기능) -> Task(구현) -> TC(테스트)
```

| 레벨 | 기준 | 예시 |
|------|------|------|
| Epic | 도메인/비즈니스 | 정책정보, 인증 |
| Feature | 사용자 기능 | 중앙정부 정책 |
| Task | 구현 단위 | 보건복지부 탭 |

**PRD 필요 섹션** (Feature 분해 근거):

| PRD 섹션 | ooplan 활용 |
|----------|------------|
| §기능요구사항 (MoSCoW 목록) | Epic → Feature 분해 근거 |
| §기능 상세 (입출력/시나리오) | Feature → Task 세분화 근거 |
| §기술스택 (언어/프레임워크) | 기술 설계 방향 |

### streamlit 프레임워크 (자동 감지)

**감지 조건**: `pages/*.py` 존재 | `import streamlit` 검출 | `run.bat`에 streamlit 포함
**감지 시**: `.claude/skills/ooplan/references/streamlit_guide.md` 자동 참조

**3계층**: PRD(What) -> Plan(Where) -> 개발서 d{SP}1XXX_페이지명_단위개발.md(How)
**명명**: `d{서브프로젝트번호}{4자리순번}_{페이지명}_단위개발.md`

> 설계 패턴(레이아웃/컴포넌트/DB): `streamlit_guide.md` 참조

### 상세 문서 현황 (plan.md 8.2절)

### 8.1 자동 스캔 규칙

`ooplan sync` 또는 `ooplan run` 실행 시 현재 SP의 `00_doc/sp{N}/` 하위를 스캔하여 **파일명에 상세 단계가 포함된 문서**를 자동 탐색 → plan.md 8.2절 갱신.

**스캔 패턴**: `*_상세기획_*.md | *_상세설계_*.md | *_상세개발_*.md | *_상세검증_*.md`

**단계 감지**: 파일명에서 `_상세기획_` / `_상세설계_` / `_상세개발_` / `_상세검증_` 키워드로 현재 단계 판별.

### 8.2 plan.md 8.2절 형식

```markdown

### 진행추적

### 8.2 상세 문서 현황
| 문서번호 | 기능명 | 단계 | 연결 Feature | 파일 |
|---------|--------|------|-------------|------|
| d41001 | 데이터수집소스 | 🔵설계 | F001-1 | d41001_상세설계_데이터수집소스.md |
| d40101 | 크롤러모듈 | 🟡개발 | F001-2 | d40101_상세개발_크롤러모듈.md |
```

**단계 아이콘**: `⚪기획 → 🔵설계 → 🟡개발 → 🟢검증 → ✅완료`

### 8.3 연동 스킬

- **oofeature**: 상세 문서 생성/단계 전환/현황 조회
- **oodev run dXXXX**: 상세 문서 기반 개발 실행

## 5. 워크플로우

### 5.1 run

> **핵심 원칙**: PRD에서 Plan 생성에 필요한 정보를 먼저 파악하고, 부족한 항목은 사용자에게 1개씩 질문한다. 정보 부족 상태로 Plan을 생성하지 않는다.

**정보 수집 → Plan 생성 프로토콜**:

```
1. PRD 로드 및 분석
   d{SP}0001_prd.md 읽기 → Plan 생성에 필요한 항목 추출

2. 필수 정보 누락 확인
   | 항목 | PRD 출처 | 누락 시 질문 |
   |------|---------|------------|
   | Epic 분해 근거 | §기능요구사항 | "어떤 도메인/기능 그룹으로 나눌까요?" |
   | 기술 스택 | §기술스택 | "사용할 언어/프레임워크는?" |
   | 구현 우선순위 | MoSCoW | "우선 구현할 Feature는?" |
   | 일정/스프린트 | §마일스톤 | "스프린트 기간과 목표 완료 시점은?" |
   | 제약/리스크 | §비기능 | "기술적 제약이나 리스크가 있나요?" |

3. 누락 항목 순차 질문 (1개씩)
   - PRD에서 파악 가능 → 자동 채우고 다음
   - PRD에 없음 → 사용자에게 직접 질문
   - "skip" 입력 시 → AI 판단으로 채우고 계속

4. Epic 도출 → Feature 분리 → Task 세분화 → d{SP}0002_plan.md 저장
```

**질문 형식** (1개씩 순차):
```
[Plan 정보 수집 N/M] 항목명

PRD 파악 내용: [추출된 내용 또는 "PRD에 정보 없음"]
질문: [구체적 질문]

(skip 입력 시 AI 판단으로 대체)
```

> **완료 후 권장**: `oofeature needed` 실행 — plan.md Feature vs 상세 문서 교차 비교로 미착수 Feature 확인 (gate check)

**PRD 필요 조건** (웹 개발 프로젝트):

| 옵션 | PRD 필요 섹션 | 근거 |
|------|-------------|------|
| run epic | 페이지 개요 (5.1) | 대분류 기반 Epic 도출 |
| run feature | 페이지 상세 (5.2) | 페이지별 기능 정의 필요 |
| run task | 페이지 상세 (5.2) + 상세기획 | 구현 단위 분해 |

**진행 컬럼 필터링**: PRD 5.1 페이지 개요의 진행=아니오인 페이지는 Plan 생성 시 자동 제외

**하위 레벨 처리**:

| 옵션 | 범위 | 기존 하위 레벨 |
|------|------|--------------|
| run epic | Epic까지 | Feature/Task 삭제 |
| run feature | Feature까지 | Task 삭제 |
| run task (기본) | Task까지 | 전체 업데이트 |

### 5.2 detail
입력 분석 -> 태스크 구체화 -> 실행 계획 -> 사용자 승인

### 5.3 optimize
Plan 로드 -> PRD 정합성 -> 구조/일정 최적화 -> 리스크 검토 -> 업데이트

**체크**: PRD 커버리지 100% / 순환 의존성 없음 / 크리티컬 패스 최소화 / 스프린트 균형

### 5.4 sync
PRD 버전 확인 -> 변경 분석 -> Plan 업데이트

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ooplan run
```

### 서브명령어 활용
```bash
ooplan run  # 구현 계획 생성 실행
ooplan update  # 현행화 — 현재 코드/현황 스캔 → Plan 문서 변경분 반영
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|---------|------|------|:----:|
| 분석 | oh-my-claudecode:explore | haiku | 코드베이스/기술 스택 스캔 | O |
| 계획 수립 | oh-my-claudecode:planner | opus | Epic-Feature-Task 분해, 실행 계획, 리스크 파악 | - |
| 아키텍처 설계 | oh-my-claudecode:architect | opus | 시스템 설계, 인터페이스, 기술적 트레이드오프 | - |
| 계획 검토 | oh-my-claudecode:critic | opus | 계획 비판적 검토 및 개선 | - |
| 문서화 | task-executor | - | d{SP}0002_plan.md 작성 | - |
| 검증 | task-checker | - | 완성도/품질 검증 | - |

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
