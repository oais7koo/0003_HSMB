# oocontext Tutorial

> 서브프로젝트(SP) 번호 설정으로 세션 컨텍스트 관리 | 버전: v09 | 카테고리: meta-util

## §1 이유 (Reason)

대규모 프로젝트에서 여러 서브프로젝트를 다룰 때 현재 작업 대상을 명확히 설정하고, 문서번호(d{SP}NNNN) 자동 감지 및 경로 설정을 합니다.

## §2 빠른 시작 (Quick Start)

```bash
oocontext set 02
# 또는 현재 디렉토리에서 자동 감지
oocontext auto
```

SP02 (Streamlit) 컨텍스트로 세션 설정 완료

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oocontext set {SP}` | SP 번호 직접 설정 |
| `oocontext auto` | CWD 패턴에서 자동 감지 |
| `oocontext show` | 현재 컨텍스트 표시 |
| `oocontext list` | 모든 SP 정보 표시 |

## §4 권장 흐름 (Recommended Flow)

1. 세션 시작: `oostart run`
2. 작업 대상 SP 결정
3. `oocontext set {SP}` 또는 `oocontext auto` 실행
4. 이후 모든 명령에서 SP 번호 자동 적용

## §5 전체 명령어 (All Commands)

```
oocontext help
oocontext version
oocontext set {SP}
oocontext auto
oocontext show
oocontext list
oocontext reset
```

## §6 상세 사용법 (Detailed Usage)

**SP 번호 체계:**
- `00` — 공통 (base_config.py, oais/)
- `01` — 알고리즘 (01_algorithm/)
- `02` — Streamlit ({project}/)
- `03` — Django (`03_*/` 패턴 폴더)
- `04` — FastAPI (`04_*/` 패턴 폴더)

**자동 감지 패턴:**
- `{project}/pages/` → SP02
- `01_algorithm/` → SP01
- `03_*/` → SP03
- `04_*/` → SP04

## §7 실전 예시 (Real Examples)

```bash
cd {project}/pages
oocontext auto      # SP02 자동 감지
oodev               # 개발

cd 04_api_server
oocontext set 04
oocheck run
```

## §8 입출력 (Input/Output)

**입력:** SP 번호 또는 CWD 경로
**출력:** `~/.claude/.omc/sp-context.json` 설정

## §9 FAQ

**Q: 여러 SP를 동시에 작업할 수 있나?**
A: 불가. 한 세션에 한 SP만 활성.

**Q: SP 번호를 모르면?**
A: `oocontext list` 로 전체 확인.

## §10 서브에이전트 (Sub-agents)

- path-detector, context-manager

## §11 관련 스킬 (Related Skills)

- `oostart`, `ooplan`, `ooenv`, `oohistory`

---

**버전**: v09 | **카테고리**: meta-util | **업데이트**: 2026-04-14
