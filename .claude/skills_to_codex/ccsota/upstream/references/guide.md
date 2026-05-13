# oosota 가이드

## 문서 이력 관리
- v02 2026-04-21 — 소스 문서 체계·워크플로우 상세 단계 이동 (SKILL.md 리팩토링)
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**oosota**: SOTA 분석 논문 작성.

- **참조**: SKILL.md (서브명령어·워크플로우 구조)
- **이 문서**: 방법론(How) — 소스 문서 체계, 워크플로우 상세 단계, 입력/출력 형식

---

## 2. 소스 문서 체계

### 2.1 실험 결과 (1차 소스)

```
d0012_실험결과.md        # 전체 실험 요약
d0013_SOTA성과.md        # SOTA 비교 결과
d3xxx_*.md               # 개별 실험 (베이스라인, 변형, 절제)
d4xxx_*.md               # 공개 데이터셋 실험
d0020_성과논문.md        # 논문 목차 및 기여점 정리
```

### 2.2 문헌 (2차 소스)

```
03_paper/11_paper_en/    # 수집된 참고 논문
d0110_survey.md          # 서베이 결과
d0110_spnet.md           # 특정 아키텍처 분석
```

### 2.3 논문 초안 저장 경로

```
d{SP}6200_paper_draft_v01.md   # 메인 논문 초안
d{SP}6200_paper_draft_v02.md   # 버전업 시 새 파일
```

---

## 3. 워크플로우 상세

### 3.1 init (논문 구조 초기화)

```
oosota init
    1. 실험 문서 스캔 (d0012, d0013, d3xxx, d4xxx)
    2. 핵심 기여점 추출 (vs SOTA 성과)
    3. 논문 섹션 골격 생성 (d{SP}6200_paper_draft.md)
    4. Figure/Table 계획 목록 출력
    5. 투고 저널 추천 (임팩트팩터, 범위 기준)
```

### 3.2 run (전체 논문 작성)

```
oosota run
    1. init 선행 (기존 초안 있으면 스킵)
    2. 실험 데이터 추출 → 테이블/수식 생성
    3. 섹션별 병렬 작성 (academic-researcher 에이전트)
       - abstract / intro / related / method
       - experiments / discussion / conclusion
    4. 내부 교차 검토 (수치 일관성, 참조 연결)
    5. 영문 교정 (grammar, academic tone)
    6. d{SP}6200 저장 + 이력 업데이트
```

### 3.3 section (섹션별 작성/수정)

```
oosota section experiments
    1. d3xxx/d4xxx 실험 문서 로드
    2. 비교 테이블 생성 (베이스라인 vs 제안 vs SOTA)
    3. 절제 연구 테이블 생성
    4. 섹션 작성 → 기존 초안에 병합
    5. 수치 일관성 검토
```

### 3.4 review (논문 종합 교정)

> `ooreport review`(P01~P21) 기능을 통합. 기준 문서: `paper_quality_checklist.md` 전체 카테고리 적용.

```
oosota review [논문파일]
    1. 섹션 구조 검사 (S01~S05): 도입문, 테이블 단독 등장
    2. 내부 마커 검사 (M01~M06): ps코드, 타임스탬프, 이모지
    3. 내부 정보 노출 (E01~E03): Phase 번호, 임시 메모
    4. 수치 일관성 (N01~N05): Abstract ↔ 본문 ↔ 테이블
    5. Abstract 품질 (A01~A04): 4요소, 수치 명시
    6. 기여점·논리 흐름 (C01~C04, L01~L08): 기승전결 대응
    7. 참고문헌 (R01~R05): 인용 완전성, 20개 이상, IEEE 스타일 번호 리스트 형식
    8. 테이블 품질 (T01~T04): 캡션, 수치 출처
    9. 용어 정의 (D01~D03): 수식 기호, 약어 풀어쓰기
   10. 교차 섹션 정합성 (X01~X06): 용어·수치·테이블 번호
   11. 제안 모델 표기 (PI01~PI03): 모델명 Keywords, 주어 통일
   12. 문서 구조 고급 (H01~H06): pseudo-heading, 섹션 밀도, 서술문
   13. 이슈 목록 출력 (Critical → Warning → Info 순)
   14. 수정 우선순위 제시
```

### 3.5 check (논문 품질 체크)

> 체크 기준: `.claude/skills/oosota/paper_quality_checklist.md` (S/M/N/A/C/R/T 7개 카테고리, Critical/Warning/Info 3등급)

```
oosota check [논문파일]
    1. paper_quality_checklist.md 로드 (기준 문서)
    2. 섹션 구조 검사 (S01~S05): 도입문 누락, 표 단독 등장
    3. 내부 마커 검사 (M01~M06): ps코드, 타임스탬프, 이모지, 버전 레이블
    4. 수치 일관성 검사 (N01~N05): Abstract ↔ 본문 ↔ 테이블
    5. Abstract 품질 검사 (A01~A04): 4요소 포함, 수치 명시
    6. 기여점·흐름 검사 (C01~C04): 기여점 수, 논리 일관성
    6-1. 기승전결 논리성 검사 (L01~L08): 기(起)문제→승(承)방법→전(轉)실험→결(結)결론 대응 관계, 도전과제 커버리지, 용어 일관성
    7. 참고문헌 검사 (R01~R04): 인용 완전성, 개수
    8. 테이블 품질 검사 (T01~T04): 캡션, 수치 출처, 본문 참조
    9. 이슈 목록 출력 (Critical N건 / Warning N건 / Info N건)
   10. 수정 우선순위 제시 (Critical → Warning 순)
```

### 3.6 submit (저널 투고 준비)

```
oosota submit aic
    1. 저널 가이드라인 로드 (글자 수, 섹션, 그림 형식)
    2. 현재 초안 vs 가이드라인 차이점 출력
    3. 투고 체크리스트 생성
    4. Cover letter 초안 생성
```

---

## 4. 입출력 형식

| 항목 | 내용 |
|------|------|
| 입력 | 서브명령어 인자 또는 현재 SP 컨텍스트 |
| 출력 | 터미널 출력 또는 문서 파일 생성 (d{SP}6200_paper_draft.md) |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록 |

---

## 5. 주의사항

- SP 컨텍스트 확인 후 실행 (SKILL.md 참조)
- 상세 서브명령어는 SKILL.md 참조
- 수치/테이블/수식은 실험 문서에서 직접 추출 (임의 생성 금지)
- `oosota`는 SOTA 조사 직접 수행 안 함 → `ooresearch` 선행 필요
