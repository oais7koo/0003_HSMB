# oofeature 워크플로우 상세 레퍼런스

> SKILL.md §3~§5 상세 내용 분리본. SKILL.md에서 참조됨.

---

## §3. 파일명 규칙

### 3.1 형식

```
d{SP번호}{기능번호}_상세{단계}_{기능명}.md
```

| 구성 | 설명 | 예시 |
|------|------|------|
| `d{SP번호}{기능번호}` | SP+기능 식별자 | `d41001`, `d51001` |
| `_상세{단계}_` | 현재 단계 | `_상세기획_`, `_상세설계_` |
| `{기능명}` | 기능 한글명 | `데이터수집소스`, `크롤러모듈` |

### 3.2 단계 순서

```
⚪ 상세기획 → 🔵 상세설계 → 🟡 상세구현 → 🟢 상세검증 → ✅ 상세완료
```

| 단계 | 파일명 키워드 | 다음 연계 스킬 |
|------|-------------|--------------|
| 기획 | `_상세기획_` | ooplan detail |
| 설계 | `_상세설계_` | oofeature next dXXXX (→ oodev run 자동 연계) |
| 구현 | `_상세구현_` | oofeature next dXXXX (→ oocheck run 자동 연계) |
| 검증 | `_상세검증_` | oofeature next dXXXX (→ 완료) |
| 완료 | `_상세완료_` | oocommit run (자동 연계) |

### 3.3 스캔 패턴

`ooplan sync` 및 `oofeature list`가 사용하는 탐색 패턴:
```
00_doc/sp{N}/*_상세기획_*.md
00_doc/sp{N}/*_상세설계_*.md
00_doc/sp{N}/*_상세구현_*.md
00_doc/sp{N}/*_상세검증_*.md
00_doc/sp{N}/*_상세완료_*.md
```

### 3.4 번호 부여 규칙

| 범위 | 용도 |
|------|------|
| `d{SP}0001~d{SP}0999` | SP 공통 문서 (PRD, Plan, Test, Todo 등) — 예약, oofeature 미사용 |
| **`d{SP}1000~d{SP}9999`** | **상세 문서 전용 범위 (oofeature 관리 대상)** |

**카테고리 (천번대) 체계:**
- 큰 기능 카테고리별로 **1000, 2000, 3000...** 단위로 할당
- 세부 번호는 **10단위** 사용 (1010, 1020, 1030...)
- 카테고리 내 번호가 부족하면 다음 천번대로 이동

```
d{SP}1000~1999  → 1번 카테고리 (기능 그룹 A)
  d{SP}1010       첫 번째 기능
  d{SP}1020       두 번째 기능
  d{SP}1030       세 번째 기능
d{SP}2000~2999  → 2번 카테고리 (기능 그룹 B)
  d{SP}2010       첫 번째 기능
  ...
```

> **카테고리 정의는 각 SP의 PRD §1.4 참조** — SKILL.md에 SP별 카테고리를 두지 않음 (oosync 배포 대상).
> 예) SP04: `d40001_prd.md §1.4` / SP05: `d50001_prd.md §1.4`

> **기존 문서 번호 (d40xxx)**: 규칙 정비 전 생성된 문서로, 신규 문서는 1000번대부터 사용한다.

---

## §4. 워크플로우 상세

### 4.1 new (상세기획 문서 생성)

```
oofeature new d41001 "데이터수집소스"                         # 공통 템플릿 (기본)
oofeature new d41001 "데이터수집소스" --framework fastapi      # FastAPI 전용 템플릿
oofeature new d40448 "챗봇관리" --framework streamlit          # Streamlit 전용 템플릿
    ↓
[템플릿 선택]
  --framework streamlit 또는 04_backoffice/ 자동 감지 → templates/상세기획_template_streamlit.md
  --framework fastapi   또는 05_api_server/ 자동 감지 → templates/상세기획_template_fastapi.md
  그 외 (기본)                                        → templates/상세기획_template.md
    ↓
00_doc/sp{N}/d41001_상세기획_데이터수집소스.md 저장
    ↓
ooplan sync → plan.md 8.2절 자동 갱신
```

### 4.2 next (다음 단계 전환 / 상세기획 자동 생성)

> **메인 플로우**: `oofeature next dXXXX`로 모든 단계 전환 가능. 설계→구현 시 `oodev run` 자동 연계, 구현→검증 시 `oocheck run` 자동 연계.
> **파일 없을 때**: `oofeature new`처럼 동작 — 상세기획 문서 자동 생성.

```
oofeature next d41001
    ↓
[파일 존재 여부 확인]
  파일 없음 → 상세기획 자동 생성 (new 대용)
    plan.md에서 d41001 기능명 자동 조회
    조회 실패 시: 기능명 입력 요청
    → 00_doc/sp{N}/d41001_상세기획_{기능명}.md 생성
    → ooplan sync
  파일 있음 → 현재 파일명에서 단계 감지
    ↓
파일명 rename → 다음 단계로 변경
  (예: 상세기획 → 상세설계)
    ↓
연계 스킬 안내:
  기획→설계: rename → "설계 작성 완료 후 `oofeature next dXXXX` 재실행하세요"
  설계→구현: rename → `oodev run dXXXX` 자동 연계 실행 (TC RED + 코딩)
  구현→검증: rename → `oocheck run dXXXX` 자동 연계 실행 (코드 체크 + d0004 등록)
  검증→완료: rename → `oocommit run` 자동 연계 실행
    ↓
ooplan sync → plan.md 8.2절 갱신
```

> **⚠️ 설계→구현 전환 필수 체크리스트 (건너뜀 금지)**
>
> 설계→구현 파일명 rename 직후 반드시 아래 순서로 실행:
> 1. ✅ 파일명 확인: `_상세설계_` → `_상세구현_` rename 완료
> 2. ✅ **즉시** `oodev run dXXXX` Skill 도구로 실행 — 이 단계를 건너뛰면 TDD 사이클이 누락됨
> 3. ✅ oodev GREEN+REFACTOR 완료 후 다음 단계 진행
>
> **실수 방지**: `oofeature next`가 설계→구현 rename을 완료하면 그 자리에서 `oodev run dXXXX`를 Skill 도구로 호출할 것. rename만 하고 다른 작업을 먼저 하거나 사용자 응답으로 끝내지 말 것.

**`oofeature new` vs `oofeature next` 선택 기준:**

| 상황 | 권장 명령 |
|------|----------|
| plan.md에 Feature 있음 (일반) | `oofeature next dXXXX` |
| plan.md에 없는 기능 추가 | `oofeature new dXXXX "기능명"` |
| 기능명을 직접 지정하고 싶을 때 | `oofeature new dXXXX "기능명"` |

### 4.3 needed (상세기획 미착수 Feature 리스트업)

> `ooplan run` 완료 후 실행하는 gate check. plan.md에 Feature 목록이 생성되어 있어야 동작함.

```
oofeature needed
    ↓
1. d{SP}0002_plan.md 읽기 → Feature 목록 추출
   (8.1절 Feature 테이블: Feature ID / Epic / 우선순위 / 기능명)
    ↓
2. 00_doc/sp{N}/ 스캔 → 상세 문서 목록 수집
   (*_상세기획_*.md, *_상세설계_*.md, *_상세구현_*.md, *_상세검증_*.md)
    ↓
3. 교차 비교 → 상세 문서가 없는 Feature 식별
    ↓
4. 우선순위 순 정렬 (high > medium > low)
    ↓
5. 미착수 Feature 목록 출력
```

**출력 형식**:

```markdown
[oofeature needed] SP04 — 상세기획 미착수 Feature

| Feature ID | 기능명 | Epic | 우선순위 | 권장 시작 단계 |
|-----------|--------|------|:-------:|:------------|
| F001-1 | 데이터수집소스 정의 | E001 | high | 상세기획 |
| F001-2 | 크롤러 모듈 설계 | E001 | high | 상세기획 |
| F002-1 | 전처리 파이프라인 | E002 | medium | 상세기획 |

총 N개 미착수 (전체 M개 중)
```

**규칙**:
- 상세 문서가 어떤 단계(기획/설계/구현/검증)든 **하나라도 존재**하면 착수로 간주
- Feature ID 매핑: 문서 파일명의 번호(`d41001` 등) ↔ plan.md Feature ID 교차 확인
- `--sp N` 옵션: 해당 SP만 스캔 (기본값: 현재 oocontext SP)
- 권장 시작 단계: 기본 "상세기획", 관련 설계서가 이미 있으면 "상세설계"

### 4.5 note (AI 통합 메모)

> **Claude 실행 전용** — 스크립트는 파일 탐색만, 본문 통합은 Claude가 직접 수행

```
oof note dXXXX "내용"
    ↓
1. 스크립트로 파일 경로 탐색
   uv run python oofeature_note.py dXXXX --find [--sp N]
   → 파일 경로 출력 (예: 00_doc/sp04/d40101_상세기획_기능명.md)
    ↓
2. Read 툴로 문서 전체 읽기
    ↓
3. 노트 내용 분석 → 적절한 섹션 판단
   예) "입력 유효성 조건 추가" → ## 2. 요구사항 또는 ## 4. 제약조건
       "API 엔드포인트 변경"   → ## 3. 입출력 정의
       "외부 연동 제거"        → ## 4. 제약조건
    ↓
4. Edit 툴로 해당 섹션에 내용 통합
   - 기존 섹션 내용은 보존, 추가/수정만
    ↓
5. 스크립트로 ## 메모에 이력 기록
   uv run python oofeature_note.py dXXXX --memo "내용" --section "섹션명" [--sp N]
```

**섹션 판단 기준**:

| 노트 내용 키워드 | 대상 섹션 |
|----------------|----------|
| 요구사항, 기능, 조건, 허용/금지 | ## 2. 요구사항 |
| 입력, 출력, API, 파라미터, 반환 | ## 3. 입출력 정의 |
| 제약, 예외, 에러, 금지, 불가 | ## 4. 제약조건 / 예외처리 |
| 연관 기능, Feature, 의존 | ## 5. 관련 Feature |
| 참고, 문서, 링크, 참조 | ## 6. 참고 자료 |
| 판단 불가 | ## 2. 요구사항 (기본값) |

### 4.6 list (현황 조회)

```
oofeature list
    ↓
현재 SP 00_doc/sp{N}/ 스캔
    ↓
상세 문서 목록 + 단계 출력:

[oofeature list] SP04

| 문서번호 | 기능명 | 단계 | 파일 |
|---------|--------|------|------|
| d41001 | 데이터수집소스 | 🔵설계 | d41001_상세설계_데이터수집소스.md |
| d40101 | 크롤러모듈 | 🟡구현 | d40101_상세구현_크롤러모듈.md |

총 2개 | 기획:0 설계:1 구현:1 검증:0 완료:0
```

### 4.7 issue (이슈 추가/해결)

```
oof issue dXXXX "이슈내용"
    ↓
uv run python oofeature_issue.py dXXXX "이슈내용" [--sp N]
    ↓
상세 문서 ## 이슈 섹션에 행 추가:
  | 날짜 | 내용 | 상태 |
  | 2026-04-10 | 이슈내용 | 🔴 미해결 |
    ↓
## 이슈 섹션 없으면 자동 생성
```

```
oof issue dXXXX --resolve
    ↓
uv run python oofeature_issue.py dXXXX --resolve [--sp N]
    ↓
## 이슈 섹션에서 가장 마지막 🔴 미해결 행 → ✅ 해결 로 변경
```

**이슈 테이블 형식**:

| 날짜 | 내용 | 상태 |
|------|------|------|
| 2026-04-10 | 예시 이슈 | 🔴 미해결 |
| 2026-04-09 | 해결된 이슈 | ✅ 해결 |

**스크립트**: `uv run python .claude/skills/oofeature/scripts/oofeature_issue.py`

---

## §5. 상세기획 문서 표준 구조

### 5.1 템플릿 구조

| 구분 | 파일 | 사용 조건 | 선택 방법 |
|------|------|---------|---------|
| 공통 | `templates/상세기획_template.md` | 일반 Python / 프레임워크 미지정 | 기본값 |
| Streamlit | `templates/상세기획_template_streamlit.md` | `04_backoffice/` Streamlit 백오피스 페이지 | `--framework streamlit` |
| FastAPI | `templates/상세기획_template_fastapi.md` | `05_api_server/` 기반 API 기능 | `--framework fastapi` |

> **자동 감지 규칙**: `--framework` 미지정 시 SP 폴더 자동 감지
> - SP04(`04_backoffice/`) → streamlit 자동 적용
> - SP05(`05_api_server/`) → fastapi 자동 적용
> - 그 외 → 공통 템플릿

### 5.2 공통 템플릿 (`상세기획_template.md`)

기본 섹션 (§1~§7):

```markdown
## 1. 기능 개요
## 2. 요구사항
## 3. 입출력 정의 (입력/출력 테이블)
## 4. 제약조건 / 예외처리
## 5. 관련 Feature
## 6. 참고 자료
## 7. 이슈
```

### 5.3 FastAPI 전용 템플릿 (`상세기획_template_fastapi.md`)

총 10개 섹션 구성. §1 문서관리 표 포함, §9~§10 FastAPI 전용:

**§1 문서 관리** — 문서 식별 정보 표:

| 항목 | 설명 |
|------|------|
| 문서번호 | `{dXXXX}` |
| 대상 기능 | `{F_ID} {기능명}` |
| 원본 페이지 | `{project}/pages/{page}.py` (없으면 삭제) |
| oais 함수 | `oais/{module}.py {function}()` |
| 버전 | v01 |
| 작성일 | `{YYYY-MM-DD}` |
| 관련 문서 | (없으면 삭제) |
| **엔드포인트 (1단계)** | `POST /api/v1/tasks/{task_type_1}` — {단계 설명} |
| **엔드포인트 (2단계)** | `POST /api/v1/tasks/{task_type_2}` — {단계 설명} (단일 단계 시 삭제) |

**전체 섹션 구조:**

```markdown
## 변경 이력
## 1. 문서 관리
## 2. 기능 개요
  ### 2.1 엔드포인트
## 3. 요구사항
## 4. 입출력 정의
  ### 4.1 입력
    #### 4.1.1 작업 접수
  ### 4.2 출력
    #### 4.2.1 응답 — 작업 접수 성공
    #### 4.2.2 응답 — 작업 결과 조회
## 5. 제약조건 / 예외처리
## 6. 관련 Feature
## 7. 참고 자료
## 8. 이슈
## 9. Spring 연동 흐름  ← FastAPI 전용 (SCP / apl_id 연계)
## 10. 상태 전이       ← FastAPI 전용 (READY → PROCESS → SUCCESS / FAIL)
```

### 5.4 Streamlit 전용 템플릿 (`상세기획_template_streamlit.md`)

SP04 백오피스 Streamlit 페이지 전용. 공통 §1~§6 + 이슈 포함, Streamlit 특화 섹션 구성:

```markdown
## 3. 입출력 정의
  ### 3.1 화면 구성
    #### 레이아웃 (Streamlit 컴포넌트 명세)
      st.title / st.tabs 구조 명세
      탭별 접근 권한 테이블 (전체 / admin 전용)
      탭별 위젯 명세 테이블 (위젯 | 타입 | 설명)
      admin 전용 탭 RBAC 패턴:
        if current_user.role != "admin":
            st.warning("🔒 시스템 관리자 계정만 접근할 수 있습니다.")
            st.stop()
    #### 항목 상세 (유효성·제약 규칙)
  ### 3.2 저장 출력
    저장 위치 테이블 (.env / DB 구분)
    신규 테이블 스키마 (선택)
```

**탭 설계 원칙** (Streamlit 패턴):
- 조회/현황 탭: 전체 계정 → 앞 배치
- admin 전용 탭: 설정/관리 → 마지막 배치

### 5.5 단계 전환 시 공통 추가 섹션

단계 전환 시 자동 추가됨 (템플릿 종류 무관):
- **설계 단계**: `## A. 설계 상세 (아키텍처/API/DB)`
- **구현 단계**: `## B. 구현 노트 (Task 체크리스트)`
- **검증 단계**: `## C. 검증 결과 (TC 통과 현황)`
- **완료 단계**: `## D. 완료 확인 (검증 통과 확정·서명)`

#### §A 상세설계 섹션 표준 구조

기획→설계 전환 시 다음 구조로 `## A. 설계 상세` 섹션을 작성한다:

```markdown
## A. 설계 상세 (아키텍처/API/DB)

### A.1 구현 코드 구조 및 파일 위치

| 구분 | 폴더/파일 경로 | 역할 | 상태 |
|------|--------------|------|------|
| {레이어명} | {폴더/파일 경로} | {역할 설명} | 신규/수정/통합 |

> **상태**: 신규(새로 생성) / 수정(기존 파일 변경) / 통합(기존 모듈에 병합)

### A.2 아키텍처 / 흐름도

{시퀀스 다이어그램 또는 데이터 흐름 설명}

### A.3 DB 설계 (변경 있을 때만)

| 테이블 | 변경 내용 |
|--------|----------|
| {테이블명} | {컬럼 추가/변경/삭제} |

### A.4 API 설계 (FastAPI/외부 연동 있을 때만)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| {GET/POST} | {/api/v1/...} | {설명} |
```

**A.1 코드 구조 작성 원칙**:
- 레이어별 경로를 명확히 기재 (API 서버 / DB 모델 / 프론트엔드 / Streamlit 등)
- 신규 생성 / 수정 / 기존 모듈 통합 여부를 반드시 명시
- 개발자 인수인계·자동화·문서-코드 싱크의 기준이 되므로 실제 경로 정확히 기재

**프레임워크별 경로 예시**:

| 구분 | 경로 예시 |
|------|----------|
| FastAPI 라우터 | `03_server/api/{기능명}.py` |
| FastAPI DB 모델 | `03_server/db/models/{기능명}.py` |
| Streamlit 페이지 | `04_backoffice/pages/{N_NN_기능명.py}` |
| React 컴포넌트 | `05_frontend/src/pages/{기능명}.jsx` |
| oais 공통 모듈 | `oais/{module}.py` |
