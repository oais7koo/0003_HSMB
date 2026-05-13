---
name: oopaper
description: "통합 문헌 관리 스킬 'oopaper', '논문 관리', '문헌 관리', '학술 논문', '국내 보고서', '논문 수집' 등을 요청할 때 트리거된다"
metadata:
  version: "v02"
  category: "content"
  replaces: ["oopaper (v41)", "ooessay (v05)"]
---

> 공통: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`
> 영어 가이드: `.claude/skills/oopaper/references/guide_en.md` | 검색: academic-researcher 에이전트

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 학술 논문·국내 보고서 통합 문헌 관리 (수집·분류·분석·번역) |
| **하는 것** | 논문 수집, 분류 정리, 영문 전문·한글 번역 생성, {paper_root}/ 관리 |
| **하지 않는 것** | 논문 작성(→oosota), 서베이 생성(→oosurvey), 연구 수행(→ooresearch) |
| **참조 범위** | 현재 프로젝트 `{paper_root}/` + 웹 검색(논문 수집 시) |
| **수정 대상** | `{paper_root}/**/*.md`, `d30004_todo.md` |
| **실행 레벨** | [반자동] — 수집 대상 확인 후 실행 |
| **에이전트 호환** | Claude Code 권장 — academic-researcher 서브에이전트 자동 배치 / 다른 에이전트: 웹 검색 후 수동으로 파일 생성 |

## 문서 이력 관리
- v07 2026-05-03 — Phase 순서 재변경(영문 → **서머리(영문 기반, 한글 출력)** → 한글 번역). 상태 체계 X/E/**S**/**T**/O로 swap. 서머리 기반 데이터: 한글 전문 → 영문 전문. 번역 미완 상태에서도 서머리 생성 가능.
- v06 2026-04-29 — 문서 템플릿 신설(`templates/summary.md`, `translation_english.md`, `translation_korean.md`). 한글 번역 2단계 프로세스 정의(1차 Gemma → 2차 Claude 검수, YAML frontmatter로 단계 추적).
- v05 2026-04-29 — oopaper_auto.py 신설: organize/dedup/meta/ref-match-fuzzy 자동화 명령 추가. Phase 0·5 토큰 절감. sync-list 헤더 카운트 자동 갱신, run 명령에 Phase 7 자동 sync 통합.
- v04 2026-04-29 — Phase 순서 변경: 영문 전문 추출 → 한글 번역 → 서머리 생성. 5단계 상태 체계(X/E/T/S/O)로 확장. 한글 전문 기반 서머리로 정확도 향상.
- v03 2026-04-18 — `--gemma` 플래그 추가 — Phase 2 서머리·Phase 4 번역 초안을 로컬 Gemma에 위임 (경계: `.claude/guides/gemma_delegation.md`)
- v02 2026-03-29 — extend 명령어 추가, Phase 5 참고문헌 템플릿 DOI/arXiv 컬럼 강화
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 개요

영어 논문(EN)과 한국어 보고서(KO)를 통합 관리하는 문헌 수집 스킬.

> **`{paper_root}` 표기**: 스크립트가 자동 감지
> - `03_paper/` 폴더가 있으면 `{project_root}/03_paper/` (OAIS 레거시 호환)
> - 없으면 `{project_root}/` (독립 프로젝트: 03_paper)

- `--lang en` (기본값): 영어 논문 → `{paper_root}/11_paper_en/`
- `--lang ko`: 한국어 보고서 → `{paper_root}/12_paper_ko/`

> **ooreport와의 구분**: oopaper는 **수집/정리** (외부 → 내부), ooreport는 **생성/출력** (내부 → 외부)

### 1.1 데이터 경로

| lang | 입력 (다운로드) | 저장소 | 목록 |
|------|----------------|--------|------|
| `en` | `{paper_root}/00_down/` | `{paper_root}/11_paper_en/YYMMDD-HHMM/` | `{paper_root}/11_paper_en/paper_list.md` |
| `ko` | `{paper_root}/00_down/` | `{paper_root}/12_paper_ko/YYMMDD-HHMM/` | `{paper_root}/12_paper_ko.md` |

### 1.2 PRD/TODO 참조

| 문서 | 용도 |
|------|------|
| `00_doc/sp00/d0001_prd.md` | SP03 PRD (기능 요구사항) |
| `00_doc/sp00/d0004_todo.md` | SP03 이슈/과업 관리 |

## 2. 명령어

| 명령어 | EN | KO | 설명 |
|--------|:--:|:--:|------|
| `oopaper help` | O | O | 서브명령어 목록 표시 |
| `oopaper version` | O | O | 스킬 버전 정보 (v01) |
| `oopaper status` | O | O | 서브명령어 리스트, 폴더 현황, 상태 통계 |
| `oopaper check` | O | O | references/checklist.md 기반 체크 및 리포팅 |
| `oopaper show checklist` | O | O | 역할 수행 체크리스트 표시 |
| `oopaper add checklist "항목"` | O | O | 체크리스트 항목 추가 |
| `oopaper run [--lang]` | O | O | **통합 자동 파이프라인** |
| `oopaper update [--lang]` | O | O | 현행화 — 논문 목록 재스캔 → 메타데이터 갱신 |
| `oopaper update --dry-run` | O | O | 변경 예정 내용 미리 출력 (실제 수정 안 함) |
| **`oopaper run this`** | O | O | **직전 논문 계속** (→ common_guide.md §9) |
| `oopaper anal [--lang]` | O | O | **분석**: 서베이 생성 또는 정밀 분석 |
| `oopaper trans [--lang]` | O | O | **텍스트 추출/번역** |
| `oopaper compress [--lang]` | O | O | **PDF 압축** |
| `oopaper search` | O | - | **논문 검색** (arXiv, Semantic Scholar 등) |
| `oopaper download` | O | - | **PDF 자동 다운로드** (리스트 파일 기반) |
| `oopaper ref` | O | - | **인용 통합 관리** |
| `oopaper net` | O | - | **인용 네트워크 분석** |
| `oopaper keyword-sync` | O | - | **키워드 동기화** (서머리 → paper_list) |
| `oopaper ref-match` | O | - | **참고문헌 내부 매칭** |
| `oopaper fix` | - | O | **무결성 검사/수정** |
| `oopaper extend [--folder] [--dry-run] [--limit] [--source]` | O | - | **참고문헌 확장 수집** (서머리 → 외부 논문 다운로드) |
| `oopaper backup [--dry-run]` | O | O | **PDF 백업** (03_paper → 백업 경로로 이동) |
| `oopaper restore [--dry-run]` | O | O | **PDF 복원** (백업 경로 → 03_paper로 이동) |
| **자동화 (v04+, oopaper_auto.py)** | | | |
| `oopaper_auto organize [--dry-run]` | O | - | **00_down → YYMMDD-HHMM 폴더 자동 이동** (Phase 0 자동화) |
| `oopaper_auto dedup [--fuzzy] [--threshold N]` | O | - | **폴더 간 중복 검출** (정규화 + rapidfuzz) |
| `oopaper_auto meta [--folder ID] [--limit N]` | O | - | **PDF 메타데이터 추출** (제목/저자/연도/DOI/arXiv) |
| `oopaper_auto ref-match-fuzzy [--threshold N]` | O | - | **rapidfuzz 기반 참고문헌 내부 매칭** (Claude 대체) |

실행 분기:
- `--lang en` (기본): `uv run python .claude/skills/oopaper/scripts/oopaper_run.py [subcommand]`
- `--lang ko`: `uv run python .claude/skills/oopaper/scripts/ooessay_run.py [subcommand]`
- `backup/restore`: `uv run python .claude/skills/oopaper/scripts/oopaper_backup.py [subcommand]`

## 3. run 명령어

### 3.1 --lang en (영어 논문, 8 Phase) — v07+ 신규 순서

```
Phase 0: 00_down → 11_paper_en 이동 + 파일명 정규화
Phase 1: 스캔 → 미완료 논문 목록 + 5단계 상태 (X/E/S/T/O)
Phase 2: 영문 전문 추출 (AI) → *_03_*_전문(영어).md
Phase 3: 서머리 생성 (AI, 영문 전문 기반, 한글 출력) → *_00_*_서머리.md
Phase 4: 한글 번역 (AI / translator 에이전트) → *_04_*_전문(한글).md
Phase 5: 참고문헌 추출 + 내부 매칭 (AI)
Phase 6: 정밀 분석 → 05_분석.md 생성 (AI, anal --deep 동일)
Phase 7: paper_list.md 동기화 + 상태 갱신
```

> **v07 변경 (2026-05-03)**: Phase 3↔4 swap. 영문 전문에서 직접 한글 서머리를 생성한 뒤 한글 번역(전체) 진행. 한글 번역이 미완이어도 서머리는 생성 가능 → Gemma 의존 감소, 우선순위 재배치(전문 → 서머리 우선).

### 3.2 --lang ko (한국어 보고서, 4 Phase)

```
Phase 0: 00_down 스캔 → 한국어 보고서 PDF 식별
Phase 1: 12_paper_ko/YYMMDD-HHMM/ 폴더 생성 → PDF 이동
Phase 2: 서머리 생성 (00_서머리.md)
Phase 3: 한글 전문 추출 (04_전문(한글).md)
Phase 4: 검증 → 12_paper_ko.md 동기화
```

### 3.3 실행 옵션 (공통)

| 옵션 | 설명 |
|------|------|
| `--lang en\|ko` | 언어 지정 (기본: en) |
| `--limit N` | 처리할 최대 문헌 수 |
| `--folder ID` | 특정 폴더만 처리 (YYMMDD-HHMM) |
| `--dry-run` | 실행 없이 계획만 출력 |
| `--phase [N]` | 특정 Phase만 실행 (EN 전용) |
| `--skip-organize` | Phase 0 건너뛰기 (EN 전용) |
| `--gemma` | **Phase 2 서머리 · Phase 4 번역 초안을 로컬 Gemma에 위임** (EN 전용, v03+). 최종 포맷·검수는 여전히 Claude 필요. 환각 방지 설정 자동 적용(`enable_thinking=False`, `reasoning_effort=none`, `max_tokens≥4000`). 상세: `.claude/guides/gemma_delegation.md` |

## 4. 5단계 상태 체계 (EN, v07+ 신규 순서)

| 상태 | EN | KO | 의미 |
|------|:--:|:--:|------|
| X | O | O | 미처리 (PDF만 존재) |
| E | O | - | 영문 전문 추출 완료 (`*_03_*_전문(영어).md`) |
| S | O | O | 서머리 완료 (영문 전문 기반, 한글 출력) |
| T | O | - | 한글 번역 완료 (`*_04_*_전문(한글).md`) |
| O | O | - | 완료 (영문+서머리+한글+참고문헌 매칭) |

> **상태 진행 (v07)**: X → E → S → T → O
> **순서 변경 사유 (v07)**: 영문 전문에서 직접 한글 서머리를 생성한 뒤 한글 번역(전체)을 수행. 번역 미완 상태에서도 서머리 생성 가능 → 우선순위 재배치(전문 → 서머리 우선, 번역은 후처리).
> KO는 X/S 2단계 (영문 추출/번역 단계 없음).

## 5. anal 명령어

| 옵션 | EN | KO | 설명 |
|------|:--:|:--:|------|
| `--compare` | O | - | 논문 간 비교 분석 |
| `--add [폴더]` | O | - | 새 논문 추가 → 기존 서베이 병합 |
| `--deep` | O | O | 정밀 분석 → 05_분석.md 생성 |
| `--topic` | O | - | 연구 주제 오버라이드 |
| `--folder ID` | - | O | 특정 폴더만 분석 |
| `--force` | - | O | 기존 05_분석.md 덮어쓰기 |

서베이 저장: `{paper_root}/15_paper_survey/`

## 6. trans 명령어

### --lang en
- `english`: PDF → `*_03_*_전문(영어).md`
- `korean`: 영문 → `*_04_*_전문(한글).md` (translator 에이전트)

### --lang ko
- PDF → `*_04_*_전문(한글).md` (한글 직접 추출)
- `--folder ID` / `--force` 옵션

## 7. 파일 구조

### EN ({paper_root}/11_paper_en/YYMMDD-HHMM/)
```
{CODE}_00_{Title3}_서머리.md      # 서머리 + 키워드 + 참고문헌
{CODE}_01_{Title3}.pdf             # 원본 PDF
{CODE}_03_{Title3}_전문(영어).md   # 영문 전문 (References 포함)
{CODE}_04_{Title3}_전문(한글).md   # 한글 번역
{CODE}_05_{Title3}_분석.md         # 정밀 분석 (anal --deep)
```

### KO ({paper_root}/12_paper_ko/YYMMDD-HHMM/)
```
{CODE}_00_{Title3}_서머리.md      # 서머리
{CODE}_01_{Title3}.pdf             # 원본 PDF
{CODE}_04_{Title3}_전문(한글).md   # 한글 전문
{CODE}_05_{Title3}_분석.md         # 정밀 분석 (anal --deep)
```

### 다중 논문 폴더 규칙

> **원칙**: 하나의 YYMMDD-HHMM 폴더에는 논문 1편만 존재해야 한다.

다수의 PDF가 하나의 폴더에 묶여 있는 경우(예: DS01~DS10, IR01~IR07 등):

1. **논문별 서브폴더 생성**: `{paper_root}/11_paper_en/YYMMDD-HHMM/{PREFIX}/` 형태로 분리
   - 또는 각 논문을 독립된 `YYMMDD-HHMM` 폴더로 재배치
2. **전체 정리 파이프라인 실행**: 각 논문에 대해 `oopaper run` (Phase 1~7) 수행
3. **원본 다중 폴더 제거**: 정리 완료 후 빈 폴더 삭제

| 상황 | 조치 |
|------|------|
| prefix 없는 PDF 파일 | 해당 폴더와 무관한 파일 → 삭제 또는 올바른 폴더로 이동 |
| 다중 PDF 묶음 폴더 | 논문별 폴더 분리 후 oopaper run 실행 |
| 번호 체계 다른 파일 (DS/IR 등) | 새 YYMMDD-HHMM 폴더로 이동 또는 별도 디렉토리 정리 |

## 8. search 명령어 (EN 전용)

| 옵션 | 설명 |
|------|------|
| `--mode` | keyword, abstract, code, dataset, trend, recent, conf |
| `--년도` | 연도 범위 (예: 2020-2024) |
| `--인용` | 최소 인용 수 |
| `--정렬` | 인용순, 최신순, 관련순 |
| `--개수` | 결과 수 제한 |

## 9. download 명령어 (EN 전용)

- 입력: `{paper_root}/00_down/*_download_list.md` (마크다운 테이블)
- 미다운로드 항목(`[ ]`) 자동 다운로드 → `[x]` 업데이트
- arXiv URL 자동 처리, rate limiting (3초 딜레이)

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 대상 목록만 출력 |
| `--file FILE` | 특정 리스트 파일만 처리 |
| `--force` | 기다운로드 항목도 재다운로드 |

> ⚠️ **download/extend/Phase 0 organize 직후에는 반드시 `oopaper sync-list` 실행**.
> 신규 다운로드는 `paper_list.md`에 자동 등록되지 않음. 미동기화 시 `extend`의 중복 검사가
> 무력화되어 동일 논문이 다시 수집됨. (`run` 명령은 Phase 7에서 자동 sync — 단독 download는 수동 sync 필요)

## 10. ref 명령어 (EN 전용)

`oopaper ref 00_doc/보고서.md` → 인용 검증 → 정리 → 정규화

내부 매칭 규칙:
- **매칭 시**: `[폴더ID] 제목 (저자 연도)` 형식
- **미매칭 시**: `제목 (저자 연도) [arXiv:ID]` 형식

## 11. compress 명령어

텍스트 보존 PDF 압축, OCR 적용, 배치 처리 (`--lang en|ko`)

## 12. fix 명령어 (KO 전용)

> 코드 예시: references/guide.md §8 참조

## 13. extend 명령어 (EN 전용)

보유 서머리의 `### 외부` 참고문헌을 스캔하여 미보유 논문을 자동 검색·다운로드합니다.

| 옵션 | 설명 |
|------|------|
| `--folder ID` | 특정 폴더만 처리 (YYMMDD-HHMM) |
| `--dry-run` | 검색만 수행, 다운로드 생략 |
| `--limit N` | 최대 다운로드 수 (기본: 10) |
| `--source all\|arxiv\|s2` | 검색 소스 (기본: all) |

처리 흐름:
1. `*_00_*_서머리.md` → `## 참고 논문` → `### 외부` 섹션 파싱
2. paper_list.md 및 기존 서머리 제목과 중복 제거
3. arXiv API / Semantic Scholar API 검색 (타임아웃 5초, 딜레이 0.5초)
4. PDF 다운로드 → `{paper_root}/00_down/` 저장
5. 결과 테이블 출력

> 코드 예시: references/guide.md §5 참조

## 14. 서브에이전트 매핑

| 작업 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 논문 검색 | academic-researcher | sonnet | O |
| 서머리 분석 | academic-researcher | sonnet | O |
| 영문 추출 | data-analyst | sonnet | O |
| 한글 번역 | translator | haiku | O |
| 참고문헌 매칭 | academic-researcher | sonnet | O |
| 문서 생성 | task-executor | sonnet | - |
| 검증 | task-checker | sonnet | - |

## 15. backup/restore 명령어

PDF 파일을 외부 백업 경로로 이동하거나 복원합니다. 대상: `11_paper_en/`, `12_paper_ko/` (`00_down` 제외)

설정 파일: `{paper_root}/backup_config.json` (컴퓨터별로 다름, git ignore 권장)

### 옵션

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 실제 이동 없이 대상 목록만 출력 |
| `--folder ID` | 특정 폴더만 (예: `260222-1921`) |
| `--subdir DIR` | 특정 하위 폴더만 (예: `11_paper_en`) |

> 코드 예시: references/guide.md §6 참조

## 16. 스크립트 참조

### EN 스크립트
| 스크립트 | 설명 |
|----------|------|
| `oopaper/scripts/oopaper_run.py` | 통합 실행, 상태 확인, paper_list 동기화 |
| `oopaper/scripts/oopaper_trans.py` | PDF 텍스트 추출, 한글 번역 템플릿 |
| `oopaper/scripts/oopaper_pdf_compress.py` | PDF 압축 (EN/KO 공유) |
| `oopaper/scripts/oopaper_cite_*.py` | 인용 검증/정규화/매핑/정리 |
| `oopaper/scripts/oopaper_backup.py` | PDF 백업/복원 (EN/KO 공통) |

### KO 스크립트
| 스크립트 | 설명 |
|----------|------|
| `oopaper/scripts/ooessay_run.py` | 통합 실행, 상태 확인, 무결성 체크, 텍스트 추출, 정밀 분석 |

## 17. 문서 템플릿 (templates/, v06+)

| 파일 | 용도 | 주요 변수 |
|------|------|---------|
| `templates/summary.md` | 서머리(`*_00_*_서머리.md`) | `{folder_id}` `{title}` `{authors}` `{year}` `{doi}` `{arxiv}` `{abstract}` `{keywords}` `{internal_refs}` `{external_refs}` |
| `templates/translation_english.md` | 영문 전문(`*_03_*_전문(영어).md`) | `{title}` `{engine}` `{full_text}` `{page_count}` `{char_count}` |
| `templates/translation_korean.md` | 한글 번역(`*_04_*_전문(한글).md`) | `{stage}` `{stage_label}` `{v1_engine}` `{v2_engine}` `{v1_at}` `{v2_at}` `{full_text}` |

YAML frontmatter로 메타데이터 추적. 파싱 가능 + 재처리 시 단계 식별.

## 18. 한글 번역 2단계 프로세스 (v06+)

```
trans korean
├─ 1차: Gemma 가용성 체크
│   ├─ OK  → Gemma 자동 번역 (stage=1, v1_engine=gemma4:26b)
│   └─ 실패 → 사용자 확인 ("Gemma 미가용. Claude 단독 번역? y/n")
│             ├─ y → Claude 단독 (stage=2 직행)
│             └─ n → 건너뜀
├─ 2차: Claude 검수 (옵션, 기본 활성)
│   ├─ Gemma 결과 + 영문 원문 입력
│   ├─ 오타/포맷/일관성 보정
│   └─ stage=2, v2_engine=claude-* 갱신
└─ 결과: 한글 번역 파일 + frontmatter 단계 표시
```

**스테이지 라벨**:
- `★ 1차 (Gemma 자동)` — 빠른 1차 번역, 검수 미수행
- `★★ 2차 (Claude 검수 완료)` — 정밀 번역, 권장 최종 상태

**플래그**:
- `--no-claude-review` — Gemma만 (1차에서 멈춤, 일괄 처리용)
- `--claude-only` — Gemma 건너뛰기 (Claude 직접 호출)
- `--stage 1|2` — 특정 단계만 처리

**토큰 절감**: 813편 처리 시 1차만 Gemma (무료) → Claude 검수만 부분 적용 → Claude 토큰 ≈90% 절감

## 19. KISTI ScienceON 보고서 PDF 추출 방법

KISTI ScienceON(`scienceon.kisti.re.kr`) 보고서는 직접 PDF URL이 노출되지 않으나 추출 가능.

> **적용 대상**: KISTI R&D 보고서 (TRKO* 접두사), NTIS 연계 보고서
> **제한**: 비공개/유료 보고서는 로그인 필요

> 코드 예시: references/guide.md §7 참조

> **관련 문서**: `00_doc/sp00/d0001_prd.md` | `00_doc/sp00/d0004_todo.md` | `{paper_root}/11_paper_en/paper_list.md` | `{paper_root}/12_paper_ko.md`

## 사용 예시

> 코드 예시: references/guide.md §2 참조

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

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
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

