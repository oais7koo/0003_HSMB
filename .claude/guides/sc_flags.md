# SuperClaude Flags Reference

> 이 파일은 SuperClaude 플래그 참조 가이드입니다.
> 상세 내용은 글로벌 설정 ~/.claude/FLAGS.md 참조

## 주요 플래그

### 분석/계획
| 플래그 | 용도 |
|--------|------|
| --plan | 실행 계획 표시 |
| --think | 다중 파일 분석 (~4K) |
| --think-hard | 아키텍처 분석 (~10K) |
| --ultrathink | 시스템 재설계 분석 (~32K) |

### MCP 서버
| 플래그 | 용도 |
|--------|------|
| --c7 | Context7 활성화 |
| --seq | Sequential Thinking 활성화 |
| --magic | Magic UI 활성화 |
| --play | Playwright 활성화 |
| --all-mcp | 전체 MCP 활성화 |
| --no-mcp | MCP 비활성화 |

### 효율/범위
| 플래그 | 용도 |
|--------|------|
| --uc | 토큰 압축 모드 |
| --scope | 분석 범위 지정 |
| --focus | 도메인 집중 |
| --delegate | 서브에이전트 위임 |
| --loop | 반복 개선 모드 |
