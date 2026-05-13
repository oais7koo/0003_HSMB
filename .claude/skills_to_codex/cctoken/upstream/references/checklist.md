# ootoken check 체크리스트

> ootoken 스킬 자체 건강 상태 검증 항목

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/ootoken_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 캐시 파일 접근 | ~/.claude/plugins/oh-my-claudecode/.usage-cache.json 존재 및 읽기 가능 | CRITICAL |
| C04 | 캐시 데이터 유효성 | data 필드에 fiveHourPercent, weeklyPercent 등 필수 키 존재 | ERROR |
| C05 | 시간대 변환 정확성 | UTC -> KST 변환 및 여유/초과 계산 정상 동작 | ERROR |
| C06 | 스크립트 인코딩 | cp949 환경에서 UTF-8 재설정 정상 동작 | WARNING |

## check 출력 형식

```
[ootoken check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 캐시 파일 접근             [OK]
C04 캐시 데이터 유효성           [OK]
C05 시간대 변환 정확성           [OK]
C06 스크립트 인코딩             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
