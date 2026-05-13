# oo[스킬명] - [한 줄 설명]

## 문서 이력 관리
- v01 YYYY-MM-DD — 최초 생성

---

> 공통 가이드: `.claude/guides/common_guide.md` | 컨텍스트: `.claude/skills/oocontext/SKILL.md`

## 1. 개요

[스킬의 목적과 주요 기능 설명]

**옵션**: `--sp N` (서브프로젝트)

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oo[스킬명] status` | 서브명령어 리스트, 현재 상태 |
| `oo[스킬명] version` | 스킬 버전 정보 (v01) |
| `oo[스킬명] run` | [주요 기능 설명] |

실행: `uv run python .claude/skills/oo[스킬명]/scripts/oo[스킬명]_run.py [subcommand] [args]`

## 3. 워크플로우

```
단계 1: [설명]
    ↓
단계 2: [설명]
    ↓
단계 3: [설명]
```

## 4. 서브에이전트

| 단계 | 에이전트 | 역할 | 병렬 |
|------|----------|------|:----:|
| 분석 | Explore | 코드베이스 탐색 | O |
| 실행 | task-executor | 기능 구현 | - |
| 검증 | task-checker | 결과 검증 | - |

## 5. 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--sp N` | 서브프로젝트 지정 | 00 |
| `--dry-run` | 실제 실행 없이 미리보기 | false |

## 6. 사용 예시

### 예시 1: 기본 실행

```bash
oo[스킬명] run
```

### 예시 2: 서브프로젝트 지정

```bash
oo[스킬명] run --sp 02
```

## 7. 관련 문서

| 문서 | 용도 |
|------|------|
| `.claude/skills/oo[스킬명]/references/guide.md` | 상세 가이드 |
| `.claude/skills/oo*/SKILL.md` | 관련 스킬 |
| `00_doc/d{SP}XXXX.md` | 연동 문서 |

## 8. 관련 명령어

| 명령어 | 용도 |
|--------|------|
| `.claude/commands/sc/*.md` | 범용 명령어 |

## 9. 관련 경로

- 스크립트: `.claude/skills/oo[스킬명]/scripts/oo[스킬명]_run.py`
- 템플릿: `.claude/skills/oo[스킬명]/templates/oo[스킬명]_*.md`
- 가이드: `.claude/skills/oo[스킬명]/references/guide.md`
