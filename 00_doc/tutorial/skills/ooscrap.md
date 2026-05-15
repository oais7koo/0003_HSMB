# ooscrap Tutorial

> 유튜브 STT 및 웹 스크래핑 통합 스킬 | 버전: v02

## 개요

유튜브 영상과 웹 기사를 자동으로 수집하여 마크다운 텍스트로 변환하는 스킬입니다. 자막 우선 추출(STT 폴백) 및 웹 스크래핑으로 참고 자료를 체계적으로 관리합니다.

**핵심 역할**:
- 유튜브 자막 추출 (수동 → 자동 → Whisper STT)
- 채널 스캔 및 신규 영상 자동 추가
- 웹 기사 전문 스크래핑
- 이력 관리 및 중복 제거

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `ooscrap help` | 서브명령어 목록 |
| `ooscrap version` | 버전 정보 |
| `ooscrap status` | 상태 확인 |
| `ooscrap run [--url]` | **통합 처리** (URL 자동 감지 + 분류) |
| `ooscrap summary` | 유튜브 STT (기본 모드) |
| `ooscrap read` | 웹 기사 전문 스크래핑 |
| `ooscrap add <URL>` | URL 리스트에 추가 |
| `ooscrap sync` | 등록 채널 신규 영상 검색 |
| `ooscrap search "키워드"` | 서머리/읽을거리 검색 |
| `ooscrap list` | 다운로드 리스트 표시 |

---

## 사용 예시

### 1. 통합 배치 처리

```bash
oocontext 4          # SP04 전환
ooscrap run          # 전체 처리
```

**처리 흐름**:
1. `01_다운로드.md`의 `## 다운` 섹션 읽기
2. URL 패턴 자동 감지 (유튜브 동영상 / 채널 / 웹 기사)
3. 각 URL 처리 및 결과 저장
4. 이력 파일 자동 갱신
5. `01_다운로드.md` 정리

### 2. 채널 신규 영상 추가

```bash
ooscrap sync                    # 모든 등록 채널 스캔
ooscrap sync --channel <URL>    # 특정 채널만
```

---

## URL 자동 감지

| URL 패턴 | 처리 | 출력 |
|----------|------|------|
| `youtu.be/*` | STT (자막→Whisper) | `01_유튜브서머리/` |
| `youtube.com/@*` | 채널 스캔 → 영상 목록 | - |
| `youtube.com/shorts/*` | 스킵 (자동 삭제) | - |
| 그 외 URL | 웹 스크래핑 | `04_읽을거리/` |

---

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oopaper` | 논문 관리 (웹 스크래핑 보완) |
| `oomemo` | 임시 메모 (수집 후 정리) |
| `oowiki` | Wiki 지식 통합 (스크랩 콘텐츠 정리) |
