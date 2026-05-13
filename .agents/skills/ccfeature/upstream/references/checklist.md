# oofeature check 체크리스트

> oofeature 스킬 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, templates/상세기획_template.md 존재 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 파일명 규칙 준수 | 현재 SP 상세 문서가 `d{N}_상세{단계}_{기능명}.md` 형식 준수 — `_상세{단계}_`가 번호 바로 뒤(2번째 토큰)에 위치하는지 순서까지 검증 | WARNING |
| C04 | plan.md 8.2절 동기화 | plan.md 8.2절의 상세 문서 목록이 실제 파일과 일치 | WARNING |
| C05 | 단계 연계 스킬 존재 | oodev, oocheck, ooplan 스킬 정상 존재 | ERROR |
| C06 | 네이밍 규칙 정확성 | 파일명이 `d{SP}XXXX_상세{단계}_{기능명}.md` 형식 완전 준수 — `_`으로 분리 시 토큰 순서가 `[번호, 상세단계, 기능명]` 인지 검증. `{기능명}_상세{단계}` 역순은 ERROR | ERROR |
| C07 | plan 문서 매칭 | 상세문서 번호(dXXXX)가 plan.md Feature ID와 1:1 매칭되는지 확인 (고아 문서·미연결 Feature 감지) | WARNING |
| C08 | plan-문서 단계 일치 | plan.md 8.2절에 기록된 단계와 실제 파일명의 단계 키워드(`_상세기획_` 등)가 일치하는지 확인 | ERROR |
| C09 | 엔드포인트 항목 존재 | 상세 문서 문서관리 테이블에 `엔드포인트` 행 존재 여부 확인 (아키텍처 문서는 `—` 허용) | WARNING |
| C10 | 파일명-문서내 단계 일치 | 파일명의 단계 키워드(`_상세기획_` 등)와 문서 본문 상단 `단계:` 메타데이터(또는 헤더 표기)가 일치하는지 확인 — 불일치 시 rename 누락 또는 내용 오기입 의심 | ERROR |
| C11 | 단계별 필수 섹션 존재 | 현재 단계에 맞는 필수 섹션이 문서에 존재하는지 템플릿 기준으로 확인. 기획: §1~§8 / 설계: §A(A.1 코드구조·A.2 흐름도 포함) / 구현: §B(Task 체크리스트) / 검증: §C(TC 통과 현황) / 완료: §D(완료 확인). 이전 단계 섹션 누락도 ERROR | ERROR |

## check 출력 형식

```
[oofeature check]

C01 필수 파일 존재     [OK]
C02 버전 일치         [OK]
C03 파일명 규칙 준수   [OK]
C04 plan.md 동기화    [WARN]
C05 단계 연계 스킬    [OK]

소계: OK:4 | WARN:1 | ERROR:0
```
