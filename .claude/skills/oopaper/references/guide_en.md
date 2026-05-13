# oopaper EN 가이드 — 영어 논문 처리 상세

> 진입점: `.claude/skills/oopaper/SKILL.md` | 한국어 보고서: `guide_ko.md` | 코드 예시: `guide.md`

## 문서 이력 관리
- v16 2026-05-09 — SKILL.md v08 동기화. 폴더 ID 표준 §2 strict화, 1폴더 1논문 정책 §3 분리, paper_list 양방향 동기화 §6, doctor/fix §9 재정의, 진단 결과 반영
- v15 2026-02-20 — 경로 정리(03_paper/), 4단계 상태(C4), 서베이 15_paper_survey/ 추가
- v14 ~ v01 — 누적 이력은 git 참조

---

## 1. 개요

이 문서는 **영어 논문(EN) 전용** 처리 절차를 SKILL.md에 정의된 표준에 따라 해설한다.
모든 명령어 카탈로그·정책 선언은 SKILL.md를 단일 진실 공급원으로 한다.

| 구분 | EN |
|------|----|
| 입력 | `{paper_root}/00_down/*.pdf` |
| 저장소 | `{paper_root}/11_paper_en/{FOLDER_ID}/` |
| 목록 | `{paper_root}/11_paper_en/paper_list.md` |
| 상태 | X / E / S / T / O (5단계) |

---

## 2. 폴더 ID 표준 (FOLDER_ID)

> SKILL.md §2 표준에 strict 적용. 본 절은 EN 처리 시 발생하는 실무 케이스 해설.

### 2.1 발급 시점별 우선순위

| 우선순위 | 출처 | 사유 |
|:------:|------|------|
| 1 | PDF 파일 mtime | 다운로드 시각을 가장 잘 보존 |
| 2 | 다운로드 메타(arXiv 등록일 등) | mtime이 후처리(압축·이동)로 갱신된 경우 |
| 3 | `datetime.now()` | 위 두 정보가 모두 부재할 때만 |

### 2.2 같은 분에 다수 PDF 처리

```
대상: 5개 PDF (모두 mtime = 2026-05-09 14:23)
→ 발급 ID:
   260509-1423   (1번째)
   260509-1424   (2번째, 분 +1)
   260509-1425   (3번째)
   260509-1426   (4번째)
   260509-1427   (5번째)
```

> 분이 24시간을 넘기면 자동으로 다음 날로 이월. **suffix `-NN` 부착 금지**.

### 2.3 자주 발생하는 위반 패턴

| 패턴 | 진단 (`oopaper doctor --check folder-id`) |
|------|----------------------------------------|
| `260222-1851-08` | ERROR: suffix 부착 — `split-multi`로 신규 ID 발급 후 폴더 재배치 필요 |
| `260222-185` | ERROR: 자릿수 부족 — 수동 정정 또는 `Phase 0` 재실행 |
| `2602221851` | ERROR: 구분자 누락 |
| `DS01_260222-1851` | ERROR: prefix 부착 — prefix 제거 후 재정규화 |

---

## 3. 1폴더 1논문 정책

> 이 정책은 paper_list.md 무결성과 인용 매칭 정확도의 핵심 전제다.

### 3.1 위반 케이스 진단 흐름

```
oopaper doctor --check multi-pdf
    ↓
폴더 내 *_01_*.pdf 또는 미정규화 *.pdf 가 2개 이상인 폴더 보고
    ↓
oopaper split-multi --folder {ID} --dry-run    # 분리 계획 확인
    ↓
oopaper split-multi --folder {ID}              # 실행: 신규 FOLDER_ID 발급
    ↓
oopaper update --lang en                       # paper_list 양방향 동기화
```

### 3.2 분리 후 산출물 처리

| 케이스 | 후속 조치 |
|--------|----------|
| 분리 전에 이미 서머리·전문이 작성된 폴더 | 첫 번째 PDF의 산출물만 유지, 나머지는 새 폴더에서 `oopaper run --folder {NEW_ID}` 재처리 |
| 분리 전에 산출물이 없는 폴더 | 분리 후 각 폴더에서 `oopaper run` 실행하면 자동 처리 |

---

## 4. 파일명 prefix 표준 — EN 적용 예시

| Prefix | 파일명 예시 | 비고 |
|:------:|------------|------|
| 00 | `260509-1423_00_Deep_Residual_Learning_서머리.md` | 한글 출력 (영문 기반 작성) |
| 01 | `260509-1423_01_Deep_Residual_Learning.pdf` | 원본 PDF |
| 03 | `260509-1423_03_Deep_Residual_Learning_전문(영어).md` | References 섹션 필수 포함 |
| 04 | `260509-1423_04_Deep_Residual_Learning_전문(한글).md` | YAML frontmatter로 stage(1/2) 추적 |
| 05 | `260509-1423_05_Deep_Residual_Learning_분석.md` | `anal --deep` 산출물 |

### 4.1 {Title3} 추출 규칙

| 단계 | 처리 |
|------|------|
| 1. 토크나이즈 | 공백·하이픈·문장부호 분리 |
| 2. stopword 제거 | `a, an, the, of, for, in, on, at, to, with, and` |
| 3. 첫 3토큰 채택 | 부족하면 stopword 포함하여 보충 |
| 4. 정규화 | `re.sub(r"[^\w\-가-힣().]+", "_", title)[:60].strip("_")` |

예:
- `Attention Is All You Need` → `Attention_Is_All`
- `BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding` → `BERT_Pre_training_Deep`

---

## 5. 서머리(`00_*_서머리.md`) 작성 규칙

> SKILL.md §3에 정의된 prefix 표준 + 본 절차로 통일된 서머리 생성.

### 5.1 필수 구조

```markdown
# {논문 제목}

## 기본 정보
- **저자**: ...
- **발행년도**: ...
- **출처/저널**: ...
- **DOI**: ...
- **arXiv**: ...

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
{AI 자유 추출, 분류 체계 없음}

## 참고 논문 (References)

### 내부 보유
| # | 참고문헌 | 보유 폴더 |
|---|----------|----------|
| 1 | 저자 (연도). 제목. 저널. | [YYMMDD-HHMM] |

### 외부 (미보유)
| # | 참고문헌 | DOI/arXiv | 링크 |
|---|----------|-----------|------|
| 1 | 저자 (연도). 제목. 저널. | DOI:10.xxxx/xxx | - |
```

### 5.2 참고문헌 추출 규칙

| 규칙 | 내용 |
|------|------|
| **요약 금지** | 원문 References 섹션을 그대로 복사 (선별·요약 X) |
| **개별 분리** | "다수 논문", "관련 연구" 등 뭉뚱그린 표현 금지 — 1행 1논문 |
| **DOI/arXiv** | 원문에 있으면 `DOI:10.xxxx/xxx` 또는 `arXiv:YYMM.NNNNN` 기재 / 없으면 `-` (빈칸 금지) |
| **추정 금지** | 제목 기반 DOI 추정 금지 — 원문에 없으면 `-` |
| **내부 매칭** | `paper_list.md` 대조 → 보유 시 `[FOLDER_ID]` 링크 |

---

## 6. paper_list.md 양방향 동기화

> SKILL.md §9의 EN 적용. `oopaper update`가 단일 진입점.

### 6.1 헤더 포맷

```markdown
# 영어 논문 리스트

> 총 N편 완료 (마지막 동기화: YYYY-MM-DD HH:MM)

## 항목

### {FOLDER_ID} - {제목} (저자, 연도)
- **상태**: O (X/E/S/T/O)
- **DOI**: ...
- **arXiv**: ...
- **키워드**: ...
- **요약**: ...

### {FOLDER_ID} - ...
```

### 6.2 양방향 검증 규칙

| 검증 | 동작 |
|------|------|
| 폴더 → 리스트 | 신규 폴더는 append |
| 리스트 → 폴더 | 폴더 부재 항목은 `[DELETED]` 태그 부착 (실제 삭제 X — 사용자 검토 후 수동 처리) |
| 헤더 카운트 | 항목 수와 일치하도록 자동 갱신 |
| 키워드 컬럼 | `oopaper keyword-sync`로 서머리에서 재추출 |

### 6.3 `download` / `extend` 직후 필수 절차

```bash
oopaper download --file 00_down/list_0509.md   # 새 PDF 다운로드
oopaper_auto organize                          # 00_down → 11_paper_en 이동
oopaper update --lang en --dry-run             # 동기화 변경 확인
oopaper update --lang en                       # 적용
```

> ⚠️ 이 단계를 건너뛰면 80개 단위로 누락 항목이 누적된다 (실제 진단 사례).

---

## 7. EN 8 Phase 상세 (run)

| Phase | 입력 | 출력 | 주체 | 주요 위험 |
|:----:|------|------|------|----------|
| 0 | `00_down/*.pdf` | `{FOLDER_ID}/{FOLDER_ID}_01_{Title3}.pdf` | `oopaper_auto.py` | mtime 부재 시 ID 의미 손실 |
| 1 | 전체 폴더 | 작업 목록(미완료·상태) | `oopaper_run.py scan` | 품질 임계 미달 검출 |
| 2 | PDF | `*_03_*_전문(영어).md` | data-analyst | References 섹션 누락 시 미완료 처리 |
| 3 | `*_03_*` | `*_00_*_서머리.md` | academic-researcher | 키워드/참고문헌 형식 위반 |
| 4 | `*_03_*` + 옵션(`--gemma`) | `*_04_*_전문(한글).md` | translator / Gemma+Claude | 번역 품질 stage 라벨 누락 |
| 5 | `*_03_*` References | 서머리 갱신 | academic-researcher | 내부/외부 분류 오류 |
| 6 | 전체 산출물 | `*_05_*_분석.md` | academic-researcher | 분석 깊이 부족 |
| 7 | 폴더 전체 | `paper_list.md` | `oopaper_run.py update` | 양방향 sync 실행 필수 |

### 7.1 5단계 상태 판정 임계

| 파일 | 최소 용량 | 추가 검증 |
|------|:--------:|----------|
| `*_00_*_서머리.md` | 500 B | 템플릿 미완료 마커 부재 + 키워드 + 참고문헌 |
| `*_03_*_전문(영어).md` | 1,000 B | References 섹션 존재 + 인코딩 정상 |
| `*_04_*_전문(한글).md` | 1,000 B | 번역 미완 마커 부재 + stage 라벨 |

미완료 마커: `(추출 필요)`, `(추후 작성)`, `[저자명]`, `# 번역 필요`, `TODO`, `[미완료]`, `작성 예정`, `(미작성)`

---

## 8. PDF 압축 (compress)

| 상황 | 옵션 | 설명 |
|------|------|------|
| 일반 논문(텍스트) | `--compress-only` | pypdf 기본 압축 |
| 스캔 PDF(이미지) | (기본) | 자동 OCR (pytesseract + poppler 필요) |
| 빠른 처리 | `--compress-only --quality 70` | 품질 보존 |
| 최대 압축 | `--quality 30 --dpi 100` | 텍스트 없는 PDF만 권장 |

```bash
# 단일 파일
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py input.pdf output.pdf --compress-only

# 00_down 일괄
uv run python .claude/skills/oopaper/scripts/oopaper_pdf_compress.py --batch 03_paper/00_down tmp/compressed -r
```

---

## 9. fix · doctor — EN 운영 시나리오

### 9.1 일상 점검 루틴 (주 1회 권장)

```bash
oopaper doctor --check folder-id     # ID 표준 위반
oopaper doctor --check multi-pdf     # 1폴더 1논문 위반
oopaper doctor --check sync          # paper_list 동기화 차이
oopaper doctor --check orphan        # 고아 항목
oopaper doctor --check quality       # 산출물 품질
```

### 9.2 자동 수정 가능 항목

| 항목 | `--auto-fix` 동작 |
|------|------------------|
| 파일명 prefix (`01_00_*` → `00_*`) | 자동 |
| 헤더 카운트 불일치 | 자동 |
| Title3 인코딩 깨짐 | 정규화 정규식 재적용 |

### 9.3 수동 처리 필요 (자동 X)

| 항목 | 사유 |
|------|------|
| FOLDER_ID 위반 (suffix 부착) | 데이터 손실 위험 → `split-multi` 또는 수동 재배치 |
| multi-PDF 폴더 | `split-multi` 명시 실행 |
| `[DELETED]` 마킹된 고아 항목 | 사용자가 백업 확인 후 paper_list에서 제거 |

---

## 10. extend — 외부 참고문헌 자동 다운로드

### 10.1 처리 흐름

```
서머리(*_00_*) → ## 참고 논문 → ### 외부 섹션 파싱
   ↓
paper_list.md + 기존 서머리 제목과 중복 제거
   ↓
arXiv API / Semantic Scholar API 검색 (5초 타임아웃, 0.5초 딜레이)
   ↓
PDF 다운로드 → {paper_root}/00_down/
   ↓
oopaper update --lang en (수동) → paper_list 동기화
```

### 10.2 사용 예시

```bash
oopaper extend                          # 전체 서머리 → 최대 10편
oopaper extend --dry-run                # 검색만
oopaper extend --folder 260301-1001     # 특정 폴더
oopaper extend --limit 5                # 최대 5편
oopaper extend --source arxiv           # arXiv만
oopaper extend --source s2              # Semantic Scholar만
```

---

## 11. KISTI ScienceON 보고서 추출

> EN 가이드에 포함된 이유: KISTI는 영어 보고서·번역 보고서도 다수 제공 (TRKO* 시리즈).

### 11.1 URL 패턴

| 단계 | URL 패턴 |
|------|---------|
| 보고서 페이지 | `scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn={CN}` |
| 원문 뷰어 | `scienceon.kisti.re.kr/commons/util/originalView.do?cn={CN}&dbt=TRKO&rn=1` |
| PDF 다운로드 | `scienceon.kisti.re.kr/commons/util/orgDocDown.do?url={PDF_PATH}` |

### 11.2 추출 절차

```
1. 보고서 페이지 URL에서 cn 파라미터 추출
2. 원문 뷰어 URL 구성 → WebFetch로 HTML 분석
3. iframe 내부에서 /tr_img/YYYYNNN/rttrkoNNNNNN.pdf 경로 추출
4. PDF 다운로드 URL 조합 → curl/requests로 다운로드
5. {paper_root}/00_down/에 저장 → oopaper_auto organize 실행
```

### 11.3 적용 범위

| 적용 | 제한 |
|------|------|
| TRKO* 접두사 R&D 보고서 | 비공개·유료 보고서는 로그인 필요 |
| NTIS 연계 공개 보고서 | 본문 텍스트 추출 정확도는 PDF 품질에 의존 |

---

## 12. translator 에이전트 활용

### 12.1 호출 패턴

```bash
# 1. 번역 템플릿 생성
oopaper trans korean --folder {FOLDER_ID}

# 2. translator 에이전트 호출 (Claude Code)
"translator 에이전트로 03_paper/11_paper_en/{FOLDER_ID}/*_04_*_전문(한글).md 번역해줘"
```

### 12.2 에이전트 특성

| 특성 | 효과 |
|------|------|
| 학술 용어 일관성 | 용어집 기반 (도메인별 사전 자동 적용) |
| 수식·코드 블록 보존 | LaTeX·코드는 원문 유지 |
| 자연스러운 번역 | 번역투 제거 (직역 X) |
| 스테이지 라벨 | YAML frontmatter `stage: 1|2` 자동 갱신 |

### 12.3 2단계 프로세스 (Gemma + Claude)

| 단계 | 엔진 | stage | 라벨 |
|:---:|------|:---:|------|
| 1차 | Gemma (`gemma4:26b`) | 1 | `★ 1차 (Gemma 자동)` |
| 2차 | Claude | 2 | `★★ 2차 (Claude 검수 완료)` |

토큰 절감: 1차 무료, 2차만 부분 — Claude 토큰 ≈90% 절감 (813편 기준).

---

## 13. 분석 명령어 (anal)

### 13.1 옵션 매트릭스

| 옵션 | 동작 | 출력 |
|------|------|------|
| (옵션 없음) | 서베이 생성 | `15_paper_survey/d{SP}0110_survey_*.md` |
| `--add [폴더]` | 신규 논문 추가 → 기존 서베이 병합 | 기존 서베이 갱신 |
| `--compare` | 논문 간 비교 분석 | 별도 비교 문서 |
| `--deep` | 정밀 분석 | `*_05_*_분석.md` |
| `--topic "..."` | 연구 주제 오버라이드 | 키워드 매칭 재계산 |

### 13.2 deeprun 분석 항목

| 항목 | 설명 |
|------|------|
| 모델 아키텍처 | 레이어·파라미터 수·구조도 |
| 실험 설정 | 데이터셋·하이퍼파라미터·학습 전략 |
| 성능 수치 | IoU, F1, mAP 등 정량 |
| 핵심 수식 | Loss, 핵심 알고리즘 |
| Figure/Table | 주요 시각자료 분석 |
| 한계점 | 논문이 명시한 한계 |

---

## 14. 자주 발생하는 트러블 (FAQ)

| 증상 | 원인 | 조치 |
|------|------|------|
| paper_list에 80개 누락 | Phase 7 단방향 sync, 폴더 이동 후 update 미실행 | `oopaper update --lang en` |
| `260222-1851-08` 폴더 | multi-PDF 분리 시 suffix 부착 (구버전 동작) | `split-multi`로 신규 ID 재발급 |
| `01_00_*_서머리.md` | Phase 1 정규화 결함 (특정 시점 폴더) | `oopaper fix --auto-fix` |
| 한글 인코딩 깨짐 | `clean_name` 정규식 한계 | 수동 정정 후 `keyword-sync` |
| Phase 4 번역 stuck | Gemma 서버 미가동 | `--no-claude-review` 또는 `--claude-only` |
| download 후 paper_list 미반영 | 자동 sync 안 됨 | `oopaper update` 수동 실행 |

---

## 15. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/oopaper/SKILL.md` | 명령어·정책 단일 진실 공급원 |
| `references/guide.md` | 공통 코드 예시 (extend/backup/KISTI) |
| `references/guide_ko.md` | 한국어 보고서(KO) 처리 가이드 |
| `00_doc/sp03/d30001_prd.md` | SP03 PRD |
| `00_doc/sp03/d30004_todo.md` | SP03 이슈/과업 |
| `{paper_root}/11_paper_en/paper_list.md` | EN 목록 |
