---
name: ccreview
description: "참조: .claude/guides/common_guide.md | .claude/skills/oocontext/SKILL.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

> 참조: .claude/guides/common_guide.md | .claude/skills/oocontext/SKILL.md
> 결과: 리뷰 이슈 → d{SP}0004_todo.md | 상세 리뷰 → 터미널 출력
> 상세 체크리스트: .claude/skills/ccreview/references/checklist.md

**옵션**: --sp N (서브프로젝트) | --codex (Codex 2차 리뷰 강제) | --no-codex (Codex 생략)
**에이전트**: code-reviewer(opus), security-reviewer(sonnet), quality-reviewer(sonnet), codex:rescue

> ⚠️ **필수**: 리뷰는 반드시 Agent 도구로 위임할 것. 직접 처리 금지.
> 순서: explore(haiku) 스캔 → 3-way 병렬 리뷰 → Codex 2차 의견 → 결과 합산

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 설계·패턴·보안·성능 판단 기반 AI 코드 리뷰 (oocheck 정적 분석과 다름) |
| **하는 것** | code-reviewer·security-reviewer·quality-reviewer 병렬 리뷰, 이슈 d{SP}0004 등록 |
| **하지 않는 것** | 정적 분석(→oocheck), 이슈 수정(→oofix), 코드 구현(→oodev) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `d{SP}0004_todo.md` (리뷰 이슈 등록만, 코드 수정 안 함) |
| **실행 레벨** | [자동] — 병렬 리뷰 에이전트 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — opus 모델 병렬 에이전트 자동 배치 / 다른 에이전트: 리뷰 항목별 순차 처리로 대체 |

## 문서 이력 관리
- v02 2026-04-19 — 이슈 자동등록 + SP별 단일 등록 원칙 (이중등록 제거)
- v01 2026-04-08 — 최초 생성 — code-reviewer + Codex 이중 리뷰 구조

---

## oocheck vs ccreview

| 항목 | oocheck | ccreview |
|------|---------|----------|
| 방식 | 도구 실행 (pylint, mypy) | AI 판단 |
| 대상 | 문법·타입·lint 오류 | 설계·패턴·보안·성능 |
| 결과 | PASS/FAIL, 에러 코드 | 개선 제안, 리뷰 코멘트 |
| 실행 | 자동 | 에이전트 위임 |

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccreview help` | 서브명령어 목록 |
| `ccreview run` | 현재 SP 전체 리뷰 |
| `ccreview run [파일/디렉토리]` | 특정 대상만 리뷰 |
| `ccreview run this` | 직전 작업 파일만 리뷰 (common_guide.md §9) |
| `ccreview run dXXXX` | 상세 문서 기반 관련 코드만 리뷰 |
| `ccreview security` | 보안 집중 리뷰 (security-reviewer + Codex) |
| `ccreview design` | 아키텍처/설계 집중 리뷰 (architect + code-reviewer) |
| `ccreview codex [파일]` | Codex 단독 2차 리뷰 |
| `ccreview status` | 미해결 리뷰 이슈 현황 |

## 워크플로우

### 표준 흐름 (ccreview run)

> 코드 예시: references/guide.md 참조

### Codex 활용 상세

Codex는 Claude와 다른 관점에서 코드를 분석하여 Claude가 놓친 이슈를 발견함.

> 코드 예시: references/guide.md 참조

**Codex 리뷰 프롬프트 템플릿** (references/codex_prompts.md 참조):
- 일반: `"Review [file] for bugs, design issues, and improvements. Give line-specific feedback."`
- 보안: `"Security audit [file]: injection, auth bypass, data exposure, input validation."`
- 성능: `"Performance review [file]: bottlenecks, inefficient patterns, memory issues."`

### ccreview run dXXXX

> 코드 예시: references/guide.md 참조

## 리뷰 범주 및 심각도

| 범주 | 에이전트 | 예시 |
|------|---------|------|
| [DESIGN] | code-reviewer | 과도한 결합, SRP 위반, API 계약 불명확 |
| [SECURITY] | security-reviewer | SQL Injection, 하드코딩 시크릿, 권한 미검증 |
| [QUALITY] | quality-reviewer | O(n²) 루프, 중복 로직, 300줄 초과 함수 |
| [LOGIC] | Codex | 엣지 케이스 누락, 오프바이원, 레이스 컨디션 |
| [COMPAT] | code-reviewer | 하위 호환성 파괴, deprecated API 사용 |

심각도: [CRITICAL] 즉시 | [ERROR] 24h | [WARNING] 1주 | [INFO] 백로그

## 결과 기록

등록 원칙:
- SP==00: `d0004_todo.md`에 등록
- SP!=00: `d{SP}0004_todo.md`에만 등록 (d0004 중복 등록 금지 — 관리 혼선 방지)
- 확인 없이 자동 등록

등록 형식:

> 코드 예시: references/guide.md 참조

## 리뷰 리포트 출력 형식

> 코드 예시: references/guide.md 참조

## GSD 연계

| 시나리오 | 명령어 |
|---------|--------|
| 페이즈 완료 전 리뷰 | `ccreview run` → `/gsd:validate-phase` |
| PR 전 종합 리뷰 | `ccreview run` → `oocommit run` |
| 보안 감사 | `ccreview security` → `/gsd:forensics` |

## 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 파일 탐색 | Explore | haiku | 대상 파일 스캔 및 변경 범위 파악 | - |
| 설계/패턴 리뷰 | code-reviewer | opus | 설계·패턴·API 계약·하위 호환성 검토 | O |
| 보안 리뷰 | security-reviewer | sonnet | OWASP Top10·인증·인가·민감정보 검토 | O |
| 품질 리뷰 | quality-reviewer | sonnet | 성능·복잡도·유지보수성 검토 | O |
| Codex 2차 리뷰 | codex:rescue / omc-teams codex | - | 엣지케이스·로직 결함 2차 의견 | O |
| 결과 합산 | (메인) | - | 리뷰 리포트 집계 및 출력 | - |

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oocheck` | 선행 — 자동 정적 분석 |
| `oofix` | 후행 — 리뷰 이슈 수정 |
| `oocommit` | 후행 — 리뷰 완료 후 커밋 |

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

