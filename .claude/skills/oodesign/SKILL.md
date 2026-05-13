---
name: oodesign
description: "디자인 통합 스킬 'oodesign', '디자인 시스템', '토큰 생성', '컴포넌트 생성', '테마 생성', '레퍼런스 분석', 'URL 레퍼런스', 'AI 디자인', '디자인투코드', 'd42500', 'd42500 적용', 'SP04 web 표준 디자인' 등 모든 디자인 작업을 요청할 때 사용한다. SP04 web 페이지에 표준 디자인을 적용하려면 d42500 SSOT 문서를 참조한다."
metadata:
  version: "v11"
  category: "content"
---

# oodesign - 디자인 통합 스킬

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 디자인 시스템 통합 스킬 — 토큰·컴포넌트·테마 생성 및 AI 디자인·코드 변환 |
| **하는 것** | 디자인 토큰 생성, 컴포넌트 파일 생성, 테마 관리, URL 레퍼런스 분석, 디자인→코드 변환 |
| **하지 않는 것** | 앱 코드 구현(→oodev), 문서 작성(→oodoc), 스크린샷 캡처(→oocapture) |
| **참조 범위** | 현재 프로젝트 내부 파일 + 지정 URL 레퍼런스 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `07_designsystem/` 하위 파일 (03_vars/, 04_components/, 05_themes/ 등) |
| **실행 레벨** | [반자동] — 생성 계획 확인 후 실행 |
| **에이전트 호환** | 범용 — URL 레퍼런스 분석 시 웹 접근 필요 |

## 문서 이력 관리
- v09 2026-04-05 — 04_components 플랫 구조 전환: 01_web/02_flutter 서브폴더 제거, atoms/molecules 등 직접 배치
- v11 2026-04-05 — init 서브명령어 + 템플릿(colors_template.json, component_template.html) 추가: 다른 프로젝트 이식 가능
- v10 2026-04-05 — pencil 서브명령어 추가: 새 pen 파일 생성 시 테마 변수 자동 등록
- v09 2026-04-05 — 03_vars 단순화: 00_shared/01_web/02_flutter/10_themes 삭제, 테마 폴더(11~15)만 유지
- v08 2026-04-05 — export 서브명령어 추가: pen → PNG/Dart 변환 (섹션 11)

> 공통 가이드라인: `.claude/guides/common_guide.md` 참조
> 디자인 원칙: `00_doc/sp07/d70300_디자인원칙.md`
> 방법론 참조: `00_doc/sp07/d70200~d70240`
> **SP04 web 표준 디자인 SSOT**: `00_doc/sp04/d42500_상세설계_web_base_표준디자인시스템.md` — `tokens.css`·`components.css`·`_components.html` 매크로·신규 페이지 체크리스트 + DO/DON'T 가이드. SP04 web 페이지 마이그레이션 시 이 문서를 참조한다.
> 명령 패턴 예: `oodesign d42500 적용 — stamp/create.html` → d42500 §7 체크리스트 따라 마이그레이션 수행 + 회귀 검증

---

## 1. 개요

모든 디자인 작업을 담당하는 통합 스킬.

- **디자인 시스템**: 토큰 정의/변환, 컴포넌트 구축, 테마 관리
- **크로스플랫폼**: 웹(Bootstrap) + 앱(Flutter) 공유 토큰 아키텍처
- **실제 디자인**: 레퍼런스 분석, AI 보조 생성(Pencil MCP 채택), 디자인→코드 변환

프로세스 전체 흐름: `d70002_plan.md` 참조

---

## 2. 토큰-테마 아키텍처

> 상세: `.claude/skills/oodesign/references/design-detail.md` §2 참조

- `02_tokens/`: 공유(00_shared), 웹(01_web), 테마 오버라이드(11~15)
- `03_vars/`: 테마별 산출물 (CSS/SCSS/pen) — 11_bootstrap_official ~ 15_wello
- 플랫폼별 포맷 추가 시 테마 폴더 하위에 `dart/` 등으로 추가

---

## 3. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oodesign help` | 서브명령어 목록 표시 |
| `oodesign version` | 스킬 버전 정보 (v11) |
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

> 코드 예시: references/guide.md 참조

### analyze 워크플로우

> 코드 예시: references/guide.md 참조

---

## 4. 디자인 프로세스 매핑

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

## 5. 폴더 구조 (v2.0 넘버링)

> AMOTP 넘버링·플랫폼 접미사·00_index.html 규칙 상세: `.claude/skills/oodesign/references/design-detail.md` §5 참조

| 경로 | 용도 |
|------|------|
| `07_designsystem/01_references/` | 레퍼런스 이미지/템플릿 |
| `07_designsystem/02_tokens/00_shared/` | 공유 토큰 (색상, 간격) |
| `07_designsystem/02_tokens/01_web/` | 웹 전용 토큰 (타이포, 레이아웃) |
| `07_designsystem/02_tokens/11_~15_{테마}/` | 테마 오버라이드 |
| `07_designsystem/03_vars/11_~15_{테마}/` | 테마별 산출물 (CSS/SCSS/pen) |
| `07_designsystem/04_components/{atoms\|molecules\|organisms\|templates\|pages}/` | 컴포넌트 (플랫 구조) |
| `07_designsystem/06_pencil/` | Pencil MCP 프로토타입 (.pen) |
| `.claude/skills/oodesign/scripts/token_sync.py` | 토큰 변환 스크립트 v2.0 |

**핵심 규칙**: 색상은 `var(--ds-xxx)` CSS 변수 참조 / T·P 계층은 플랫폼 접미사 필수(bw/fm 등) / 각 폴더에 `00_index.html` 필수

### 테마 현황

| 테마 | 토큰 | CSS/SCSS | 데모 |
|------|:---:|:---:|:---:|
| bootstrap_official | ✅ | ✅ | 테마 스위처 |
| chuckchuck | ✅ | ✅ | 테마 스위처 |
| galaxy_oneui | ✅ | ✅ | 테마 스위처 |
| senior_world | ✅ | ✅ | 테마 스위처 |
| wello | ✅ | ✅ | 테마 스위처 |

---

## 6. AI 도구 연동

| 도구 | 상태 | 특징 |
|------|------|------|
| Pencil Dev MCP | **채택** | 로컬 .pen 파일 기반, 23/25점 |
| Figma MCP | 미채택 | 14/25점 (Phase 3 비교 결과) |
| Claude Code | 보조 | 직접 HTML/CSS 생성 |

> 도구 비교 결과: `00_doc/sp07/d70300_ai_comparison.md`

### 6.1 Pencil MCP 사전 체크 (필수)

> **⚠️ Pencil 작업을 요청받으면 반드시 먼저 MCP 상태를 확인한 뒤 진행한다.**

> 코드 예시: references/guide.md §4 참조

---

## 7. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | Explore | haiku | 레퍼런스 이미지 구조 파악 | - |
| 생성 | oh-my-claudecode:designer | sonnet | 컴포넌트/화면 디자인 | - |
| 검증 | oh-my-claudecode:verifier | sonnet | 디자인 원칙 준수 확인 | - |

---

## 8. elem-box 분리 원칙

> 상세 규칙: `.claude/skills/oodesign/references/design-detail.md` §8 참조

- **분리 O**: 독립 CSS 클래스 조합, 상태/색상 variant, 밑줄/아이콘 위치 변형
- **유지 O**: 복합 패턴, 그룹/목록, 레이아웃 컨텍스트 필요, 상태 기반 컴포넌트
- 분리 후 순차 재번호 / 섹션 제목 `섹션명 (A{xxx}-시작 ~ 끝)` / `comp-count` 업데이트 필수

---

## 9. compbuild — 컴포넌트 엘리먼트 빌드

> elem-box 구조·elem-deps 규칙·넘버링 상세: `.claude/skills/oodesign/references/design-detail.md` §9 참조

> 코드 예시: references/guide.md 참조

옵션: `--all` (전체), `--platform web|flutter` (기본: web), `--dry-run` (목록만)

---

## 10. Pen 컴포넌트 번호 라벨링

> 라벨 스타일 규격·wrapper 패턴·컴포넌트 매핑 테이블 상세: `.claude/skills/oodesign/references/design-detail.md` §10 참조

**핵심 원칙**: `04_components`가 기준, pen이 따라감. pen 요소가 기존 컴포넌트와 다를 경우 디자인 시스템에 먼저 추가 후 pen에서 참조.

| 라벨 | 위치 | 색상 | 형식 |
|------|------|------|------|
| 섹션번호 | 좌상단 | `$brand-primary` (파란색) | `S01`~`S99` |
| 요소번호 | 우상단 | `$semantic-danger` (붉은색) | `M104` (M/O만) |

Atom(A) 레벨은 라벨 생략 — M/O 단위만 표출.

---

## 11. export — pen 파일 변환

> PNG/Dart 변환 상세 워크플로우: `.claude/skills/oodesign/references/design-detail.md` §11 참조

```
oodesign export [pen파일경로] [--format png|dart|both] [--output 경로]
```

| 포맷 | 방식 |
|------|------|
| PNG | pen JSON → 임시 HTML → Playwright 스크린샷 |
| Dart | pen JSON 분석 → StatelessWidget 코드 생성 |

---

### init — 새 프로젝트 초기화

> 상세 워크플로우·이식 복사 대상: `.claude/skills/oodesign/references/design-detail.md` init 섹션 참조

다른 프로젝트에 `oodesign` 스킬 폴더 복사 후 실행 → 폴더 구조 + bootstrap_official 토큰 자동 생성.

> 코드 예시: references/guide.md 참조

---

### pencil — 테마 변수 자동 등록

> 토큰 매핑 상세·테마 매핑 테이블: `.claude/skills/oodesign/references/design-detail.md` pencil 섹션 참조

새 `.pen` 파일 생성 시 `02_tokens/`에서 토큰을 읽어 Pencil 변수로 자동 등록.

> 코드 예시: references/guide.md 참조

---

### vars 연결 가이드

> 상세: `.claude/skills/oodesign/references/design-detail.md` vars 섹션 참조

> 코드 예시: references/guide.md 참조

**주의**: `fontFamily`는 변수 참조 미지원 → 직접 문자열 사용

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

