# oosota 튜토리얼

**생성일**: 2026-04-14 | **버전**: v01 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# 학술 논문 작성 시작
oosota write --topic "attention mechanisms" --outline

# 논문 SOTA 분석 추가
oosota sota --paper draft.md --comparison

# 참고문헌 자동 생성
oosota citations --paper draft.md --format bibtex

# 논문 최종 검수
oosota review --paper draft.md --full
```

---

## 2. 권장 사용 흐름

**5단계 학술 논문 작성 워크플로우**:

1. **주제 선정**: 개요 작성
2. **배경 조사**: 관련 논문 수집
3. **논문 작성**: 구조화된 작성
4. **SOTA 비교**: 최신 연구와 비교
5. **최종 검수**: 피드백 및 수정

---

## 3. 실전 시나리오

### 시나리오 1: 학술 논문 기본 구조 생성

```bash
oosota write --topic "vision transformers" \
  --outline \
  --sections "abstract,introduction,methodology,results,conclusion"

# 생성 구조:
# # Vision Transformers: Survey
# 
# ## Abstract
# [자동 생성 개요]
# 
# ## 1. Introduction
# [배경 및 동기]
# 
# ## 2. Methodology
# [주요 방법론]
# 
# ## 3. Results
# [성과 분석]
# 
# ## 4. Conclusion
# [결론 및 향후 연구]
```

---

### 시나리오 2: SOTA 비교 테이블 생성

```bash
oosota sota --paper draft.md \
  --comparison \
  --metrics "accuracy,speed,parameters"

# 결과:
# | 모델 | 정확도 | 속도 | 파라미터 | 논문연도 |
# |------|--------|------|---------|---------|
# | ViT-B | 77.9% | 2.1s | 86M | 2020 |
# | Swin | 83.4% | 1.8s | 87M | 2021 |
```

---

## 4. Sub-Agent 역할

| Agent | 역할 |
|-------|------|
| **academic-researcher** | 논문 분석 |
| **scribe** | 논문 작성 |

---

## 5. 관련 스킬

```
oosota (학술 논문)
  ├─ ooresearch (SOTA 연구)
  ├─ oopaper (참고문헌)
  └─ oobook (콘텐츠)
```

---

## 6. 주요 기능

- 논문 구조 자동 생성
- SOTA 비교 자동화
- 참고문헌 관리
- 학술 검증

---

## 7. 설정

**config.yaml**:
```yaml
oosota:
  default_language: en
  cite_format: IEEE
  auto_structure: true
```

---

## 8. 오류 처리

| 오류 | 해결 |
|------|------|
| 구조 오류 | `oosota validate --paper [file]` |
| 인용 오류 | 수동 확인 및 수정 |

---

## 9. 성능 최적화

```bash
oosota write --topic "..." --fast --outline
```

---

## 10. 고급 활용

```bash
# 다국어 지원
oosota write --topic "..." --language zh,es,ko

# 커스텀 템플릿
oosota write --topic "..." --template custom_template.md
```

---

## 11. FAQ

### Q: IEEE 형식이 아닌 다른 형식을 사용하려면?
**A**:
```bash
oosota citations --paper draft.md --format APA|MLA|Chicago
```

---

**문서 버전**: v01 (2026-04-14 기준)
**다음 단계**: `oosota write --topic [주제명]` 으로 논문 작성 시작
