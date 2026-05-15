# OAIS 사용 튜토리얼

> 생성: `ooenv tutorial` | 현행화: `ooenv tutorial --update` | 날짜: 2026-04-29

## 빠른 시작 (Quick Start)

```
1. 세션 시작   → oostart run
2. 컨텍스트    → oocontext [N]        (서브프로젝트 번호, 미입력 시 SP00)
3. 개발 사이클 → ooprd → ooplan → oodev → oocheck → oofix → oocommit
4. 세션 종료   → oostop run
```

## 목차

| 문서 | 내용 |
|------|------|
| [31_모델설정.md](31_모델설정.md) | Claude 모델 선택 전략 (Sonnet/Opus/Haiku 라우팅) |
| [01_quickstart.md](.claude/tutorial/01_quickstart.md) | 기본 워크플로우 시나리오 (처음 시작하는 분) |
| [02_skills.md](.claude/tutorial/02_skills.md) | oo 스킬 전체 레퍼런스 (카테고리별 상세) |
| [03_commands.md](.claude/tutorial/03_commands.md) | sc/ 범용 명령어 사용법 |
| [04_plugins.md](.claude/tutorial/04_plugins.md) | 플러그인 · MCP 서버 사용법 |
| [10_prd와plan을이용한프로젝트아키텍처관리.md](10_prd와plan을이용한프로젝트아키텍처관리.md) | ooprd+ooplan 통합 워크플로우 (목표설정·플래닝·방향변경) |

## 스킬 튜토리얼 (skills/)

| 스킬 | 파일 | 카테고리 | 최종 업데이트 |
|------|------|----------|-------------|
| oowiki | [skills/oowiki.md](skills/oowiki.md) | content | 2026-04-29 |
| oodoc | [skills/oodoc.md](.claude/tutorial/skills/oodoc.md) | doc-env | 2026-04-29 |
| oofeature | [skills/oofeature.md](.claude/tutorial/skills/oofeature.md) | core-dev | 2026-04-29 |
| ooplan | [skills/ooplan.md](.claude/tutorial/skills/ooplan.md) | core-dev | 2026-04-29 |
| ooprd | [skills/ooprd.md](.claude/tutorial/skills/ooprd.md) | core-dev | 2026-04-29 |
| ootest | [skills/ootest.md](.claude/tutorial/skills/ootest.md) | core-dev | 2026-04-29 |
| ooscrap | [skills/ooscrap.md](.claude/tutorial/skills/ooscrap.md) | content | 2026-04-29 |
| oofix | [skills/oofix.md](.claude/tutorial/skills/oofix.md) | core-dev | 2026-04-29 |
| oocheck | [skills/oocheck.md](.claude/tutorial/skills/oocheck.md) | core-dev | 2026-04-29 |

## 스킬 카테고리 요약

| 카테고리 | 스킬 | 대표 명령 |
|----------|------|----------|
| **세션/메타** | oostart, oostop, oohelp, oocontext | `oostart run` |
| **핵심 개발** | ooprd, ooplan, oodev, ootest, oocheck, oofix, oocommit | `oodev run` |
| **모듈/DB** | oolib, oodb, oodeep | `oodb run` |
| **문서/환경** | oodoc, ooenv, oohistory, oonote, ootodo, oouser | `oodoc run` |
| **실행/유틸** | oorun, oouv, oosync | `oorun run` |
| **콘텐츠** | ooppt, ooword, oohwp, oobook, oopaper, ooreport, ooresearch, oosota, oosurvey, ooscrap | `oopaper run` |
| **스킬 관리** | ooskill, oocommand, oopdf | `ooskill validate` |

## 서브프로젝트 (SP) 체계

| SP | 폴더 | 문서 prefix |
|----|------|-------------|
| SP00 | (공통) | d0001~d9999 |
| SP01 | 01_obsidian/ | d10001~ |
| SP02 | 02_pycode/ | d20001~ |
| SP03 | D:/resilio/1_oais/03_paper/ | d30001~ |
| SP04 | 04_scraping/ | d40001~ |
| SP05 | 05_youtube_graphRAG/ | d50001~ |

> **컨텍스트 전환**: `oocontext 3` → SP03 활성화, 이후 모든 oo 스킬이 d30001~ 문서 사용
