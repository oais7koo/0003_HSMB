# oodata check 체크리스트

> oodata 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oodata_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | data/ 폴더 존재 | 백업 대상 data/ 폴더 접근 가능 여부 | CRITICAL |
| C04 | 외부 백업 경로 설정 | references/config.json 또는 환경변수에서 백업 경로 정의 | ERROR |
| C05 | zip 의존성 | Python zipfile 모듈 사용 가능 (표준 라이브러리) | WARNING |
| C06 | 백업 파일명 규칙 | YYMMDD-HHMMSS.zip 형식 준수 | WARNING |
| C07 | 복원 안전성 | 복원 시 기존 data/ 폴더 덮어쓰기 경고/확인 절차 | ERROR |

## check 출력 형식

```
[oodata check]

C01 필수 파일 존재             [OK]
C02 버전 일치                  [OK]
C03 data/ 폴더 존재            [OK]
C04 외부 백업 경로 설정        [WARN]  config.json 미작성
C05 zip 의존성                 [OK]
C06 백업 파일명 규칙           [OK]
C07 복원 안전성                [OK]

소계: OK:6 | WARN:1 | FAIL:0
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | ❌ | 스킬 동작 불가 (즉시 조치) |
| ERROR | ⚠️ | 정상 동작 어려움 (24시간 내) |
| WARNING | ⚡ | 품질 저하 (1주 내) |
| INFO | ℹ️ | 개선 권장 (백로그) |
