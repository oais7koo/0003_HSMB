# ooflow check 체크리스트

> ooflow 스킬 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/ooflow_run.py 존재 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 연계 스킬 존재 | oofeature, oodev, oocheck, oofix, oodoc, oohistory, oocommit 정상 존재 | ERROR |
| C04 | 튜토리얼 동기화 | 11_SW개발워크플로우.md 전체 흐름과 워크플로우 섹션 일치 | WARNING |
| C05 | PRD/Plan 존재 | 현재 SP의 d{SP}0001_prd.md, d{SP}0002_plan.md 존재 | WARNING |

## check 출력 형식

```
[ooflow check]

C01 필수 파일 존재     [OK]
C02 버전 일치         [OK]
C03 연계 스킬 존재    [OK]
C04 튜토리얼 동기화   [OK]
C05 PRD/Plan 존재     [WARN]

소계: OK:4 | WARN:1 | ERROR:0
```
