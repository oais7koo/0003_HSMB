# ggcopy 스킬 (Copilot용 oo스킬 동기화/변환)

---

## ※ 참고: 본 스킬의 상세 사용법, 예외 처리, 한계 등은 동일 기능 oo스킬의 guide.md(예: .claude/skills/oo\*/guide.md) 파일을 반드시 참조하세요.

## 목적

- .claude/skills/ 내 oo* 스킬을 Copilot 환경(.github/skills/)에 gg* 스킬로 동기화/변환
- oo\* 스킬의 SKILL.md, scripts/, references/ 등 모든 파일을 Copilot에서 최대한 활용 가능하도록 변환/복사
- 기존 gg* 스킬이 있으면 oo* 스킬 변경분을 반영(동기화)
- Copilot에서 직접 사용할 수 없는 파일/코드는 변환 또는 요약/가이드 형태로 gg\* 폴더에 생성

## 사용법

- `ggcopy <oo스킬명>` : 해당 oo스킬(.claude/skills/oo*)을 Copilot용 gg스킬(.github/skills/gg*)로 동기화/변환
- `ggcopy all` : 모든 oo* 스킬을 gg* 스킬로 일괄 동기화/변환

## 동작 방식

1. .claude/skills/oo\* 폴더의 SKILL.md, scripts/, references/ 등 전체 파일 구조를 분석
2. Copilot에서 직접 사용 가능한 파일은 그대로 gg\* 폴더로 복사
3. Copilot에서 사용할 수 없는 코드/스크립트/설정 등은 요약, 가이드, 또는 변환본을 gg\* 폴더에 생성
4. 기존 gg* 스킬이 있으면 oo* 스킬 변경분을 반영(동기화)
5. references/guide.md 등 레퍼런스 파일도 최대한 동일하게 제공(불가시 요약본 생성)
6. .claude/skills/ 폴더에 gg* 스킬이 있으면 .github/skills/로 복사(이동)하며, .github/skills/에 이미 gg* 스킬이 있으면 내용을 병합(최신/중요 내용 유지)
7. 병합 후 .claude/skills/의 gg\* 스킬을 삭제할지 사용자에게 확인(yes/no)
8. 사용자가 동의하면 .claude/skills/의 gg\* 스킬 폴더 삭제

## 제한사항

- Copilot 환경 제약(외부 명령, 시스템 접근 등)은 자동 감지하여 변환/요약 처리
- 완전 자동화가 불가한 경우, 수동 가이드/설명 파일로 대체

## 예시

- `ggcopy ootest` → .claude/skills/ootest/ → .github/skills/ggtest/로 동기화/변환
- `ggcopy all` → 모든 oo* 스킬을 gg* 스킬로 일괄 동기화

## 참고

- oo* 스킬의 guide.md, checklist.md, agents.md 등도 Copilot에서 최대한 활용 가능하도록 gg* 폴더에 포함
- Copilot에서 직접 실행 불가한 부분은 명확히 안내/요약
