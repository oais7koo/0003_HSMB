# oosync ftp 사용 가이드

## 문서 이력 관리
- v01 2026-03-27 — 초기 작성 — FTP 동기화 가이드

---

## 1. 개요

`oosync ftp`는 SP(서브프로젝트)별로 FTP 서버의 리모트 폴더와 로컬 폴더를 동기화하는 서브커맨드입니다.

기존에 `06_SSweb/deploy.py`, `07_KWweb/deploy.py`에 분산되어 있던 FTP 배포 로직을 통합하여, 설정 파일 기반으로 일관되게 관리합니다.

## 2. 사전 준비

### 2.1 .env 설정

```env
# .env (프로젝트 루트)
FTP_PASS=yoon!234
```

### 2.2 설정 파일

경로: `.claude/skills/oosync/references/ftp_config.json`

```json
{
  "default_password_env": "FTP_PASS",
  "profiles": {
    "SP06": {
      "name": "시니어세상",
      "host": "seniorworld.co.kr",
      "user": "yoon004",
      "port": 21,
      "remote_root": "/www",
      "local_dir": "06_SSweb",
      "targets": ["css", "index.html"],
      "encoding": "latin-1"
    },
    "SP07": {
      "name": "케이웍스",
      "host": "kworksk.co.kr",
      "user": "yoon008",
      "port": 21,
      "remote_root": "/www",
      "local_dir": "07_KWweb/03_upload",
      "targets": ["css", "images", "js", "index.html"],
      "encoding": "euc-kr"
    }
  }
}
```

## 3. 명령어 상세

### 3.1 접속 테스트

```bash
# 전체 프로필 테스트
uv run python .claude/skills/oosync/scripts/oosync_ftp.py status

# 특정 SP만
uv run python .claude/skills/oosync/scripts/oosync_ftp.py status SP07
```

### 3.2 리모트 파일 목록

```bash
uv run python .claude/skills/oosync/scripts/oosync_ftp.py list SP07
```

### 3.3 로컬 vs 리모트 비교

```bash
# 차이점 비교 (크기 기준)
uv run python .claude/skills/oosync/scripts/oosync_ftp.py diff SP07
```

출력 상태 코드:
| 상태 | 설명 |
|------|------|
| `==` | 동일 (크기 일치) |
| `!=` | 크기 다름 |
| `->` | 로컬에만 존재 |
| `<-` | 리모트에만 존재 |

### 3.4 업로드 (push)

```bash
# 미리보기
uv run python .claude/skills/oosync/scripts/oosync_ftp.py push SP07 --dry-run

# 실제 업로드 (기존 삭제 후 전체 업로드)
uv run python .claude/skills/oosync/scripts/oosync_ftp.py push SP07
```

**주의**: push는 targets에 해당하는 리모트 파일/폴더를 **삭제 후 재업로드**합니다.

### 3.5 다운로드 (pull)

```bash
# 미리보기
uv run python .claude/skills/oosync/scripts/oosync_ftp.py pull SP06 --dry-run

# 실제 다운로드
uv run python .claude/skills/oosync/scripts/oosync_ftp.py pull SP06
```

## 4. 프로필 추가

새 SP에 FTP 배포가 필요하면 `ftp_config.json`에 프로필을 추가합니다:

```json
"SP08": {
  "name": "새 프로젝트",
  "host": "example.com",
  "user": "ftpuser",
  "port": 21,
  "remote_root": "/public_html",
  "local_dir": "08_NewProject",
  "targets": ["css", "js", "index.html"],
  "encoding": "utf-8",
  "password_env": "FTP_PASS_SP08"
}
```

개별 비밀번호가 필요하면 `password_env`를 설정하고 `.env`에 해당 키를 추가합니다.

## 5. 기존 deploy.py와의 관계

| 항목 | 기존 (deploy.py) | oosync ftp |
|------|------------------|------------|
| 위치 | SP마다 개별 파일 | 중앙 스크립트 1개 |
| 설정 | 하드코딩 | config JSON + .env |
| 기능 | push만 | status/list/diff/push/pull |
| 비밀번호 | 소스에 노출 | .env로 분리 |

기존 `deploy.py`는 레거시로 유지하되, 향후 `oosync ftp push`로 대체 권장합니다.

## 6. 관련 문서

- SKILL.md: `.claude/skills/oosync/SKILL.md` (FTP 동기화 섹션)
- SP06 PRD: `00_doc/sp06/d60001_prd.md` (시니어세상 배포 정보)
- SP07 PRD: `00_doc/sp07/d70001_prd.md` (케이웍스 배포 정보)
