# ggscrap 스킬 (Copilot용 간이 스크래핑)

---

## ※ 참고: 본 스킬의 상세 사용법, 예외 처리, 한계 등은 동일 기능 oo스킬의 guide.md(예: .claude/skills/ooscrap/guide.md) 파일을 반드시 참조하세요.

## 목적

- Copilot 환경에서 웹/유튜브 URL의 텍스트(자막/기사)만 추출하여 마크다운 파일로 저장
- 복잡한 자동화, 다운로드, STT, 이력 관리는 미지원

## 사용법

- `ggscrap <url>` : 웹 기사/유튜브 URL 입력 시 텍스트(자막/본문) 추출 후 마크다운 저장

## 제한사항

- yt-dlp, whisper 등 외부 CLI/파이썬 패키지 직접 실행 불가
- Agent 위임, 대용량 다운로드, 이력 관리, 배치 처리 등 미지원
- 유튜브 자막은 공개 자막만 추출(Whisper 등 STT 불가)
- 웹 기사도 단순 텍스트 추출만 지원(로그인/동적 페이지 등 미지원)

## 예시

- `ggscrap https://www.youtube.com/watch?v=xxxx` → 자막 텍스트를 ggscrap_output.md로 저장
- `ggscrap https://news.example.com/article` → 기사 본문을 ggscrap_output.md로 저장

## 참고

- 고급 자동화, 이력 관리, Whisper STT 등은 oo스킬(ooscrap)에서만 지원
