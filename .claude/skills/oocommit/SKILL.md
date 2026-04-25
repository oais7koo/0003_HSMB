---
name: oocommit
description: "Git 커밋 및 이력 정리 스킬 'oocommit', '커밋', 'git 커밋', '이력 정리', 'github' 등의 키워드로 트리거된다"
metadata:
  version: v03
  category: core-dev
---

> 공통: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md
> 상세 가이드: .claude/skills/oocommit/references/guide.md

Git 커밋 + d{SP}0004 완료항목 -> d{SP}0010 이동 통합 워크플로우

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | Git 커밋 실행 + d{SP}0004 완료 항목 → d{SP}0010 이력 이동 통합 |
| **하는 것** | git commit, 기본 git push, d{SP}0004 완료 항목 아카이브, GitHub Issues 연동(선택) |
| **하지 않는 것** | 코드 수정(→oofix), 이슈 발견(→oocheck) |
| **참조 범위** | 현재 프로젝트 내부 파일 + 연결된 Git remote |
| **수정 대상** | Git 커밋, `d{SP}0004_todo.md`, `d{SP}0010_history.md` |
| **실행 레벨** | [반자동] — `--dry-run` 권장, 확인 후 실행 |
| **에이전트 호환** | 범용 — `git` CLI 사용 / GitHub Issues 연동(`github` 서브명령)은 `gh` CLI 및 MCP 필요 |

## 문서 이력 관리
- v03 2026-04-10 — `oocommit run/commit` 기본 동작을 commit + push로 변경, `--no-push` 유지
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oocommit help` | 서브명령어 목록 표시 |
| `oocommit version` | 스킬 버전 정보 (v03) |
| `oocommit status` | 서브명령어 리스트, 현재 상태 |
| `oocommit check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oocommit run` | Git 커밋 + 기본 push 실행 |
| `oocommit show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oocommit add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| run | 커밋 + push + 이력 정리 통합 (기본) - --dry-run 권장 |
| **run this** | **직전 작업 변경사항 커밋** (→ common_guide.md §9) |
| commit | Git 커밋 + 기본 push |
| sync | 이력 정리만 (d{SP}0004 -> d{SP}0010) |
| github | 태스크 -> GitHub Issues 변환 (MCP 연동) |
| preview | 변경사항 미리보기 |
| clear | 오래된 커밋 squash + .git 용량 정리 |

## 2. 워크플로우 (5단계)

1. **분석** -> git status/diff, 커밋 메시지 생성
2. **커밋** -> 스테이징, 실행 (사용자 확인)
3. **푸시** -> remote 반영 (upstream 없으면 `-u` 자동 처리)
4. **추출** -> d{SP}0004에서 [x]/해결 항목 식별
5. **이동/검증** -> d{SP}0010 추가, d{SP}0004 제거, 무결성 확인

## 3. 커밋 형식

`<type>(<scope>): <subject>` (Conventional Commits)

| 타입 | 설명 | 타입 | 설명 |
|------|------|------|------|
| feat | 새 기능 | refactor | 리팩토링 |
| fix | 버그 수정 | test | 테스트 |
| docs | 문서 | chore | 기타 |

## 4. 이력 이동 규칙

- **대상**: [x], 해결, 완료, CLOSED 키워드 항목
- **태그 매핑**: CRITICAL->HOTFIX, ERROR->BUGFIX, WARNING->IMPROVE, INFO->ENHANCE
- **형식**: ### [YYYY-MM-DD] [태그] 제목 + 파일/내용 기술

## 5. GitHub Issues 워크플로우 (github)

태스크(d{SP}0002, tasks.md)를 GitHub Issues로 변환하여 협업 및 추적 용이화

```bash
oocommit github                    # 전체 태스크 변환
oocommit github --task-id 1,2,3    # 특정 태스크만
oocommit github --dry-run          # 미리보기
oocommit github --sync             # 기존 이슈와 동기화
```

**워크플로우**:
```
oocommit github
    |
    |-> 1. 태스크 로드 (d{SP}0002, tasks.md, d{SP}0003)
    |-> 2. 의존성 분석 (태스크 간 의존관계, 생성 순서)
    |-> 3. GitHub CLI 연동 (gh issue create, 라벨 매핑)
    |-> 4. 이슈 생성 (제목, 본문, 라벨)
    |-> 5. 결과 반영 (이슈 번호 기록, 리포트)
```

**라벨 매핑**:

| 태스크 속성 | GitHub 라벨 |
|------------|-------------|
| priority: high | P0-critical |
| priority: medium | P1-important |
| priority: low | P2-normal |
| type: feature | enhancement |
| type: bug | bug |
| type: docs | documentation |

**옵션**:

| 옵션 | 설명 |
|------|------|
| --task-id <ids> | 특정 태스크만 변환 (쉼표 구분) |
| --dry-run | 실제 생성 없이 미리보기 |
| --sync | 기존 이슈와 양방향 동기화 |
| --labels <labels> | 추가 라벨 지정 |
| --milestone <name> | 마일스톤 지정 |
| --project <name> | GitHub Project 연결 |

## 6. 일반 옵션

| 옵션 | 설명 |
|------|------|
| --message "msg" | 커밋 메시지 지정 |
| --no-push | 기본 push 생략 |
| --dry-run | 미리보기 |
| --force-sync | 완료 항목 강제 이동 |

## 7. 주의사항

- 명시적 요청 없이 자동 커밋 금지 (확인 필수)
- 기본 동작은 push 포함이므로 로컬만 반영하려면 `--no-push` 사용
- 테스트/린트 통과, 민감정보 제외
- 완료 상태 명확한 항목만 이동

## 8. 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 분석 | Explore | haiku | O |
| 검토 | python-code-reviewer | sonnet | O |
| 검증/실행 | task-checker, task-executor | sonnet | - |
| GitHub | task-executor (MCP 연동) | sonnet | - |
| QA | oo-qa | sonnet | - |

## 9. GSD 연계

| 시나리오 | oo 스킬 | GSD 명령어 |
|---------|---------|-----------|
| 커밋 + push + 이력 정리 | `oocommit run` | - |
| 페이즈 완료 배포 | `oocommit run` 후 추가 배포 | `/gsd:ship` |
| PR 브랜치 생성 | `oocommit github` | `/gsd:pr-branch` |
| 마일스톤 완료 처리 | `oocommit run` → 수동 | `/gsd:complete-milestone` |
| 진행 상황 리포트 | - | `/gsd:session-report` |

**차이점:**
- `oocommit run` → git commit + 기본 push + d{SP}0004 완료항목 d{SP}0010 이동, Conventional Commits 형식
- `/gsd:ship` → GSD 기준 페이즈 완료 + 배포 자동화

**조합 패턴:**
```
oocheck run                # 품질 검증
  ↓
oocommit run               # 커밋 + push + OAIS 이력 정리(d0010)
  ↓
/gsd:ship                  # GSD 페이즈 완료 배포 (선택)
  OR
/gsd:complete-milestone    # 마일스톤 완료 처리 (선택)
```

## 10. 관련 문서

d{SP}0004_todo.md, d{SP}0010_history.md, .claude/skills/oocheck/SKILL.md, .claude/skills/oofix/SKILL.md

> **관련 명령어**: `.claude/commands/sc/git.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.claude/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |
| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |
| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |
| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |

**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.

<!-- KARPATHY-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->

