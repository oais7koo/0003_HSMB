# oostart 튜토리얼

**생성일**: 2026-04-14 | **버전**: v03 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 세션 시작
oostart run

# 환경 확인
oostart check --env

# 모델 캐시 초기화
oostart cache --clear

# 모드 선택
oostart run --mode autopilot
```

---

## 2. 권장 사용 흐름

**4단계 세션 초기화 워크플로우**:

1. **환경 검사**: OS, 경로, 도구 확인
2. **캐시 관리**: 모델 캐시 업데이트
3. **컨텍스트 로드**: 프로젝트 설정 읽기
4. **모드 활성화**: 작업 모드 선택

---

## 3. 실전 시나리오

### 시나리오 1: 풀 세션 시작

```bash
oostart run

# 실행 결과:
# ✅ Environment Check
#   ├─ OS: Windows 11
#   ├─ Python: 3.11.0
#   ├─ Git: 2.42.0
#   └─ Claude: v4.5.1
#
# ✅ Cache Management
#   ├─ Model: haiku-4.5 (cached)
#   ├─ Libraries: 42 modules loaded
#   └─ Memory: 2.1GB available
#
# ✅ Context Loaded
#   ├─ Project: CCone Platform
#   ├─ Branch: main
#   └─ Documents: d0001_prd.md, d0004_todo.md loaded
#
# ✅ Session Ready
#   Mode: autopilot
#   Timestamp: 2026-04-14T09:15:30
```

---

### 시나리오 2: 환경 상태 확인

```bash
oostart check --env --verbose

# 결과:
# Checking environment...
# 
# PATH Variables:
#   HOME: C:\Users\oaiskoo
#   TEMP: C:\Users\oaiskoo\AppData\Local\Temp
#   PYTHONPATH: ...
# 
# Tools:
#   ✅ Git: 2.42.0
#   ✅ Python: 3.11.0
#   ✅ Claude: 4.5.1
#   ⚠️ NODE: Not installed
```

---

## 4. Sub-Agent 역할

| Agent | 역할 |
|-------|------|
| **ooenv** | 환경 검사 |
| **ootoken** | 토큰 모니터링 |

---

## 5. 관련 스킬

```
oostart (세션 시작)
  ├─ ooenv (환경 상태)
  ├─ ootoken (토큰 모니터링)
  └─ oostop (세션 종료)
```

---

## 6. 주요 기능

- 자동 환경 검사
- 모델 캐시 관리
- 프로젝트 컨텍스트 로드
- 모드 자동 선택

---

## 7. 설정

**config.yaml**:
```yaml
oostart:
  auto_check_env: true
  cache_models: true
  load_context: true
  default_mode: autopilot
```

---

## 8. 오류 처리

| 오류 | 해결 |
|------|------|
| 경로 오류 | `oostart check --paths` |
| 캐시 손상 | `oostart cache --clear --rebuild` |
| 컨텍스트 로드 실패 | `oostart load --force` |

---

## 9. 성능 최적화

```bash
# 빠른 시작 (환경 검사 생략)
oostart run --quick

# 캐시 재구축
oostart cache --rebuild --async
```

---

## 10. 고급 활용

```bash
# 특정 프로젝트로 시작
oostart run --project /path/to/project

# 특정 모드로 시작
oostart run --mode ultrawork --depth hard
```

---

## 11. FAQ

### Q: 캐시를 초기화하려면?
**A**: `oostart cache --clear --rebuild`

### Q: 특정 환경 변수를 설정하려면?
**A**:
```bash
oostart env --set KEY=value
```

---

**문서 버전**: v03 (2026-04-14 기준)
**다음 단계**: `oostart run` 으로 세션 시작
