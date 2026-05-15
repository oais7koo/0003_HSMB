# 플러그인: codex

> Claude×Codex 코드 리뷰·버그 수정 위임 | 선택

## 개요

OpenAI가 Claude Code용으로 공식 공개한 플러그인. Claude Code에서 작업하면서 Codex를 코드 리뷰어 또는 버그 수정 서브에이전트로 활용할 수 있다.

| 항목 | 내용 |
|------|------|
| 플러그인 ID | `codex` |
| 저장소 | `openai/codex-plugin-cc` |
| 설치 여부 | ✅ 설치됨 |
| 필수 여부 | - 선택 |
| 인증 | ChatGPT 무료 계정 또는 OpenAI API 키 |
| 비용 | Claude Code + Codex 사용량 별도 차감 |

## 설치

```
# 1. Codex CLI 전역 설치 (bash)
npm install -g @openai/codex

# 2. 마켓플레이스 등록 (Claude Code 프롬프트)
/plugin marketplace add openai/codex-plugin-cc

# 3. 플러그인 설치
/plugin install codex@openai-codex

# 4. 플러그인 활성화 (필수, 누락 시 명령어 안 보임)
/plugin
#  → Installed 메뉴 진입
#  → 'codex' 항목이 [disabled] 상태로 표시됨
#  → Enter 또는 Space로 토글 → [✓] enabled 변경
#  → "✓ Enabled codex. Run /reload-plugins to apply." 메시지 확인

# 5. 리로드
/reload-plugins

# 6. 셋업 확인
/codex:setup

# 7. 로그인
! codex login
```

> **중요**: `/plugin install` 만으로는 플러그인이 활성화되지 않는다. 설치된 플러그인은 기본 **disabled** 상태로 등록되므로 반드시 4단계 활성화 토글을 거쳐야 `/codex:*` 명령어가 자동완성에 노출된다.

로그인 대안:
```bash
codex login --device-auth    # 브라우저 불가 시
codex login --with-api-key   # API 키 방식
```

## 주요 명령어

| 명령어 | 모드 | 설명 |
|--------|------|------|
| `/codex:review` | read-only | 미커밋 변경 또는 브랜치 비교 리뷰 |
| `/codex:adversarial-review` | read-only | 보안·설계 공격적 리뷰 (7개 공격 면) |
| `/codex:rescue` | write | 버그 조사·수정·후속 작업 Codex 위임 |
| `/codex:status` | - | 백그라운드 작업 상태 확인 |
| `/codex:result` | - | 완료된 작업 결과 조회 |
| `/codex:cancel` | - | 작업 취소 |
| `/codex:setup` | - | CLI 상태 확인 및 Review Gate 설정 |

## 사용 예시

```bash
# 1. 변경사항 일반 리뷰 (작은 변경)
/codex:review --wait

# 2. 변경사항 일반 리뷰 (큰 변경 - 백그라운드)
/codex:review --background
/codex:status          # 진행 상황 확인
/codex:result          # 완료 후 결과 조회

# 3. 보안/아키텍처 민감 코드 리뷰
/codex:adversarial-review

# 4. 버그 수정 위임
/codex:rescue

# 5. 모델·품질 옵션 지정
/codex:rescue --model spark --effort high
```

## adversarial-review 7개 공격 면

| 항목 | 내용 |
|------|------|
| 인증/권한 | 접근 제어 결함 |
| 데이터 손실 | 데이터 유실 가능성 |
| 롤백 안전성 | 배포 롤백 가능 여부 |
| 레이스 컨디션 | 동시성 문제 |
| 빈 상태 | 엣지케이스 (빈 배열, null 등) |
| 버전 스큐 | 구버전 클라이언트 호환성 |
| 관찰성 갭 | 로깅·모니터링 누락 |

## Review Gate

Claude가 멈출 때마다 Codex 리뷰를 자동 실행하는 기능.

```
/codex:setup --enable-review-gate    # 활성화
/codex:setup --disable-review-gate   # 비활성화 (기본값 권장)
```

> 무료 계정 사용 한도 소모 주의. 기본 비활성화 권장.

## oo 스킬 연계

| 단계 | oo 스킬 | Codex 플러그인 |
|------|---------|--------------|
| 코드 작성 | `oodev run` | - |
| 에러 체크 | `oocheck run` | - |
| 일반 리뷰 | - | `/codex:review` |
| 보안 리뷰 | - | `/codex:adversarial-review` |
| 버그 수정 위임 | - | `/codex:rescue` |
| 커밋 | `oocommit run` | - |

## 트러블슈팅

### `/codex:*` 명령어가 자동완성에 안 보임

**원인**: 설치 후 플러그인이 **disabled 상태**로 등록되어 있음.

**확인**:
```bash
# enabledPlugins 확인 (비어있으면 비활성)
python -c "import json; d=json.load(open(r'C:/Users/USERNAME/.claude.json',encoding='utf-8')); p=d.get('projects',{}).get('현재프로젝트경로',{}); print(p.get('enabledPlugins',{}))"
```

**해결**:
1. `/plugin` 진입 → Installed 메뉴
2. `codex` 항목 찾기 (disabled로 표시됨)
3. Enter/Space로 활성화 토글
4. `/reload-plugins` 실행
5. `/codex:setup` 자동완성 확인

### 로드 시 에러 (`2 errors during load`)

`/reload-plugins` 출력의 에러는 codex와 무관한 다른 플러그인 이슈일 수 있다. `/doctor` 명령으로 세부 내용 확인.

### 인증 실패

`/codex:setup` 결과의 `auth.loggedIn`이 `false`라면:
```bash
! codex login                # 브라우저 인증
! codex login --device-auth  # 브라우저 불가 시
! codex login --with-api-key # API 키 방식
```

---

## 주의사항

- Claude Code 사용량과 Codex 사용량 **별도** 청구
- 저장소 초기 단계 — 프로덕션 의존 주의
- `code-review` 플러그인과 달리 **write 모드**(`/codex:rescue`) 지원
- OMC `code-reviewer` 에이전트(opus)는 더 포괄적, 이 플러그인은 OpenAI 모델 관점의 크로스벤더 리뷰

---

> 생성일: 2026-04-08 | 참조: `01_obsidian/5800_AI솔루션/5811_claude/11_claudecode/claudecode-plugin.codex.md`
