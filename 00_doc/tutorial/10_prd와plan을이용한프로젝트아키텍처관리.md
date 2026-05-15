# ooprd + ooplan으로 프로젝트 아키텍처 관리하기

> 목표 설정·플래닝·방향성 변경·추가/수정의 전체 생애주기 | 최종 업데이트: 2026-04-29

## 개요

`ooprd`와 `ooplan`은 함께 쓰일 때 가장 강력하다.

| 스킬 | 역할 | 관리 문서 |
|------|------|-----------|
| `ooprd` | **"무엇을 만들까"** — 목표·요구사항·범위 정의 | `d{SP}0001_prd.md` |
| `ooplan` | **"어떻게 만들까"** — Epic→Feature→Task 분해·설계 | `d{SP}0002_plan.md` |

PRD가 바뀌면 Plan도 바뀐다. 이 두 문서의 정합성을 유지하는 것이 프로젝트 아키텍처 관리의 핵심이다.

---

## 시나리오 1: 신규 프로젝트 셋업

서브프로젝트를 처음 시작할 때의 흐름.

### 1단계: 컨텍스트 설정

```bash
oocontext 4    # SP04로 전환 (예시)
```

### 2단계: PRD 생성 (목표 정의)

```bash
ooprd run
```

- PRD가 없으면 템플릿 기반 초안 생성 모드로 진입
- Claude가 1개씩 순차 질문 → `skip` 입력 시 AI 판단으로 대체
- 결과: `00_doc/sp04/d40001_prd.md` 생성

**PRD 핵심 섹션**:
```
1. 프로젝트 개요 (목적·배경)
2. 기능 요구사항 (Must/Should/Could)
3. 기술 스택
4. 제약 조건
5. 성공 지표
```

### 3단계: Plan 생성 (구현 분해)

```bash
ooplan run
```

- PRD를 읽어 Epic→Feature→Task로 자동 분해
- 결과: `00_doc/sp04/d40002_plan.md` 생성

**Plan 분해 체계**:
```
PRD 목표
  └─ Epic (도메인 단위, 예: 인증, 데이터수집, 분석)
      └─ Feature (기능 단위, 예: 로그인, OAuth, 토큰갱신)
          └─ Task (구현 단위, 예: JWT 미들웨어 작성)
              └─ TC (테스트 케이스)
```

### 4단계: 검증

```bash
ooprd check --structure    # PRD 구조 검증
ooplan check --fix         # Plan 검토·개선 제안
```

---

## 시나리오 2: 기능 추가

기존 프로젝트에 새 기능을 추가할 때.

### 방법 A: PRD 먼저 수정 후 Plan 동기화 (권장)

> `ooprd update`는 코드베이스 스캔 → PRD 갱신 방향이다. **새 요구사항 추가**는 먼저 Claude에게 내용을 설명하거나 PRD 파일을 직접 편집한 뒤 해당 섹션을 갱신해야 한다.

```bash
# 1. 새 요구사항을 Claude에게 설명하거나 PRD 직접 편집
#    예) "사용자 인증 기능을 추가하고 싶다. 소셜 로그인(Google/Kakao) 포함"
#    → Claude가 내용을 반영하여 PRD 섹션 갱신
ooprd section 2          # 기능 요구사항 섹션만 갱신 (권장)
# 또는
ooprd run this           # 직전 대화 기반으로 관련 섹션 갱신

# 2. PRD 변경사항을 Plan에 동기화
ooplan sync

# 3. 변경 전 미리보기 (선택)
ooplan update --dry-run
```

### 방법 B: 직전 작업 기준 부분 갱신

작은 기능 1개만 추가한 경우. `run this`는 **직전 대화에서 언급한 내용**을 컨텍스트로 사용하므로, 반드시 먼저 Claude에게 무엇을 추가할지 말해야 한다.

```
[사용자] CSV 다운로드 버튼을 결과 페이지에 추가하고 싶어
[Claude] 알겠습니다. ...
```

```bash
# 직전 대화 내용 기준으로 PRD 관련 섹션만 갱신
ooprd run this

# 직전 대화 내용 기준으로 Plan 업데이트
ooplan run this
```

> `run this`는 대화 컨텍스트를 읽는다. **명령만 단독으로 실행하면 무엇을 추가할지 모른다.**

---

## 시나리오 3: 방향성 변경 (목표 수정)

요구사항이 바뀌거나 스코프가 조정될 때.

### 소규모 변경 (기능 1~3개 수정)

먼저 Claude에게 무엇을 바꿀지 설명하고, 해당 섹션만 갱신한다.

```
[사용자] 결제 수단에 카카오페이를 추가하고 싶어. 기존 카드결제는 유지.
[Claude] 알겠습니다. ...
```

```bash
ooprd section 2            # 기능 요구사항 섹션만 갱신
ooplan sync                # Plan에 반영
```

### 중규모 변경 (방향 일부 전환)

방향을 바꾸는 것이므로 PRD-first 접근이 맞다. 먼저 Claude에게 변경 방향을 설명한 뒤 PRD를 갱신하고, 이후 Plan을 동기화한다.

> `ooprd update`는 코드→PRD 방향(코드가 이미 바뀐 경우)이라 방향 전환 시나리오에는 맞지 않는다.

```
[사용자] API 방식을 REST에서 GraphQL로 전환하고 싶어. 기술 스택과 아키텍처가 바뀜.
[Claude] 알겠습니다. ...
```

```bash
# 1. 변경 방향을 반영하여 PRD 갱신
ooprd run this             # 직전 대화 기반 PRD 갱신
# 또는 여러 섹션이 바뀌면
ooprd section 3            # 기술 스택 섹션 갱신
ooprd section 4            # 제약 조건 섹션 갱신

# 2. 변경 전 Plan 미리 확인
ooplan update --dry-run

# 3. Plan 동기화
ooplan sync

# 4. 정합성 최종 검증
ooprd check --structure
```

### 대규모 변경 (목표 자체가 바뀜)

```bash
# 1. 기존 PRD 백업은 git이 처리 → 바로 재생성
ooprd run --template [type]    # 새 템플릿으로 재시작

# 2. Plan 완전 재생성
ooplan run

# 3. 모호한 부분 해소
ooprd clarify
```

**템플릿 선택 기준**:
| 상황 | 템플릿 |
|------|--------|
| 웹앱/대시보드 | `streamlit` |
| ML·분석 파이프라인 | `algorithm` |
| CLI·에이전트 | `agent` |
| 일반 | `common` (기본값) |

---

## 시나리오 4: 코드 변경 후 문서 현행화

구현이 진행되면서 PRD·Plan과 코드가 벌어질 때.

```bash
# 코드베이스 스캔 → PRD 불일치 자동 감지 → d0004_todo.md 등록
ooprd run

# 코드 현황 스캔 → Plan 변경분 반영
ooplan update

# 완료 후 미착수 Feature 확인
oofeature needed
```

---

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| Plan 먼저 만들고 PRD 나중에 | PRD → Plan 순서 필수 |
| 코드만 고치고 PRD/Plan 방치 | `ooprd run` + `ooplan update` 세트로 실행 |
| 방향 바꿀 때 Plan만 수정 | PRD 먼저 수정 → `ooplan sync` |
| 큰 변경을 `run this`로 처리 | 변경 규모에 맞게 `update` 또는 `run` 선택 |

---

## 빠른 참조

```bash
# 신규 셋업
ooprd run → ooplan run

# 기능 추가 (Claude에게 설명 후)
ooprd section N 또는 ooprd run this → ooplan sync

# 방향성 변경 (소규모)
ooprd section N → ooplan sync

# 방향성 변경 (대규모)
ooprd run --template X → ooplan run

# 코드→문서 현행화
ooprd run → ooplan update → oofeature needed
```

---

## 관련 스킬

| 스킬 | 역할 |
|------|------|
| `oofeature` | Plan의 Feature를 상세 문서로 관리 |
| `oodev` | Task 기반 구현 |
| `oocheck` | 구현 후 코드 정합성 검증 |
| `oofix` | 발견된 이슈 수정 |
| `oodoc` | 전체 문서 일괄 관리 |
| `oocontext` | 서브프로젝트 전환 (SP 컨텍스트 설정) |
