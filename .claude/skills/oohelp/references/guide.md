# oohelp_guide - 명령어/스킬 도움말 가이드

## 문서 이력 관리
- v02 2026-04-07 — 마스터 문서 d0007 → .claude/CLAUDE.md 전환
- v01 2026-02-05 — 초기 생성

---

> 스킬: `.claude/skills/oohelp/SKILL.md` | 공통: `.claude/guides/common_guide.md`

## 1. 개요

### 1.1 목적

프로젝트의 모든 스킬, 에이전트, 명령어 정보를 통합 조회할 수 있는 도움말 시스템입니다.

### 1.2 주요 기능

- **스킬 카탈로그**: `.claude/CLAUDE.md` "OAIS 스킬 및 에이전트 카탈로그" 섹션 표시
- **카테고리 필터링**: 특정 카테고리만 조회 (oo, agent, command)
- **개별 스킬 상세**: 특정 스킬의 `.claude/skills/oo*/SKILL.md` 내용 표시

### 1.3 핵심 원칙

- **단일 정보원**: `.claude/CLAUDE.md`가 스킬 카탈로그 SSOT (세션 자동 로드)
- **읽기 전용**: 문서를 수정하지 않고 표시만
- **빠른 참조**: 자주 사용하는 스킬 빠른 조회

---

## 2. 워크플로우

### 2.1 전체 흐름도

```
oohelp [명령어]
    ↓
명령어 파싱
    ├─ 인자 없음 → CLAUDE.md 스킬 카탈로그 전체 표시
    ├─ 카테고리명 → 해당 카테고리 스킬만 표시
    └─ 스킬명 → .claude/skills/oo*/SKILL.md 표시
    ↓
완료
```

### 2.2 CLAUDE.md 카탈로그 구조

`.claude/CLAUDE.md`의 "OAIS 스킬 및 에이전트 카탈로그" 섹션:

| 섹션 | 내용 |
|------|------|
| 핵심 개발 스킬 | ooprd, ooplan, oofeature, oodev, ootest, oocheck, oofix, oocommit |
| 모듈/DB 스킬 | oolib, oodb, oodeep, ooopti |
| 문서/환경 스킬 | oodoc, ooenv, oohistory, oonote, ootodo, oouser, oodesign, ootutorial |
| 실행/유틸 스킬 | oorun, oouv, oocontext, oonext, oonow, ooprevious, ootoken, oowork, oocapture |
| 콘텐츠 생성 스킬 | ooppt, ooword, oobook, oopaper, ooreport, oopdf, ooresearch, oosota, oosurvey, ooscrap, oohwp, oosidi |
| 메타 스킬 | oostart, oostop, oohelp, ooskill, oosync |
| 범용 명령어 | sc/ (analyze, build, implement 등) |
| 에이전트 | .claude/agents/ 전문 서브에이전트 |

---

## 3. 상세 사용법

### 3.1 전체 도움말 표시

```bash
oohelp
# → .claude/CLAUDE.md 스킬 카탈로그 전체 출력
```

### 3.2 카테고리별 조회

```bash
oohelp oo       # OAIS 스킬 전체 목록
oohelp agent    # 에이전트 목록
oohelp command  # 범용 명령어(sc/) 목록
```

### 3.3 개별 스킬 상세 조회

```bash
oohelp oodev    # .claude/skills/oodev/SKILL.md 표시
oohelp ootest   # .claude/skills/ootest/SKILL.md 표시
```

---

## 4. 스킬 카탈로그 갱신

스킬 추가/변경 시 `.claude/CLAUDE.md`의 카탈로그 섹션을 직접 수정합니다.  
d0007_command.md는 더 이상 관리하지 않습니다.

| 상황 | 작업 |
|------|------|
| 새 스킬 추가 | CLAUDE.md 카탈로그 섹션에 행 추가 |
| 스킬 삭제 | CLAUDE.md 카탈로그 섹션에서 행 제거 |
| 스킬 상세 변경 | 해당 .claude/skills/oo*/SKILL.md 수정 |

---

## 5. 관련 문서

| 문서 | 역할 |
|------|------|
| `.claude/CLAUDE.md` | OAIS 스킬 및 에이전트 카탈로그 (SSOT) |
| `.claude/skills/oo*/SKILL.md` | 개별 스킬 상세 정의 |
| `.claude/guides/common_guide.md` | 공통 가이드라인 |

---

**버전**: v02 (2026-04-07)
