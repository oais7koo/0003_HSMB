# oosurvey_guide - 논문 서베이 및 분석 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oosurvey/SKILL.md` | 공통: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 1. 개요

oosurvey는 논문 폴더를 분석하여 연구 주제 관련 서베이 문서를 생성/관리하는 스킬입니다.

### 1.1 핵심 기능

- 논문 폴더 분석 및 관련 논문 필터링
- 선행연구 정리 및 분석
- 추가 연구 제안 (연구 갭, 후속 방향)
- PRD 연동 (연구 주제 자동 감지)
- d0004 이슈 연동

### 1.2 입출력

- **입력**: 논문 폴더 (PDF, 서머리, 전문)
- **출력**: `00_doc/sp00/d0110_survey.md` 서베이 문서
- **연동**: `d0001_prd.md` (연구 주제), `d0004_todo.md` (이슈)

---

## 2. 워크플로우

### 2.1 run 워크플로우 (기본)

```
1. 주제 결정 (--topic 옵션 또는 PRD 추출)
    ↓
2. 논문 폴더 스캔 (paper_list.md 우선, 없으면 폴더 스캔)
    ↓
3. 관련 논문 필터링 (키워드 매칛, 관련성 점수)
    ↓
4. 선행연구 정리 (핵심 방법론, 성능, 한계점)
    ↓
5. 추가 연구 제안 생성 (연구 갭, 후속 방향)
    ↓
6. 결과 저장 (d0110_survey.md)
    ↓
7. 이슈 등록 (분석 불가 논문 → d0004)
```

### 2.2 서브에이전트 활용

| 작업 | 에이전트 | 병렬 가능 |
|------|---------|:--------:|
| 서머리 분석 | `Explore` | O |
| 전문 분석 | `academic-researcher` | O |
| PDF 분석 | `data-analyst` | O |
| 문서 생성 | `task-executor` | - |

---

## 3. 상세 사용법

### 3.1 명령어

| 명령어 | 설명 |
|--------|------|
| `oosurvey status` | paper 폴더 현황, d0110 상태, 미분석 논문 |
| `oosurvey version` | 스킬 버전 정보 (v07) |
| `oosurvey list` | 논문 목록 (paper_list.md 참조, 없으면 폴더 스캔) |
| `oosurvey run` | 서머리 기반 분석 → d0110_survey.md 생성 |
| `oosurvey deeprun` | PDF 포함 정밀 분석 → d0110_survey.md 생성 |
| `oosurvey compare` | 논문 간 비교 분석 |
| `oosurvey cite` | 인용 형식 생성 (APA, IEEE, BibTeX) |
| `oosurvey add [폴더]` | 새 논문 추가 분석 → 기존 d0110에 병합 |

### 3.2 공통 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--paper-dir` | 논문 폴더 경로 오버라이드 | `--paper-dir ../0002_paper/02_paper` |
| `--topic` | 연구 주제 오버라이드 | `--topic "객체 탐지"` |
| `--keywords` | 키워드 오버라이드 (콤마 구분) | `--keywords "YOLO,ResNet"` |
| `--threshold` | 관련성 임계값 (기본 2) | `--threshold 3` |
| `--output` | 출력 파일 경로 지정 | `--output 00_doc/sp00/d0101_survey.md` |
| `--dry-run` | 실행 없이 계획만 출력 | |
| `--verbose` | 상세 로그 출력 | |

### 3.3 논문 폴더 설정

**.env 파일에서 설정** (권장):

```bash
# .env
OAIS_PAPER_DIR=../0002_paper/02_paper   # 상대경로
# 또는
OAIS_PAPER_DIR=C:/Users/.../paper       # 절대경로
```

**기본값**: `paper/` (프로젝트 내)

**우선순위**:
1. `--paper-dir` 옵션
2. `.env`의 `OAIS_PAPER_DIR`
3. 기본값 `paper/`

---

## 4. 사용 예시

### 4.1 기본 실행

```bash
# 현황 확인
oosurvey status

# 논문 목록
oosurvey list

# 서베이 생성 (PRD 기반)
oosurvey run

# 정밀 분석 (PDF 포함)
oosurvey deeprun
```

### 4.2 주제 지정

```bash
# 커스텀 주제로 서베이
oosurvey run --topic "크랙 탐지 딥러닝"

# 키워드 지정
oosurvey run --topic "객체 탐지" --keywords "YOLO,SSD,RetinaNet"

# 출력 파일 지정
oosurvey run --topic "Transformer" --output 00_doc/sp00/d0101_transformer_survey.md
```

### 4.3 논문 폴더 지정

```bash
# 논문 폴더 지정
oosurvey run --topic "U-Net" --paper-dir ../0002_paper/02_paper
```

### 4.4 list 명령어

```bash
# 전체 목록
oosurvey list --all

# 미완료만
oosurvey list --pending

# 최근 10개
oosurvey list --recent 10

# 제목 검색
oosurvey list --search crack
```

### 4.5 논문 비교 및 인용

```bash
# 특정 논문들 비교
oosurvey compare 251201-0036 251130-2321 251108-1402

# 전체 관련 논문 비교
oosurvey compare --all

# 성능 중심 비교
oosurvey compare --focus performance

# 인용 생성
oosurvey cite --all --format bibtex > references.bib
oosurvey cite 251201-0036 --format apa
```

### 4.6 새 논문 추가

```bash
# 새 논문 추가 분석
oosurvey add paper/251206-1234
```

---

## 5. 지원 폴더 구조

### 5.1 구조 A: 날짜-시간 코드 (권장)

```
paper/
├── {YYMMDD}-{HHMM}/           # 논문별 폴더
│   ├── {코드}_00_*_서머리.md   # 서머리 (최우선)
│   ├── {코드}_04_전문(한글).md  # 한글 전문
│   ├── {코드}_03_전문(영어).md  # 영문 전문
│   └── *.pdf                  # 원본 PDF
```

### 5.2 파일 우선순위

| 순서 | 패턴 | 분석 대상 |
|------|------|:--------:|
| 1 | `*서머리*.md`, `summary*.md` | run, deeprun |
| 2 | `*전문(한글)*.md`, `*korean*.md` | run, deeprun |
| 3 | `*전문(영어)*.md`, `*english*.md` | deeprun |
| 4 | `*.pdf` | deeprun |

---

## 6. 관련성 판단

### 6.1 키워드 매칭 기반 점수

| 카테고리 | 예시 키워드 | 가중치 |
|----------|------------|:------:|
| 핵심 기술 | PRD에서 추출한 키워드 | 2.0 |
| 모델/아키텍처 | U-Net, ResNet, Transformer, YOLO | 1.5 |
| 방법론 | segmentation, detection, attention | 1.0 |
| 도메인 | image, vision, NLP, audio | 0.5 |

**기본 임계값**: 2.0 (2개 이상 매칭)

---

## 7. 출력 문서 구조

```markdown
# d0110_survey.md - 논문 서베이

## 1. 개요
- 연구 주제, 분석 논문 수, 관련 키워드

## 2. 서베이
### 2.1 {논문 제목}
- 출처, 핵심 내용, 관련 기술, 관련도, 적용 가능성

## 3. 분석 요약
### 3.1 기술별 분류
### 3.2 핵심 인사이트
### 3.3 본 연구 적용점

## 4. 참고 논문 목록

## 5. 추가 연구 제안
### 5.1 추가 분석 필요 논문
### 5.2 연구 갭 (Research Gap)
### 5.3 후속 연구 방향 제안
### 5.4 추가 검색 키워드 제안
```

---

## 8. d0004 연동

### 8.1 이슈 유형

| 유형 | 분류 | 설명 |
|------|------|------|
| 서머리 누락 | DOCS | 논문에 서머리 파일 없음 |
| PDF 분석 실패 | BUGFIX | PDF 읽기/파싱 오류 |
| 관련성 미판단 | MISC | 키워드 매칭 불가 |

### 8.2 ID 규칙

- Prefix: `P` (Paper)
- 예: P001, P002...

---

## 9. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/oosurvey/SKILL.md` | 스킬 정의 |
| `00_doc/sp00/d0001_prd.md` | 연구 주제 참조 |
| `00_doc/sp00/d0110_survey.md` | 생성 문서 |
| `00_doc/sp00/d0004_todo.md` | 이슈 등록 |
| `.claude/guides/common_guide.md` | 공통 가이드 |
