# ggtodo 스킬 (Copilot용 todo 관리)

---

## ※ 참고: 본 스킬의 상세 사용법, 예외 처리, 한계 등은 동일 기능 oo스킬의 guide.md(예: .claude/skills/ootodo/guide.md) 파일을 반드시 참조하세요.

## 목적

- Copilot 환경에서 간단한 todo 관리 기능 제공
- ootodo의 핵심 기능만 최소화하여 구현

## 사용법

- `python todo.py <sp번호> add <내용>`: 해당 SP의 todo 문서에 항목 추가
- `python todo.py <sp번호> list`: 해당 SP의 todo 목록 출력
- `python todo.py <sp번호> done <번호>`: 해당 SP의 todo 완료 처리

※ todo 항목은 00_doc/spXX/d{SP번호×10000+4}\_todo.md 파일에 직접 반영됩니다.

## 제한사항

- 복잡한 워크플로우, 외부 플러그인 미지원
- SP별 todo 문서(00_doc/spXX/d{SP번호×10000+4}\_todo.md)만 지원

## 예시

- `python todo.py 1 add "문서 작성"` → 00_doc/sp01/d10004_todo.md에 추가
- `python todo.py 8 list` → 00_doc/sp08/d80004_todo.md 목록 출력
- `python todo.py 1 done 2` → 00_doc/sp01/d10004_todo.md 2번 완료
