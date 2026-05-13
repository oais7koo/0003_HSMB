# oonote check 체크리스트

> oonote 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | d0020 접근 | 연구노트 문서 경로 접근 가능 | ERROR |
| C04 | 노트 형식 정의 | 연구노트 마크다운 형식 명시 | WARNING |
| C05 | 타임스탬프 형식 | 날짜/시간 기록 형식 준수 | WARNING |

## check 출력 형식

```
[oonote check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 d0020 접근             [OK]
C04 노트 형식 정의             [OK]
C05 타임스탬프 형식             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
