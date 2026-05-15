# d1010 — 청송 터널 MTF 이동촬영 데이터셋 (ps1010_chungsong_MTF)

## 1. 개요

| 항목 | 내용 |
|------|------|
| **데이터셋명** | ps1010_chungsong_MTF |
| **경로** | `data/ps1010_chungsong_MTF/` |
| **출처** | 청송 터널 내부 벽면에 MTF(eSFR) 차트를 부착한 후, MTSS로 이동 촬영한 현장 실측 데이터 |
| **총 조건 수** | 50개 폴더 |
| **총 이미지 수** | 507장 (조건당 평균 10.1장, 범위 7~13) |
| **이미지 형식** | PNG |
| **측정 도구** | Imatest 24.1.1 Master (SFR multi-ROI) |
| **측정일자** | 2026-03-09 |
| **용도** | E1 실험 — NR-IQA 측정 및 BEW-H/V 상관성 분석의 ground truth 입력 |

---

## 2. 촬영 방법

청송 터널 내벽에 **eSFR(slant-edge MTF) 차트**를 부착하고, MTSS(Mobile Tunnel Scanning System) 차량으로 이동하면서 area-scan 8K 카메라로 촬영하였다. 차량 이동 속도와 카메라 ISO 감도, 카메라-벽면 거리를 변화시켜 **다양한 모션블러 수준**을 재현한 3-factor factorial 설계 실험이다.

---

## 3. 폴더 명명 규칙

```
low_{거리A}_{속도}_{거리B}_{ISO}/
```

| 필드 | 값 | 설명 |
|------|----|------|
| 조도 | low | 터널 내부 저조도 환경 |
| 거리A | 2.5m ~ 6.5m | 카메라-벽면 거리 (거리B와 동일, 현장 메타데이터 보존용 중복 표기) |
| 속도 | 60km, 80km | 차량 이동 속도 (km/h) |
| 거리B | 2.5m ~ 6.5m | 거리A와 동일값 |
| ISO | ISO100 ~ ISO1600 | 카메라 ISO 감도 |

**예시**: `low_4.5m_60km_4.5m_ISO400` → 거리 4.5m, 60 km/h, ISO 400 조건

---

## 4. 실험 조건 구성

### 4.1 3-factor Factorial 설계

| 인자 | 수준 | 비고 |
|------|------|------|
| 속도 | 60 km/h, 80 km/h | 2개 |
| 거리 | 2.5m, 3.5m, 4.5m, 5.5m, 6.5m | 5개 |
| ISO | 100, 200, 400, 800, 1600 | 5개 |
| **전체 조합** | **50개 조건** | 누락 없음 |

### 4.2 조건별 이미지 수 (조건 폴더 직속 frame)

| 거리 | ISO100 | ISO200 | ISO400 | ISO800 | ISO1600 | 소계 |
|------|--------|--------|--------|--------|---------|------|
| 2.5m | 13+9 | 11+9 | 13+10 | 13+11 | 12+11 | 112장 |
| 3.5m | 13+9 | 13+10 | 12+9 | 13+11 | 13+12 | 115장 |
| 4.5m | 16+14 | 17+13 | 16+13 | 17+12 | 14+14 | (ps1301 참조) |
| 5.5m | 16+15 | 16+11 | 15+13 | 15+14 | 15+14 | - |
| 6.5m | 21+18 | 17+14 | 16+16 | 14+13 | 16+14 | - |
| **합계** | | | | | | **507장** |

> 각 셀: 60km/h장 + 80km/h장

---

## 5. 폴더 내 파일 구조

```
low_{조건}/
├── frame_XXXXXX.png          # 이동 촬영 원본 프레임 (조건당 7~13장)
└── Results/
    ├── frame_XXXXXX_Y_multi.csv       # Imatest SFR multi-ROI 측정 결과
    ├── frame_XXXXXX_Y_multi_cpp.png   # ROI 위치 시각화
    ├── frame_XXXXXX_YT {각도}_{N}_sfr.png  # Top 방향 ROI SFR 곡선
    ├── frame_XXXXXX_YB {각도}_{N}_sfr.png  # Bottom 방향
    ├── frame_XXXXXX_YL {각도}_{N}_sfr.png  # Left 방향
    └── frame_XXXXXX_YR {각도}_{N}_sfr.png  # Right 방향
```

| 파일 유형 | 수량 | 설명 |
|-----------|------|------|
| frame PNG (원본) | 507장 | 조건 폴더 직속, 분석 대상 |
| Y_multi.csv | 479개 | Imatest multi-ROI 출력 (28장 측정 미완료) |
| sfr.png (ROI) | 1,763개 | frame당 평균 3.7개 ROI (방향별 slant-edge) |
| cpp.png (ROI 위치) | ≈479개 | Y_multi.csv 1:1 매핑 |

---

## 6. 특이 조건

### 6.1 의도적 Defocus 조건 (ISO 400)

PRD §2.6에 따라 ISO 400 조건은 defocus(초점 이탈)가 발생하도록 의도적으로 설계한 조건이다.

| 조건 | 특성 |
|------|------|
| 전 거리 × ISO400 × 전 속도 (10개 조건) | Motion blur + defocus 복합 블러 |
| BEW 절대값 높음 | Defocus로 인한 등방성 블러 추가 |
| BEW_H − BEW_V 이방성 작음 | Defocus의 등방성 특성 반영 |
| **complex-blur stress test 핵심 서브셋** | `d45_ISO400` 조건이 대표 케이스 |

---

## 7. 활용 계획

| 실험 | 내용 |
|------|------|
| **E1-1: NR-IQA 측정** | 507장 frame → HSMB + 비교 NR-IQA 6종 스코어 산출 |
| **E1-2: BEW 상관 분석** | Y_multi.csv → BEW-H/V 집계 → NR-IQA × BEW scatter + PLCC/SROCC |
| **v1 50조건 벤치마크** | 50조건 ground truth CSV 생성 → HSMB v1 PLCC/SROCC 재현 |
| **Complex-blur stress test** | ISO=400, d=4.5m 조건 분리 → HSMB 복합 블러 응답성 검증 |

---

## 8. 관련 문서

| 문서 | 설명 |
|------|------|
| `00_doc/sp00/d1010_상세기획_청송_MTF_데이터셋.md` | 상세기획 (요구사항·Feature 연결·이슈) |
| `00_doc/sp00/d0001_prd.md` §2.5 | 터널표준영상 정의 |
| `00_doc/sp00/d0001_prd.md` §2.6 | ISO400 의도적 defocus 조건 정의 |
| `00_doc/sp00/d0002_plan.md` F002-1, F002-2 | E1-1·E1-2 실험 계획 |
