# ggtodo_copilot 스킬 (Copilot용 자동 todo 처리)

---

## ※ 참고: 본 스킬의 상세 사용법, 예외 처리, 한계 등은 동일 기능 oo스킬의 guide.md(예: .claude/skills/ootodo/guide.md) 파일을 반드시 참조하세요.

## 목적

- 00_doc/spXX/d{문서번호}\_todo.md 내 대기중 todo를 자동 처리하고, 완료 todo로 이동하며 상세 설명을 추가

## 사용법

- `python run.py <문서번호>`
  - 예: `python run.py 10004`

## 동작 방식

1. 해당 문서의 대기중 todo(- [ ]) 항목을 순차적으로 처리
2. 각 todo를 실제로 처리(자동화 불가 시 설명만 추가)
3. 처리 결과를 각 todo 아래에 상세 설명으로 추가
4. 완료된 todo는 "완료 todo" 섹션(또는 - [x] 항목)으로 이동

## 제한사항

- 실제 자동화 처리가 불가능한 경우, 상세 설명만 추가
- 문서 포맷이 다를 경우 정상 동작하지 않을 수 있음

## 예시

- `python run.py 10004` → 00_doc/sp01/d10004_todo.md 내 대기중 todo를 모두 처리
