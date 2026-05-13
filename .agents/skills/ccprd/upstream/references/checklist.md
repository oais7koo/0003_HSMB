# ooprd check 체크리스트

> ooprd 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | d0001 쓰기 가능 | PRD 파일 생성/수정 가능 | CRITICAL |
| C04 | 템플릿 존재 | templates/prd/ 내 템플릿 1개 이상 | ERROR |
| C05 | 정합성 비교 대상 | Plan/Test/Lib/DB 문서 존재 여부 | WARNING |
| C06 | MoSCoW 할당 | 기능 목록에 우선순위 지정 | WARNING |

## check 출력 형식

```
[ooprd check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 d0001 쓰기 가능          [OK]
C04 템플릿 존재               [OK]
C05 정합성 비교 대상            [OK]
C06 MoSCoW 할당            [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
