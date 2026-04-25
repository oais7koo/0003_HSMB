# oocommit Tutorial

> Git 커밋 + d{SP}0004 → d{SP}0010 이력 이동 자동화 | 버전: v03 | 카테고리: core-dev

## §1 이유 (Reason)

작업 완료 후 Git 커밋, GitHub 푸시, TODO 문서 → 이력 문서 이동을 한 번에 처리합니다.

## §2 빠른 시작 (Quick Start)

```bash
oocommit "feat: 새 기능 추가"
```

자동 처리: staging → commit → push → d0004 → d0010 이동

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oocommit "feat: ..."` | 기능 추가 |
| `oocommit "fix: ..."` | 버그 수정 |
| `oocommit "refactor: ..."` | 코드 정리 |
| `oocommit "docs: ..."` | 문서 수정 |
| `oocommit github` | GitHub Issue 링크 |

## §4 권장 흐름 (Recommended Flow)

1. 기능/버그 수정 완료
2. `git add .` 로 스테이징
3. `oocommit "type: description"` 실행
4. 자동으로:
   - Git 커밋 생성
   - GitHub 푸시
   - d{SP}0004 내용 → d{SP}0010 이동

## §5 전체 명령어 (All Commands)

```
oocommit help
oocommit version
oocommit "type: message"
oocommit github [ISSUE_NUM]
oocommit history
oocommit revert [COMMIT_HASH]
```

## §6 상세 사용법 (Detailed Usage)

**Conventional Commits 타입:**
- `feat` — 새로운 기능
- `fix` — 버그 수정
- `refactor` — 코드 리팩토링
- `docs` — 문서 수정
- `test`, `chore`, `perf`, `ci`

## §7 실전 예시 (Real Examples)

```bash
oocommit "feat(sp02): 카드내역 자동 매칭 기능 추가"
oocommit "fix(sp04): CMS 배치 apl_id 상태 불일치 해결"
oocommit "fix: 로그인 오류" --issue 123
```

## §8 입출력 (Input/Output)

**입력:** 스테이징된 Git 변경사항, 메시지
**출력:** Git 커밋, d{SP}0010 기록

## §9 FAQ

**Q: 커밋 메시지 규칙은?**
A: Conventional Commits: `type: description`

**Q: GitHub에 자동 푸시되나?**
A: 네, 기본 동작. `--no-push` 플래그로 비활성화.

## §10 서브에이전트 (Sub-agents)

- git-workflow-expert, github-integration, document-keeper

## §11 관련 스킬 (Related Skills)

- `oocheck`, `oodev`, `oohistory`, `ootodo`

---

**버전**: v03 | **카테고리**: core-dev | **업데이트**: 2026-04-14
