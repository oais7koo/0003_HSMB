# oosurvey 튜토리얼

**생성일**: 2026-04-14 | **버전**: v07 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 논문 설문 작성
oosurvey create --topic "machine learning trends" --scope comprehensive

# 관련 논문 자동 분석
oosurvey analyze --input survey_draft.md --related-papers

# 설문 검증
oosurvey validate --survey survey.md --completeness

# 설문 최종 생성
oosurvey publish --survey survey.md --format pdf
```

---

## 2. 권장 사용 흐름

**4단계 설문 작성 워크플로우**:

1. **주제 선정**: 설문 범위 정의
2. **논문 수집**: 관련 논문 자동 분석
3. **콘텐츠 작성**: 구조화된 설문 작성
4. **최종 검증**: 완성도 확인

---

## 3. 실전 시나리오

### 시나리오 1: 포괄적 문헌 설문

```bash
oosurvey create --topic "deep learning in computer vision" \
  --scope comprehensive \
  --period 2015-2026 \
  --num-papers 100

# 생성 결과:
# # Deep Learning in Computer Vision: A Survey
# 
# ## 1. Introduction
# [배경 및 범위]
# 
# ## 2. Historical Evolution
# [2015-2026 발전 경로]
# 
# ## 3. Key Methodologies
# [CNN, RNN, Transformers, etc.]
# 
# ## 4. Benchmark Analysis
# [ImageNet, COCO, etc. 성능 비교]
# 
# ## 5. Future Directions
# [향후 연구 방향]
```

---

### 시나리오 2: 관련 논문 자동 분석

```bash
oosurvey analyze --input draft_survey.md \
  --extract-methodologies \
  --extract-benchmarks \
  --generate-comparison-tables

# 결과:
# - 43개 논문 분석 완료
# - 12개 주요 방법론 추출
# - 8개 벤치마크 비교표 생성
```

---

## 4. Sub-Agent 역할

| Agent | 역할 |
|-------|------|
| **academic-researcher** | 논문 분석 |
| **data-analyst** | 데이터 비교 |

---

## 5. 관련 스킬

```
oosurvey (설문 분석)
  ├─ ooresearch (SOTA 연구)
  ├─ oosota (논문 작성)
  └─ oopaper (참고문헌)
```

---

## 6. 주요 기능

- 자동 논문 수집
- 방법론 추출
- 벤치마크 비교
- 시간축 분석

---

## 7. 설정

**config.yaml**:
```yaml
oosurvey:
  sources: [arxiv, scholar, pubmed]
  auto_extract: true
  generate_tables: true
  cite_format: IEEE
```

---

## 8. 오류 처리

| 오류 | 해결 |
|------|------|
| 논문 부족 | 검색 범위 확대 |
| 추출 오류 | 수동 검토 |

---

## 9. 성능 최적화

```bash
oosurvey create --topic "..." --fast --num-papers 50
```

---

## 10. 고급 활용

```bash
# 다중 주제 설문
oosurvey create --topics topics.json --parallel 3

# 업데이트 설문
oosurvey update --survey existing_survey.md --since 2024-01-01
```

---

## 11. FAQ

### Q: 특정 년도 범위의 논문만 분석하려면?
**A**:
```bash
oosurvey create --topic "..." --period 2020-2026
```

---

**문서 버전**: v07 (2026-04-14 기준)
**다음 단계**: `oosurvey create --topic [주제명]` 으로 설문 시작
