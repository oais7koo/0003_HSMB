# oosidi check 체크리스트

> oosidi 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oosidi_run.py | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 명령어 테이블 일치 | ERROR |
| C03 | 볼트 경로 존재 | 01_obsidian/ 폴더 접근 가능 | CRITICAL |
| C04 | 스크립트 구문 검증 | python -m py_compile 통과 | ERROR |
| C05 | 인덱스 파일 정합성 | 폴더별 인덱스 파일 내 링크가 실제 파일과 일치 | WARNING |
| C06 | 빈 문서 탐지 | 헤더만 있는 문서 목록 | INFO |
| C07 | 디자인 가이드 문서 존재 여부 | (검증 내용 작성 필요) | INFO |

## check 출력 형식

```
[oosidi check]

C01 필수 파일 존재       [OK]
C02 버전 일치            [OK]
C03 볼트 경로 존재       [OK]
C04 스크립트 구문 검증   [OK]
C05 인덱스 파일 정합성   [OK]
C06 빈 문서 탐지         [INFO] N건

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
