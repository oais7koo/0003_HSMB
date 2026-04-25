# oosidi 튜토리얼

**생성일**: 2026-04-14 | **버전**: v01 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# Obsidian 볼트 동기화
oosidi sync --vault /path/to/vault

# 문서 자동 생성
oosidi generate --template project --output vault/projects/new_project

# 백링크 맵 생성
oosidi map --vault /path/to/vault --output graph.json

# Markdown 검증
oosidi validate --vault /path/to/vault
```

---

## 2. 권장 사용 흐름

**4단계 Obsidian 관리 워크플로우**:

1. **연결**: 로컬 볼트 연결
2. **생성**: 템플릿 기반 문서 생성
3. **링킹**: 자동 백링크 관리
4. **동기화**: 변경사항 추적

---

## 3. 실전 시나리오

### 시나리오 1: 프로젝트 문서 자동 생성

```bash
oosidi generate --template project \
  --name "CCone Platform" \
  --vault ~/obsidian/vault \
  --structure hierarchical

# 생성 결과:
# projects/CCone Platform/
#   ├─ README.md
#   ├─ Architecture.md
#   ├─ API.md
#   └─ Changelog.md
```

---

### 시나리오 2: 문서 간 백링크 자동화

```bash
oosidi link --vault ~/obsidian/vault \
  --auto-link \
  --patterns "[[%s]]"

# 결과: 자동 참조 링크 생성
```

---

## 4. Sub-Agent 역할

| Agent | 역할 |
|-------|------|
| **scribe** | 문서 작성 |
| **architect** | 구조 설계 |

---

## 5. 관련 스킬

```
oosidi (Obsidian 관리)
  ├─ oodoc (문서화)
  └─ oosync (동기화)
```

---

## 6. 주요 기능

- 볼트 구조 자동 생성
- 템플릿 기반 문서 생성
- 백링크 자동 관리
- Markdown 검증

---

## 7. 설정

**config.yaml**:
```yaml
oosidi:
  vault_path: ~/obsidian/vault
  auto_link: true
  validate_on_sync: true
```

---

## 8. 오류 처리

| 오류 | 해결 |
|------|------|
| 볼트 경로 오류 | 절대 경로 확인 |
| 링크 손상 | `oosidi repair` 실행 |

---

## 9. 성능 최적화

```bash
# 캐시 활용
oosidi sync --cache --vault ~/obsidian/vault
```

---

## 10. 고급 활용

```bash
# 커스텀 템플릿
oosidi generate --custom-template template.md
```

---

## 11. FAQ

### Q: 여러 볼트를 관리하려면?
**A**:
```bash
oosidi multi-vault --vaults vault1,vault2,vault3 --sync
```

---

**문서 버전**: v01 (2026-04-14 기준)
**다음 단계**: `oosidi sync --vault [경로]` 로 동기화 시작
