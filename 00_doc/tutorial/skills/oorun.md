# oorun 튜토리얼

**생성일**: 2026-04-14 | **버전**: v02 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 자동 실행 (모든 작업)
oorun all

# 특정 작업만 실행
oorun task --id task_001

# 일시 중지된 작업 재개
oorun resume --from task_005

# 진행 상황 확인
oorun status

# 드라이 런 (실제 실행 없이 계획만)
oorun plan --dry-run
```

---

## 2. 권장 사용 흐름

**TDD 기반 자동 실행 사이클**:

1. **RED 단계**: 테스트 작성 및 실패 확인
   ```bash
   oorun test --watch
   ```

2. **GREEN 단계**: 최소한의 구현
   ```bash
   oorun implement --mode minimal
   ```

3. **REFACTOR 단계**: 코드 개선
   ```bash
   oorun refactor --lint --format
   ```

4. **VERIFY 단계**: 전체 검증
   ```bash
   oorun verify --full
   ```

---

## 3. 실전 시나리오

### 시나리오 1: 풀 자동 개발 사이클

```bash
# 요구사항 정의
cat > requirements.md << 'DOC'
# 새 기능: 사용자 인증 시스템

## 요구사항
- 사용자 등록/로그인
- JWT 토큰 발급
- 권한 검증

## 성공 기준
- 단위 테스트 95% 커버
- 통합 테스트 통과
- 성능: <500ms 응답 시간
DOC

# 자동 실행 시작
oorun all --requirement requirements.md --auto-commit

# 진행 상황 모니터링
oorun status --watch --interval 5s
```

**실행 순서**:
1. 테스트 자동 생성 (RED)
2. 구현 자동 생성 (GREEN)
3. 코드 정리 (REFACTOR)
4. 커밋 자동 (VERIFY)

---

### 시나리오 2: 일시 중지 후 재개

```bash
# 작업 시작 (작업 3에서 중단될 예정)
oorun all --max-tasks 3 --pause-after

# 사용자 개입 (수동 검토 등)
# ... 사용자가 작업 검토 ...

# 중단된 작업부터 재개
oorun resume --from-pause

# 특정 작업부터 재개
oorun resume --from task_004
```

---

### 시나리오 3: 드라이 런 및 계획 검토

```bash
# 계획 검토 (실제 실행 없음)
oorun plan --dry-run --verbose

# 출력 예시:
# PLAN: oorun all
# ├─ TASK-001: Generate tests (RED phase)
# ├─ TASK-002: Implement feature (GREEN phase)
# ├─ TASK-003: Refactor code (REFACTOR phase)
# └─ TASK-004: Verify & commit (VERIFY phase)

# 계획 확인 후 실제 실행
oorun all --confirm
```

---

## 4. Sub-Agent 역할

| Agent | 역할 | 사용 케이스 |
|-------|------|-----------|
| **ood (oodev)** | TDD 기반 개발 | RED→GREEN→REFACTOR |
| **ootest** | 테스트 생성/실행 | 단위/통합 테스트 |
| **oofix** | 오류 수정 | 테스트 실패 시 자동 수정 |
| **oocommit** | 커밋 및 이력 | 변경사항 자동 기록 |

---

## 5. 관련 스킬

```
oorun (자동 실행)
  ├─ oodev (TDD 개발)
  ├─ ootest (통합 테스트)
  ├─ oocheck (오류 검사)
  ├─ oofix (오류 수정)
  └─ oocommit (커밋)
```

**연계 스킬**:
- `oodev`: TDD 기반 개발 구현
- `ootest`: 테스트 작성 및 실행
- `oocommit`: 자동 커밋 및 이력 관리

---

## 6. 주요 기능

### 작업 추적

| 상태 | 의미 | 동작 |
|------|------|------|
| `PENDING` | 대기 중 | 실행 대기 |
| `RUNNING` | 실행 중 | 모니터링 |
| `PAUSED` | 일시 중지 | `oorun resume` 대기 |
| `COMPLETED` | 완료 | 다음 작업 진행 |
| `FAILED` | 실패 | 오류 수정 후 재시도 |

### TDD 자동 실행

```yaml
RED:
  - 테스트 요구사항 해석
  - 테스트 코드 자동 생성
  - 테스트 실행 (FAIL)

GREEN:
  - 최소 구현 코드 생성
  - 테스트 실행 (PASS)

REFACTOR:
  - 코드 정리 및 최적화
  - 린트 적용
  - 포맷 통일

VERIFY:
  - 전체 테스트 재실행
  - 성능 검사
  - 자동 커밋
```

---

## 7. 설정 및 커스터마이징

**config.yaml**:
```yaml
oorun:
  tdd_mode: true
  auto_commit: true
  max_retries: 3
  timeout_minutes: 30
  phases:
    - red
    - green
    - refactor
    - verify
```

---

## 8. 오류 처리

| 오류 | 원인 | 해결 |
|------|------|------|
| `Test generation failed` | 요구사항 불명확 | 요구사항 상세화 |
| `Implementation error` | 복잡한 로직 | 단순화 또는 수동 개입 |
| `Timeout` | 작업 시간 초과 | 타임아웃 증가 또는 작업 분할 |

---

## 9. 성능 최적화

```bash
# 병렬 처리 (독립적 작업 동시 실행)
oorun all --parallel 4

# 캐시 활용 (이전 결과 재사용)
oorun all --cache

# 리소스 제한
oorun all --max-memory 2GB --max-cpu 75%
```

---

## 10. 고급 활용

### 커스텀 워크플로우

```bash
# 사용자 정의 단계 추가
oorun all --custom-phases \
  --phase "analyze:검증" \
  --phase "document:문서화" \
  --phase "deploy:배포"
```

### 조건부 실행

```bash
# 특정 조건에서만 실행
oorun all --if "branch==main" \
         --if "all_tests_pass==true"
```

---

## 11. 트러블슈팅 및 FAQ

### Q: 작업이 자꾸 실패합니다. 어떻게 하나요?
**A**: 드라이 런으로 계획 검토 후 단계적 실행:
```bash
oorun plan --dry-run
oorun all --step-by-step  # 각 단계마다 일시 중지
```

### Q: 특정 단계만 건너뛰려면?
**A**: 
```bash
oorun all --skip-phases refactor,verify
```

### Q: 자동 커밋을 비활성화하려면?
**A**:
```bash
oorun all --no-auto-commit
```

---

**문서 버전**: v02 (2026-04-14 기준)
**관련 에이전트**: oodev, ootest, oofix, oocommit
**다음 단계**: `oorun plan --dry-run` 으로 실행 계획 검토
