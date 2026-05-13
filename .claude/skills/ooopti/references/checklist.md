# ooopti check 체크리스트

> ooopti 스킬 자체 건강 상태 + 최적화 품질 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

## 스킬 건강 상태

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/ooopti_run.py 존재 | CRITICAL |
| C02 | 버전 일치 | metadata version == 서브명령어 표 버전 | ERROR |
| C03 | 프로파일러 사용 가능 | cProfile import 가능 | WARNING |

## 최적화 품질 검증

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| O01 | 측정 선행 | 프로파일링 결과가 최적화 전에 존재 | CRITICAL |
| O02 | 기능 보존 | 최적화 후 기존 테스트 전부 통과 | CRITICAL |
| O03 | 벤치마크 비교 | 전/후 실행 시간 수치 비교 존재 | ERROR |
| O04 | 복잡도 명시 | 변경 전/후 시간복잡도 명시 | WARNING |
| O05 | 가독성 판단 | 10% 미만 개선 시 가독성 우선 확인 | WARNING |
| O06 | 리포트 생성 | d{SP}0012_optimization.md 존재 | INFO |

## check 출력 형식

```
[ooopti check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 프로파일러 사용 가능       [OK]
O01 측정 선행                [OK]
O02 기능 보존                [OK]
O03 벤치마크 비교             [OK]
O04 복잡도 명시              [WARN]
O05 가독성 판단              [OK]
O06 리포트 생성              [INFO]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 최적화 무효 (테스트 실패, 측정 없음) |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
