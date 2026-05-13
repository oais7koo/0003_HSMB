---
name: oostop
description: "세션 종료 워크플로우 스킬 'oostop', '세션 종료', '작업 종료' 등을 요청할 때 트리거된다"
metadata:
  version: "v01"
  category: "meta-util"
---

# oostop - 세션 종료 워크플로우

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 세션 종료 전 미완료 항목 정리·요약·이력 기록 |
| **하는 것** | 미완료 작업 목록 표시, 이력 정리 안내, 세션 요약 출력 |
| **하지 않는 것** | 파일 강제 저장(자동 저장됨), git push, 세션 외부 상태 변경 |
| **참조 범위** | 현재 프로젝트 내부 문서 파일 / 외부 시스템 자동 연결 안 함 |
| **수정 대상** | `d{SP}0010_history.md` (세션 요약 기록, 선택) |
| **실행 레벨** | [반자동] — 정리 항목 확인 후 종료 |
| **에이전트 호환** | 범용 — 파일 읽기·요약 중심으로 모든 에이전트 처리 가능 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oostop help` | 서브명령어 목록 표시 |
| `oostop version` | 스킬 버전 정보 (v01) |
| `oostop status` | 서브명령어 리스트, 현재 상태 |
| `oostop check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oostop show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oostop add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oostop run` | **전체 종료 실행 (기본): cleanup → readme → sync → oocommit run** |
| `oostop cleanup` | MCP 좀비 node 프로세스 정리 (Windows) |
| `oostop readme` | README.md만 (1단계) |
| `oostop sync` | 00_doc/*.md만 (2단계) |

## 종료 워크플로우

```
1단계: README.md → 2단계: 00_doc/*.md → 3단계: oocommit run
(작업내역, 다음작업)  (d0001~d0010)      (git 커밋)
```

### README.md 템플릿

```markdown
## 최근 작업 내역
- 날짜: YYYY-MM-DD
- 작업: [요약]
- 변경: [파일]
- 다음: [후속]
```

### 00_doc/*.md 동기화

| 문서 | 조건 |
|------|------|
| d{SP}0001_prd.md | 기능 추가/변경 |
| d{SP}0004_todo.md | 완료/새 이슈 |
| d0005_lib.md | 라이브러리 추가 |
| d{SP}0010_history.md | 모든 변경 |

## 체크리스트

**사전**: 문법 오류 없음 | 테스트 통과 | tmp/ 정리

**문서**:
- [ ] README.md: 개요, 구조, 설치, 변경
- [ ] d{SP}0004_todo.md: 완료/이슈
- [ ] d{SP}0010_history.md: 버전 이력

## 커밋

> Git 규칙: `.claude/guides/common_guide.md` 3.2절

| 타입 | 형식 |
|------|------|
| feat | `feat: [기능] 완료` |
| fix | `fix: [버그] 수정` |
| refactor | `refactor: [대상] 개선` |

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 조합 |
|------|----------|------|----------|
| 검증 | `task-checker` | sonnet | + `ooqa` (다수 파일) |
| 품질 | `ooqa` | sonnet | + `task-checker` |
| 탐색 | `Explore` | haiku | + `task-executor` (문서 갱신) |
| 갱신 | `task-executor` | sonnet | + `Explore` |

## 주의사항

- 테스트 필수: 변경 후 통과 확인
- 문서 일관성: 코드-문서 불일치 방지
- 커밋 원자성: 관련 변경만
- 임시 제외: tmp/, __pycache__/

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

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
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

## 관련 문서

- `.claude/skills/oostart/SKILL.md` - 세션 시작
- `00_doc/d{SP}0004_todo.md` - 할 일/디버깅
- `00_doc/d{SP}0010_history.md` - 변경 이력
