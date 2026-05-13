# oocommit_guide - Git 커밋 + 이력 정리 가이드

## 문서 이력 관리
- v02 2026-04-02 — clear 서브명령어, GSD 연계 추가
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oocommit/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oocommit은 Git 커밋과 이력 정리를 통합하는 스킬입니다. 커밋과 동시에 완료된 todo 항목을 자동으로 history로 이동하여 프로젝트 이력을 체계적으로 관리합니다.

### 1.1 핵심 역할

- **Git 커밋**: Conventional Commits 형식으로 변경사항 커밋
- **이력 정리**: 완료된 todo → history 자동 이동
- **GitHub 연동**: Task → GitHub Issues 변환
- **통합 워크플로우**: 커밋 + 이력 + GitHub를 하나의 명령으로

### 1.2 출력

| 출력 | 역할 | 비고 |
|------|------|------|
| Git commit | 버전 관리 | 주 출력 |
| `d{SP}0004_todo.md` | 완료 항목 제거 | 부 출력 |
| `d{SP}0010_history.md` | 완료 항목 추가 | 부 출력 |
| GitHub Issues | 태스크 변환 | github 서브명령어 |

### 1.3 5단계 워크플로우

| 단계 | 작업 | 산출물 |
|------|------|--------|
| 1. 분석 | git status/diff, 커밋 메시지 생성 | 커밋 계획 |
| 2. 커밋 | 스테이징, 실행 (사용자 확인) | Git commit |
| 3. 추출 | d{SP}0004에서 완료 항목 식별 | 완료 목록 |
| 4. 이동 | d{SP}0010 추가, d{SP}0004 제거 | 문서 업데이트 |
| 5. 검증 | 무결성 확인 | 검증 리포트 |

## 2. 워크플로우

### 2.1 전체 흐름도 (run)

```
┌─────────────────────────────────────────────┐
│ 1. 분석                                      │
└─────────────┬───────────────────────────────┘
              │
              ├─► git status
              │      └─ 변경된 파일 목록
              │
              ├─► git diff
              │      └─ 변경 내용 상세
              │
              └─► 커밋 메시지 생성
                     ├─ 변경사항 분석
                     ├─ 타입 판단 (feat/fix/docs/refactor...)
                     ├─ Conventional Commits 형식
                     └─ Co-Authored-By: Claude 추가
                                                │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ 2. 커밋                                      │
└─────────────┬──────────────────────────────┘
              │
              ├─► 사용자 확인
              │      └─ 커밋 메시지 승인
              │
              ├─► git add (관련 파일)
              │      └─ 변경된 파일만 스테이징
              │
              └─► git commit
                     └─ 생성된 메시지로 커밋
                                                │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ 3. 추출 (완료 항목)                          │
└─────────────┬──────────────────────────────┘
              │
              ├─► d{SP}0004_todo.md 읽기
              │
              ├─► 완료 키워드 검색
              │      ├─ [x] (체크박스)
              │      ├─ "해결" (상태)
              │      ├─ "완료"
              │      └─ "CLOSED"
              │
              └─► 완료 항목 목록 생성
                                                │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ 4. 이동 (todo → history)                    │
└─────────────┬──────────────────────────────┘
              │
              ├─► d{SP}0010_history.md 추가
              │      ├─ 날짜: [YYYY-MM-DD]
              │      ├─ 태그: [HOTFIX/BUGFIX/IMPROVE/ENHANCE]
              │      ├─ 제목
              │      ├─ 파일 목록
              │      └─ 내용 상세
              │
              ├─► d{SP}0004_todo.md 제거
              │      └─ 완료 항목 삭제
              │
              └─► 버전 업데이트
                     └─ 문서 버전 증가
                                                │
┌─────────────────────────────────────────────┘
│
┌─────────────▼──────────────────────────────┐
│ 5. 검증                                      │
└─────────────┬──────────────────────────────┘
              │
              ├─► 문서 무결성 확인
              │      ├─ 중복 항목 없음
              │      ├─ 누락 없음
              │      └─ 형식 일치
              │
              └─► 완료 리포트
                     ├─ 커밋 ID
                     ├─ 이동 항목 수
                     └─ 업데이트된 문서
```

### 2.2 커밋 메시지 생성 (1단계)

```
커밋 메시지 생성
    │
    ├─► 1. git diff 분석
    │      ├─ 변경된 파일
    │      ├─ 추가/삭제/수정 라인
    │      └─ 변경 내용 요약
    │
    ├─► 2. 타입 판단
    │      ├─ feat: 새 기능
    │      ├─ fix: 버그 수정
    │      ├─ docs: 문서
    │      ├─ refactor: 리팩토링
    │      ├─ test: 테스트
    │      └─ chore: 기타
    │
    ├─► 3. scope 식별
    │      ├─ oo: oo 모듈
    │      ├─ pages: Streamlit 페이지
    │      ├─ tests: 테스트
    │      └─ docs: 문서
    │
    ├─► 4. subject 작성
    │      ├─ 변경 요약 (50자 이내)
    │      ├─ 현재형 동사 (add, fix, update)
    │      └─ 명확하고 간결하게
    │
    └─► 5. Conventional Commits 형식
           ```
           <type>(<scope>): <subject>

           Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
           ```
```

**Conventional Commits 형식**:

| 타입 | 설명 | 예시 |
|------|------|------|
| `feat` | 새 기능 | feat(pages): add welfare policy tab |
| `fix` | 버그 수정 | fix(oo): resolve duplicate key error |
| `docs` | 문서 | docs(readme): update installation guide |
| `refactor` | 리팩토링 | refactor(utils): extract date formatting |
| `test` | 테스트 | test(policy): add unit tests |
| `chore` | 기타 | chore(deps): update dependencies |

### 2.3 완료 항목 추출 (3단계)

```
완료 항목 추출
    │
    ├─► 1. d{SP}0004_todo.md 읽기
    │      ```markdown
    │      | ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
    │      | T100 | 2026-02-05 | [ERR] | E0611: oo.db export | 높음 | 해결 |
    │      | T101 | 2026-02-05 | [ERR] | E0102: 중복 정의 | 중간 | 대기 |
    │      ```
    │
    ├─► 2. 완료 키워드 검색
    │      ├─ 상태 컬럼: "해결", "완료", "CLOSED"
    │      ├─ 체크박스: [x]
    │      └─ 기타: "done", "fixed"
    │
    ├─► 3. 완료 항목 목록 생성
    │      └─ T100: [ERR] E0611: oo.db export (해결)
    │
    └─► 4. 태그 매핑
           ├─ CRITICAL → [HOTFIX]
           ├─ ERROR → [BUGFIX]
           ├─ WARNING → [IMPROVE]
           └─ INFO → [ENHANCE]
```

**완료 키워드**:

| 키워드 | 매칭 |
|--------|------|
| `[x]` | 체크박스 |
| `해결` | 상태 컬럼 |
| `완료` | 상태 컬럼 |
| `CLOSED` | 상태 컬럼 |

### 2.4 이력 이동 (4단계)

```
이력 이동 (todo → history)
    │
    ├─► 1. d{SP}0010_history.md 추가
    │      ```markdown
    │      ### [2026-02-05] [BUGFIX] oo 모듈 에러 수정
    │
    │      **분류**: [ERR]
    │      **우선순위**: 높음
    │      **원인**: oo.db export 누락 (E0611)
    │
    │      **수정 내용**:
    │      - oo/__init__.py에 get_db_connection import 추가
    │
    │      **수정 파일**:
    │      - oo/__init__.py
    │
    │      **관련 이슈**: T100
    │      ```
    │
    ├─► 2. d{SP}0004_todo.md 제거
    │      ├─ T100 라인 삭제
    │      └─ 테이블 정렬 유지
    │
    ├─► 3. 버전 업데이트
    │      ├─ d{SP}0004_todo.md 버전 증가 (v05 → v06)
    │      └─ d{SP}0010_history.md 버전 증가 (v08 → v09)
    │
    └─► 4. 문서 이력 관리 섹션 업데이트
           ```markdown
           | 버전 | 날짜 | 변경 내용 |
           | v06 | 2026-02-05 | T100 완료 항목 제거 (1건) |
           ```
```

**태그 매핑 규칙**:

| todo 분류 | history 태그 | 우선순위 |
|----------|-------------|---------|
| [CRITICAL] | [HOTFIX] | 즉시 |
| [ERROR] | [BUGFIX] | 24시간 |
| [WARNING] | [IMPROVE] | 1주일 |
| [INFO] | [ENHANCE] | 백로그 |

### 2.5 GitHub 워크플로우 (github 서브명령어)

```
oocommit github
    │
    ├─► 1. 태스크 로드
    │      ├─ d{SP}0002_plan.md (개발 태스크)
    │      ├─ tasks.md (TaskMaster 사용 시)
    │      └─ d{SP}0003_test.md (테스트 태스크)
    │
    ├─► 2. 의존성 분석
    │      ├─ Task 간 의존관계 파악
    │      ├─ Epic → Feature → Task 계층
    │      └─ 생성 순서 결정 (의존성 순)
    │
    ├─► 3. GitHub CLI 연동
    │      ├─ gh issue create 호출
    │      ├─ 라벨 자동 매핑
    │      │  ├─ priority: high → P0-critical
    │      │  ├─ priority: medium → P1-important
    │      │  └─ type: feature → enhancement
    │      └─ 마일스톤 연결 (있는 경우)
    │
    ├─► 4. 이슈 생성
    │      ├─ 제목: Task 제목
    │      ├─ 본문:
    │      │  ```markdown
    │      │  ## 설명
    │      │  {Task 상세 설명}
    │      │
    │      │  ## 체크리스트
    │      │  - [ ] 구현 완료
    │      │  - [ ] 테스트 작성
    │      │  - [ ] 문서 업데이트
    │      │
    │      │  ## 관련 정보
    │      │  - **우선순위**: {priority}
    │      │  - **의존성**: #{dep_issue_number}
    │      │  - **원본**: d{SP}0002_plan.md
    │      │  ```
    │      └─ 라벨: priority, type, status
    │
    └─► 5. 결과 반영
           ├─ 이슈 번호 → Task 문서에 기록
           │  ```markdown
           │  #### F002-1.1: 보건복지부 탭
           │  - **GitHub Issue**: #123
           │  ```
           └─ 생성 리포트 출력
```

**GitHub 라벨 매핑**:

| Task 속성 | GitHub 라벨 |
|----------|------------|
| priority: high | `P0-critical` |
| priority: medium | `P1-important` |
| priority: low | `P2-normal` |
| type: feature | `enhancement` |
| type: bug | `bug` |
| type: docs | `documentation` |

## 3. 상세 사용법

### 3.1 서브명령어

#### 3.1.1 oocommit status

서브명령어 리스트 및 상태

```bash
oocommit status
```

**출력 예시**:
```
=== oocommit 서브명령어 ===
- run: 커밋 + push + 이력 정리 통합 (기본)
- commit: Git 커밋 + 기본 push
- sync: 이력 정리만
- github: 태스크 → GitHub Issues
- preview: 변경사항 미리보기
- version: v03

=== 상태 ===
- 변경된 파일: 5개
- 완료 항목 (d0004): 3건
- 커밋 대기: yes
```

#### 3.1.2 oocommit run

커밋 + push + 이력 정리 통합 (기본)

```bash
oocommit run                            # 통합 실행
oocommit run --dry-run                  # 미리보기
oocommit run --sp 02                    # 서브프로젝트 02
oocommit run --message "custom message" # 커밋 메시지 지정
oocommit run --no-push                  # 기본 push 생략
```

#### 3.1.3 oocommit commit

Git 커밋 + 기본 push (이력 정리 생략)

```bash
oocommit commit
oocommit commit --message "fix: resolve duplicate key"
```

#### 3.1.4 oocommit sync

이력 정리만 (커밋 생략)

```bash
oocommit sync                           # d{SP}0004 → d{SP}0010
oocommit sync --force-sync              # 강제 이동
```

#### 3.1.5 oocommit github

태스크 → GitHub Issues 변환

```bash
# 전체 태스크 변환
oocommit github

# 특정 태스크만 변환
oocommit github --task-id 1,2,3

# 미리보기
oocommit github --dry-run

# 기존 이슈와 동기화
oocommit github --sync

# 추가 옵션
oocommit github --labels "sprint-1,backend" --milestone "v1.0"
```

**옵션**:

| 옵션 | 설명 |
|------|------|
| `--task-id <ids>` | 특정 태스크만 변환 (쉼표 구분) |
| `--dry-run` | 실제 생성 없이 미리보기 |
| `--sync` | 기존 이슈와 양방향 동기화 |
| `--labels <labels>` | 추가 라벨 지정 |
| `--milestone <name>` | 마일스톤 지정 |
| `--project <name>` | GitHub Project 연결 |

#### 3.1.6 oocommit clear

오래된 커밋 squash + .git 용량 정리

```bash
oocommit clear                          # 오래된 커밋 정리 + .git 용량 최적화
oocommit clear --dry-run                # 미리보기만
```

> ⚠️ 파괴적 작업 — 반드시 사용자 확인 후 실행

#### 3.1.7 oocommit preview

변경사항 미리보기

```bash
oocommit preview
```

**출력 예시**:
```
=== 커밋 미리보기 ===

[커밋 메시지]
fix(oo): resolve export and duplicate errors

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

[변경된 파일]
- oo/__init__.py
- oo/utils.py
- pages/7_72_앱_시니어복지.py

[완료 항목 (3건)]
- T100: [ERR] E0611: oo.db export
- T101: [ERR] E0102: 중복 정의
- T102: [WARNING] W0612: 미사용 변수

[이력 이동]
→ d0010_history.md 추가: 3건
→ d0004_todo.md 제거: 3건

계속 진행하시겠습니까? (y/n):
```

### 3.2 옵션

| 옵션 | 설명 |
|------|------|
| `--message "msg"` | 커밋 메시지 지정 |
| `--no-push` | 기본 push 생략 |
| `--dry-run` | 미리보기 (실제 실행 X) |
| `--force-sync` | 완료 항목 강제 이동 |
| `--sp N` | 서브프로젝트 번호 |

### 3.3 Git 안전 프로토콜

**절대 금지**:

- ❌ 명시적 요청 없이 자동 커밋
- ❌ `git config` 변경
- ❌ 파괴적 명령 (`reset --hard`, `push --force`, `clean -f`)
- ❌ 훅 스킵 (`--no-verify`)
- ❌ 민감정보 커밋 (`.env`, `credentials.json`)

**필수 확인**:

- ✅ 테스트 통과
- ✅ 린트 통과
- ✅ 사용자 승인
- ✅ 민감정보 제외

## 4. 사용 예시

### 4.1 기본 커밋 + 이력 정리

**시나리오**: 9건 이슈 수정 후 커밋

```bash
# 1. 변경사항 확인
git status
# modified: oo/__init__.py
# modified: oo/utils.py
# modified: pages/7_72_앱_시니어복지.py

# 2. 미리보기
oocommit preview

# === 커밋 미리보기 ===
# [커밋 메시지]
# fix(oo): resolve 9 errors (E0611, E0102, W0612)
# ...

# 3. 실행
oocommit run

# === 1. 분석 ===
# 변경된 파일: 3개
# 커밋 메시지 생성 완료

# === 2. 커밋 ===
# 승인하시겠습니까? (y/n): y
# [main abc1234] fix(oo): resolve 9 errors

# === 3. 추출 ===
# 완료 항목 발견: 3건

# === 4. 이동 ===
# d0010_history.md 추가: 3건 ✓
# d0004_todo.md 제거: 3건 ✓
# 버전 업데이트: d0004 v05→v06, d0010 v08→v09 ✓

# === 5. 검증 ===
# 무결성 확인 ✓

# === 완료 ===
# 커밋 ID: abc1234
# 이동 항목: 3건
```

### 4.2 커밋만 실행

**시나리오**: 이력 정리 없이 커밋만

```bash
oocommit commit --message "docs: update README"

# === 커밋 완료 ===
# [main def5678] docs: update README
```

### 4.3 이력 정리만 실행

**시나리오**: 커밋 없이 완료 항목만 이동

```bash
oocommit sync

# === 완료 항목 추출 ===
# d0004_todo.md: 2건

# === 이동 ===
# d0010_history.md 추가: 2건 ✓
# d0004_todo.md 제거: 2건 ✓

# === 완료 ===
```

### 4.4 GitHub Issues 생성

**시나리오**: Plan의 Task를 GitHub Issues로 변환

```bash
# 1. 미리보기
oocommit github --dry-run

# === GitHub Issues 미리보기 ===
#
# Issue #1: [F001-1.1] 로그인 UI
# - 우선순위: P0-critical
# - 라벨: enhancement, P0-critical
# - 본문: ...
#
# Issue #2: [F002-1.1] 보건복지부 탭
# - 우선순위: P1-important
# - 라벨: enhancement, P1-important
# - 의존성: #1
# - 본문: ...
#
# 총 24개 이슈 생성 예정

# 2. 실행
oocommit github

# === 의존성 분석 ===
# Epic 3개 → Feature 8개 → Task 24개

# === GitHub Issues 생성 ===
# Issue #123: [F001-1.1] 로그인 UI 생성 ✓
# Issue #124: [F001-1.2] 권한 체크 생성 ✓
# Issue #125: [F002-1.1] 보건복지부 탭 생성 ✓
# ...
# (24개 이슈 생성 완료)

# === d0002_plan.md 업데이트 ===
# Task에 GitHub Issue 번호 추가 ✓

# === 완료 ===
# 생성: 24개 이슈
```

### 4.5 특정 Task만 GitHub Issue 생성

**시나리오**: F002-1 Feature만 Issues 생성

```bash
oocommit github --task-id F002-1.1,F002-1.2,F002-1.3

# === GitHub Issues 생성 ===
# Issue #130: [F002-1.1] 보건복지부 탭 ✓
# Issue #131: [F002-1.2] 고용노동부 탭 ✓
# Issue #132: [F002-1.3] 필터링 기능 ✓

# === 완료 ===
# 생성: 3개 이슈
```

### 4.6 서브프로젝트 커밋 (병행 처리)

**시나리오**: SP=02 커밋 시 병행 업데이트

```bash
# 1. 컨텍스트 설정
oocontext 02

# 2. 실행
oocommit run

# === 완료 항목 추출 (병행) ===
# d0004_todo.md: 2건 (공통)
# d20004_todo.md: 2건 (SP=02)

# === 이동 (병행) ===
# d0010_history.md 추가: 2건 ✓ (공통)
# d20010_history.md 추가: 2건 ✓ (SP=02)
# d0004_todo.md 제거: 2건 ✓ (공통)
# d20004_todo.md 제거: 2건 ✓ (SP=02)

# === 완료 ===
# 양쪽 문서 모두 업데이트됨
```

## 4.7 GSD 연계

**시나리오**: GSD 워크플로우와 oocommit 조합

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 페이즈 완료 배포 | `oocommit run` 후 수동 | `/gsd:ship` |
| PR 브랜치 생성 | `oocommit github` | `/gsd:pr-branch` |
| 마일스톤 완료 처리 | `oocommit run` 후 수동 | `/gsd:complete-milestone` |
| 진행 상황 리포트 | - | `/gsd:session-report` |

**조합 패턴**:

```bash
# 패턴 1: 페이즈 완료 후 배포
oocheck run          # 코드 검증
oocommit run         # 커밋 + 이력 정리
/gsd:ship            # 브랜치 병합, 태그, 배포

# 패턴 2: PR 기반 워크플로우
oocommit run         # 커밋
/gsd:pr-branch       # PR 브랜치 생성 + 설명 자동 작성

# 패턴 3: 마일스톤 완료
oocommit run         # 최종 커밋
/gsd:complete-milestone  # 마일스톤 요약 + 다음 마일스톤 준비
```

## 5. 관련 문서

### 5.1 스킬 및 명령어

| 문서 | 역할 |
|------|------|
| `.claude/skills/oocommit/SKILL.md` | 본 스킬 정의 |
| `.claude/skills/oocheck/SKILL.md` | 코드 체크 (선행) |
| `.claude/skills/oofix/SKILL.md` | 코드 수정 (선행) |
| `.claude/commands/sc/git.md` | Git 명령어 |

### 5.2 핵심 문서

| 문서 | 역할 |
|------|------|
| `00_doc/d{SP}0004_todo.md` | TODO/디버깅 (입력) |
| `00_doc/d{SP}0010_history.md` | 변경 이력 (출력) |
| `00_doc/d{SP}0002_plan.md` | 구현 계획 (github 입력) |
| `tasks.md` | TaskMaster (github 입력, 있는 경우) |

### 5.3 공통 가이드

| 문서 | 역할 |
|------|------|
| `.claude/guides/common_guide.md` | 프로젝트 공통 개발 표준 |
| `.claude/skills/oocheck/references/guide.md` | 코드 체크 가이드 |
| `.claude/skills/oofix/references/guide.md` | 코드 수정 가이드 |
