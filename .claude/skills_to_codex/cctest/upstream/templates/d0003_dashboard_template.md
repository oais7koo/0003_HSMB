# d0003_test.md - 테스트 현황 대시보드 (SP00 공통)

## 문서이력관리
- v01 {날짜} — 초기 생성

---

## 개요

SP00 공통 테스트 대시보드. 모든 서브프로젝트(SP)의 테스트 현황을 집계하고, SP별 상세 문서로 연결한다.

- **테스트 방법론**: `.claude/skills/ootest/references/guide.md`
- **테스트 폴더**: `tests/sp{N}/` (SP별 분리)
- **SP별 상세**: 아래 현황 테이블의 링크 참조

---

## 1. SP별 테스트 디렉토리 구조

```
tests/
├── conftest.py          # 공통 fixture
├── sp02/                # 02_pycode (oais 모듈)
│   ├── conftest.py
│   └── TC*.py
├── sp05/                # 05_youtube_graphRAG
│   ├── conftest.py
│   └── TC*.py
├── sp06/                # 06_oohwp_skill
├── sp08/                # 08_RRag
│   ├── conftest.py
│   ├── TC*.py
│   └── integration/
└── sp09/                # 09_ooppt
```

---

## 2. SP별 테스트 현황

> 업데이트: `ootest run` 실행 후 아래 테이블 갱신

| SP | 폴더 | TC 수 | 통과 | 실패 | 통과율 | 최종 실행일 | 상세 문서 |
|----|------|:----:|:----:|:----:|:------:|------------|----------|
| SP02 | 02_pycode | - | - | - | - | - | [d20003](../sp02/d20003_test.md) |
| SP03 | 03_paper | - | - | - | - | - | [d30003](../sp03/d30003_test.md) |
| SP04 | 04_scraping | - | - | - | - | - | [d40003](../sp04/d40003_test.md) |
| SP05 | 05_youtube_graphRAG | - | - | - | - | - | [d50003](../sp05/d50003_test.md) |
| SP06 | 06_oohwp_skill | - | - | - | - | - | - |
| SP07 | 07_designsystem | - | - | - | - | - | - |
| SP08 | 08_RRag | - | - | - | - | - | [d80003](../sp08/d80003_test.md) |
| SP09 | 09_ooppt | - | - | - | - | - | - |
| **합계** | - | **-** | **-** | **-** | **-** | - | - |

---

## 3. SP별 테스트 구조 규칙

### 3.1 테스트 파일 배치 원칙

| 원칙 | 규칙 |
|------|------|
| 기능별 파일 분리 | 1 기능 = 1 TC 파일 (`TC{Epic}-{Feature}.{Task}_{이름}.py`) |
| SP별 폴더 분리 | `tests/sp{N}/` — `00_doc/sp{N}/` 구조와 동일하게 분리 |
| conftest.py | 각 SP 폴더에 SP 전용 fixture 배치 |
| 통합 테스트 | `tests/sp{N}/integration/` 하위 (선택) |

### 3.2 conftest.py 표준 템플릿

```python
"""SP{NN} 테스트 설정"""
import sys
from pathlib import Path

# SP 루트를 sys.path에 추가
SP_ROOT = Path(__file__).parent.parent.parent / "{SP_folder}"
sys.path.insert(0, str(SP_ROOT))

import pytest

@pytest.fixture
def sp_root():
    return SP_ROOT

@pytest.fixture
def test_data_dir():
    return SP_ROOT / "tests" / "data"
```

### 3.3 현행화 체크 커맨드

```bash
# SP별 TC 파일 수 확인
find tests/ -name "TC*.py" | sort

# 전체 TC 수집 확인
uv run pytest --collect-only -q

# SP별 테스트 실행
uv run pytest tests/sp08/ -v
```

---

## 4. oo 모듈 테스트 (공통 Part D)

> oo 모듈은 공통이므로 이 문서에서 통합 관리. SP별 d0003에서는 이 섹션 링크만 참조.

### 4.1 테스트 대상

| 카테고리 | 모듈 수 | 테스트 파일 | 설명 |
|----------|:-------:|-------------|------|
| Core | - | `tests/sp02/test_core.py` | DB 연결, 인증, 세션 |
| Utils | - | `tests/sp02/test_utils.py` | 유틸리티 함수 |
| Metrics | - | `tests/sp02/test_metrics.py` | 세그멘테이션 메트릭 |
| Image | - | `tests/sp02/test_image.py` | 이미지 처리 |

### 4.2 실행 결과

| 실행일 | 대상 | 전체 | 통과 | 실패 | 비고 |
|--------|------|:----:|:----:|:----:|------|
| - | oo/*.py | - | - | - | (검사 기록 없음) |

---

## 관련 문서

| 문서 | 경로 |
|------|------|
| 테스트 방법론 | `.claude/skills/ootest/references/guide.md` |
| PRD | `00_doc/sp00/d0001_prd.md` |
| TODO | `00_doc/sp00/d0004_todo.md` |
| SP별 d0003 | 위 현황 테이블 링크 참조 |
