# oopaper_guide.md - 논문 관리 및 분석 가이드

## 문서 이력 관리
- v15 2026-02-20 — **경로 변경**: data/01_book/ → 03_paper/, 4단계 상태(C4), 서베이 15_paper_survey/, PRD 참조 추가
- v14 2026-02-08 — **루트 폴더 경로 변경**: 03_document/ → data/01_book/ (down→00_down, paper_en→11_paper_en, paper_ko→12_paper_ko)
- v13 2026-02-07 — **경로 변경**: 00_doc/down, 00_doc/paper_en, 00_doc/paper_ko → 03_document/ 하위로 이동
- v12 2026-02-05 — **논문리스트 경로 변경**: d0110_영어논문(보고서)_리스트.md → d0110_영어논문(보고서)_리스트.md, d0101 추가
- v11 2026-02-05 — **경로 변경**: 01_down → 00_doc/down, 00_doc/paper_en/1_paper → 00_doc/paper_en
- v10 2026-02-01 — **PDF 압축 규칙 추가**: 새 PDF 다운로드/처리 시 압축 적용 권장, 섹션 1.6 신설
- v09 2026-01-23 — **폴더 ID 규칙 명확화**: 접미사(-0001, -0002) 사용 금지, 1분 대기 방식으로 고유성 확보
- v08 2026-01-21 — **translator 에이전트 연동**: 섹션 1.3 한글 번역 규칙에 에이전트 사용법 추가
- v07 2026-01-21 — **파일명 변경**: paper_guide.md → oopaper_guide.md
- v06 2026-01-18 — 참고문헌 규칙 강화: B안(영어 전문 References 필수) + A안(서머리 참고문헌 전체 포함)
- v05 2026-01-15 — 섹션 1.3.1 추가: 서머리 참고문헌 섹션 필수화
- v04 2026-01-14 — 섹션 1.5 추가: `oopaper run` 전체 자동 정리 워크플로우
- v03 2026-01-13 — 섹션 1.4 추가: `oopaper 정리` 워크플로우
- v02 2026-01-06 — 섹션 1.3 추가: 한글 번역 규칙 (수동 번역 필수)
- v01 2026-01-06 — 최초 생성 (oopaper.md에서 분리)

---

> 스킬: `.claude/skills/oopaper/SKILL.md` | 공통: `.claude/guides/common_guide.md`
> PRD: `00_doc/sp03/d30001_prd.md` | TODO: `00_doc/sp03/d30004_todo.md`

## 0. 폴더 구분

| 폴더 | 설명 | 리스트 파일 |
|------|------|------------|
| `03_paper/11_paper_en/` | 영어 논문/보고서 | `03_paper/11_paper_en/paper_list.md` |
| `03_paper/12_paper_ko/` | 한글 논문/보고서 | (별도 관리) |
| `03_paper/15_paper_survey/` | 서베이/종합 문서 | - |

---

## 1. paper 폴더 구조

### 1.1 지원 구조

**구조 A: 날짜-시간 코드 (표준)**
```
03_paper/11_paper_en/
├── {YYMMDD}-{HHMM}/                     # 논문별 폴더
│   ├── {CODE}_00_{Title3}_서머리.md      # 서머리 + 키워드 + 참고문헌
│   ├── {CODE}_01_{Title3}.pdf           # 원본 PDF
│   ├── {CODE}_03_{Title3}_전문(영어).md  # 영어 전문 (References 포함)
│   ├── {CODE}_04_{Title3}_전문(한글).md  # 한글 번역
│   └── {CODE}_05_{Title3}_분석.md       # 정밀 분석 (anal --deep)
```

**파일명 규칙 상세**:
- **{CODE}**: `YYMMDD-HHMM` 형식의 폴더 코드
- **{Title3}**: 논문 제목의 **첫 3단어** (공백을 `_`로 연결)
  - 예: "Deep Residual Learning for Image Recognition" -> `Deep_Residual_Learning`
- **번호 체계**:
  - `00`: 서머리 및 메타데이터 + 키워드 + 참고문헌
  - `01`: 원본 PDF
  - `03`: 영어 전문 (Markdown, References 포함)
  - `04`: 한글 번역 전문 (Markdown)
  - `05`: 정밀 분석 (anal --deep)

**폴더 ID 생성 규칙**:
- 형식: `YYMMDD-HHMM` (연월일-시분)
- **접미사 금지**: `-0001`, `-0002` 등의 접미사 사용 불가
- **고유성 확보**: 다수 PDF 처리 시 각 PDF 간 60초 대기하여 분 단위 고유성 유지
- 예시: `260123-1241`, `260123-1242`, `260123-1243` (1분 간격)

**구조 B: 논문명 기반 (Legacy)**
```
paper/
├── {논문제목}/
│   ├── summary.md
│   ├── full_text.md
│   └── paper.pdf
```

### 1.2 파일 우선순위

| 순서 | 패턴 | 분석 대상 |
|------|------|:--------:|
| 1 | `*서머리*.md`, `summary*.md` | run, deeprun |
| 2 | `*전문(한글)*.md`, `*korean*.md` | run, deeprun |
| 3 | `*전문(영어)*.md`, `*english*.md` | deeprun |
| 4 | `*.pdf` | deeprun |

### 1.3 한글 번역 규칙

> **권장**: translator 에이전트를 사용한 고품질 번역

| 항목 | 규칙 |
|------|------|
| 번역 방식 | **translator 에이전트 사용 권장** (또는 AI 어시스턴트 수동 번역) |
| 번역 주체 | translator 에이전트 또는 AI 어시스턴트 |
| 입력 파일 | `03_전문(영어).md` 또는 원본 PDF |
| 출력 파일 | `04_전문(한글).md` |

#### translator 에이전트 사용법

```bash
# 1. 번역 템플릿 생성
oopaper trans korean --folder {폴더ID}

# 2. Claude Code에서 translator 에이전트 호출
"translator 에이전트를 사용해서 03_paper/11_paper_en/{폴더ID}/04_전문(한글).md 번역해줘"
```

**translator 에이전트 특징**:
- 학술 논문 전문 용어 일관성 유지
- 수식/코드 블록 원문 보존
- 번역투 없는 자연스러운 한국어
- 용어집 기반 일관된 번역

**에이전트 정의**: `.claude/agents/translator.md`

### 1.3.1 서머리 참고문헌 섹션 (필수)

> **필수**: 서머리 생성 시 **참고문헌(References) 섹션**을 반드시 포함
> **중요**: 참고문헌은 **요약하지 않고 원문 그대로** 전체를 가져올 것

**서머리 필수 구조**:
```markdown
# 논문 제목

## 기본 정보
- **저자**: ...
- **발행년도**: ...
- **출처/저널**: ...

## 초록 (Abstract)
...

## 핵심 내용
### 연구 목적
### 주요 방법론
### 핵심 기여
### 실험 결과

## 결론 및 시사점
...

## 키워드
AI가 추출한 자유 키워드 (C3: 분류 체계 없이 자유 형식)

## 참고 논문 (References)
논문의 References 섹션에서 **전체 참고문헌을 원문 그대로** 추출하여 기록
(03_전문(영어).md의 References 섹션을 그대로 복사)

### 내부 보유
| # | 참고문헌 | 보유 폴더 |
|---|----------|----------|
| 1 | 저자명 (연도). 제목. 저널. | [YYMMDD-HHMM] |

### 외부 (미보유)
| # | 참고문헌 | DOI/arXiv | 링크 |
|---|----------|-----------|------|
| 1 | 저자명 (연도). 제목. 저널. | DOI:10.xxxx/xxx 또는 arXiv:YYMM.NNNNN | [PDF] 또는 - |
```

**참고문헌 추출 규칙**:
- PDF 또는 03_전문(영어).md의 References 섹션에서 **모든 참고문헌** 원문 그대로 추출
- 절대 요약하거나 선별하지 않음 - 전체를 그대로 가져올 것
- 번호가 있는 경우 원본 번호 유지
- 형식: `저자 (연도). 제목. 저널/출처.`
- DOI/arXiv ID 필수 추출 (extend 연동):
  - DOI가 있으면 반드시 `DOI:10.xxxx/xxx` 형식으로 기재
  - arXiv 논문이면 `arXiv:YYMM.NNNNN` 형식으로 기재
  - 둘 다 없으면 `-` 기재 (빈칸 금지)
  - 원문 References에서 DOI/arXiv를 찾을 수 없으면 제목 기반 추정하지 말고 `-` 사용
- **내부 매칭 (C1)**: paper_list.md와 대조하여 보유 논문은 `[폴더ID]` 링크, 미보유는 DOI/arXiv 컬럼 활용
- "다수 논문", "관련 연구" 등 뭉뚱그린 표현 금지 - 개별 논문으로 분리하여 각각 1행씩 기재

### 1.3.2 영어 전문 References 섹션 (필수)

> **필수**: 03_전문(영어).md 생성 시 **References 섹션**을 반드시 포함

**영어 전문 필수 구조**:
```markdown
# 논문 제목

## Abstract
...

## 1. Introduction
...

(본문 섹션들...)

## N. Conclusion
...

## Keywords
...

## References

[1] Author A, Author B. (Year). Title of the paper. Journal Name, Volume(Issue), Pages.
[2] Author C, et al. (Year). Title of another paper. Conference Proceedings, Pages.
...
(원본 논문의 모든 참고문헌)
```

**영어 전문 References 규칙**:
- PDF에서 텍스트 추출 시 **References 섹션까지 반드시 포함**
- 모든 참고문헌을 원문 형식 그대로 추출
- 참고문헌이 누락된 영어 전문은 **미완료 상태**로 처리
- References 섹션이 없으면 서머리의 참고문헌도 누락되므로 필수

**참고문헌 워크플로우**:
```
PDF → 03_전문(영어).md (References 포함) → 00_서머리.md (References 복사 + 내부 매칭)
```

**번역 워크플로우**:
```
1. 영어 전문(03_전문(영어).md) 읽기
2. AI 어시스턴트가 전체 내용 한글 번역
3. 04_전문(한글).md 파일에 작성
4. 핵심 용어 정리 테이블 추가 (선택)
```

**금지 사항**:
- 자동 번역 스크립트/API 사용
- 기계 번역 결과 그대로 사용
- 템플릿만 생성하고 번역 미수행

### 1.4 정리 워크플로우 (00_down → 11_paper_en)

**명령어**: `oopaper run` (Phase 0에서 자동 처리)

#### PDF 파일 처리

```
03_paper/00_down/ 스캔
    ↓
각 PDF 파일에 대해 반복:
    1. 메타데이터 추출 (제목, 저자, 연도, arXiv ID 등)
    2. 03_paper/11_paper_en/에 YYMMDD-HHMM 폴더 생성
    3. PDF를 {CODE}_01_{Title3}.pdf로 리네임 후 이동
    4. 03_paper/00_down/에서 해당 PDF 삭제
    ↓
다음 파일 처리
```

#### 다운로드 리스트 처리

```
03_paper/00_down/*.md (다운로드 리스트) 스캔
    ↓
각 논문 항목에 대해 반복:
    1. 다운로드 시도 (arXiv/DOI)
    2-a. 성공 → 03_paper/11_paper_en/에 폴더 생성 및 정리
    2-b. 실패 → paper_list.md "다운로드 불가" 섹션에 추가
    3. 리스트에서 해당 항목 제거
    ↓
다음 항목 처리
    ↓
빈 리스트 파일 삭제
```

#### 결과 구조

```
03_paper/11_paper_en/
├── paper_list.md                              # 전체 논문 목록
└── 260123-1241/
    ├── 260123-1241_00_Attention_Is_All_서머리.md
    └── 260123-1241_01_Attention_Is_All.pdf
```

### 1.5 전체 자동 파이프라인 (oopaper run)

**명령어**: `oopaper run` 또는 `oopaper run --limit N`

> **PRD 참조**: d30001_prd.md §4 기능요구사항, §9 Clarifications (C1~C5)

모든 미완료 논문을 7단계(Phase 0~6)로 자동 처리하는 통합 명령어입니다.

#### 처리 단계

```
Phase 0: 00_down → 11_paper_en 이동          [F3001, F3003]
Phase 1: 스캔 → 미완료 논문 목록 + 4단계 상태  [F3031, C4]
Phase 2: 서머리 생성 + 키워드 추출             [F3010, F3012, C3]
Phase 3: 영문 전문 추출                       [F3010]
Phase 4: 한글 번역                            [F3011]
Phase 5: 참고문헌 추출 + 내부 매칭             [F3013, F3020, C1]
Phase 6: paper_list.md 동기화 + 상태 갱신      [F3031, C4]
```

#### 각 단계별 작업 내용

| 단계 | 입력 | 출력 | 작업 내용 | PRD |
|------|------|------|----------|-----|
| Phase 0 | 00_down PDF | YYMMDD-HHMM 폴더 | PDF 이동 및 리네임 | F3001 |
| Phase 1 | 전체 폴더 | 작업 목록 | 완성도 검사 + 4단계 상태 판정 | C4 |
| Phase 2 | PDF | 00_서머리.md | 서머리 + 키워드 추출 | F3010, F3012, C3 |
| Phase 3 | PDF | 03_전문(영어).md | PDF 전체 텍스트 추출 | F3010 |
| Phase 4 | 03_전문(영어).md | 04_전문(한글).md | translator 에이전트 번역 | F3011 |
| Phase 5 | References | 서머리 갱신 | 참고문헌 내부/외부 매칭 | F3013, C1 |
| Phase 6 | 폴더 스캔 | paper_list.md | 동기화 + 상태 갱신 | F3031, C4 |

#### 4단계 상태 체계 (C4)

| 상태 | 설명 | 판정 조건 |
|------|------|----------|
| X | 미처리 | PDF만 존재 |
| S | 서머리 완료 | 서머리.md 존재 (품질 OK) |
| T | 번역 완료 | 서머리 + 영문 + 한글 존재 |
| O | 완료 | 서머리 + 영문 + 한글 + 참고문헌 내부매칭 |

#### 품질 기준

| 파일 | 최소 용량 | 필수 조건 |
|------|:--------:|----------|
| 00_서머리.md | 500 bytes | 템플릿 마커 없음, 필수 섹션 존재, 키워드 포함 |
| 03_전문(영어).md | 1000 bytes | 깨진 문자 없음, References 포함 |
| 04_전문(한글).md | 1000 bytes | 번역 완료 마커 없음 |

#### 실행 예시

```bash
# 전체 논문 정리 (미완료 전체)
oopaper run

# 10개만 처리
oopaper run --limit 10

# 실행 계획만 확인
oopaper run --dry-run

# 특정 폴더만 처리
oopaper run --folder 260220-1401

# Phase 0 건너뛰기
oopaper run --skip-organize
```

### 1.6 PDF 압축 규칙

> **권장**: 새 PDF 다운로드 또는 처리 시 압축 적용

**적용 시점**:
- 03_paper/00_down/에 새 PDF 추가 시
- 용량이 큰 PDF (20MB 이상) 처리 시
- 배치 정리 작업 전

**압축 명령어**:
```bash
# 단일 파일 압축
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py input.pdf output.pdf --compress-only

# 00_down 폴더 전체 압축
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py --batch 03_paper/00_down tmp/compressed -r

# 특정 논문 폴더 압축
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py "03_paper/11_paper_en/260123-1241/*.pdf" --compress-only
```

**압축 옵션 가이드**:

| 상황 | 옵션 | 설명 |
|------|------|------|
| 일반 논문 (텍스트 있음) | `--compress-only` | 텍스트 보존, 이미지 스트림만 압축 |
| 스캔 PDF (텍스트 없음) | (기본) | 자동 OCR 적용 → 검색 가능 |
| 빠른 처리 | `--compress-only --quality 70` | 품질 높게 유지 |
| 최대 압축 | `--quality 30 --dpi 100` | 이미지 품질 낮춤 (텍스트 없는 PDF만) |

**주의사항**:
- 텍스트가 있는 PDF는 pypdf 기본 압축만 적용 (효과 제한적)
- 강력한 압축이 필요하면 Ghostscript 별도 설치 필요
- OCR 기능은 pytesseract + poppler 설치 필요

**워크플로우 통합**:
```
다운로드 → 압축(선택) → 정리(00_down → 11_paper_en) → 분석
```

---

## 2. 분석 기준

### 2.1 관련성 판단

키워드 매칭 기반 점수 계산:

| 카테고리 | 예시 키워드 | 가중치 |
|----------|------------|:------:|
| 핵심 기술 | PRD에서 추출한 키워드 | 2.0 |
| 모델/아키텍처 | U-Net, ResNet, Transformer, YOLO | 1.5 |
| 방법론 | segmentation, detection, attention | 1.0 |
| 도메인 | image, vision, NLP, audio | 0.5 |

**기본 임계값**: 2.0 (2개 이상 매칭)

### 2.2 deeprun 추가 분석 항목

| 항목 | 설명 |
|------|------|
| 모델 아키텍처 | 상세 구조, 레이어, 파라미터 수 |
| 실험 설정 | 데이터셋, 하이퍼파라미터, 학습 전략 |
| 성능 수치 | 정량적 메트릭 (IoU, F1, mAP 등) |
| 핵심 수식 | Loss function, 핵심 알고리즘 |
| Figure/Table | 주요 시각자료 분석 |
| 한계점 | 논문에서 언급한 한계 |

---

## 3. 서베이 문서 (15_paper_survey/)

> 서베이 문서는 `03_paper/15_paper_survey/`에 저장

### 3.1 기본 구조

```markdown
# d0110_survey_{주제}.md - 논문 서베이

## 문서 이력 관리
- v01 YYYY-MM-DD — 초기 서베이 (N편 분석)

---

## 1. 개요

- **연구 주제**: {PRD에서 추출}
- **분석 논문**: N편
- **분석 일시**: YYYY-MM-DD HH:MM
- **관련 키워드**: {키워드 목록}

---

## 2. 서베이

### 2.1 {논문 제목}

- **출처**: {폴더코드}
- **핵심 내용**: {1-2문장 요약}
- **관련 기술**: {키워드}
- **관련도**: {높음/중간/낮음} ({점수})
- **적용 가능성**: {본 연구와의 연관성}

---

## 3. 분석 요약

### 3.1 기술별 분류

| 기술 | 논문 수 | 대표 논문 |
|------|---------|----------|
| {기술1} | N | {논문명} |

### 3.2 핵심 인사이트

1. {인사이트}
2. {인사이트}

### 3.3 본 연구 적용점

| 논문 | 적용 가능 기술 | 구현 우선순위 |
|------|--------------|:------------:|
| {논문} | {기술} | P1/P2/P3 |

---

## 4. 참고 논문 목록

| # | 폴더코드 | 제목 | 관련도 | 상태(C4) |
|---|----------|------|:------:|:--------:|
| 1 | 260123-1241 | ... | 높음 | O |
```

### 3.2 deeprun 추가 섹션

```markdown
### 2.N {논문 제목}

- **출처**: {폴더코드}
- **핵심 내용**: {상세 요약}
- **모델 아키텍처**:
  - Encoder: {설명}
  - Decoder: {설명}
  - 파라미터: {M}
- **실험 결과**:
  - Dataset: {데이터셋}
  - Metrics: IoU {값}, F1 {값}, mAP {값}
  - 비교 모델 대비: {+/-}%
- **핵심 기여**: {주요 기여점}
- **한계점**: {한계}
- **본 연구 적용**:
  - 적용 가능 기술: {기술}
  - 구현 난이도: {상/중/하}
  - 예상 효과: {설명}
```

---

## 4. d30004 연동

### 4.1 이슈 유형

| 유형 | 분류 | 설명 |
|------|------|------|
| 서머리 누락 | DOCS | 논문에 서머리 파일 없음 |
| PDF 분석 실패 | BUGFIX | PDF 읽기/파싱 오류 |
| 관련성 미판단 | MISC | 키워드 매칭 불가 |

### 4.2 이슈 등록 형식

| ID | 발생일 | 분류 | 내용 | 우선순위 | 상태 |
|----|--------|------|------|---------|------|
| P001 | 2026-01-06 | DOCS | paper/260123-1241 - 서머리 누락 | 낮음 | 대기 |

### 4.3 ID 규칙

- Prefix: `P` (Paper)
- 예: P001, P002...

---

## 5. 인용 출력 형식

### 5.1 BibTeX

```bibtex
@article{chen2024unet,
  title={Deep Learning for Crack Detection},
  author={Chen, Wei and Zhang, Li},
  journal={Pattern Recognition},
  year={2024},
  volume={89},
  pages={1-15}
}
```

### 5.2 APA

Chen, W., & Zhang, L. (2024). Deep Learning for Crack Detection. *Pattern Recognition*, 89, 1-15.

### 5.3 IEEE

W. Chen and L. Zhang, "Deep Learning for Crack Detection," *Pattern Recognition*, vol. 89, pp. 1-15, 2024.

---

## 6. 관련 문서

| 문서 | 용도 |
|------|------|
| .claude/skills/oopaper/SKILL.md | 논문 관리 스킬 |
| 00_doc/sp03/d30001_prd.md | SP03 PRD (기능 요구사항, Clarifications) |
| 00_doc/sp03/d30004_todo.md | SP03 이슈/과업 관리 |
| 03_paper/11_paper_en/paper_list.md | 논문 목록 |
| 03_paper/15_paper_survey/ | 서베이 문서 |
