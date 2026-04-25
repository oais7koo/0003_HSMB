# 플러그인: pyright-lsp

> Python 타입 체크 (Pyright LSP) | 필수 ★

## 개요

pyright-lsp는 Microsoft Pyright 타입 체커를 Claude Code에 통합하는 LSP(Language Server Protocol) 플러그인입니다. Python 코드의 타입 오류를 실시간으로 감지합니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `pyright-lsp` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | ★ 필수 |
| 설치 명령어 | `/plugin install pyright-lsp@claude-plugins-official` |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| 타입 추론 | Python 코드 타입 자동 추론 |
| 타입 오류 감지 | 잘못된 타입 사용 실시간 검출 |
| 자동 완성 | 타입 기반 코드 자동 완성 |
| 정의 이동 | 변수/함수 정의 위치 추적 |
| 참조 찾기 | 심볼 사용처 전체 조회 |

## LSP 도구 사용법

pyright-lsp는 Claude Code의 LSP 도구를 활성화합니다:

```bash
# 타입 진단 (파일 또는 디렉토리)
lsp_diagnostics("src/oo/metrics.py")
lsp_diagnostics_directory("src/")

# 정의 이동
lsp_goto_definition("src/oo/utils.py", line=45, character=12)

# 참조 찾기
lsp_find_references("src/oo/utils.py", line=10, character=5)

# 타입 정보 hover
lsp_hover("src/oo/datasets.py", line=80, character=15)

# 심볼 목록
lsp_document_symbols("src/oo/api.py")
```

## oo 스킬 연계

| oo 스킬 | pyright-lsp 연계 |
|---------|----------------|
| `oocheck run` | LSP 진단 결과 포함 |
| `oodev run` | 코드 작성 시 타입 검증 |
| `oofix run` | 타입 오류 자동 수정 |

## pyproject.toml 설정

```toml
[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "basic"  # off / basic / standard / strict
include = ["src", "pages"]
exclude = ["**/__pycache__"]
```

## mypy vs pyright

| 항목 | mypy | pyright |
|------|------|---------|
| 속도 | 느림 | 빠름 |
| 정확도 | 높음 | 높음 |
| IDE 통합 | 제한적 | 우수 (LSP) |
| Claude 연계 | oocheck로 별도 실행 | LSP 도구로 직접 연계 |

---

> 생성일: 2026-04-02 | ootutorial v01
