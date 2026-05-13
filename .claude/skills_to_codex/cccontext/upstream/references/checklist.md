# oocontext check 체크리스트

> oocontext 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | SP 디렉터리 존재 | 01_*~10_* 서브프로젝트 디렉터리 스캔 | ERROR |
| C04 | 문서 매핑 정합성 | SP x 10000 + 기본번호 공식 적용 | ERROR |
| C05 | CWD 감지 동작 | 작업 디렉터리 기반 SP 자동 감지 | WARNING |

## check 출력 형식

```
[oocontext check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 SP 디렉터리 존재           [OK]
C04 문서 매핑 정합성            [OK]
C05 CWD 감지 동작            [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
