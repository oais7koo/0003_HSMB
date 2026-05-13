# ooskill_guide - 스킬 최적화 검증 가이드

## 문서 이력 관리
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/ooskill/SKILL.md` | 공통: `.claude/guides/common_guide.md` | 에이전트: `agents.md`

## 0. help / version 출력 형식

### help 표준 출력 형식 (예: ooskill help)

```
`ooskill help` 서브명령어 목록:

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `ooskill help`    | 서브명령어 목록 표시 | 터미널 |
| `ooskill version` | 스킬 버전 정보 (v04) | 터미널 |
| `ooskill status`  | ...                  | -      |
| ...               | ...                  | ...    |
```

### version 출력 형식

```
[스킬명] 버전: vXX
```

---

## 0b. check --checklist 출력 형식 및 워크플로우

### 출력 형식

```
[ooskill check --checklist]

| 스킬 | 파일 | C01 | C02 | 테이블 | 심각도 | 항목수 | 결과 |
|------|------|-----|-----|--------|--------|--------|------|
| ooscrap | OK | OK | OK | OK | OK | 8 | PASS |
| ooprd | OK | FAIL | FAIL | WARN | OK | 12 | FAIL |
| oodev | OK | OK | OK | WARN | OK | 6 | WARN |
...

소계: PASS:20 | WARN:5 | FAIL:3
```

### 워크플로우

```
1. .claude/skills/oo*/ 디렉터리 스캔
2. 각 스킬의 references/checklist.md 읽기
3. 표준 포맷 검증 (6개 항목)
4. 결과 테이블 출력
5. FAIL 스킬은 자동 수정 제안 (--fix 옵션 시 자동 재작성)
```

---

## 1. 개요

### 1.1 목적

`.claude/skills/oo*/SKILL.md` 스킬 파일들이 서브에이전트 위임 및 명령어 활용을 최적화하고 있는지 검증하고 자동 개선하는 스킬입니다.

### 1.2 주요 기능

- **서브에이전트 최적화**: 적절한 에이전트 활용 검증
- **명령어 연동 분석**: `.claude/commands/sc/` 명령어 활용 현황
- **병렬 처리 검증**: 독립 작업의 병렬화 여부
- **자동 개선**: validate 결과 기반 스킬 파일 자동 수정

### 1.3 검증 항목

| 검증 영역 | 내용 |
|----------|------|
| 서브에이전트 위임 | 작업 유형에 맞는 에이전트 사용 |
| 명령어 활용 | .claude/commands/sc/*.md 명령어 연동 |
| 병렬 처리 | 독립 작업의 동시 실행 패턴 |
| 중복 방지 | 불필요한 위임, 과도한 병렬화 |

---

## 2. 워크플로우

### 2.1 전체 흐름도

```
ooskill validate/run
    ↓
.claude/skills/oo*/SKILL.md 파일 목록 수집
    ↓
각 스킬 파일 분석 (병렬)
    ├─ Explore: 패턴 추출
    ├─ ooqa: 중복/누락 분석
    └─ task-executor: 개선안 생성
    ↓
최적화 기회 식별
    ├─ 위임 가능하나 직접 처리 중
    ├─ 활용 가능하나 미사용 명령어
    └─ 병렬화 가능하나 순차 처리
    ↓
validate: 권장사항 출력
run: 스킬 파일 자동 수정
    ↓
변경 사항 요약 및 검증
```

### 2.2 validate 워크플로우

**목적**: 현재 상황 검토 후 최적화 권장사항 제안

```
1. 스킬 파일 스캔
    ├─ .claude/skills/oo*/SKILL.md 목록 (22개)
    └─ 각 스킬별 패턴 추출

2. 서브에이전트 현황 분석
    ├─ 현재 사용 중인 에이전트
    ├─ Task 도구 위임 패턴
    └─ 병렬 처리 (run_in_background) 여부

3. 명령어 활용 현황 분석
    ├─ .claude/commands/sc/*.md 참조 여부
    ├─ 관련 명령어 연동 확인
    └─ 스킬 간 연동 체크

4. 최적화 기회 식별
    ├─ 권장 에이전트 매핑 비교
    ├─ 활용 가능한 명령어 식별
    └─ 병렬화 가능 작업 탐지

5. 권장사항 출력
    └─ Markdown 형식 리포트
```

### 2.3 run 워크플로우

**목적**: validate 결과 기반 자동 최적화 수행

```
1. validate 실행
    └─ 개선 항목 식별

2. 수정 계획 생성
    ├─ 에이전트 추가/변경
    ├─ 명령어 연동 추가
    └─ 병렬화 패턴 적용

3. 스킬 파일 수정 (병렬)
    ├─ task-executor: 파일 수정
    └─ task-checker: 검증

4. 변경 사항 검증
    ├─ 문법 오류 확인
    └─ 구조 일관성 체크

5. 결과 요약
    └─ 수정된 스킬, 변경 내용
```

---

## 3. 상세 사용법

### 3.1 현황 검토 (validate)

```bash
# 전체 스킬 최적화 현황 분석
ooskill validate
```

**출력**:
```markdown
# ooskill validate 결과

## 분석 대상: 22개 스킬

## 에이전트 활용 현황

| 스킬 | 현재 에이전트 | 권장 추가 | 병렬화 |
|------|-------------|----------|--------|
| oocheck | code-error-checker | ooqa | O |
| oofix | task-executor | task-checker | O |
| ootest | web-test-orchestrator | qa | O |

## 명령어 활용 현황

| 스킬 | 연동 명령어 | 권장 추가 |
|------|-----------|----------|
| oocheck | analyze | test, troubleshoot |
| oodev | implement | build |
| oodb | - | design |

## 개선 권장사항

### oocheck.md
1. [에이전트] `ooqa` 에이전트 병렬 활용 권장
   - 정적 분석 + 품질 분석 동시 실행
2. [명령어] `test`, `troubleshoot` 명령어 연동 추가 권장
   - 관련 워크플로우: analyze → test → troubleshoot

### oofix.md
1. [에이전트] 수정 후 `task-checker` 검증 위임 권장
   - 수정 완료 → 자동 검증 패턴
2. [병렬화] 다수 파일 수정 시 병렬 처리 권장

### oodb.md
1. [에이전트] `data-engineer` 활용 권장
   - DB 작업 전문 에이전트
2. [명령어] `design` 명령어 연동 추가
   - DB 스키마 설계 워크플로우
3. [병렬화] 스키마 분석 + 데이터 검증 동시 실행
```

### 3.2 자동 최적화 (run)

```bash
# 전체 스킬 자동 최적화
ooskill run

# 특정 스킬만 최적화
ooskill run oocheck
ooskill run oodb
```

**출력** (전체):
```markdown
# ooskill run 결과

## 수정된 스킬: 3개

| 스킬 | 변경 내용 |
|------|----------|
| oocheck.md | 에이전트 병렬화, 명령어 연동 추가 |
| oofix.md | task-checker 검증 단계 추가 |
| oodb.md | data-engineer 추가, design 명령어 연동 |

## 상세 변경 사항

### oocheck.md
- [+] 에이전트: ooqa (품질 분석 병렬 실행)
  ```markdown
  ## 4. 서브에이전트

  | 단계 | 에이전트 | 역할 | 병렬 |
  |------|----------|------|:----:|
  | 정적 분석 | python-code-reviewer | 코드 리뷰 | O |
  | 품질 분석 | ooqa | 중복/의존성 | O |
  ```

- [+] 명령어 연동: test, troubleshoot
  ```markdown
  ## 7. 관련 명령어

  - `analyze`: 코드 분석
  - `test`: 테스트 실행
  - `troubleshoot`: 문제 해결
  ```

- [~] 워크플로우: Task(run_in_background=true) 적용
  ```
  [python-code-reviewer] 정적 분석
          +
  [ooqa] 품질 분석 (병렬)
  ```

### oofix.md
- [+] 에이전트: task-checker (수정 검증)
  ```markdown
  ## 4. 서브에이전트

  | 단계 | 에이전트 | 역할 |
  |------|----------|------|
  | 수정 | task-executor | 코드 수정 |
  | 검증 | task-checker | 수정 검증 |
  ```

### oodb.md
- [+] 에이전트: data-engineer
- [+] 명령어: design
- [+] 병렬화: 스키마 분석 + 데이터 검증
```

**출력** (특정 스킬):
```markdown
# ooskill run oocheck 결과

## 수정된 스킬: 1개

### oocheck.md
- [+] 에이전트 섹션에 ooqa 추가
- [+] 명령어 연동 섹션에 test, troubleshoot 추가
- [~] 워크플로우에 병렬 처리 패턴 적용

완료: .claude/skills/oocheck/SKILL.md 업데이트됨
```

### 3.3 상태 확인

```bash
ooskill status
```

**출력**:
```
## ooskill 상태

스킬: ooskill.md (v01)

### 서브명령어
- ooskill status   : 서브명령어 목록, 현황, 최적화 요약
- ooskill version  : 버전 정보
- ooskill validate : 검토 후 권장사항 제안
- ooskill run      : 자동 최적화 (전체)
- ooskill run [스킬명] : 특정 스킬 최적화

### 분석 대상
- .claude/skills/oo*/SKILL.md (22개 스킬)

### 검증 항목
- 서브에이전트 위임 적절성
- 명령어 활용 현황
- 병렬 처리 패턴
```

---

## 4. 사용 예시

### 4.1 전체 스킬 최적화 검토

**시나리오**: 프로젝트 구조 개편 후 전체 스킬 점검

```bash
$ ooskill validate
```

**출력**:
```markdown
# ooskill validate 결과

## 분석 대상: 22개 스킬

## 개선 권장사항

### oocheck.md
- [에이전트] ooqa 추가 권장 (품질 분석 병렬화)
  → 정적 분석 + 품질 분석 동시 실행으로 시간 절약
- [명령어] test 연동 추가 권장
  → 에러 체크 후 테스트 실행 워크플로우 표준화

### oodb.md
- [에이전트] data-engineer 활용 권장 (DB 작업)
  → DB 스키마, 마이그레이션 전문 에이전트
- [병렬화] 스키마 분석/데이터 검증 병렬 처리 권장
  → 독립 작업 동시 실행

### ootest.md
- [명령어] analyze 연동 추가 권장
  → 테스트 전 코드 분석 워크플로우

### oolib.md
- [에이전트] python-code-reviewer 추가 권장
  → oo 모듈 리뷰 자동화

## 요약
- 에이전트 추가 권장: 5개 스킬
- 명령어 연동 권장: 4개 스킬
- 병렬화 권장: 3개 스킬
```

### 4.2 특정 스킬 최적화 실행

**시나리오**: oocheck 스킬만 개선

```bash
$ ooskill run oocheck
```

**출력**:
```markdown
# ooskill run oocheck 결과

## 수정된 스킬: 1개

### oocheck.md 변경 사항

#### 1. 에이전트 섹션 추가

**변경 전**:
```markdown
## 4. 서브에이전트

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| 정적 분석 | python-code-reviewer | 코드 리뷰 |
```

**변경 후**:
```markdown
## 4. 서브에이전트

| 단계 | 에이전트 | 역할 | 병렬 |
|------|----------|------|:----:|
| 정적 분석 | python-code-reviewer | 코드 리뷰 | O |
| 품질 분석 | ooqa | 중복/의존성 | O |
```

#### 2. 명령어 연동 섹션 추가

**추가**:
```markdown
## 7. 관련 명령어

| 명령어 | 용도 | 연동 시점 |
|--------|------|----------|
| `analyze` | 코드 분석 | 에러 체크 전 |
| `test` | 테스트 실행 | 에러 체크 후 |
| `troubleshoot` | 문제 해결 | 에러 발견 시 |
```

#### 3. 워크플로우 병렬화

**변경 전**:
```
정적 분석 (python-code-reviewer)
    ↓
에러 기록 (d0004_todo.md)
```

**변경 후**:
```
[python-code-reviewer] 정적 분석
        +
[ooqa] 품질 분석 (병렬)
    ↓
결과 통합 → d0004_todo.md
```

완료: .claude/skills/oocheck/SKILL.md 업데이트됨
```

### 4.3 다수 스킬 순차 최적화

**시나리오**: 핵심 개발 스킬 3개 개선

```bash
$ ooskill run oocheck
$ ooskill run oofix
$ ooskill run ootest
```

**또는**:
```bash
# 스크립트로 일괄 실행
for skill in oocheck oofix ootest; do
  ooskill run $skill
done
```

---

## 5. 검증 기준

### 5.1 서브에이전트 위임 검증

**원칙**: 단일 에이전트보다 멀티 에이전트 병렬 처리 우선

**작업-에이전트 매핑**:

| 작업 유형 | 권장 에이전트 | 비고 |
|----------|-------------|------|
| 코드 구현/수정 | `task-executor` | 기능 구현, 버그 수정 |
| Python 리뷰 | `python-code-reviewer` | 품질/성능/버그 검토 |
| 구현 검증 | `task-checker` | 완료 작업 QA |
| 품질/중복 분석 | `ooqa` | 중복 감지, 의존성 분석 |
| 에러 분석 | `code-error-checker` | 에러 메시지 분석 |
| E2E 웹 테스트 | `oo-web-test-orchestrator` | Playwright 테스트 |
| 데이터 분석 | `data-analyst` | 통계, 트렌드 |
| Streamlit 구현 | `streamlit-implementer` | UI 페이지 구현 |
| 웹 디자인 | `web-design-expert` | Bootstrap 기반 UI |
| 학술 연구 | `academic-researcher` | 논문/문헌 분석 |

**검증 체크리스트**:
- [ ] 독립 작업 2개 이상 → 병렬 처리 (`run_in_background=true`)
- [ ] 작업 유형에 맞는 에이전트 사용
- [ ] 단순 작업에 불필요한 위임 없음

### 5.2 명령어 활용 검증

**원칙**: `.claude/commands/sc/` 명령어로 표준화된 워크플로우 활용

**명령어 매핑**:

| 명령어 | 용도 | 연관 스킬 |
|--------|------|----------|
| `analyze` | 코드 분석 | oocheck, oolib |
| `build` | 프로젝트 빌드 | oodev |
| `cleanup` | 정리/삭제 | oofix |
| `design` | 설계 | ooprd, ooplan |
| `document` | 문서화 | oodoc |
| `estimate` | 추정 | ooplan |
| `explain` | 설명 | oohelp |
| `git` | Git 작업 | oocommit |
| `implement` | 구현 | oodev |
| `improve` | 개선 | oofix |
| `load` | 로드 | oocontext |
| `spawn` | 멀티태스킹 | ooflow |
| `task` | 작업 관리 | ooplan |
| `test` | 테스트 | oocheck |
| `troubleshoot` | 트러블슈팅 | oocheck, oofix |
| `workflow` | 워크플로우 | ooflow |

**검증 체크리스트**:
- [ ] 해당 작업에 맞는 명령어 존재 → 연동 추가
- [ ] 명령어로 대체 가능한 로직 → 호출로 변경
- [ ] 연관 명령어 체인 정의

### 5.3 병렬 처리 패턴

**병렬 처리 가능 조건**:
- 독립 작업 (상호 의존성 없음)
- 동시 실행 안전 (파일 충돌 없음)
- 성능 이득 (I/O 대기, 네트워크 호출)

**병렬 패턴 예시**:
```
[python-code-reviewer] 정적 분석
        +
[ooqa] 품질 분석 (병렬)
    ↓
결과 통합
```

---

## 6. 분석 패턴

### 6.1 스킬 파일 스캔 패턴

| 패턴 | 추출 정보 |
|------|----------|
| `에이전트:.*` | 현재 사용 중인 에이전트 |
| `Task\(.*subagent_type=` | Task 도구 에이전트 위임 |
| `run_in_background` | 병렬 처리 여부 |
| `.claude/commands/sc/.*\.md` | 명령어 참조 |
| `## 관련 스킬` | 스킬 간 연동 |

### 6.2 분석 대상

**포함**: `.claude/skills/oo*/SKILL.md` (스킬 파일 전체)

**예외**: 없음 (모든 스킬 분석)

---

## 7. 출력 형식

### 7.1 validate 출력

```markdown
# ooskill validate 결과

## 분석 대상: N개 스킬

## 에이전트 활용 현황

| 스킬 | 현재 에이전트 | 권장 추가 | 병렬화 |
|------|-------------|----------|--------|
| oocheck | code-error-checker | ooqa | O |
| oofix | task-executor | task-checker | O |

## 명령어 활용 현황

| 스킬 | 연동 명령어 | 권장 추가 |
|------|-----------|----------|
| oocheck | analyze | test, troubleshoot |
| oodev | implement | build |

## 개선 권장사항

### oocheck.md
1. [에이전트] `ooqa` 에이전트 병렬 활용 권장
2. [명령어] `test` 명령어 연동 추가 권장

### oofix.md
1. [에이전트] 수정 후 `task-checker` 검증 위임 권장
```

### 7.2 run 출력

```markdown
# ooskill run 결과

## 수정된 스킬: N개

| 스킬 | 변경 내용 |
|------|----------|
| oocheck.md | 에이전트 병렬화, 명령어 연동 추가 |
| oofix.md | task-checker 검증 단계 추가 |

## 상세 변경 사항

### oocheck.md
- [+] 에이전트: ooqa (품질 분석 병렬 실행)
- [+] 명령어 연동: test, troubleshoot
- [~] 워크플로우: Task(run_in_background=true) 적용
```

---

## 8. 서브에이전트 활용

| 단계 | 에이전트 | 역할 | 병렬 |
|------|----------|------|:----:|
| 스킬 분석 | `Explore` | 파일 탐색, 패턴 추출 | O |
| 최적화 검토 | `ooqa` | 중복/누락 분석 | O |
| 파일 수정 | `task-executor` | 스킬 파일 수정 | O |
| 검증 | `task-checker` | 수정 결과 검증 | - |

---

## 9. 관련 문서

### 9.1 스킬 파일

| 문서 | 용도 |
|------|------|
| `.claude/skills/ooskill/SKILL.md` | 스킬 정의 |
| `.claude/skills/ooskill/scripts/ooskill_run.py` | 실행 스크립트 (해당 시) |

### 9.2 참조 문서

| 문서 | 용도 |
|------|------|
| `agents.md` | 에이전트 검색 경로, 역할, 위임 규칙 |
| `.claude/agents/*.md` | 서브에이전트 정의 |
| `.claude/commands/sc/*.md` | 명령어 정의 |
| `.claude/guides/common_guide.md` | 에이전트 활용 원칙 |

### 9.3 연관 스킬

| 스킬 | 연동 시점 |
|------|----------|
| `oohelp` | .claude/CLAUDE.md 스킬 카탈로그 표시 |
| `ooskill` | 스킬 정합성 검증 |
| `ooqa` | 품질 분석 (최적화 검토 시) |

---

## 10. 체크리스트

### 10.1 validate 실행 전

- [ ] .claude/skills/oo*/SKILL.md 파일 최신 상태 확인
- [ ] agents.md 에이전트 정의 최신화
- [ ] .claude/commands/sc/*.md 명령어 목록 확인

### 10.2 run 실행 전

- [ ] validate 결과 검토
- [ ] 백업 (Git 커밋 또는 복사)
- [ ] 수정 대상 스킬 확인

### 10.3 run 실행 후

- [ ] 수정된 파일 검토
- [ ] 문법 오류 확인 (pylint)
- [ ] Git diff로 변경 확인
- [ ] oocommit으로 커밋

---

## 11. 팁 & 주의사항

### 11.1 권장 사항

- **정기 점검**: 월 1회 `ooskill validate` 실행
- **스킬 추가 시**: 즉시 `ooskill validate` 실행
- **백업**: `ooskill run` 전 Git 커밋

### 11.2 주의사항

- `run`은 파일을 직접 수정 (복구 불가)
- 수정 결과 반드시 검토 (자동 수정 오류 가능)
- 여러 스킬 동시 수정 시 충돌 주의

### 11.3 워크플로우 체이닝

```bash
# 검증 → 수정 → 커밋
ooskill validate && ooskill run && oocommit

# 특정 스킬만
ooskill run oocheck && oocommit
```

---

## 12. FAQ

**Q1. validate와 run의 차이점은?**

| 명령어 | 동작 | 파일 수정 |
|--------|------|---------|
| `validate` | 권장사항 제안 | 없음 |
| `run` | 자동 최적화 | 있음 |

**Q2. 어떤 스킬부터 최적화해야 하나요?**

**권장 순서**:
1. 핵심 개발 스킬 (oocheck, oodev, ootest)
2. 자주 사용하는 스킬 (oostart, oostop)
3. 나머지 스킬

**Q3. 수정 결과가 마음에 안 들어요.**

**복구**:
```bash
# Git으로 복구
git checkout .claude/skills/oo[스킬명]/SKILL.md

# 또는 백업에서 복구
cp backup/oo[스킬명]/SKILL.md .claude/skills/
```

**Q4. 특정 스킬만 제외하고 싶어요.**

현재 버전은 전체 실행만 지원. 특정 스킬 제외 불가.
**대안**: 개별 실행 (`ooskill run [스킬명]`)

---

## 13. 관련 워크플로우

### 13.1 스킬 최적화 워크플로우

```
ooskill validate (권장사항 확인)
    ↓
ooskill run (자동 최적화)
    ↓
검토 (Git diff)
    ↓
oocommit (커밋)
```

### 13.2 새 스킬 추가 후 워크플로우

```
.claude/skills/oo[스킬명]/SKILL.md 작성
    ↓
ooskill validate (최적화 확인)
    ↓
ooskill run [스킬명] (개선)
    ↓
ooskill validate
    ↓
oocommit (커밋)
```

---

**버전**: v01 (2026-02-05)
**스킬 파일**: `.claude/skills/ooskill/SKILL.md`
**참조**: `agents.md`, `.claude/commands/sc/*.md`
