# oodesign Tutorial

> 디자인 시스템 통합 스킬 — 토큰·컴포넌트·테마 생성 및 AI 디자인·코드 변환 | 버전: v03 | 카테고리: content

## 1. 이 스킬은 왜 필요한가?

웹(Bootstrap) + 모바일 앱(Flutter) 공유 토큰 아키텍처로 디자인 시스템을 통합 관리할 수 있습니다. Pencil MCP 기반 AI 디자인 생성, URL 레퍼런스 분석, 자동 코드 변환이 가능합니다.

**이런 상황에서 사용합니다:**
- **디자인 시스템**: 토큰 정의/변환, 컴포넌트 구축, 테마 관리
- **크로스플랫폼**: 웹(Bootstrap) + 앱(Flutter) 공유 토큰 아키텍처
- **실제 디자인**: 레퍼런스 분석, AI 보조 생성(Pencil MCP 채택), 디자인→코드 변환

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oodesign run

# 상태 확인
oodesign status

# 도움말
oodesign help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oodesign help` | 서브명령어 목록 표시 |
| `oodesign version` | 스킬 버전 정보 (v03) |
| `oodesign status` | 현재 디자인 시스템 상태 (토큰/테마/컴포넌트 현황) |
| `oodesign token [--theme 테마명\|--all-themes]` | 토큰 파이프라인 실행 (JSON → CSS/SCSS/pen) |
| `oodesign analyze [이미지경로\|--url URL] [--sample 샘플명]` | 레퍼런스 분석 → 토큰 추출 제안 (이미지 또는 URL) |
| `oodesign theme [테마명] [--new\|--apply\|--list]` | 테마 생성/적용/목록 |
| `oodesign component [컴포넌트명] [--platform web\|flutter] [--tool pencil\|code]` | 컴포넌트 생성 |
| `oodesign generate [화면명] [--theme 테마명]` | 컴포넌트 조합으로 화면 생성 |
| `oodesign compbuild [컴포넌트\|--all] [--platform web\|flutter]` | 컴포넌트 엘리먼트 넘버링 + 구성요소 라벨링 |
| `oodesign check [--platform web\|flutter\|senior_world\|all]` | 컴포넌트 정합성 감사 (넘버링·구조·인덱스 불일치 검출) |
| `oodesign export [pen파일] [--format png\|dart\|both] [--output 경로]` | pen 파일 → PNG 이미지 / Dart 코드 변환 |
| `oodesign pencil [--theme 테마명] [--file 경로]` | Pencil 새 파일 생성 + 테마 변수 자동 등록 |
| `oodesign init [--root 경로]` | 새 프로젝트에 디자인 시스템 폴더 구조 + 빈 템플릿 생성 |
| `oodesign run [--theme 테마명]` | 전체 프로세스 실행 (analyze → token → component) |

실행:
- token: `uv run python .claude/skills/oodesign/scripts/token_sync.py [--theme 테마명|--all-themes]`
- check: `uv run python .claude/skills/oodesign/scripts/audit_script.py [--platform web|flutter|senior_world|all]`
- 나머지: Claude Code 직접 수행 (AI 분석/생성)

### check 워크플로우

```
oodesign check [--platform web|flutter|senior_world|all]
        │
        ▼
[1] audit_script.py 실행 (대상 플랫폼 폴더)
        │
        ▼
[2] section-title 넘버링 범위 표기 누락 검출
        │
        ▼
[3] elem-box 구조 무결성 검사 (elem-id / elem-preview / elem-code)
        │
        ▼
[4] 00_index.html ↔ 실제 파일 불일치 검출
    - 사이드바 링크 ↔ 카드 목록 불일치
    - 사이드바 ↔ 디스크 파일 불일치
        │
        ▼
[5] 이슈 목록 출력 (없으면 NO ISSUES FOUND)
```

### analyze 워크플로우

```
oodesign analyze [이미지경로|--url URL] [--sample 샘플명]
        │
        ▼
[1] 소스 수집 (이미지 Read 또는 WebFetch)
        │
        ▼
[2] 색상/타이포/간격/레이아웃 추출
        │
        ▼
[3] 토큰 JSON 초안 생성
    - 02_tokens/{NN}_{샘플명}/ 에 저장
        │
        ▼
[4] token_sync.py --theme {샘플명} 실행
        │
        ▼
[5] 분석 결과 리포트 출력
```

---

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 디자인 시스템 통합 스킬 — 토큰·컴포넌트·테마 생성 및 AI 디자인·코드 변환 |
| **하는 것** | 디자인 토큰 생성, 컴포넌트 파일 생성, 테마 관리, URL 레퍼런스 분석, 디자인→코드 변환 |
| **하지 않는 것** | 앱 코드 구현(→oodev), 문서 작성(→oodoc), 스크린샷 캡처(→oocapture) |
| **참조 범위** | 현재 프로젝트 내부 파일 + 지정 URL 레퍼런스 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `07_designsystem/` 하위 파일 (03_vars/, 04_components/, 05_themes/ 등) |
| **실행 레벨** | [반자동] — 생성 계획 확인 후 실행 |
| **에이전트 호환** | 범용 — URL 레퍼런스 분석 시 웹 접근 필요 |

### 토큰-테마 아키텍처

> **원칙**: 브랜드 정체성은 테마 단위로 관리, 플랫폼 구분은 산출물 포맷으로 분리

```
02_tokens/                     원본 토큰 (JSON)
├── 00_shared/                 색상, 간격(px), 라운딩 → 공유
├── 01_web/                    타이포(rem), 레이아웃, 그림자 → 웹 전용
├── 11~15_{테마}/              테마 오버라이드

03_vars/                       산출물 (CSS/SCSS/pen)
├── 11_bootstrap_official/     기본 Bootstrap 테마
├── 12_chuckchuck/             척척 테마
├── 13_galaxy_oneui/           Galaxy One UI 테마
├── 14_senior_world/           시니어월드 테마
└── 15_wello/                  웰로 테마
```

| 번호 | 용도 |
|------|------|
| 11~15 | 테마별 산출물 (CSS/SCSS/pen) |

> 플랫폼별 포맷(Dart 등)이 필요하면 테마 폴더 하위에 `dart/` 등으로 추가

---

### 디자인 프로세스 매핑

| 단계 | 명령어 | 방법론 참조 |
|------|--------|------------|
| STEP 1 레퍼런스 분석 | `oodesign analyze` | d70210_방법론_AI디자인.md |
| STEP 2 토큰 정의/변환 | `oodesign token` | d70200_방법론_토큰파이프라인.md |
| STEP 3 컴포넌트 생성 | `oodesign component` | d70210_방법론_AI디자인.md |
| STEP 4 라이브러리 편입 | `oodesign component --save` | d70220_아토믹디자인.md |
| STEP 5 테마 패키징 | `oodesign theme --new` | d70230_방법론_테마시스템.md |
| STEP 5.5 테마 컴포넌트 생성 | `oodesign theme --apply` | 05_components_theme/ |
| STEP 6 화면 생성 | `oodesign generate` | d70240_방법론_디자인투코드.md |

### 테마 적용 방식

`04_components/00_index.html`의 **테마 스위처**(dropdown)가 iframe 내 CSS `<link>`를 동적으로 교체하여 테마 적용.
별도의 `05_components_theme/` 폴더 복사 불필요.

---

### 폴더 구조 (v2.0 넘버링)

| 경로 | 용도 |
|------|------|
| `07_designsystem/01_references/` | 레퍼런스 이미지/템플릿 |
| `07_designsystem/02_tokens/00_shared/` | 공유 토큰 (색상, 간격) |
| `07_designsystem/02_tokens/01_web/` | 웹 전용 토큰 (타이포, 레이아웃) |
| `07_designsystem/02_tokens/11_~15_{테마}/` | 테마 오버라이드 |
| `07_designsystem/03_vars/11_~15_{테마}/` | 테마별 산출물 (CSS/SCSS/pen) |
| `07_designsystem/04_components/atoms/` | Atom 컴포넌트 (Bootstrap + Flutter 통합) |
| `07_designsystem/04_components/molecules/` | Molecule 컴포넌트 |
| `07_designsystem/04_components/organisms/` | Organism 컴포넌트 |
| `07_designsystem/04_components/templates/` | Template (T/P — 플랫폼 접미사 bw/fm) |
| `07_designsystem/04_components/pages/` | Page (T/P — 플랫폼 접미사 bw/fm) |
| `07_designsystem/05_components_theme/` | (미사용 — 테마 스위처로 대체) |
| `07_designsystem/06_pencil/` | Pencil MCP 프로토타입 (.pen) |
| `.claude/skills/oodesign/scripts/token_sync.py` | 토큰 변환 스크립트 v2.0 |

### 컴포넌트 규칙

- **테마 독립**: 색상은 CSS 변수(`var(--ds-xxx, fallback)`)로 참조
- **플랫 구조**: `04_components/{atoms|molecules|organisms|templates|pages}/` — 플랫폼 구분 없이 통합
- **T/P 접미사**: Template/Page는 파일명에 플랫폼 접미사 부여 (e.g. `T101bw_`, `P101fm_`)
- **AMOTP 넘버링**: `{단계}{그룹}{순번}_{컴포넌트명}.html`
- **`00_index.html` 필수**: 04_components 및 05_components_theme 하위 모든 폴더에 카탈로그 인덱스 필수

### AMOTP 넘버링 체계

#### 요소번호 형식

| 계층 | 파일명 | 요소번호 | 비고 |
|------|--------|---------|------|
| A (Atom) | `A501_card.html` | `A501-001` | 접미사 없음 |
| M (Molecule) | `M401_carousel.html` | `M401-001` | 접미사 없음 |
| O (Organism) | `O201_news-card.html` | `O201-001` | 접미사 없음 |
| T (Template) | `T101_tpl-auth.html` | `T101-001bw` | **접미사 필수** |
| P (Page) | `P101_page-login.html` | `P101-001fm` | **접미사 필수** |

#### 플랫폼 공유 원칙

| 계층 | 번호 공유 | 이유 |
|------|---------|------|
| A/M/O | 플랫폼 간 공유 | 컴포넌트 개념 동일, 구현만 다름 |
| T/P | 플랫폼별 독립 | 레이아웃·구성이 근본적으로 다름 |

#### T/P 플랫폼 접미사 (2자리)

요소번호 맨 뒤에 프레임워크 + 타겟 접미사 부여:

| 접미사 | 프레임워크 + 타겟 | 예시 |
|:------:|-----------------|------|
| **bw** | Bootstrap + Web | `P101-001bw` |
| **rw** | React + Web | `P101-001rw` |
| **fw** | Flutter + Web | `P101-001fw` |
| **fm** | Flutter + Mobile | `P101-001fm` |
| **fd** | Flutter + Desktop | `P101-001fd` |
| **rn** | React Native | `P101-001rn` |
| **si** | Swift + iOS | `P101-001si` |
| **ka** | Kotlin + Android | `P101-001ka` |

#### 현재 프로젝트 매핑

| 폴더 | 해당 파일 |
|------|----------|
| `04_components/atoms/` ~ `organisms/` | A/M/O — 접미사 없음 |
| `04_components/templates/` | `T{NNN}bw_*.html`, `T{NNN}fm_*.html` |
| `04_components/pages/` | `P{NNN}bw_*.html`, `P{NNN}fm_*.html` |

### 00_index.html 필수 규칙

컴포넌트 **생성/삭제/리네이밍** 시 해당 폴더의 `00_index.html`을 반드시 업데이트:

| 폴더 | 00_index.html | 업데이트 시점 |
|------|:-------------:|-------------|
| `04_components/` | 필수 | 컴포넌트 추가/삭제 시 |
| `05_components_theme/{NN}_{테마}/` | 필수 | 테마 컴포넌트 생성 시 |

**포함 내용**:
1. AMOTP 그룹별 사이드바 네비게이션
2. 각 항목에 AMOTP 코드 표시 (모노스페이스)
3. 컴포넌트 총 수 + 그룹 수 통계
4. iframe 미리보기 기능
5. 다른 카탈로그 링크 (컴포넌트↔테마 상호 참조)
- **인덱스**: 각 플랫폼 폴더에 `00_index.html`로 전체 컴포넌트 브라우징

### 테마 현황

| 테마 | 토큰 | CSS/SCSS | 데모 |
|------|:---:|:---:|:---:|
| bootstrap_official | ✅ | ✅ | 테마 스위처 |
| chuckchuck | ✅ | ✅ | 테마 스위처 |
| galaxy_oneui | ✅ | ✅ | 테마 스위처 |
| senior_world | ✅ | ✅ | 테마 스위처 |
| wello | ✅ | ✅ | 테마 스위처 |

---

### ai 도구 연동

| 도구 | 상태 | 특징 |
|------|------|------|
| Pencil Dev MCP | **채택** | 로컬 .pen 파일 기반, 23/25점 |
| Figma MCP | 미채택 | 14/25점 (Phase 3 비교 결과) |
| Claude Code | 보조 | 직접 HTML/CSS 생성 |

> 도구 비교 결과: `00_doc/sp07/d70300_ai_comparison.md`

### 6.1 Pencil MCP 사전 체크 (필수)

> **⚠️ Pencil 작업을 요청받으면 반드시 먼저 MCP 상태를 확인한 뒤 진행한다.**

#### 체크 절차

```
[1] get_editor_state 호출
        │
        ├─ 성공 + activeFile 존재 → 정상, 바로 작업 진행
        │
        ├─ 성공 + activeFile 없음 → open_document('new') 또는 기존 .pen 경로로 열기
        │
        └─ 오류 / MCP 응답 없음  → 사용자에게 알리고 중단
                                   (Pencil Dev 앱 실행 여부 확인 요청)
```

#### 확인 항목

| 확인 항목 | 방법 | 정상 조건 |
|----------|------|----------|
| MCP 연결 | `get_editor_state()` 호출 | 오류 없이 응답 반환 |
| 활성 문서 | 응답의 `activeFile` 필드 | 경로가 존재하고 `.pen` 파일 |
| 가이드라인 로드 | `get_guidelines()` 호출 | 스타일/레이아웃 가이드 반환 |

#### 코드 패턴

```
# Pencil 작업 시작 전 항상 실행
state = mcp__pencil__get_editor_state()

if state.activeFile:
    # 정상 → 작업 진행
    guidelines = mcp__pencil__get_guidelines()
else:
    # 문서 없음 → 열기
    mcp__pencil__open_document('new')  # 또는 기존 경로
```

#### 오류 대응

| 상황 | 원인 | 대응 |
|------|------|------|
| MCP 도구 자체가 없음 | Pencil Dev 앱 미실행 | 사용자에게 Pencil Dev 앱 실행 요청 |
| `activeFile` 없음 | 열린 문서 없음 | `open_document('new')` 또는 경로 지정 |
| 응답 지연/타임아웃 | 앱 응답 불가 | Pencil Dev 재시작 요청 |

---

### elem-box 분리 원칙

컴포넌트 카탈로그에서 elem-box를 분리할지 유지할지 판단하는 기준.

### 분리 O (Split)

| 조건 | 예시 |
|------|------|
| 독립적으로 사용 가능한 다른 CSS 클래스 조합 | `.oo-link-icon` vs `.oo-link-icon.oo-link-danger` |
| 상태/색상 변형 (variant) | Primary / Success / Danger / Secondary |
| 밑줄 방식 변형 | 항상 밑줄 / 호버 밑줄 / 연한 밑줄 |
| 아이콘 위치 변형 | 아이콘 앞 / 아이콘 뒤 |

### 유지 O (Keep Together)

| 조건 | 예시 |
|------|------|
| 복합 패턴 (여러 요소 조합 표현) | Disabled — `<span>` + `<a>` 두 가지 표현 |
| 그룹/목록 패턴 | 리스트 아이템 그룹, 버튼 그룹 |
| 레이아웃 컨텍스트 필요 | 인라인 텍스트 속 링크 예시 |
| 구조적으로 분리 불가한 UI | 탭/아코디언 등 상태 기반 컴포넌트 |

### 번호 부여 규칙

- 분리 후 빈 번호 없이 순차 재번호 부여
- 섹션 제목: `섹션명 (A{xxx}-{시작} ~ {끝})` 형식
- `comp-count` 총 수 업데이트 필수
- 이후 섹션 번호도 연쇄 업데이트

---

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oodesign run
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/oodesign/scripts/token_sync.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | Explore | haiku | 레퍼런스 이미지 구조 파악 | - |
| 생성 | oh-my-claudecode:designer | sonnet | 컴포넌트/화면 디자인 | - |
| 검증 | oh-my-claudecode:verifier | sonnet | 디자인 원칙 준수 확인 | - |

---

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-14 11:32 | ootutorial v03
