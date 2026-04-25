# oostop 튜토리얼

**생성일**: 2026-04-14 | **버전**: v01 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 세션 정상 종료
oostop run

# 상태 저장 후 종료
oostop save --state

# Git 커밋 및 종료
oostop commit --message "End of session"

# 강제 종료
oostop force
```

---

## 2. 권장 사용 흐름

**3단계 세션 종료 워크플로우**:

1. **상태 저장**: 진행 상황 기록
2. **Git 커밋**: 변경사항 커밋
3. **세션 종료**: 리소스 정리

---

## 3. 실전 시나리오

### 시나리오 1: 정상 세션 종료

```bash
oostop run

# 실행 결과:
# ✅ Saving State
#   ├─ Tasks: 5 completed, 2 pending
#   ├─ Changes: 12 files modified
#   └─ State saved: .omc/state/session.json
#
# ✅ Git Operations
#   ├─ Branch: main
#   ├─ Staged: 12 files
#   └─ Commit: "chore: end of session"
#
# ✅ Cleanup
#   ├─ Temp files: deleted
#   ├─ Cache: optimized
#   └─ Memory: freed
#
# Session ended successfully (Duration: 2h 15m)
```

---

### 시나리오 2: 커밋 메시지 커스텀

```bash
oostop commit --message "feat: complete feature X + docs update" \
  --scope sp04 \
  --tags "important,tested"
```

---

## 4. Sub-Agent 역할

| Agent | 역할 |
|-------|------|
| **oocommit** | Git 커밋 |
| **oohistory** | 이력 기록 |

---

## 5. 관련 스킬

```
oostop (세션 종료)
  ├─ oocommit (커밋)
  ├─ oohistory (이력)
  └─ oostart (다음 시작)
```

---

## 6. 주요 기능

- 상태 자동 저장
- Git 자동 커밋
- 리소스 정리
- 이력 기록

---

## 7. 설정

**config.yaml**:
```yaml
oostop:
  auto_save_state: true
  auto_commit: true
  cleanup_temp: true
```

---

## 8. 오류 처리

| 오류 | 해결 |
|------|------|
| 커밋 실패 | `oostop commit --force` |
| 상태 저장 실패 | 수동 백업 |

---

## 9. 성능 최적화

```bash
# 빠른 종료 (커밋 생략)
oostop run --quick
```

---

## 10. 고급 활용

```bash
# 상태 보관 (재개용)
oostop save --checkpoint --name "session-20260414"

# 부분 커밋
oostop commit --only "src/,docs/" --message "..."
```

---

## 11. FAQ

### Q: 강제로 세션을 종료하려면?
**A**: `oostop force --no-commit`

---

**문서 버전**: v01 (2026-04-14 기준)
**다음 단계**: `oostop run` 으로 세션 종료
