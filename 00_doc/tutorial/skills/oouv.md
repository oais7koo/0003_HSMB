# oouv Tutorial

> UV 기반 의존성 관리 스킬 | 버전: v02 | 카테고리: meta-util

## 1. 이 스킬은 왜 필요한가?


**이런 상황에서 사용합니다:**
- 의존성 상태 확인 (최신 버전 여부, 보안 취약점)
- 의존성 업데이트 제안 및 실행
- `uv run`을 통한 Python 스크립트 실행 지침

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oouv run

# 상태 확인
oouv status

# 도움말
oouv help
```

## 3. 전체 서브명령어

| 명령어 | 설명 | 관련 키워드 |
|--------|------|------------|
| `oouv help` | 서브명령어 목록 표시 | 터미널 |
| `oouv version` | 스킬 버전 정보 (v02) | `버전`, `version` |
| `oouv status` | 서브명령어 리스트, 현재 상태 | `상태`, `status` |
| `oouv check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `oouv show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `oouv add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `oouv check` | 의존성 상태 체크 (오래된/취약점 패키지) | `업데이트`, `의존성`, `패키지`, `취약점` |
| `oouv update` | 오래된/취약점 패키지 업데이트 (실행) | `업데이트`, `패치`, `uv update` |
| `oouv run` | `uv run`을 사용하여 파이썬 스크립트 실행 | `uv run`, `실행`, `파이썬` |

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | UV 기반 Python 의존성 관리 (추가·업데이트·취약점 검사) |
| **하는 것** | uv add/remove/update, 취약점 스캔, pyproject.toml/uv.lock 관리 |
| **하지 않는 것** | 환경 전체 점검(→ooenv), 코드 수정(→oofix), GPU 설치(→oodeep) |
| **참조 범위** | 현재 프로젝트 `pyproject.toml`, `uv.lock` / 외부 레지스트리 접속 가능 |
| **수정 대상** | `pyproject.toml`, `uv.lock` |
| **실행 레벨** | [반자동] — 변경 대상 패키지 확인 후 실행 |
| **에이전트 호환** | Claude Code 권장 — `uv` CLI 자동 실행 / 다른 에이전트: `uv add`, `uv sync` 등 수동 실행 |

### 의존성 관리

### 의존성 체크

`pyproject.toml` 및 `uv.lock` 파일 기반으로 의존성 상태 확인:
- **오래된 패키지 감지**: 설치된 패키지 중 최신 버전이 있는지 확인
- **보안 취약점 감지**: 알려진 보안 취약점이 있는 패키지 식별

### 의존성 업데이트

- **제안 모드**: 업데이트 가능한 패키지 목록과 권장 버전 표시
- **자동 업데이트**: `uv update` 명령으로 `uv.lock` 파일 업데이트

### Python 실행 지침: `uv run`

프로젝트 내 Python 스크립트는 항상 `uv run` 명령으로 실행:

```bash
uv run python src/main.py
```

### oocheck 연동

```
oocheck 실행 시:
  - (선택적) oouv check를 호출하여 의존성 상태를 확인
  - 문제가 발견되면 00_doc/sp00/d0004_todo.md에 기록
```

### 결과 기록 형식

검출된 의존성 문제는 `00_doc/sp00/d0004_todo.md`에 기록:

```markdown
#### TODO-XXX [DEP] 의존성 문제 제목
- **우선순위**: 높음/중간/낮음
- **관련 패키지**: `패키지명`
- **문제**: 문제 설명
- **영향**: 프로젝트에 미치는 영향
- **조치**: 권장 해결 방안
- **등록일**: YYYY-MM-DD
```

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oouv run
```

### 서브명령어 활용
```bash
oouv update  # 오래된/취약점 패키지 업데이트 (실행)
oouv run  # `uv run`을 사용하여 파이썬 스크립트 실행
```

### 스크립트 직접 실행
```bash
uv run python src/main.py
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

- `00_doc/sp00/d0004_todo.md` - Todo 및 디버깅 관리
- `.claude/skills/oocheck/SKILL.md` - 통합 코드 품질 체크 워크플로우 (연동)

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
