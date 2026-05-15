---
name: oodata
description: "data/ 폴더 백업·복원·문서화 스킬. 'oodata', 'data 백업', 'data 복원', 'data 문서화' 등을 요청할 때 트리거된다"
metadata:
  version: "v02"
  category: "meta-util"
---

# oodata - data/ 폴더 핸들링 스킬

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | data/ 폴더 문서화(run) + 외부 경로 백업·복원 |
| **하는 것** | data/ 서브폴더 목록화·설명 문서 생성(run), ps폴더 이동(backup), _backup 마커 생성/제거, 외부 경로 복원(restore), 현황 조회(list) |
| **하지 않는 것** | 코드 실행(→oorun), 환경 설치(→ooenv), 문서 동기화(→oosync) |
| **참조 범위** | 현재 프로젝트 data/ 폴더 (SP 무관, 프로젝트 공통) / 사용자 지정 외부 경로 |
| **수정 대상** | `00_doc/sp00/d0007_data.md` (SP 공통, 단일 문서), data/ 폴더 구조, 외부 백업 경로 |
| **실행 레벨** | [수동] — 사용자 명시 요청 시에만 실행 |
| **에이전트 호환** | Claude Code 권장 — `uv run` 기반 인터랙티브 실행 |

## 문서 이력 관리
- v04 2026-05-15 — 상세 섹션 추가: 폴더별 파일 수·확장자 분포·서브폴더 트리·추정 성격·코멘트 표시 (`build_detail_section`)
- v03 2026-05-15 — 문서 경로 SP 공통화: `d0007_data.md` 단일 문서 (`00_doc/sp00/`) — data/는 프로젝트 공통 폴더이므로 SP 무관
- v02 2026-05-14 — run 서브명령어 추가: data/ 서브폴더 목록화 + d0007 문서 생성/업데이트
- v01 2026-04-14 — 초기 생성 — backup/restore/list 서브명령어

---

## 서브명령어

| 명령어 | 설명 |
|--------|------|
| `oodata help` | 서브명령어 목록 표시 |
| `oodata version` | 스킬 버전 정보 (v04) |
| `oodata status` | 스킬 상태 및 경로 정보 표시 |
| `oodata run` | data/ 서브폴더 스캔 → d0007_data.md 생성/업데이트 |
| `oodata comment <폴더명> "<메모>"` | 특정 서브폴더 설명에 메모 추가 → d0007_data.md 업데이트 |
| `oodata list` | data/ 폴더 현황 (실제 폴더 + 백업 마커) |
| `oodata backup` | 대상 폴더 선택 후 외부 경로로 이동 + _backup 마커 생성 |
| `oodata restore` | _backup 마커 기준으로 외부 경로에서 data/ 로 복원 |

실행: `uv run python .claude/skills/oodata/scripts/oodata_run.py [서브명령어]`

## 워크플로우

### run 절차 (d0007_data.md 생성/업데이트)
1. `data/` 내 서브폴더 전체 스캔 (백업 마커 포함 여부 병기)
2. 각 서브폴더의 내용 파악 — 파일 수·확장자 분포·서브폴더 트리·추정 성격
3. `d0007_data.md` 에 **서브폴더 목록(요약 테이블)** + **폴더 상세 섹션** 두 섹션 생성/업데이트
4. 기존 설명·코멘트는 보존 (재실행 시 누적, 삭제하지 않음)

**d0007_data.md 포맷**:
```markdown
# data/ 폴더 구조 (프로젝트 공통)

## 서브폴더 목록
| 폴더 | 상태 | 설명 |
|------|------|------|
| ps1000_원본데이터/ | 존재 (12.3 MB) | (코멘트) |
| ps3000_실험결과/ | 백업됨 | ... |

## 폴더 상세

### ps1000_원본데이터/
- 상태: 존재 (12.3 MB)
- 코멘트: (oodata comment로 추가된 내용)
- 총 파일 수: 234개
- 주요 확장자: `.png` 200, `.json` 30, `.txt` 4
- 서브폴더:
  - `train/` (180 files)
  - `val/` (20 files)
- 추정 성격: 이미지 위주 (200/234) · 원본 데이터 추정 (백업 정책: 제외)
```

### comment 절차 (서브폴더 메모 추가)
1. `d0007_data.md` 로드 (없으면 `oodata run` 먼저 실행 안내)
2. 지정 서브폴더 행 탐색
3. 해당 폴더 설명에 메모 내용 추가 (기존 설명 보존, 뒤에 덧붙임)
4. `d0007_data.md` 저장

```bash
oodata comment ps1000_원본데이터 "2026-05-14 재생성 불가 확인됨"
oodata comment ps3000_실험결과 "최종 제출본 포함"
```

### backup 절차
1. 백업 대상 경로 입력 (기본: `f:\udd\data_exa\exa63_dual_branch\`)
2. data/ 내 ps 폴더 목록 표시 → 선택 (번호 / 쉼표 구분 복수 / all)
3. 확인 후 이동: `data/{ps}/` → `{백업경로}/{ps}/`
4. 마커 생성: `data/{ps}_backup/` (빈 폴더)

### restore 절차
1. 백업 경로 입력 (기본 동일)
2. data/ 내 `_backup` 마커 목록 표시 → 선택
3. 확인 후 복원: `{백업경로}/{ps}/` → `data/{ps}/`
4. 마커 제거: `data/{ps}_backup/`

## 백업 정책 (d0040_실험데이터.md §6.6 기준)

| 분류 | ps 범위 | 기본 정책 |
|------|---------|----------|
| 원본 입력 데이터 | ps1000번대 | 기본 제외 (용량 크고 재생성 가능) |
| Inopam 실험 결과 | ps3000번대 | 백업 대상 |
| CrackSeg9k 실험 결과 | ps4000번대 | 백업 대상 |

> 백업은 **사용자가 명시적으로 요청할 때만** 수행 (자동 백업 없음)

## 서브에이전트

| 단계 | 에이전트 | 모델 | 병렬 |
|------|---------|------|:----:|
| 백업/복원 실행 | `task-executor` | sonnet | O |
| 결과 검증 | `task-checker` | sonnet | - |

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

> **관련 명령어**: analyze, implement (`.claude/commands/sc/`)

## 관련 문서

| 문서 | 용도 |
|------|------|
| `00_doc/sp00/d0007_data.md` | **data/ 폴더 구조·설명 문서** (SP 무관 단일 문서, oodata 관리 전용, 번호 0007 예약) |
| `00_doc/sp00/d0040_실험데이터.md §6.6` | 백업 정책 원문 |
| `00_doc/sp00/d0001_prd.md §5.6` | 실험 데이터 백업 정책 |
