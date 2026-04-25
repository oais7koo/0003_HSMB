# OAIS 프로젝트 튜토리얼

> OAIS (One AI System) 프로젝트의 Claude Code 환경 사용 가이드

## 프로젝트 구조

| 폴더 | 설명 |
|------|------|
| `00_doc/` | 프로젝트 문서 (PRD, TODO, 이력 등) |
| `01_obsidian/` | 옵시디언 노트 (SP01) |
| `02_pycode/` | Python/알고리즘 코드 (SP02) |
| `D:/resilio/1_oais/03_paper/` | 논문 관리 (SP03) |
| `04_scraping/` | 스크래핑/유튜브 (SP04) |
| `.claude/` | Claude Code 설정, 스킬, 에이전트 |

## 시작하기

1. **세션 시작**: `oostart run` (매 세션 첫 실행)
2. **도움말**: `oohelp` (전체 스킬 목록)
3. **환경 점검**: `ooenv run` (환경 검증)

## oo 스킬 (54개)

| 스킬 | 설명 |
|------|------|
| `oobook` | 도서 서머리 생성 스킬 |
| `ooc` | oocontext 스킬의 약어 alias. |
| `oocapture` |  |
| `oocheck` | 코드 품질 체크 스킬 |
| `oocommit` | Git 커밋 및 이력 정리 스킬 |
| `oocontext` | 서브프로젝트 컨텍스트 관리 스킬 |
| `ood` | oodev 스킬의 약어 alias. |
| `oodb` | DB 수정 및 최적화 스킬 |
| `oodeep` | 딥러닝 GPU 효율성 최적화 스킬 |
| `oodesign` | 디자인 통합 스킬 |
| `oodev` | TDD 기반 개발 스킬 |
| `oodoc` | 문서 생성 통합 스킬 |
| `ooenv` | 개발 환경 및 스킬 정합성 검증 스킬 |
| `oof` | oofeature 스킬의 약어 alias. |
| `oofeature` | 기능별 상세 문서(상세기획/설계/개발/검증) 생성·단계 전환·현황 관리 스킬. |
| `oofix` | 코드 오류 자동 개선 스킬 |
| `ooflow` | 전체 SW 개발 워크플로우(기획→설계→개발→검증) 자동 실행 오케스트레이터. |
| `oohelp` | 명령어/스킬 도움말 스킬 |
| `oohistory` | 완료 항목 이력 이동 스킬 |
| `oohwp` | 한글(HWPX) 문서 생성/읽기/편집 스킬 |
| `ook` | oocheck 스킬의 약어 alias. |
| `oolib` | oo 모듈 수정/최적화 스킬 |
| `oonext` | 다음 작업 추천 스킬 |
| `oonote` | 연구노트 작성 스킬 |
| `oonow` | 현재 작업 상황 표시 스킬. 직전 사용자 입력 내용과 현재 컨텍스트를 요약 표시한다. |
| `ooopti` | 알고리즘 및 코드 최적화 스킬. |
| `oopaper` | 통합 문헌 관리 스킬 |
| `oopdf` | PDF 변환/처리 스킬 |
| `ooplan` | 구현 계획 및 상세 설계 스킬 |
| `ooppt` | PPT 노트 생성 스킬. 대상 MD 문서를 PPT 발표용 슬라이드 노트 형식의 MD 문서로 변환한다. |
| `ooprd` | PRD 생성 및 정합성 검증 스킬 |
| `ooprevious` |  |
| `ooref` | 프레임워크 레퍼런스 관리 및 적용 체크 스킬. |
| `ooreport` | 리포트 자동 생성 스킬 |
| `ooresearch` | SOTA 기반 연구 수행 스킬 |
| `ooreview` | 코드 리뷰 스킬. |
| `oorun` | TDD 기반 자율 실행 스킬 (Builder) |
| `oos` | oostart 스킬의 약어 alias. |
| `ooscrap` | 콘텐츠 스크래핑 통합 스킬. 유튜브 STT/다운로드 + 웹 기사 전문 스크래핑. URL 자동 감지(유튜브/채널/일반). |
| `oosidi` | 옵시디언 볼트 문서 작성/관리 스킬 |
| `ooskill` | 스킬 최적화 검증 스킬 |
| `oosota` | SOTA급 학술 논문 작성 스킬. |
| `oostart` | 세션 시작 워크플로우 스킬 |
| `oostop` | 세션 종료 워크플로우 스킬 |
| `oosurvey` | 논문 서베이 및 분석 스킬 |
| `oosync` | Vibe 환경 동기화 스킬 |
| `ootest` | 통합 테스트 스킬 |
| `ootodo` | TODO 자동 처리 스킬 |
| `ootoken` | 토큰 사용량 모니터링 스킬. |
| `ootutorial` | 프로젝트 튜토리얼 생성 스킬 |
| `oouser` | 사용자 가이드 관리 스킬 |
| `oouv` | UV 기반 의존성 관리 스킬 |
| `ooword` | Word 문서 생성 및 변환 스킬 |
| `oowork` | 범용 문서 작업 워크플로우 엔진. 기술수요조사, 제안서, 보고서, 견적서 등 다단계 문서 작업 프로세스를 정의하고 순차 실행한다. |

## SC 명령어

| 명령어 | 경로 |
|--------|------|
| `estimate` | `.claude/commands/sc/estimate.md` |
| `index` | `.claude/commands/sc/index.md` |
| `spawn` | `.claude/commands/sc/spawn.md` |
| `task` | `.claude/commands/sc/task.md` |

## 공통 서브명령어

모든 oo 스킬은 다음 서브명령어를 지원합니다:

| 서브명령어 | 설명 |
|-----------|------|
| `help` | 서브명령어 목록 |
| `version` | 버전 정보 |
| `status` | 상태 확인 |
| `check` | 체크리스트 검증 |
| `show checklist` | 체크리스트 표시 |
| `add checklist "항목"` | 체크리스트 추가 |
| `run` | 기본 실행 |
| `tutorial` | 사용법 안내 |

---

> 생성일: 2026-04-14 11:32 | ootutorial v02
