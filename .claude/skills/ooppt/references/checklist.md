# ooppt check 체크리스트

> ooppt 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | python-pptx 설치 | PPT 생성 라이브러리 설치 | CRITICAL |
| C04 | 템플릿 존재 | PPT 템플릿 파일 존재 | WARNING |
| C05 | 출력 경로 유효 | PPT 저장 경로 접근 가능 | ERROR |
| C06 | 폰트 latin+ea 동시 설정 | run의 a:latin 설정 시 a:ea(동아시아)도 반드시 설정 (누락 시 한글이 테마 폰트로 표시됨) | ERROR |
| C07 | 테마/마스터/레이아웃 폰트 | 슬라이드 마스터, 테마 폰트(majorFont/minorFont), 레이아웃의 defRPr도 대상 폰트로 변경 | WARNING |
| C08 | 폰트 변경 3계층 | run 폰트 → 마스터/레이아웃 폰트 → 테마 폰트(latin+ea+cs) 순서로 전체 변경 | ERROR |

## check 출력 형식

```
[ooppt check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 python-pptx 설치       [OK]
C04 템플릿 존재               [OK]
C05 출력 경로 유효             [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
