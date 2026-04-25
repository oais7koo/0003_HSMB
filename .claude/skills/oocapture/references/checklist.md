# oocapture check 체크리스트

> oocapture 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oocapture_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | Playwright 설치 | `uv run playwright install chromium` 완료 여부 | WARNING |
| C04 | Flutter SDK | flutter 명령어 실행 가능 여부 | WARNING |
| C05 | Flutter 프로젝트 | `--flutter-dir` 경로 존재 및 web 플랫폼 지원 여부 | WARNING |

## check 출력 형식

```
[oocapture check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 Playwright 설치          [WARN] chromium 미설치
C04 Flutter SDK              [OK]
C05 Flutter 프로젝트          [OK]

소계: OK:4 | WARN:1 | ERROR:0
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
