# oodesign 상세 참조

SKILL.md에서 분리된 서브명령어 상세 워크플로우 및 아키텍처 설명.

---

## §2 토큰-테마 아키텍처 상세

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

## §5 폴더 구조 상세

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

---

## §8 elem-box 분리 원칙

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

## §9 compbuild 상세

### elem-box 구조

```html
<div class="elem-box elem-box-wide">
  <div class="elem-id"><span>M101-001</span><span class="elem-name">Basic Tabs</span></div>
  <div class="elem-deps">A101 Button</div>          <!-- M/O/T/P만 -->
  <div class="elem-preview">[렌더링된 컴포넌트]</div>
  <div class="elem-code" onclick="copyCode(this)">[HTML 코드]</div>
</div>
```

### elem-deps 규칙

| 항목 | 규칙 |
|------|------|
| 대상 | M/O/T/P (A는 최소 단위이므로 불필요) |
| 위치 | elem-id 바로 아래 |
| 스타일 | monospace 0.55rem, 회색(#adb5bd), 배경 #f8f9fa |
| 내용 | AMOTP 번호 + 이름 (예: `A101 Button, A201 Badge`) |
| 미분리 | 전용 Atom 없는 요소는 생략 (상단 주석에만 `[input]` 표기) |

### 넘버링 규칙

| 항목 | 규칙 |
|------|------|
| 섹션 간 갭 | 10단위 (001~, 011~, 021~) |
| 섹션 내 | 순차 (001, 002, 003) |
| section-title | `섹션명 (M101-001 ~ 003)` 형식 |

### compbuild 워크플로우

```
oodesign compbuild [컴포넌트|--all] [--platform web|flutter]
    │
    ▼
[1] 대상 파일 읽기 (04_components/{platform}/{file}.html)
    │
    ▼
[2] 엘리먼트 넘버링
    - 각 변형을 elem-box로 분리
    - {AMOTP번호}-{3자리} 번호 부여 (10단위 갭)
    - elem-id: 번호 + 이름 (파란 monospace)
    │
    ▼
[3] 구성요소 식별 (M/O/T/P만)
    - HTML 상단 주석에 구성요소 목록 작성
    - 각 elem-box에 elem-deps 라벨 추가
    │
    ▼
[4] 코드 스니펫
    - elem-code: 핵심 HTML 코드 (클릭 복사)
    │
    ▼
[5] comp-count 자동 업데이트 (JS)
```

---

## §10 Pen 컴포넌트 번호 라벨링

> **핵심 원칙**: 디자인 시스템(`04_components`)이 기준, pen 파일이 따라감. pen에서 새 디자인을 만들 때 디자인 시스템의 기존 컴포넌트를 참조하고, 디자인 시스템을 pen에 맞춰 변경하지 않는다.

스크린샷 → .pen 파일 생성 시, 화면 각 영역에 `04_components` AMOTP 번호를 라벨로 표시하는 가이드.

### 라벨 체계

| 라벨 | 위치 | 색상 | 형식 | 용도 |
|------|------|------|------|------|
| 섹션번호 | 좌상단 | 파란색 (`$brand-primary`) | `S01` ~ `S99` | 화면 영역 구분 |
| 요소번호 | 우상단 | 붉은색 (`$semantic-danger`) | `M104` | 컴포넌트 식별 |

- **요소번호 형식**: 4자리 코드만 표출 (예: `M104`, `O201`, `O210`)
- **M/O 레벨만 표출**: Molecule(M), Organism(O) 컴포넌트만 라벨링. Atom(A)은 라벨 생략
- 동일 컴포넌트 반복 시 name 속성에 `#N` 순번 부여 (예: `O210_senior-card #1`, `O210_senior-card #2`)

### 워크플로우

```
[1] 스크린샷 분석 (Read 이미지)
        │
        ▼
[2] 화면 영역 → AMOTP 컴포넌트 매핑
    - 04_components/01_web/ 파일 목록과 대조
    - M/O 레벨만 매핑 (M104, O201, O210 등)
        │
        ▼
[3] Pen 화면 구축 (batch_design)
    - 각 컴포넌트 영역을 wrapper frame으로 감쌈
    - wrapper에 layout:"none" 적용 (라벨 absolute 배치용)
        │
        ▼
[4] 라벨 삽입
    - 좌상단: 섹션번호 (파란색 텍스트)
    - 우상단: 요소번호 (붉은색 텍스트)
        │
        ▼
[5] vars 연결 (선택)
    - 02_tokens/{테마}/ 토큰 → set_variables → $변수 참조
```

### 라벨 스타일 규격

```javascript
// 섹션번호 (좌상단, 파란색)
sectionLabel=I(wrapperFrame,{
  type:"text", content:"S01", fontSize:10, fontWeight:"700",
  fill:"$brand-primary", layoutPosition:"absolute", x:4, y:2
})

// 요소번호 (우상단, 붉은색, M/O 레벨만)
elementLabel=I(wrapperFrame,{
  type:"text", content:"O210", fontSize:10, fontWeight:"700",
  fill:"$semantic-danger", layoutPosition:"absolute", x:360, y:2
})
```

### wrapper frame 패턴

```javascript
wrap=I(phone,{
  type:"frame",
  name:"M401_carousel - 히어로배너",  // AMOTP번호_이름 (M/O만)
  layout:"none",                       // 라벨 absolute 배치 필수
  width:"fill_container", height:108, fill:"#FFFFFF"
})
```

### 컴포넌트 매핑 기준 (M/O 레벨만)

| 화면 요소 | 매핑 | AMOTP |
|-----------|------|-------|
| 뉴스/콘텐츠 카드 | news-card | O201 |
| 시니어 카드 | senior-card | O210 |
| 기사 상세 | article-detail | O204 |
| 하단 내비게이션 | bottom-nav | M104 |
| 검색바 | search-bar | M201 |
| 탭 | tabs | M101 |
| 폼 | form | M202 |
| 로그인 폼 | login-form | O101 |
| 모달/다이얼로그 | modal | O401 |
| 캐러셀 | carousel | M401 |

### 적용 예시 (시니어월드 홈)

| 섹션 | 섹션번호 | 요소번호 |
|------|---------|---------|
| 헤더 | S01 | - |
| 히어로 배너 | S02 | M401 |
| 빠른 메뉴 | S03 | - |
| 섹션 제목+탭 | S04 | M101 |
| 시니어 카드 1 | S05 | O210 |
| 시니어 카드 2 | S06 | O210 |
| 하단 내비 | S07 | M104 |

---

## §11 export 상세 워크플로우

### PNG 변환

```
[1] pen JSON 읽기 → children 구조 파악
        │
        ▼
[2] pen_to_html.py 실행
    - pen JSON → 임시 HTML 생성
    - 디자인 토큰 ($변수) → 실제 색상값 치환
        │
        ▼
[3] Playwright Python으로 스크린샷
    - viewport: pen 캔버스 크기
    - 출력: {pen파일명}.png
```

### Dart 변환

```
[1] pen JSON 읽기 → frame/children 구조 분석
        │
        ▼
[2] 컴포넌트 매핑
    - frame → Column/Row/Container
    - text → Text widget
    - rectangle → Container/Image
    - icon_font → Icon widget (lucide → flutter_lucide 또는 Icons)
        │
        ▼
[3] Dart 코드 생성
    - StatelessWidget 기반
    - 디자인 토큰 → const Color / TextStyle
    - 출력: {pen파일명}.dart
```

### 구현 방식

| 포맷 | 방식 | 스크립트 |
|------|------|---------|
| PNG | Playwright Python 스크린샷 | `pen_export_png.py` (Claude 직접 생성) |
| Dart | Claude Code 직접 분석·생성 | AI 코드 생성 |

---

## init 상세 워크플로우

```
oodesign init [--root 경로]
    │
    ▼
[1] 루트 경로 결정
    - --root 지정 시: 해당 경로 / 미지정 시: 프로젝트 루트/07_designsystem/
    │
    ▼
[2] 폴더 구조 생성
    {root}/
    ├── 01_references/
    ├── 02_tokens/
    │   └── 11_bootstrap_official/
    │       ├── colors.json      ← templates/colors_template.json 복사
    │       └── typography.json
    ├── 03_vars/                  ← token_sync.py 실행 후 자동 생성
    ├── 04_components/
    │   ├── atoms/ molecules/ organisms/ templates/ pages/
    └── 06_work_pencil/
    │
    ▼
[3] token_sync.py 실행 → 03_vars/11_bootstrap_official/ 생성
    │
    ▼
[4] 완료 리포트 + 다음 단계 안내
```

**이식 시 복사 대상**:

```
.claude/skills/oodesign/
├── SKILL.md
├── scripts/token_sync.py
├── scripts/audit_script.py     ← 선택
├── templates/
│   ├── colors_template.json
│   └── component_template.html
└── references/
```

---

## pencil 상세 워크플로우

```
oodesign pencil [--theme 테마명] [--file 경로]
    │
    ▼
[1] Pencil MCP 상태 확인 (get_editor_state)
    │
    ▼
[2] 문서 열기/생성
    - --file 지정 시: open_document(경로)
    - 미지정 시: open_document('new')
    │
    ▼
[3] 토큰 JSON 읽기
    - 02_tokens/{NN}_{테마}/colors.json → 색상 토큰
    - 02_tokens/{NN}_{테마}/typography.json → 타이포 토큰 (있으면)
    │
    ▼
[4] set_variables() 호출 — 토큰 → Pencil 변수 자동 매핑
    brand-primary / brand-secondary / semantic-* / neutral-* / surface-*
    │
    ▼
[5] 완료 — $brand-primary 등 바로 사용 가능
```

**테마 매핑**:

| --theme 값 | 토큰 경로 |
|------------|----------|
| bootstrap_official | `02_tokens/11_bootstrap_official/` |
| chuckchuck | `02_tokens/12_chuckchuck/` |
| galaxy_oneui | `02_tokens/13_galaxy_oneui/` |
| senior_world (기본) | `02_tokens/14_senior_world/` |
| wello | `02_tokens/15_wello/` |

---

## vars 연결 가이드

```
[1] get_variables() → 현재 vars 확인 (비어 있으면 등록 필요)
        │
        ▼
[2] 02_tokens/{테마}/colors.json 읽기 → 색상 토큰 확인
        │
        ▼
[3] set_variables() → 토큰 기반 변수 등록
    - brand-primary, neutral-gray-*, semantic-*, nav-* 등
        │
        ▼
[4] batch_design U() → 하드코딩 색상을 $변수 참조로 교체
    - fill:"#1A73E8" → fill:"$brand-primary"
```

**주의**: `fontFamily`는 변수 참조 미지원 → 직접 문자열 사용 (예: `fontFamily:"Pretendard"`)
