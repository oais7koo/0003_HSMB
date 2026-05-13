# ooreview 가이드

## 문서 이력 관리
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**ooreview**: 병렬 에이전트 기반 코드 리뷰.

- **참조**:  (서브명령어·워크플로우)
- **이 문서**: 방법론(How) — 실행 패턴, 입력/출력 형식, 사용 가이드

---

## 2. 기본 사용법

### Codex 활용 패턴

**방법 1 — tmux CLI (항상 사용 가능)**:
```
/omc-teams 1:codex "Review the following Python code for bugs, design issues, and improvement opportunities. Be specific with line numbers.

[코드 또는 파일 경로]"
```

**방법 2 — codex:rescue 에이전트 (플러그인 설치 시)**:
```
Task(subagent_type="codex:rescue",
     prompt="Second-opinion review: [파일경로] — focus on logic defects and missed edge cases")
```

**Codex 리뷰 프롬프트 템플릿**:
- 일반: `"Review [file] for bugs, design issues, and improvements. Give line-specific feedback."`
- 보안: `"Security audit [file]: injection, auth bypass, data exposure, input validation."`
- 성능: `"Performance review [file]: bottlenecks, inefficient patterns, memory issues."`

---

## 3. 워크플로우

### 표준 흐름 (ooreview run)

```
[Step 1] explore(haiku) — 대상 파일 탐색 및 변경 범위 파악
    ↓
[Step 2] 병렬 1차 리뷰 (Task run_in_background=true)
    ├─ code-reviewer(opus)      — 설계·패턴·API 계약·가독성·하위 호환성
    ├─ security-reviewer(sonnet) — OWASP Top10·인증·인가·민감정보 노출
    └─ quality-reviewer(sonnet)  — 성능·복잡도·유지보수성·중복
    ↓
[Step 3] Codex 2차 리뷰 (다른 AI 관점)
    → /omc-teams 1:codex "[리뷰 프롬프트]"   # 항상 사용 가능 (tmux)
    → codex:rescue 에이전트                   # 플러그인 설치 시 추가 활용
    ↓
[Step 4] 결과 합산 → 리뷰 리포트 출력
    ↓
[Step 5] 이슈 자동 등록 (확인 없이 즉시)
    → SP==00: d0004_todo.md
    → SP!=00: d{SP}0004_todo.md 만 (d0004에 중복 등록 안 함)
```

### ooreview run dXXXX 흐름

```
ooreview run d41001
    ↓
1. d41001_*.md 탐색 → 관련 코드 파일 추출
    ↓
2. 해당 파일 대상 3-way 병렬 리뷰 + Codex 2차 리뷰
    ↓
3. 결과 → d40004_todo.md 등록
```

---

## 4. 입출력 형식

### 이슈 등록 형식

```
| R001 | 2026-04-08 | [DESIGN] | [ooreview] src/api.py:45 — SRP 위반: 단일 함수가 파싱+저장+알림 수행 | high | 신규 |
```

### 리뷰 리포트 출력 형식

```
[ooreview] 리뷰 완료

대상: src/crawler.py, src/manager.py (2개 파일)
리뷰어: code-reviewer(opus) + security-reviewer + quality-reviewer + Codex

━━━ code-reviewer ━━━━━━━━━━━━━━━━━━━━━━━━━
R001 [ERROR][DESIGN] crawler.py:89 — 재시도 로직이 무한루프 가능
R002 [WARNING][COMPAT] manager.py:23 — deprecated requests.get() 파라미터 사용

━━━ security-reviewer ━━━━━━━━━━━━━━━━━━━━
R003 [CRITICAL][SECURITY] crawler.py:45 — User-Agent 헤더 미검증 → SSRF 가능

━━━ quality-reviewer ━━━━━━━━━━━━━━━━━━━━━
R004 [WARNING][QUALITY] manager.py:67~120 — 54줄 함수, 단일 책임 원칙 위반

━━━ Codex (2차 의견) ━━━━━━━━━━━━━━━━━━━━
R005 [ERROR][LOGIC] crawler.py:102 — timeout=None 시 영원히 블로킹

총 5건 (CRITICAL 1, ERROR 2, WARNING 2)
→ d40004_todo.md에 자동 등록 완료
```

---

## 5. 주의사항

- SP 컨텍스트 확인 후 실행 (SKILL.md 참조)
- 상세 서브명령어는 SKILL.md 참조
