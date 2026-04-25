# oouser_guide - 사용자 가이드 관리 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oouser/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

사용자 대상 가이드 문서(d{SP}0008_user.md) 생성 및 관리 가이드입니다.

**목적**: 사용자 친화적 가이드 문서 자동화
**입력**: 00_doc/d{SP}0001_prd.md (기능 목록)
**출력**: 00_doc/d{SP}0008_user.md

**사용자 유형**: 관리자, 일반 사용자, 신규 사용자

## 2. 워크플로우

### 2.1 신규 생성 (run)

```
PRD 기능 목록 수집
    ↓
사용자 유형별 중점 파악
    ↓
표준 템플릿 적용
    ↓
d{SP}0008_user.md 생성
```

### 2.2 기능 추가 (add)

```
기능 정보 수집
    ↓
템플릿 적용 (설명/접근/사용법/주의)
    ↓
d{SP}0008 "주요 기능" 섹션에 추가
```

### 2.3 PRD 동기화 (sync)

```
PRD ↔ 가이드 비교
    ↓
누락/불일치 항목 파악
    ↓
동기화 보고서 출력
    ↓
선택적 반영
```

## 3. 상세 사용법

### 3.1 기본 명령어

```bash
# 신규 생성
uv run python .claude/skills/oouser/scripts/oouser_run.py run

# 서브프로젝트 지정
uv run python .claude/skills/oouser/scripts/oouser_run.py run --sp 02

# 상태 조회
uv run python .claude/skills/oouser/scripts/oouser_run.py status
```

### 3.2 기능 추가

```bash
# 기능 사용법 추가
uv run python .claude/skills/oouser/scripts/oouser_run.py add "로그인"

# 세부 옵션
uv run python .claude/skills/oouser/scripts/oouser_run.py add "데이터 내보내기" --user-type admin

# FAQ 추가
uv run python .claude/skills/oouser/scripts/oouser_run.py faq "로그인이 안 될 때"
```

### 3.3 PRD 동기화

```bash
# PRD 기반 동기화 확인
uv run python .claude/skills/oouser/scripts/oouser_run.py sync

# 결과:
# - PRD 신규 기능: 3개 → d0008에 추가 권장
# - d0008 고아 항목: 1개 → PRD 확인 필요
```

## 4. 사용 예시

### 예시 1: 사용자 가이드 신규 생성

```bash
# 1. PRD 확인
# d20001_prd.md: 로그인, 대시보드, 정책 조회 기능

# 2. 사용자 가이드 생성
uv run python .claude/skills/oouser/scripts/oouser_run.py run --sp 02

# 3. d20008_user.md 생성 완료
# - 섹션 1: 개요 (시스템 소개)
# - 섹션 2: 시작하기 (접속, 로그인)
# - 섹션 3: 주요 기능 (PRD 기반)
# - 섹션 4: 화면별 안내
# - 섹션 5: FAQ
# - 섹션 6: 트러블슈팅
```

### 예시 2: 기능별 사용법 추가

```bash
# 로그인 기능 상세 추가
uv run python .claude/skills/oouser/scripts/oouser_run.py add "로그인"
```

**d0008 출력**:
```markdown
### 3.1 로그인

**설명**: 시스템 접속을 위한 로그인 절차

**접근 방법**: 메인 화면 → [로그인] 버튼

**사용법**:
1. 사용자 ID 입력
2. 비밀번호 입력
3. [로그인] 버튼 클릭

**주의사항**: ID/PW 5회 오류 시 계정 잠금
```

### 예시 3: FAQ 추가

```bash
# FAQ 항목 추가
uv run python .claude/skills/oouser/scripts/oouser_run.py faq "로그인이 안 될 때"
```

**d0008 출력**:
```markdown
## 5. FAQ

### Q: 로그인이 안 될 때
A: 다음을 확인하세요.
- ID/PW 확인
- 계정 잠금 여부
- 브라우저 쿠키 허용 설정
```

## 5. 작성 규칙

### 5.1 문체

| 항목 | 규칙 |
|------|------|
| 문체 | 경어체 통일 ("~합니다", "~하세요") |
| 동사 | 구체적 (클릭, 입력, 선택) |
| 길이 | 1문장 1행동 |

### 5.2 표기법

| 요소 | 표기 | 예시 |
|------|------|------|
| 버튼 | 대괄호 | [저장] 버튼 |
| 메뉴 | 화살표 | [파일]→[새로만들기] |
| 단축키 | 백틱 | `Ctrl+S` |

### 5.3 이미지

- 경로: `00_doc/images/user/d0008_*.png`
- 네이밍: `d0008_섹션번호_기능명.png`
- 예시: `d0008_3.1_로그인.png`

### 5.4 사용자 유형별 중점

| 유형 | 중점 내용 |
|------|----------|
| 관리자 | 설정, 권한 관리, 백업 절차 |
| 일반 사용자 | 핵심 기능, 스크린샷 중심 |
| 신규 사용자 | 시작하기, 용어 설명, 튜토리얼 |

## 6. 표준 템플릿 구조

```markdown
# d{SP}0008_user.md - 사용자 가이드

## 문서 이력
| 버전 | 날짜 | 변경 |
|------|------|------|

## 1. 개요
- 시스템: [프로젝트명] - [목적]
- 대상: 관리자/일반/게스트
- 요구사항: 브라우저, 해상도

## 2. 시작하기
접속 → 로그인 → 기본 사용법

## 3. 주요 기능
### 3.X [기능명]
- 설명
- 접근 방법
- 사용법
- 주의사항

## 4. 화면별 안내

## 5. FAQ

## 6. 트러블슈팅
| 증상 | 원인 | 해결 |

## 7. 용어 설명

## 8. 문의처
```

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oouser/SKILL.md | 스킬 명세 |
| 00_doc/d{SP}0008_user.md | 출력 문서 |
| 00_doc/d{SP}0001_prd.md | 입력 (기능 목록) |
| 00_doc/d{SP}0003_test.md | 검증 참조 |

**에이전트**: Explore, task-checker

**이미지 저장**: `00_doc/images/user/`
