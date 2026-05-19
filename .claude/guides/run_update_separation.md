# run과 update 역할 분리 원칙 (모든 oo* 스킬)

> 모든 `oo*` 스킬은 `run`과 `update` 서브커맨드를 명확히 분리해야 한다.

## 1. 역할 정의

| 서브커맨드 | 역할 | 성격 | 호출 시점 |
|-----------|------|------|----------|
| **`run`** | 해당 스킬의 **배치 실행** 또는 그 뒤에 오는 구체적인 명령 실행 | 일회성·실행 중심 | 사용자가 작업을 수행할 때 |
| **`update`** | 최상의 상태로 유지되어야 하는 **모든 상태·설정의 현행화** | 멱등·유지보수 중심 | 정기적 점검, 스킬 추가/변경 후 |

## 2. 분리 기준

### `run`에 포함되는 것
- 스킬의 핵심 기능 실행 (예: `oocheck run` = 코드 체크 실행)
- 사용자 입력을 받아 처리하는 동작
- 구체적 서브커맨드 실행 (예: `oopaper run --lang en`)
- 일회성 배치 작업

### `update`에 포함되는 것
- 카탈로그·인덱스 현행화 (예: CLAUDE.md 스킬 카탈로그)
- 표준 포맷·버전 정보 일괄 통일
- 참조 블록 삽입/갱신 (예: Gemma 위임 블록)
- 체크리스트 표준 자동 수정
- 다른 스킬/프로젝트와의 정합성 갱신

### `run`에서 `update`로 이동해야 하는 패턴 (안티패턴)
- `run` 끝에서 "CLAUDE.md 자동 갱신" 하는 로직
- `run` 시 "부수 효과로 인덱스 갱신"
- `run`과 `update` 기능이 섞여 있어 사용자가 의도치 않게 양쪽을 실행하는 구조

## 3. 표준 명령어 구조

```
oo{skill} help             # 서브명령어 목록
oo{skill} version          # 버전 정보
oo{skill} status           # 현재 상태 요약
oo{skill} check            # 체크리스트 검증
oo{skill} run              # 배치 실행 (핵심 동작)
oo{skill} run [대상]       # 특정 대상만 실행
oo{skill} update           # 모든 현행화 타겟 일괄 실행
oo{skill} update [타겟]    # 특정 타겟만 현행화
oo{skill} update --dry-run # 현행화 미리보기
```

## 4. 구현 가이드 (Python 스크립트)

### UPDATE_TARGETS 레지스트리 패턴 (권장)

```python
UPDATE_TARGETS = {
    "catalog": {
        "kind": "func",
        "call": lambda: cmd_update_catalog(dry_run=dry_run),
        "desc": "카탈로그 현행화",
    },
    "version": {
        "kind": "func",
        "call": lambda: cmd_update_version(dry_run=dry_run),
        "desc": "버전 정보 일괄 갱신",
    },
    # 외부 스크립트로 위임하는 경우:
    "foo": {
        "kind": "script",
        "script": "oo{skill}_foo.py",
        "desc": "foo 현행화",
    },
}
```

### run 내부에서 update 자동 호출 금지

```python
# ❌ BAD: run이 update를 호출
def cmd_run():
    # ... 배치 실행 ...
    cmd_update()  # 자동 호출 금지

# ✅ GOOD: run 완료 후 안내만 제공
def cmd_run():
    # ... 배치 실행 ...
    if modified > 0:
        print("[TIP] 현행화는 `oo{skill} update` 실행")
```

## 5. 적용 대상 스킬 (우선순위)

### 높음 (내부에 cmd_update 함수 존재)
- `ooskill` — 완료 (catalog, gemma 타겟으로 분리)
- `oocheck`, `oocontext`, `oofeature`, `ooprd`, `ooreport` — 분리 필요

### 중간 (SKILL.md에 update 언급, 구현 위치 불명확)
- `oodoc`, `ooenv`, `oopaper`, `ooppt`, `oorun`, `ootodo`, `ootutorial`, `oouv`, `ooword`

### 신규 스킬 생성 시
- 이 원칙을 처음부터 적용
- `run`과 `update`를 반드시 분리된 서브커맨드로 설계

## 6. 마이그레이션 체크리스트

각 스킬을 분리할 때:

- [ ] 현재 `run`의 코드를 분석하여 "실행" 부분과 "현행화" 부분 식별
- [ ] "현행화" 부분을 별도 함수로 추출
- [ ] `UPDATE_TARGETS` 레지스트리에 등록
- [ ] `run`에서 `update` 자동 호출 제거
- [ ] `run` 완료 시 `update` 실행 안내 메시지 추가
- [ ] SKILL.md 서브명령어 표에 `update`, `update <타겟>`, `update --dry-run` 추가
- [ ] `run` 동작이 축소된 점을 SKILL.md에 명시

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/ooskill/SKILL.md` | 분리 적용된 레퍼런스 구현 |
| `.claude/skills/ooskill/scripts/ooskill_run.py` | UPDATE_TARGETS 구현 예시 |
| `.claude/guides/gemma_delegation.md` | Gemma 위임 가이드 (관련 원칙) |
