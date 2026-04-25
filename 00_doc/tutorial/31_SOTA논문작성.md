# 시나리오: SOTA급 학술 논문 작성

> 실험 결과에서 저널 투고용 논문 초안까지

---

## 개요

oosota 스킬로 실험 결과 데이터를 기반으로 SOTA급 학술 논문 초안을 작성합니다. IEEE, Elsevier, Springer 등 저널 형식을 지원하며, oopaper와 연동하여 참고문헌을 관리합니다.

**이럴 때 사용:** 실험 결과를 정리해 저널 투고용 논문을 작성할 때
**결과물:** 저널 형식 논문 초안 (MD) + 참고문헌 + (선택) PDF

## 전체 흐름

```
실험 결과 준비 → ooresearch run (선행연구) → oosota run (논문 작성)
→ oopaper run (참고문헌) → oopdf run (PDF 변환)
```

---

## 1. 선행연구 조사 (ooresearch)

```bash
ooresearch run --ai          # AI 도메인 최신 연구 동향
ooresearch run --domain "image segmentation"   # 특정 주제
```

- SOTA 기법 비교 분석
- 연구 갭(gap) 식별
- 참고 논문 목록 생성

---

## 2. 논문 작성 (oosota)

```bash
oosota run
```

### 논문 구조 (자동 생성)

| 섹션 | 내용 |
|------|------|
| Abstract | 연구 요약 (250단어) |
| Introduction | 배경, 문제 정의, 기여점 |
| Related Work | 선행연구 비교 |
| Methodology | 제안 방법 상세 |
| Experiments | 실험 설정, 데이터셋, 평가지표 |
| Results | 실험 결과, 비교 분석, 어블레이션 |
| Discussion | 결과 해석, 한계, 향후 연구 |
| Conclusion | 결론 |
| References | 참고문헌 |

### 저널 형식 지원

```bash
oosota run --format ieee       # IEEE 형식
oosota run --format elsevier   # Elsevier 형식
oosota run --format springer   # Springer 형식
```

---

## 3. 참고문헌 관리 (oopaper)

```bash
oopaper status                 # 현재 논문 보유 현황
oopaper run --lang en          # 영어 논문 파이프라인
```

- 논문 PDF 수집 → 메타데이터 추출 → 서머리 생성
- D:/resilio/1_oais/03_paper/ 디렉토리에 체계적 관리

---

## 4. PDF 변환 (oopdf)

```bash
oopdf run                      # MD → PDF 변환
```

---

## oosota와 oopaper 연동

| 스킬 | 역할 | 관계 |
|------|------|------|
| ooresearch | 선행연구 조사, SOTA 분석 | oosota 입력 |
| oosota | 논문 본문 작성 | 핵심 작업 |
| oopaper | 참고문헌 PDF 관리 | oosota 참조 |
| oosurvey | 서베이 논문 분석 | oosota 보조 |
| oopdf | PDF 변환 | oosota 출력 |

---

## FAQ

**Q: 실험 데이터 없이도 쓸 수 있나?**
A: oosota는 실험 결과 기반 논문 작성이 핵심입니다. 실험 데이터가 있어야 Results/Discussion이 의미 있습니다.

**Q: 한국어 논문도 되나?**
A: 기본은 영어입니다. 한국어 논문은 oosota로 영어 초안을 작성한 뒤 번역하는 흐름을 추천합니다.

**Q: 서베이 논문은?**
A: 서베이는 `oosurvey run`을 사용합니다. oosota는 실험 기반 연구 논문 전용입니다.

---

> 관련: [논문 관리](18_논문관리.md) | [문서 산출물](21_문서산출물.md)
