---
name: ooword
description: "Word 문서 생성 및 변환 스킬 'ooword', 'Word 변환', 'docx 생성', '견적서 생성' 등을 요청할 때 트리거된다"
metadata:
  version: "v02"
  category: "content"
---

> 공통: `.claude/guides/common_guide.md` | 가이드: `.claude/skills/ooword/references/guide.md`

Markdown을 Word(.docx) 문서로 변환하는 전문 스킬.

**2가지 처리 방식 지원:**
- **기본**: python-docx, pandoc, Node.js docx 라이브러리 직접 사용 (빠름, 간단)
- 플러그인 (`--plugin`): document-skills:docx 플러그인 (변경추적, 주석, Redlining 지원)

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | Markdown을 Word(.docx) 문서로 변환 |
| **하는 것** | MD→docx 변환, 스타일 적용, 견적서 생성 |
| **하지 않는 것** | PPT 생성(→ooppt), PDF 변환(→oopdf), HWP 생성(→oohwp) |
| **참조 범위** | 현재 프로젝트 내부 파일만 / 외부 문서 서비스 자동 연동 안 함 |
| **수정 대상** | 출력 `*.docx` 파일 |
| **실행 레벨** | [자동] — 변환 자동 실행 |
| **에이전트 호환** | Claude Code 권장 — python-docx/pandoc `uv run` 자동 실행 / 다른 에이전트: `pandoc input.md -o output.docx` 수동 실행 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ooword help` | 서브명령어 목록 표시 |
| `ooword version` | 스킬 버전 정보 (v02) |
| `ooword status` | 서브명령어 리스트, 현재 상태 |
| `ooword check` | references/checklist.md 기반 체크 및 리포팅 | 터미널 |
| `ooword run` | Word 문서 생성 실행 |
| `ooword update` | 현행화 — 소스 변경분 감지 → Word 문서 재생성 | .docx |
| `ooword update --dry-run` | 변경 예정 내용 미리 출력 (실제 수정 안 함) | 터미널 |
| `ooword show checklist` | 역할 수행 체크리스트 표시 | 터미널 |
| `ooword add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |
| `convert` | Markdown -> Word 기본 변환 (python-docx) |
| **`convert this`** | **직전 MD 파일 Word 변환** (→ common_guide.md §9) |
| `convert --pandoc` | Markdown -> Word (LaTeX 수식 + mermaid 지원) |
| `convert --plugin` | Markdown -> Word (플러그인, 고급 기능 지원) |
| `quotation` | 견적서 마크다운 -> 워드 (표/스타일 자동 서식) |
| `quotation --plugin` | 견적서 변환 (플러그인, 변경추적 지원) |
| `edit` | 기존 DOCX 편집 (플러그인 전용) |
| `template` | 커스텀 템플릿 기반 Word 생성 |

### --plugin 모드 추가 옵션

| 옵션 | 설명 |
|------|------|
| `--track-changes` | 변경 추적 활성화 (Tracked Changes) |
| `--comment "텍스트"` | 주석 추가 |
| `--redline` | Redlining 워크플로우 (문서 검토용) |
| `--author "이름"` | 작성자 이름 지정 (기본: Claude) |

## convert 서브명령어

> 코드 예시: references/guide.md 참조

### convert 지원 요소

| 마크다운 요소 | 변환 결과 |
|--------------|----------|
| `# H1` ~ `##### H5` | Word 제목 스타일 (Heading 0~4) |
| `- 목록` | 글머리 기호 목록 |
| `1. 번호` | 번호 매기기 목록 |
| `> 인용` | 들여쓰기 단락 |
| `**굵게**` | Bold |
| `*기울임*` | Italic |
| `` `코드` `` | Consolas 글꼴 (10pt) |
| `|표|` | Word 테이블 (테두리 자동) |

## quotation 서브명령어 (견적서)

> 코드 예시: references/guide.md 참조

### quotation 자동 서식

| 기능 | 설명 |
|------|------|
| 표 헤더 | 배경색 자동 적용, 중앙 정렬, 굵게 |
| 금액 셀 | 우측 정렬 |
| 소계 행 | 회색 배경, 굵게 |
| 합계 행 | 노란색 배경, 굵게 |
| 서명란 | 문서 하단 자동 추가 (작성/검토/승인) |

## edit 서브명령어 (플러그인 전용)

> 코드 예시: references/guide.md 참조

## 워크플로우

> 코드 예시: references/guide.md 참조

## 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | Explore | haiku | 입력 파일 구조 분석 | - |
| 변환 | task-executor | sonnet | MD -> DOCX 변환 실행 | - |
| 검증 | task-checker | sonnet | 출력 파일 검증 | - |

## 의존성

### 기본 모드
| 패키지 | 용도 | 필수 |
|--------|------|:----:|
| python-docx | 기본 MD->DOCX 변환 | O |
| pandoc | LaTeX 수식/mermaid 지원 | - |
| mermaid-cli | mermaid -> PNG | - |
| docx (npm) | quotation용 워드 생성 | - |

### 스킬 의존성
| 스킬 | 용도 | 필수 |
|------|------|:----:|
| ooreport | MD->DOCX 변환 스크립트 (`ooreport_md2docx.py`) 제공 | O |

## 관련 파일

| 구분 | 경로 |
|------|------|
| 스킬 정의 | `.claude/skills/ooword/SKILL.md` |
| 변환 스크립트 | `.claude/skills/ooreport/scripts/ooreport_md2docx.py` |
| 견적서 변환기 | `.claude/skills/ooword/templates/quotation_docx.js` |
| 견적서 스타일 | `.claude/skills/ooword/templates/quotation_docx.json` |
| 가이드 | `.claude/skills/ooword/references/guide.md` |

## 출력 경로 규칙

> **핵심 원칙**: 출력 파일은 입력 파일과 동일한 폴더에, 동일한 파일명으로, 확장자만 `.docx`로 변경

| 입력 | 출력 |
|------|------|
| `00_doc/sp00/d0102_문서.md` | `00_doc/sp00/d0102_문서.docx` |
| `tmp/draft.md` | `tmp/draft.docx` |

## 사용 예시

> 코드 예시: references/guide.md 참조

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

