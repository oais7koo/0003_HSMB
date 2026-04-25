# 플러그인: context7

> 라이브러리 공식 문서 실시간 조회 | 필수 ★

## 개요

context7은 외부 라이브러리의 최신 공식 문서를 Claude 세션에 직접 주입하는 플러그인입니다. 오래된 학습 데이터 대신 실시간 문서를 참조하여 정확한 코드를 생성합니다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `context7` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | ★ 필수 |
| 설치 명령어 | `/plugin install context7@claude-plugins-official` |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| 라이브러리 문서 조회 | npm/PyPI 라이브러리 공식 문서 실시간 로드 |
| 버전별 문서 | 특정 버전의 API 문서 조회 가능 |
| 코드 예제 | 공식 예제 코드 자동 포함 |
| 자동 활성화 | import 문 감지 시 자동 활성화 |

## 활성화 방법

| 방법 | 예시 |
|------|------|
| 플래그 | `--c7` 또는 `--context7` |
| 자동 | `import pandas as pd` 코드 작성 시 자동 |
| 자동 | 프레임워크 관련 질문 시 자동 |

## 사용 예시

```bash
# 1. 플래그로 명시적 사용
"FastAPI 엔드포인트 구현해줘 --c7"

# 2. 라이브러리 질문 (자동 활성화)
"pandas DataFrame merge 방법 알려줘"
# → context7이 pandas 공식 문서 자동 로드

# 3. 특정 버전 문서
"langchain 0.3 버전 체인 구성법 --context7"

# 4. oo 스킬과 함께
oodev run --framework fastapi  # context7 자동 연계
```

## MCP 도구

| 도구 | 설명 |
|------|------|
| `mcp__context7__resolve-library-id` | 라이브러리명 → context7 ID 변환 |
| `mcp__context7__get-library-docs` | 공식 문서 로드 |

## 지원 라이브러리 (예시)

React, Vue, FastAPI, Django, pandas, numpy, PyTorch, LangChain, SQLAlchemy, Pydantic, streamlit 등 수천 개

## oo 스킬 연계

| oo 스킬 | context7 활용 |
|---------|-------------|
| `oodev` | 프레임워크 패턴 참조 |
| `oolib` | 모듈 최적화 시 문서 조회 |
| `oodb` | ORM 쿼리 패턴 조회 |

---

> 생성일: 2026-04-02 | ootutorial v01
