# 플러그인: github

> GitHub API 연동 — Issues, PR, 리포지토리 관리

## 개요

github 플러그인은 GitHub API를 Claude Code에 통합하여 Issues, Pull Request, 리포지토리 작업을 직접 수행합니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `github` |
| 설치 여부 | ✅ 설치됨 |
| 사전 조건 | `gh` CLI 인증 필요 (`gh auth login`) |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| Issues 관리 | 생성, 조회, 댓글, 상태 변경 |
| PR 관리 | 생성, 리뷰, 병합 |
| 리포지토리 조회 | 파일, 브랜치, 커밋 히스토리 |
| 코드 검색 | GitHub 코드 검색 API |

## 사용 예시

```bash
# 1. Issues 조회
"현재 열린 이슈 목록 보여줘"

# 2. Issue 생성
"로그인 버그 이슈 만들어줘: 제목, 설명, 라벨"

# 3. PR 생성
"현재 브랜치로 PR 만들어줘"

# 4. PR 리뷰
"PR #42 리뷰해줘"

# 5. 코드 검색
"이 리포에서 'def authenticate' 찾아줘"
```

## oo 스킬 연계

| oo 스킬 | github 플러그인 |
|---------|--------------|
| `oocommit github` | Issues 생성 (plan → GitHub Issues) |
| `oocommit run` | 커밋 후 PR 관련 작업 |

## gh CLI와의 관계

| 방법 | 용도 |
|------|------|
| `gh` CLI (Bash) | 스크립트/자동화에 직접 사용 |
| github 플러그인 | Claude와 대화형 GitHub 작업 |

---

> 생성일: 2026-04-02 | ootutorial v01
