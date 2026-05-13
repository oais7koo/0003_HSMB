# SKILL.md 완성 템플릿

> `ootutorial`이 관리하는 oo 스킬용 `SKILL.md` 완성형 템플릿

```yaml
---
name: oo{skill_name}
description: "{스킬 한 줄 설명}. 'oo{skill_name}', '{트리거 키워드1}', '{트리거 키워드2}' 등을 요청할 때 트리거된다"
metadata:
  version: "v01"
  category: "core-dev|doc-env|meta-util|content"
---
```

```md
# oo{skill_name} - {스킬 제목}

> {한 줄 목적 설명} | ref: `{주요 참조 문서 또는 경로}`

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | {이 스킬이 반드시 해결하는 핵심 문제} |
| **하는 것** | {핵심 기능 3~5개} |
| **하지 않는 것** | {이 스킬이 다루지 않는 범위 / 다른 스킬로 넘길 범위} |
| **참조 범위** | {문서 / 코드 / DB / 외부 시스템 범위} |
| **수정 대상** | {어떤 파일/문서를 수정하는지, 또는 읽기 전용인지} |
| **실행 레벨** | [자동]\|[반자동]\|[수동] — {언제 실행되는지} |
| **에이전트 호환** | {권장 에이전트 / 대체 실행 방식} |

## 문서 이력 관리
- v01 {YYYY-MM-DD} — 초기 작성

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oo{skill_name} help` | 서브명령어 목록 표시 |
| `oo{skill_name} version` | 스킬 버전 정보 (v01) |
| `oo{skill_name} status` | 서브명령어 리스트, 스킬 상태 |
| `oo{skill_name} check` | references/checklist.md 기반 체크 및 리포팅 |
| `oo{skill_name} show checklist` | 역할 수행 체크리스트 표시 |
| `oo{skill_name} add checklist "항목"` | 체크리스트 항목 추가 |
| `oo{skill_name} run` | 기본 실행 |
| `oo{skill_name} {custom_subcommand}` | {선택: 스킬 전용 서브명령어 설명} |

실행: `uv run python .claude/skills/oo{skill_name}/scripts/oo{skill_name}_run.py`

> 스크립트가 없는 읽기 전용 스킬이면 실행 줄을 제거하고, 문서형 스킬임을 명시한다.

---

## 워크플로우

**{시작 조건}** → **{분석/판단}** → **{실행}** → **{검증/기록}** → **{종료 조건}**

### 1. 입력 확인

- {필수 입력 1}
- {필수 입력 2}
- {없으면 기본값 또는 실패 조건}

### 2. 대상 탐색

- {문서 / 파일 / 코드 / DB 탐색 규칙}
- {컨텍스트 우선순위}
- {자동 감지 규칙}

### 3. 실행 규칙

1. {실행 단계 1}
2. {실행 단계 2}
3. {실행 단계 3}

### 4. 결과 처리

- {수정 결과 저장 위치}
- {history / todo / report 반영 위치}
- {실패 시 처리 방식}

---

## 입출력 정의

### 입력

| 항목 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| `{input_1}` | `{str\|file\|path\|doc}` | O | {설명} |
| `{input_2}` | `{str\|file\|path\|doc}` | - | {설명} |

### 출력

| 출력 | 형식 | 설명 |
|------|------|------|
| 터미널 출력 | 텍스트 | {요약 / 상태 / 에러 메시지} |
| 수정 파일 | 파일 | `{수정 대상 경로}` |
| 생성 파일 | 파일 | `{생성 대상 경로 또는 없음}` |

---

## 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|
| 분석 | {agent_name} | {haiku\|sonnet\|opus} | {용도} |
| 실행 | {agent_name} | {haiku\|sonnet\|opus} | {용도} |
| 검증 | {agent_name} | {haiku\|sonnet\|opus} | {용도} |

> 단일 스킬에서 서브에이전트를 쓰지 않으면 이 섹션을 삭제하거나 "없음"으로 표기한다.

---

## 예외 / 제한사항

- {금지 사항 1}
- {환경 의존성 1}
- {사용자가 알아야 할 제약 1}

### 실패 시 대응

| 상황 | 대응 |
|------|------|
| {입력 누락} | {에러 메시지 또는 ask_user 유도} |
| {대상 파일 없음} | {생성 / 중단 / 대체 경로} |
| {외부 시스템 실패} | {재시도 / skip / 명시적 실패} |

---

## 체크리스트 연동

- `references/checklist.md`를 사용한다.
- 최소 체크 항목:
  - 입력이 충분한가
  - 대상 문서/파일을 정확히 찾았는가
  - 수정 결과를 관련 문서에 반영했는가
  - 검증 또는 후속 확인이 필요한가

---

## 관련

`{관련 스크립트}` | `{관련 스킬 1}` | `{관련 스킬 2}` | `{관련 문서}`
```

## 사용 메모

1. frontmatter의 `name`, `description`, `metadata.version`, `metadata.category`는 필수
2. 모든 oo 스킬은 기본적으로 `help / version / status / check / show checklist / add checklist / run` 서브명령어를 우선 포함
3. 스크립트를 언급하면 실제 `scripts/oo{skill_name}_run.py`가 존재해야 함
4. 상세 내용이 길어지면 `references/`로 분리
5. 작성 후 `ooskill run` 또는 `ooskill check`로 검증
