# ooessay_guide - 국내 보고서 관리 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/ooessay/SKILL.md` | 공통: `.claude/guides/common_guide.md` | PRD: `00_doc/sp00/d0001_prd.md` 섹션 12

## 1. 개요

ooessay는 국내 사이트(사이언스온, RISS, DBpia, KCI 등)에서 수집한 한글 보고서/논문을 체계적으로 관리하는 스킬입니다.

### 1.1 핵심 차이점 (vs oopaper)

| 항목 | oopaper (해외 논문) | ooessay (국내 보고서) |
|------|----------------------|------------------------|
| 대상 | 영문 논문 | 한글 보고서/논문 |
| 저장소 | 02_paper/1_paper/ | 02_paper/2_essay/ |
| 파일 구성 | 00, 01, 03, 04, 05 | 00, 01, 04, 05 (03 없음) |
| 언어 | 영어 → 한글 번역 | 한글 원문 |

### 1.2 연동 문서

- `00_doc/sp00/d0001_prd.md` 섹션 12: 국내 보고서 관리 규격
- `d0004_todo.md`: 이슈 등록
- `02_paper/2_essay/report_list.md`: 보고서 목록

---

## 2. 워크플로우

### 2.1 run 워크플로우 (통합 실행)

```
Phase 0: 01_down 스캔
    → 국내 보고서 PDF 파일 스캔
    ↓
Phase 1: 폴더 생성
    → 02_paper/2_essay/YYMMDD-HHMM/ 생성
    → PDF 이동 및 파일명 표준화
    ↓
Phase 2: 서머리 작성
    → PDF 메타데이터 추출
    → 00_서머리.md 생성
    ↓
Phase 3: 한글 추출
    → PDF에서 전문 텍스트 추출
    → 04_전문(한글).md 생성
    ↓
Phase 4: 검증
    → 품질 검사
    → report_list.md 업데이트
    → d0004_todo.md 업데이트
```

### 2.2 데이터 흐름

```
외부 DB (사이언스온, RISS, DBpia, KCI)
    ↓ 수동 다운로드
01_down/ (PDF)
    ↓ run
02_paper/2_essay/ (표준 폴더)
    ↓ status
report_list.md
```

---

## 3. 상세 사용법

### 3.1 명령어

| 명령어 | 설명 |
|--------|------|
| `ooessay run` | 통합 실행: 01_down → 02_paper/2_essay 정리 + 서머리 + 한글추출 |
| `ooessay status` | 서브명령어 리스트, 01_down 대기 PDF, 02_paper/2_essay 현황 |
| `ooessay anal` | 정밀 분석: 05_분석.md 생성 |
| `ooessay trans` | PDF 텍스트 추출 (한글) |
| `ooessay compress` | PDF 압축 (텍스트 보존) |
| `ooessay fix` | 무결성 검사/수정 |
| `ooessay version` | 스킬 버전 정보 (v04) |

### 3.2 run 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| (없음) | 기본 실행: 01_down 정리 + 서머리 + 한글추출 | `ooessay run` |
| `--limit N` | 처리할 최대 보고서 수 | `ooessay run --limit 10` |
| `--folder ID` | 특정 폴더만 처리 | `ooessay run --folder 260131-0001` |
| `--dry-run` | 실행 없이 계획만 출력 | `ooessay run --dry-run` |

### 3.3 anal 옵션 (정밀 분석)

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--deep` | 정밀 분석: 참고문헌 추출, AI 요약 강화 | `ooessay anal --deep` |
| `--folder ID` | 특정 폴더만 분석 | `ooessay anal --folder 260202-0801 --deep` |
| `--force` | 기존 05_분석.md 덮어쓰기 | `ooessay anal --deep --force` |
| `--dry-run` | 실행 없이 계획만 출력 | `ooessay anal --deep --dry-run` |

### 3.4 품질 기준

| 파일 | 최소 조건 | 품질 검사 |
|------|----------|----------|
| 00_서머리.md | 500 bytes 이상 | 필수 섹션 존재, 템플릿 마커 없음 |
| 04_전문(한글).md | 1000 bytes 이상 | PDF 추출 완료, 깨진 문자 없음 |

---

## 4. 사용 예시

### 4.1 기본 실행

```bash
# 현황 확인
ooessay status

# 01_down → 02_paper/2_essay 정리
ooessay run

# 특정 폴더만 처리
ooessay run --folder 260131-0001

# 최대 10개만 처리
ooessay run --limit 10
```

### 4.2 텍스트 추출

```bash
# 전체 텍스트 추출
ooessay trans

# 특정 폴더만
ooessay trans --folder 260131-0001

# 기존 파일 덮어쓰기
ooessay trans --force
```

### 4.3 정밀 분석 (anal --deep)

```bash
# 전체 폴더 정밀 분석
ooessay anal --deep

# 특정 폴더만 정밀 분석
ooessay anal --folder 260202-0801 --deep

# 기존 분석 덮어쓰기
ooessay anal --folder 260202-0801 --deep --force
```

**정밀 분석 흐름**:
```
Phase 1: 전처리 확인 (04_전문.md 없으면 자동 생성)
    ↓
Phase 2: PDF 텍스트 분석 (참고문헌 섹션 자동 탐지)
    ↓
Phase 3: AI 분석 (핵심 요약, 주요 기여, 방법론, 결론)
    ↓
Phase 4: 분석 파일 생성 ({CODE}_05_{Title3}_분석.md)
```

### 4.4 무결성 검사

```bash
# 검사만 수행
ooessay fix --check-only

# 자동 수정 가능한 오류 수정
ooessay fix --auto-fix

# 특정 폴더만 검사
ooessay fix --folder 260131-0001
```

### 4.5 PDF 압축

```bash
# 단일 파일 압축
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py input.pdf output.pdf --compress-only

# 02_paper/2_essay 폴더 전체 압축
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py --batch 02_paper/2_essay tmp/compressed -r

# 특정 보고서 폴더 압축
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py "02_paper/2_essay/260131-0001/*.pdf" --compress-only
```

**압축 옵션**:
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--compress-only` | 압축만 (OCR 제외) | - |
| `--ocr-only` | OCR만 적용 | - |
| `--quality N` | 이미지 품질 (1-100) | 50 |
| `--dpi N` | 이미지 DPI | 150 |
| `--lang` | OCR 언어 | kor+eng |
| `--batch` | 배치 처리 모드 | - |
| `-r` | 하위 폴더 포함 | - |

---

## 5. 파일 구조

### 5.1 표준 폴더 구조

```
02_paper/2_essay/YYMMDD-HHMM/
├── {CODE}_00_{Title3}_서머리.md
├── {CODE}_01_{Title3}.pdf
├── {CODE}_04_{Title3}_전문(한글).md
└── {CODE}_05_{Title3}_분석.md      ← anal --deep 생성
```

**예시** (폴더: 260131-1105, 제목: "딥러닝 기반 균열 탐지 연구"):
```
02_paper/2_essay/260131-1105/
├── 260131-1105_00_딥러닝_기반_균열_서머리.md
├── 260131-1105_01_딥러닝_기반_균열.pdf
├── 260131-1105_04_딥러닝_기반_균열_전문(한글).md
└── 260131-1105_05_딥러닝_기반_균열_분석.md    ← anal --deep
```

### 5.2 05_분석.md 템플릿

```markdown
# {CODE}_05_{Title3}_분석

## 문서 정보
| 항목 | 내용 |
|------|------|
| 보고서 ID | {YYMMDD-HHMM} |
| 분석일 | {YYYY-MM-DD} |
| 분석 모드 | deep |

## 1. 핵심 요약 (AI 강화)
## 2. 주요 기여
## 3. 방법론 분석
## 4. 결론 및 시사점
## 5. 참고문헌 (자동 추출)
## 6. 관련 키워드
```

---

## 6. 국내 출처 약어

| 약어 | 설명 |
|------|------|
| SCIENCEON | 사이언스온 |
| RISS | 학술연구정보서비스 |
| DBpia | DBpia |
| KCI | 한국학술지인용색인 |
| KISS | 한국학술정보 |
| KISTI | KISTI 보고서 |
| NRF | 한국연구재단 |
| NTIS | 국가과학기술지식정보서비스 |
| NDSL | 국가과학기술정보센터 |

---

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/ooessay/SKILL.md` | 스킬 정의 |
| `00_doc/sp00/d0001_prd.md` 섹션 12 | 국내 보고서 관리 규격 |
| `00_doc/sp00/d0004_todo.md` | 이슈 등록 |
| `.claude/skills/oopaper/SKILL.md` | 해외 논문 관리 (참고) |
| `.claude/guides/common_guide.md` | 공통 가이드 |
