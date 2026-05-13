# ooresearch check 체크리스트

> ooresearch 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 웹 검색 가능 | WebSearch/WebFetch 도구 접근 | CRITICAL |
| C04 | 출력 디렉터리 | 연구 결과 저장 경로 존재 | ERROR |
| C05 | SOTA 비교 형식 | 비교 테이블 출력 형식 정의 | WARNING |

## check 출력 형식

```
[ooresearch check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 웹 검색 가능              [OK]
C04 출력 디렉터리              [OK]
C05 SOTA 비교 형식           [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
