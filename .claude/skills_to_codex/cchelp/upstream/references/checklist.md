# oohelp check 체크리스트

> oohelp 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 스킬 목록 수집 | oo* 스킬 디렉터리 스캔 가능 | CRITICAL |
| C04 | 서브명령어 파싱 | 각 SKILL.md에서 서브명령어 추출 | ERROR |
| C05 | 출력 형식 정의 | 도움말 출력 형식 명시 | WARNING |

## check 출력 형식

```
[oohelp check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 스킬 목록 수집             [OK]
C04 서브명령어 파싱             [OK]
C05 출력 형식 정의             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
