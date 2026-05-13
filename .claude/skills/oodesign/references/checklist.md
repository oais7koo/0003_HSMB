# oodesign check 체크리스트

> oodesign 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oodesign_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 컴포넌트 디렉터리 | 04_components/ 구조 존재 여부 | WARNING |
| C04 | 토큰 파이프라인 | token_sync.py 스크립트 존재 여부 | WARNING |
| C05 | 인덱스 파일 | 04_components/01_web/00_index.html 존재 여부 | WARNING |

---

## 역할 수행 체크리스트

## 컴포넌트 작업 시

- [ ] elem-box 분리 원칙 적용 (섹션 8: 독립 CSS 클래스 조합 → 분리)
- [ ] elem-id 넘버링 순차 부여 + 섹션 제목 범위 표기 `섹션명 (A{xxx}-{시작} ~ {끝})`
- [ ] comp-count JS 업데이트
- [ ] `00_index.html` 해당 폴더 업데이트 (추가/삭제/리네이밍 시)

## Pencil MCP 작업 시

- [ ] `get_editor_state()` 호출 → activeFile 확인
- [ ] MCP 응답 없으면 작업 중단 + 사용자 알림 (Pencil Dev 앱 실행 여부 확인 요청)
- [ ] `get_guidelines()` 로드 확인

## 토큰 파이프라인 시

- [ ] `token_sync.py` 실행 (`--theme 테마명` 또는 `--all-themes`)
- [ ] CSS/SCSS 산출물 확인 (`03_vars/{NN}_{테마}/`)

## 테마 생성 시 (STEP 5.5)

- [ ] `05_components_theme/{NN}_{테마}/` 폴더 생성
- [ ] `04_components/01_web/` 전체 컴포넌트 복사
- [ ] CSS 변수 경로 교체 (`bootstrap_official` → 해당 테마)
- [ ] `00_index.html` 생성/업데이트

## compbuild 작업 시

### 사전 확인
- [ ] 대상 파일 AMOTP 번호 확인 (파일명에서)
- [ ] `--dry-run`으로 대상 목록 먼저 확인
- [ ] 플랫폼 지정 (`--platform web|flutter`)

### elem-box 분리 판단
- [ ] 독립 CSS 클래스 조합인가? → 분리
- [ ] 상태/색상 변형(variant)인가? → 분리
- [ ] 아이콘 위치 변형인가? → 분리
- [ ] 복합 패턴(여러 요소 조합)인가? → 유지
- [ ] 그룹/목록 패턴인가? → 유지
- [ ] 레이아웃 컨텍스트 필요한가? → 유지

### 엘리먼트 넘버링
- [ ] 섹션 간 갭 10단위 적용 (001~, 011~, 021~)
- [ ] 섹션 내 순차 번호 (001, 002, 003)
- [ ] 섹션 제목 범위 표기 `섹션명 (A{xxx}-{시작} ~ {끝})`
- [ ] elem-id: 번호 + 이름 (파란 monospace)
- [ ] 삭제된 번호 재사용 금지

### 구성요소 라벨링 (M/O/T/P만)
- [ ] Atom 파일은 elem-deps 생략
- [ ] M/O/T/P: `elem-deps` 위치는 elem-id 바로 아래
- [ ] elem-deps 스타일: monospace 0.55rem, 회색 #adb5bd, 배경 #f8f9fa
- [ ] 형식: `A101 Button, A201 Badge`
- [ ] 전용 Atom 없는 요소: 생략 후 상단 주석에 `[input]` 표기

### elem-box 구조 검증
- [ ] `elem-box` / `elem-box-wide` 클래스 적용
- [ ] `elem-preview` (렌더링 영역) 존재
- [ ] `elem-code` (클릭 복사 코드) 존재
- [ ] `onclick="copyCode(this)"` 함수 연결

### 완료 후
- [ ] `comp-count` JS 총 수 업데이트
- [ ] `00_index.html` 해당 폴더 업데이트
- [ ] `d74020_넘버링.md` 매핑 테이블 업데이트
- [ ] `d74000_컴포넌트_개요.md` 플랫폼 현황 수치 업데이트

## 문서 정합성 확인

- [ ] 디자인 원칙: `00_doc/sp07/d70300_디자인원칙.md`
- [ ] 넘버링: `00_doc/sp07/d74020_넘버링.md`
- [ ] 웹 가이드라인: `00_doc/sp07/d74030_웹_가이드라인.md`
- [ ] 컴포넌트 개요: `00_doc/sp07/d74000_컴포넌트_개요.md` (플랫폼 현황 수치 업데이트)
