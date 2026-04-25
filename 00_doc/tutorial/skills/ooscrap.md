# ooscrap 튜토리얼

**생성일**: 2026-04-14 | **버전**: v12 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# URL 자동 감지 및 스크래핑
ooscrap auto --url https://example.com

# YouTube 다운로드 + STT
ooscrap youtube --url "https://youtube.com/watch?v=..." --stt --lang ko

# 웹 페이지 마크다운 변환
ooscrap web --url "https://example.com/article" --format markdown

# 배치 스크래핑
ooscrap batch --urls urls.txt --format json
```

---

## 2. 권장 사용 흐름

**3단계 콘텐츠 수집 워크플로우**:

1. **감지**: URL 유형 자동 판단
   - 웹 페이지 / YouTube / PDF / 이미지

2. **다운로드**: 콘텐츠 추출
   - 텍스트 / 비디오 / 오디오

3. **변환**: 필요 형식으로 변환
   - Markdown / JSON / CSV / HTML

---

## 3. 실전 시나리오

### 시나리오 1: YouTube 강의 자동 필기

```bash
# YouTube 영상 다운로드 + 자동 자막 생성
ooscrap youtube --url "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --stt \
  --lang ko \
  --output lecture_notes.md \
  --timestamp

# 결과:
# # 강의 제목
# 
# ## 00:00 - 소개
# [강의 내용...]
# 
# ## 02:15 - 첫 번째 주제
# [강의 내용...]
```

---

### 시나리오 2: 뉴스 기사 자동 요약

```bash
# 기사 URL에서 텍스트 추출 + 요약
ooscrap web --url "https://news.example.com/article" \
  --extract-text \
  --summary \
  --format markdown
```

---

### 시나리오 3: 배치 웹 스크래핑

```bash
# URL 목록 파일 준비
cat > urls.txt << 'URLS'
https://example.com/page1
https://example.com/page2
https://example.com/page3
URLS

# 배치 스크래핑
ooscrap batch --input urls.txt \
  --format markdown \
  --output-dir ./articles \
  --parallel 3
```

---

## 4. Sub-Agent 역할

| Agent | 역할 | 사용 케이스 |
|-------|------|-----------|
| **data-engineer** | 데이터 추출 | 웹 스크래핑, 파싱 |
| **translator** | 언어 변환 | 다국어 STT |
| **ai-engineer** | STT/음성 인식 | YouTube 자막 생성 |

---

## 5. 관련 스킬

```
ooscrap (스크래핑/STT)
  ├─ oopdf (PDF 추출)
  ├─ oobook (콘텐츠 요약)
  └─ ooresearch (웹 데이터 수집)
```

---

## 6. 주요 기능

### URL 유형 자동 감지

| 유형 | 감지 방식 | 처리 |
|------|----------|------|
| **웹 페이지** | URL 패턴 | HTML 파싱 → 마크다운 |
| **YouTube** | youtube.com | 비디오 다운 + STT |
| **PDF** | .pdf 확장자 | 텍스트 추출 |
| **이미지** | .jpg/.png 등 | OCR 처리 |

### STT 옵션

```bash
# 언어 자동 감지
ooscrap youtube --url "..." --stt --auto-lang

# 특정 언어 지정
ooscrap youtube --url "..." --stt --lang ko,en

# 자막 포맷 선택
ooscrap youtube --url "..." --subtitle-format srt|vtt|json
```

---

## 7. 설정 및 커스터마이징

**config.yaml**:
```yaml
ooscrap:
  auto_detect: true
  default_format: markdown
  stt_engine: google|azure|openai
  stt_languages: [ko, en]
  timeout_seconds: 300
```

---

## 8. 오류 처리

| 오류 | 원인 | 해결 |
|------|------|------|
| `URL not accessible` | 네트워크/차단 | VPN 확인 또는 재시도 |
| `STT failed` | 음성 인식 오류 | 언어 설정 확인 |
| `Parse error` | HTML 구조 변경 | 수동 조정 또는 업데이트 대기 |

---

## 9. 성능 최적화

```bash
# 캐시 활용
ooscrap web --url "..." --cache

# 병렬 배치 처리
ooscrap batch --input urls.txt --parallel 5

# 이미지 압축
ooscrap web --url "..." --compress-images 80
```

---

## 10. 고급 활용

### 조건부 처리

```bash
# 특정 패턴 필터링
ooscrap batch --input urls.txt \
  --filter "title:contains('tutorial')" \
  --filter "lang==ko"
```

### 스케줄 실행

```bash
# 정기적 스크래핑
ooscrap schedule --cron "0 9 * * *" \
  --url "https://example.com/news" \
  --output-dir ./daily_news
```

---

## 11. 트러블슈팅 및 FAQ

### Q: YouTube 자막이 없는 영상을 처리하려면?
**A**: 자동 STT 사용:
```bash
ooscrap youtube --url "..." --stt --force-transcribe
```

### Q: 특정 섹션만 스크래핑하려면?
**A**: CSS 선택자 지정:
```bash
ooscrap web --url "..." --selector "article.main-content"
```

### Q: 다양한 인코딩의 파일을 처리하려면?
**A**:
```bash
ooscrap batch --input urls.txt --encoding auto
```

---

**문서 버전**: v12 (2026-04-14 기준)
**관련 에이전트**: data-engineer, translator, ai-engineer
**다음 단계**: `ooscrap auto --url [URL]` 으로 자동 감지 시작
