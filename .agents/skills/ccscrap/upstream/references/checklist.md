# ooscrap check 체크리스트

> ooscrap 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/ooscrap_summary.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | yt-dlp 설치 | `uv run python -c "import yt_dlp"` 오류 없이 실행 | CRITICAL |
| C04 | 입력 파일 존재 | `04_scraping/00_down/01_유튜브다운로드.md` 존재 | ERROR |
| C05 | 출력 디렉터리 존재 | `01_유튜브서머리/`, `02_유튜브동영상/`, `03_유튜브음악/`, `04_읽을거리/` 존재 | ERROR |
| C06 | 이력 파일 접근 | `02_유튜브동영상리스트.md`, `03_유튜브채널리스트.md`, `04_읽을거리리스트.md` 존재 또는 생성 가능 | WARNING |
| C07 | 파일명 규칙 정합성 | 기존 파일이 `YYMMDD-HHMMSS_첫5단어.*` 형식 준수 | WARNING |
| C08 | PRD 정합성 | SKILL.md 섹션 구조와 d40001_prd.md 기능 목록 일치 | WARNING |

## check 출력 형식

```
[ooscrap check]

C01 필수 파일 존재       [OK]
C02 버전 일치            [OK]
C03 yt-dlp 설치          [OK]
C04 입력 파일 존재       [OK]
C05 출력 디렉터리 존재   [OK]
C06 이력 파일 접근       [OK]
C07 파일명 규칙 정합성   [WARN]  2건 불일치
C08 PRD 정합성           [OK]

소계: OK:7 | WARN:1 | ERROR:0
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
