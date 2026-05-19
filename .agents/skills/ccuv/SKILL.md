---
name: ccuv
description: "중앙 안내: `.codex/guides/common_guide.md`"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# ccuv - UV 기반 의존성 관리 워크플로우

> 중앙 안내: `.codex/guides/common_guide.md`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | UV 기반 Python 의존성 관리 (추가·업데이트·취약점 검사) |
| **하는 것** | uv add/remove/update, 취약점 스캔, pyproject.toml/uv.lock 관리 |
| **하지 않는 것** | 환경 전체 점검(→ooenv), 코드 수정(→ccfix), GPU 설치(→ccdeep) |
| **참조 범위** | 현재 프로젝트 `pyproject.toml`, `uv.lock` / 외부 레지스트리 접속 가능 |
| **수정 대상** | `pyproject.toml`, `uv.lock` |
| **실행 레벨** | [반자동] — 변경 대상 패키지 확인 후 실행 |
| **에이전트 호환** | Codex 권장 — `uv` CLI 자동 실행 / 다른 에이전트: `uv add`, `uv sync` 등 수동 실행 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ccskill run 자동)

---

## 개요

`uv` 도구를 활용하여 프로젝트의 Python 의존성을 체계적으로 관리하는 워크플로우.
`cccheck` 스킬에서 분리되어 의존성 관리에 특화된 기능을 제공.

**핵심 기능**:
- 의존성 상태 확인 (최신 버전 여부, 보안 취약점)
- 의존성 업데이트 제안 및 실행
- `uv run`을 통한 Python 스크립트 실행 지침

> **스코프 경계**: oouv는 **Python 패키지 의존성 관리** 전담. 환경 전반 점검(MCP, 스킬 정합성, 환경변수)은 `ccenv` 담당.

## 서브명령어

| 명령어 | 설명 | 관련 키워드 |
|--------|------|------------|
| `ccuv help` | 서브명령어 목록 표시 | 터미널 |
| `ccuv version` | 스킬 버전 정보 (v02) | `버전`, `version` |
| `ccuv status` | 서브명령어 리스트, 현재 상태 | `상태`, `status` |
| `ccuv check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ccuv show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ccuv add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `ccuv check` | 의존성 상태 체크 (오래된/취약점 패키지) | `업데이트`, `의존성`, `패키지`, `취약점` |
| `ccuv update` | 오래된/취약점 패키지 업데이트 (실행) | `업데이트`, `패치`, `uv update` |
| `ccuv run` | `uv run`을 사용하여 파이썬 스크립트 실행 | `uv run`, `실행`, `파이썬` |

## 의존성 관리

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

## cccheck 연동

```
cccheck 실행 시:
  - (선택적) ccuv check를 호출하여 의존성 상태를 확인
  - 문제가 발견되면 00_doc/sp00/d0004_todo.md에 기록
```

## 결과 기록 형식

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

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 의존성 분석 | `Explore` | haiku | O |
| 패키지 업데이트 | `task-executor` | sonnet | - |
| 검증 | `task-checker` | sonnet | - |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.codex/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .agents/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Codex 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.agents/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

## 관련 문서

- `00_doc/sp00/d0004_todo.md` - Todo 및 디버깅 관리
- `.agents/skills/cccheck/SKILL.md` - 통합 코드 품질 체크 워크플로우 (연동)
