# oostart check 체크리스트

> oostart 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | common_guide.md 존재 | 공통 가이드 파일 존재 | CRITICAL |
| C04 | oostart_run.py 존재 | 세션 시작 스크립트 존재 | CRITICAL |
| C05 | 환경변수 체크 | PYTHONUTF8/OAIS_SYNC_TARGET 확인 | ERROR |

## check 출력 형식

```
[oostart check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 common_guide.md 존재   [OK]
C04 oostart_run.py 존재    [OK]
C05 환경변수 체크              [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
