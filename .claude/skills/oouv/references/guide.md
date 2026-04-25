# oouv_guide - UV 기반 의존성 관리 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oouv/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

oouv는 `uv` 도구를 활용하여 프로젝트의 Python 의존성을 체계적으로 관리하는 스킬입니다.

### 1.1 핵심 기능

- 의존성 상태 확인 (최신 버전 여부, 보안 취약점)
- 의존성 업데이트 제안 및 실행
- `uv run`을 통한 Python 스크립트 실행 지침

### 1.2 oocheck와의 차이

`oocheck`에서 분리되어 **의존성 관리에 특화**:

| 스킬 | 역할 |
|------|------|
| `oocheck` | 코드 구문 및 로직 오류 검사 |
| `oouv` | 의존성 레벨 건강 상태 관리 |

---

## 2. 워크플로우

### 2.1 기본 흐름

```
pyproject.toml / uv.lock 분석
    ↓
의존성 상태 체크 (오래된 패키지, 보안 취약점)
    ↓
업데이트 제안 (버전, 우선순위)
    ↓
사용자 승인
    ↓
uv update 실행
    ↓
결과 검증 및 d0004 기록
```

### 2.2 oocheck 연동

```
oocheck 실행 시:
  - (선택적) oouv check 호출하여 의존성 상태 확인
  - 문제 발견 시 00_doc/sp00/d0004_todo.md에 기록
```

---

## 3. 상세 사용법

### 3.1 명령어

| 명령어 | 설명 | 역할 |
|--------|------|------|
| `oouv version` | 스킬 버전 정보 (v02) | 버전 확인 |
| `oouv check` | 의존성 상태 체크 | 오래된/취약점 패키지 감지 |
| `oouv update` | 오래된/취약점 패키지 업데이트 | 업데이트 실행 |
| `oouv run` | `uv run`을 사용하여 파이썬 스크립트 실행 | 실행 |

### 3.2 의존성 체크

**목적**: 프로젝트의 `pyproject.toml` 및 `uv.lock` 기반 의존성 상태 확인

**검사 항목**:
- 오래된 패키지 감지: 설치된 패키지 중 최신 버전 확인
- 보안 취약점 감지: 알려진 보안 취약점이 있는 패키지 식별

**실행 예시**:
```bash
# 전체 의존성 상태 확인
oouv check
```

### 3.3 의존성 업데이트

**목적**: 오래되거나 취약점이 있는 패키지 업데이트

**모드**:
- **제안 모드**: 업데이트 가능한 패키지 목록과 권장 버전 표시
- **자동 업데이트**: `uv update` 명령 사용하여 `uv.lock` 파일 업데이트

**실행 예시**:
```bash
# 오래된 의존성 업데이트 실행
oouv update
```

### 3.4 Python 실행 지침: `uv run`

**중요 원칙**: 프로젝트 내 Python 스크립트는 **항상 `uv run` 사용**

**이유**:
- `uv`가 관리하는 가상 환경 내에서 실행 보장
- 의존성 불일치 문제 방지
- 일관된 실행 환경 제공

**실행 예시**:
```bash
# main.py 스크립트 실행
uv run python src/main.py

# 다른 스크립트 실행
uv run python .claude/skills/oocheck/scripts/oocheck_py_compile.py
```

---

## 4. 사용 예시

### 4.1 의존성 관리 워크플로우

```bash
# 1. 현재 상태 확인
oouv check

# 2. 문제 발견 시 업데이트
oouv update

# 3. 스크립트 실행 (uv run 사용)
oouv run python src/main.py
```

### 4.2 결과 기록

검출된 의존성 문제는 `00_doc/sp00/d0004_todo.md`에 기록:

```markdown
#### TODO-XXX [DEP] 의존성 문제 제목
- **우선순위**: 높음/중간/낮음
- **관련 패키지**: `패키지명`
- **문제**: 문제 설명 (예: 오래된 버전, 보안 취약점)
- **영향**: 프로젝트에 미치는 영향 설명
- **조치**: 권장 해결 방안 (예: `uv update <package_name>`)
- **등록일**: YYYY-MM-DD
```

### 4.3 일반적인 시나리오

**시나리오 1: 정기 점검**
```bash
# 매주 금요일 의존성 점검
oouv check

# 오래된 패키지 발견 시
oouv update
```

**시나리오 2: 보안 취약점 대응**
```bash
# 보안 취약점 확인
oouv check

# 긴급 업데이트
oouv update

# 테스트 실행 (uv run 사용)
oouv run python -m pytest tests/
```

**시나리오 3: 새 패키지 설치 후**
```bash
# 패키지 설치
uv add requests

# 의존성 상태 확인
oouv check

# 스크립트 실행
oouv run python src/api_client.py
```

---

## 5. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/oouv/SKILL.md` | 스킬 정의 |
| `.claude/skills/oocheck/SKILL.md` | 통합 코드 품질 체크 워크플로우 (연동) |
| `00_doc/sp00/d0004_todo.md` | Todo 및 디버깅 관리 |
| `.claude/guides/common_guide.md` | 공통 개발 표준 |
