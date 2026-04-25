# ootutorial_guide - 프로젝트 튜토리얼 생성 가이드

## 문서 이력 관리
- v02 2026-04-10 — SKILL.md 완성 템플릿 자산 경로 및 사용 가이드 추가
- v01 2026-04-02 — 초기 생성 — 서브명령어 상세, 출력 구조, 플러그인 튜토리얼 섹션 포함

---

> 스킬: `.claude/skills/ootutorial/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

ootutorial은 OAIS 프로젝트의 전체 Claude 환경(oo 스킬, SC 명령어, 플러그인/MCP)에 대한 튜토리얼 문서를 자동 생성·관리하는 스킬입니다.

### 1.1 핵심 역할

- **스킬 튜토리얼**: 각 oo 스킬의 SKILL.md → `tutorial/skills/{스킬명}.md` 변환
- **명령어 튜토리얼**: `.claude/commands/sc/*.md` → `tutorial/commands/{명령어}.md`
- **플러그인 튜토리얼**: Claude 플러그인 + MCP 서버 → `tutorial/plugins/{플러그인}.md`
- **인덱스 관리**: `tutorial/README.md` 전체 목차 자동 갱신

### 1.3 템플릿 자산 관리

- `ootutorial`은 출력 문서뿐 아니라 **문서 생성용 템플릿 자산**도 관리한다.
- 새 oo 스킬용 `SKILL.md` 초안은 아래 템플릿을 기준으로 작성한다.

| 자산 | 경로 | 설명 |
|------|------|------|
| SKILL.md 완성 템플릿 | `.claude/skills/ootutorial/templates/SKILL_md_template.md` | 새 스킬의 `SKILL.md`를 바로 복사해 사용할 수 있는 완성형 템플릿 |
| 튜토리얼 출력 템플릿 | `.claude/skills/ootutorial/templates/tutorial_skill_template.md` | `00_doc/tutorial/skills/*.md` 생성 시 사용하는 표준 구조 템플릿 |

**운영 원칙**
1. 스킬 생성/문서화와 직접 연결된 템플릿은 가능한 한 `ootutorial` 스킬 폴더 내부에 둔다.
2. 일반 튜토리얼 독자용 산출물은 `00_doc/tutorial/` 아래에 둔다.
3. 템플릿 경로가 바뀌면 관련 가이드와 참조 문서를 함께 갱신한다.

### 1.2 출력 디렉토리 구조

```
00_doc/tutorial/
├── README.md                    # 전체 목차 (인덱스)
├── 00_overview.md               # 프로젝트 전체 사용법
├── skills/                      # oo 스킬 (37개)
│   ├── oostart.md
│   ├── oodev.md
│   └── ...
├── commands/                    # SC 명령어 (4개)
│   ├── estimate.md
│   ├── index.md
│   ├── spawn.md
│   └── task.md
└── plugins/                     # 플러그인/MCP 서버
    ├── oh-my-claudecode.md      # OMC ★
    ├── context7.md              # 라이브러리 문서 ★
    ├── code-review.md           # 코드 리뷰 ★
    ├── commit-commands.md       # 커밋 메시지 ★
    ├── pyright-lsp.md           # Python 타입체크 ★
    ├── document-skills.md       # 문서 생성 모음
    ├── github.md                # GitHub 연동
    ├── playwright.md            # E2E 테스트
    ├── sequential-thinking.md   # 다단계 추론 ★ (MCP)
    └── desktop-commander.md     # 파일 I/O ★ (MCP)
```

## 2. 서브명령어 상세

### 2.1 ootutorial run — 전체 생성

```bash
ootutorial run
```

모든 카테고리(개요, 스킬, 명령어, 플러그인)를 순서대로 생성합니다.

**실행 흐름**:

```
1. 00_doc/tutorial/ 디렉토리 확인 (없으면 생성)
2. [개요] 00_doc/tutorial/00_overview.md 생성
  → CLAUDE.md, .claude/CLAUDE.md 분석
3. [oo 스킬] skills/*.md 생성 (병렬)
  → .claude/skills/oo*/ 스캔 → SKILL.md 읽기 → 변환
4. [SC 명령어] commands/*.md 생성 (병렬)
  → .claude/commands/sc/*.md 스캔 → 변환
5. [플러그인] plugins/*.md 생성 (병렬)
  → d0009_env.md 플러그인 섹션 + .mcp.json 분석
6. [인덱스] README.md 전체 목차 갱신
7. 결과 요약 출력
```

### 2.2 ootutorial run --skill \<스킬명\>

```bash
ootutorial run --skill oodev      # oodev만 재생성
ootutorial run --skill oocommit   # oocommit만
```

특정 스킬 튜토리얼 1개만 갱신. SKILL.md가 업데이트된 경우 활용.

**실행 흐름**:

```
1. .claude/skills/{스킬명}/SKILL.md 읽기
2. tutorial/skills/{스킬명}.md 생성/덮어쓰기
3. tutorial/README.md 인덱스 업데이트
```

### 2.3 ootutorial run --category \<카테고리\>

```bash
ootutorial run --category skills     # 스킬 전체 재생성
ootutorial run --category commands   # 명령어 전체 재생성
ootutorial run --category plugins    # 플러그인 전체 재생성
ootutorial run --category overview   # 개요만 재생성
```

카테고리 단위로 갱신. 스킬 여러 개가 동시에 업데이트된 경우 활용.

### 2.4 ootutorial status

```bash
ootutorial status
```

생성된 튜토리얼 현황 요약.

**출력 예시**:

```
=== ootutorial 상태 ===
tutorial/ 디렉토리: OK
- skills/: 37개
- commands/: 4개
- plugins/: 10개
- README.md: OK
- 00_overview.md: OK

마지막 갱신: 2026-04-02
```

### 2.5 ootutorial check

```bash
ootutorial check
```

checklist.md 기반 자체 건강 상태 검증.

**검증 항목**:

| ID | 항목 | 심각도 |
|----|------|--------|
| C01 | SKILL.md 등 필수 파일 존재 | CRITICAL |
| C02 | SKILL.md 버전 일치 | ERROR |
| C03 | 00_doc/tutorial/ 디렉토리 존재 | ERROR |
| C04 | tutorial/README.md 존재 | WARNING |
| C05 | 각 스킬 튜토리얼 파일 존재 | INFO |

## 3. 튜토리얼 문서 형식

### 3.1 oo 스킬 튜토리얼 (`skills/*.md`)

```markdown
# {스킬명} Tutorial

> {한줄 설명} | 버전: {version} | 카테고리: {category}

## 개요
## 명령어 (서브명령어 테이블)
## 사용 예시 (주요 시나리오 3개 이상)
## 워크플로우 (실행 흐름도)
## 관련 스킬
```

### 3.2 플러그인 튜토리얼 (`plugins/*.md`)

```markdown
# 플러그인: {플러그인명}

> {한줄 설명} | 필수 여부

## 개요 (설치 정보 테이블)
## 핵심 기능
## 주요 스킬/도구 명령어
## 사용 예시
## oo 스킬 연계
```

## 4. 사용 예시

### 4.0 새 oo 스킬의 SKILL.md 초안 작성

```bash
# 1. 템플릿 복사
copy .claude\skills\ootutorial\templates\SKILL_md_template.md .claude\skills\oonew\SKILL.md

# 2. 플레이스홀더 치환
# {skill_name}, {description}, {workflow} 등을 실제 내용으로 교체

# 3. 검증
ooskill check
```

### 4.1 새 스킬 추가 후 튜토리얼 갱신

```bash
# 1. 새 스킬 개발 완료
# .claude/skills/oonew/SKILL.md 작성됨

# 2. 해당 스킬만 튜토리얼 갱신
ootutorial run --skill oonew

# 3. 인덱스 자동 업데이트됨
# → tutorial/skills/oonew.md 생성
# → tutorial/README.md 갱신
```

### 4.2 플러그인 신규 설치 후 튜토리얼 갱신

```bash
# 1. 새 플러그인 설치
/plugin install new-plugin@claude-plugins-official

# 2. 플러그인 카테고리만 재생성
ootutorial run --category plugins

# 3. 또는 수동으로 plugins/new-plugin.md 작성
```

### 4.3 전체 튜토리얼 초기 생성

```bash
# 프로젝트 초기 또는 전체 재생성
ootutorial run

# 결과 확인
ootutorial status
```

### 4.4 특정 카테고리 업데이트

```bash
# oo 스킬 SKILL.md 여러 개가 업데이트됨
ootutorial run --category skills

# 커밋
oocommit run
```

## 5. 플러그인 튜토리얼 관리 원칙

### 5.1 추가 기준

| 조건 | 처리 |
|------|------|
| d0009_env.md에 ✅ 설치된 플러그인 | `plugins/` 튜토리얼 생성 |
| .mcp.json에 등록된 MCP 서버 | `plugins/` 튜토리얼 생성 |
| 미설치 플러그인 | 생성 안 함 (README 표에서만 언급) |

### 5.2 현재 플러그인 목록

| 파일 | 플러그인 | 필수 |
|------|---------|:----:|
| `oh-my-claudecode.md` | OMC 멀티에이전트 | ★ |
| `context7.md` | 라이브러리 문서 조회 | ★ |
| `code-review.md` | 코드 리뷰 자동화 | ★ |
| `commit-commands.md` | 커밋 메시지 생성 | ★ |
| `pyright-lsp.md` | Python 타입 체크 | ★ |
| `document-skills.md` | 문서 생성 스킬 모음 | - |
| `github.md` | GitHub 연동 | - |
| `playwright.md` | E2E 테스트 | - |
| `sequential-thinking.md` | 다단계 추론 (MCP) | ★ |
| `desktop-commander.md` | 파일 I/O (MCP) | ★ |

## 6. 관련 문서

| 문서 | 역할 |
|------|------|
| `.claude/skills/ootutorial/SKILL.md` | 본 스킬 정의 |
| `.claude/skills/ooenv/SKILL.md` | `ooenv tutorial` 연계 (구 방식) |
| `00_doc/tutorial/README.md` | 전체 튜토리얼 인덱스 |
| `00_doc/sp00/d0009_env.md` | 플러그인 설치 현황 |
| `.mcp.json` | MCP 서버 등록 현황 |
