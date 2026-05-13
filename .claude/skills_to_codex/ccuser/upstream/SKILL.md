---
name: oouser
description: "사용자 가이드 관리 스킬 'oouser', '사용자 가이드', '유저 가이드', 'FAQ' 등을 요청할 때 사용한다"
metadata:
  version: "v01"
  category: "doc-env"
---

# oouser - 사용자 가이드 관리 스킬

> 공통: `.claude/guides/common_guide.md` 참조

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d{SP}0008_user.md (사용자 가이드/FAQ) 생성 및 현행화 |
| **하는 것** | 기능별 사용법 문서화, 스크린샷 연동, FAQ 업데이트 |
| **하지 않는 것** | 개발 문서(→oodoc), 튜토리얼(→ootutorial), 코드 수정(→oodev) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (코드, 기존 문서) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/d{SP}0008_user.md` |
| **실행 레벨** | [반자동] — 현재 기능 스캔 후 확인하여 작성 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

## 1. 개요

d{SP}0008_user.md 생성/관리

## 2. 서브명령어

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `oouser help` | 서브명령어 목록 표시 | 터미널 |
| `oouser version` | 스킬 버전 정보 (v01) | 터미널 |
| `oouser run` | 신규 생성 | 00_doc/d{SP}0008_user.md |
| `oouser update` | 현행화 — 현재 기능 스캔 → 사용자 가이드 갱신 | d{SP}0008_user.md |
| `oouser update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| `oouser status` | 서브명령어 리스트, 현황 조회 | 터미널 |
| `oouser check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oouser show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oouser add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oouser add [기능명]` | 기능 사용법 추가 | 00_doc/d{SP}0008_user.md |
| `oouser faq [질문]` | FAQ 추가 | 00_doc/d{SP}0008_user.md |
| `oouser sync` | PRD 기반 동기화 | 00_doc/d{SP}0008_user.md |

실행: `uv run python .claude/skills/oouser/scripts/oouser_run.py [args]`

## 3. 표준 템플릿

```markdown
# d0008_user.md - 사용자 가이드

## 문서 이력
| 버전 | 날짜 | 변경 |
|------|------|------|

## 1. 개요
- 시스템: [프로젝트명] - [목적]
- 대상: 관리자/일반/게스트
- 요구: Chrome/Edge/Firefox, 1280x720+

## 2. 시작하기
접속 -> 로그인 -> 기본 사용법

## 3. 주요 기능
### 3.X [기능명]
- 설명/접근/사용법/주의

## 4. 화면별 안내
## 5. FAQ
## 6. 트러블슈팅
| 증상 | 원인 | 해결 |
## 7. 용어
## 8. 문의
```

## 4. 워크플로우

| 명령어 | 흐름 |
|--------|------|
| run | PRD 수집 -> 템플릿 생성 -> 저장 |
| add | 기능 수집 -> 템플릿 적용 -> 추가 |
| sync | PRD<->가이드 비교 -> 동기화 보고 |
| faq | 카테고리 결정 -> FAQ 추가 |

## 5. 작성 규칙

| 항목 | 규칙 |
|------|------|
| 문체 | 경어체 통일 |
| 동사 | 구체적 (클릭/입력/선택) |
| 길이 | 1문장 1행동 |
| 이미지 | `00_doc/images/user/d0008_*.png` |

**표기**: 버튼 `[저장]`, 메뉴 [파일]->[새로만들기], 단축키 `Ctrl+S`

## 6. 사용자 유형별

| 유형 | 중점 |
|------|------|
| 관리자 | 설정, 권한, 백업 |
| 일반 | 핵심 기능, 스크린샷 |
| 신규 | 시작하기, 용어, 튜토리얼 |

## 7. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 분석 | Explore | haiku | 기능/UI/메뉴 스캔 (병렬) |
| 검증 | task-checker | sonnet | 완성도 검증 |

## 컴팩트 생성 원칙 (--compact)

`oouser run --compact` 또는 `oodoc run --compact` 호출 시 적용. guide.md 템플릿보다 우선:

| 원칙 | 규칙 |
|------|------|
| 목표 크기 | 3KB 이내 |
| 형식 | 테이블/불릿 우선, 산문 금지 |
| 이력 | 최근 3개만 유지 |
| 섹션 | 필수 섹션만 (문서이력 + 핵심 2~3개) |
| 설명 | 줄당 1개 정보, 10줄 이내/섹션 |
| 제외 | 예제 코드, 워크플로우 다이어그램, 부연 설명 |

> **관련 문서**: `d{SP}0008_user.md` | `d{SP}0001_prd.md` | `d{SP}0003_test.md`

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

