# oonext check 체크리스트

> oonext 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oonext_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 문서 접근성 | d0001_prd.md, d0002_plan.md, d0004_todo.md 존재 | CRITICAL |
| C04 | 스크립트 실행 | oonext_run.py 정상 실행 여부 | ERROR |
| C05 | 출력 형식 | 추천 테이블 형식 정상 출력 | WARNING |

## check 출력 형식

```
[oonext check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 문서 접근성              [OK]
C04 스크립트 실행             [OK]
C05 출력 형식               [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
