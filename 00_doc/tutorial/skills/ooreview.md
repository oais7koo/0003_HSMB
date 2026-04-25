# ooreview 스킬 튜토리얼

코드 리뷰를 병렬로 진행하고 Codex 2차 의견까지 받아 품질을 보증하는 스킬입니다.

## §1. 왜 필요한가?

코드 리뷰는 품질 보증의 핵심이지만, 수동 리뷰는 시간이 오래 걸리고 리뷰어의 관점이 제한됩니다.

**문제점**:
- 단일 리뷰어의 관점만 적용됨
- 여러 측면(성능, 보안, 가독성)을 모두 검토하기 어려움
- 리뷰 시간이 오래 걸림
- AI와 인간 리뷰의 조합이 없음

**해결책**: `ooreview`로 3개 에이전트가 병렬 리뷰 후 Codex가 최종 검증합니다.

## §2. 빠른 시작 (3가지 자주 쓰는 명령)

```bash
# 1. 단일 파일 리뷰
ooreview path/to/file.py

# 2. 여러 파일 병렬 리뷰
ooreview path/to/module/ --parallel

# 3. 특정 측면만 검토
ooreview path/to/file.py --focus security
```

## §3. 자주 쓰는 명령어

| 명령어 | 목적 | 사용 시점 |
|--------|------|----------|
| `ooreview <file>` | 파일 리뷰 | 코드 작성 후 |
| `ooreview <dir>` | 폴더 리뷰 | 기능 구현 완료 후 |
| `ooreview --parallel` | 병렬 리뷰 | 대량 파일 검토 |
| `ooreview --focus security` | 보안 중심 | 보안 관련 코드 |
| `ooreview --focus performance` | 성능 중심 | 성능 최적화 |
| `ooreview --codex` | Codex 2차 의견 | 최종 검증 필요 시 |
| `ooreview --fix` | 자동 수정 제안 | 간단한 오류 수정 |

## §4. 권장 워크플로우

**개발 후 리뷰 프로세스**:

```
코드 작성 완료
  ↓
ooreview --parallel (3개 에이전트 병렬 리뷰)
  ├─ 성능 리뷰
  ├─ 보안 리뷰
  └─ 가독성 리뷰
  ↓
리뷰 결과 수집
  ↓
ooreview --codex (Codex 2차 검증)
  ↓
피드백 적용 및 수정
  ↓
커밋 및 PR
```

## §5. 모든 명령어

- `ooreview <target>` — 기본 리뷰
- `ooreview --parallel` — 병렬 리뷰 (3개 에이전트)
- `ooreview --focus <domain>` — 특정 측면 중심
- `ooreview --codex` — Codex 2차 의견
- `ooreview --fix` — 수정안 제시
- `ooreview --json` — JSON 출력
- `ooreview --summary` — 요약 리포트
- `ooreview --detailed` — 상세 리포트

## §6. 상세 사용법

### 6.1 기본 리뷰 (`ooreview <file>`)

단일 파일의 전반적인 품질을 검토합니다:
- 코드 구조 및 가독성
- 에러 처리
- 테스트 커버리지
- 문서화 수준

### 6.2 병렬 리뷰 (`ooreview --parallel`)

3개 에이전트가 동시에 다른 측면을 검토합니다:
- **에이전트 1**: 성능 및 최적화
- **에이전트 2**: 보안 및 안정성
- **에이전트 3**: 가독성 및 유지보수성

### 6.3 포커스된 리뷰 (`ooreview --focus`)

특정 측면만 깊이 있게 검토합니다:
- `--focus security` — 보안 취약점 중심
- `--focus performance` — 성능 병목 중심
- `--focus quality` — 코드 품질 중심
- `--focus testing` — 테스트 커버리지 중심

### 6.4 Codex 2차 검증 (`ooreview --codex`)

Codex가 초기 리뷰 결과를 검증하고 추가 의견을 제시합니다:
- 초기 리뷰 결과 검증
- 추가 개선안 제시
- 최종 권장사항

### 6.5 자동 수정 (`ooreview --fix`)

간단한 오류는 자동으로 수정 제안을 생성합니다:
- 코드 스타일 정렬
- 미사용 import 제거
- 간단한 로직 개선

## §7. 실제 예시

**예시 1: 성능 리뷰**

```bash
$ ooreview app/api/handlers.py --focus performance

=== 성능 리뷰 결과 ===

[경고] O(n²) 알고리즘 발견
- 라인 45: for loop 내 추가 loop
- 권장: 해시맵 사용으로 O(n) 변경

[경고] 반복된 DB 쿼리
- 라인 78: 루프 내 SELECT 쿼리 반복
- 권장: Batch query로 변경

[최적화] 메모리 사용
- 현재: ~50MB
- 권장: 스트리밍 처리로 ~5MB 감소 가능
```

**예시 2: 보안 리뷰**

```bash
$ ooreview app/auth/login.py --focus security

=== 보안 리뷰 결과 ===

[중대] SQL Injection 가능성
- 라인 32: 사용자 입력을 쿼리에 직접 삽입
- 권장: Parameterized query 사용

[높음] 비밀번호 해싱 약함
- 라인 45: SHA1 사용 (레거시)
- 권장: bcrypt 또는 argon2 사용

[낮음] 에러 메시지 정보 유출
- 라인 58: 상세 DB 에러 메시지 노출
- 권장: 일반적인 메시지 반환
```

**예시 3: 병렬 리뷰**

```bash
$ ooreview src/ --parallel

=== 병렬 리뷰 진행 중 ===

✓ 성능 리뷰 완료 (3개 이슈)
✓ 보안 리뷰 완료 (1개 이슈)
✓ 가독성 리뷰 완료 (5개 개선안)

=== 종합 결과 ===
총 9개 피드백
우선순위: [중대:1, 높음:3, 중간:3, 낮음:2]

다음: ooreview --codex (Codex 2차 검증)
```

## §8. 입출력 정의

### 입력

**리뷰 대상**:
- 파일 경로 (예: `app/api/handlers.py`)
- 폴더 경로 (예: `src/`)
- 커밋 범위 (예: `HEAD~5..HEAD`)

**리뷰 옵션**:
- `--focus <domain>` — 검토 측면 지정
- `--parallel` — 병렬 리뷰
- `--codex` — Codex 2차 의견
- `--detailed` — 상세 리포트

### 출력

**리뷰 결과 객체**:
```json
{
  "file": "path/to/file.py",
  "reviewers": ["performance", "security", "quality"],
  "issues": [
    {
      "severity": "high",
      "category": "security",
      "line": 32,
      "message": "SQL Injection risk",
      "suggestion": "Use parameterized query"
    }
  ],
  "metrics": {
    "code_quality": 7.5,
    "security_score": 6.0,
    "performance_score": 8.2
  },
  "codex_opinion": "Approve with suggestions"
}
```

## §9. FAQ

**Q: Codex 2차 의견은 정말 도움이 되나요?**  
A: 예, Codex는 초기 리뷰에서 놓친 부분을 종종 지적합니다.

**Q: 병렬 리뷰가 정확한가요?**  
A: 3개 에이전트의 다양한 관점으로 더 정확합니다. 단일 리뷰보다 오류 감지율이 높습니다.

**Q: 자동 수정은 안전한가요?**  
A: 스타일/가독성 관련만 자동 적용 추천. 로직 변경은 검토 후 적용하세요.

**Q: 어떤 언어를 지원하나요?**  
A: Python, JavaScript/TypeScript, Java, Go, Rust 등 주요 언어 지원.

**Q: 리뷰 결과를 어떻게 저장하나요?**  
A: `--json` 또는 `--summary` 옵션으로 파일로 저장 가능.

## §10. 서브 에이전트

- **python-code-reviewer** — Python 코드 전문 리뷰
- **code-error-checker** — 에러 및 예외 처리 검토
- **streamlit-code-reviewer** — Streamlit 코드 검토
- **oo-python-algorithm-expert** — 알고리즘 효율성 검토

## §11. 관련 스킬

- `oocheck` — 자동 에러 체크
- `oofix` — 오류 자동 수정
- `ootest` — 테스트 작성 및 검증
- `oocommit` — 코드 리뷰 후 커밋
- `oof` — 기능 구현 워크플로우 (리뷰 포함)
