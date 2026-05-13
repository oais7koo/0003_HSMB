# oonow check 체크리스트

> oonow 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oonow_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | TODO 문서 접근 | d0004_todo.md 읽기 가능 여부 | WARNING |
| C04 | 세션 컨텍스트 | 현재 SP 컨텍스트 감지 가능 여부 | INFO |
| C05 | 이력 문서 접근 | d0010_history.md 읽기 가능 여부 | INFO |

## check 출력 형식

```
[oonow check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 TODO 문서 접근            [OK]
C04 세션 컨텍스트              [INFO] AI 직접 감지
C05 이력 문서 접근             [OK]

소계: OK:4 | WARN:0 | ERROR:0
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
