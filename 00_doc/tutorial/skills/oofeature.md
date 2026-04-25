# oofeature Tutorial

> 기능별 상세 문서(상세기획/설계/개발/검증/완료) 생성·단계 전환·현황 관리 스킬. | 버전: v15 | 카테고리: core-dev

## §1. 개요

| 항목 | 내용 |
|------|------|
| **핵심 역할** | 기능별 상세 문서를 기획→설계→개발→검증→완료 5단계로 생명주기 관리 |
| **하는 것** | 상세기획/설계/개발/검증/완료 문서 생성, 파일명 rename으로 단계 전환, 미착수 Feature 리스트업 |
| **하지 않는 것** | 코드 구현(→oodev), 테스트 실행(→ootest), 코드 체크(→oocheck) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (`00_doc/sp{N}/dXXXX_*.md`) / 외부 프로젝트 자동 포함 안 함 |
| **수정 대상** | `00_doc/sp{N}/dXXXX_상세*.md` (파일명 rename 포함) |
| **실행 레벨** | [반자동] — 단계 전환 전 현재 단계 확인 후 실행 |
| **에이전트 호환** | Claude Code 권장 — Agent 도구로 서브에이전트 위임 필수 (메인 컨텍스트 보호) |

> ⚠️ **필수**: next/run 명령 시 반드시 Agent 도구로 executor(sonnet) 상세 문서 읽기 및 생성 순서로 위임할 것. 상세 문서 직접 읽기 금지 — 메인 컨텍스트 보호.

> ⚠️ **이슈 우선 원칙**: 모든 작업 전 대상 상세 문서를 확인하여 미해결 이슈가 있으면 해당 이슈 해결에 집중한다. 새 기능 진행보다 기존 이슈 해소가 우선이다.

---

## §2. 명령어 목록

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `oofeature help` | 서브명령어 목록 표시 | 터미널 |
| `oofeature version` | 스킬 버전 정보 | 터미널 |
| `oofeature status` | 현재 SP 상세 문서 현황 | 터미널 |
| `oofeature new dXXXX "기능명"` | 상세기획 문서 생성 (공통 템플릿) | `dXXXX_상세기획_기능명.md` |
| `oofeature new dXXXX "기능명" --stage 설계` | 특정 단계로 생성 | `dXXXX_상세설계_기능명.md` |
| `oofeature new dXXXX "기능명" --framework streamlit` | Streamlit 전용 템플릿으로 생성 | `dXXXX_상세기획_기능명.md` |
| `oofeature new dXXXX "기능명" --framework fastapi` | FastAPI 전용 템플릿으로 생성 | `dXXXX_상세기획_기능명.md` |
| `oofeature next dXXXX` | 다음 단계로 파일명 변경 + 연계 스킬 실행 | 파일 rename |
| **`oofeature next this`** | **직전 작업 상세 문서 다음 단계** (→ common_guide.md §9) | 파일 rename |
| `oofeature stage dXXXX 단계` | 단계 수동 변경 (파일 rename만) | 파일 rename |
| `oofeature list` | 현재 SP 상세 문서 목록 + 단계 현황 | 터미널 |
| **`oofeature needed`** | **plan.md Feature 교차 비교 → 상세기획 미착수 Feature 리스트업** | 터미널 |
| `oofeature needed --sp N` | 특정 SP의 미착수 Feature 리스트업 | 터미널 |
| `oofeature sync` | plan.md 8.2절 강제 갱신 | plan.md |
| `oofeature update` | plan.md + 상세 문서 변경 자동 감지 → 롤백 후보 표시 | 터미널 |
| `oofeature update --apply` | 변경 감지 → 상세기획 롤백 실행 | 파일 rename |
| `oofeature update --force` | `--apply` 와 동일 (별칭) | 파일 rename |
| `oofeature update --dry` | 롤백 미리보기 (실제 수정 안 함) | 터미널 |
| `oofeature update --from-plan` | (하위 호환) plan.md 변경 기반 이전 단계 롤백 | 터미널 |
| `oofeature update --from-doc` | (하위 호환) 상세개발 문서 변경 + oocheck 기반 롤백 | 터미널 |
| `oofeature note dXXXX "내용"` | 상세 문서 ## 메모 섹션에 날짜+내용 추가 | 파일 수정 |
| `oofeature note dXXXX "내용" --sp N` | 특정 SP 상세 문서에 메모 추가 | 파일 수정 |
| `oofeature issue dXXXX "이슈내용"` | 상세 문서 ## 이슈 섹션에 이슈 추가 (🔴 미해결) | 파일 수정 |
| `oofeature issue dXXXX "이슈내용" --sp N` | 특정 SP 상세 문서에 이슈 추가 | 파일 수정 |
| `oofeature issue dXXXX --resolve` | 최신 미해결 이슈 → ✅ 해결 처리 | 파일 수정 |
| `oofeature validate` | 상세 문서 정합성 검증 (V01~V08) | 터미널 |
| `oofeature validate --sp N` | 특정 SP 상세 문서 검증 | 터미널 |
| `oofeature validate --verbose` | 상세 메시지 포함 출력 | 터미널 |
| `oofeature validate --dry-run` | 검증 대상 목록만 출력 | 터미널 |
| `oofeature check` | references/checklist.md 기반 체크 | 터미널 |

실행(validate): `uv run python .claude/skills/oofeature/scripts/oofeature_validate.py [--sp N] [--verbose] [--dry-run]`

---

## §3. 자주 쓰는 명령

```bash
# 상세기획 생성 (파일 없으면 자동 생성)
oofeature next dXXXX

# 다음 단계로 전환 (기획→설계→개발→검증→완료)
oofeature next dXXXX

# 직전 작업 문서 다음 단계
oofeature next this

# 현재 SP 상세 문서 목록 확인
oofeature list

# plan.md 미착수 Feature 확인
oofeature needed

# 메모 추가
oofeature note dXXXX "입력 유효성 조건 추가"

# 이슈 추가 / 해결
oofeature issue dXXXX "API 응답 형식 불일치"
oofeature issue dXXXX --resolve

# 정합성 검증
oofeature validate
```

---

## §4. 권장 흐름

### Feature 1개 기준 표준 개발 흐름

```
oofeature next dXXXX           # 상세기획 생성 (파일 없으면 자동 생성, plan.md 기능명 조회)
oofeature next dXXXX           # 기획→설계 (의도적 게이트, 설계 작성)
oofeature next dXXXX           # 설계→개발 전환 + oodev run 자동 연계 (TC/코딩)
oofeature next dXXXX           # 개발→검증 전환 + oocheck run 자동 연계 (코드 체크)
[oofix run]                    # 이슈 수정 (필요시)
oofeature next dXXXX           # 검증→완료 전환 + oocommit run 자동 연계
```

### `oofeature new` vs `oofeature next` 선택 기준

| 상황 | 권장 명령 |
|------|----------|
| plan.md에 Feature 있음 (일반) | `oofeature next dXXXX` |
| plan.md에 없는 기능 추가 | `oofeature new dXXXX "기능명"` |
| 기능명을 직접 지정하고 싶을 때 | `oofeature new dXXXX "기능명"` |

### plan.md 연동 흐름

```
ooplan run                      # plan.md Feature 목록 생성
oofeature needed                # 미착수 Feature 리스트업
oofeature next dXXXX            # Feature별 상세기획 시작
oofeature sync                  # plan.md 8.2절 갱신
```

---

## §5. 실전 시나리오

### 시나리오 A: 신규 Feature 상세기획 시작

```bash
# 1. 미착수 Feature 확인
oofeature needed

# 2. 상세기획 생성 (FastAPI 기반 SP)
oofeature new d41010 "데이터수집소스" --framework fastapi

# 3. 기획 완료 후 설계 단계 전환
oofeature next d41010

# 결과: d41010_상세기획_데이터수집소스.md → d41010_상세설계_데이터수집소스.md
```

### 시나리오 B: 단계 전환 전체 흐름

```bash
# 설계 완료 후 개발 단계 전환 (oodev run 자동 연계)
oofeature next d41010
# → d41010_상세설계_데이터수집소스.md → d41010_상세개발_데이터수집소스.md
# → oodev run d41010 자동 실행 (TC RED + 코딩)

# 개발 완료 후 검증 단계 전환 (oocheck run 자동 연계)
oofeature next d41010
# → d41010_상세개발_데이터수집소스.md → d41010_상세검증_데이터수집소스.md
# → oocheck run d41010 자동 실행

# 검증 완료 후 최종 완료
oofeature next d41010
# → d41010_상세검증_데이터수집소스.md → d41010_상세완료_데이터수집소스.md
# → oocommit run 자동 연계
```

### 시나리오 C: 이슈 관리

```bash
# 개발 중 이슈 등록
oofeature issue d41010 "Spring 연동 시 apl_id 누락 케이스 처리 필요"

# 이슈 확인 후 해결
oofeature issue d41010 --resolve

# 메모 추가 (요구사항 변경)
oofeature note d41010 "입력 파라미터에 timeout 추가 — 기본값 30초"
```

### 시나리오 D: 현황 조회 및 정합성 검증

```bash
# SP 전체 상세 문서 현황 확인
oofeature list

# 출력 예시:
# [oofeature list] SP04
# | 문서번호 | 기능명 | 단계 | 파일 |
# | d41010 | 데이터수집소스 | 🔵설계 | d41010_상세설계_데이터수집소스.md |
# | d41020 | 크롤러모듈 | 🟡개발 | d41020_상세개발_크롤러모듈.md |
# 총 2개 | 기획:0 설계:1 개발:1 검증:0 완료:0

# 정합성 검증
oofeature validate --sp 4
```

---

## §6. 워크플로우 상세

### 파일명 규칙

```
d{SP번호}{기능번호}_상세{단계}_{기능명}.md
```

| 구성 | 설명 | 예시 |
|------|------|------|
| `d{SP번호}{기능번호}` | SP+기능 식별자 | `d41001`, `d51001` |
| `_상세{단계}_` | 현재 단계 | `_상세기획_`, `_상세설계_` |
| `{기능명}` | 기능 한글명 | `데이터수집소스`, `크롤러모듈` |

### 5단계 생명주기

```
⚪ 상세기획 → 🔵 상세설계 → 🟡 상세개발 → 🟢 상세검증 → ✅ 상세완료
```

| 단계 | 파일명 키워드 | oof next 연계 |
|------|-------------|--------------|
| 기획 | `_상세기획_` | "설계 작성 완료 후 재실행하세요" 안내만 |
| 설계 | `_상세설계_` | `oodev run dXXXX` 자동 실행 |
| 개발 | `_상세개발_` | `oocheck run dXXXX` 자동 실행 |
| 검증 | `_상세검증_` | `oocommit run` 자동 실행 |
| 완료 | `_상세완료_` | — (최종 단계) |

### 스캔 패턴

`ooplan sync` 및 `oofeature list`가 사용하는 탐색 패턴:

```
00_doc/sp{N}/*_상세기획_*.md
00_doc/sp{N}/*_상세설계_*.md
00_doc/sp{N}/*_상세개발_*.md
00_doc/sp{N}/*_상세검증_*.md
00_doc/sp{N}/*_상세완료_*.md
```

### 번호 부여 규칙

| 범위 | 용도 |
|------|------|
| `d{SP}0001~d{SP}0999` | SP 공통 문서 (PRD, Plan, Test, Todo 등) — 예약, oofeature 미사용 |
| **`d{SP}1000~d{SP}9999`** | **상세 문서 전용 범위 (oofeature 관리 대상)** |

**카테고리 (천번대) 체계:**
- 큰 기능 카테고리별로 **1000, 2000, 3000...** 단위로 할당
- 세부 번호는 **10단위** 사용 (1010, 1020, 1030...)
- 카테고리 내 번호가 부족하면 다음 천번대로 이동

> 카테고리 정의는 각 SP의 PRD §1.4 참조 (예: SP04 → `d40001_prd.md §1.4`)

### 단계 전환 시 자동 추가 섹션

| 단계 | 자동 추가 섹션 |
|------|--------------|
| 설계 단계 | `## A. 설계 상세 (아키텍처/API/DB)` |
| 개발 단계 | `## B. 구현 노트 (Task 체크리스트)` |
| 검증 단계 | `## C. 검증 결과 (TC 통과 현황)` |
| 완료 단계 | `## D. 완료 확인 (검증 통과 확정·서명)` |

### 템플릿 선택 규칙

| 템플릿 | 파일 | 자동 감지 조건 |
|--------|------|--------------|
| 공통 (기본) | `상세기획_template.md` | 기타 모든 경우 |
| FastAPI 전용 | `상세기획_template_fastapi.md` | `--framework fastapi` 또는 `05_api_server/` 경로 |
| Streamlit 전용 | `상세기획_template_streamlit.md` | `--framework streamlit` 또는 `04_backoffice/` 경로 (SP04) |

### note 섹션 판단 기준

| 노트 내용 키워드 | 대상 섹션 |
|----------------|----------|
| 요구사항, 기능, 조건, 허용/금지 | ## 2. 요구사항 |
| 입력, 출력, API, 파라미터, 반환 | ## 3. 입출력 정의 |
| 제약, 예외, 에러, 금지, 불가 | ## 4. 제약조건 / 예외처리 |
| 연관 기능, Feature, 의존 | ## 5. 관련 Feature |
| 참고, 문서, 링크, 참조 | ## 6. 참고 자료 |
| 판단 불가 | ## 2. 요구사항 (기본값) |

### 이슈 테이블 형식

| 날짜 | 내용 | 상태 |
|------|------|------|
| 2026-04-10 | 예시 이슈 | 🔴 미해결 |
| 2026-04-09 | 해결된 이슈 | ✅ 해결 |

---

## §7. 관련 스킬

| 스킬 | 연동 내용 |
|------|----------|
| `ooplan` | plan.md 8.2절 상세 문서 현황 갱신 (`ooplan sync`) |
| `oodev` | `oodev run dXXXX` — 상세 문서 기반 TDD 개발 (설계→개발 자동 연계) |
| `oocheck` | `oocheck run dXXXX` — 상세 문서 기반 검증 (개발→검증 자동 연계) |
| `oofix` | 이슈 해결 후 검증 재실행 |
| `oocommit` | `oocommit run` — 완료 단계 전환 시 자동 연계 |

---

## §8. 주의사항

- **메인 컨텍스트 보호**: next/run 명령 시 반드시 Agent 도구로 executor 위임. 상세 문서 직접 읽기 금지
- **이슈 우선**: 미해결 이슈(🔴)가 있으면 새 기능 진행보다 이슈 해소 우선
- **파일명 규칙**: 단계가 파일명에 포함 — 파일 목록만 봐도 진행 상황 즉시 파악 가능
- **번호 범위**: 신규 문서는 반드시 `d{SP}1000` 이상 사용 (0001~0999는 예약)
- **연계는 Claude 행동**: 연계 스킬 실행은 Python 스크립트 자동 실행이 아닌, Claude가 SKILL.md 읽고 다음 스킬을 호출하는 방식
- **카테고리 정의**: SKILL.md에 SP별 카테고리 없음 → 각 SP PRD §1.4 참조

---

## §9. 산출물

| 산출물 | 경로 | 설명 |
|--------|------|------|
| 상세기획 문서 | `00_doc/sp{N}/dXXXX_상세기획_기능명.md` | 요구사항·API·TC 포함 |
| 상세설계 문서 | `00_doc/sp{N}/dXXXX_상세설계_기능명.md` | 기획 + 설계 상세 추가 |
| 상세개발 문서 | `00_doc/sp{N}/dXXXX_상세개발_기능명.md` | 설계 + 구현 노트 추가 |
| 상세검증 문서 | `00_doc/sp{N}/dXXXX_상세검증_기능명.md` | 개발 + 검증 결과 추가 |
| 상세완료 문서 | `00_doc/sp{N}/dXXXX_상세완료_기능명.md` | 검증 + 완료 확인 추가 |
| plan.md 갱신 | `00_doc/sp{N}/d{SP}0002_plan.md` | 8.2절 상세 문서 현황 테이블 |

---

## §10. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 문서 생성 | task-executor | sonnet | 템플릿 기반 문서 작성 | - |
| 스캔/분석 | Explore | haiku | 상세 문서 탐색 | - |
| plan.md 갱신 | task-executor | sonnet | 8.2절 업데이트 | - |

---

## §11. 참조

- **SKILL.md**: `.claude/skills/oofeature/SKILL.md`
- **공통 템플릿**: `.claude/skills/oofeature/templates/상세기획_template.md`
- **FastAPI 템플릿**: `.claude/skills/oofeature/templates/상세기획_template_fastapi.md`
- **Streamlit 템플릿**: `.claude/skills/oofeature/templates/상세기획_template_streamlit.md`
- **validate 스크립트**: `.claude/skills/oofeature/scripts/oofeature_validate.py`
- **공통 가이드**: `.claude/guides/common_guide.md`
- **프레임워크 레퍼런스**: `.claude/reference/development/{framework}/`

> 생성일: 2026-04-14 | 최종 동기화: 2026-04-17 (v15 기준 전면 재작성 — §1~§11 표준 구조, 5단계 완료 반영, 스캔패턴 완료 추가)
