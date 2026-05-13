---
name: oofix
description: "코드 오류 자동 개선 스킬 'oofix', '오류 수정', '버그 수정', '이슈 수정' 등의 키워드로 트리거된다"
metadata:
  version: v01
  category: core-dev
---

> 에이전트 활용: .claude/guides/common_guide.md | 서브프로젝트: .claude/skills/oocontext/SKILL.md
> 상세 가이드: .claude/skills/oofix/references/guide.md

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | d{SP}0004_todo.md 활성 이슈를 서브에이전트 병렬 처리로 자동 수정 |
| **하는 것** | 코드 이슈(S/T/W) 자동 수정, 수정 후 d{SP}0010으로 이동 |
| **하지 않는 것** | 커스텀 Todo 처리(→ootodo), 이슈 발견(→oocheck), Git 커밋(→oocommit) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | 이슈 관련 코드 파일, `d{SP}0004_todo.md`, `d{SP}0010_history.md` |
| **실행 레벨** | [자동] — 3단계(분석→병렬수정→검증) 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — 병렬 서브에이전트 자동 배치 / 다른 에이전트: 이슈별 순차 처리로 대체 가능 |

## 문서 이력 관리
- v03 2026-04-23 — 동적 sys.path 패턴 [WARNING] 룰 추가 — 정적 import로 마이그레이션 권장
- v02 2026-03-29 — Flutter/Dart 지원 추가 — 프로젝트 자동 감지, Dart 에러 코드/검증/False Positive 패턴
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 개요

d{SP}0004_todo.md 이슈를 **서브에이전트 병렬 처리**로 자동 수정 -> d{SP}0010_history.md 기록.

- **컨텍스트**: --sp N 또는 oocontext N
- **역할 구분**: 에러/버그 -> d{SP}0004_todo.md, 개발 작업 -> d{SP}0002_plan.md
- **병행 처리**: SP!=00일 때 d0004 AND d{SP}0004 모두 확인/수정
- **3단계**: Phase 1(분석) -> Phase 2(병렬 수정) -> Phase 3(검증/문서)
- **다중 언어**: Python (.py) + Flutter/Dart (.dart) 지원 — 프로젝트 자동 감지

### oofix vs ootodo 역할 구분

- **oofix**: d0004의 "현재 이슈 (Active Issues)" 섹션을 관리. oocheck가 발견한 코드 에러(S/T/W 이슈)를 서브에이전트 병렬로 자동 수정하는 **코드 이슈 전문 수정기**.
- **ootodo**: d0004의 "커스텀 Todo" 섹션을 관리. 사용자가 직접 추가한 할 일을 처리하며, 코딩(oodev 위임)과 비코딩(문서, 분석 등 직접 처리) 모두 대응하는 **범용 할 일 관리자**.
- **공통점**: 둘 다 d0004_todo.md를 읽고, 완료 시 d0010_history.md에 기록.
- **차이점**: 다루는 섹션(현재 이슈 vs 커스텀 Todo), 작업 범위(코드 전용 vs 범용), 처리 방식(3단계 병렬 분석/수정/검증 vs 단순 위임)이 다름.

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oofix help` | 서브명령어 목록 표시 |
| `oofix version` | 스킬 버전 정보 (v01) |
| `oofix status` | 서브명령어 리스트, 이슈 상태 |
| `oofix check` | references/checklist.md 기반 체크 및 리포팅 |
| oofix show checklist | 역할 수행 체크리스트 표시 |
| oofix add checklist "항목" | 체크리스트 항목 추가 |
| oofix run | 이슈 자동 수정 (병렬) |
| **oofix run this** | **직전 작업 파일 이슈 수정** (→ common_guide.md §9) |
| oofix run [대상] | 특정 이슈/파일/카테고리 |
| oofix improve [대상] | d0004 이슈 없이 품질/성능/보안 개선 (improve 흡수) |
| oofix preview | 수정 미리보기 |
| oofix test | 테스트 실행 |
| oofix verify | 수정 검증 |
| oofix rollback | 롤백 |

**옵션**: --interactive, --force, --no-history, --sequential
improve 옵션: `--focus performance\|security\|quality\|readability`, `--scope file\|module\|project`, `--preserve-api`, `--measure`

## 3. 병렬 처리

### 3.1 구조

```
메인 에이전트 (Phase 1,3: 분석/검증)
    | Task(run_in_background=true)
    |-- Agent 1~3: 영역별 수정
```

### 3.2 에이전트

**Python 프로젝트:**

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| codebase-investigator | opus | 영향 범위 분석 |
| python-code-reviewer | opus | 코드 품질/버그 |
| task-executor (1~3) | opus | 영역별 수정 |
| task-checker | opus | 수정 검증 |

**Flutter/Dart 프로젝트:**

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| codebase-investigator | opus | 영향 범위 분석 |
| code-reviewer | opus | Dart 코드 품질/패턴 |
| task-executor (1~3) | opus | 영역별 수정 |
| task-checker | opus | 수정 검증 |

### 3.3 병렬화 기준

| 병렬화 | 이슈 |
|--------|------|
| 낮음 | E0611 (export), E0102 (중복) - 우선 순차 처리 |
| 높음 | E0606, E1101, E0704, W0612 - 파일별 독립 |

### 3.4 처리 시간

| 구분 | 순차 | 병렬 |
|------|------|------|
| Phase 2 | 60분+ | 15-20분 |
| 총계 | 75분+ | 30-35분 |

## 4. 워크플로우

**Phase 1** (메인): todo 파싱 -> False Positive 필터 -> 우선순위 -> 병렬 계획

**Phase 2** (서브에이전트):
- 우선: oo/__init__.py export, E0102
- 병렬: Agent별 영역 수정 -> py_compile 검증

**Phase 3** (메인): 검증 -> d{SP}0004_todo.md 업데이트 -> d{SP}0010_history.md 기록

## 5. False Positive

> Python: .claude/guides/debugging_guide.md 섹션 4 참조

### 5.1 Flutter/Dart False Positive 패턴

| 패턴 | 이유 |
|------|------|
| `*.g.dart` (generated) | 코드 생성 파일 — 수정 금지 |
| `*.freezed.dart` | Freezed 생성 파일 — 수정 금지 |
| `firebase_options.dart` | Firebase CLI 생성 — 수정 금지 |
| `*.mocks.dart` | Mockito 생성 파일 — 수정 금지 |
| platform-specific 경고 | Android/iOS 네이티브 코드 경고 — 무시 |

## 6. 이슈별 수정 전략

### 6.1 Python 에러 코드

| 코드 | 이슈 | 수정 |
|------|------|------|
| E0611 | export 누락 | __init__.py import 추가 |
| E0102 | 중복 정의 | 첫 번째만 유지 |
| E0606 | 변수 미할당 | 초기화/로직 수정 |
| E1101 | 멤버 누락 | 올바른 멤버명 |
| E0704 | raise 오류 | except 블록 내 이동 |
| W0611/W0612 | 미사용 | 삭제 또는 _ prefix |

### 6.2 동적 sys.path 패턴 [WARNING]

> `sys.path.insert/append`로 런타임에 경로를 주입하는 패턴은 pylint 정적 분석을 우회하여
> **import 오류를 숨길 수 있다**. 발견 시 [WARNING]으로 등록하고 정적 import로 교체를 권장한다.

**감지 패턴**:
```python
# 감지 대상
sys.path.insert(0, some_path)
sys.path.append(some_path)
from some.module import something   # 위 sys.path 이후 위치한 import
```

**권장 수정 방향**:
- 모듈을 `oais/` 또는 표준 패키지로 이전 → 정적 import 사용
- `pyproject.toml`의 `[tool.uv.sources]` 또는 패키지 구조 개선으로 경로 문제 근본 해결

**수정 시 주의**: 동적 sys.path 제거 후 반드시 `ootest run --runtime`으로 import 검증 실행

### 6.2 Flutter/Dart 에러 코드

| 코드 | 이슈 | 수정 |
|------|------|------|
| unused_import | 미사용 import | import 문 삭제 |
| unused_local_variable | 미사용 로컬 변수 | 삭제 또는 _ prefix |
| unused_field | 미사용 필드 | 삭제 또는 _ prefix |
| dead_code | 도달 불가 코드 | 삭제 |
| undefined_identifier | 미정의 식별자 | import 추가 또는 선언 |
| invalid_assignment | 타입 불일치 | 타입 캐스팅 또는 수정 |
| missing_return | return 누락 | return 문 추가 |
| unnecessary_import | 불필요 import | 삭제 |
| prefer_const_constructors | const 미사용 | const 추가 |
| prefer_final_fields | final 미사용 | final 추가 |
| unnecessary_this | 불필요한 this | this. 제거 |
| avoid_print | print() 사용 | debugPrint() 또는 logger 전환 |

## 7. 검증

### 7.1 Python 프로젝트

**필수**: uv run python -m py_compile <파일> (common_guide.md 2.8 참조)

수정 -> py_compile -> 오류 시 재수정 -> pytest -> 완료

### 7.2 Flutter/Dart 프로젝트

**필수**: dart analyze <파일 또는 디렉토리>

수정 -> dart analyze -> 오류 시 재수정 -> flutter test -> 완료

**추가 도구**:
- `dart fix --apply` — 자동 수정 가능한 lint 이슈 일괄 적용
- `dart format --set-exit-if-changed` — 포맷팅 검증

## 8. 완료 조건

| 조건 | 검증 |
|------|------|
| 이슈 해결 | d0004 AND d{SP}0004 "현재 이슈" 비움 (SP!=00) |
| 구문 정상 | py_compile 통과 |
| 테스트 통과 | pytest 성공 |
| 문서 기록 | d0010 AND d{SP}0010 history (SP!=00) |

## 9. 에러 처리

- **수정 실패**: 원본 유지 -> todo 상세 추가
- **검증 실패**: rollback -> 대안 제시
- **에이전트 실패**: 3회 재시도 -> 메인 직접 처리

## 10. 주의사항

- **수정 제한**: 복잡 로직, DB 스키마, 프로덕션 직접 수정 불가
- **안전**: preview 사전 확인, --interactive 단계별, git 커밋 후 수정

> **관련 문서**: `.claude/skills/oocheck/SKILL.md` | `.claude/skills/oolib/SKILL.md` | `00_doc/d{SP}0004_todo.md` | `00_doc/d{SP}0010_history.md`

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 이슈 분석 | `Explore` | haiku | O |
| 에러 검사 | `code-error-checker` | opus | O |
| 자동 수정 | `task-executor` | opus | O |
| 결과 검증 | `task-checker` | opus | - |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.claude/rules/karpathy-guidelines.md`

| # | 원칙 | 핵심 규칙 |
|---|------|----------|
| 1 | **Think Before Coding** | 가정 명시, 불확실하면 질문, 해석이 여러 개면 제시 (혼자 결정 금지) |
| 2 | **Simplicity First** | 요청된 최소 코드만, 투기적 추상화·유연성·에러처리 금지 |
| 3 | **Surgical Changes** | 요청 범위 밖 코드 "개선" 금지, 기존 스타일 유지, 자기가 만든 쓰레기만 치움 |
| 4 | **Goal-Driven Execution** | 검증 가능한 성공 기준으로 변환 후 루프 (예: 버그 수정 → 재현 테스트 작성 → 통과) |

**트레이드오프**: 속도보다 신중함. 사소한 작업엔 판단력 발휘.

<!-- KARPATHY-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

