# ooreport 튜토리얼

**생성일**: 2026-04-14 | **버전**: v12 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 리포트 생성 (MD → PPTX/DOCX)
ooreport generate --input docs/report.md --output output/report.pptx

# 기존 리포트 갱신
ooreport update --file project/report.md --template corporate

# 배치 처리 (여러 파일)
ooreport batch --dir ./reports --output-format docx

# 실시간 미리보기
ooreport preview --file draft.md --watch
```

---

## 2. 권장 사용 흐름

**3단계 워크플로우**:

1. **작성**: Markdown으로 리포트 콘텐츠 작성
   - 구조화된 섹션 (제목, 본문, 표, 차트)
   - 메타데이터 추가 (제목, 저자, 날짜)

2. **렌더링**: `ooreport generate`로 프레젠테이션/문서 변환
   - 템플릿 선택 (corporate, minimal, academic)
   - 출력 형식 결정 (PPTX, DOCX, PDF)

3. **검증**: 생성된 파일 확인 및 최종 조정
   - 스타일 확인
   - 레이아웃 검증
   - 내용 정확성 검토

---

## 3. 실전 시나리오

### 시나리오 1: 주간 보고서 생성

```markdown
# 주간 보고 리포트 (2026-04-14)
**부서**: 개발팀
**기간**: 2026-04-07 ~ 2026-04-14

## 핵심 성과
- 문제 6건 해결 (R001~R006)
- 새 기능 3개 구현
- 성능 개선 15% 달성

## 주요 과제
- Spring 서버 CMP 파일 누락 (R020)
- DB 보안 강화 필요 (R021)

## 다음주 계획
- CMS 배치 안정화
- 보안 감시 강화
```

**실행**:
```bash
ooreport generate --input weekly_report.md \
  --output week_report_2026-04-14.pptx \
  --template corporate
```

---

### 시나리오 2: 기술 문서 변환

Markdown 기술 문서 → DOCX 형식으로 팀 배포

```bash
ooreport generate --input technical_guide.md \
  --output technical_guide.docx \
  --style academic \
  --add-toc
```

**옵션**:
- `--add-toc`: 목차 자동 생성
- `--add-page-numbers`: 페이지 번호 추가
- `--style academic`: 학술 스타일 적용

---

### 시나리오 3: 대시보드 리포트

데이터 기반 리포트 생성:

```markdown
# 월간 대시보드 (2026-04)

| 지표 | 목표 | 실제 | 달성도 |
|------|------|------|--------|
| 버그 해결 | 10 | 11 | 110% |
| 성능 개선 | 20% | 15% | 75% |
| 보안 감사 | 완료 | 진행중 | - |

## 차트 삽입
![performance-chart](./data/performance.png)
```

---

## 4. Sub-Agent 역할

| Agent | 역할 | 사용 케이스 |
|-------|------|-----------|
| **ooppt-agent** | PPTX 렌더링 | 프레젠테이션 생성, 슬라이드 레이아웃 |
| **data-analyst** | 데이터 시각화 | 차트, 표, 대시보드 리포트 |
| **scribe** | 콘텐츠 작성 | 리포트 초안, 섹션 작성 |

---

## 5. 관련 스킬

```
ooreport
  ├─ ooppt (PPT 생성)
  ├─ ooword (DOCX 생성)
  ├─ oopdf (PDF 변환)
  └─ ooreport (최종 생성)
```

**연계 스킬**:
- `ooppt`: PowerPoint 파일 직접 조작
- `ooword`: Word 문서 생성 및 수정
- `oopdf`: PDF 변환 및 최적화

---

## 6. 주요 기능

### 템플릿 시스템

| 템플릿 | 용도 | 특징 |
|--------|------|------|
| `corporate` | 기업 보고서 | 정식 포맷, 로고 지원 |
| `minimal` | 간단 문서 | 최소 스타일 |
| `academic` | 논문/보고서 | 학술 형식, APA 스타일 |
| `creative` | 마케팅 | 색상, 이미지 강조 |

### 출력 형식

- **PPTX**: 프레젠테이션 (슬라이드)
- **DOCX**: Word 문서 (A4 형식)
- **PDF**: 정적 문서 (배포용)

---

## 7. 설정 및 커스터마이징

**config.yaml**:
```yaml
ooreport:
  default_template: corporate
  default_format: pptx
  line_height: 1.5
  font_family: "Noto Sans CJK KR"
  colors:
    primary: "#0066CC"
    secondary: "#FF6600"
```

**커스텀 템플릿 추가**:
```bash
ooreport template --create my_template \
  --base corporate \
  --colors primary:#FF0000,secondary:#0000FF
```

---

## 8. 오류 처리

### 일반 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `File not found` | 입력 파일 경로 오류 | 절대 경로 확인 |
| `Template not found` | 템플릿 이름 오류 | 지원 템플릿 확인: `ooreport list-templates` |
| `Render failed` | Markdown 문법 오류 | 문법 검증: `ooreport validate --file report.md` |

### 오류 복구

```bash
# 로그 확인
ooreport generate --verbose --input report.md

# 검증 실행
ooreport validate --file report.md --detailed

# 캐시 초기화 후 재시도
ooreport generate --clear-cache --input report.md
```

---

## 9. 성능 최적화

### 대용량 리포트

```bash
# 이미지 압축 활성화
ooreport generate --input large_report.md \
  --compress-images 80 \
  --optimize
```

### 배치 처리 최적화

```bash
# 병렬 처리 (4개 파일 동시)
ooreport batch --dir ./reports \
  --concurrency 4 \
  --format pptx,docx
```

---

## 10. 고급 활용

### 데이터 소스 연동

```bash
# CSV 데이터로 표 자동 생성
ooreport generate --input template.md \
  --data-source data.csv \
  --inject-tables
```

### 동적 콘텐츠

```markdown
# 자동 생성 리포트

## 현재 날짜
생성일: {TODAY}

## 시스템 메트릭
총 파일: {FILE_COUNT}
저장소 크기: {REPO_SIZE}
```

---

## 11. 트러블슈팅 및 FAQ

### Q: Markdown에서 이미지가 안 보여요
**A**: 상대 경로 확인. 절대 경로 사용 권장:
```bash
ooreport generate --base-path /absolute/path --input report.md
```

### Q: 특정 스타일이 PPTX에 미적용되었어요
**A**: 템플릿 버전 확인. 최신 버전 사용:
```bash
ooreport template --list
ooreport generate --template corporate:latest
```

### Q: 대용량 파일 처리가 느려요
**A**: 배치 최적화 및 캐시 활용:
```bash
ooreport batch --dir reports --cache --parallel 4
```

---

**문서 버전**: v12 (2026-04-14 기준)
**관련 에이전트**: ooppt-agent, data-analyst
**다음 단계**: `ooreport list-templates` 로 사용 가능한 템플릿 확인
