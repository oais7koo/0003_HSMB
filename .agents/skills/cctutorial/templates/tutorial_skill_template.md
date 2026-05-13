# oo{skill_name} Tutorial

> {한 줄 설명} | 버전: {vNN} | 카테고리: {core-dev|doc-env|meta-util|content}

## 1. 이 스킬은 왜 필요한가?

{이 스킬이 해결하는 문제를 1~3문장으로 설명}

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oo{skill_name} run

# 상태 확인
oo{skill_name} status

# 도움말
oo{skill_name} help
```

## 3. 자주 쓰는 명령 요약

> 이것만 기억하면 됩니다.

| # | 명령어 | 언제 쓰나 |
|---|--------|----------|
| 1 | `oo{skill_name} status` | 현재 상태 확인 |
| 2 | `oo{skill_name} run` | 기본 실행 |
| 3 | `oo{skill_name} {sub1}` | {상황 1} |
| 4 | `oo{skill_name} {sub2}` | {상황 2} |

**예시 (oofeature):**

| # | 명령어 | 언제 쓰나 |
|---|--------|----------|
| 1 | `oof status` | 현재 SP 상세 문서 현황 확인 |
| 2 | `oof list` | 상세 문서 목록 + 단계 상태 |
| 3 | `oof new dXXXX "기능명"` | 새 상세기획 문서 생성 |
| 4 | `oof next dXXXX` | 다음 단계로 전환 |
| 5 | `oof needed` | 미착수 Feature 찾기 |
| 6 | `oof note dXXXX "메모"` | 상세 문서에 메모 추가 |
| 7 | `oof validate` | 정합성 검사 |

## 4. 권장 흐름 (이렇게 쓰세요)

```
{단계1} → {단계2} → {단계3} → ... → {완료}
```

{각 단계별 어떤 명령을 쓰는지, 다른 스킬과 어떻게 연계되는지 설명}

**예시 (oofeature 표준 개발 흐름):**

```
1. oof needed              ← 미착수 Feature 확인
2. oof next dXXXX          ← 상세기획 생성 (파일 없으면 자동 생성)
3. oof next dXXXX          ← 기획→설계 전환
4. oodev run dXXXX         ← 설계→개발 (TDD: RED→GREEN→REFACTOR)
5. oocheck run dXXXX       ← 개발→검증 (코드 체크 + 이슈 등록)
6. [oofix run]             ← 이슈 수정 (필요시)
7. oof next dXXXX          ← 완료 처리
```

> 핵심: `oof next`는 기획→설계만 직접 전환. 설계→개발은 `oodev`, 개발→검증은 `oocheck`가 자동 처리.

## 5. 전체 명령어

| 명령어 | 설명 |
|--------|------|
| `oo{skill_name} help` | 서브명령어 목록 표시 |
| `oo{skill_name} version` | 스킬 버전 정보 |
| `oo{skill_name} status` | 현재 상태 |
| `oo{skill_name} check` | 체크리스트 기반 검증 |
| `oo{skill_name} run` | 기본 실행 |

## 6. 상세 사용법

### 핵심 기능

{주요 기능별 상세 설명 - SKILL.md의 워크플로우/실행규칙에서 추출}

### 옵션

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 미리보기 (실제 수정 안 함) |
| `--sp N` | 특정 서브프로젝트 지정 |

## 7. 실전 예시

### 기본 사용
```bash
# 예: 현재 SP 상태 확인
oo{skill_name} status
```

### 응용 사용
```bash
# 예: 특정 SP 대상 실행
oo{skill_name} run --sp 04
```

### 실전 시나리오

> 실제 작업 흐름에서 이 스킬을 어떻게 쓰는지 보여주는 시나리오

```
사용자: "d40321 CMS 기능 기획서를 만들고 싶다"

1. oof new d40321 "cms매핑api"
   → 00_doc/sp04/d40321_상세기획_cms매핑api.md 생성

2. (기획 내용 작성)

3. oof next d40321
   → 상세기획 → 상세설계로 전환

4. oof list
   → d40321 | cms매핑api | 설계 | d40321_상세설계_cms매핑api.md
```

## 8. 입출력

### 입력
| 항목 | 타입 | 필수 | 설명 |
|------|------|:----:|------|

### 출력
| 출력 | 형식 | 설명 |
|------|------|------|

## 9. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.

**Q: 별칭(alias)이 있나요?**
A: `oof` = `oofeature`, `ook` = `oocheck` 등 약어 별칭이 있습니다. `.claude/CLAUDE.md`의 alias 스킬 테이블 참조.

**Q: 다른 스킬과 어떻게 연계되나요?**
A: §4 권장 흐름을 참조하세요. 대부분의 oo 스킬은 단독이 아닌 체인으로 사용됩니다.

> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 10. 서브에이전트

| 단계 | 에이전트 | 모델 | 용도 |
|------|----------|------|------|

> 서브에이전트를 쓰지 않으면 "없음" 표기

## 11. 관련 스킬

| 스킬/문서 | 역할 |
|----------|------|

---

> 생성일: {YYYY-MM-DD HH:MM} | ootutorial {vNN}
