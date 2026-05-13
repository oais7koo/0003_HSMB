# ooplan check 체크리스트

> ooplan 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | d0001 존재 | PRD 파일 존재 (계획 기반) | ERROR |
| C04 | d0002 쓰기 가능 | 계획 문서 생성/수정 가능 | CRITICAL |
| C05 | WBS 형식 정의 | 작업 분해 구조 형식 명시 | WARNING |

## check 출력 형식

```
[ooplan check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 d0001 존재             [OK]
C04 d0002 쓰기 가능          [OK]
C05 WBS 형식 정의            [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
