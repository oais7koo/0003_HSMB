# ootodo check 체크리스트

> ootodo 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | d0004 존재 | TODO 문서 존재 | CRITICAL |
| C04 | 이슈 ID 체계 | T/A/D/S 접두사 체계 준수 | WARNING |
| C05 | 우선순위 분류 | CRITICAL/ERROR/WARNING/INFO 분류 | WARNING |

## check 출력 형식

```
[ootodo check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 d0004 존재             [OK]
C04 이슈 ID 체계             [OK]
C05 우선순위 분류              [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
