# oostop check 체크리스트

> oostop 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 세션 상태 확인 | 현재 세션 정보 접근 가능 | WARNING |
| C04 | 정리 작업 정의 | 세션 종료 시 수행할 작업 목록 | WARNING |
| C05 | 이력 기록 | 세션 종료 이력 기록 정의 | INFO |

## check 출력 형식

```
[oostop check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 세션 상태 확인             [OK]
C04 정리 작업 정의             [OK]
C05 이력 기록                [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
