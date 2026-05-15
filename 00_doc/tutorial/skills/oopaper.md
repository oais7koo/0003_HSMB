# oopaper Tutorial

> 영문 논문과 국문 보고서의 통합 문헌 관리 스킬 | 버전: v02

## 개요

학술 논문(EN)과 국내 보고서(KO)를 수집·정리·분석하는 통합 스킬입니다. PDF 수집부터 메타데이터 추출, 전문 마크다운 변환, 한글 번역, 서베이 분석까지 논문 라이프사이클을 전담합니다.

**핵심 역할**: 
- 논문 수집 및 메타데이터 자동 추출
- 영문 전문 추출 → 한글 번역 (2단계 프로세스)
- 서머리 생성 및 키워드 추출
- 참고문헌 매칭 및 확장 수집

---

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oopaper help` | 서브명령어 목록 |
| `oopaper version` | 버전 정보 |
| `oopaper status` | 논문 현황 (통계) |
| `oopaper check` | 체크리스트 검증 |
| `oopaper run [--lang]` | **통합 자동 파이프라인** (8단계 EN / 4단계 KO) |
| `oopaper update [--lang]` | 메타데이터 갱신 (멱등) |
| `oopaper anal [--lang]` | 서베이 생성 또는 정밀 분석 |
| `oopaper trans [--lang]` | 텍스트 추출/번역 |
| `oopaper search` | 논문 검색 (arXiv, Semantic Scholar) |
| `oopaper download` | PDF 자동 다운로드 |
| `oopaper extend [--limit]` | 참고문헌 확장 수집 |
| `oopaper backup / restore` | PDF 백업/복원 |
| `oopaper_auto organize` | Phase 0 자동화 (폴더 이동) |
| `oopaper_auto dedup` | 중복 검출 (rapidfuzz) |
| `oopaper_auto meta` | PDF 메타데이터 추출 |

---

## 사용 예시

### 1. 영문 논문 통합 처리

```bash
oocontext 3               # SP03 전환
oopaper run --lang en    # 8단계 파이프라인 실행
```

**처리 순서**:
1. Phase 0: `00_down/` → `11_paper_en/YYMMDD-HHMM/` 이동 + 정규화
2. Phase 1: 미처리 논문 스캔 (상태: X/E/T/S/O)
3. Phase 2: 영문 전문 추출
4. Phase 3: 한글 번역 (translator 에이전트)
5. Phase 4: 서머리 생성 (한글 전문 기반)
6. Phase 5: 참고문헌 추출 + 매칭
7. Phase 6: 정밀 분석
8. Phase 7: paper_list.md 동기화

---

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oosurvey` | 서베이 보고서 생성 (별도) |
| `ooresearch` | SOTA 연구 동향 분석 |
| `oosota` | 논문 작성 (저널 투고용) |
| `ooscrap` | 웹 스크래핑 (논문 외 콘텐츠) |
