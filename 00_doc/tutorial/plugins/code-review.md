# 플러그인: code-review

> PR/코드 리뷰 자동화 | 필수 ★

## 개요

code-review는 Pull Request와 코드 변경사항에 대한 자동화된 리뷰를 제공하는 플러그인입니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `code-review` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | ★ 필수 |
| 설치 명령어 | `/plugin install code-review@claude-plugins-official` |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| PR 리뷰 | 깃허브 PR 자동 분석 및 리뷰 |
| 코드 품질 | 가독성, 성능, 보안 관점 리뷰 |
| 리뷰 코멘트 생성 | PR 코멘트 자동 작성 |
| diff 분석 | git diff 기반 변경사항 파악 |

## 주요 스킬 명령어

| 명령어 | 설명 |
|--------|------|
| `/code-review:code-review` | 현재 코드 또는 지정 파일 리뷰 |

## 사용 예시

```bash
# 1. 현재 변경사항 리뷰
/code-review:code-review

# 2. 특정 파일 리뷰
/code-review:code-review src/api/endpoints.py

# 3. PR 리뷰 (gh CLI와 연계)
# gh pr diff 123 | code-review

# 4. oocheck와 함께
oocheck run          # pylint/mypy 에러 체크
/code-review:code-review  # 코드 품질 리뷰
```

## oo 스킬 연계

| 단계 | oo 스킬 | 플러그인 |
|------|---------|---------|
| 코드 작성 | `oodev run` | - |
| 에러 체크 | `oocheck run` | - |
| 코드 리뷰 | - | `/code-review:code-review` |
| 수정 | `oofix run` | - |
| 커밋 | `oocommit run` | - |

## 주의사항

- OMC의 `code-reviewer` 에이전트 (opus)와 별개의 플러그인
- OMC 에이전트는 더 포괄적인 리뷰, 이 플러그인은 빠른 리뷰에 적합

---

> 생성일: 2026-04-02 | ootutorial v01
