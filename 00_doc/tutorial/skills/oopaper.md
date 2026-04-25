# oopaper Tutorial

> 통합 문헌 관리 스킬 | 버전: v02 | 카테고리: content

## 1. 이 스킬은 왜 필요한가?


**이런 상황에서 사용합니다:**
- `--lang en` (기본값): 영어 논문 → `{paper_root}/11_paper_en/`
- `--lang ko`: 한국어 보고서 → `{paper_root}/12_paper_ko/`

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oopaper run

# 상태 확인
oopaper status

# 도움말
oopaper help
```

## 3. 전체 서브명령어

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

실행 분기:
- `--lang en` (기본): `uv run python .claude/skills/oopaper/scripts/oopaper_run.py [subcommand]`
- `--lang ko`: `uv run python .claude/skills/oopaper/scripts/ooessay_run.py [subcommand]`
- `backup/restore`: `uv run python .claude/skills/oopaper/scripts/oopaper_backup.py [subcommand]`

## 4. 상세 사용법

### 4단계 상태 체계

| 상태 | EN | KO | 의미 |
|------|:--:|:--:|------|
| X | O | O | 미처리 (PDF만 존재) |
| S | O | O | 서머리 완료 |
| T | O | - | 번역 완료 (서머리+영문+한글) |
| O | O | - | 완료 (서머리+영문+한글+참고문헌 매칭) |

KO는 X/S 2단계 (번역/참고문헌 단계 없음).

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 학술 논문·국내 보고서 통합 문헌 관리 (수집·분류·분석·번역) |
| **하는 것** | 논문 수집, 분류 정리, 영문 전문·한글 번역 생성, {paper_root}/ 관리 |
| **하지 않는 것** | 논문 작성(→oosota), 서베이 생성(→oosurvey), 연구 수행(→ooresearch) |
| **참조 범위** | 현재 프로젝트 `{paper_root}/` + 웹 검색(논문 수집 시) |
| **수정 대상** | `{paper_root}/**/*.md`, `d30004_todo.md` |
| **실행 레벨** | [반자동] — 수집 대상 확인 후 실행 |
| **에이전트 호환** | Claude Code 권장 — academic-researcher 서브에이전트 자동 배치 / 다른 에이전트: 웹 검색 후 수동으로 파일 생성 |

### run 명령어

### 3.1 --lang en (영어 논문, 8 Phase)

```
Phase 0: 00_down → 11_paper_en 이동 + 파일명 정규화
Phase 1: 스캔 → 미완료 논문 목록 + 4단계 상태 (X/S/T/O)
Phase 2: 서머리 생성 + 키워드 추출 (AI)
Phase 3: 영문 전문 추출 (AI)
Phase 4: 한글 번역 (AI / translator 에이전트)
Phase 5: 참고문헌 추출 + 내부 매칭 (AI)
Phase 6: 정밀 분석 → 05_분석.md 생성 (AI, anal --deep 동일)
Phase 7: paper_list.md 동기화 + 상태 갱신
```

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

### anal 명령어

| 옵션 | EN | KO | 설명 |
|------|:--:|:--:|------|
| `--compare` | O | - | 논문 간 비교 분석 |
| `--add [폴더]` | O | - | 새 논문 추가 → 기존 서베이 병합 |
| `--deep` | O | O | 정밀 분석 → 05_분석.md 생성 |
| `--topic` | O | - | 연구 주제 오버라이드 |
| `--folder ID` | - | O | 특정 폴더만 분석 |
| `--force` | - | O | 기존 05_분석.md 덮어쓰기 |

서베이 저장: `{paper_root}/15_paper_survey/`

### trans 명령어

### --lang en
- `english`: PDF → `*_03_*_전문(영어).md`
- `korean`: 영문 → `*_04_*_전문(한글).md` (translator 에이전트)

### --lang ko
- PDF → `*_04_*_전문(한글).md` (한글 직접 추출)
- `--folder ID` / `--force` 옵션

### 파일 구조

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

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

```bash
# 영어 논문 (기본)
oopaper status                          # EN 현황
oopaper run                             # EN 전체 파이프라인
oopaper run --folder 260201-1430        # 특정 폴더
oopaper search "crack detection CNN"    # 논문 검색
oopaper anal --deep --folder 260201-1430  # 정밀 분석

# 한국어 보고서
oopaper status --lang ko               # KO 현황
oopaper run --lang ko                  # KO 전체 파이프라인
oopaper anal --lang ko --deep          # KO 정밀 분석
oopaper fix --lang ko --check-only     # 무결성 검사

# 공통
oopaper compress --lang en             # EN PDF 압축
oopaper compress --lang ko             # KO PDF 압축
```

<!-- RUN-UPDATE-REF:START -->

## 7. 입출력

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

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

| 작업 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 논문 검색 | academic-researcher | sonnet | O |
| 서머리 분석 | academic-researcher | sonnet | O |
| 영문 추출 | data-analyst | sonnet | O |
| 한글 번역 | translator | haiku | O |
| 참고문헌 매칭 | academic-researcher | sonnet | O |
| 문서 생성 | task-executor | sonnet | - |
| 검증 | task-checker | sonnet | - |

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-17 19:50 | ootutorial v02
