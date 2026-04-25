# oopaper check 체크리스트

> oopaper 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 03_paper 디렉터리 | 논문 저장 디렉터리 존재 | CRITICAL |
| C04 | 논문 카운트 정합성 | 실제 파일 수와 관리 목록 일치 | ERROR |
| C05 | 다국어 지원 | --lang en/ko 옵션 동작 | WARNING |
| C06 | 논문폴더 형식 표준 | 논문폴더 네이밍/구조가 표준 규칙 준수 여부 | ERROR |

## check 출력 형식

```
[oopaper check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 03_paper 디렉터리        [OK]
C04 논문 카운트 정합성           [OK]
C05 다국어 지원               [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
