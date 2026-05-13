# oodesign 가이드

## 문서 이력 관리
- v02 2026-04-21 — SKILL.md 코드블록 이동: check/analyze 워크플로우, Pencil 체크 패턴, compbuild·init·pencil·vars 흐름도
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**oodesign**: SP07 디자인 시스템 구축·관리. 컴포넌트·토큰·가이드라인 관리.

- **참조**: SKILL.md (서브명령어·워크플로우)
- **이 문서**: 방법론(How) — 실행 패턴, 입력/출력 형식, 사용 가이드

---

## 2. 기본 사용법

서브명령어별 실행 방식:

- `token`, `check`: `uv run python .claude/skills/oodesign/scripts/` 경유
- 나머지(`analyze`, `theme`, `component`, `generate`, `compbuild`, `export`, `pencil`, `init`, `run`): Claude Code 직접 수행 (AI 분석/생성)

---

## 3. 워크플로우

### 3.1 check 워크플로우

```
oodesign check [--platform web|flutter|senior_world|all]
        │
        ▼
[1] audit_script.py 실행 (대상 플랫폼 폴더)
        │
        ▼
[2] section-title 넘버링 범위 표기 누락 검출
        │
        ▼
[3] elem-box 구조 무결성 검사 (elem-id / elem-preview / elem-code)
        │
        ▼
[4] 00_index.html ↔ 실제 파일 불일치 검출
    - 사이드바 링크 ↔ 카드 목록 불일치
    - 사이드바 ↔ 디스크 파일 불일치
        │
        ▼
[5] 이슈 목록 출력 (없으면 NO ISSUES FOUND)
```

### 3.2 analyze 워크플로우

```
oodesign analyze [이미지경로|--url URL] [--sample 샘플명]
        │
        ▼
[1] 소스 수집 (이미지 Read 또는 WebFetch)
        │
        ▼
[2] 색상/타이포/간격/레이아웃 추출
        │
        ▼
[3] 토큰 JSON 초안 생성
    - 02_tokens/{NN}_{샘플명}/ 에 저장
        │
        ▼
[4] token_sync.py --theme {샘플명} 실행
        │
        ▼
[5] 분석 결과 리포트 출력
```

### 3.3 compbuild 워크플로우

```
[1] 대상 파일 읽기  →  [2] elem-box 분리 + {AMOTP}-{3자리} 넘버링 (10단위 갭)
→  [3] M/O/T/P: elem-deps 라벨 추가  →  [4] elem-code 스니펫  →  [5] comp-count 업데이트
```

### 3.4 init 워크플로우

```
oodesign init [--root 경로]
→ 폴더 생성 (01_references ~ 06_work_pencil) → token_sync.py 실행 → 완료 리포트
```

### 3.5 pencil 워크플로우

```
oodesign pencil [--theme 테마명] [--file 경로]
→ MCP 상태 확인 → 문서 열기 → 토큰 JSON 읽기 → set_variables() 호출
```

테마 전환: `oodesign pencil --theme wello` 재실행 → `set_variables()` 덮어쓰기.

### 3.6 vars 연결 패턴

```
get_variables() → 02_tokens/{테마}/colors.json 읽기 → set_variables() → batch_design으로 하드코딩 색상 → $변수 교체
```

주의: `fontFamily`는 변수 참조 미지원 → 직접 문자열 사용.

---

## 4. Pencil MCP 사전 체크 패턴

Pencil 작업 시작 전 반드시 MCP 상태를 확인한다.

### 체크 절차

```
[1] get_editor_state 호출
        │
        ├─ 성공 + activeFile 존재 → 정상, 바로 작업 진행
        │
        ├─ 성공 + activeFile 없음 → open_document('new') 또는 기존 .pen 경로로 열기
        │
        └─ 오류 / MCP 응답 없음  → 사용자에게 알리고 중단
                                   (Pencil Dev 앱 실행 여부 확인 요청)
```

### 확인 항목

| 확인 항목 | 방법 | 정상 조건 |
|----------|------|----------|
| MCP 연결 | `get_editor_state()` 호출 | 오류 없이 응답 반환 |
| 활성 문서 | 응답의 `activeFile` 필드 | 경로가 존재하고 `.pen` 파일 |
| 가이드라인 로드 | `get_guidelines()` 호출 | 스타일/레이아웃 가이드 반환 |

### 코드 패턴

```python
# Pencil 작업 시작 전 항상 실행
state = mcp__pencil__get_editor_state()

if state.activeFile:
    # 정상 → 작업 진행
    guidelines = mcp__pencil__get_guidelines()
else:
    # 문서 없음 → 열기
    mcp__pencil__open_document('new')  # 또는 기존 경로
```

### 오류 대응

| 상황 | 원인 | 대응 |
|------|------|------|
| MCP 도구 자체가 없음 | Pencil Dev 앱 미실행 | 사용자에게 Pencil Dev 앱 실행 요청 |
| `activeFile` 없음 | 열린 문서 없음 | `open_document('new')` 또는 경로 지정 |
| 응답 지연/타임아웃 | 앱 응답 불가 | Pencil Dev 재시작 요청 |

---

## 5. 입출력 형식

| 항목 | 내용 |
|------|------|
| 입력 | 서브명령어 인자 또는 현재 SP 컨텍스트 |
| 출력 | 터미널 출력 또는 문서 파일 생성 |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록 |

---

## 6. 주의사항

- SP 컨텍스트 확인 후 실행 (SKILL.md 참조)
- 상세 서브명령어는 SKILL.md 참조
