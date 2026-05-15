# oodesign Tutorial — 웹 디자인 적용편

> SP04 웹 페이지에 표준 디자인을 적용·관리하는 oodesign 스킬 사용법 | 버전: v11 | 카테고리: content

## 1. 이 스킬은 왜 필요한가?

SP04 표준웹은 31개 페이지에 일관된 비주얼·UX를 유지해야 한다. 각 페이지마다 색상·여백·카드 스타일을 재작성하면 디자인이 흐트러진다. oodesign은 **표준 디자인 시스템(d42500)**을 SSOT로 두고, 새 페이지를 만들거나 기존 페이지를 마이그레이션할 때 같은 토큰·컴포넌트를 자동 적용한다.

핵심 효과:
- **신규 페이지**: 처음부터 표준 디자인으로 작성 (체크리스트 + 컴포넌트 재사용)
- **기존 페이지**: 점진 마이그레이션 (Bootstrap 기본 → 표준 토큰)
- **디자인 변경**: tokens.css 한 곳만 수정해도 전체 페이지 반영

---

## 2. 빠른 시작 (5분 가이드)

```bash
# 표준 디자인 적용 (가장 자주 쓰는 명령)
oodesign d42500 적용 — stamp/create.html

# 디자인 시스템 상태 확인
oodesign status

# 도움말
oodesign help
```

명령 하나로 Claude가:
1. d42500 SSOT 문서를 자동 참조
2. 대상 페이지 분석 후 변경 계획 제시
3. 승인 후 토큰·컴포넌트 적용
4. 회귀 테스트 + 커밋

---

## 3. 자주 쓰는 명령 요약

> 이것만 기억하면 됩니다.

| # | 명령어 | 언제 쓰나 |
|---|--------|----------|
| 1 | `oodesign d42500 적용 — {페이지}` | **단일 페이지 표준 디자인 마이그레이션** (가장 자주 사용) |
| 2 | `oodesign d42500 패턴으로 새 페이지 — {URL}` | 신규 페이지를 표준 컴포넌트로 작성 |
| 3 | `oodesign status` | 디자인 시스템 자산(토큰·테마·컴포넌트) 현황 |
| 4 | `oodesign token` | JSON 토큰 → CSS 변환 파이프라인 실행 |
| 5 | `oodesign analyze --url {URL}` | 외부 사이트 디자인 분석 → 토큰 제안 |
| 6 | `oodesign check` | 컴포넌트 정합성 감사 (넘버링·구조 불일치 검출) |

---

## 4. 권장 흐름 (이렇게 쓰세요)

### 4.1 신규 페이지 작성 흐름

```
1. d42500 §7 체크리스트 확인          ← 표준 진입점
2. oodesign d42500 패턴으로 새 페이지 — /web/tax/data/coupang
   → routes.py + templates/tax/coupang.html (extra_css/extra_js 분리)
3. 페이지 고유 스타일만 extra_css 블록에
4. 컴포넌트 클래스 사용 (.page-wrap, .step-card, .stats-grid 등)
5. 회귀 테스트 PASS 확인
6. oocommit run                          ← 커밋
```

### 4.2 기존 페이지 마이그레이션 흐름

```
1. oodesign d42500 적용 — {페이지}
   → Claude가 inline :root 제거 + Bootstrap 클래스 → 표준 클래스 치환 계획 제시
2. 사용자 승인
3. 자동 적용 + 회귀 테스트
4. 시각 동등성 확인 (Playwright 또는 수동)
5. oocommit run
```

> 핵심: `d42500` 키워드가 있으면 Claude가 자동으로 SSOT 문서 → §7 체크리스트 → §6 DO/DON'T 순으로 참조.

### 4.3 디자인 토큰 변경 흐름 (글로벌 영향)

```
1. tokens.css 변경 (예: --primary 색상 교체)
2. oodesign check          ← 컴포넌트 정합성 확인
3. card_slip_map 등 reference 페이지 시각 확인
4. 회귀 테스트 (시각 변경만 — 기능 영향 없음 확인)
5. oocommit run
```

---

## 5. 전체 명령어

| 명령어 | 설명 |
|--------|------|
| `oodesign help` | 서브명령어 목록 |
| `oodesign version` | 스킬 버전 (v11) |
| `oodesign status` | 디자인 시스템 상태 (토큰/테마/컴포넌트 현황) |
| `oodesign token [--theme N]` | JSON 토큰 → CSS/SCSS/pen 변환 |
| `oodesign analyze [경로|--url URL]` | 레퍼런스 분석 → 토큰 추출 제안 |
| `oodesign theme [N] [--new|--apply|--list]` | 테마 생성/적용/목록 |
| `oodesign component [이름] [--platform web|flutter]` | 컴포넌트 생성 |
| `oodesign generate [화면명]` | 컴포넌트 조합으로 화면 생성 |
| `oodesign compbuild [컴포넌트|--all]` | 엘리먼트 넘버링 + 라벨링 |
| `oodesign check [--platform web|flutter|all]` | 정합성 감사 |
| `oodesign export [pen파일] [--format png|dart]` | pen → PNG/Dart 변환 |
| `oodesign pencil [--theme N] [--file 경로]` | Pencil 새 파일 생성 |
| `oodesign init [--root 경로]` | 새 프로젝트 디자인 시스템 부트스트랩 |
| `oodesign run` | 전체 프로세스 (analyze → token → component) |
| **`oodesign d42500 적용 — {페이지}`** | **SP04 web 표준 디자인 마이그레이션 (자연어 명령)** |

---

## 6. 상세 사용법

### 6.1 디자인 시스템 자산 위치

| 자산 | 경로 | 역할 |
|------|------|------|
| 토큰 CSS | `04_api_server/web/static/css/tokens.css` | 색상·여백·그림자 CSS 변수 SSOT (--primary, --border 등) |
| 컴포넌트 CSS | `04_api_server/web/static/css/components.css` | 재사용 클래스 (.step-card, .stat-card 등 13종) |
| Jinja 매크로 | `04_api_server/web/templates/_components.html` | `step_card(num, title)`, `stats_grid(...)` |
| **표준 문서 SSOT** | **`00_doc/sp04/d42500_상세설계_web_base_표준디자인시스템.md`** | 토큰 카탈로그·컴포넌트 가이드·체크리스트·DO/DON'T |
| 참조 페이지 | `04_api_server/web/templates/tax/card_slip_map.html` | 표준 디자인 적용 reference |

### 6.2 표준 토큰 카탈로그

```css
:root {
  /* Primary */
  --primary: #265cdc;
  --primary-700: #1e48b0;
  --primary-soft: rgba(38, 92, 220, 0.1);

  /* Text */
  --body: #444;
  --navy: #1a2036;          /* main.css 정의 */

  /* Surface */
  --border: #e6eaf2;
  --surface-alt: #f5f6ff;
  --surface-pale: #f8fafc;

  /* Status */
  --success: #1a7a4a;       --success-soft: #e8f5ef;
  --warn: #b97817;          --warn-soft: #fff4e3;
  --danger: #dc2626;        --danger-soft: #fee2e2;

  /* Shadow */
  --shadow: 0 6px 24px rgba(35, 61, 99, 0.08);
  --shadow-lg: 0 30px 60px rgba(35, 61, 99, 0.12);
}
```

### 6.3 표준 컴포넌트 13종

| 클래스 | 용도 |
|--------|------|
| `.page-wrap` | 페이지 공통 컨테이너 (max-width, padding) |
| `.page-header` + `.sec-num` | 페이지 제목 영역 (라벨 + 제목 + 설명) |
| `.step-card` + `.step-num` + `.step-head/body` | 단계 카드 (`.is-disabled`로 비활성) |
| `.alert-error` | 빨간색 오류 배너 |
| `.spinner-inline` | 로딩 인디케이터 |
| `.btn-primary-cta` | 주요 CTA 버튼 |
| `.btn-action` + `.btn-action.danger` | 보조 버튼 |
| `.stats-grid` + `.stat-card.success/.warn` | 결과 통계 카드 (3개) |
| `.preview-tabs` | 결과 미리보기 탭 |
| `.preview-table` | 미리보기 테이블 (sticky thead, 가로 스크롤) |
| `.btn-download` | 다운로드 버튼 (green) |

### 6.4 옵션

| 옵션 | 설명 |
|------|------|
| `--platform web\|flutter` | 컴포넌트/체크 대상 플랫폼 |
| `--theme {번호}` | 특정 테마 대상 (11=bootstrap_official ~ 15=wello) |
| `--all-themes` | 모든 테마 일괄 처리 |
| `--dry-run` | 미리보기 (실제 수정 안 함, 일부 서브명령) |

---

## 7. 실전 예시

### 7.1 기존 페이지 마이그레이션 (단일)

```bash
사용자: oodesign d42500 적용 — stamp/create.html
```

Claude 동작:
1. `00_doc/sp04/d42500_상세설계_web_base_표준디자인시스템.md` 로드
2. `04_api_server/web/templates/stamp/create.html` 분석
3. 변경 계획 제시:
   - inline `:root` 블록 제거 (tokens.css가 자동 로드)
   - Bootstrap `card` → `.step-card` 치환
   - Bootstrap `btn-primary` → `.btn-primary-cta`
4. 사용자 승인 → 적용
5. `pytest tests/sp04/test_stamp_*.py` 회귀 확인
6. `git commit -m "style(sp04): stamp/create.html 표준 디자인 적용"`

### 7.2 신규 페이지 작성

```bash
사용자: oodesign d42500 패턴으로 새 페이지 — /web/tax/data/coupang, 단계 3개 (업로드/실행/결과)
```

Claude 동작:
1. d42500 §7 체크리스트 따라:
   - `routes.py`에 라우트 5개 추가 (GET 페이지, AJAX 2개, GET download/sample)
   - `templates/tax/coupang.html` 작성:
     - `{% extends "base.html" %}`
     - `extra_css` 블록: 페이지 고유 스타일만
     - `.page-wrap` → `.page-header` → 3개 `.step-card` → `.stats-grid`
     - `extra_js` 블록: fetch + CSRF + 결과 렌더링
2. 테스트 스켈레톤 생성 (TC1~TC8)
3. 회귀 확인 후 커밋

### 7.3 도메인 단위 마이그레이션

```bash
사용자: oodesign d42500 적용 — auth/login·signup·find-id
```

Claude 동작:
1. task-executor 위임 (3개 파일 병렬 분석)
2. 각 페이지별 변경 계획 통합 제시
3. 일괄 적용 + 페이지별 회귀 PASS 확인
4. 단일 커밋: `style(sp04): auth 페이지 3건 표준 디자인 적용`

### 7.4 디자인 토큰 변경 (글로벌)

```bash
사용자: --primary 색상을 #1a73e8로 바꿔줘
```

Claude 동작:
1. `04_api_server/web/static/css/tokens.css` `--primary` 값 수정
2. `oodesign check` — 컴포넌트 정합성 자동 검증
3. card_slip_map 시각 동등성 확인 (Playwright 또는 가이드 안내)
4. 커밋

---

## 8. 입출력

### 입력
| 항목 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| 페이지 경로 | str | ✅ | `stamp/create.html` 형태 또는 URL `/web/tax/data/coupang` |
| 도메인 | str | | 도메인 단위 적용 시 (`auth`, `work` 등) |
| --theme N | int | | 테마 지정 (기본 11_bootstrap_official) |

### 출력
| 출력 | 형식 | 설명 |
|------|------|------|
| 변경 계획 | console | 적용 전 미리보기 (Before/After 요약) |
| 마이그레이션 결과 | 수정된 파일 | routes/templates/css/test 갱신 |
| 회귀 결과 | console | pytest 통과 여부 |
| 커밋 | git | `style(sp04): {페이지} 표준 디자인 적용` |

---

## 9. 자주 묻는 질문 (FAQ)

**Q: `oodesign d42500 적용`과 `d42500 적용` 차이는?**
A: 동일합니다. 둘 다 d42500 SSOT를 자동 참조합니다. `oodesign` 키워드를 붙이면 스킬 트리거가 명확해집니다.

**Q: 기존 인트로/랜딩 페이지에도 적용해도 되나요?**
A: ⚠️ 권장하지 않음. `landing/intro_*`, `landing/home.html`은 hero·gradient 등 독자 디자인을 가집니다. d42500은 일반 콘텐츠 페이지(form·data·dashboard) 대상이며 랜딩 페이지는 별건.

**Q: components.css 클래스와 Bootstrap 클래스를 같이 써도 되나요?**
A: ❌ 금지. d42500 §6 DO/DON'T에 명시. 같은 컴포넌트에 `.card`(Bootstrap)와 `.step-card`(표준)를 혼용하면 스타일 충돌. 한 페이지는 한 시스템만.

**Q: 신규 페이지를 만들 때 매크로(`_components.html`)를 써야 하나요?**
A: 선택 사항. 단계 3개 이상 페이지면 `step_card` 매크로가 가독성 ↑. 단순 페이지면 클래스 직접 사용도 OK.

**Q: 토큰 색상이 변경되면 기존 페이지도 자동 반영되나요?**
A: ✅ 자동. `tokens.css`는 `:root`에 정의되어 모든 페이지가 var(--*)로 참조. 단, inline 색상값(예: `color: #265cdc`)이 남아있다면 수동 마이그레이션 필요.

**Q: `oodesign d42500 적용` 후 회귀 실패하면?**
A: Claude가 자동 롤백하지 않음. 사용자가 `git diff`로 변경 확인 후 부분 수정 또는 `git restore`로 되돌림. 디자인 마이그레이션은 시각 변경이라 기능 회귀가 발생하면 매핑 실수 가능성 큼 — 보고 후 재시도.

**Q: oodesign과 d42500은 무슨 관계?**
A: d42500은 SP04 web 한정 표준 디자인 SSOT. oodesign은 SP07 디자인 통합 스킬(멀티플랫폼·테마). 현재는 양방향 참조로 느슨하게 결합. R159에서 점진적으로 oodesign 파이프라인에 d42500 통합 예정.

> `ootutorial add-faq oodesign "질문" "답변"` 으로 추가 가능

---

## 10. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 페이지 분석 | Explore | haiku | 대상 페이지 + 기존 디자인 패턴 파악 |
| 마이그레이션 | task-executor | sonnet | 다중 파일 일괄 변경 (도메인 단위) |
| 시각 검증 | webapp-testing (Playwright) | sonnet | Before/After 스크린샷 비교 (선택) |
| 정합성 감사 | task-checker | sonnet | components.css 클래스 사용 검증 |

---

## 11. 관련 스킬

| 스킬/문서 | 역할 |
|----------|------|
| `d42500_상세설계_web_base_표준디자인시스템.md` | **SP04 web 표준 디자인 SSOT** — 토큰 카탈로그·체크리스트·DO/DON'T |
| `oocapture` | 페이지 스크린샷 (시각 동등성 비교용) |
| `ooreview` | 코드 리뷰 (디자인 적용 시 패턴 검증) |
| `oocommit` | 마이그레이션 결과 커밋 + 이력 정리 |
| `oodoc` | 디자인 가이드 문서 갱신 |

---

> 생성일: 2026-05-11 | ootutorial v01
