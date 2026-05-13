# oolib check 체크리스트

> oolib 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | oo 모듈 존재 | oo/ 디렉터리에 Python 모듈 존재 | CRITICAL |
| C04 | import 검증 | 모듈 import 오류 없음 | ERROR |
| C05 | 테스트 커버리지 | oo 모듈 테스트 파일 존재 | WARNING |

## check 출력 형식

```
[oolib check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 oo 모듈 존재             [OK]
C04 import 검증            [OK]
C05 테스트 커버리지             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
