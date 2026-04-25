# SuperClaude MCP Server Reference

> 이 파일은 SuperClaude MCP 서버 참조 가이드입니다.
> 상세 내용은 글로벌 설정 ~/.claude/MCP.md 참조

## MCP 서버 목록

| 서버 | 용도 | 활성화 플래그 |
|------|------|--------------|
| Context7 | 라이브러리 문서, 패턴 | --c7 |
| Sequential Thinking | 복잡한 분석, 다단계 추론 | --seq |
| Magic | UI 컴포넌트, 디자인 시스템 | --magic |
| Playwright | E2E 테스트, 브라우저 자동화 | --play |

## 자동 활성화 조건

- Context7: 외부 라이브러리 import 감지
- Sequential: 복잡한 디버깅, --think 플래그
- Magic: UI 컴포넌트 요청, 프론트엔드 작업
- Playwright: 테스트 워크플로우, QA 작업
