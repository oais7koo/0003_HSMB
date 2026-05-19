# ooskill check 체크리스트

> ooskill 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 스킬 디렉터리 스캔 | oo* 스킬 목록 수집 가능 | CRITICAL |
| C04 | agents.md 존재 | 에이전트 참조 문서 존재 | WARNING |
| C05 | 검증 기준 정의 | skill-creator 구조 검증 항목 | ERROR |
| C06 | 기본 실행 동작 | 서브명령어 없이 `oo*`만 호출 시 기본 동작 확인. run이 destructive(파일 수정 수반)한 스킬은 status/show 기본 허용, 그 외는 run이 기본이어야 함 | ERROR |
| C07 | 중복 기능 검사 | 모든 스킬(oo*)·플러그인·커맨드(.claude/commands/) 간 중복 기능 존재 여부 확인 및 리포트 | WARNING |
| C08 | 스크립트화 가능 항목 | 스킬 서브명령어 및 에이전트 처리 작업 중 AI가 직접 처리하지만 규칙적/반복적 로직으로 파이썬 스크립트화 가능한 항목 식별 및 리포트 (예: list/status/update 등 데이터 스캔·집계류, scripts/*.py 미구현 서브명령어) | WARNING |
| C09 | CLAUDE.md 스킬 등록 | .claude/CLAUDE.md의 스킬 카탈로그에 모든 oo 스킬이 등록되어 있는지 확인 | ERROR |
| C10 | 유령 스킬 제거 | CLAUDE.md `## oo 스킬` 섹션(스킬 카탈로그)에만 등록되어 있으나 실제 .claude/skills/oo*/ 디렉터리가 존재하지 않는 스킬 발견 시 카탈로그에서 삭제 (에이전트 섹션 등록은 제외) | ERROR |
| C11 | 모델 라우팅 검증 | 각 스킬 SKILL.md의 서브에이전트 테이블에서 모델(haiku/sonnet/opus) 사용 현황을 스캔하여 비용 최적화 기회 및 미명시 스킬 리포트 | WARNING |
| C12 | help 완전스크립트화 | scripts/*_run.py에 help 분기(`_print_skill_help()` 호출)가 반드시 존재해야 함 (표준: 스크립트가 SKILL.md 파싱하여 출력, AI 직접출력 금지) | ERROR |
| C13 | help 표준 표기 | `oo* help` 스크립트 출력 형식이 표준을 준수하는지 확인: `` `{스킬명} help` 서브명령어 목록: `` 헤더 + SKILL.md 서브명령어 테이블 | WARNING |
| C14 | help AI직접출력 금지 | Claude가 `oo* help` 요청 시 반드시 `uv run python .claude/skills/{스킬명}/scripts/{스킬명}_run.py help` 실행해야 함. SKILL.md 직접 읽어 출력하면 C14 위반 | ERROR |
| C15 | 에이전트 매핑 적절성 | 서브에이전트 테이블의 에이전트가 작업 유형에 맞는지 확인 (구현→task-executor, Python리뷰→python-code-reviewer, 탐색→Explore, 검증→task-checker, 품질분석→ooqa) | WARNING |
| C16 | gemma --caller 전파 | 스킬이 gemma(gemma_run.py)를 호출하는 경우 `--caller <skill>` 인자 또는 `GEMMA_CALLER` 환경변수를 반드시 전달해야 함. 미전달 시 로그 caller가 `direct`로 기록되어 스킬별 집계 불가. 현재 gemma 직접 호출 지점 없음 → 필요 시점에 개별 반영 | INFO |
| C17 | guide.md 존재 및 완전성 | 모든 oo 스킬이 `references/guide.md`를 보유하고 있는지 확인. 존재하는 경우 핵심 방법론(How)이 SKILL.md 외부로 분리되어 guide.md에 정리되어 있는지 점검. 누락 스킬은 WARNING, guide.md가 있으나 내용이 SKILL.md 수준(구조·명령어만)이면 INFO 리포트 | WARNING |
| C18 | SKILL.md/guide.md 역할 분리 | SKILL.md(명령어·구조·워크플로우)와 guide.md(방법론·코드·패턴) 간 역할 혼재 감지. ① guide.md에 `## 서브명령어` 섹션 존재 시 WARN(명령어 목록은 SKILL.md 전용), ② SKILL.md 코드블록 10개 이상 시 INFO(guide.md로 분리 권장) | WARNING |
| C19 | clean/clear/cleanup 용어 일관성 | 모든 oo* 스킬·커맨드의 서브명령어 중 `clean`·`clear`·`cleanup`이 유사 용어로 같은 의미에 혼용되는지 검사. 각 용어의 실제 동작을 비교하여 동일 의미면 하나로 통일 권고(예: 이력 정리=`clear`, 산출물 삭제=`clean`), 의미가 다르면 정의를 SKILL.md에 명시하도록 리포트 | WARNING |

## check 출력 형식

```
[ooskill check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 스킬 디렉터리 스캔           [OK]
C04 agents.md 존재         [OK]
C05 검증 기준 정의             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
