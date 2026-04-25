# oowork 튜토리얼

## § 1. 필요한 이유

다단계 문서 작업 프로세스를 반복 수행할 때마다 스크립트를 새로 작성하는 것은 비효율적입니다. 기술수요조사, 제안서, 보고서, 견적서 같은 반복되는 문서 작업을 프로세스로 등록하면 팀 전체가 동일한 품질과 절차를 유지하며 일관되게 수행할 수 있습니다. 이것이 oowork의 목표입니다.

## § 2. 빠른 시작 (3가지 기본 명령)

```bash
# 1. 등록된 프로세스 확인
oowork list

# 2. 전체 파이프라인 실행
oowork run 기술수요조사 --topic "1-3 엣지전처리" --keywords "MLOps,AutoML"

# 3. 비텍스트 문서 → 마크다운 변환
oowork extract 기술사업계획서.hwp 변환결과.md
```

## § 3. 자주 쓰는 명령어

| 명령어 | 사용 시점 | 설명 |
|--------|---------|------|
| `oowork list` | 프로세스 시작 전 | 등록된 프로세스 목록 확인 |
| `oowork status <프로세스>` | 진행 중 상태 확인 | 현재 단계 및 출력물 확인 |
| `oowork run <프로세스>` | 전체 실행 | 프로세스 처음부터 끝까지 순차 실행 |
| `oowork add <프로세스명>` | 신규 프로세스 생성 | 템플릿 기반 새 프로세스 등록 |
| `oowork extract <파일>` | 파일 변환 필요 시 | HWP/PDF 등 → Markdown 자동 변환 |

## § 4. 권장 워크플로우

```
1. [프로세스 선택/생성]
   oowork list → 기존 프로세스 확인
   또는
   oowork add 신규프로세스 → 새 프로세스 등록

2. [파일 준비]
   비텍스트 문서(HWP/PDF) 있으면:
   oowork extract <파일> → 마크다운 변환

3. [실행]
   oowork run <프로세스> --topic "주제" --keywords "k1,k2"
   
4. [진행 중 상태 확인]
   oowork status <프로세스> → 현재 단계 확인
   
5. [중단 후 재개]
   oowork run <프로세스> --resume → 마지막 위치부터 재시작
```

## § 5. 전체 명령어 참조

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `oowork help` | 서브명령어 목록 | 터미널 |
| `oowork version` | 스킬 버전 (v02) | 터미널 |
| `oowork status` | 전체 상태 | 터미널 |
| `oowork list` | 등록된 프로세스 목록 | 터미널 |
| `oowork status <프로세스>` | 특정 프로세스 상태 | 터미널 |
| `oowork run <프로세스>` | 프로세스 실행 | 각 단계 산출물 |
| `oowork add <프로세스명>` | 새 프로세스 등록 | 템플릿 생성 |
| `oowork extract <파일>` | 비텍스트 → 마크다운 | 변환된 .md 파일 |
| `oowork check` | 체크리스트 검증 | 터미널 |

## § 6. 상세 사용 방법

### 6.1 프로세스 정의

`references/processes/{프로세스명}.md` 파일 형식:

```markdown
# 기술수요조사

## meta
- version: v01
- author: 작성자
- description: 논문수집부터 기술수요까지 5단계 조사

## steps

### step.0 논문 수집
- tool: oosota
- input: --keywords "${topic}"
- output: 03_paper/
- rules: 영문논문 중심, 최신순
- confirm: true

### step.1 서베이 작성
- tool: oosurvey
- input: ${step.0.output}
- output: 02_기획/21_서베이.md
- rules: 동향분석, 비교표 필수
- confirm: true
```

### 6.2 옵션 상세

| 옵션 | 예시 | 설명 |
|------|------|------|
| `--topic` | `--topic "엣지전처리"` | 작업 주제 (논문 수집 등에 사용) |
| `--keywords` | `--keywords "MLOps,AutoML"` | 검색 키워드 (논문 수집 단계) |
| `--step N` | `--step 2` | 특정 단계만 실행 (2번 단계) |
| `--step N-M` | `--step 1-3` | 범위 실행 (1~3단계) |
| `--workdir` | `--workdir /path` | 작업 디렉토리 (기본: 현재 폴더) |
| `--dry-run` | `--dry-run` | 실행 계획 미리보기 |
| `--resume` | `--resume` | 마지막 중단 지점부터 재개 |

### 6.3 비텍스트 문서 변환

HWP, PDF, DOCX 등 비텍스트 파일을 마크다운으로 변환:

```bash
# HWP → Markdown (자동 넘버링)
oowork extract 10_기술사업계획서.hwp
→ 11_기술사업계획서.md 생성

# PDF 추출
oowork extract 제안서.pdf 변환결과.md

# DOCX 추출
oowork extract 보고서.docx
```

**변환 규칙**:
- 파일명: 원본 유지, 번호만 +1
- 변환 위치: 원본과 동일 폴더
- 중간물: HWPX 등 변환 중간물 유지, txt 등 임시파일 삭제

## § 7. 실전 시나리오

### 7.1 기술수요조사 전체 실행

```bash
# 프로세스 확인
oowork list

# 주제와 키워드 지정하여 실행
oowork run 기술수요조사 \
  --topic "3-3 AI학습자동화" \
  --keywords "MLOps,AutoML,자동화학습" \
  --workdir /path/to/project

# 실행 중 상태 확인
oowork status 기술수요조사

# 중단 후 재개
oowork run 기술수요조사 --resume
```

**출력 구조**:
```
/path/to/project/
├── 02_기획/
│   ├── 10_논문_요약.md
│   ├── 20_서베이.md
│   ├── 30_기술연구.md
│   └── 40_기술수요.md
├── 03_paper/
│   └── (논문 파일들)
└── .oowork/
    └── 기술수요조사_state.json
```

### 7.2 특정 단계만 실행

```bash
# 기술연구(step 2) 단계만 재실행
oowork run 기술수요조사 --step 2

# 서베이부터 기술수요까지 (1~3단계)
oowork run 기술수요조사 --step 1-3

# 실행 계획 미리보기
oowork run 기술수요조사 --dry-run
```

### 7.3 제안서 작성 프로세스

```bash
# 1. 프로세스 생성
oowork add 제안서작성

# 2. 템플릿 기반 정의 (references/processes/제안서작성.md 편집)

# 3. 실행
oowork run 제안서작성 \
  --topic "데이터분석플랫폼" \
  --keywords "빅데이터,ETL,분석"
```

## § 8. 입출력 명세

### 8.1 입력 항목

| 항목 | 타입 | 용도 | 필수 |
|------|------|------|:----:|
| topic | 문자열 | 작업 주제 | O |
| keywords | 쉼표 구분 문자열 | 검색 키워드 | △ |
| step | 번호 또는 범위 | 특정 단계 지정 | - |
| workdir | 경로 | 작업 폴더 | - |

### 8.2 출력 항목

| 항목 | 타입 | 용도 |
|------|------|------|
| 단계별 산출물 | 파일 | 각 단계 결과물 (md, pdf 등) |
| 상태 파일 | JSON | `.oowork/{프로세스}_state.json` |
| 로그 | 텍스트 | 각 단계 실행 로그 |

### 8.3 상태 파일 형식

```json
{
  "process": "기술수요조사",
  "topic": "1-3 엣지전처리",
  "started": "2026-03-24T14:00:00",
  "current_step": 2,
  "steps": {
    "0": {"status": "done", "output": ["03_paper/..."]},
    "1": {"status": "done", "output": ["02_기획/21_서베이.md"]},
    "2": {"status": "running", "output": []},
    "3": {"status": "pending"},
    "4": {"status": "pending"}
  }
}
```

## § 9. FAQ

**Q. HWP 파일이 변환되지 않습니다.**
A. pyhwpx 라이브러리가 필요합니다. `uv add pyhwpx` 실행 후 재시도하세요.

**Q. 프로세스를 중단했는데 처음부터 다시 시작하고 싶습니다.**
A. `--resume` 옵션을 제거하고 그냥 `oowork run <프로세스>`를 실행하세요.

**Q. 특정 단계에서 에러가 발생했습니다.**
A. `.oowork/{프로세스}_state.json` 파일에서 현재 단계를 확인 후 해당 단계 입력물 수정 후 `--step N` 옵션으로 재실행하세요.

**Q. 여러 주제를 동시에 처리할 수 있나요?**
A. 각 주제별로 별도 폴더에서 `--workdir` 옵션으로 실행하세요.

**Q. 새 프로세스를 추가할 때 템플릿이 없습니다.**
A. `oowork add 프로세스명`으로 기본 템플릿이 생성됩니다. `references/processes/프로세스명.md`를 편집하세요.

## § 10. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 논문 수집 | academic-researcher | sonnet | 논문 선별 및 정리 | O |
| 서베이 | academic-researcher | sonnet | 동향분석 및 비교 | O |
| 기술연구 | task-executor | sonnet | 상세 기술 분석 | - |
| 기술수요 | task-executor | sonnet | 요구사항 정의 | - |
| 검증 | task-checker | sonnet | 품질 확인 | - |

## § 11. 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oopaper` | 논문 처리 및 요약 |
| `oosurvey` | 서베이 작성 및 분석 |
| `ooreport` | 보고서/제안서 변환 |
| `oocommit` | 완료 후 커밋 |
| `oodoc` | 최종 문서 정리 |
