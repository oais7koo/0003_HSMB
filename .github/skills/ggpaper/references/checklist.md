# ggpaper check 체크리스트 (Copilot)

ooopaper checklist.md 기반, Copilot 환경에 맞게 수동 검증/점검용으로 변환

| ID  | 항목               | 검증 내용                                                     | 심각도   |
| --- | ------------------ | ------------------------------------------------------------- | -------- |
| C01 | 필수 파일 존재     | SKILL.md 등 핵심 파일 존재 여부 (직접 확인)                   | CRITICAL |
| C02 | 버전 일치          | metadata version <-> 서브명령어 테이블 (vXX) 일치 (수동 확인) | ERROR    |
| C03 | 03_paper 디렉터리  | 논문 저장 디렉터리 존재 (수동 확인)                           | CRITICAL |
| C04 | 논문 카운트 정합성 | 실제 파일 수와 관리 목록 일치 (수동 확인)                     | ERROR    |
| C05 | 다국어 지원        | --lang en/ko 옵션 동작 (수동 확인)                            | WARNING  |
| C06 | 논문폴더 형식 표준 | 논문폴더 네이밍/구조가 표준 규칙 준수 여부 (수동 확인)        | ERROR    |

## check 출력 형식 (예시)

```
[ggpaper check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 03_paper 디렉터리        [OK]
C04 논문 카운트 정합성           [OK]
C05 다국어 지원               [OK]

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
- ooopaper checklist.md를 참고하여 직접 점검/기록
