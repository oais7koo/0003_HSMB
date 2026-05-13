# ggplan 가이드 (Copilot)

ooplan/references/guide.md 기반, Copilot 환경에 맞게 수동 워크플로우 안내로 변환

---

## 1. 개요

- **ggplan**: PRD 기반 구현 계획/상세 설계 워크플로우 안내 (자동 실행 불가)
- Copilot에서는 자동 계획/설계/동기화/리포트 생성 불가, 수동 명령어/절차 안내만 제공

---

## 2. 기본 사용법

1. 구현 계획/상세 설계 대상 문서 선정
2. 아래 명령어를 터미널에서 직접 실행
   - 전체 계획: `ooplan run`
   - Epic/Feature/Task 단위: `ooplan run epic`, `ooplan run feature`, `ooplan run task`
   - 상세 설계: `ooplan detail`
   - 동기화/최적화: `ooplan sync`, `ooplan check --fix`
3. Copilot에서 계획/설계 결과 문서를 열어 확인
4. 추가 편집/수정은 직접 수행

---

## 3. 워크플로우

- [1] PRD 준비 → [2] 계획/설계 명령 실행 → [3] 결과 확인 및 추가 편집
- 각 단계별 명령어는 위 참조

---

## 4. 입출력 형식

| 항목 | 내용                                |
| ---- | ----------------------------------- |
| 입력 | 명령어 인자(문서명 등)              |
| 출력 | 터미널 출력, 계획/설계 문서 등      |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록 |

---

## 5. 주의사항

- Copilot에서는 자동 실행/계획/설계/동기화 불가 (수동 명령어 실행 필요)
- ooplan SKILL.md/guide.md를 참고하여 워크플로우를 따라야 함
