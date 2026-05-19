# 청송터널 MTF IQA 산출 상세구현

> 문서번호: d3010 | 단계: 기획 | SP: 00 | 생성일: 2026-05-15
> 연결 Feature: F002-4 | plan.md §3 E002 | S1 병행 작업

## 1. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v09 | 2026-05-19 | ps3011(SFR↔IQA 상관분석) 내용을 신규 문서 d3011로 분리 — 본 문서는 ps3010 IQA 산출 전용. §9·§11 SFR 부분 제거 |
| v08 | 2026-05-19 | 결과 리포트(d0043) 통합 — §11 실험 결과 섹션 신설, 별도 리포트 폐지 |
| v07 | 2026-05-19 | §9 SFR↔IQA 상관을 속도 그룹별(all/60km/80km) 분리 재분석으로 갱신, 산출 경로 `data/ps3010` → `data/ps3011` 표준화 (ps3011 스크립트 번호 기준) |
| v06 | 2026-05-17 | B.3 재개 실행 명령어 섹션 추가 — `--resume` 사용법 명시 |

---

## 2. 문서 관리

| 항목 | 내용 |
|------|------|
| 문서번호 | `d3010` |
| 대상 기능 | `F002-4 E3-1 ps1010 IQA 분석` |
| 원본 데이터 | `data/ps1010_chungsong_MTF/` (50조건, frame 520장 — ISO1600 평탄화 반영) |
| IQA 라이브러리 | `src/common_iqa7.py` — 7종 정식 산출 (9컬럼) |
| 진입 스크립트 | `src/ps3010_e3_1_ps1010_iqa.py` (common_iqa7 `compute_all_from_path()` 호출) |
| 진행 상태 | IQA 산출 ✅ **완료** (2026-05-15) |
| 버전 | v09 |
| 작성일 | 2026-05-15 (v09: 2026-05-19) |
| 관련 문서 | `d0001_prd.md` §2.7, `d1010_상세기획_청송_MTF_데이터셋.md`, `d0100_수정안의견.md` §4.2 |

---

## 3. 기능 개요

청송 터널 MTF 이동촬영 데이터셋(`ps1010_chungsong_MTF`, 50조건 frame 520장) 전체에 대해 **d0100 표준 7종 NR-IQA** 스코어를 `common_iqa7.py`로 일괄 산출한다. NIQE·BRISQUE는 pyiqa 기본/MATLAB 두 변형을 모두 산출하므로 출력은 **9컬럼**이다. PRD v06 §2.7에서 신규 정의한 E3 실험군의 첫 작업으로, 현장 50조건 실측 데이터셋의 IQA 분포 기준선을 확보한다.

IQA 산출은 정식 라이브러리 `common_iqa7.py`(HSMB 자체구현 + CPBD PyPI + pyiqa 5종)를 사용하며, batch runner는 이 라이브러리를 import해 50조건을 순회한다.

> SFR↔IQA 상관분석은 후속 스크립트 ps3011에서 수행한다 — d3011_상세구현_청송MTF_SFR상관분석.md 참조.

---

## 4. 요구사항

| ID | 요구사항 | 우선순위 | 출처 |
|----|---------|---------|------|
| R01 | `ps3010_e3_1_ps1010_iqa.py`가 `common_iqa7.py`의 `compute_all_from_path()`를 호출해 ps1010 50조건 순회 | Must | PRD F16a |
| R02 | common_iqa7 9컬럼 산출 — `hsmb, cpbd, niqe, niqe_matlab, piqe, brisque, brisque_matlab, dbcnn, arniqa` | Must | PRD §2.7.3, common_iqa7 `METRIC_COLUMNS` |
| R03 | 분석 대상은 조건 폴더 직속 `frame_*.png` 520장만 (`Results/` 하위 제외) | Must | d1010 §5 |
| R04 | 조건 폴더명 파싱(`low_{거리}_{속도}_{거리}_ISO{값}`) → CSV 메타 컬럼화 | Must | d1010 §5.4 |
| R05 | 조건별·전체 기술통계 + 히스토그램 리포트 생성 | Must | PRD F16a |
| R06 | ISO=400 의도적 defocus 조건 별도 플래그 컬럼 표시 | Should | PRD §2.6 |
| R07 | 중간 체크포인트 저장 (이미지 단위 incremental CSV, key=`condition+frame`) | Should | plan R03 |

---

## 5. 입출력 정의

### 5.1 입력

| 항목 | 타입 | 설명 | 필수 |
|------|------|------|------|
| `data/ps1010_chungsong_MTF/` | folder | 50개 조건 폴더, 각 폴더 직속 `frame_*.png` (총 520장) | Y |
| `src/common_iqa7.py` | Python | 7종 IQA 정식 산출 라이브러리 (`compute_all_from_path()`) | Y |

### 5.2 출력

| 항목 | 타입 | 설명 |
|------|------|------|
| `src/ps3010_e3_1_ps1010_iqa.py` | Python | ps1010 50조건 일괄 실행 진입점 (common_iqa7 import) |
| `data/ps3010/01_전체데이터_{dsr}.xlsx` | XLSX | 이미지별 9컬럼 스코어 + 조건 메타 (520행) |
| `data/ps3010/02_그룹별통계_{dsr}.xlsx` | XLSX | 조건별 mean/std/min/max (50조건) |
| `data/ps3010/03_그룹별평균_{dsr}.xlsx` | XLSX | 조건별 평균 + best_group 행 |
| `data/ps3010/04_histogram_{dsr}.png` | PNG | 9종 메트릭 히스토그램 |
| `00_doc/sp00/d3010_상세구현_청송MTF_IQA산출.md` §11 | MD | 결과 요약 + 조건별 분포 표 + 히스토그램 (본 문서 통합) |

### 5.3 출력 스키마 (`data/ps3010/01_전체데이터_{dsr}.xlsx`)

```
condition, distance_m, speed_kmh, iso, frame, is_defocus,
hsmb, cpbd, niqe, niqe_matlab, piqe, brisque, brisque_matlab, dbcnn, arniqa
```

- `condition`: 조건 폴더명 (예: `low_4.5m_60km_4.5m_ISO400`)
- `is_defocus`: ISO=400 조건이면 1, 아니면 0
- IQA 9컬럼: common_iqa7 `METRIC_COLUMNS` — NIQE·BRISQUE는 기본/MATLAB 2변형 산출
- 공통 규칙: d0100 §6.4 — UTF-8, 소수점 4자리(`.4f`), 결측 `NaN`

---

## 6. 제약조건 / 예외처리

| 상황 | 처리 방식 |
|------|----------|
| GPU OOM (50조건 일괄) | 조건 단위 분할 + 매 조건 후 `torch.cuda.empty_cache()` |
| 폴더명 파싱 실패 | 경고 로그 + 해당 조건 스킵 (수동 검토용 리스트) |
| 일부 NR-IQA 모델 로드 실패 | common_iqa7 `compute_all()`이 해당 컬럼만 `NaN` 처리, 나머지 진행 |
| `Results/` 하위 PNG 혼입 | 조건 폴더 직속 `frame_*.png`만 glob, `Results/` 명시 제외 |
| ISO=400 조건 (의도적 defocus) | `is_defocus` 플래그 컬럼 표시 (PRD §2.6, F003-2 연계) |
| common_iqa7 의존성 미설치 (pyiqa/cpbd) | GPU 환경 `uv sync` + common_iqa7 동작 검증 선결 (d0004 TODO) |

---

## 7. 관련 Feature (plan.md 연결)

- 연결 Feature: `F002-4` — E3-1 ps1010 IQA 분석
- 의존 Feature: 없음 (즉시 착수 가능, common_iqa7 IQA 라이브러리만 의존)
- 후속 의존: **F002-7** (E3-4 ps1010+ps1301 통합 풀 — 본 결과를 개별 비교 기준으로 사용)
- 선행 조건: `common_iqa7.py` 동작 검증 (d0004 TODO, GPU 환경)

---

## 8. 참고 자료

- PRD: `00_doc/sp00/d0001_prd.md` §2.7 (E3 실험군), §2.6 (의도적 defocus)
- 계획: `00_doc/sp00/d0002_plan.md` §3 E002 F002-4, S1
- 데이터셋: `00_doc/sp00/d1010_상세기획_청송_MTF_데이터셋.md`, `d1010_chungsong_MTF.md`
- 메트릭 사양: `00_doc/sp00/d0100_수정안의견.md` §4.2 (산출 메트릭 7종)
- IQA 라이브러리: `src/common_iqa7.py` — `compute_all()`, `METRIC_COLUMNS` (9컬럼)
- 유사 작업: `00_doc/sp00/d9040_상세기획_E1_1_NR_IQA_측정.md` (E1-1, 동일 파이프라인)
- 베이스 스크립트: `src/ps2000_통합IQA.py` v04 (HSMB·DL-IQA 로직 원본)
- 후속 분석(SFR 상관): `00_doc/sp00/d3011_상세구현_청송MTF_SFR상관분석.md`

---

## 9. 후속 분석 — SFR↔IQA 상관

ps3010 IQA 산출 결과와 ps1010 SFR 측정값(R1090·MTF50)의 상관 분석은 별도 스크립트 `ps3011_e3_1_sfr_correlation.py`에서 수행한다. 상세 명세·결과는 `d3011_상세구현_청송MTF_SFR상관분석.md` 참조.

---

## 10. 이슈

| 날짜 | 내용 | 상태 |
|------|------|------|
| 2026-05-15 | `low_4.5m_60km_4.5m_ISO1600` 폴더 평탄화 누락(`MTF 50/` 중간폴더) → 사용자 평탄화 완료, `--resume` 재처리로 50조건 520프레임 완성 | ✅ 해결 |
| 2026-05-15 | frame.png 수와 Imatest 측정 CSV(Y_multi.csv) 수 불일치 — IQA 측정은 frame 전수 대상이므로 영향 없음, BEW/SFR 상관(d3011·E1-2)에서만 매칭 검토 필요 | 🟡 참고 |

---

## A. 설계 상세 (아키텍처/API/DB)

### A.1 구현 코드 구조 및 파일 위치

| 구분 | 폴더/파일 경로 | 역할 | 상태 |
|------|--------------|------|------|
| IQA 라이브러리 | `src/common_iqa7.py` | 7종 NR-IQA(9컬럼) 산출 — `compute_all_from_path()` | ✅ 완료 |
| 진입 스크립트 | `src/ps3010_e3_1_ps1010_iqa.py` | ps1010 50조건 순회 → IQA 산출 → xlsx 3종 + histogram | ✅ 완료 |
| IQA 산출물 | `data/ps3010/01~04_*` | 520프레임 9컬럼 + 통계 + 히스토그램 | ✅ 완료 |
| 결과 리포트 | §11 실험 결과 (본 문서 통합) | IQA 분포 결과 리포트 | ✅ 완료 |

### A.2 아키텍처 / 흐름도

```
[IQA 산출 흐름]
ps1010 50조건 폴더 → 조건명 파싱(low_*) → frame_*.png 순회
  → common_iqa7.compute_all_from_path() → 9컬럼 → 조건 단위 체크포인트
  → 01_전체데이터.xlsx(520행) + 02·03 통계 + 04 histogram
```

### A.3 DB 설계

해당 없음 — 실험 산출물은 CSV·XLSX·MD로 관리, DB 미사용.

### A.4 API 설계

해당 없음 — 외부 API·웹 연동 없음. common_iqa7 라이브러리 함수 호출만.

---

## B. 구현 노트 (Task 체크리스트)

### B.1 구현 Task

| Task | 산출물 | 상태 |
|------|--------|------|
| ps3010 진입 스크립트 작성 (조건 순회·IQA 산출·xlsx 출력) | `src/ps3010_e3_1_ps1010_iqa.py` | ✅ 완료 |
| ps1010 50조건 520프레임 IQA 산출 실행 | `data/ps3010/01~04_2605151913.*` | ✅ 완료 |
| 결과 리포트 작성 | §11 실험 결과 (본 문서 통합) | ✅ 완료 |

### B.2 진행 현황

- **IQA 산출**: ✅ 완료 — 50조건 520프레임 9컬럼, 정합성 검증 완료 (HSMB 재산출 일치)

### B.3 구현 메모

- IQA 산출은 CPU 실행으로 완료 (GPU+CPU 혼재분 device 미세차 무시 수준 — 현 결과 확정)

### B.4 재개 실행 가이드 (체크포인트 기반)

> 윈도우 재부팅·강제 종료 후 아래 명령으로 중단 지점부터 재개한다.

```powershell
# 최초 실행
uv run python src/ps3010_e3_1_ps1010_iqa.py --device cpu

# 재개 실행 (체크포인트부터 이어서)
uv run python src/ps3010_e3_1_ps1010_iqa.py --resume --device cpu
```

| 항목 | 내용 |
|------|------|
| 체크포인트 파일 | `data/ps3010/_checkpoint.csv` |
| 중복 제거 기준 | `condition + frame` (재개 시 자동 중복 제거) |
| 원자적 저장 | `.tmp` 파일 → `os.replace()` (재부팅 직전 쓰기 중 파일 손상 방지) |
| 체크포인트 없는 경우 | `--resume` 지정해도 처음부터 실행 |

---

## 11. 실험 결과

### 11.1 실험 개요

| 항목 | 내용 |
|------|------|
| 데이터셋 | 청송터널 MTF 이동촬영 (`ps1010_chungsong_MTF`) |
| 조건 수 | 50조건 (조도×거리×속도×ISO 조합) |
| 프레임 수 | 520장 (ISO1600 평탄화 포함) |
| defocus 조건 | ISO=400 의도적 defocus 102장 (PRD §2.6) |
| IQA 메트릭 | 7종 9컬럼 (hsmb·cpbd·niqe·niqe_matlab·piqe·brisque·brisque_matlab·dbcnn·arniqa) |

### 11.2 IQA 분포 (50조건 평균 기준)

#### 11.2.1 기술통계

| 메트릭 | mean | std | min | max |
|--------|------|-----|-----|-----|
| hsmb | 0.7316 | 0.1070 | — | — |
| cpbd | 0.8988 | 0.1004 | — | — |
| niqe | 7.3258 | 1.1602 | — | — |
| niqe_matlab | 6.1106 | 0.7249 | — | — |
| piqe | 11.8347 | 4.1559 | — | — |
| brisque | 10.3803 | 10.0902 | — | — |
| brisque_matlab | 36.7481 | 5.1121 | — | — |
| dbcnn | 0.3375 | 0.0135 | — | — |
| arniqa | 0.3206 | 0.0447 | — | — |

> 히스토그램: `data/ps3010/04_histogram_2605171535.png`

#### 11.2.2 조건별 분포 특징

- **HSMB**: mean=0.73, std=0.11 — 모션블러 조건별 분산 존재, defocus(ISO=400) 102장 별도 식별됨
- **ARNIQA**: mean=0.32, std=0.04 — 전 조건 걸쳐 가장 안정적 분포 (std 최소)
- **BRISQUE**: std=10.09 — 가장 큰 분산, 조건 간 편차 크며 SFR 상관도 높음

### 11.3 산출물 목록

| 파일 | 설명 |
|------|------|
| `data/ps3010/01_전체데이터_2605171535.xlsx` | 520프레임 × 9컬럼 IQA |
| `data/ps3010/02_그룹별통계_2605171535.xlsx` | 50조건별 mean/std/min/max |
| `data/ps3010/03_그룹별평균_2605171535.xlsx` | 50조건별 평균 |
| `data/ps3010/04_histogram_2605171535.png` | 9종 메트릭 히스토그램 |

### 11.4 후속 과제

> SFR↔IQA 상관분석 및 후속 과제는 d3011 참조.
