# ggplan check 체크리스트 (Copilot)

ooplan checklist.md 기반, Copilot 환경에 맞게 수동 검증/점검용으로 변환

| ID  | 항목            | 검증 내용                                                     | 심각도   |
| --- | --------------- | ------------------------------------------------------------- | -------- |
| C01 | 필수 파일 존재  | SKILL.md 등 핵심 파일 존재 여부 (직접 확인)                   | CRITICAL |
| C02 | 버전 일치       | metadata version <-> 서브명령어 테이블 (vXX) 일치 (수동 확인) | ERROR    |
| C03 | d0001 존재      | PRD 파일 존재 (계획 기반, 수동 확인)                          | ERROR    |
| C04 | d0002 쓰기 가능 | 계획 문서 생성/수정 가능 (수동 확인)                          | CRITICAL |
| C05 | WBS 형식 정의   | 작업 분해 구조 형식 명시 (수동 확인)                          | WARNING  |

## check 출력 형식 (예시)

```
[ggplan check]
C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 d0001 존재             [OK]
C04 d0002 쓰기 가능          [OK]
C05 WBS 형식 정의            [OK]
소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도   | 기호    | 의미                |
| -------- | ------- | ------------------- |
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR    | [ERROR] | 즉시 수정 필요      |
| WARNING  | [WARN]  | 권장 수정           |
| INFO     | [INFO]  | 참고용              |

---

- Copilot에서는 자동 체크/출력 불가, 반드시 수동 점검 필요
- ooplan checklist.md를 참고하여 직접 점검/기록
