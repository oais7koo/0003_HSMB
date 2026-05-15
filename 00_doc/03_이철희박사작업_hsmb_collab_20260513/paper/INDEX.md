# Paper Revision Workspace

> HSMB 논문 수정 작업 공간. PRD [d0001_prd.md](../00_doc/sp00/d0001_prd.md) **v05** 기반.
> **2026-04-22 구조 개편**: Discussion을 별도 §VIII로 분리, §VII에 CNN Crack Detection 신규 장 삽입 (R03 정면 대응).

## 구조

```
paper/
├── original/
│   └── Revision_0224.docx      # 원본 투고본 (2026-02-24)
├── full_manuscript.md          # pandoc 변환 전체 텍스트 (참조용)
├── media/                      # 원본 이미지 (pandoc 추출)
├── sections/                   # 장별 분리 작업 파일 (영문)
│   ├── 00_frontmatter.md       # Title / Abstract / Keywords
│   ├── 01_introduction.md      # §I Introduction
│   ├── 02_related_research.md  # §II Related Research
│   ├── 03_hsmb_dataset.md      # §III HSMB Dataset (+ E. Directional BEW/MTF 예정)
│   ├── 04_proposed_nr_iqa.md   # §IV Proposed NR-IQA (+ D. Theoretical Basis, E. Ablation)  ← R04
│   ├── 05_experimental.md      # §V Experimental Results (H/V 분리)
│   ├── 06_field_validation.md  # §VI Field Validation (area-scan 재작성, complex-blur)  ← R01/R02
│   ├── 07_crack_detection.md   # §VII CNN Crack Detection (신규 장)  ← R03
│   ├── 08_discussion.md        # §VIII Discussion (신규 분리)
│   ├── 09_conclusion.md        # §IX Conclusion + Backmatter
│   ├── 99_references.md        # References (번호 정리 보류)
│   └── ko/                     # 한글 저자 내부 검토 버전 (동일 9개 파일 + 99)
└── revised/                    # 최종 수정본 (머지 단계)
```

## 섹션 매핑 — 원본 → 개편안

| 원본 § | 개편안 § | 제목 | 수정 범위 | 관련 Reviewer |
|:------:|:--------:|------|----------|--------------|
| Frontmatter | Frontmatter | Title/Abstract/Keywords | Abstract 수치 + downstream·방향성 언급 | R01~R03 |
| I | I | INTRODUCTION | roadmap 문장 업데이트, downstream 언급 추가 | R03 |
| II | II | RELATED RESEARCH | 경미 (선택: 파라미터 선행연구) | R04 |
| III | III | HSMB DATASET | + E. Directional BEW/MTF Analysis (H/V) | R01 간접 |
| IV | IV | PROPOSED NR-IQA | + D. Theoretical Basis / E. Ablation | **R04** |
| V | V | EXPERIMENTAL RESULTS | Tables 4~8 H/V 분리, 표 재포맷 | (구조 정비) |
| VI | VI | FIELD VALIDATION | 전면 재작성 (area-scan, 50조건, complex-blur) | **R01, R02** |
| — | **VII (신규)** | CNN CRACK DETECTION | 신규 장 — Task B 결과 반영 | **R03** |
| (§VI 말미) | **VIII (신규 분리)** | DISCUSSION | 주제별 R01~R04 체계적 대응 | 종합 |
| VII | **IX** | CONCLUSION | 수치 업데이트 + Backmatter | R01~R03 |

## 현재 준비 상태

- [x] 원본 docx → markdown 변환 (pandoc, 969 라인)
- [x] 이미지 추출 (media/)
- [x] Frontmatter 분리 (영문 + ko)
- [x] §I Introduction (영문 + ko) — roadmap 문장 v05 구조에 맞게 업데이트
- [x] §II Related Research (영문 + ko)
- [x] §III HSMB Dataset (영문 + ko)
- [x] §IV Proposed NR-IQA (영문 + ko) — D/E 서브섹션 추가 대기
- [x] §V Experimental Results (영문 + ko) — 재작성 초안 v02 (표 재포맷)
- [x] §VI Field Validation (영문 + ko) — 재작성 초안 v02 + Figure 18 + complex-blur
- [x] **§VII Crack Detection** (영문 + ko) — 신규 골격 작성 (2026-04-22), Task B 결과 대기
- [x] **§VIII Discussion** (영문 + ko) — 신규 골격 작성 (2026-04-22), 주제별 A~E 서술
- [x] §IX Conclusion + Backmatter (영문 + ko) — 원본 §VII → §IX 재번호
- [x] References (번호 정합성 오류 발견, 최종 정리 보류)

## 작업 방식

1. 각 section 파일을 개별 편집 → `## 수정 메모` 섹션 참조
2. Reviewer 코멘트별 수정 근거를 수정 메모에 기록
3. 영문은 학술지 제출용, 한글(`ko/`)은 저자 내부 검토용
4. 최종 단계에서 `revised/submission_revised.md` 통합 → docx 변환
