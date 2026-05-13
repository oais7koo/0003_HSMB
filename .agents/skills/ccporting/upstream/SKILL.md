---
name: ccporting
description: Claude oo* 스킬을 Codex cc* 스킬로 분리 관리하기 위한 포팅 파이프라인. manifest 기반으로 sync/apply/status를 수행하고, 필요 시 CLAUDE.md -> AGENTS.md 정책 동기화를 함께 실행한다.
---

# ccporting

## 1. 분리 관리 원칙

- Codex 스킬 문서/운영 규칙은 `.agents/skills/cc*/`에서 독립 관리
- Claude 원본은 `upstream/`으로만 동기화(직접 덮어쓰기 지양)
- 동기화는 `sync`와 `apply` 두 단계로 분리
- 포팅/업데이트 작업 경로는 항상 `.claude/skills_to_codex/` 사용
- 포팅 대상에서 ooenv는 제외한다.
- 포팅 실행 후 결과물은 .agents/skills/로 이동한다.
- 파일 존재 확인, diff 검토, 동작 검증의 기준 경로는 항상 .agents/skills/를 사용한다.

## 2. 명령

```powershell
python .agents/skills/ccporting/scripts/init_cc_skill.py sync --port oostart_to_ccstart
python .agents/skills/ccporting/scripts/init_cc_skill.py apply --port oostart_to_ccstart
python .agents/skills/ccporting/scripts/init_cc_skill.py status
```

## 3. 옵션

- `--manifest <path>`: 외부 JSON manifest 사용
- `--state-dir <path>`: 상태/플랜 저장 위치 (기본 `.claude/skills_to_codex/.ccporting_state`)
- `--sync-agents`: CLAUDE.md -> AGENTS.md 동기화 동시 실행
- `--target-root <path>`: 포팅 출력 루트 (기본 `.claude/skills_to_codex`)

## 4. 기본 포트

- `oostart_to_ccstart`
- `ooskill_to_ccskill`

## 5. 정리

- 기본 정책상 `.claude/skills_to_codex`는 유지한다(삭제하지 않음).

