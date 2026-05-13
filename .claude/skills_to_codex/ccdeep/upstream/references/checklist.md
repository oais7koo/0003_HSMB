# oodeep check 체크리스트

> oodeep 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | CUDA 환경 확인 | GPU/CUDA 사용 가능 여부 확인 | WARNING |
| C04 | 학습 스크립트 존재 | 딥러닝 학습 스크립트 경로 유효 | ERROR |
| C05 | CPU 폴백 정의 | CUDA 실패 시 CPU 폴백 로직 | WARNING |

## check 출력 형식

```
[oodeep check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 CUDA 환경 확인           [OK]
C04 학습 스크립트 존재           [OK]
C05 CPU 폴백 정의            [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
