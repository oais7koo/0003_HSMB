# ooskill 튜토리얼

**생성일**: 2026-04-14 | **버전**: v03 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 스킬 검증
ooskill validate --skill oodev

# 모든 스킬 상태 확인
ooskill status --all

# 스킬 최적화
ooskill optimize --skill ooreport

# 스킬 문서 생성
ooskill docs --skill oohistory --output tutorial.md
```

---

## 2. 권장 사용 흐름

**3단계 스킬 관리 워크플로우**:

1. **검증**: 스킬 기능 검증
2. **최적화**: 성능 개선
3. **문서화**: 튜토리얼 생성

---

## 3. 실전 시나리오

### 시나리오 1: 스킬 상태 확인

```bash
# 특정 스킬 검증
ooskill validate --skill oodev

# 결과:
# SKILL: oodev
# ├─ Status: ✅ HEALTHY
# ├─ Version: v02
# ├─ Dependencies: 3/3 satisfied
# ├─ Performance: 95% (within budget)
# └─ Last used: 2026-04-14 15:23:10
```

---

### 시나리오 2: 모든 스킬 대시보드

```bash
ooskill status --all --format dashboard

# 결과:
# ┌─────────────────┬─────────┬────────┬──────────┐
# │ Skill           │ Status  │ Version│ Last Use │
# ├─────────────────┼─────────┼────────┼──────────┤
# │ oodev           │ ✅      │ v02    │ 2h ago   │
# │ ootest          │ ✅      │ v03    │ 4h ago   │
# │ ooreport        │ ⚠️      │ v12    │ 1d ago   │
# │ oosync          │ ✅      │ v13    │ 30m ago  │
# └─────────────────┴─────────┴────────┴──────────┘
```

---

## 4. Sub-Agent 역할

| Agent | 역할 |
|-------|------|
| **task-checker** | 스킬 검증 |
| **performance** | 성능 분석 |

---

## 5. 관련 스킬

```
ooskill (스킬 관리)
  ├─ ooflow (워크플로우)
  └─ ooenv (환경 상태)
```

---

## 6. 주요 기능

- 스킬 검증 및 상태 확인
- 성능 모니터링
- 의존성 관리
- 자동 최적화

---

## 7. 설정

**config.yaml**:
```yaml
ooskill:
  validate_on_startup: true
  performance_threshold: 90%
  auto_optimize: true
```

---

## 8. 오류 처리

| 오류 | 해결 |
|------|------|
| 의존성 누락 | `ooskill install-deps --skill [name]` |
| 성능 저하 | `ooskill optimize --skill [name]` |

---

## 9. 성능 최적화

```bash
ooskill optimize --skill oodev --aggressive
```

---

## 10. 고급 활용

```bash
# 스킬 벤치마크
ooskill benchmark --skill oodev --iterations 100

# 버전 비교
ooskill compare-versions --skill oodev --versions v01,v02,v03
```

---

## 11. FAQ

### Q: 스킬이 정상인지 어떻게 확인하나요?
**A**: `ooskill validate --skill [name]` 실행

---

**문서 버전**: v03 (2026-04-14 기준)
**다음 단계**: `ooskill status --all` 로 모든 스킬 확인
