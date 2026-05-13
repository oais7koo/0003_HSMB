# oopaper 공통 가이드 — 코드 예시·실행 패턴

> 진입점: `.claude/skills/oopaper/SKILL.md` | EN 상세: `guide_en.md` | KO 상세: `guide_ko.md`

## 문서 이력 관리
- v03 2026-05-09 — SKILL.md v08 동기화. 폴더 ID·파일명 표준 검증 예시, doctor/fix/split-multi 코드 패턴, 양방향 sync 절차 추가
- v02 2026-04-21 — extend/backup/KISTI 상세 패턴 통합
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

이 문서는 SKILL.md에서 `references/guide.md §N 참조`로 위임된 **코드 예시·실행 cheatsheet** 모음이다.
정책·표준은 SKILL.md, 언어별 상세는 `guide_en.md` / `guide_ko.md`에 있다.

---

## 2. 기본 사용법 (cheatsheet)

### 2.1 EN (영어 논문)

```bash
oopaper status                          # 현황·상태 통계
oopaper run                             # 8 Phase 전체 파이프라인
oopaper run --folder 260509-1423        # 특정 폴더만
oopaper run --phase 2                   # Phase 2(영문 추출)만
oopaper run --skip-organize             # Phase 0 스킵
oopaper run --gemma                     # Gemma 위임 (Phase 3·4)
oopaper search "crack detection CNN"    # 논문 검색
oopaper extend                          # 외부 참고문헌 자동 다운로드
oopaper anal --deep --folder 260509-1423  # 정밀 분석
oopaper update --lang en --dry-run      # paper_list 동기화 미리보기
```

### 2.2 KO (한국어 보고서)

```bash
oopaper status --lang ko
oopaper run --lang ko
oopaper anal --lang ko --deep
oopaper fix --lang ko --check-only
oopaper update --lang ko
```

### 2.3 정합성 점검

```bash
oopaper check                           # 자체 헬스체크 (checklist.md)
oopaper doctor --check folder-id        # ID 표준 위반
oopaper doctor --check multi-pdf        # 1폴더 1논문 위반
oopaper doctor --check sync             # paper_list 동기화 차이
oopaper doctor --check orphan           # 고아 항목
oopaper doctor --check quality          # 산출물 품질 미달
oopaper fix --auto-fix                  # 자동 수정 가능 항목 적용
```

### 2.4 PDF 압축

```bash
oopaper compress --lang en
oopaper compress --lang ko
```

---

## 3. 폴더 ID·파일명 표준 검증 예시

### 3.1 위반 폴더 일괄 탐지

```bash
# strict 정규식: ^\d{6}-\d{4}$ (10자) 위반 폴더
oopaper doctor --check folder-id

# 출력 예 (의사):
# [ERROR] 260222-1851-08  : suffix 부착 위반 (split-multi 필요)
# [ERROR] 260222-185      : 자릿수 부족
# [ERROR] DS01_260222-1851: prefix 부착
```

### 3.2 파일명 prefix 위반

```bash
oopaper doctor --check file-name

# 출력 예:
# [WARN] 250214-1415: 01_00_*_서머리.md → 00_*_서머리.md 로 정정 필요
# [WARN] 250214-1415: PDF prefix 미적용 (Abstract...pdf → 250214-1415_01_*.pdf)
```

### 3.3 자동 수정

```bash
oopaper fix --auto-fix --folder 250214-1415
# 안전 항목만 자동: 파일명 prefix·헤더 카운트
# multi-PDF·suffix 폴더는 자동 X (split-multi 또는 수동 처리)
```

---

## 4. multi-PDF 분리 (split-multi)

### 4.1 단계별 절차

```bash
# Step 1: 위반 폴더 탐지
oopaper doctor --check multi-pdf
# [ERROR] 260222-1851: PDF 4개 (OG-RAG, OntoRAG, ...)

# Step 2: 분리 계획 미리보기
oopaper split-multi --folder 260222-1851 --dry-run
# Plan:
#   260222-1851 : OG-RAG... (유지)
#   260222-1852 : OntoRAG... (신규 발급, mtime 기반)
#   260222-1853 : KG-RAG... (신규 발급)
#   260222-1854 : Vision-RAG... (신규 발급)

# Step 3: 적용
oopaper split-multi --folder 260222-1851

# Step 4: 신규 폴더에 산출물 생성
oopaper run --folder 260222-1852
oopaper run --folder 260222-1853
oopaper run --folder 260222-1854

# Step 5: paper_list 동기화
oopaper update --lang en
```

### 4.2 suffix 폴더(`-NN`) 정리

이미 `260222-1851-08`처럼 suffix가 붙어버린 폴더는 다음 절차로 정상화:

```bash
# 임시 디렉토리로 PDF 회수
mkdir 03_paper/00_down/_recover_260222
mv 03_paper/11_paper_en/260222-1851-*/[!2]*_01_*.pdf 03_paper/00_down/_recover_260222/
# (또는 정규화 안 된 PDF: *.pdf 중 prefix 미적용 파일)

# suffix 폴더 잔여 산출물 보관
mv 03_paper/11_paper_en/260222-1851-* 03_paper/_attic/

# 회수 PDF를 정상 경로로 organize
oopaper_auto organize --dry-run
oopaper_auto organize

# paper_list 동기화 (고아 마킹)
oopaper update --lang en
```

> ⚠️ `_attic/`은 임시 보관소 — 신규 폴더 검증 후 수동 정리.

---

## 5. extend 명령어 상세

### 5.1 전형적 사용

```bash
oopaper extend                          # 전체 → 최대 10편
oopaper extend --dry-run                # 검색만
oopaper extend --folder 260301-1001     # 특정 폴더
oopaper extend --limit 5                # 최대 5편
oopaper extend --source arxiv           # arXiv만
oopaper extend --source s2              # Semantic Scholar만
```

### 5.2 스크립트 직접 실행

```bash
uv run python .claude/skills/oopaper/scripts/oopaper_extend.py --dry-run --limit 3
```

### 5.3 사후 동기화 (필수)

```bash
oopaper_auto organize             # 새 PDF를 11_paper_en으로 이동
oopaper update --lang en          # paper_list 양방향 sync
```

---

## 6. backup / restore 상세

### 6.1 설정 파일 (`backup_config.json`)

호스트별로 다름. git ignore 권장.

```json
{
  "backup_dir": "C:/Users/oaiskoo/doom/7_box/03_paper",
  "hostname": "oaiskoo"
}
```

### 6.2 설정 초기화

```bash
uv run python .claude/skills/oopaper/scripts/oopaper_backup.py config \
  --path "C:/Users/oaiskoo/doom/7_box/03_paper"
```

### 6.3 일상 사용

```bash
oopaper backup --dry-run                # 대상 확인
oopaper backup                          # 전체 PDF 백업
oopaper backup --folder 260222-1921     # 특정 폴더만
oopaper backup --subdir 11_paper_en     # EN만

oopaper restore --dry-run               # 복원 대상 확인
oopaper restore                         # 전체 PDF 복원

uv run python .claude/skills/oopaper/scripts/oopaper_backup.py status   # 현황
```

---

## 7. KISTI ScienceON 보고서 PDF 추출

### 7.1 URL 패턴

| 단계 | 패턴 |
|------|------|
| 보고서 페이지 | `scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn={CN}` |
| 원문 뷰어 | `scienceon.kisti.re.kr/commons/util/originalView.do?cn={CN}&dbt=TRKO&rn=1` |
| PDF 다운로드 | `scienceon.kisti.re.kr/commons/util/orgDocDown.do?url={PDF_PATH}` |

### 7.2 추출 절차

```
1. 보고서 페이지 URL 확인
   https://scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn=TRKO201900017765

2. 원문보기 URL 구성
   https://scienceon.kisti.re.kr/commons/util/originalView.do?cn=TRKO201900017765&dbt=TRKO&rn=1

3. WebFetch로 원문 페이지 HTML 분석
   → iframe 내부에 실제 PDF 경로:
   /commons/util/orgDocDown.do?url=/tr_img/2019017/rttrko000000315524.pdf

4. PDF 다운로드 URL 조합 후 다운로드
   https://scienceon.kisti.re.kr/commons/util/orgDocDown.do?url=/tr_img/2019017/rttrko000000315524.pdf
   → {paper_root}/00_down/ 저장

5. 후속 처리
   oopaper_auto organize          # 폴더화
   oopaper run --lang ko          # KO 파이프라인
```

### 7.3 자동화 스니펫 (의사코드)

```python
# WebFetch로 원문 뷰어 페이지 HTML 가져오기
html = WebFetch(viewer_url, "find iframe with /commons/util/orgDocDown.do path")

# iframe src 추출 (예: /commons/util/orgDocDown.do?url=/tr_img/.../rttrkoNNNNNN.pdf)
pdf_url = "https://scienceon.kisti.re.kr" + extract_iframe_src(html)

# requests/curl로 다운로드 (로그인 불필요, 공개 보고서 한정)
download(pdf_url, target=f"{paper_root}/00_down/{report_id}.pdf")
```

> **적용**: TRKO* / NTIS 연계 공개 보고서. **제한**: 비공개·유료 보고서는 로그인 필요.

---

## 8. fix 명령어 상세

### 8.1 EN/KO 통합 (v08+)

```bash
oopaper fix --check-only                    # 검사만
oopaper fix --auto-fix                      # 자동 수정 항목 적용
oopaper fix --folder 250214-1415            # 특정 폴더
oopaper fix --lang ko --auto-fix            # KO 전용 자동 수정
```

### 8.2 자동 수정 가능 항목

| 항목 | 수정 동작 |
|------|----------|
| 파일명 prefix 순서 (`01_00_*` → `00_*`) | rename |
| `paper_list.md` 헤더 카운트 | 항목 수에 맞춰 갱신 |
| `12_paper_ko.md` 헤더 카운트 | 폴더 수에 맞춰 갱신 |
| `{Title3}` 인코딩 깨짐 | 정규식 재적용 (`re.sub(r"[^\w\-가-힣().]+", "_", ...)`) |
| 미동기화 키워드 | `keyword-sync` 호출 |

### 8.3 자동 수정 불가 (수동)

| 항목 | 권장 절차 |
|------|----------|
| FOLDER_ID 표준 위반 | `split-multi` 또는 폴더 재배치 |
| multi-PDF | `split-multi` 명시 실행 |
| 고아 항목 (`[DELETED]`) | 사용자가 백업 확인 후 paper_list 정리 |
| 품질 미달 산출물 | 해당 Phase 재실행 (예: `run --phase 2 --folder ID`) |

---

## 9. doctor — 종합 진단 (읽기 전용)

### 9.1 체크 종류

```bash
oopaper doctor                              # 모든 체크 일괄
oopaper doctor --check folder-id            # ID 표준
oopaper doctor --check file-name            # 파일명 prefix
oopaper doctor --check multi-pdf            # 1폴더 1논문
oopaper doctor --check sync                 # paper_list 동기화
oopaper doctor --check orphan               # 고아 항목
oopaper doctor --check quality              # 산출물 품질
```

### 9.2 출력 형식

```
[oopaper doctor]

폴더 ID 표준 (folder-id) ........... [ERROR] 4건
  - 260222-1851-08 : suffix 부착 위반
  - 260222-1851-09 : suffix 부착 위반
  - ...

파일명 prefix (file-name) .......... [WARN] 5건
  - 250214-1415 : 01_00_*_서머리.md → 00_*_서머리.md
  - ...

1폴더 1논문 (multi-pdf) ............ [OK]
paper_list 동기화 (sync) ........... [WARN] 80건 (폴더 부재)
고아 항목 (orphan) ................. [WARN] 80건
산출물 품질 (quality) .............. [INFO] 12건 (품질 미달)

소계: OK:1 | WARN:3 | ERROR:1
```

---

## 10. 한글 번역 2단계 (Gemma + Claude)

### 10.1 자동 흐름 (`run --gemma` 또는 `trans korean`)

```
1. Gemma 가용성 체크
   ├─ OK   → Gemma 1차 번역 (stage=1, v1_engine=gemma4:26b)
   └─ FAIL → 사용자 확인 ("Claude 단독? y/n")
2. Claude 검수 (옵션 기본 활성)
   └─ Gemma 결과 + 영문 원문 입력 → 검수 (stage=2, v2_engine=claude-*)
3. 결과 파일에 YAML frontmatter로 단계 기록
```

### 10.2 플래그

```bash
oopaper trans korean --no-claude-review     # Gemma만 (1차에서 멈춤, 일괄 처리용)
oopaper trans korean --claude-only          # Gemma 건너뛰기 (Claude 직접)
oopaper trans korean --stage 1              # 1차만
oopaper trans korean --stage 2              # 2차만 (1차 산출물 필요)
```

### 10.3 토큰 절감 효과

| 시나리오 | Claude 토큰 | 비고 |
|---------|:----------:|------|
| Claude 단독 (`--claude-only`) | 100% | 기준 |
| 2단계 (Gemma 1차 + Claude 검수) | ≈10% | 813편 기준 약 90% 절감 |
| Gemma만 (`--no-claude-review`) | 0% | 검수 없음 (품질 ★ 1차) |

---

## 11. 인용 출력 형식

### 11.1 BibTeX

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

### 11.2 APA

Chen, W., & Zhang, L. (2024). Deep Learning for Crack Detection. *Pattern Recognition*, 89, 1-15.

### 11.3 IEEE

W. Chen and L. Zhang, "Deep Learning for Crack Detection," *Pattern Recognition*, vol. 89, pp. 1-15, 2024.

---

## 12. 주의사항 / 운영 규칙

| 규칙 | 설명 |
|------|------|
| SP 컨텍스트 | EN(SP03) / KO(SP03) 모두 SP03 ─ `oocontext 3` 권장 |
| 단독 download/extend 후 sync | 반드시 `oopaper update` 수동 실행 |
| backup 전 검증 | `oopaper doctor` 통과 후 백업 권장 |
| Phase별 dry-run | 첫 실행은 항상 `--dry-run`으로 계획 확인 |
| FOLDER_ID 직접 편집 금지 | paper_list 동기화가 깨짐 |
| `_attic/` 임시 보관 | suffix 폴더 정리 시 사용 후 수동 검증 |

---

## 13. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/oopaper/SKILL.md` | 명령어·정책 단일 진실 공급원 |
| `references/guide_en.md` | 영어 논문(EN) 처리 상세 |
| `references/guide_ko.md` | 한국어 보고서(KO) 처리 상세 |
| `references/checklist.md` | `oopaper check` 체크리스트 |
| `templates/summary.md` | 서머리 템플릿 |
| `templates/translation_english.md` | 영문 전문 템플릿 |
| `templates/translation_korean.md` | 한글 번역 템플릿 (stage frontmatter) |
| `00_doc/sp03/d30001_prd.md` | SP03 PRD |
| `00_doc/sp03/d30004_todo.md` | SP03 이슈/과업 |
