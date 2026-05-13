# oosync check 체크리스트

> oosync 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 동기화 대상 설정 | OAIS_SYNC_TARGET 환경변수 설정 | CRITICAL |
| C04 | oosync_run.py 존재 | 동기화 스크립트 존재 | CRITICAL |
| C05 | 대상 경로 유효 | 동기화 대상 디렉터리 접근 가능 | ERROR |
| C06 | 출력 결과 그대로 표시 | list/view 등 스크립트 결과를 텍스트 요약 없이 그대로 출력 (표 형식 포함) | WARNING |
| C07 | 템플릿 파일 로드 | templates/ 파일명이 스크립트 로드 경로와 일치 (oosync_*.md) | ERROR |
| C08 | 출력 포맷 템플릿화 | 고정 출력 섹션은 스크립트 내장이 아닌 templates/*.md 로 분리 (정적 가이드/보일러플레이트 제거 후 재발 방지) | WARNING |

## check 출력 형식

```
[oosync check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 동기화 대상 설정            [OK]
C04 oosync_run.py 존재     [OK]
C05 대상 경로 유효             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
