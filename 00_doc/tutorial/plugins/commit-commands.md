# 플러그인: commit-commands

> Git 커밋 메시지 생성 및 관리 | 필수 ★

## 개요

commit-commands는 Conventional Commits 형식의 커밋 메시지 자동 생성과 Git 워크플로우를 지원하는 플러그인입니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `commit-commands` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | ★ 필수 |
| 설치 명령어 | `/plugin install commit-commands@claude-plugins-official` |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| 커밋 메시지 생성 | git diff 분석 → Conventional Commits 메시지 자동 생성 |
| 커밋+푸시 | 커밋 후 원격 저장소 push |
| PR 생성 | 브랜치 push + PR 자동 생성 |
| 브랜치 정리 | 삭제된 원격 브랜치 로컬 정리 |

## 주요 스킬 명령어

| 명령어 | 설명 |
|--------|------|
| `/commit-commands:commit` | 커밋 메시지 생성 후 커밋 |
| `/commit-commands:commit-push-pr` | 커밋 → push → PR 생성 |
| `/commit-commands:clean_gone` | `git remote prune origin` 후 gone 브랜치 삭제 |

## 사용 예시

```bash
# 1. 커밋 메시지 자동 생성 및 커밋
/commit-commands:commit
# → git diff 분석 → "feat(auth): add JWT token refresh" 생성 → 커밋

# 2. 커밋 + push + PR 한 번에
/commit-commands:commit-push-pr
# → 커밋 → push → gh pr create 자동 실행

# 3. 없어진 원격 브랜치 정리
/commit-commands:clean_gone
# → 원격에서 삭제된 브랜치 로컬에서 제거
```

## Conventional Commits 형식

```
<type>(<scope>): <subject>

types: feat, fix, refactor, docs, test, chore, perf, ci
```

## oo 스킬과의 관계

| 플러그인 | oo 스킬 | 차이점 |
|---------|---------|--------|
| `commit-commands` | `oocommit` | commit-commands는 커밋+push 중심 |
| - | `oocommit` | oocommit은 TODO 이력 이동 + GitHub Issues 포함 |

> **권장**: OAIS 프로젝트에서는 `oocommit run` 사용 권장 (이력 정리 포함)

---

> 생성일: 2026-04-02 | ootutorial v01
