# oohistory Tutorial

> 프로젝트 개발 이력 관리 및 변경사항 추적 | 버전: v03 | 카테고리: doc-env

## §1. 자주 쓰는 명령어 (Quick Commands)

```bash
# 이전 세션의 주요 변경사항 조회
oohistory last

# 특정 이슈 해결 기록
oohistory bugfix --id R001

# 날짜 범위로 이력 검색
oohistory range --from 2026-04-01 --to 2026-04-14

# 카테고리별 필터링
oohistory filter --type BUGFIX,FEATURE
```

## §2. 권장 사용 흐름 (Recommended Workflow)

1. **매일 세션 시작**: `oohistory last` → 어제 작업 내용 확인
2. **주요 변경 후**: `oohistory add --type BUGFIX --desc "R001 해결"` → 이력 기록
3. **주간 정리**: `oohistory summary --week` → 주간 변경사항 요약
4. **릴리스 준비**: `oohistory range --from sprint-start --to sprint-end` → 릴리스 노트 생성

## §3. 실전 시나리오 (Practical Scenarios)

**시나리오 1: 버그 수정 추적**
- 오류 발생 → d0004_todo.md에 기록 (R021)
- 수정 완료 → `oohistory add --type BUGFIX --id R021 --desc "평문 비밀번호 환경변수로 변경"`
- 결과 검증 → d0010_history.md에 자동 이동 및 정합성 링크 생성

**시나리오 2: 신기능 릴리스 추적**
- PRD 작성 → `oohistory add --type FEATURE --desc "SP04 CMS 배치 previous_apl_id 방식 전환"`
- 구현 → `oohistory add --type UPDATE --desc "PayrollCalculator 버그 수정"`
- 테스트 → `oohistory add --type IMPROVE --desc "CMS 매칭 로직 개선"`

**시나리오 3: 문서 관리**
- 문서 생성 → `oohistory add --type DOCS --desc "d0011_streamlit_page_structure.md 작성"`
- 버전 업그레이드 → `oohistory add --type DOCS --version v02.1 --desc "PRD 섹션 재구조화"`

## §4. 핵심 개념 (Core Concepts)

**태그 시스템 (Auto-Tagging)**:
- `BUGFIX`: 버그 수정 (우선순위 높음)
- `HOTFIX`: 긴급 수정 (운영 중단 방지)
- `UPDATE`: 기능 업데이트 (기존 기능 개선)
- `FEATURE`: 신규 기능 (새로운 능력 추가)
- `IMPROVE`: 최적화 및 리팩토링
- `DOCS`: 문서 작성/수정
- `REFACTOR`: 코드 구조 개선
- `CONFIG`: 설정 변경
- `MISC`: 기타 유지보수

**워크플로우 단계**:
1. 이슈 발생 → d0004_todo.md 등록 (R시리즈)
2. 해결 작업 → `oohistory add` 기록
3. 완료 검증 → d0010_history.md 이동 (자동)
4. 이력 조회 → 링크 생성 및 추적 가능

## §5. 명령어 레퍼런스 (Command Reference)

```yaml
oohistory:
  last:
    desc: 마지막 변경사항 조회 (기본값: 10개)
    usage: oohistory last [--count N]
    
  add:
    desc: 수동으로 이력 추가
    usage: oohistory add --type [TYPE] --desc [TEXT] [--id ID] [--version VNN]
    types: BUGFIX, HOTFIX, UPDATE, FEATURE, IMPROVE, DOCS, REFACTOR, CONFIG, MISC
    
  filter:
    desc: 카테고리/태그로 필터링
    usage: oohistory filter --type TYPE1,TYPE2 [--date-from YYYY-MM-DD]
    
  range:
    desc: 날짜 범위 검색
    usage: oohistory range --from YYYY-MM-DD --to YYYY-MM-DD
    
  summary:
    desc: 기간별 요약 (주/월/분기)
    usage: oohistory summary --[week|month|quarter]
```

## §6. 내부 구조 (Internal Structure)

**d0010_history.md 형식**:
```markdown
| 버전 | 날짜 | 변경 내용 |
| :--- | :--- | :--- |
| 1.84 | 2026-04-14 | oocheck d43040: CRITICAL 1건(R021), ERROR 2건 → oohistory 태그 자동 생성 |
```

**자동 링크 생성**:
- d0004_todo.md의 R시리즈 → d0010_history.md의 완료된 항목으로 자동 링크
- 예: "R001 [ERROR] … 수정 완료" → "d0010_history.md #79에서 추적"

## §7. 통합 패턴 (Integration Patterns)

**다른 스킬과의 연계**:
- `oocheck` 실행 → 에러(R00X) 발생 → `oohistory add --type BUGFIX` 기록
- `oofix run` → 수정 완료 → `oohistory add --type UPDATE` 자동 기록
- `oocommit` → 커밋 메시지 자동 생성 (이력 기반)

**문서 동기화**:
- d0001_prd.md 변경 → `oohistory add --type DOCS --version v02.1`
- d0004_todo.md에서 완료 항목 → `oohistory add --type IMPROVE` + d0010_history.md 연결

## §8. 예제 및 응용 (Examples & Applications)

**예제 1: 주간 변경사항 요약**
```bash
oohistory summary --week > /tmp/weekly_changes.md
# 출력: 7개 FEATURE, 3개 BUGFIX, 12개 IMPROVE, 4개 DOCS
```

**예제 2: 특정 이슈 추적**
```bash
oohistory filter --id R001 --type BUGFIX
# 결과: R001 [ERROR] 카드내역 파일 변경 감지 미초기화 → 2026-04-14 수정됨
```

**예제 3: 릴리스 노트 생성**
```bash
oohistory range --from 2026-03-01 --to 2026-04-14 --format release-notes
# 자동 생성: ## SP04 Release v02.1 ... FEATURE 7개, BUGFIX 3개, IMPROVE 12개
```

## §9. 문제 해결 (Troubleshooting)

**Q: 이력 기록이 누락되었다**
- `oohistory check` → 미기록 이슈 검사
- 수동 추가: `oohistory add --type MISC --date 2026-04-13 --desc "..."`

**Q: 날짜 형식이 잘못되었다**
- 표준 형식: YYYY-MM-DD (2026-04-14)
- ISO 8601: 2026-04-14T15:54:13Z (자동 현재시간)

**Q: d0010_history.md와 d0004_todo.md 동기화 오류**
- `oohistory sync` → 양쪽 문서 자동 정합성 검사 및 수정

## §10. 고급 팁 (Advanced Tips)

1. **버전 번호 추적**: `--version v02.1` → 문서 버전 관리와 연동
2. **크로스 참조**: `--ref d0001_prd.md` → 관련 문서 자동 링크
3. **배치 기록**: 여러 이슈 한 번에 → `oohistory batch < issues.txt`
4. **검색 최적화**: 태그 조합으로 빠른 조회 → `--type BUGFIX,HOTFIX --priority HIGH`

## §11. 다음 단계 (Next Steps)

- **이력 활용**: `oocommit` 실행 시 이력 자동 반영 → 커밋 메시지 자동 생성
- **품질 추적**: 주간 요약으로 팀 성과 측정
- **트렌드 분석**: 월간 집계로 기술부채 추적

---

> 생성일: 2026-04-14 | ootutorial v03
