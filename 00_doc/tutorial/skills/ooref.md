# ooref Tutorial

> 프레임워크 레퍼런스 목록 조회 + 현재 프로젝트 적용 여부 체크 스킬 | 버전: v03 | 카테고리: doc-env

## 1. 이 스킬은 왜 필요한가?

FastAPI/Django/Streamlit 등 프레임워크별 표준 패턴과 구조를 정의하고, 현재 프로젝트가 이를 따르고 있는지 검증합니다. 프레임워크 레퍼런스 불일치를 자동으로 감지합니다.

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
ooref run

# 상태 확인
ooref status

# 도움말
ooref help
```

## 3. 전체 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ooref help` | 서브명령어 목록 표시 |
| `ooref version` | 스킬 버전 정보 (v01) |
| `ooref list` | 사용 가능한 프레임워크 레퍼런스 목록 |
| `ooref check` | references/checklist.md 기반으로 ooref 스킬 자체 기능 검증 |
| `ooref add checklist "항목"` | checklist.md에 새 항목 추가 |
| `ooref run` | 현재 프로젝트 기술스펙 감지 + 레퍼런스 기준 체크 |
| `ooref run [path]` | 특정 프로젝트 경로 체크 |
| `ooref run [framework]` | 특정 프레임워크 강제 지정 후 체크 |

실행: `uv run python .claude/skills/ooref/scripts/ooref_run.py [subcommand] [args]`

---

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 프레임워크 레퍼런스 목록 조회 + 현재 프로젝트 적용 여부 체크 |
| **하는 것** | 레퍼런스 목록 표시, 프레임워크 자동 감지, 구조/패턴 체크, 문제점 리스트업 |
| **하지 않는 것** | 코드 수정(→oofix), 레퍼런스 문서 작성, 동기화(→oosync) |
| **참조 범위** | `.claude/reference/development/` 폴더 전체 |
| **수정 대상** | 읽기 전용 (체크 결과만 출력) |
| **실행 레벨** | [반자동] — 프로젝트 경로 자동 감지 후 체크 |
| **에이전트 호환** | 범용 — 스크립트 실행 중심 |

### 레퍼런스 구조

```
.claude/reference/development/
├── README.md                   # 프레임워크 목록 + 감지 규칙
└── fast-api/                   # FastAPI 레퍼런스 (13개 문서)
    ├── 00_overview.md
    ├── 01_directory_structure.md
    ├── 02_config_pattern.md
    ├── 03_main_app.md
    ├── 04_routers.md
    ├── 05_models_schemas.md
    ├── 06_batch_engine.md
    ├── 07_error_handling.md
    ├── 08_testing.md
    ├── 09_admin_dashboard.md
    ├── 10_external_integration.md
    ├── 11_menu_structure.md
    └── 12_dashboard_data.md
```

---

### 프레임워크 지원 현황

| 프레임워크 | 자동 감지 | 체크 구현 | 감지 조건 |
|-----------|----------|----------|----------|
| FastAPI | O | O | `pyproject.toml`/`requirements.txt`에 `fastapi` 또는 `main.py`에 `from fastapi import` |
| Django | O | - | `manage.py` + `settings.py` 존재 |
| Streamlit | O | - | `import streamlit` 패턴 |

---

### 출력 수준

| 수준 | 의미 | 대응 |
|------|------|------|
| CRITICAL | 즉시 수정 필요 (앱 동작 불가) | 즉시 |
| ERROR | 레퍼런스 패턴 미적용 (기능 누락) | 24시간 내 |
| WARNING | 권장 패턴 미적용 | 검토 후 적용 |
| INFO | 선택적 개선 사항 | 백로그 |

---

## 5. 워크플로우

**`ooref list`** → `README.md` 파싱 → 프레임워크 목록 + 감지 규칙 출력

**`ooref run`**:
1. 프로젝트 경로 결정 (기본: 현재 디렉토리)
2. 프레임워크 자동 감지 (`pyproject.toml`, `requirements.txt`, `main.py` import 패턴)
3. 해당 레퍼런스 폴더 로드 (`.claude/reference/development/{framework}/`)
4. 체크 실행:
   - 디렉토리 구조 (`01_directory_structure.md` 기준)
   - 파일 크기 (권장 한도 초과 여부)
   - 코드 패턴 (`lifespan`, rate limiting, 예외 핸들러)
   - 설정 파일 분리 여부
   - 테스트 구조 (`conftest.py`, `test_*.py`)
5. 문제점 CRITICAL/ERROR/WARNING/INFO 수준으로 리스트업

---

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
ooref run
```

### 서브명령어 활용
```bash
ooref list  # 사용 가능한 프레임워크 레퍼런스 목록
ooref run  # 현재 프로젝트 기술스펙 감지 + 레퍼런스 기준 체크
```

### 스크립트 직접 실행
```bash
uv run python .claude/skills/ooref/scripts/ooref_run.py
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

(서브에이전트 정보 없음)

## 10. 관련 스킬

`oosync` (레퍼런스 동기화) | `oocheck` (코드 체크) | `oodev` (개발) | `oofix` (이슈 수정)

---

> 생성일: 2026-04-14 11:32 | ootutorial v03
