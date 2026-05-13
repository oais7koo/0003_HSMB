---
name: ccporting
description: "Claude oo* 스킬을 Codex cc* 스킬로 포팅하거나 개선 산출물을 생성할 때 사용한다. 모든 산출물은 먼저 .agents/skills에 완전한 스킬 형태로 생성한다."
---

# ccporting

## 1. 분리 관리 원칙

- Codex 스킬 문서/운영 규칙은 `.agents/skills/cc*/`에서 독립 관리한다.
- Claude 원본은 `upstream/`으로만 동기화하고 직접 덮어쓰지 않는다.
- 동기화는 `sync`와 `apply` 두 단계로 분리한다.
- `run`은 `sync` 후 `apply`까지 한 번에 수행하는 업데이트 명령이다.
- 포팅/업데이트/개선 산출물의 기본 생성 경로는 항상 `.agents/skills/<skill>/`이다.
- 스킬을 개선할 때도 활성 경로인 `.agents/skills/<skill>/`을 직접 수정하지 말고, 먼저 `.agents/skills/<skill>/`에 완전한 스킬 형태로 생성한다.
- 생성된 스킬은 루트 `SKILL.md`, 실행 보조 파일(`scripts/` 등), 원본 보관용 `upstream/`을 포함해야 한다.
- 검토가 끝난 결과물만 별도 반영 절차로 `.agents/skills/`에 이동한다.
- 파일 존재 확인, diff 검토, 동작 검증의 기준 경로는 기본적으로 `.agents/skills/`를 사용하고, 반영 후 검증은 `.agents/skills/`를 사용한다.
- 포팅 대상에서 `ooenv`는 제외한다.
- manifest를 생략하면 `.agents/skills/ccporting_manifest_all.json`을 우선 사용하고, 없을 때만 내장 기본 포트를 사용한다.
- 루트 `SKILL.md`는 Claude 원본 `SKILL.md` 본문을 기반으로 생성하되 Codex용 YAML frontmatter를 반드시 포함한다.
- `upstream/SKILL.md`도 Codex 스킬 로더의 스캔 대상이 될 수 있으므로, 복사 후 반드시 YAML frontmatter(`---`)를 포함해야 한다.

## 2. 명령

```powershell
python .agents/skills/ccporting/scripts/init_cc_skill.py status
python .agents/skills/ccporting/scripts/init_cc_skill.py sync --port oostart_to_ccstart
python .agents/skills/ccporting/scripts/init_cc_skill.py apply --port oostart_to_ccstart
python .agents/skills/ccporting/scripts/init_cc_skill.py run
python .agents/skills/ccporting/scripts/init_cc_skill.py run --port oocapture_to_cccapture
python .agents/skills/ccporting/scripts/init_cc_skill.py autofix
python .agents/skills/ccporting/scripts/init_cc_skill.py audit
```

## 3. 옵션

- `--manifest <path>`: 외부 JSON manifest 사용
- `--state-dir <path>`: 상태/플랜 저장 위치, 기본 `.agents/skills/.ccporting_state`
- `--sync-agents`: `CLAUDE.md` -> `AGENTS.md` 동기화 동시 실행
- `--target-root <path>`: 포팅 출력 루트, 기본 `.agents/skills`
- `run` 실행 시 포팅 완료 후 `autofix`(기본 치환)와 `audit`(의심 패턴 점검)을 자동 수행한다.

## 3.1 스킬 실행 원칙

- `cc*`는 실행파일(.cmd/.bat) 생성을 전제로 하지 않고, Codex 스킬(`SKILL.md` + `scripts/`)로 동작하는 것을 원칙으로 한다.
- `ccporting`은 포팅 산출물(문서/스크립트/upstream) 정합성에만 집중하며, OS 명령 등록(PATH/래퍼 생성)은 기본 범위에서 제외한다.

## 4. 산출물 구조

```text
.agents/skills/<target>/
  SKILL.md
  scripts/
  upstream/
    SKILL.md
    scripts/
```

## 5. 기본 포트

- 기본 manifest가 있으면 `.agents/skills/ccporting_manifest_all.json` 전체 포트를 사용한다.
- 기본 manifest가 없으면 내장 기본 포트만 사용한다.

## 6. 반영 원칙

- `.agents/skills/<target>/`에서 diff와 동작을 검토한다.
- 검토가 끝난 뒤에만 `.agents/skills/<target>/`로 이동하거나 복사한다.
- `.agents/skills` 직접 수정은 긴급 복구 외에는 피한다.

## 7. 포팅 검증 체크리스트

- `cc*` 스킬 포팅 시 루트 `SKILL.md`의 `name`/`description`/예시 명령은 `cc*` 기준으로 일치해야 한다.
- 포팅본 `scripts/`의 CLI 서브명령어가 문서와 동일하게 동작해야 한다. 문서에 `search`가 있으면 스크립트에도 실제 분기가 있어야 한다.
- 실행 출력 문구, 도움말(`help`), 오류 메시지에 원본 `oo*` 이름이 남아 있지 않아야 한다. 별칭 호환을 제외하고 기본 노출명은 `cc*`를 사용한다.
- `SKILL.md`와 `upstream/SKILL.md`의 차이는 포팅 정책상 필요한 항목(frontmatter, 포팅 주석, Codex 지시)으로 제한한다.
- 반영 전 아래 점검을 수행한다.
  - `rg -n "oowiki|oo[A-Za-z0-9_]+" .agents/skills/<target>`
  - `python .agents/skills/<target>/scripts/<entry>.py help`
  - 핵심 서브명령 1회 실행 (`status`, `search` 등)

## 7. 포팅 후 명령어 정규화 규칙 (필수)

- 전체 포팅(`run`) 완료 후 각 대상 스킬(`.agents/skills/<target>`)에 대해 아래를 반드시 수행한다.
- `SKILL.md`의 사용자 노출 명령어는 `oo*`가 아니라 `cc*` 기준으로 표기한다.
- `scripts/` 내 help/로그/오류 메시지의 기본 노출명은 `oo*`가 아니라 `cc*`로 정규화한다.
- 단, `upstream/` 경로의 원본 보관 파일은 수정하지 않는다.
- 별칭 호환 목적의 문구는 허용하되, 기본 사용 예시는 `cc*`를 우선한다.
- 정규화 후 검증을 수행한다.
  - `rg -n "\boo[a-z0-9_]+\b" .agents/skills/<target>/SKILL.md .agents/skills/<target>/scripts`
  - 핵심 서브명령 실행 (`help`, `status`, `search` 등)

## 8. 전체 재포팅 실행 규칙

- 전체 포팅은 `--manifest .agents/skills/ccporting_manifest_all.json` 기준으로 수행한다.
- 전체 포팅 직후 7번 정규화 규칙을 전체 대상에 일괄 적용한다.
- 정규화 결과는 누락 없이 검증 로그로 남긴다.
- `audit` 결과 리포트는 `.agents/skills/.ccporting_audit_report.json`에 저장한다.

