---
name: ccpaper
description: "공통: `.codex/guides/common_guide.md` | 컨텍스트: `.agents/skills/cccontext/SKILL.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

> 공통: `.codex/guides/common_guide.md` | 컨텍스트: `.agents/skills/cccontext/SKILL.md`
> 한글 코드 예시: `references/guide.md` | EN 상세: `references/guide_en.md` | KO 상세: `references/guide_ko.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 학술 논문(EN)·국내 보고서(KO) 통합 문헌 관리 (수집·정규화·분류·번역·정합성) |
| **하는 것** | PDF 수집·폴더화, 영문 추출, 한글 번역, 서머리·참고문헌 생성, paper_list 동기화 |
| **하지 않는 것** | 논문 작성(→ccsota), 서베이(→ccsurvey), SOTA 연구(→ccresearch), 외부 일반 스크래핑(→ccscrap) |
| **참조 범위** | `{paper_root}/**` + 웹(논문 검색·확장 다운로드 시) |
| **수정 대상** | `{paper_root}/**/*.md`, `paper_list.md`, `12_paper_ko.md`, `00_doc/sp03/d30004_todo.md` |
| **실행 레벨** | [반자동] — Phase별 dry-run 후 적용 |
| **에이전트 호환** | Codex 권장 — academic-researcher / translator 서브에이전트 자동 위임 |

## 문서 이력 관리
- v08 2026-05-09 — 진단 반영 전면 재구조화: 폴더 ID 표준 strict화(suffix 금지 명시), 파일명 prefix 표준 표 신설, 1폴더 1논문 정책 강조, paper_list **양방향** 동기화 명시, `fix`/`doctor` 정의 재정의, multi-PDF 분리 절차 추가
- v07 2026-05-03 — Phase 순서 재변경(영문→**서머리**→한글). 상태 체계 X/E/**S**/**T**/O로 swap
- v06 2026-04-29 — 문서 템플릿 신설, 한글 번역 2단계(Gemma 1차 → Codex 검수)
- v05 2026-04-29 — `ccpaper_auto.py` 신설 (organize/dedup/meta/ref-match-fuzzy)
- v04 2026-04-29 — Phase 순서 변경, 5단계 상태 체계 도입
- v03 2026-04-18 — `--gemma` 플래그
- v02 2026-03-29 — extend 명령어 추가
- v01 2026-03-24 — 문서이력 섹션 추가

---

## 1. 개요

영어 논문(EN)과 한국어 보고서(KO)를 **분리 저장소**로 관리하는 통합 문헌 스킬.

### 1.1 paper_root 자동 감지

| 환경 | `{paper_root}` 결정 |
|------|--------------------|
| OAIS 워크스페이스 | `{project_root}/03_paper/` 가 존재하면 채택 |
| 독립 프로젝트 | 위 경로 부재 시 `{project_root}/` 직하 사용 |

### 1.2 데이터 경로

| lang | 입력 | 저장소 | 목록 파일 |
|------|------|--------|---------|
| `en` (기본) | `{paper_root}/00_down/` | `{paper_root}/11_paper_en/{FOLDER_ID}/` | `{paper_root}/11_paper_en/paper_list.md` |
| `ko` | `{paper_root}/00_down/` | `{paper_root}/12_paper_ko/{FOLDER_ID}/` | `{paper_root}/12_paper_ko.md` |

> ooreport와 구분: ccpaper = **수집/정리** (외부 → 내부), ccreport = **출력/생성** (내부 → 외부)

### 1.3 PRD/TODO 참조

- `00_doc/sp03/d30001_prd.md` — SP03 기능 요구사항
- `00_doc/sp03/d30004_todo.md` — SP03 이슈/과업

---

## 2. 폴더 ID 표준 (FOLDER_ID) ★

> **이 표준은 모든 명령어·스크립트·산출물에 강제 적용된다.**

### 2.1 형식

| 항목 | 규칙 |
|------|------|
| **정규식** | `^\d{6}-\d{4}$` — 정확히 10자 (`YYMMDD-HHMM`) |
| **YYMMDD** | 연·월·일 6자리 (00~99 / 01~12 / 01~31) |
| **HHMM** | 24시간제 시·분 4자리 (00~23 / 00~59) |
| **구분자** | 하이픈(`-`) 단 1개 |

### 2.2 발급 규칙

| 규칙 | 내용 |
|------|------|
| **출처 시각** | PDF 파일의 mtime(파일 수정 시각) → 부재 시 다운로드 시각 → 둘 다 부재 시 `datetime.now()` |
| **충돌 해결** | 같은 분에 N개 PDF 처리 시 분(minute)을 +1씩 증가하여 고유 ID 발급 |
| **재발급 금지** | 한번 발급된 FOLDER_ID는 변경하지 않는다 (renumbering 금지) |
| **수동 편집 금지** | 사용자가 폴더명을 직접 수정하면 paper_list 동기화가 깨짐 |

### 2.3 금지 패턴

| 패턴 | 사유 |
|------|------|
| `260222-1851-08` (suffix `-NN`) | **strict 10자 위반** — multi-PDF 분리는 신규 FOLDER_ID로 재발급 (§4) |
| `260222-185` / `260222-18510` | 자릿수 위반 |
| `26-02-22-1851` / `260222_1851` | 구분자 위반 |
| `DS01_260222-1851` / `IR07_*` | prefix 부착 금지 |
| 한글/특수문자 포함 | ASCII만 허용 |
| 미래일자(현재일+1일 초과) | 시계 오류 추정 → 폐기 |

### 2.4 검증

```bash
ccpaper doctor --check folder-id   # FOLDER_ID 위반 일괄 검증 (§13)
```

---

## 3. 파일명 prefix 표준 ★

> 한 폴더 안의 모든 산출물은 아래 prefix를 따라야 한다.

| Prefix | EN | KO | 패턴 | 비고 |
|:------:|:--:|:--:|------|------|
| `00` | O | O | `{FOLDER_ID}_00_{Title3}_서머리.md` | 서머리 + 키워드 + 참고문헌 |
| `01` | O | O | `{FOLDER_ID}_01_{Title3}.pdf` | 원본 PDF (필수, 1편만) |
| `03` | O | - | `{FOLDER_ID}_03_{Title3}_전문(영어).md` | 영문 전문 (References 포함) |
| `04` | O | O | `{FOLDER_ID}_04_{Title3}_전문(한글).md` | 한글 번역(EN) / 한글 직접 추출(KO) |
| `05` | O | O | `{FOLDER_ID}_05_{Title3}_분석.md` | `anal --deep` 산출물 |

### 3.1 {Title3} 규칙

- 논문 제목의 **첫 3단어**를 언더스코어로 연결 (영문 stopword 제거 권장)
- 정규화: `re.sub(r"[^\w\-가-힣().]+", "_", title)[:60].strip("_")`
- 예: `Deep Residual Learning for Image Recognition` → `Deep_Residual_Learning`

### 3.2 금지 패턴

| 패턴 | 사유 |
|------|------|
| `01_00_*_서머리.md` | prefix 순서 오류 (기대: `00_*_서머리.md`) |
| 한 폴더에 `_01_*.pdf` 2개 이상 | 1폴더 1논문 위반 (§4) |
| 정규화 안 된 PDF (`OG-RAG_Ontology....pdf`) | `{FOLDER_ID}_01_` 미적용 — Phase 0 재실행 필요 |
| 인코딩 깨진 한자/괄호 | 정규화 정규식 재처리 |

---

## 4. 1폴더 1논문 정책 ★

> **불변 원칙**: 한 `{FOLDER_ID}` 폴더에는 **PDF 1편**만 존재한다.

### 4.1 다중 PDF 처리 절차

| 상황 | 조치 |
|------|------|
| 한 폴더에 PDF 2개 이상 | `ccpaper split-multi --folder ID` 실행 → 첫 PDF는 그대로, 나머지는 **신규 FOLDER_ID 발급**하여 분리 |
| `DS01/IR07` 등 prefix 다른 PDF 묶음 | 각각 신규 FOLDER_ID로 분리 (suffix `-NN` 금지) |
| 폴더와 무관한 부속 파일 | `00_down/`로 회수 또는 삭제 |

### 4.2 split-multi 동작

1. 대상 폴더에서 `*_01_*.pdf` 파일 N개 식별
2. 첫 번째 PDF는 원래 폴더에 유지
3. 2~N번째 PDF는 mtime 기반 신규 FOLDER_ID 폴더로 이동
4. 이동 후 `ccpaper update` 호출하여 paper_list 동기화

> ⚠️ **금지**: `260222-1851-08`처럼 suffix 부착하여 분리 (§2.3 위반)

### 4.3 fix-suffix — 이미 만들어진 suffix 폴더 정규화

이미 `260222-1851-08` 같은 suffix 폴더가 존재할 때 (PDF 1개, 산출물 N개 보유):

| 단계 | 동작 |
|------|------|
| 1 | baseline prefix(`260222-1851`) 추출 |
| 2 | baseline 우선 발급 → 충돌 시 분 +1 (예: `260222-1852`, `260222-1853`) |
| 3 | 폴더 + 내부 산출물 prefix 일괄 rename |
| 4 | 정규화 안 된 PDF는 `{NEW_ID}_01_{Title3}.pdf` 형식으로 재명명 |
| 5 | `ccpaper update` 호출하여 paper_list 동기화 |

```bash
ccpaper fix-suffix --batch --dry-run     # 모든 suffix 폴더 일괄 (계획만)
ccpaper fix-suffix --batch                # 적용
ccpaper fix-suffix --folder 260222-1851-08  # 특정 폴더만
ccpaper fix-suffix --batch --use-mtime    # baseline 대신 mtime 기반 (예외)
```

---

## 5. 5단계 상태 체계 (X/E/S/T/O)

| 상태 | EN | KO | 의미 | 판정 조건 |
|:----:|:--:|:--:|------|----------|
| X | O | O | 미처리 | PDF만 존재 |
| E | O | - | 영문 전문 추출 완료 | `*_03_*_전문(영어).md` 품질 OK (≥1000B) |
| S | O | O | 서머리 완료 | `*_00_*_서머리.md` 품질 OK (≥500B) — 영문 기반, 한글 출력 |
| T | O | - | 한글 번역 완료 | `*_04_*_전문(한글).md` 품질 OK (≥1000B) |
| O | O | - | 완료 | 모든 산출물 + 참고문헌 내부매칭 완료 |

> **상태 진행**: X → E → S → T → O. KO는 X/S 2단계.

---

## 6. 명령어

| 명령어 | EN | KO | 설명 |
|--------|:--:|:--:|------|
| `ccpaper help` | O | O | 서브명령어 목록 |
| `ccpaper version` | O | O | 스킬 버전 (v08) |
| `ccpaper status` | O | O | 폴더 현황·상태 통계 |
| `ccpaper check` | O | O | `references/checklist.md` 기반 자체 점검 |
| `ccpaper run [--lang]` | O | O | **통합 자동 파이프라인** (§7~§8) |
| `ccpaper update [--lang] [--dry-run]` | O | O | **현행화** — paper_list 양방향 sync (§9) |
| `ccpaper run this` | O | O | 직전 논문 계속 처리 |
| `ccpaper anal [--deep] [--folder]` | O | O | 분석 — 서베이/정밀 (§10) |
| `ccpaper trans [english\|korean]` | O | O | 텍스트 추출/번역 (§11) |
| `ccpaper compress` | O | O | PDF 압축 (텍스트 보존) |
| `ccpaper search` | O | - | 논문 검색 (arXiv, S2) |
| `ccpaper download [--dry-run]` | O | - | 리스트 기반 PDF 자동 다운로드 |
| `ccpaper extend [--folder] [--limit]` | O | - | 서머리 외부 참고문헌 → 자동 다운로드 (§12) |
| `ccpaper ref` | O | - | 인용 검증·정규화 |
| `ccpaper net` | O | - | 인용 네트워크 분석 |
| `ccpaper keyword-sync` | O | - | 키워드 동기화 (서머리 → paper_list) |
| `ccpaper ref-match` | O | - | 참고문헌 내부 매칭 |
| `ccpaper fix [--folder] [--auto-fix]` | O | O | **정합성 검사·수정** (§13) — EN/KO 통합 |
| `ccpaper doctor [--check NAME]` | O | O | **종합 진단** — folder-id, file-name, multi-pdf, sync, orphan (§13) |
| `ccpaper split-multi --folder ID` | O | O | **다중 PDF 분리** — 신규 FOLDER_ID 발급 (§4) |
| `ccpaper fix-suffix [--folder\|--batch]` | O | O | **suffix 폴더(`-NN`) 정규화** — baseline prefix 보존 rename (§4.3) |
| `ccpaper backup [--dry-run]` | O | O | PDF 외부 경로 백업 |
| `ccpaper restore [--dry-run]` | O | O | 백업 PDF 복원 |
| **자동화 (oopaper_auto.py)** | | | |
| `ccpaper_auto organize [--dry-run]` | O | - | 00_down → FOLDER_ID 자동 정리 (Phase 0) |
| `ccpaper_auto dedup [--fuzzy]` | O | - | 폴더 간 중복 검출 |
| `ccpaper_auto meta [--folder] [--limit]` | O | - | PDF 메타데이터 추출 |
| `ccpaper_auto ref-match-fuzzy` | O | - | rapidfuzz 기반 참고문헌 매칭 |

### 6.1 실행 분기

| --lang | 진입 스크립트 |
|--------|--------------|
| `en` (기본) | `uv run python .agents/skills/ccpaper/scripts/oopaper_run.py [subcommand]` |
| `ko` | `uv run python .agents/skills/ccpaper/scripts/ooessay_run.py [subcommand]` |
| `backup`/`restore` | `uv run python .agents/skills/ccpaper/scripts/oopaper_backup.py [subcommand]` |

---

## 7. run 명령어 — EN 8 Phase

```
Phase 0: 00_down → 11_paper_en 이동 + 파일명 정규화 (FOLDER_ID 발급)
Phase 1: 스캔 → 미완료 논문 + 5단계 상태 (X/E/S/T/O)
Phase 2: 영문 전문 추출 (AI)              → *_03_*_전문(영어).md
Phase 3: 서머리 생성 (영문 기반, 한글 출력)  → *_00_*_서머리.md
Phase 4: 한글 번역 (translator/Gemma)      → *_04_*_전문(한글).md
Phase 5: 참고문헌 추출 + 내부 매칭
Phase 6: 정밀 분석 (anal --deep 동일)       → *_05_*_분석.md
Phase 7: paper_list.md 양방향 동기화 (§9)
```

> v07 변경 사유: 영문 전문에서 직접 한글 서머리를 생성한 뒤 한글 번역 진행. 번역 미완에서도 서머리 생성 가능 → Gemma 의존 감소.

## 8. run 명령어 — KO 4 Phase

```
Phase 0: 00_down 스캔 → 한국어 보고서 PDF 식별
Phase 1: 12_paper_ko/FOLDER_ID/ 폴더 생성 → PDF 이동
Phase 2: 서머리 생성 → *_00_*_서머리.md
Phase 3: 한글 전문 추출 → *_04_*_전문(한글).md
Phase 4: 12_paper_ko.md 헤더·항목 양방향 동기화
```

### 8.1 공통 옵션

| 옵션 | 설명 |
|------|------|
| `--lang en\|ko` | 언어 지정 (기본: en) |
| `--limit N` | 처리할 최대 문헌 수 |
| `--folder ID` | 특정 폴더만 처리 |
| `--dry-run` | 실행 없이 계획만 출력 |
| `--phase N` | 특정 Phase만 (EN 전용) |
| `--skip-organize` | Phase 0 건너뛰기 (EN 전용) |
| `--gemma` | Phase 3 서머리·Phase 4 번역 초안을 Gemma 위임 (§15) |

---

## 9. paper_list 양방향 동기화 (`update`)

> Phase 7 및 `ccpaper update`는 **양방향 검증**을 수행한다.

| 방향 | 검증 |
|------|------|
| **폴더 → 리스트** | 실제 폴더에 있으나 `paper_list.md`에 없는 항목 → **append** |
| **리스트 → 폴더** | `paper_list.md`에 있으나 실제 폴더 없음 → **고아(orphan)로 마킹** (`[DELETED]` 태그) |
| **헤더 카운트** | 리스트의 "총 N편" 헤더 자동 갱신 (EN: `paper_list.md`, KO: `12_paper_ko.md`) |
| **상태 컬럼** | X/E/S/T/O 갱신 |

### 9.1 단독 download / extend 직후

```bash
ccpaper update --lang en --dry-run    # 변경 예정 확인
ccpaper update --lang en              # 적용
```

> ⚠️ `download`·`extend` 직후 자동 sync 안 됨 — 반드시 `update` 수동 실행. (`run`은 Phase 7에서 자동 호출)

---

## 10. anal 명령어

| 옵션 | EN | KO | 설명 |
|------|:--:|:--:|------|
| `--compare` | O | - | 논문 간 비교 분석 |
| `--add [폴더]` | O | - | 신규 논문 추가 → 기존 서베이 병합 |
| `--deep` | O | O | 정밀 분석 → `*_05_*_분석.md` |
| `--topic` | O | - | 연구 주제 오버라이드 |
| `--folder ID` | - | O | 특정 폴더만 분석 |
| `--force` | - | O | 기존 분석 덮어쓰기 |

서베이 저장: `{paper_root}/15_paper_survey/`

---

## 11. trans 명령어

### 11.1 EN
- `english`: PDF → `*_03_*_전문(영어).md`
- `korean`: 영문 → `*_04_*_전문(한글).md` (translator 에이전트)

### 11.2 KO
- PDF → `*_04_*_전문(한글).md` (한글 직접 추출)
- 옵션: `--folder ID`, `--force`

---

## 12. extend 명령어 (EN 전용)

서머리의 `### 외부` 참고문헌을 스캔 → 미보유 논문 자동 검색·다운로드.

| 옵션 | 설명 |
|------|------|
| `--folder ID` | 특정 폴더만 처리 |
| `--dry-run` | 검색만, 다운로드 생략 |
| `--limit N` | 최대 다운로드 수 (기본: 10) |
| `--source all\|arxiv\|s2` | 검색 소스 (기본: all) |

처리 흐름: 서머리 파싱 → 중복 제거 → arXiv/S2 검색 → `00_down/` 저장 → **`ccpaper update` 수동 실행**

---

## 13. fix · doctor — 정합성 검사 ★

> v08에서 재정의: `fix`는 EN/KO 모두 적용. `doctor`는 종합 진단(읽기 전용).

### 13.1 doctor 체크 항목

| 체크 (`--check`) | 내용 | 심각도 |
|-----------------|------|--------|
| `folder-id` | §2 표준 위반 폴더 (suffix·자릿수 등) | ERROR |
| `file-name` | §3 prefix 위반 / `{Title3}` 깨짐 | WARNING |
| `multi-pdf` | 한 폴더 PDF 2개 이상 | ERROR |
| `sync` | paper_list ↔ 실제 폴더 차이 | WARNING |
| `orphan` | paper_list에만 등재, 폴더 없음 | WARNING |
| `quality` | 산출물 품질 미달 (서머리 <500B / 영문·한글 <1000B / 미완료 마커 포함) | INFO |

### 13.2 fix 옵션

| 옵션 | 설명 |
|------|------|
| `--check-only` | 검사만 (수정 없음) |
| `--auto-fix` | 자동 수정 가능한 항목만 적용 (파일명 prefix·헤더 카운트) |
| `--folder ID` | 특정 폴더만 |
| `--lang en\|ko` | 언어 지정 |

> ID 위반·multi-PDF는 `split-multi` 수동 실행 필요 (자동 수정 X — 데이터 손실 위험)

---

## 14. backup / restore

PDF를 외부 경로로 이동·복원. 대상: `11_paper_en/`, `12_paper_ko/` (`00_down/` 제외).

설정 파일: `{paper_root}/backup_config.json` (호스트별, git ignore 권장)

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 대상만 출력 |
| `--folder ID` | 특정 폴더만 |
| `--subdir DIR` | 특정 하위 폴더만 (예: `11_paper_en`) |

> 코드 예시: `references/guide.md §6`

---

## 15. 한글 번역 2단계 (v06+)

```
trans korean
├─ 1차 (Gemma)
│  ├─ 가용 → 자동 (stage=1, v1_engine=gemma4:26b)
│  └─ 미가용 → 사용자 확인 ("Codex 단독? y/n")
└─ 2차 (Codex 검수, 옵션 기본 활성)
   └─ Gemma 결과 + 영문 원문 → 검수 (stage=2, v2_engine=codex-*)
```

| 플래그 | 설명 |
|--------|------|
| `--no-codex-review` | Gemma만 (1차에서 멈춤) |
| `--codex-only` | Gemma 건너뛰기 |
| `--stage 1\|2` | 특정 단계만 |

> 토큰 절감: 813편 처리 시 1차 Gemma → Codex 검수만 부분 → Codex 토큰 ≈90% 절감

---

## 16. KISTI ScienceON 보고서 PDF 추출

> KISTI(`scienceon.kisti.re.kr`) 보고서는 직접 PDF URL 미노출. 추출 절차는 `references/guide.md §7` 참조.

> **적용**: KISTI R&D 보고서 (`TRKO*`), NTIS 연계 / **제한**: 비공개·유료 보고서는 로그인 필요

---

## 17. 파일 구조 (요약)

### EN
```
{paper_root}/11_paper_en/
├─ paper_list.md                    # 전체 목록 (헤더 카운트 + 상태 컬럼)
├─ {FOLDER_ID}/                     # 1폴더 1논문
│  ├─ {FOLDER_ID}_00_{Title3}_서머리.md
│  ├─ {FOLDER_ID}_01_{Title3}.pdf
│  ├─ {FOLDER_ID}_03_{Title3}_전문(영어).md
│  ├─ {FOLDER_ID}_04_{Title3}_전문(한글).md
│  └─ {FOLDER_ID}_05_{Title3}_분석.md
└─ ...
```

### KO
```
{paper_root}/12_paper_ko/
└─ {FOLDER_ID}/
   ├─ {FOLDER_ID}_00_{Title3}_서머리.md
   ├─ {FOLDER_ID}_01_{Title3}.pdf
   ├─ {FOLDER_ID}_04_{Title3}_전문(한글).md
   └─ {FOLDER_ID}_05_{Title3}_분석.md
{paper_root}/12_paper_ko.md          # 헤더 + 항목 목록
```

---

## 18. 서브에이전트 매핑

| 작업 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 논문 검색 | `academic-researcher` | sonnet | O |
| 서머리 분석 | `academic-researcher` | sonnet | O |
| 영문 추출 | `data-analyst` | sonnet | O |
| 한글 번역 | `translator` | haiku | O |
| 참고문헌 매칭 | `academic-researcher` | sonnet | O |
| 문서 생성 | `task-executor` | sonnet | - |
| 정합성 검증 | `task-checker` | sonnet | - |

---

## 19. 스크립트 참조

### EN
| 스크립트 | 용도 |
|---------|------|
| `ccpaper_run.py` | 통합 실행, 상태, sync(양방향), fix, download, doctor/split-multi/fix-suffix 라우팅 |
| `ccpaper_doctor.py` | 종합 정합성 진단 6종 (folder-id/file-name/multi-pdf/sync/orphan/quality) |
| `ccpaper_split_multi.py` | 다중 PDF 폴더 분리 (1폴더 1논문 정책) |
| `ccpaper_fix_suffix.py` | suffix 폴더(`-NN`) 정규화 |
| `ccpaper_auto.py` | organize / dedup / meta / ref-match-fuzzy |
| `ccpaper_trans.py` | PDF 텍스트 추출, 한글 번역 템플릿 |
| `ccpaper_extend.py` | 서머리 → 외부 참고문헌 자동 다운로드 |
| `ccpaper_pdf_compress.py` | PDF 압축 (EN/KO 공유) |
| `ccpaper_cite_*.py` | 인용 검증·정규화·매핑·정리 |
| `ccpaper_backup.py` | PDF 백업·복원 (EN/KO 공통) |

### KO
| 스크립트 | 용도 |
|---------|------|
| `ccessay_run.py` | 통합 실행, 상태, 무결성, 텍스트 추출, 정밀 분석 |

---

## 20. 문서 템플릿 (`templates/`)

| 파일 | 용도 |
|------|------|
| `templates/summary.md` | 서머리 (`*_00_*_서머리.md`) |
| `templates/translation_english.md` | 영문 전문 (`*_03_*_전문(영어).md`) |
| `templates/translation_korean.md` | 한글 번역 (`*_04_*_전문(한글).md`) — YAML frontmatter로 단계 추적 |

---

> **관련 문서**: `00_doc/sp03/d30001_prd.md` | `00_doc/sp03/d30004_todo.md` | `{paper_root}/11_paper_en/paper_list.md` | `{paper_root}/12_paper_ko.md`

> **사용 예시 / 코드 패턴**: `references/guide.md`

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

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
| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.agents/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->
