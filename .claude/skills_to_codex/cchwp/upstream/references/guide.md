# oohwp 가이드

## 문서 이력 관리
- v02 2026-04-21 — 워크플로우 코드 예시 이동 (SKILL.md → guide.md)
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**oohwp**: 한글(HWPX) 문서 작성·읽기·변환.

- **참조**: SKILL.md (서브명령어·워크플로우)
- **이 문서**: 방법론(How) — 실행 패턴, 입력/출력 형식, 사용 가이드

---

## 2. 워크플로우 코드 예시

### build — 신규 문서 생성

```bash
uv run --with lxml python .claude/skills/oohwp/scripts/build_hwpx.py \
  --template gonmun \
  --section my_section.xml \
  --title "제목" \
  --creator "작성자" \
  --output result.hwpx
```

### extract — 텍스트 추출

```bash
uv run --with lxml python .claude/skills/oohwp/scripts/text_extract.py \
  document.hwpx [--include-tables]
```

### check — 구조 검증

```bash
uv run --with lxml python .claude/skills/oohwp/scripts/validate.py document.hwpx
```

### analyze — 기존 문서 분석

```bash
uv run --with lxml python .claude/skills/oohwp/scripts/analyze_template.py document.hwpx
```

### edit — 기존 문서 편집

```bash
# unpack → XML 수정 → pack
uv run --with lxml python .claude/skills/oohwp/scripts/office/unpack.py document.hwpx ./work_dir/
# section0.xml, header.xml 수정
uv run --with lxml python .claude/skills/oohwp/scripts/office/pack.py ./work_dir/ result.hwpx
```

### convert — HWP → HWPX 변환

> Windows + 아래한글 설치 필요. 의존성: `pyhwpx`

```bash
# 단일 파일 변환
uv run --with pyhwpx python .claude/skills/oohwp/scripts/hwp_to_hwpx.py input.hwp [output.hwpx]

# 폴더 일괄 변환
uv run --with pyhwpx python .claude/skills/oohwp/scripts/hwp_to_hwpx.py --batch <dir>

# 변환 중 한글 창 표시
uv run --with pyhwpx python .claude/skills/oohwp/scripts/hwp_to_hwpx.py input.hwp --visible
```

### pagecount — 페이지 카운트

> Windows + 아래한글 설치 필요 (HWP/HWPX 변환 시). 의존성: `pyhwpx`, `pypdf`, `openpyxl`

```bash
# 폴더 내 문서 타입 자동 감지 (.hwp → .hwpx → .pdf 순)
uv run --with pyhwpx,pypdf,openpyxl python scripts/page_count.py <폴더경로>
```

---

## 3. 입출력 형식

| 항목 | 내용 |
|------|------|
| 입력 | 서브명령어 인자 또는 현재 SP 컨텍스트 |
| 출력 | 터미널 출력 또는 문서 파일 생성 |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록 |

---

## 4. 주의사항

- SP 컨텍스트 확인 후 실행 (SKILL.md 참조)
- 상세 서브명령어는 SKILL.md 참조
