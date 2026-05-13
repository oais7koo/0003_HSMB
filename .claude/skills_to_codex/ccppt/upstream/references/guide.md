# ooppt_guide - PPT 생성 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/ooppt/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

ooppt는 마크다운/텍스트 소스에서 전문적인 PPTX 프레젠테이션을 자동 생성하는 스킬입니다.

### 1.1 핵심 특징

- **소스 기반 생성**: MD/TXT/JSON → PPTX
- **디자인 자동화**: 다크/라이트 테마, 카드 레이아웃
- **환각 방지**: 소스 내용만 사용, 원문 유지, 출처 표기
- **병렬 처리**: 슬라이드 10개 이상 시 `run_in_background=true`

---

## 2. 워크플로우

### 2.1 전체 흐름

```
Explore (소스 수집)
    ↓
ooppt-agent (스크립트 생성)
    ↓
task-executor (PPTX 생성)
    ↓
task-checker (검증)
```

### 2.2 서브에이전트 활용

| 단계 | 에이전트 | 역할 |
|------|---------|------|
| 소스 수집 | `Explore` | 문서 탐색 및 콘텐츠 추출 |
| 스크립트 생성 | `ooppt-agent` | PPTX 생성 스크립트 작성 |
| PPTX 생성 | `task-executor` | 스크립트 실행 |
| 검증 | `task-checker` | 품질 확인 |

---

## 3. 상세 사용법

### 3.1 명령어

| 명령어 | 설명 |
|--------|------|
| `ooppt status` | 서브명령어 리스트, 상태 요약 |
| `ooppt version` | 스킬 버전 정보 (v3.3) |
| `ooppt run [경로]` | PPTX 생성 |
| `ooppt preview` | 미리보기 |

### 3.2 출력 규칙

| 항목 | 규칙 |
|------|------|
| **출력 위치 (입력 파일 있음)** | 입력 파일과 동일한 디렉토리 |
| **출력 위치 (입력 파일 없음)** | `00_doc/` 폴더 |
| **파일명** | `{주제}_프레젠테이션.pptx` |

**예시**:
- 입력: `00_doc/sp00/d0001_prd.md` → 출력: `00_doc/sp00/d0001_prd_프레젠테이션.pptx`
- 입력: `data/report.txt` → 출력: `data/report_프레젠테이션.pptx`
- 입력 없음 (대화 기반) → 출력: `00_doc/{주제}_프레젠테이션.pptx`

### 3.3 슬라이드 API

| 메서드 | 용도 | 배경 |
|--------|------|------|
| `add_cover_slide(title, subtitle, description, badge_text, footer_items)` | 표지 | 다크 |
| `add_about_slide(icon, name, subtitle, headline, description, stats[3])` | 소개 | 라이트 |
| `add_grid_slide(badge_text, subtitle, cards[4])` | 그리드 | 다크 |
| `add_features_slide(badge_text, subtitle, features[4], quote)` | 특징 | 라이트 |
| `add_tips_slide(badge_text, subtitle, tips[3])` | 팁 | 다크 |
| `add_closing_slide(title, subtitle, badge_text, footer_items)` | 마무리 | 다크 |

**파라미터 형식**:
- `cards`: `[{icon, title, desc, label}]`
- `features`: `[{title, desc}]`
- `tips`: `[{icon, title, desc}]`
- `footer_items/stats`: `[{label, value}]`

---

## 4. 사용 예시

### 4.1 기본 실행

```bash
# 마크다운 파일에서 PPTX 생성
ooppt run 00_doc/sp00/d0001_prd.md
# → 00_doc/sp00/d0001_prd_프레젠테이션.pptx

# 텍스트 파일에서 생성
ooppt run data/report.txt
# → data/report_프레젠테이션.pptx

# 미리보기
ooppt preview
```

### 4.2 소스 매핑 전략

| 소스 | 처리 | 권장 슬라이드 |
|------|------|--------------|
| `.md` 제목 | 구조 파싱 | cover |
| `.md` 개요 | 계층 추출 | about |
| `.txt` 단락 | 문단 분리 | features |
| `.json` 데이터 | 구조화 | grid |
| 목록 3-4개 | 항목 추출 | grid/tips |
| 결론 | 마무리 | closing |

### 4.3 스타일 설정

| 항목 | 값 |
|------|-----|
| 다크 배경 | `#0F0F0F` |
| 라이트 배경 | `#F5F5F0` |
| 카드 배경 | `#1A1A1A` |
| 텍스트 | `#FFFFFF`, `#1A1A1A`, `#888888` |
| 폰트 | Pretendard (대체: 맑은 고딕) |
| 크기 | 16:9, 여백 0.67인치 |

### 4.4 환각 방지 원칙

- ✅ 소스 내용만 사용
- ✅ 원문 유지
- ✅ 출처 표기
- ❌ AI 추가 콘텐츠 생성 금지

---

## 5. 스크립트 구조

### 5.1 파일 구조

```
.claude/skills/ooppt/scripts/ooppt_pptx.py   # 생성 라이브러리
.claude/skills/ooppt/scripts/ooppt_pack.py   # XML → PPTX
.claude/skills/ooppt/scripts/ooppt_unpack.py # PPTX → XML
```

### 5.2 유틸리티 명령어

```bash
# PPTX 언팩 (디버깅용)
python .claude/skills/ooppt/scripts/ooppt_unpack.py input.pptx output_dir

# XML 팩 (재구성용)
python .claude/skills/ooppt/scripts/ooppt_pack.py input_dir output.pptx
```

---

## 6. 의존성

### 6.1 설치

```bash
pip install python-pptx Pillow
```

### 6.2 확인

```bash
python -c "import pptx; print('python-pptx OK')"
python -c "from PIL import Image; print('Pillow OK')"
```

---

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/ooppt/SKILL.md` | 스킬 정의 |
| `.claude/skills/ooppt/scripts/ooppt_pptx.py` | 생성 라이브러리 |
| `.claude/guides/common_guide.md` | 공통 가이드 |
