# common_guide - 프로젝트 공통 가이드라인 중앙 문서

## 문서 이력 관리
- v16 2026-04-17 — 섹션 4.2.6 보강: `OAIS_NO_SP=1` 마커 및 oostart 자동 감지 규칙 명시
- v15 2026-03-16 — 섹션 4.2.6 추가: SP 미사용 독립 프로젝트 규칙 (3_code 등)
- v14 2026-03-01 — 섹션 4.2.4/6.2 수정: SP00 예외 표현 제거, 문서번호 = SP x 10000 + 기본번호 공식으로 통일
- v13 2026-03-01 — 섹션 4.2.4/6.1/6.2 수정: SP 파일명 패턴 올바르게 수정 (SP01~10은 d{SP번호}{4자리}, 예: d20001)
- v12 2026-02-24 — 섹션 4.2.5 추가: SP 내부 프로세스 번호 체계 및 문서 네이밍 규칙 (SP04 기준)

---

## 0. 필수 실행 규칙 (MANDATORY)

> **🚨 모든 Python 실행(스크립트, 도구, 테스트 등)은 반드시 `uv run` 명령어를 사용해야 합니다.**
> - **올바른 예**: `uv run python .claude/skills/oostart/scripts/oostart_run.py`
> - **잘못된 예**: `python .claude/skills/oostart/scripts/oostart_run.py`

---

## 1. 개요

이 문서는 AI 에이전트 종류에 독립적으로, **프로젝트 전체가 따라야 할 공통 원칙, 가이드라인, 워크플로우를 통합 관리하는 중앙 문서**입니다. `CLAUDE.md`나 `GEMINI.md`와 같은 특정 에이전트별 설정 파일, 또는 `.claude/skills/ooprd/SKILL.md`, `.claude/skills/oorun/SKILL.md`와 같은 개별 스킬 문서에 중복되거나 분산되어 있던 공통 가이드라인들을 이곳으로 모아, 모든 프로젝트 참여자와 AI 에이전트가 단일하고 일관된 정보원을 참조하도록 합니다. 이를 통해 유지보수성을 높이고, 정보의 일관성을 확보하며, 어떤 에이전트를 사용하든 프로젝트의 핵심 규칙을 명확히 이해하고 준수할 수 있도록 돕습니다.

---

## 2. 에이전트 활용 원칙

### 2.1 업무 처리 우선순위 (5단계)

| 단계 | 처리 방법 | 설명 |
|------|----------|------|
| 1 | 메인 에이전트 검토 | 모든 업무 요청은 메인 에이전트(Claude/Gemini 등)가 먼저 검토 |
| 2 | Skills 활용 | 프로젝트/범용 스킬 우선 사용 |
| 3 | 기타 MCP/도구 | Sequential Thinking, Context7, Playwright 등 |
| 4 | 서브에이전트 위임 | 병렬 처리 가능 작업 동시 위임 |

### 2.2 Subagent 기본 위임 규칙

> **에이전트 레퍼런스**: `agents.md` (프로젝트 루트) - 에이전트 검색 경로, 역할, 위임 규칙 통합 문서
> **에이전트 정의 파일 위치**: `agents.md`의 검색 경로 참조 (`.claude/agents/`)

| 작업 유형 | Subagent | 설명 | 정의 파일 |
|----------|----------|------|----------|
| 코드베이스 탐색 | Explore | 파일 찾기, 코드 검색, 구조 파악 | - (내장) |
| 코드 구현/수정 | task-executor | 기능 구현, 버그 수정, 리팩토링 | `.claude/agents/task-executor.md` |
| Python 코드 리뷰 | python-code-reviewer | 품질, 성능, 버그 검토 | `.claude/agents/python-code-reviewer.md` |
| 구현 검증 | task-checker | 완료된 작업 검증, QA | `.claude/agents/task-checker.md` |
| 품질 분석 | oo-qa | 중복 감지, 의존성 분석 | `.claude/agents/ooqa.md` |
| 복잡한 다중 작업 | (메인 에이전트) | 여러 subagent 조율 | 이 문서의 '에이전트 활용 원칙' 참조 |
| 웹앱 테스트 | web-test-orchestrator | E2E 테스트, Playwright | `.claude/agents/oo-web-test-orchestrator.md` |
| 데이터 분석 | data-analyst | 통계, 트렌드 분석 | `.claude/agents/data-analyst.md` |
| 학술 연구 | academic-researcher | 논문 검색, 문헌 분석 | `.claude/agents/academic-researcher.md` |

### 2.3 다중 에이전트 조율 조건

메인 에이전트는 다음 조건 중 하나라도 해당되면 **병렬 에이전트 조율 패턴**을 자동 활성화해야 합니다:

- 동시 수정 파일 3개 이상
- 복잡도 점수 0.8 이상 (자체 판단)
- 다중 도메인 작업 (예: frontend + backend + DB)
- 의존성 충돌 감지
- 10회 이상 반복 실패
- "종합", "전체", "comprehensive" 등의 키워드 포함 요청

### 2.4 에이전트 선택 요약

| 작업 유형 | 권장 에이전트 |
|----------|----------------|
| 새 코드 작성 후 빠른 검증 | `code-error-checker` |
| Python 코드 상세 리뷰 | `python-code-reviewer` |
| 알고리즘 분석/수정 | `python-code-reviewer` (`--focus algorithm`) |
| 개별 구현(기능 개발) | `task-executor` |
| 구현 완료 검증 | `task-checker` |
| 중복/의존성 분석 | `ooqa` |
| 웹앱 E2E 테스트 | `oo-web-test-orchestrator` |

### 2.5 python-code-reviewer 빠른 참조

- 기본: `python-code-reviewer`
- 한글 출력: `--lang ko`
- 알고리즘 집중 분석: `--focus algorithm`
- 수정 전 확인(사용자 승인): `--confirm`
- 예시: `python-code-reviewer --lang ko --focus algorithm --confirm`

### 2.6 워크플로 요약

- 새 기능 개발(간략):
  1. 메인 에이전트 → 작업 분석 및 분할
  2. `task-executor` → 구현
  3. `code-error-checker` → 즉시 오류 확인
  4. `python-code-reviewer` → 상세 리뷰 및 개선안
  5. `task-checker` → 최종 검증

- 알고리즘 버그 수정(간략):
  1. `python-code-reviewer --lang ko --focus algorithm` → 분석 보고서
  2. `python-code-reviewer --confirm` → 수정제안 및 승인
  3. `code-error-checker` → 수정 후 오류 확인

### 2.7 제거/통합된 에이전트 및 파일 위치

- 제거/통합 요약: `ooleader`, `task-orchestrator` 등은 메인 에이전트(Claude)로 역할 이동/통합됨.
- 백업 위치: `data/00_old/agents_backup/`
- 에이전트 파일 위치: `.claude/agents/`

### 2.8 [필수] 서브에이전트 코드 수정 후 구문 검증

> **⚠️ 중요**: 서브에이전트가 Python 파일을 수정한 후, **반드시 구문 검증을 수행**해야 합니다.
> 이 단계를 건너뛰면 docstring 중복, 미닫힌 따옴표 등의 구문 오류가 런타임에서 발생할 수 있습니다.

**필수 검증 명령어:**

```bash
uv run python -m py_compile <수정된파일.py>
```

**수정 완료 조건:**

```
서브에이전트 코드 수정 완료
          ↓
uv run python -m py_compile <파일>  ← [필수]
          ↓
오류 발생? → 수정 후 재검증
          ↓
성공 → 태스크 완료 처리
```

**주요 감지 대상:**

| 오류 유형 | 원인 | 해결 |
|----------|------|------|
| `unterminated string literal` | docstring 미닫힘/중복 | 따옴표 쌍 확인 |
| `invalid syntax` | 구문 오류 | 해당 라인 검토 |
| `IndentationError` | 들여쓰기 불일치 | 공백/탭 통일 |

### 2.9 명령어 참조

#### oo 스킬 ↔ SuperClaude 명령어 매핑

| oo 스킬 | SC 명령어 | 용도 |
|-----------|----------|------|
| oocheck | /analyze | 코드 분석 |
| oofix | /improve | 코드 개선 |
| ootest | /test | 테스트 실행 |
| oodoc | /document | 문서 생성 |
| oocommit | /git | Git 워크플로우 |
| ooenv | /load | 환경 분석 |
| ooprd | /design | 설계 |

#### 명령어 카테고리

| 카테고리 | 명령어 | 설명 |
|----------|--------|------|
| 개발 | `/build`, `/implement`, `/design` | 프로젝트 빌드, 기능 구현, 시스템 설계 |
| 분석 | `/analyze`, `/troubleshoot`, `/explain` | 코드 분석, 문제 조사, 설명 |
| 품질 | `/improve`, `/cleanup`, `/test` | 코드 개선, 정리, 테스트 |
| 문서 | `/document`, `/git` | 문서 생성, Git 워크플로우 |

#### 인자 형식

```
@<경로>      파일/폴더 지정     /analyze @src/api/
!<명령어>    셸 명령어 실행     /build !npm run build
--<플래그>   옵션 지정          /improve --think
```

> **권장**: SuperClaude 명령어 대신 oo 스킬 사용 (예: `/analyze` 대신 `oocheck run`)

### 2.10 플래그 참조

#### 분석 플래그

| 플래그 | 토큰 | 용도 | 자동 활성화 |
|--------|------|------|------------|
| `--think` | ~4K | 다중 파일 분석 | import 체인 >5 파일 |
| `--think-hard` | ~10K | 아키텍처 분석 | 시스템 리팩토링, 보안 취약점 |
| `--ultrathink` | ~32K | 시스템 전체 분석 | 레거시 현대화, 중대 취약점 |

#### 효율 플래그

| 플래그 | 효과 | 자동 활성화 |
|--------|------|------------|
| `--uc` | 30-50% 토큰 절감 | context >75% |
| `--plan` | 실행 전 계획 표시 | - |
| `--validate` | 사전 검증 | - |
| `--safe-mode` | 최대 검증 모드 | 운영 환경, 리소스 >85% |

#### MCP 서버 플래그

| 플래그 | 서버 | 용도 |
|--------|------|------|
| `--c7` | Context7 | 라이브러리 문서 조회 |
| `--seq` | Sequential | 복잡한 분석 |
| `--magic` | Magic | UI 컴포넌트 생성 |
| `--play` | Playwright | E2E 테스트 |
| `--all-mcp` | 전체 | 모든 서버 활성화 |
| `--no-mcp` | - | 서버 비활성화 |

#### 범위/반복 플래그

```
--scope file|module|project|system    범위 지정
--focus performance|security|quality  집중 영역
--loop                                반복 개선 (기본 3회)
--iterations [n]                      반복 횟수 지정
```

#### 플래그 우선순위

1. 안전 플래그 > 최적화 플래그
2. 명시적 플래그 > 자동 활성화
3. `--ultrathink` > `--think-hard` > `--think`
4. `--no-mcp`가 모든 MCP 플래그 무효화

### 2.11 MCP 서버 참조

#### 서버 개요

| 서버 | 용도 | 플래그 | 자동 활성화 |
|------|------|--------|------------|
| **Context7** | 라이브러리 문서, 패턴 | `--c7` | 외부 라이브러리 import, 프레임워크 질문 |
| **Sequential** | 복잡한 분석, 추론 | `--seq` | 복잡한 디버깅, 시스템 설계, `--think` 플래그 |
| **Magic** | UI 컴포넌트 생성 | `--magic` | UI 컴포넌트 요청, 디자인 시스템 |
| **Playwright** | E2E 테스트, 브라우저 | `--play` | 테스트 워크플로우, 성능 모니터링 |

#### 서버 선택 가이드

| 작업 유형 | 추천 서버 |
|----------|----------|
| 라이브러리 사용법 | Context7 |
| 버그 분석 | Sequential |
| UI 개발 | Magic |
| 테스트 작성 | Playwright |
| 복잡한 설계 | Sequential + Context7 |

#### 에러 복구

| 서버 | 폴백 전략 |
|------|----------|
| Context7 없음 | WebSearch → 수동 구현 |
| Sequential 타임아웃 | 네이티브 분석 → 제한 표시 |
| Magic 실패 | 기본 컴포넌트 → 수동 개선 |
| Playwright 연결 끊김 | 수동 테스트 → 테스트케이스 제공 |

### 2.12 페르소나 참조

11개의 전문 페르소나로 도메인별 최적화된 AI 동작 제공. 활성화: `--persona-[name]` 플래그 또는 자동 감지.

#### 기술 전문가

| 페르소나 | 역할 | 우선순위 | 주요 MCP |
|----------|------|----------|----------|
| `--persona-architect` | 시스템 설계, 장기 아키텍처 | 유지보수성 > 확장성 > 성능 | Sequential |
| `--persona-frontend` | UI/UX, 접근성 | 사용자 > 접근성 > 성능 | Magic |
| `--persona-backend` | 서버, API, 데이터 무결성 | 신뢰성 > 보안 > 성능 | Context7 |
| `--persona-security` | 위협 모델링, 취약점 분석 | 보안 > 규정준수 > 신뢰성 | Sequential |
| `--persona-performance` | 최적화, 병목 제거 | 측정 → 최적화 → UX | Playwright |

#### 프로세스/품질 전문가

| 페르소나 | 역할 | 우선순위 | 주요 MCP |
|----------|------|----------|----------|
| `--persona-analyzer` | 근본 원인 분석, 조사 | 증거 > 체계적 접근 | Sequential |
| `--persona-qa` | 품질 보증, 테스트 | 예방 > 감지 > 수정 | Playwright |
| `--persona-refactorer` | 코드 품질, 기술 부채 | 단순함 > 유지보수성 | Sequential |
| `--persona-devops` | 인프라, 배포 자동화 | 자동화 > 관찰성 | Sequential |

#### 지식/커뮤니케이션

| 페르소나 | 역할 | 주요 MCP |
|----------|------|----------|
| `--persona-mentor` | 교육, 지식 전달 | Context7 |
| `--persona-scribe=lang` | 문서화, 로컬라이제이션 (en, ko, ja 등) | Context7 |

#### oo 스킬과 페르소나 매핑

| oo 스킬 | 권장 페르소나 |
|-----------|--------------|
| oocheck | analyzer |
| oofix | refactorer |
| ootest | qa |
| oodoc | scribe=ko |
| oocommit | devops |

### 2.13 OMC 모델 라우팅 규칙

> **참조**: `.claude/skills/omc-reference/SKILL.md` | `~/.claude/CLAUDE.md`

서브에이전트 위임 시 반드시 아래 모델을 명시하여 비용/성능을 최적화합니다.

| 모델 | 용도 | 대표 에이전트 |
|------|------|-------------|
| **haiku** | 빠른 탐색, 경량 스캔, 문서 요약 | `explore`, `writer` |
| **sonnet** | 표준 구현, 디버깅, 리뷰, 검증 | `executor`, `debugger`, `verifier`, `test-engineer`, `quality-reviewer`, `security-reviewer`, `scientist` |
| **opus** | 아키텍처, 심층 분석, 복잡한 계획 | `architect`, `analyst`, `planner`, `critic`, `code-reviewer`, `code-simplifier` |

**적용 방법**:
- Agent 도구 호출 시: `subagent_type="oh-my-claudecode:executor", model="sonnet"`
- 복잡한 구조 분석: `model="opus"` 명시
- SKILL.md 서브에이전트 테이블: `| 모델 |` 컬럼 추가

```
탐색(haiku) → 구현(sonnet) → 검증(sonnet)
복잡한 계획/설계 → opus 사용
```

---

## 3. 개발 가이드라인

### 3.1 코드 품질 표준

- 깨끗하고, 읽기 쉬우며, 유지보수 가능한 코드 작성
- 프로젝트 전체에서 일관된 명명 규칙 따르기
- 의미 있는 변수 및 함수 이름 사용
- 함수는 단일 목적에 집중
- 복잡한 로직 및 비즈니스 규칙에 주석 추가

### 3.2 Git 워크플로우

- Conventional Commits 형식 사용
- 새로운 개발을 위한 기능 브랜치 생성
- 커밋은 원자적이고 단일 변경사항에 집중
- 병합 전 코드 리뷰를 위한 풀 리퀘스트 사용

### 3.3 문서화

- 공개 API 및 인터페이스 문서화
- 복잡한 기능에 대한 사용 예제 포함
- 변경 시 문서 업데이트

### 3.4 테스트 접근법

- 새로운 기능 및 버그 수정에 대한 테스트 작성
- 좋은 테스트 커버리지 유지
- 변경사항 커밋 전 테스트 실행

### 3.5 보안 모범 사례

- 민감한 정보(API 키, 비밀번호, 토큰) 절대 커밋하지 않기
- 설정에 환경 변수 사용
- 입력 데이터 검증 및 출력 살균
- 의존성을 최신 상태로 유지

### 3.6 설계 원칙

#### 핵심 지침

**"증거 > 가정 | 코드 > 문서 | 효율 > 장황함"**

#### SOLID 원칙

| 원칙 | 설명 |
|------|------|
| **S**ingle Responsibility | 클래스/함수는 하나의 변경 이유만 |
| **O**pen/Closed | 확장에 열려있고, 수정에 닫혀있음 |
| **L**iskov Substitution | 파생 클래스는 기본 클래스 대체 가능 |
| **I**nterface Segregation | 불필요한 인터페이스 의존 금지 |
| **D**ependency Inversion | 추상화에 의존, 구체화에 의존 X |

#### 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **DRY** | 중복 제거 |
| **KISS** | 단순하게 유지 |
| **YAGNI** | 필요할 때만 구현 |

#### 품질 기준

- **에러 처리**: Fail Fast (즉시 감지, 명확한 컨텍스트), 절대 묵살 금지
- **테스트**: 테스트 피라미드 (유닛 > 통합 > E2E), 커버리지 유닛 ≥80%, 통합 ≥70%
- **의존성**: 표준 라이브러리 우선, 취약점 지속 모니터링
- **성능**: 측정 우선 (가정 전 측정), 성능 = 기능

#### 8단계 품질 게이트

```
1. 문법 검사    5. 테스트 (커버리지)
2. 타입 검사    6. 성능 검사
3. 린트 검사    7. 문서 검사
4. 보안 검사    8. 통합 테스트
```

#### 복잡도 분류

| 레벨 | 지표 | 토큰 예산 |
|------|------|----------|
| simple | 단일 파일, <3단계 | 5K |
| moderate | 다중 파일, 3-10단계 | 15K |
| complex | 시스템 전체, >10단계 | 30K+ |

---

## 4. 운영 지침 (MIG)

### 4.1 핵심 운영 규칙

| 항목 | 규칙 |
|------|------|
| 언어 | 항상 한국어로 답변 |
| 인코딩 | UTF-8 출력 필수 |
| 실행 환경 | Python은 `uv run`으로 실행 |

- 모든 Python 실행 및 자동화 스킬은 `uv run`을 통해 실행되어야 하며, oorun 등 자동화 워크플로우도 `uv run`으로 호출해야 합니다.

| 경로 | 절대경로 사용 금지, 상대경로 사용 |
| **[필수] 프로젝트 루트** | 설정 파일(*.md, *.toml, *.json)만 허용, **py/임시파일 생성 절대 금지** |
| **[필수] 임시 파일** | 모든 테스트/디버그/임시 출력 파일은 **반드시 `tmp/` 폴더에만 생성** |
| 에러 처리 | `try-except` 구문 생성 금지 (에러 시 즉시 중단) |
| 버전 관리 | 파일 업버전 요청 전까지 새버전 생성 금지 |
| 이모지 | 웹페이지 이외에는 이모지 사용 금지 |
| 실행 영향 범위 정책 | 수정/실행 전 영향 범위 분석 (자동 커밋 금지; 파일 변경은 Read→Write/Edit; 문서 업데이트는 00_doc/*.md 범위; 새 파일 생성은 제한적; 중요 작업은 --interactive 권장) |

### 4.2 디렉토리 구조

#### 4.2.1 프로젝트 유형별 폴더 구조

**Type A: 알고리즘 위주 프로젝트** (웹서버 없음)

```text
project_root/
├── src/          # 소스 코드 (알고리즘, 스크립트)
├── data/         # 데이터 파일
├── oo/         # oo 공통 모듈
└── v/            # 스킬 문서
```text

> **예시**: `d:\3_code\0013_dualbranck\`
> **특징**: 단순한 구조, 알고리즘 개발/연구/분석 목적

**Type B: 웹서버 포함 프로젝트** (다중 서브프로젝트)

```text
project_root/
├── 01_algorithm/     # 알고리즘 서브프로젝트
├── 02_1st_server/    # 1차 서버 (예: 백엔드 API)
├── 03_2nd_server/    # 2차 서버 (예: 프론트엔드)
├── data/             # 공유 데이터 파일
├── oo/             # oo 공통 모듈
├── db/               # 데이터베이스
├── 00_doc/              # 프로젝트 문서
└── v/                # 스킬 문서
```text

> **예시**: `d:\3_code\0003_CCone\`
> **특징**: 복합 구조, 서브프로젝트별 독립 개발 및 통합

**Type C: 에이전트/CLI 도구 프로젝트** (신규)

```text
project_root/
├── v/                # 스킬 및 에이전트 문서 (핵심)
├── src/              # CLI 소스 코드 (진입점 등)
├── tests/            # 단위/통합 테스트 (SP별 서브폴더: tests/sp{00}/, 공통은 tests/sp00/)
├── 00_doc/              # 프로젝트 관리 문서 (PRD, Plan, Todo, History)
├── .claude/          # Claude 설정
├── .gemini/          # Gemini 설정
├── oo/             # oo 공통 모듈 (선택)
└── data/             # 테스트 데이터
```

> **예시**: `d:\3_code\0001_agent\01_sanbox\`
> **특징**: 에이전트 스킬(`v/*.md`) 정의와 CLI 도구 개발이 핵심. `00_doc/` 문서를 통한 관리 중요.

#### 4.2.2 공통 디렉토리 설명

| 디렉토리 | 용도 |
|----------|------|
| `oo/` | oo 모듈 (공통 유틸리티) |
| `data/` | 데이터 파일 |
| `00_doc/` | 문서 (Type B/C에서 필수), `sp00/`~`spNN/` 서브폴더로 SP별 분리 |
| **`tmp/`** | **[필수]** 모든 임시/테스트/디버그 파일 생성 위치 (프로젝트 루트에 py 파일 생성 금지) |
| `db/` | 데이터베이스 (Type B에서 사용) |
| `v/` | 스킬 문서 |
| `.claude/agents/` | 에이전트 정의 문서 |
| `.claude/commands/sc/` | 프로젝트 공통 명령어 정의 |
| `.claude/templates/` | 재사용 템플릿 |
| `src/` | 소스 코드 (Type A/C에서 사용) |

#### 4.2.3 프로젝트 유형 선택 기준

| 조건 | 권장 유형 |
|------|----------|
| 알고리즘 개발/연구/분석 | Type A |
| 단일 스크립트 실행 | Type A |
| 웹서버/API 포함 | Type B |
| 다중 서비스 통합 | Type B |
| 데이터베이스 사용 | Type B |
| **에이전트 스킬 개발** | **Type C** |
| **CLI 도구 개발** | **Type C** |

#### 4.2.4 서브프로젝트 정의 규칙

서브프로젝트는 **프로젝트 루트의 `01_*` ~ `10_*` 디렉토리만 해당**합니다.

| 항목 | 규칙 |
|------|------|
| 서브프로젝트 범위 | 루트의 `01_*` ~ `10_*` 패턴 디렉토리만 인식 |
| 최대 개수 | 10개 (SP01 ~ SP10) |
| 내부 하위 폴더 | 서브프로젝트 내부의 폴더(예: `01_algorothm/ps00~ps99`)는 카테고리이며 서브프로젝트가 아님 |
| 감지 도구 | `oostart run`에서 자동 스캔 |
| 문서 번호 체계 | `문서번호 = SP x 10000 + 기본번호` 공식 적용 (예: SP00 → d0001~d9999, SP02 → d20001~d29999, SP04 → d40001~d49999) |

#### 4.2.5 SP 내부 프로세스 번호 체계 및 문서 네이밍 규칙

> **적용 대상**: SP 내부에 `psNNNN_` 패턴의 서브폴더를 사용하는 서브프로젝트 (예: SP04 `04_oorag/`)

일부 서브프로젝트는 내부적으로 **4자리 프로세스 번호(`psNNNN_`)** 로 서브폴더를 구분합니다. 이때 각 서브폴더가 나타내는 역할과 해당 문서의 네이밍 규칙은 아래와 같습니다.

**프로세스 번호 역할 분류 (SP04 기준):**

| 번호 범위 | 역할 | 예시 폴더 |
|----------|------|----------|
| `ps1000~1999` | 데이터 (Data) | `ps1010_dataset/` |
| `ps2000~2999` | 전처리 (Preprocessing) | `ps2010_preprocess/` |
| `ps3000~3999` | 베이스라인 모델 (Baseline) | `ps3010_baseline/` |
| `ps4000~9999` | 응용 모델 (Applied Models) | `ps4010_rag/`, `ps4020_finetuning/` |

**문서 네이밍 규칙:**

프로세스별 분석/설계 문서는 `00_doc/` 아래에 **SP번호 + 프로세스 번호** 를 prefix로 사용합니다.

```
형식: d{SP번호(1자리)}{프로세스 번호(4자리)}_{설명}.md
위치: 00_doc/

예시 (SP04, 프로세스 ps1110):
  00_doc/sp04/d41110_ps1110_rag_proto.md
```

| 항목 | 규칙 |
|------|------|
| prefix 형식 | `d` + SP번호(1자리) + 프로세스번호(4자리) = 5자리 숫자 |
| SP04 예시 | `d4` + `1110` = `d41110_` |
| 공통 문서 구분 | `d0001_prd.md` 등 기본번호(d0001~d0999)는 SP 공통 문서로 유지 |
| 프로세스 문서 범위 | `d41000`~`d49999` (SP04 기준), `d51000`~`d59999` (SP05 기준) |

**예시 파일 트리 (SP04):**

```text
00_doc/
├── d40001_prd.md          # SP04 공통 PRD
├── d40004_todo.md         # SP04 공통 TODO
├── d40010_history.md      # SP04 공통 이력
├── d41010_ps1010_data.md  # ps1010 데이터 분석 문서
├── d41110_ps1110_rag_proto.md  # ps1110 RAG 프로토타입 문서
└── d44010_ps4010_model.md # ps4010 응용 모델 문서
```

#### 4.2.6 SP 미사용 독립 프로젝트 규칙

> **적용 대상**: `D:/3_code/NNNN_*/` 등 OAIS SP 체계 밖에서 운영되는 독립 프로젝트

독립 프로젝트는 `01_*`~`10_*` 서브프로젝트 구조를 갖지 않으며, SP 체계 없이 단일 프로젝트로 관리됩니다.

**핵심 규칙:**

| 항목 | 규칙 |
|------|------|
| SP 체계 | 사용 안 함 (SP 번호 없음) |
| oocontext | 기본값 SP=00 (공통) 으로 동작 |
| 문서 위치 | 프로젝트 루트의 `00_doc/` (sp 서브폴더 없음) |
| 문서 번호 | 기본번호만 사용 (d0001~d9999) |
| oo 스킬 | SP=00 기준으로 동작 (todo → `d0004`, history → `d0010`) |
| vibe 동기화 | `oosync`로 OAIS 설정(.claude/) 동기화 |

**독립 프로젝트 마커 (`OAIS_NO_SP`):**

`01_*`~`10_*` 패턴 폴더가 있어도 SP가 아닌 콘텐츠/데이터 버킷인 경우(예: `03_paper`의 `01_book_ko/`, `11_paper_en/`), 명시적 마커로 SP 오탐을 방지한다.

| 우선순위 | 판정 기준 | 결과 |
|:--------:|----------|------|
| 1 | `.env`에 `OAIS_NO_SP=1` | 독립 프로젝트 확정 (SP 스캔 스킵) |
| 2 | `00_doc/` 존재 + `00_doc/sp00~sp99/` 서브폴더 없음 + `d*.md` 직접 존재 | 독립 프로젝트 자동 추정 |
| 3 | 그 외 | SP 모드 (`01_*`~`10_*` 스캔) |

**oostart 동작:**
- 독립 프로젝트로 판정되면 `## 0-1. Subproject Status` 섹션에서 SP 스캔 생략 및 안내 메시지 출력
- 문서 체크 경로를 `00_doc/sp00/`에서 `00_doc/`로 자동 전환
- `## 5. 컨텍스트 설정`에서 `oocontext` 전환 안내 대신 독립 프로젝트 규칙 안내

**문서 구조 예시 (독립 프로젝트):**

```text
project_root/
├── 00_doc/
│   ├── d0001_prd.md       # PRD (sp 서브폴더 없음)
│   ├── d0004_todo.md      # TODO
│   └── d0010_history.md   # 이력
└── ...
```

**OAIS 서브프로젝트와 비교:**

| 항목 | OAIS 서브프로젝트 | 독립 프로젝트 |
|------|:----------------:|:-----------:|
| SP 체계 | O (SP01~SP10) | X |
| 문서 경로 | `00_doc/dNN000N.md` | `00_doc/sp00/d000N.md` |
| oocontext | `oocontext N` | 기본값(00) 고정 |
| 관리 방식 | OAIS 통합 관리 | 프로젝트별 독립 |
| vibe 동기화 | - | `oosync` |

---

## 5. 테스트 및 품질 관리

### 5.1 테스트 전략

| 유형 | 범위 | 도구 | 책임 |
|------|------|------|------|
| Unit | 함수/클래스 | pytest | 개발자 |
| Integration | API/서비스 | pytest | 개발자 |
| E2E | 사용자 시나리오 | Playwright | QA |
| Security | 취약점 | OWASP ZAP | 보안팀 |

### 5.2 커버리지 기준

| 유형 | 목표 |
|------|------|
| Unit Test | 80% |
| Integration | 70% |
| E2E Critical Path | 100% |

### 5.3 릴리스 기준 (Definition of Done)

- [ ] 코드가 확립된 규칙을 따르는가 (`.claude/guides/common_guide.md` 준수)
- [ ] 테스트가 작성되고 통과하는가
- [ ] 문서가 업데이트되었는가
- [ ] 보안 고려사항이 해결되었는가
- [ ] 성능 영향이 고려되었는가
- [ ] 코드가 유지보수성 측면에서 검토되었는가

### 5.4 최종 검토 체크리스트

작업을 완료로 표시하기 전, 다음을 확인하십시오:

- [ ] 코드가 확립된 표준을 준수하는가?
- [ ] 테스트가 작성되었고 통과하는가?
- [ ] 문서가 업데이트되었는가?
- [ ] 보안 고려사항이 해결되었는가?
- [ ] 성능 영향이 고려되었는가?
- [ ] 코드가 유지보수 가능한가?

### 5.5 oo 스킬 체크리스트 표준

> **템플릿**: `.claude/templates/oo_checklist_template.md`

모든 oo* 스킬의 `references/checklist.md`는 이 템플릿을 준수해야 한다.

**필수 구조**:

| 요소 | 규칙 |
|------|------|
| 포맷 | ID 테이블 (`C01`~`C10`) |
| 공통 항목 | C01(필수 파일 존재), C02(버전 일치) — 모든 스킬 필수 |
| 고유 항목 | C03 이후 — 스킬별 검증 항목 추가 (5~10개 권장) |
| 심각도 | CRITICAL / ERROR / WARNING / INFO |
| 출력 형식 | `[스킬명] check` → `C01 항목명 [OK/WARN/ERROR]` + 소계 |

**준수 검증**: `ooskill check` 실행 시 각 스킬의 checklist.md가 템플릿 구조를 따르는지 확인

---

## 6. 문서 관리 정책

### 6.1 PRD와 Plan 문서 역할 구분

프로젝트의 요구사항과 구현 계획을 명확히 분리하여 관리합니다. **중복 기재 금지** 원칙을 엄격히 적용합니다.

*   **`00_doc/sp00/d0001_prd.md` (제품 요구사항 정의서 - PRD):**
    *   **역할**: "무엇을(What)" 만들 것인지 정의합니다.
    *   **내용**: 기능 요구사항, 비기능 요구사항, 사용자 스토리, 비전 및 목표를 포함합니다.
    *   **주의**: 이 문서에는 기능의 **구현 상태(예: 완료, 진행 중)를 포함하지 않습니다.** 기능의 우선순위(Must, Should, Could)까지만 정의합니다.
    *   **SP 전용 PRD**: 서브프로젝트별 PRD는 `00_doc/d{NN}0001_prd.md`에 작성 (예: SP02 → `00_doc/sp02/d20001_prd.md`)

*   **`00_doc/sp00/d0002_plan.md` (구현 계획):**
    *   **역할**: PRD의 요구사항을 "어떻게(How)" 그리고 "언제(When)" 구현할 것인지 계획합니다.
    *   **내용**: Epic, 작업 분해(WBS), 스프린트 계획, 마일스톤, 그리고 각 기능의 **구현 상태(예: 완료, 진행예정)** 를 포함합니다.
    *   **프로세스**: PRD의 기능 목록은 이 문서의 WBS나 Epic 목록으로 구체화되며, 여기서 상태를 추적합니다.

#### 6.1.1 PRD/Plan 콘텐츠 소유권 매트릭스

| 항목 | PRD (What) | Plan (How/When) | 위반 시 |
|------|:----------:|:---------------:|---------|
| 목적/범위/비전 | **소유** | 1줄 참조만 | Plan에서 삭제 → `PRD §N 참조` |
| 기능 요구사항 (목록/상세) | **소유** | 참조만 | Plan에서 삭제 |
| 사용자 스토리/페르소나 | **소유** | X | Plan에서 삭제 |
| UI/UX 요구사항 | **소유** | X | Plan에서 삭제 |
| 비기능 요구사항 | **소유** | X | Plan에서 삭제 |
| 데이터 요구사항 (소스/주기) | **소유** | X | Plan에서 삭제 |
| 기술 스택 상세 | 1줄 요약만 | **소유** | PRD에서 삭제 → `Plan §N 참조` |
| 폴더 구조 | X | **소유** | PRD에서 삭제 |
| DB DDL/스키마 | X (테이블 목적만) | **소유** | PRD에서 DDL 삭제 |
| WBS/스프린트/마일스톤 | X | **소유** | PRD에서 삭제 |
| 구현 상태 추적 | X | **소유** | PRD에 상태 컬럼 금지 |
| 리스크 (비즈니스) | **소유** | 참조만 | Plan에서 삭제 |
| 리스크 (기술/일정) | X | **소유** | PRD에서 삭제 |
| 의사결정 로그 | X | **소유** | PRD에서 삭제 |

> **원칙**: 한 항목은 반드시 한 문서만 소유(O). 다른 문서는 `d{SP}000N §섹션번호 참조` 형태로만 언급.

### 6.2 00_doc/ flat 구조 (SP별 파일명 prefix로 구분)

모든 문서는 프로젝트 루트의 `00_doc/` 한 곳에 flat으로 배치합니다. SP 구분은 파일명 prefix로 수행합니다.

**디렉토리 구조:**

```text
00_doc/
├── d0001_prd.md          # SP00 공통 PRD
├── d0004_todo.md         # SP00 공통 TODO
├── d0010_history.md      # SP00 공통 이력
├── d10001_prd.md         # SP01 전용 PRD
├── d20001_prd.md         # SP02 전용 PRD
├── d20010_history.md     # SP02 전용 이력
└── dNN000N_*.md          # SP N 전용 문서
```

**규칙:**

| 항목 | 규칙 |
|------|------|
| 구조 | flat (sp 서브폴더 없음) |
| 파일명 | `문서번호 = SP x 10000 + 기본번호` 공식 적용 (예: SP00=`d0001`~`d9999`, SP01=`d10001`~`d19999`, SP02=`d20001`~`d29999`) |
| SP00 공통 | `00_doc/sp00/d0001~d9999` — 전체 프로젝트에 걸친 공통 문서 |
| SP 전용 | `00_doc/dNN*` — 해당 서브프로젝트 전용 문서 (파일명 prefix로 구분) |
| 교차 참조 | `00_doc/sp02/d20001_prd.md` 형식으로 경로 명시 |

**oocontext 연동:**

| `oocontext` 설정 | TODO 경로 | HISTORY 경로 |
|--------------------|-----------|--------------|
| `oocontext 00` | `00_doc/sp00/d0004_todo.md` | `00_doc/sp00/d0010_history.md` |
| `oocontext 02` | `00_doc/sp02/d20004_todo.md` | `00_doc/sp02/d20010_history.md` |
| `oocontext 09` | `00_doc/sp09/d90004_todo.md` | `00_doc/sp09/d90010_history.md` |

> 파일이 없으면 oo 스킬이 자동 생성

### 6.3 문서 이력 관리 규칙

모든 스킬 문서(`.claude/skills/oo*/SKILL.md`), 가이드 문서(`.claude/guides/*.md`, `.claude/skills/oo*/references/guide.md`), 핵심 문서(`00_doc/d*.md`)의 "문서 이력 관리" 섹션은 **최근 5개 항목만 유지**합니다.

**규칙**:

| 항목 | 내용 |
|------|------|
| 유지 개수 | 최근 5개 버전만 유지 |
| 삭제 대상 | 6번째 이후 오래된 이력 |
| 적용 시점 | 문서 업데이트 시 자동 정리 |
| 검증 도구 | `oodoc validate` |
| 자동 수정 | `oodoc validate --fix` |

**예시**:
```markdown
## 문서 이력 관리
- v10 2026-01-18 — 최신 변경
- v09 2026-01-15 — ...
- v08 2026-01-10 — ...
- v07 2026-01-05 — ...
- v06 2026-01-01 — 가장 오래된 유지 항목
```

**적용 대상**:
- `.claude/skills/oo*/SKILL.md` (정식 스킬 문서, 구 v/oo*.md)
- `.claude/guides/*.md` (공통 가이드 문서)
- `.claude/skills/oo*/references/guide.md` (스킬별 가이드 문서)
- `00_doc/d*.md` (핵심 문서)
- `.claude/*.md` (SuperClaude 문서)

### 6.4 스킬 버전 관리 규칙

모든 oo 스킬(`.claude/skills/oo*/SKILL.md`)은 다음 버전 관리 규칙을 따릅니다.

**필수 요소**:

| 항목 | 설명 | 예시 |
|------|------|------|
| 문서 이력 관리 섹션 | 문서 상단에 버전 테이블 | `## 문서 이력 관리` |
| version 서브명령어 | 서브명령어 테이블에 포함 | `ooXXX version` |
| 버전 형식 | `vNN` 또는 `vN.N` | `v01`, `v3.3` |

**version 서브명령어 출력 형식**:
```
ooXXX version
- 스킬: ooXXX
- 버전: vNN
- 최종 수정: YYYY-MM-DD
- 설명: 스킬 한줄 설명
```

**버전 업데이트 시점**:
- 서브명령어 추가/삭제
- 워크플로우 변경
- 에이전트 매핑 변경
- 기능 추가/변경

**검증 도구**:
- `ooenv validate --full`: 스킬 정합성 검증 (버전 포함)
- `ooskill version`: 전체 스킬 버전 일괄 조회

### 6.5 oo 스킬 기본 실행 규칙

> **모든 oo* 스킬 필수**: 서브명령어 없이 `oo*`만 호출하면 `oo* run`으로 기본 동작한다.

| 호출 | 동작 |
|------|------|
| `oodev` | `oodev run` 실행 |
| `ooscrap` | `ooscrap run` 실행 |
| `ootutorial` | `ootutorial run` 실행 |

**적용 대상**:
- AI가 SKILL.md를 읽고 직접 처리하는 스킬: AI가 `run` 서브명령어로 간주하여 실행
- 스크립트 기반 스킬: `argparse`에서 `command is None`일 때 `run` 함수 호출

**검증**: `ooskill check` C06 항목

### 6.6 help 서브명령어 표준

> **모든 oo* 스킬 필수**: `oo* help`는 **파이썬 스크립트를 실행**하여 출력한다. AI가 SKILL.md를 직접 읽어 출력하는 것은 C14 위반.

| 호출 | 동작 |
|------|------|
| `oodoc help` | `uv run python .claude/skills/oodoc/scripts/oodoc_run.py help` 실행 |
| `oocheck help` | `uv run python .claude/skills/oocheck/scripts/oocheck_run.py help` 실행 |
| `oo* help` (공통) | `uv run python .claude/skills/{스킬명}/scripts/{스킬명}_run.py help` 실행 |

**처리 방식**:
- Claude가 `oo* help` 요청을 받으면 → 반드시 위 스크립트를 Bash로 **실행**하고 그 출력을 보여준다
- 스크립트 내부에서 SKILL.md 서브명령어 섹션 테이블을 파싱하여 출력 (단일 진실 공급원)
- **AI 직접출력 금지**: SKILL.md를 읽어 직접 출력하면 C14 위반

**검증**: `ooskill check` C12(스크립트 존재), C13(출력 포맷), C14(AI 직접출력 금지) 항목

---

## 7. 관련 문서

- `GEMINI.md`, `CLAUDE.md`: 각 AI 에이전트별 특화 설정
- `.claude/skills/oo*/SKILL.md`: 개별 oo 스킬 정의 문서 (정식 스킬)

---

## 8. 병렬 에이전트 실행 가이드 (요약)

- 목적: 코드 분석/검증 시 여러 에이전트를 병렬 실행하여 검사 범위를 확대하고 결과를 통합 보고하기 위함.
- 권장 병렬 구성: `code-error-checker`, `python-code-reviewer`, `oo-qa` (run_in_background=true).
- 우선순위 분류: P1(즉시조치), P2(권장수정, 1주), P3(개선권고) 기준 적용.
- 결과 포맷: 문서용 Markdown 템플릿(문서 예: RESULT_FORMAT)과 운영용 기계판독 JSON 출력 옵션 병행 권장.
- 운영 권고: CLAUDE.md의 '실행 영향 범위 정책' 준수(자동 커밋 금지; 파일 변경은 Read→Write/Edit; 문서 업데이트는 00_doc/*.md 범위; 중요 작업은 --interactive 권장). 또한 실행 타임아웃/재시도 정책과 결과 병합(우선순위 기반) 규칙을 명시할 것.
- 사용법: Claude 프롬프트(get_claude_prompt) 또는 `oocheck` 명령(`oocheck`, `oocheck <path>`)을 통해 실행.

참고: 자세한 구현/프롬프트 예시는 `00_doc/parallel_check.md`를 참고하세요. (권장: 운영 신뢰성 강화를 위해 JSON 출력, 타임아웃/재시도 규칙을 도입)

---

## 9. `this` 키워드 — 마지막 작업 대상 추적

### 9.1 개요

`this`는 **직전 스킬 실행의 작업 대상**을 자동 참조하는 키워드입니다.

```
oodev run d41001     → last_target 저장
ootest run this      → last_target 로드 → d41001 관련 TC 실행
oocheck run this     → last_target 로드 → 해당 파일만 체크
```

### 9.2 last_target 저장 위치

`.claude/last_target.json`

```json
{
  "skill": "oodev",
  "command": "run",
  "target": "d41001",
  "files": ["src/crawler.py", "src/source_manager.py"],
  "sp": "04",
  "timestamp": "2026-04-07T10:30:00"
}
```

---

## 10. QMD 마크다운 문서 검색

### 10.1 검색 도구 선택 기준

| 검색 대상 | 권장 도구 | 비고 |
|----------|---------|------|
| 마크다운 문서 **내용** (키워드) | `mcp__qmd__query` (lex) | BM25 정확 매칭 |
| 마크다운 문서 **내용** (의미) | `mcp__qmd__query` (vec) | 자연어 의미 기반 |
| 파일 **경로** 패턴 | `Glob` | 경로 패턴 최적화 |
| 코드 내 특정 **문자열** | `Grep` | 정규식 지원 |

> **원칙**: 마크다운 문서 내용을 찾을 때는 Glob/Grep 대신 `mcp__qmd__query` 우선 사용.
> qmd 미가동 시 Glob/Grep으로 폴백.

### 10.2 MCP 쿼리 사용법

```json
{
  "searches": [
    { "type": "lex", "query": "PRD 요구사항 SP04" },
    { "type": "vec", "query": "스크래핑 기능 구현 방법" }
  ],
  "collections": ["1_oais"],
  "limit": 5
}
```

| 타입 | 방법 | 적합한 입력 |
|------|------|-----------|
| `lex` | BM25 키워드 | 정확한 용어, 코드 식별자, 문서번호 |
| `vec` | 벡터 의미 검색 | 자연어 질문, 기능 설명 |
| `hyde` | 가상 문서 검색 | 예상 답변 50~100자 작성 |

### 10.3 인덱싱 유지 전략

| 시점 | 명령 | 비고 |
|------|------|------|
| 세션 시작 | `qmd update` | `oostart run` 자동 실행 |
| 문서 대량 추가 후 | `qmd update` | 수동 실행 |
| 의미 검색 필요 시 | `qmd embed` | 느림 (Vulkan GPU) |
| **최초 설정** | `qmd collection add . --name 1_oais` | 프로젝트 1회 |

### 10.4 컬렉션 초기 설정 (신규 프로젝트)

```bash
qmd collection add . --name {프로젝트명}   # 컬렉션 등록
qmd update                                 # BM25 인덱싱
qmd embed                                  # 벡터 임베딩 (선택)
```

> `.mcp.json`에 qmd 서버 등록 필요 (Windows: `command: "qmd.cmd"`)

| 필드 | 설명 |
|------|------|
| `skill` | 마지막 실행 스킬명 |
| `command` | 서브명령어 (run, write 등) |
| `target` | 주요 대상 (Feature ID, 파일명, dXXXX, TC ID 등) |
| `files` | 실제 작업된 파일 경로 목록 |
| `sp` | 서브프로젝트 번호 |
| `timestamp` | 저장 시각 |

### 9.3 저장 규칙 (스킬 공통)

각 스킬은 주요 명령(`run`, `write` 등) **실행 완료 후** `.claude/last_target.json`을 갱신한다.

- `target`: 명시적 인수 (Feature ID, 파일명, dXXXX, TC ID 등). 없으면 작업한 파일 목록
- `files`: 실제 Read/Edit한 파일 경로 전체
- `sp`: 현재 oocontext SP 번호 (미설정 시 "00")

### 9.4 `this` 해석 우선순위

| 우선순위 | 조건 | 해석 |
|---------|------|------|
| 1 | 세션 내 동일 대화 | 직전 메시지의 작업 대상 (컨텍스트 자동 파악) |
| 2 | `.claude/last_target.json` 존재 | 파일에서 로드 |
| 3 | `git diff --name-only HEAD` | 변경 파일 목록 |
| 4 | 없음 | 사용자에게 대상 명시 요청 |

### 9.5 스킬별 `this` 동작

| 스킬 | `this` 동작 |
|------|------------|
| `oodev run this` | last_target Feature/파일 계속 구현 |
| `ootest run this` | last_target 관련 TC 실행 |
| `oocheck run this` | last_target 파일만 체크 |
| `oofix run this` | last_target 파일 이슈 수정 |
| `oocommit run this` | last_target 변경사항 커밋 |
| `ooprd run this` | last_target 관련 PRD 섹션 갱신 |
| `ooplan run this` | last_target 관련 계획 업데이트 |
| `oofeature run this` | last_target 상세 문서 다음 단계 진행 |
| `oolib run this` | last_target 모듈 최적화 |
| `oodb run this` | last_target DB 관련 분석 |
| `oodoc update this` | last_target 영향 문서 업데이트 |
| `oohistory run this` | last_target 완료 이슈 아카이브 |
| `ootodo run this` | last_target 관련 TODO 처리 |
| `ooopti run this` | last_target 파일 최적화 |
| `oopaper run this` | 직전 처리한 논문 계속 |
| `ooword/ooppt/oopdf this` | 직전 작업한 MD 파일 변환 |
| `ooresearch run this` | 직전 연구 주제 계속 |
| `oonext this` | last_target 기반 다음 작업 추천 |
