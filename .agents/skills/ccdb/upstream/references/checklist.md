# oodb check 체크리스트

> oodb 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | DB 문서 확인 | d0006_db.md 또는 DB 연결 설정 존재 | ERROR |
| C04 | 마이그레이션 도구 | 스키마 변경 도구 설치 여부 | WARNING |
| C05 | 백업 정책 명시 | DB 수정 전 백업 절차 정의 | WARNING |

## check 출력 형식

```
[oodb check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 DB 문서 확인             [OK]
C04 마이그레이션 도구            [OK]
C05 백업 정책 명시             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
