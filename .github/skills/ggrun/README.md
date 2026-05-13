# ggrun Skill

- **기능**: ggrun <명령어> 실행 후, 전체 로그를 00_doc/yyy.md에 append
- **구성**:
  - SKILL.md: 명세 및 사용법
  - scripts/ggrun_run.py: 명령 실행 및 기록 스크립트

## 실행 예시

```bash
uv run python .claude/skills/ggrun/scripts/ggrun_run.py ls -al
```

## 결과 예시 (00_doc/yyy.md)

```
## [2026-04-18 12:34:56] ggrun: ls -al
- 실행 환경: Windows, Python 3.10, .venv 활성화
- 명령어: ls -al
- 실행 디렉토리: d:/resilio/1_oais
- 종료 코드: 0
- 실행 시간: 0.12초

### STDOUT
...
### STDERR
...
---
```

## 참고
- 위험 명령은 별도 경고/확인 필요
- 로그는 append 모드로 누적
