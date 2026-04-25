# oopaper 상세 워크플로우

## Part A: 논문 검색/다운로드

### 지원 데이터 소스

| 소스 | 도구 | 주요 기능 |
|------|------|----------|
| **academic-researcher** | Task agent | 논문 검색, 인용 분석, 저자 검색 |
| **WebSearch** | Built-in | Google Scholar, arXiv 등 학술 검색 |
| **WebFetch** | Built-in | 논문 메타데이터 추출 |
| **arXiv API** | Python 스크립트 | 프리프린트 검색 |
| **Unpaywall API** | Python 스크립트 | 페이월 우회, 오픈 액세스 버전 |

### 검색 예시

```bash
# 키워드 검색 (기본)
oopaper search "transformer attention mechanism"
oopaper search "crack segmentation" --년도 2020-2024 --인용 50이상

# 제목/저자 검색
oopaper search "Attention Is All You Need" --type title
oopaper search "Yoshua Bengio" --type author

# 코드/데이터셋/트렌드/학회
oopaper search "Attention" --mode code
oopaper search arxiv:1706.03762 --mode dataset
oopaper search --mode trend --분야 cs.CV
oopaper search --mode conf --학회 NeurIPS --년도 2024
```

### net 옵션 (인용분석)

| 옵션 | 설명 |
|------|------|
| `--action citing` | 인용논문만 |
| `--action cited` | 참고문헌만 |
| `--action both` | 전체 네트워크 (기본) |
| `--depth N` | 탐색 깊이 (기본: 1) |

### 다운로드 워크플로우

#### arXiv 논문
```bash
oopaper run --download arxiv:2301.12345
# -> arXiv API로 PDF URL 조회 -> 00_down/ 다운로드
```

#### 일반 논문 (DOI)
```bash
oopaper run --download doi:10.1038/nature12373
# 1. Unpaywall API로 오픈 액세스 버전 검색
# 2. is_oa: true -> best_oa_location.url_for_pdf 사용
# 3. 00_down/{doi_safe}.pdf로 저장
```

## 정리 흐름 (run --organize)

### Phase 1: PDF 파일 처리

```
03_paper/00_down/ 스캔
-> 각 PDF: 메타데이터 추출 -> 11_paper_en/에 표준 폴더 생성 (YYMMDD-HHMM)
-> PDF 이동 및 표준 파일 생성
```

### Phase 2: 다운로드 리스트 처리

```
00_down/*.md (다운로드 리스트) 스캔
-> 각 항목: 다운로드 시도
-> 성공: 11_paper_en/에 폴더 생성
-> 실패: d0110 "다운로드 불가" 섹션에 추가
-> 처리 완료 리스트: data/00_old/ 이동
```

**실패 사유 분류**: API 오류, MDPI 차단, 페이월, 링크 만료

### Phase 3: d0004 기반 오류 수정

```
d0004_todo.md "논문 오류" 섹션 읽기
-> 각 오류: 유형 확인 -> 자동/수동 수정 판단
-> 수정 완료: d0010_history.md로 이동
```

### 파일명 수정 규칙

| 오류 유형 | 현재 파일명 | 수정 후 |
|----------|------------|---------|
| Type A | `00_서머리.md` | `{CODE}_00_{Title3}_서머리.md` |
| Type B | `{CODE}_03_전문(영어).md` | `{CODE}_03_{Title3}_전문(영어).md` |

Title3 추출: PDF 파일명에서 단어 3개 추출

## 동기화 기능 (run --sync)

서머리 파일에서 메타데이터 추출 -> d0110 빈 필드 채움.

### 추출 대상 필드

| 서머리 필드 | paper_list 필드 | 추출 패턴 |
|------------|----------------|----------|
| `저자:` | 저자 | `- 저자: {value}` |
| `출처:` | 출처/연도 | arXiv, IEEE, MDPI 등 + 연도 |
| `논문 제목:` | 제목 | 검증용 (폴더 ID 매칭) |

## Part B: 분석/서베이

### run --fix 옵션 (유지보수)

| 옵션 | 설명 |
|------|------|
| `--sync` | 서머리 -> d0110 메타데이터 동기화 |
| `--check-only` | 검사만 수행 |
| `--auto-fix` | 자동 수정 가능 오류 수정 |
| `--delete-broken` | 깨진 파일 삭제 |
| `--clean-duplicates` | 중복 파일 정리 |

### 비교 워크플로우

```bash
oopaper anal --compare 251201-0036 251130-2321 251108-1402
oopaper anal --compare --all
oopaper anal --compare --focus performance
```

비교 출력: 성능 비교표 (Dataset, IoU, F1, mAP, 파라미터), 아키텍처 비교표 (Backbone, 특징, 장단점)

## d0110_영어논문(보고서)_리스트.md 형식

### 논문 항목 템플릿

```markdown
### {폴더ID} - {풀 제목}
- **키워드**: {키워드1}, {키워드2}, {키워드3}, ...
- **저자**: {저자명} | **연도**: {YYYY} | **출처**: {출처}
- **등록일**: {YYYY-MM-DD} | **완료**: {O/X}
```

### 풀 제목 추출 규칙 (우선순위)

1. 테이블 형식: `| 제목 | Full Title Here |`
2. 볼드 제목: `- **제목**: Full Title Here`
3. 볼드 논문 제목: `- **논문 제목**: Full Title Here`
4. 리스트 형식: `- 논문 제목: Full Title Here`
5. H1 헤더: `# Full Title Here`

서머리 없는 항목: 폴더ID만 표시 (파일명 기반 축약 제목 사용 금지)

### 다운로드 불가 섹션

```markdown
## 다운로드 불가
| No. | DOI/arXiv | 논문 제목 | 연도 | 출처 | 실패 사유 | 등록일 |
```

## Part D: 인용 관리

### ref 자동 실행 워크플로우

```
1. 매핑 테이블 생성 (11_paper_en/ 스캔 -> 서머리에서 메타데이터 추출)
2. 인용 검증 (보고서의 "[001]" 인용 -> 매핑 테이블 대조)
3. 문제 발견 시 수정 여부 질문
4. 자동 정리 (검증 불가 제거 + 번호 재부여 + 형식 정규화)
5. 결과 저장 (새 버전 파일)
```

### 매핑 테이블 구조

| 번호 | 코드 | 저자 | 연도 | 제목 (앞 30자) |
|------|------|------|------|----------------|
| [001] | 240312-1611 | Ham | 2022 | 멀티스케일 멀티레벨... |

### 인용 형식 규칙

**올바른 형식**: `Zhang et al. (2022)[001]`, `Park et al. (2014)[006]`, `Kim (2023)[012]`

| 요소 | 규칙 |
|------|------|
| 저자명 | 영문 표기, et al. 사용 |
| 연도 | 4자리 숫자 괄호 |
| 번호 | 3자리 대괄호, 등장 순서 |
| 복수 저자 | `&` 연결 |

### 검증 기준

- 검증 가능: 폴더 존재 + 서머리 존재 + 메타데이터 추출 가능
- 검증 불가: 폴더 없음, 서머리 없음, 메타데이터 추출 불가

## 전체 워크플로우 (논문 수집 -> 분석 -> 서베이)

```
1. oopaper search "crack segmentation deep learning" --년도 2020-2024
2. oopaper run --download arxiv:2301.12345
3. oopaper run --organize
4. oopaper trans english / oopaper trans korean
5. oopaper anal / oopaper anal --deep
6. oopaper run --fix --check-only
7. oopaper anal --compare --all --focus performance
```

## 병렬 처리

대량 논문 분석 시:

| Phase | 작업 | 에이전트 | 병렬 |
|:-----:|------|----------|:----:|
| 1 | 영어추출 | data-analyst | O |
| 2 | 한글번역 | translator | O |
| 3 | 정밀분석 | academic-researcher | O |

예시: 93편 논문 -> 5개 배치 (각 18-20편) x 3개 Phase

## 검사 항목

| # | 검사 항목 | 검사 내용 | 수정 방식 |
|---|----------|----------|----------|
| 1 | 파일명 규칙 | `{CODE}_00_{Title3}_서머리.md` 형식 | 자동 |
| 2 | PDF 존재 | 원본 PDF 파일 존재 여부 | 수동 |
| 3 | 인코딩 검사 | UTF-8, 깨진 문자 없음 | 수동 |
| 4 | 영어 전문 품질 | PDF 추출 검증 | 수동 |
| 5 | 한글 번역 품질 | 번역 완료 여부 | 수동 |
| 6 | 서머리 품질 | 필수 섹션, 내용 충실도 | 수동 |
