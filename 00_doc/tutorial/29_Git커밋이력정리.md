# 시나리오: Git 커밋 및 이력 정리

> 커밋, PR, GitHub Issues 연동, 이력 아카이브 워크플로우

---

## 개요

코드 변경을 Git에 커밋하고, 완료된 이슈를 아카이브하며, GitHub Issues와 연동하는 워크플로우입니다. oocommit이 커밋과 이력 이동을 통합 처리하고, oohistory가 상세 아카이브를 담당합니다.

**이럴 때 사용:** 기능 완료 후 커밋, 이슈 정리, GitHub 연동
**결과물:** Git 커밋 + d0010_history.md 아카이브 + (선택) GitHub Issues

## 전체 흐름

```
oocommit preview → oocommit run → oohistory run → (선택) oocommit github
```

---

## 방법 1: 통합 커밋+이력 정리

### 1. 변경사항 미리보기

```bash
oocommit preview
```
- git status/diff 요약
- 커밋 메시지 제안
- d{SP}0004에서 완료 항목 목록

### 2. 커밋+이력 실행

```bash
oocommit run            # 커밋 + 이력 이동 통합
oocommit run --dry-run  # 미리보기만 (실제 커밋 안 함)
```

**5단계 워크플로우:**
```
1. 분석 → git status/diff, 커밋 메시지 자동 생성
2. 커밋 → 스테이징 + 실행 (사용자 확인)
3. 추출 → d{SP}0004에서 [x]/해결 항목 식별
4. 이동 → d{SP}0010에 추가, d{SP}0004에서 제거
5. 검증 → 무결성 확인
```

### 3. 커밋 메시지 형식

Conventional Commits 준수:

| 타입 | 용도 | 예시 |
|------|------|------|
| feat | 새 기능 | `feat(SP02): 로그인 API 구현` |
| fix | 버그 수정 | `fix(SP02): 세션 만료 처리 오류` |
| docs | 문서 | `docs(SP02): API 명세 업데이트` |
| refactor | 리팩토링 | `refactor(SP02): 인증 모듈 분리` |
| test | 테스트 | `test(SP02): 로그인 단위 테스트 추가` |
| chore | 기타 | `chore: 의존성 업데이트` |

---

## 방법 2: 커밋만 / 이력만 분리 실행

```bash
oocommit commit        # Git 커밋만 (이력 이동 안 함)
oocommit sync          # 이력 이동만 (d{SP}0004 → d{SP}0010)
```

---

## 방법 3: 상세 이력 아카이브 (oohistory)

```bash
oohistory run          # 완료 항목 → d{SP}0010 이동
oohistory status       # 이동 대상 수, 토큰 상태 확인
```

### 이동 흐름

```
d{SP}0004 "해결된 이슈" 스캔
  → 태그 추론 (error→BUGFIX, security→HOTFIX 등)
  → d{SP}0010에 등록
  → 토큰 체크 (>20K시 자동 요약)
  → d{SP}0004에서 삭제
```

### 태그 매핑

| 이슈 키워드 | d0010 태그 |
|------------|-----------|
| CRITICAL, security | HOTFIX |
| error, fix, bug | BUGFIX |
| feature, 기능 | FEATURE |
| refactor, optimize | IMPROVE |
| update, 버전 | UPDATE |
| doc, 문서 | DOCS |

---

## 방법 4: GitHub Issues 연동

```bash
oocommit github                    # 전체 태스크 → Issues 변환
oocommit github --task-id 1,2,3    # 특정 태스크만
oocommit github --dry-run          # 미리보기
oocommit github --sync             # 기존 이슈와 동기화
```

### 라벨 매핑

| 태스크 속성 | GitHub 라벨 |
|------------|-------------|
| priority: high | P0-critical |
| priority: medium | P1-important |
| type: feature | enhancement |
| type: bug | bug |

### 옵션

```bash
oocommit github --milestone "v1.0"     # 마일스톤 지정
oocommit github --project "OAIS"       # GitHub Project 연결
oocommit github --labels "backend"     # 추가 라벨
```

---

## .git 용량 관리

```bash
oocommit clear    # 오래된 커밋 squash + .git 용량 정리
```

---

## FAQ

**Q: 자동으로 커밋되나?**
A: 아닙니다. oocommit은 항상 사용자 확인을 거칩니다. `--dry-run`으로 미리보기를 권장합니다.

**Q: push도 같이 하나?**
A: 기본은 커밋만 합니다. push가 필요하면 별도로 `git push` 또는 `--no-push` 옵션을 빼세요.

**Q: 이력이 너무 길어지면?**
A: oohistory가 d0010이 20K 토큰을 넘으면 자동 요약합니다. `--compact` 옵션으로 3KB 이내로도 가능합니다.

---

> 관련: [기본 워크플로우](11_기본개발워크플로우.md) | [버그 수정](00_doc/tutorial/13_버그수정흐름.md)
