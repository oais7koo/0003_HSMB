---
name: ggrun
description: "ggrun 뒤에 오는 명령어를 실행하고, 실행 과정과 결과를 00doc/yyy.md에 기록하는 스킬"
metadata:
  version: "v01"
  category: "meta-util"
---

# ggrun - 명령 실행 및 결과 기록 스킬

> ggrun <명령어> 형식으로 호출 시, 해당 명령을 실행하고 전체 로그와 결과를 00doc/yyy.md에 상세히 저장

## 사용법

- `ggrun <명령어>`
  - 예: `ggrun ls -al`
  - 예: `ggrun uv run pytest`

## 동작 방식

1. 입력받은 명령어를 그대로 실행
2. 실행 전 환경 정보, 입력 명령, 실행 시간 기록
3. 표준 출력(stdout), 표준 에러(stderr), 종료 코드, 실행 시간 등 전체 로그를 수집
4. 모든 과정을 00doc/yyy.md에 마크다운 형식으로 저장 (명령별 append)

## 예시 출력 (00doc/yyy.md)

```
## [2026-04-18 12:34:56] ggrun: ls -al

- 실행 환경: Windows, Python 3.10, .venv 활성화
- 명령어: ls -al
- 실행 디렉토리: d:/resilio/1_oais
- 종료 코드: 0

### STDOUT
```

(여기에 표준 출력)

```

### STDERR
```

(여기에 표준 에러)

```

---
```

## 참고

- 위험 명령(파일 삭제 등)은 별도 경고/확인 절차 필요
- Python subprocess 사용, uv run 환경 권장
- 로그 파일은 append 모드로 누적 기록
