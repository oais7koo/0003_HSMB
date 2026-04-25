# oocheck check 체크리스트

> oocheck 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 검사 대상 .py 존재 | src/, oo/, tests/ 등에 .py 파일 존재 | CRITICAL |
| C04 | pylint/mypy 설치 | 정적 분석 도구 설치 여부 | WARNING |
| C05 | d0004 쓰기 가능 | 에러 등록 대상 todo 파일 접근 가능 | ERROR |
| C06 | 에러 분류 정확성 | CRITICAL/ERROR/WARNING/INFO 분류 출력 | ERROR |

## check 출력 형식

```
[oocheck check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 검사 대상 .py 존재         [OK]
C04 pylint/mypy 설치       [OK]
C05 d0004 쓰기 가능          [OK]
C06 에러 분류 정확성            [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
