# ootutorial Tutorial

> 프로젝트 튜토리얼 생성 스킬 | 버전: v01 | 카테고리: doc-env

## 1. 이 스킬은 왜 필요한가?

프로젝트 튜토리얼 생성 스킬

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ootutorial run

# 상태 확인
ootutorial status

# 도움말
ootutorial help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ootutorial help` | 서브명령어 목록 표시 |
| `ootutorial version` | 스킬 버전 정보 (v01) |
| `ootutorial status` | 서브명령어 리스트, 생성된 튜토리얼 현황 |
| `ootutorial check` | references/checklist.md 기반 체크 및 리포팅 |
| `ootutorial show checklist` | 역할 수행 체크리스트 표시 |
| `ootutorial add checklist "항목"` | 체크리스트 항목 추가 |
| `ootutorial run` | 전체 튜토리얼 생성 실행 |
| `ootutorial update` | 현행화 — 스킬/명령어 변경사항 → 튜토리얼 현행화 |
| `ootutorial update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) |
| `ootutorial run --skill <스킬명>` | 특정 oo 스킬 튜토리얼만 생성 |
| `ootutorial run --category <카테고리>` | 특정 카테고리만 생성 (skills/commands/plugins/overview) |
| `ootutorial sync` | 양방향 동기화 — 플래그 기반 스킬↔튜토리얼 현행화 |
| `ootutorial sync --check` | 동기화 필요 항목 확인 (실제 수정 안 함) |
| `ootutorial sync --clear` | 동기화 플래그 초기화 (.omc/sync-flags/ 삭제) |

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | OAIS 환경(스킬·명령어·플러그인)에 대한 튜토리얼 문서 생성·관리 |
| **하는 것** | `.claude/tutorial/` 튜토리얼 MD 파일 생성, 기존 튜토리얼 현행화 |
| **하지 않는 것** | 사용자 가이드(→oouser), API 문서(→oodoc), 코드 수정(→oodev) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (스킬 문서, 가이드) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `.claude/tutorial/*.md` |
| **실행 레벨** | [반자동] — 튜토리얼 주제 확인 후 작성 |
| **에이전트 호환** | Claude Code 권장 — Agent 도구로 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

### 튜토리얼 문서 형식

### oo 스킬 튜토리얼 (`skills/*.md`)

```markdown
# {스킬명} Tutorial

> {한줄 설명} | 버전: {version} | 카테고리: {category}

## 5. 워크플로우

{실행 흐름}

## 6. 실전 예시

{주요 사용 시나리오}

## 7. 입출력

```
.claude/tutorial/
├── README.md                    # 전체 목차 (인덱스)
├── 00_overview.md               # 프로젝트 전체 사용법
├── skills/                      # oo 스킬 튜토리얼
│   ├── oostart.md
│   ├── ooscrap.md
│   ├── oodev.md
│   └── ...                      # 37개 oo 스킬
├── commands/                    # SC 명령어 튜토리얼
│   ├── estimate.md
│   ├── index.md
│   ├── spawn.md
│   └── task.md
└── plugins/                     # 플러그인/MCP 튜토리얼
    ├── sequential-thinking.md
    └── ...
```

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 스캔 | Explore | haiku | 스킬/명령어/플러그인 목록 수집 (병렬) |
| 생성 | writer | haiku | 튜토리얼 문서 작성 (병렬) |

## 10. 관련 스킬

`.claude/skills/ootutorial/scripts/ootutorial_run.py` | `.claude/skills/oohelp/SKILL.md` | `.claude/tutorial/README.md`

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
