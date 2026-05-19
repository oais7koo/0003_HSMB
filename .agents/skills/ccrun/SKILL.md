---
name: ccrun
description: "이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다."
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->

# ccrun - TDD 기반 자율 실행 스킬 (Builder)

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | TDD 기반 프로젝트 자율 실행 (Builder) — 빌드·테스트·배포 자동화 |
| **하는 것** | 빌드 스크립트 실행, TDD 사이클 자율 진행, 실행 환경 설정 |
| **하지 않는 것** | 코드 구현(→ccdev), 정적 분석(→cccheck), 이슈 수정(→ccfix) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 서버 자동 배포 안 함 |
| **수정 대상** | 빌드 산출물, 실행 환경 설정 |
| **실행 레벨** | [자동] — 빌드·테스트 자동 실행 |
| **에이전트 호환** | Codex 권장 — `uv run` 기반 자동 실행 / 다른 에이전트: 빌드 명령을 수동 실행 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ccskill run 자동)

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccrun help` | 서브명령어 목록 표시 |
| `ccrun version` | 스킬 버전 정보 (v02) |
| `ccrun status` | 실행 큐 상태 확인 |
| `ccrun check` | references/checklist.md 기반 체크 및 리포팅 |
| `ccrun run` | 프로젝트 실행 |
| `ccrun show checklist` | 역할 수행 체크리스트 표시 |
| `ccrun add checklist "항목"` | 체크리스트 항목 추가 |
| `ccrun [태스크ID]` | 특정 태스크 실행 |
| `ccrun --auto` | 자동 TDD 사이클 실행 |

## 개요

**Architect vs Builder**:
- **Architect (`ccplan`)**: 무엇을 어떻게 만들지 결정(상세 설계)하여 실행 큐에 등록
- **Builder (`ccrun`)**: 실행 큐의 작업을 고민 없이 수행하고 결과 도출

**입력**: 실행 큐(Execution Queue) from `ccplan detail`, `00_doc/sp00/d0002_plan.md`

**출력**: 구현된 소스 코드, 통과된 테스트 코드, 업데이트된 문서

## TDD 서브에이전트 매핑

| TDD 단계 | 서브에이전트 | 모델 | 용도 |
|----------|--------------|------|------|
| 사전 분석 (선택) | `codebase-investigator` | sonnet | 복잡한 구현 전 의존성/영향 분석 |
| RED (테스트 작성) | `task-executor` | sonnet | 실패하는 테스트 코드 작성 |
| GREEN (구현) | `task-executor` | sonnet | 테스트 통과를 위한 최소 구현 |
| REFACTOR (개선) | `python-code-reviewer` | sonnet | 코드 품질 리뷰 및 개선 제안 |
| 검증 | `task-checker` | sonnet | 태스크 완료 여부 검증 |
| 품질 보증 | `ccqa` | sonnet | 중복 검사, 의존성 분석 |
| 에스컬레이션 | `codebase-investigator` | sonnet | TDD 실패 시 근본 원인 분석 |

## TDD 실행 사이클

```
1. RED (테스트 작성)
   - 입력: 태스크 요구사항
   - 행동: 실패하는 테스트 코드 작성 (pytest)
   - 검증: 테스트가 실패하는지 확인

2. GREEN (구현)
   - 입력: 실패하는 테스트
   - 행동: 테스트를 통과하는 최소한의 코드 작성
   - 검증: 테스트가 통과하는지 확인

3. REFACTOR (개선)
   - 입력: 통과한 코드
   - 행동: 중복 제거, 가독성 향상, 주석 추가
   - 검증: 테스트 통과 유지, Lint/Type Check 통과

4. COMPLETE (완료 처리)
   - 행동: 문서 업데이트, 커밋, 다음 태스크로 이동
```

## 명령어 체계

| 명령어 | 설명 | 역할 |
|--------|------|------|
| `ccrun` | 대기 중인 실행 큐 처리 (기본) | 구현 실행 |
| `ccrun execute [ID]` | 특정 태스크 즉시 실행 | 단일 실행 |
| `ccrun all` | 프로젝트 전체 점검 | 유지보수 |
| `ccrun status` | 현재 진행 상태 및 큐 확인 | 모니터링 |
| `ccrun resume` | 중단된 작업 재개 | 실행 제어 |

### 옵션

| 옵션 | 설명 |
|------|------|
| `--max-iterations N` | TDD 반복 최대 횟수 (기본: 10) |
| `--timeout M` | 태스크당 최대 시간(분) (기본: 30) |
| `--interactive` | 각 단계마다 사용자 승인 대기 |
| `--skip-refactor` | Refactor 단계 건너뛰기 |
| `--report` | 실행 리포트 생성 (`tmp/oorun_report.md`) |

## ccrun all (프로젝트 건강검진)

1. **cccheck**: 정적 분석 및 에러 체크
2. **ccfix run**: 발견된 단순 에러 자동 수정
3. **cctest**: 전체 테스트 스위트 실행
4. **cclib**: 모듈 문서 현행화
5. **ccdb**: DB 스키마 문서 현행화

## 에스컬레이션 조건

1. **반복 횟수 초과**: 10회 이상 시도해도 테스트 통과 실패
2. **모호한 요구사항**: `ccplan` 정보로 구현 불가
3. **환경 문제**: 패키지 설치 실패, API 연결 불가

## 병렬 실행 권장 케이스

| 조건 | 병렬 실행 방식 |
|------|----------------|
| 복잡한 태스크 사전 분석 | `codebase_investigator` + `Explore` |
| 독립된 태스크 다수 | 여러 `task-executor` 동시 실행 |
| REFACTOR 단계 | `python-code-reviewer` + `ccqa` |
| 전체 점검 (all) | 각 스킬별 에이전트 병렬 |

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.codex/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- KARPATHY-REF:START -->

## Karpathy 코딩 가이드라인 (필수 준수)

> 이 스킬은 코딩 작업 수행 시 **`/andrej-karpathy-skills:karpathy-guidelines`** 스킬의 4원칙을 준수한다.
> 로컬 미러: `.codex/rules/karpathy-guidelines.md`

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

| 문서 | 용도 |
|------|------|
| `.agents/skills/ccplan/SKILL.md` | Architect - 상세 설계 및 태스크 공급 |
| `.agents/skills/cccheck/SKILL.md` | 코드 품질 기준 정의 |
| `.agents/skills/cctest/SKILL.md` | 테스트 실행 가이드 |
| `00_doc/sp00/d0002_plan.md` | 전체 구현 계획 |
| `00_doc/sp00/d0004_todo.md` | 이슈 및 완료 처리 |
