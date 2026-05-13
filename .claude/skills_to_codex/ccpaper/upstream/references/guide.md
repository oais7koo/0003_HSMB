# oopaper 가이드

## 문서 이력 관리
- v02 2026-04-21 — SKILL.md 코드 예시 이동: extend/backup/KISTI 상세 패턴 통합
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**oopaper**: 논문 다운로드·서머리·번역·서베이 관리(EN/KO).

- **참조**: SKILL.md (서브명령어·워크플로우)
- **이 문서**: 방법론(How) — 실행 패턴, 입력/출력 형식, 사용 가이드

---

## 2. 기본 사용법

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

---

## 3. 워크플로우

### EN 파이프라인 (8 Phase)

```
Phase 0: 00_down → 11_paper_en 이동 + 파일명 정규화
Phase 1: 스캔 → 미완료 논문 목록 + 4단계 상태 (X/E/T/S/O)
Phase 2: 영문 전문 추출 (AI) → *_03_*_전문(영어).md
Phase 3: 한글 번역 (AI / translator 에이전트) → *_04_*_전문(한글).md
Phase 4: 서머리 생성 + 키워드 추출 (AI, 한글 전문 기반) → *_00_*_서머리.md
Phase 5: 참고문헌 추출 + 내부 매칭 (AI)
Phase 6: 정밀 분석 → 05_분석.md 생성 (AI, anal --deep 동일)
Phase 7: paper_list.md 동기화 + 상태 갱신
```

---

## 4. 입출력 형식

| 항목 | 내용 |
|------|------|
| 입력 | 서브명령어 인자 또는 현재 SP 컨텍스트 |
| 출력 | 터미널 출력 또는 문서 파일 생성 |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록 |

---

## 5. extend 명령어 상세 패턴

### 사용 예시

```bash
oopaper extend                          # 전체 서머리 스캔 → 최대 10편 다운로드
oopaper extend --dry-run                # 검색만, 다운로드 생략
oopaper extend --folder 260301-1001    # 특정 폴더만 처리
oopaper extend --limit 5               # 최대 5편
oopaper extend --source arxiv          # arXiv만 검색
oopaper extend --source s2             # Semantic Scholar만 검색
```

### 스크립트 직접 실행

```bash
uv run python .claude/skills/oopaper/scripts/oopaper_extend.py --dry-run --limit 3
```

---

## 6. backup/restore 상세 패턴

### 설정 파일 형식 (backup_config.json)

컴퓨터별로 다름 (git ignore 권장):

```json
{
  "backup_dir": "C:/Users/oaiskoo/doom/7_box/03_paper",
  "hostname": "oaiskoo"
}
```

### 설정 초기화

```bash
uv run python .claude/skills/oopaper/scripts/oopaper_backup.py config --path "C:/Users/oaiskoo/doom/7_box/03_paper"
```

### 사용 예시

```bash
oopaper backup --dry-run              # 대상 확인
oopaper backup                        # 전체 PDF 백업
oopaper backup --folder 260222-1921   # 특정 폴더만 백업
oopaper restore --dry-run             # 복원 대상 확인
oopaper restore                       # 전체 PDF 복원
uv run python .claude/skills/oopaper/scripts/oopaper_backup.py status  # 현황
```

---

## 7. KISTI ScienceON 보고서 PDF 추출 방법

KISTI ScienceON(`scienceon.kisti.re.kr`) 보고서는 직접 PDF URL이 노출되지 않으나, 아래 방법으로 추출 가능.

### 추출 절차

```
1. 보고서 페이지 URL 확인
   https://scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn=TRKO201900017765

2. 원문보기 URL 구성 (cn, dbt 파라미터)
   https://scienceon.kisti.re.kr/commons/util/originalView.do?cn={CN}&dbt=TRKO&rn=1

3. WebFetch로 원문보기 페이지 HTML 분석
   → iframe 내부에 실제 PDF 경로 포함:
   /commons/util/orgDocDown.do?url=/tr_img/YYYYNNN/rttrko000000NNNNNN.pdf

4. PDF 직접 다운로드 URL 조합
   https://scienceon.kisti.re.kr/commons/util/orgDocDown.do?url=/tr_img/2019017/rttrko000000315524.pdf
```

### URL 패턴

| 단계 | URL 패턴 |
|------|---------|
| 보고서 페이지 | `scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn={CN}` |
| 원문 뷰어 | `scienceon.kisti.re.kr/commons/util/originalView.do?cn={CN}&dbt=TRKO&rn=1` |
| PDF 다운로드 | `scienceon.kisti.re.kr/commons/util/orgDocDown.do?url={PDF_PATH}` |

### 자동화 패턴

```python
# WebFetch로 원문 뷰어 페이지 접근 → PDF 경로 추출 → curl 다운로드
# 로그인 불필요 (공개 보고서 한정)
```

> **적용 대상**: KISTI R&D 보고서 (TRKO* 접두사), NTIS 연계 보고서
> **제한**: 비공개/유료 보고서는 로그인 필요

---

## 8. fix 명령어 상세 패턴 (KO 전용)

```bash
oopaper fix --lang ko --check-only    # 검사만
oopaper fix --lang ko --auto-fix      # 자동 수정
oopaper fix --lang ko --folder ID     # 특정 폴더
```

---

## 9. 주의사항

- SP 컨텍스트 확인 후 실행 (SKILL.md 참조)
- 상세 서브명령어는 SKILL.md 참조
