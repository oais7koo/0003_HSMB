# oosync_guide - Vibe 환경 동기화 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성
- v02 2026-02-18 — 디렉토리 구조 변경 (대상: 3_code/ 내 프로젝트)

---

> 스킬: `.claude/skills/oosync/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

프로젝트 간 vibe 코딩 환경 파일을 비교하고 동기화하는 가이드입니다.

**목적**: vibe 환경 파일/폴더 동기화, 버전 관리, 병합
**원본(Source)**: `1_oo` (현재 프로젝트)
**대상(Target)**: `3_code/` 내 프로젝트들 (0001_SApp, 0002_CCone, 0003_RRag 등)
**동기화 대상**: .claude/, CLAUDE.md, run_claude.*, .mcp.json
**출력**: 파일 복사/동기화, 병합 파일

**디렉토리 구조**:
```
home/
├── 1_oo/          ← Source (현재 프로젝트)
└── 3_code/          ← Target 스캔 디렉토리
    ├── 0001_SApp/
    ├── 0002_CCone/
    ├── 0003_RRag/
    ├── 0004_a2z_ocr/
    └── ...
```

**동기화 방향**:
- push: 현재 프로젝트(1_oo) → 대상 프로젝트(3_code/*)
- pull: 대상 프로젝트(3_code/*) → 현재 프로젝트(1_oo)

## 2. 워크플로우

### 2.1 프로젝트 스캔 (list)

```
3_code/ 경로 스캔
    ↓
vibe 환경 판별
    ├─ Full: .claude/ 존재
    └─ None: 없음
    ↓
동기화 상태 확인 (.claude/ 기준)
    ├─ OK: 차이 없음
    ├─ 숫자: 차이 파일 수
    └─ -: 비교 불가
    ↓
박스 테이블 형식 출력
```

### 2.2 차이점 비교 (view)

```
대상 프로젝트와 파일 비교
    ↓
상태 분류
    ├─ →: 현재에만 존재 (ONLY_SOURCE)
    ├─ ←: 대상에만 존재 (ONLY_TARGET)
    ├─ >>: 현재가 최신 (NEWER_SOURCE)
    ├─ <<: 대상이 최신 (NEWER_TARGET)
    └─ ==: 동일 (SAME)
    ↓
파일별 상태 및 수정일 표시
```

### 2.3 동기화 실행 (run)

```
차이점 확인 (view)
    ↓
사용자 선택
    ├─ push: 현재 → 대상
    ├─ pull: 대상 → 현재
    ├─ skip: 건너뛰기
    └─ diff: 차이점 보기
    ↓
파일 복사/동기화
    ↓
결과 리포트
```

### 2.4 파일 병합 (merge)

```
양쪽 파일 읽기 (source + target)
    ↓
버전/이력 분석 (문서 이력 관리 섹션)
    ↓
섹션별 차이점 비교
    ↓
병합 전략 결정
    ├─ 양쪽에만 있는 섹션 → 모두 포함
    └─ 동일 섹션 다른 내용 → 최신 버전
    ↓
병합 버전 생성 (버전 +1, 이력 통합)
    ↓
저장 (source) + push (target) 옵션
```

## 3. 상세 사용법

### 3.1 프로젝트 목록

```bash
# 동기화 가능한 프로젝트 목록
uv run python .claude/skills/oosync/scripts/oosync_run.py list
```

**출력 예시** (박스 테이블):
```
┌────┬─────────────────┬─────────┬──────────┬─────┬──────┐
│ #  │ Project         │  Status │ .claude/ │  v/ │ Sync │
├────┼─────────────────┼─────────┼──────────┼─────┼──────┤
│  1 │ 0001_SApp       │   Full  │    O     │  X  │  OK  │
│  2 │ 0002_CCone      │   Full  │    O     │  O  │  3   │
│  3 │ 0003_RRag       │   Full  │    O     │  X  │  OK  │
│  4 │ 0004_a2z_ocr    │   None  │    X     │  X  │  -   │
└────┴─────────────────┴─────────┴──────────┴─────┴──────┘
```
**참고**: 3_code/ 내부의 프로젝트만 스캔합니다.

### 3.2 차이점 확인

```bash
# 대상 프로젝트와 비교 (3_code/ 내 프로젝트명)
uv run python .claude/skills/oosync/scripts/oosync_run.py view 0002_CCone

# 특정 파일 diff
uv run python .claude/skills/oosync/scripts/oosync_run.py diff 0002_CCone CLAUDE.md

# .claude/ 하위 파일
uv run python .claude/skills/oosync/scripts/oosync_run.py diff 0003_RRag .claude/skills/oosync/SKILL.md

# 프로젝트 번호로 축약 검색 (4자리 번호)
uv run python .claude/skills/oosync/scripts/oosync_run.py diff 0002 CLAUDE.md
```

**diff 출력 예시**:
```diff
--- [대상] 0002_CCone/CLAUDE.md
+++ [소스] 1_oo/CLAUDE.md
@@ -1,5 +1,6 @@
 # CLAUDE.md
+## 새로운 섹션
 ...
```

### 3.3 동기화 실행

```bash
# 대화형 동기화 (3_code/ 내 프로젝트)
uv run python .claude/skills/oosync/scripts/oosync_run.py run 0002_CCone

# push만 필요한 모든 프로젝트 일괄
uv run python .claude/skills/oosync/scripts/oosync_run.py run --push-only
```

### 3.4 파일 병합

```bash
# 자동 병합 (source에 저장)
uv run python .claude/skills/oosync/scripts/oosync_run.py merge 0002_CCone .claude/skills/ooreport/SKILL.md

# 미리보기 (실제 저장 없음)
uv run python .claude/skills/oosync/scripts/oosync_run.py merge 0002 .claude/skills/ooreport/SKILL.md --dry-run

# 양쪽에 저장 (source + target)
uv run python .claude/skills/oosync/scripts/oosync_run.py merge 0002 .claude/skills/ooreport/SKILL.md --both

# 충돌 시 source 우선
uv run python .claude/skills/oosync/scripts/oosync_run.py merge 0002 .claude/skills/ooreport/SKILL.md --prefer-source
```

**병합 규칙**:
1. 문서 이력 관리: 양쪽 이력 통합 + 병합 버전 추가
2. 서브명령어 표: 양쪽 명령어 합집합
3. 섹션: 한쪽에만 있으면 추가, 양쪽 있으면 최신 버전
4. 의존성: 양쪽 패키지 합집합

## 4. 사용 예시

### 예시 1: 프로젝트 간 동기화

```bash
# 1. 프로젝트 목록 확인 (3_code/ 내 프로젝트)
uv run python .claude/skills/oosync/scripts/oosync_run.py list
# 결과: 0002_CCone (Sync: 3)

# 2. 차이점 확인
uv run python .claude/skills/oosync/scripts/oosync_run.py view 0002_CCone

# 3. 동기화 실행
uv run python .claude/skills/oosync/scripts/oosync_run.py run 0002_CCone
# 선택: push/pull/skip/diff
```

### 예시 2: 파일 병합

```bash
# 1. diff 확인
uv run python .claude/skills/oosync/scripts/oosync_run.py diff 0002 .claude/skills/ooreport/SKILL.md

# 2. 병합 미리보기
uv run python .claude/skills/oosync/scripts/oosync_run.py merge 0002 .claude/skills/ooreport/SKILL.md --dry-run

# 3. 실제 병합 (source에 저장)
uv run python .claude/skills/oosync/scripts/oosync_run.py merge 0002 .claude/skills/ooreport/SKILL.md

# 결과:
# - 버전: v02 → v03
# - 이력: 양쪽 이력 통합 + "병합" 이력 추가
# - 섹션: 한쪽에만 있는 섹션 모두 포함
```

### 예시 3: 일괄 push

```bash
# push만 필요한 모든 프로젝트 일괄 동기화 (3_code/ 내)
uv run python .claude/skills/oosync/scripts/oosync_run.py run --push-only

# 결과:
# - 0001_SApp: 2개 파일 push
# - 0002_CCone: 1개 파일 push
# - 0003_RRag: 3개 파일 push
```

## 5. 동기화 대상

### 5.1 기본 동기화 대상

```
.claude/                      # 전체 (주요 동기화 대상)
├── *.md                      # SuperClaude 문서
├── commands/                 # 슬래시 명령어
├── skills/                   # 스킬 정의
├── agents/                   # 에이전트 정의
└── guides/                   # 가이드 문서

루트 설정:
├── CLAUDE.md                 # 프로젝트 진입점
├── run_claude.bat            # Windows 실행
├── run_claude.sh             # Linux/Mac 실행
├── pyproject.toml            # (선택) Python 설정
└── .mcp.json                 # (선택) MCP 설정

```
**참고**: `v/`는 레거시 폴더로, 최초 삭제 후 동기화 대상에서 제외됩니다.

### 5.2 제외 대상

```
__pycache__/
*.pyc
.git/
tmp/
data/
.venv/
node_modules/
.claude/settings.local.json   # 프로젝트별 로컬 설정
```

## 6. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oosync/SKILL.md | 스킬 명세 |
| .claude/skills/oostart/SKILL.md | 세션 시작 |
| .claude/skills/ooenv/SKILL.md | 환경 검증 |
| .claude/guides/common_guide.md | 공통 가이드라인 |

**에이전트**: Explore, task-executor, task-checker

**에이전트 출력 규칙**: 스크립트 출력만 표시, 별도 요약 금지 (.claude/skills/oosync/templates/oosync_*.md 형식 준수)
