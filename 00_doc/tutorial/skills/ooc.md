# ooc 스킬 튜토리얼

서브프로젝트의 컨텍스트를 빠르게 로드하고 해당 프로젝트 정보를 얻는 스킬입니다. (oocontext 의 alias)

## §1. 왜 필요한가?

모노레포 구조의 CCone 프로젝트는 SP00~SP07까지 여러 서브프로젝트를 관리합니다. 각 서브프로젝트마다 다른 구조, 기술 스택, 문서를 가지고 있습니다.

**문제점**:
- 현재 작업 중인 서브프로젝트의 정보를 매번 찾아야 함
- 다른 서브프로젝트로 전환할 때 컨텍스트 재구성 필요
- 프로젝트 구조와 주요 파일들을 매번 확인해야 함
- 기술 스택과 핵심 모듈을 일일이 조사해야 함

**해결책**: `ooc` (또는 `oocontext`)로 서브프로젝트 정보를 즉시 로드합니다.

## §2. 빠른 시작 (3가지 자주 쓰는 명령)

```bash
# 1. 현재 서브프로젝트 정보 조회
ooc

# 2. 특정 서브프로젝트로 전환
ooc sp02

# 3. 서브프로젝트 전체 목록 보기
ooc list
```

## §3. 자주 쓰는 명령어

| 명령어 | 목적 | 사용 시점 |
|--------|------|----------|
| `ooc` | 현재 컨텍스트 확인 | 세션 시작 후 |
| `ooc <spid>` | 서브프로젝트 전환 | 다른 프로젝트 작업 시 |
| `ooc list` | 전체 프로젝트 목록 | 프로젝트 둘러보기 |
| `ooc info` | 상세 정보 | 아키텍처 파악 필요 시 |
| `ooc files` | 주요 파일 목록 | 파일 구조 확인 |
| `ooc stack` | 기술 스택 | 사용 기술 확인 |
| `ooc modules` | 모듈 목록 | 기능 모듈 조사 |

## §4. 권장 워크플로우

**멀티 서브프로젝트 개발 워크플로우**:

```
프로젝트 A 작업
  ↓
ooc list (다른 프로젝트 확인)
  ↓
ooc sp03 (프로젝트 B로 전환)
  ↓
ooc (현재 프로젝트 정보 확인)
  ↓
프로젝트 B 작업
  ↓
필요시 ooc sp01 (다시 전환)
```

## §5. 모든 명령어

- `ooc` — 현재 프로젝트 정보
- `ooc <spid>` — 특정 프로젝트로 전환
- `ooc list` — 전체 프로젝트 목록
- `ooc info` — 상세 정보
- `ooc files` — 주요 파일
- `ooc stack` — 기술 스택
- `ooc modules` — 모듈 목록
- `ooc readme` — README 내용
- `ooc structure` — 폴더 구조
- `ooc --json` — JSON 형식 출력

## §6. 상세 사용법

### 6.1 현재 프로젝트 확인 (`ooc`)

현재 작업 중인 서브프로젝트의 핵심 정보를 표시합니다:
- 프로젝트 ID (SP00, SP01 등)
- 기술 스택
- 주요 파일
- 상태 (활성/계획/보관)

### 6.2 프로젝트 전환 (`ooc <spid>`)

특정 서브프로젝트로 컨텍스트를 전환합니다:
- 프로젝트 경로 설정
- 관련 파일 로드
- 기술 정보 업데이트
- 상태 초기화

### 6.3 전체 목록 조회 (`ooc list`)

CCone의 모든 서브프로젝트를 나열합니다:
- SP00: 공통 및 문서
- SP01: 원천세 자동 계산
- SP02: 세무 서비스 (척척업무관리)
- SP03: (미정)
- SP04: API 서버 (FastAPI)
- 기타

### 6.4 상세 정보 (`ooc info`)

선택한 프로젝트의 전체 정보를 표시합니다:
- 프로젝트명 및 설명
- 기술 스택 상세
- DB 정보
- 포트 번호
- 실행 명령어
- 주요 모듈

### 6.5 기술 스택 확인 (`ooc stack`)

프로젝트에서 사용하는 모든 기술을 나열합니다:
- 언어 (Python, JavaScript 등)
- 프레임워크 (Streamlit, FastAPI, Django 등)
- 데이터베이스
- 라이브러리
- 버전 정보

### 6.6 모듈 목록 (`ooc modules`)

프로젝트의 주요 모듈과 기능을 표시합니다:
- oais 모듈 (공통 유틸리티)
- 프로젝트별 모듈
- 각 모듈의 주요 기능

## §7. 실제 예시

**예시 1: SP02로 전환**

```bash
$ ooc sp02

=== SP02: 척척업무관리 (Streamlit) ===
상태: 활성 (v08)

기술 스택:
- Python 3.x
- Streamlit
- SQLite3
- Naver OCR API

포트: 8501 (개발) / 8005 (운영)

주요 파일:
- {project}/login.py (진입점)
- {project}/config.py (설정)
- {project}/pages/ (38개 페이지)

다음: 작업 개시
```

**예시 2: 프로젝트 전체 정보**

```bash
$ ooc sp04 info

=== SP04: API 서버 (FastAPI) ===

설명: 배치 처리 API 및 SCP 연동

기술:
- FastAPI + Uvicorn
- SQLite3 (공통 DB)
- Pydantic (검증)
- Paramiko (SCP/SSH)

구조:
├── main.py (진입점)
├── routers/ (API 라우터)
├── models/ (DB 모델)
├── batch/ (배치 엔진)
└── tests/ (10개 테스트)

실행:
$ uvicorn main:app --port 8007

상태: 활성
```

**예시 3: 기술 스택 조회**

```bash
$ ooc sp02 stack

=== SP02 기술 스택 ===

언어: Python 3.x
프레임워크: Streamlit (1.30+)
데이터베이스: SQLite3
주요 라이브러리:
  - pandas (데이터 처리)
  - OpenCV (이미지 처리)
  - PyMuPDF (PDF 처리)
  - requests (API 연동)
  - openpyxl (Excel 처리)
  - win32com (Windows COM)

외부 API:
  - Naver OCR API
  - 특허청 API
  - 하이픈 API

개발 도구:
  - uv (패키지 관리)
  - Git (버전 관리)
```

## §8. 입출력 정의

### 입력

**명령어 형식**:
```
ooc [<spid>] [<command>] [--flags]
```

**파라미터**:
- `<spid>` — SP01, SP02, SP04 등 (생략하면 현재)
- `<command>` — list, info, files, stack, modules 등
- `--json` — JSON 형식 출력
- `--verbose` — 상세 정보

### 출력

**컨텍스트 객체**:
```json
{
  "project_id": "sp02",
  "name": "척척업무관리",
  "status": "active",
  "version": "v08",
  "tech_stack": {
    "language": "Python 3.x",
    "framework": "Streamlit",
    "database": "SQLite3",
    "apis": ["Naver OCR", "특허청 API"]
  },
  "port_dev": 8501,
  "port_prod": 8005,
  "entry_point": "{project}/login.py",
  "config_file": "{project}/config.py",
  "main_directory": "{project}/"
}
```

## §9. FAQ

**Q: SP00는 뭐하는 프로젝트인가요?**  
A: 공통 설정, 문서, oais 모듈 등 모든 프로젝트가 공유하는 리소스입니다.

**Q: SP03는 왜 비어있나요?**  
A: 향후 확장을 위해 예약된 공간입니다.

**Q: 포트 번호는 고정인가요?**  
A: 개발/운영 환경에 따라 다릅니다. `ooc info`로 확인하세요.

**Q: 다른 SP의 모듈을 사용할 수 있나요?**  
A: 예, oais 모듈은 모든 프로젝트에서 공유됩니다.

**Q: 프로젝트 구조가 변경되면 어떻게 해야 하나요?**  
A: `.claude/guides/common_guide.md`에서 최신 정보를 확인하세요.

**Q: 컨텍스트를 저장할 수 있나요?**  
A: `--json` 옵션으로 JSON 형식으로 출력한 후 저장하세요.

## §10. 서브 에이전트

- **codebase-investigator** — 프로젝트 구조 분석
- **oo-leader** — 멀티 프로젝트 조정
- **streamlit-code-reviewer** — Streamlit 프로젝트 검토
- **python-code-reviewer** — Python 코드 검토

## §11. 관련 스킬

- `ooenv` — 환경 현황 확인 (d0009)
- `oohistory` — 프로젝트 이력 (d0010)
- `oodoc` — 문서 자동화
- `oorun` — 프로젝트 실행
- `oocontext` — ooc의 정식명 (긴 버전)
