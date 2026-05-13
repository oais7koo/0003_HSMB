---

name: ootutorial

description: "프로젝트 튜토리얼 생성 스킬 'ootutorial', '튜토리얼 생성', '사용법 문서화', '튜토리얼' 등을 요청할 때 트리거된다"

metadata:

  version: "v01"

  category: "doc-env"

---



# ootutorial - 프로젝트 튜토리얼 생성



> OAIS 프로젝트의 Claude 환경, oo 스킬, SC 명령어, 플러그인에 대한 튜토리얼 문서를 생성·관리한다 | 출력: `00_doc/tutorial/`



> ⚠️ **필수**: run/update 명령 시 반드시 Agent 도구로

> explore(haiku) 스킬 파일 스캔 → executor(sonnet) 튜토리얼 작성 순서로 위임할 것.

> 53개 스킬 파일 직접 스캔 금지 — 메인 컨텍스트 보호.



## 0. 스킬 요약



| 항목 | 내용 |

|------|------|

| **핵심 역할** | OAIS 환경(스킬·명령어·플러그인)에 대한 튜토리얼 문서 생성·관리 |

| **하는 것** | `00_doc/tutorial/` 튜토리얼 MD 파일 생성, 기존 튜토리얼 현행화 |

| **하지 않는 것** | 사용자 가이드(→oouser), API 문서(→oodoc), 코드 수정(→oodev) |

| **참조 범위** | 현재 프로젝트 내부 파일만 (스킬 문서, 가이드) / 외부 프로젝트 자동 포함 안 함 |

| **수정 대상** | `00_doc/tutorial/*.md` |

| **실행 레벨** | [반자동] — 튜토리얼 주제 확인 후 작성 |

| **에이전트 호환** | Claude Code 권장 — Agent 도구로 서브에이전트 위임 필수 (메인 컨텍스트 보호) |



## 문서 이력 관리

- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)



---



## 명령어



| 명령어 | 설명 |

|--------|------|

| `ootutorial help` | 서브명령어 목록 표시 |

| `ootutorial version` | 스킬 버전 정보 (v01) |

| `ootutorial status` | 서브명령어 리스트, 생성된 튜토리얼 현황 |

| `ootutorial check` | references/checklist.md 기반 체크 및 리포팅 |

| `ootutorial show checklist` | 역할 수행 체크리스트 표시 |

| `ootutorial add checklist "항목"` | 체크리스트 항목 추가 | checklist.md |

| `ootutorial run` | 전체 튜토리얼 생성 실행 |

| `ootutorial run --skill <스킬명>` | 특정 oo 스킬 튜토리얼만 생성 |

| `ootutorial run --category <카테고리>` | 특정 카테고리만 생성 (skills/commands/plugins/overview) |

| `ootutorial sync` | 양방향 동기화 — 플래그 기반 스킬↔튜토리얼 현행화 |

| `ootutorial sync --check` | 동기화 필요 항목 확인 (실제 수정 안 함) |

| `ootutorial sync --clear` | 동기화 플래그 초기화 (.omc/sync-flags/ 삭제) |



실행: `uv run python .claude/skills/ootutorial/scripts/ootutorial_run.py`



## 워크플로우



### `ootutorial run` 전체 실행



```

1. 00_doc/tutorial/ 디렉토리 확인 (없으면 생성)

2. [개요] 프로젝트 전체 튜토리얼 생성

  2-1) CLAUDE.md, .claude/CLAUDE.md 등 프로젝트 설정 분석

  2-2) 00_doc/tutorial/00_overview.md 생성 (프로젝트 구조, 시작 가이드)

3. [oo 스킬] 각 oo 스킬 튜토리얼 수집·저장

  3-1) .claude/skills/oo*/ 디렉토리 스캔

  3-2) 각 스킬의 SKILL.md 읽기 → tutorial 형식으로 변환

  3-3) 00_doc/tutorial/skills/{스킬명}.md 저장

4. [SC 명령어] SC 명령어 튜토리얼 생성

  4-1) .claude/commands/sc/*.md 스캔

  4-2) 00_doc/tutorial/commands/{명령어명}.md 저장

5. [플러그인] 플러그인/MCP 튜토리얼 생성

  5-1) MCP 서버 설정 분석 (.mcp.json)

  5-2) 00_doc/tutorial/plugins/{플러그인명}.md 저장

6. [인덱스] 00_doc/tutorial/README.md 생성 (전체 목차)

7. 결과 요약 출력 (생성/업데이트/스킵 건수)

```



### `ootutorial run --skill <스킬명>` 개별 실행



```

1. .claude/skills/{스킬명}/SKILL.md 읽기

2. tutorial 형식으로 변환

3. 00_doc/tutorial/skills/{스킬명}.md 저장

4. 00_doc/tutorial/README.md 인덱스 업데이트

```



## 출력 구조



```

00_doc/tutorial/

├── README.md                    # 전체 목차 (인덱스)

├── 00_overview.md               # 프로젝트 전체 사용법

├── skills/                      # oo 스킬 튜토리얼

│   ├── oostart.md

│   ├── ooscrap.md

│   ├── oodev.md

│   └── ...                      # 37개 oo 스킬

├── commands/                    # SC 명령어 튜토리얼

│   ├── estimate.md

│   ├── index.md

│   ├── spawn.md

│   └── task.md

└── plugins/                     # 플러그인/MCP 튜토리얼

    ├── sequential-thinking.md

    └── ...

```



## 튜토리얼 문서 형식



### oo 스킬 튜토리얼 (`skills/*.md`)



```markdown

# {스킬명} Tutorial



> {한줄 설명} | 버전: {version} | 카테고리: {category}



## 개요

{스킬 목적과 핵심 기능}



## 명령어

{서브명령어 테이블}



## 사용 예시

{주요 사용 시나리오}



## 워크플로우

{실행 흐름}



## 관련 스킬

{연관 스킬 목록}

```



## 서브에이전트



| 단계 | 에이전트 | 모델 | 용도 |

|------|----------|------|------|

| 스캔 | Explore | haiku | 스킬/명령어/플러그인 목록 수집 (병렬) |

| 생성 | writer | haiku | 튜토리얼 문서 작성 (병렬) |



## 관련



`.claude/skills/ootutorial/scripts/ootutorial_run.py` | `.claude/skills/oohelp/SKILL.md` | `00_doc/tutorial/README.md`



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



