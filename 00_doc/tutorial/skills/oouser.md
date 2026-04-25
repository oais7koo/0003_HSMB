# oouser Tutorial

> 사용자 가이드 관리 스킬 | 버전: v01 | 카테고리: doc-env

## 1. 이 스킬은 왜 필요한가?


**이런 상황에서 사용합니다:**
- 시스템: [프로젝트명] - [목적]
- 대상: 관리자/일반/게스트
- 요구: Chrome/Edge/Firefox, 1280x720+

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oouser run

# 상태 확인
oouser status

# 도움말
oouser help
```

## 3. 전체 서브명령어

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

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d{SP}0008_user.md (사용자 가이드/FAQ) 생성 및 현행화 |
| **하는 것** | 기능별 사용법 문서화, 스크린샷 연동, FAQ 업데이트 |
| **하지 않는 것** | 개발 문서(→oodoc), 튜토리얼(→ootutorial), 코드 수정(→oodev) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (코드, 기존 문서) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/d{SP}0008_user.md` |
| **실행 레벨** | [반자동] — 현재 기능 스캔 후 확인하여 작성 |
| **에이전트 호환** | 범용 — 파일 읽기·쓰기 작업 중심으로 모든 에이전트 처리 가능 |

### 표준 템플릿

```markdown
# d0008_user.md - 사용자 가이드

### 문서 이력

| 버전 | 날짜 | 변경 |
|------|------|------|

### 작성 규칙

| 항목 | 규칙 |
|------|------|
| 문체 | 경어체 통일 |
| 동사 | 구체적 (클릭/입력/선택) |
| 길이 | 1문장 1행동 |
| 이미지 | `00_doc/images/user/d0008_*.png` |

**표기**: 버튼 `[저장]`, 메뉴 [파일]->[새로만들기], 단축키 `Ctrl+S`

### 사용자 유형별

| 유형 | 중점 |
|------|------|
| 관리자 | 설정, 권한, 백업 |
| 일반 | 핵심 기능, 스크린샷 |
| 신규 | 시작하기, 용어, 튜토리얼 |

### 컴팩트 생성 원칙 (--compact)

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

## 5. 워크플로우

| 명령어 | 흐름 |
|--------|------|
| run | PRD 수집 -> 템플릿 생성 -> 저장 |
| add | 기능 수집 -> 템플릿 적용 -> 추가 |
| sync | PRD<->가이드 비교 -> 동기화 보고 |
| faq | 카테고리 결정 -> FAQ 추가 |

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oouser run
```

### 서브명령어 활용
```bash
oouser run  # 신규 생성
oouser update  # 현행화 — 현재 기능 스캔 → 사용자 가이드 갱신
oouser sync  # PRD 기반 동기화
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/oouser/scripts/oouser_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 분석 | Explore | haiku | 기능/UI/메뉴 스캔 (병렬) |
| 검증 | task-checker | sonnet | 완성도 검증 |

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
