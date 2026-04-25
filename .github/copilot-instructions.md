# GitHub Copilot Instructions — OAIS (One AI System)

## 언어
항상 **한국어**로 답변합니다.

---

## 빌드 / 테스트 / 린트 명령어

> **모든 Python 실행은 반드시 `uv run`을 사용해야 합니다.** 직접 `python` 호출 금지.

```bash
# 전체 테스트
uv run pytest

# 특정 테스트 파일
uv run pytest tests/sp08/test_something.py

# 단일 테스트 함수
uv run pytest tests/sp08/test_something.py::test_function_name -v

# E2E 테스트 제외
uv run pytest -m "not e2e"

# 구문 검증 (코드 수정 후 필수)
uv run python -m py_compile <수정된파일.py>

# 린트 / 타입 체크
uv run pylint oais/
uv run mypy oais/

# 코드 포맷
uv run black oais/
```

---

## 아키텍처 개요

OAIS는 **Claude Code 기반 바이브 코딩 환경**으로, 두 가지 핵심 레이어로 구성됩니다.

### 1. `oais/` — Python 공통 모듈 (v1.5.0)

이미지 처리·딥러닝·GIS·통계·시각화 유틸리티를 제공하는 패키지.

```
oais/
├── utils.py                      # 파일/폴더/날짜/엑셀 유틸리티
├── metrics.py                    # 세그멘테이션 메트릭 (skimage/cv2 optional)
├── image.py                      # 이미지 처리 (skimage/cv2 optional)
├── iqa/                          # 이미지 품질 평가 (FR-IQA, NR-IQA, DL-IQA, HSMB)
├── dl.py                         # GPU 메모리 관리, 배치 크기 최적화
├── dl_utils.py                   # GPU 설정 (torch optional)
├── datasets.py                   # 세그멘테이션 데이터셋 클래스
├── models.py                     # 모델 유틸리티, PyTorch Lightning 콜백
├── modules/                      # 고급 메트릭 (torch optional)
├── statistics.py                 # 상관분석, 그룹 통계
├── visualization.py              # 시각화 (matplotlib)
├── visualization_segmentation.py # 세그멘테이션 시각화
├── reporting.py                  # Excel 보고서 출력
└── gis.py                        # 지리정보 유틸리티 (geopandas optional)
```

**Optional import 패턴**: `skimage/cv2`, `torch`, `geopandas` 미설치 시 `try/except ImportError: pass`로 조용히 스킵. 새 모듈 추가 시 동일 패턴 준수.

### 2. `.claude/skills/oo*/` — oo 스킬 시스템 (34개)

Claude Code 세션에서 호출되는 워크플로우 스킬. 각 스킬 폴더 구조:

```
.claude/skills/oo{name}/
├── SKILL.md      # 스킬 사양 및 실행 규칙
└── scripts/      # 실행 스크립트 (uv run으로 호출)
```

### 3. SP (서브프로젝트) 체계

| SP | 폴더 | 설명 |
|----|------|------|
| SP00 | (공통) | OAIS 전체 공통 문서 (`00_doc/sp00/`) |
| SP03 | `03_paper/` | 논문 관리 (369편) |
| SP05 | `05_youtube_graphRAG/` | Graph RAG 파일럿 |
| SP06 | `06_oohwp_skill/` | oohwp 스킬 개발 |
| SP07 | `07_designsystem/` | 디자인 시스템 |
| SP08 | `08_RRag/` | RAG 평가 파이프라인 (RAGAS, 18개 모델, 3,710 조합) |
| SP09 | `09_ooppt/` | PPT 프레젠테이션 제작 |

---

## 핵심 컨벤션

### 문서 네이밍 규칙

```
00_doc/sp{NN}/d{SP번호 × 10000 + 기본번호}_설명.md

예) SP08 PRD  → 00_doc/sp08/d80001_prd.md
    SP00 TODO → 00_doc/sp00/d0004_todo.md
```

매 세션 자동 로드 문서 (컨텍스트 효율을 위해 이 2개만 유지):
- `00_doc/sp00/d0001_prd.md` — 프로젝트 요구사항
- `00_doc/sp00/d0004_todo.md` — TODO/이슈 추적

### 테스트 폴더 구조

```
tests/
├── sp05/   # 05_youtube_graphRAG 테스트
└── sp08/   # 08_RRag 테스트 (conftest.py 포함)
```

SP별 서브폴더(`tests/sp{N}/`)에 테스트를 배치합니다.

### 에러 처리 흐름

1. 에러 발생 → `00_doc/sp00/d0004_todo.md` 디버깅 섹션에 기록
2. 해결됨 → `00_doc/sp00/d0010_history.md`로 이동

### 에이전트/스킬 우선순위

1. **oo 스킬 우선** — `oocheck run`, `oofix run`, `ootest run` 등
2. `.claude/agents/` 내 전문 에이전트 (python-code-reviewer, task-executor 등)
3. MCP 서버 (Sequential Thinking, Playwright 등)

### Python 파일 수정 후 필수 검증

서브에이전트가 Python 파일을 수정한 경우 반드시 구문 검증을 수행합니다:

```bash
uv run python -m py_compile <수정된파일.py>
```

### Windows 환경 주의사항

- `TEMP/TMP` 환경변수 불일치로 Bash exit code 1이 오탐될 수 있음 → stdout 결과로 실제 성공 여부 판단
- 경로에 `home`이 포함되면 Git Bash EPERM 오류 발생 (현재 경로 `doom`으로 해결됨)

---

## 참고 문서 (필요 시 로드)

| 문서 | 경로 |
|------|------|
| 구현 계획 | `00_doc/sp00/d0002_plan.md` |
| 테스트 시나리오 | `00_doc/sp00/d0003_test.md` |
| 라이브러리 정보 | `00_doc/sp00/d0005_lib.md` |
| DB 구조 | `00_doc/sp00/d0006_db.md` |
| 환경 현황 | `00_doc/sp00/d0009_env.md` |
| 공통 가이드라인 | `.claude/guides/common_guide.md` |
