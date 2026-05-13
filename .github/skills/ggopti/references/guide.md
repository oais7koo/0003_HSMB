# ggopti 가이드 (Copilot)

> ooopti/references/guide.md 기반, Copilot 환경에 맞게 수동 워크플로우 안내로 변환

---

## 1. 개요

- **ggopti**: 알고리즘 및 코드 성능 최적화 워크플로우 안내 (자동 실행 불가)
- Copilot에서는 자동 분석/최적화/리포트 생성 불가, 수동 명령어/절차 안내만 제공

---

## 2. 기본 사용법

1. 최적화 대상 코드/모듈/함수 선정
2. 아래 명령어를 터미널에서 직접 실행
   - 프로파일링: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py profile [대상]`
   - 복잡도 분석: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py complexity [대상]`
   - 벤치마크: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py benchmark [대상]`
   - 리포트 생성: `uv run python .claude/skills/ooopti/scripts/ooopti_run.py report`
3. Copilot에서 분석 결과/리포트 파일을 열어 확인
4. 코드 개선은 직접 수정

---

## 3. 워크플로우

- [1] 대상 선정 → [2] 프로파일링/복잡도/벤치마크 실행 → [3] 결과 확인 → [4] 코드 개선 → [5] 리포트 생성
- 각 단계별 명령어는 위 참조

---

## 4. 입출력 형식

| 항목 | 내용                                                   |
| ---- | ------------------------------------------------------ |
| 입력 | 명령어 인자(파일/모듈/함수명)                          |
| 출력 | 터미널 출력, 리포트 파일(d{SP}0012_optimization.md 등) |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록                    |

---

## 5. 주의사항

- Copilot에서는 자동 실행/분석/최적화 불가 (수동 명령어 실행 필요)
- ooopti SKILL.md/guide.md를 참고하여 워크플로우를 따라야 함
