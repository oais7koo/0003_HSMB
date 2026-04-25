# ooresearch 튜토리얼

**생성일**: 2026-04-14 | **버전**: v02 | **ootutorial**: v03

---

## 1. 자주 쓰는 명령어

```bash
# SOTA 기반 연구 시작
ooresearch start --topic "reinforcement learning" --output sota_report.md

# 기존 논문 기반 확장 연구
ooresearch expand --paper arxiv:2301.12345 --depth comprehensive

# 배경 연구 (개념 이해)
ooresearch background --concept "transformer architecture"

# 연구 결과 정렬 및 분석
ooresearch analyze --input research_notes.md --format timeline
```

---

## 2. 권장 사용 흐름

**4단계 연구 워크플로우**:

1. **주제 선정**: SOTA 기반 핵심 논문 자동 수집
   - Google Scholar, arXiv, ResearchGate 통합 검색
   - 인용도 기반 정렬

2. **배경 학습**: 핵심 개념 및 용어 정리
   - 역사적 발전 경로
   - 주요 방법론 비교

3. **심화 분석**: 최신 논문 상세 분석
   - 방법론 분석
   - 성능 비교표 자동 생성

4. **결과 통합**: 최종 연구 리포트 작성
   - 요약 및 결론
   - 향후 연구 방향

---

## 3. 실전 시나리오

### 시나리오 1: SOTA 기반 문헌 분석

```bash
# 1단계: SOTA 수집
ooresearch start --topic "vision transformers" \
  --source arxiv \
  --year-range 2020-2026 \
  --limit 50

# 2단계: 핵심 논문 추출
ooresearch filter --input sota_vit.md \
  --criteria "citations:>100" \
  --output core_papers.md

# 3단계: 논문 간 관계 분석
ooresearch map --input core_papers.md \
  --timeline \
  --method-comparison
```

**결과 예시**:
```
# Vision Transformers SOTA (2020-2026)

## Timeline
2020: Dosovitskiy et al. - ViT 제안
2021: Liu et al. - Swin Transformer
2022: Li et al. - DeiT-III 발전
2023: Woo et al. - ConvNeXt V2
2024: OpenAI Vision - Multi-modal ViT

## 성능 비교
| 모델 | ImageNet Top-1 | 파라미터 | 논문 연도 |
|------|-----------------|---------|----------|
| ViT-B | 77.9% | 86M | 2020 |
| Swin-B | 83.4% | 87M | 2021 |
| ConvNeXt-B | 84.0% | 89M | 2022 |
```

---

### 시나리오 2: 특정 논문 기반 확장 연구

```bash
# arXiv ID로 시작
ooresearch expand --arxiv 2312.12456 \
  --related-papers \
  --citations \
  --depth deep

# 논문의 인용 그래프 시각화
ooresearch graph --paper arxiv:2312.12456 \
  --direction forward \
  --depth 3
```

---

### 시나리오 3: 배경 개념 학습

```bash
# 개념 정의 및 역사
ooresearch background --concept "attention mechanism" \
  --history \
  --key-papers \
  --visual-explanation
```

---

## 4. Sub-Agent 역할

| Agent | 역할 | 사용 케이스 |
|-------|------|-----------|
| **academic-researcher** | 논문 분석, 문헌 검토 | SOTA 분석, 논문 읽기 |
| **data-scientist** | 성능 데이터 분석 | 벤치마크 비교, 성능표 |
| **translator** | 논문 번역 | 비영어 논문 국문화 |

---

## 5. 관련 스킬

```
ooresearch (SOTA 기반 연구)
  ├─ oopaper (논문 관리)
  ├─ oosota (학술 논문 쓰기)
  ├─ oobook (도서 요약)
  └─ ooscrap (논문 스크래핑)
```

**연계 스킬**:
- `oosota`: SOTA 논문 작성
- `oopaper`: 논문 참고문헌 관리
- `ooscrap`: 웹에서 논문 메타데이터 수집

---

## 6. 주요 기능

### 논문 소스 통합

| 소스 | 특징 | 검색 범위 |
|------|------|----------|
| **arXiv** | 프리프린트, 즉시 공개 | 최신 연구 |
| **Google Scholar** | 인용도 높음 | 저널/컨퍼런스 |
| **PubMed** | 생의학 논문 | 의료 분야 |
| **ResearchGate** | 저자 정보 포함 | 저자 추적 |

### 자동 분석

- **문헌 맵**: 시간축 기반 논문 배치
- **방법론 비교**: 표 형식 자동 생성
- **인용 그래프**: 논문 간 인용 관계 시각화

---

## 7. 설정 및 커스터마이징

**config.yaml**:
```yaml
ooresearch:
  sources:
    - arxiv
    - scholar
    - pubmed
  language: ko
  default_depth: moderate
  cite_format: APA
```

---

## 8. 오류 처리

| 오류 | 원인 | 해결 |
|------|------|------|
| `Paper not found` | arXiv ID 오류 | ID 형식 확인: YYMM.NNNNN |
| `Connection timeout` | 네트워크 문제 | VPN 확인 또는 재시도 |
| `PDF extraction failed` | 암호화 PDF | 출판사 사이트 접근 |

---

## 9. 성능 최적화

```bash
# 캐시 활용 (이전 검색 결과 재사용)
ooresearch start --topic "transformers" --cache

# 배치 처리 (여러 주제)
ooresearch batch --topics topics.json --parallel 3
```

---

## 10. 고급 활용

### 맞춤형 분석 기준

```bash
# 특정 저자 기반 연구
ooresearch author --name "Bengio, Yoshua" --depth deep

# 특정 컨퍼런스 논문
ooresearch conference --name "NeurIPS" --year 2023

# 특정 인용도 범위
ooresearch citations --range 100-1000 --field "machine learning"
```

---

## 11. 트러블슈팅 및 FAQ

### Q: arXiv 논문의 최신 버전을 어떻게 확인하나요?
**A**: `ooresearch versions --arxiv 2301.12345` 로 모든 버전 확인 가능

### Q: 특정 분야 SOTA를 자동으로 추적하려면?
**A**: 구독 설정:
```bash
ooresearch subscribe --topic "vision transformers" --frequency weekly
```

### Q: 논문을 국문으로 번역하려면?
**A**: 
```bash
ooresearch translate --arxiv 2312.12456 --target ko --full
```

---

**문서 버전**: v02 (2026-04-14 기준)
**관련 에이전트**: academic-researcher, data-scientist
**다음 단계**: `ooresearch start --topic [주제명]` 으로 SOTA 연구 시작
