# [스킬명] check 체크리스트

> [스킬명] 스킬 자체 건강 상태 검증 항목

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/*.py 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 스킬 고유 항목 1 | (스킬별 핵심 검증 내용) | CRITICAL/ERROR/WARNING/INFO |
| C04 | 스킬 고유 항목 2 | (스킬별 핵심 검증 내용) | CRITICAL/ERROR/WARNING/INFO |
| C05 | 스킬 고유 항목 3 | (스킬별 핵심 검증 내용) | CRITICAL/ERROR/WARNING/INFO |

## check 출력 형식

```
[[스킬명] check]

C01 필수 파일 존재   [OK]
C02 버전 일치        [OK]
C03 ...              [WARN]  설명
C04 ...              [ERROR] 설명
C05 ...              [OK]

소계: OK:3 | WARN:1 | ERROR:1
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |

## 작성 가이드

1. **C01~C02**: 공통 항목 (모든 스킬 필수)
2. **C03 이후**: 스킬 고유 검증 항목 추가
   - 스킬이 의존하는 외부 도구/환경 (예: `uv`, `node`, API 키)
   - 스킬이 생성/관리하는 파일 존재 여부
   - 스킬 특유의 설정 정합성 (예: 버전 일치, 경로 유효성)
3. **개수**: 5~10개 권장 (너무 많으면 유지보수 부담)
