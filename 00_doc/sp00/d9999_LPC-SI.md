# LPC-SI — Local Phase Coherence Sharpness Index

> NR-IQA 후보 추가 검토용 (PRD §4.2 7종 외 후보)

## 1. 기본 정보

| 항목 | 내용 |
|------|------|
| **정식 명칭** | LPC-SI (Local Phase Coherence — Sharpness Index) |
| **저자** | Rania Hassen, Zhou Wang, Magdy M. A. Salama |
| **연도** | 2013 |
| **출처** | IEEE Transactions on Image Processing, vol. 22, no. 7, pp. 2798–2810 |
| **DOI** | 10.1109/TIP.2013.2251643 |
| **분류** | NR-IQA (No-Reference), Sharpness 전용 |
| **출력 범위** | [0, 1] (값↑ = 선명↑, 블러 시 phase coherence 붕괴) |
| **공식 코드** | MATLAB 원본 (LIVE 페이지 / Zhou Wang 연구실) |

## 2. 핵심 원리

### 2.1 이론적 배경

- **Local Phase Coherence (LPC)**: 자연 이미지의 edge·feature 주변에서 **다중 스케일 복소 wavelet 계수의 위상(phase)**이 일관되게 정렬되는 성질
- 블러 발생 시 위상 정렬이 깨짐 → **phase coherence 강도가 sharpness의 척도**가 됨
- Fourier 위상 정보가 인간 시각 시스템의 sharpness 인지에 핵심이라는 Oppenheim & Lim(1981) 연구에 기반

### 2.2 알고리즘 개요

1. **Complex steerable / log-Gabor wavelet** 다중 스케일 분해
   - 스케일 `s ∈ {s_1, s_2, s_3}` (일반적으로 3 스케일)
   - 방향 `θ ∈ {0°, 45°, 90°, 135°}` (또는 8 방향)
2. 각 위치에서 위상 일관성(phase coherence) 측정
   ```
   PC(x) = | Σ_s c_s(x) | / (Σ_s |c_s(x)| + ε)
   ```
   - `c_s(x)` = 스케일 `s`에서의 복소 wavelet 계수
3. 위상 일관성 강도 `S_LPC(x)`를 신뢰도 가중 평균
   ```
   LPC-SI = Σ_x w(x) × S_LPC(x) / Σ_x w(x)
   ```
   - 가중치 `w(x)` = local energy (edge가 있는 위치만 반영)
4. 정규화하여 [0, 1] 범위 출력

### 2.3 핵심 통찰

- **HSMB**: edge **width**(공간 도메인) 측정 → 블러 시 edge가 퍼지는 폭으로 정량화
- **LPC-SI**: edge **phase coherence**(주파수 도메인) 측정 → 블러 시 다중 스케일 위상 정렬 붕괴로 정량화
- → **물리적으로 직교적인 sharpness 정의** (공간 vs 주파수)

## 3. 특성

| 항목 | 내용 |
|------|------|
| **장점** | • Phase 기반 → 밝기/대비 변화에 강건 (정규화 효과)<br>• 자연영상 통계에 잘 부합 (LIVE 등 공개 DB에서 PLCC ~0.92)<br>• 학습 불필요 (모델-프리) |
| **단점** | • 계산량 큼 (multi-scale complex wavelet)<br>• 노이즈에 다소 민감 (위상 추정 불안정)<br>• 큰 균일 영역(sky) 영향 작음 → edge가 적은 이미지에서 변동성 큼 |
| **HSMB 대비** | • HSMB: Sobel + edge-width Weibull CDF (공간)<br>• LPC-SI: complex wavelet phase coherence (주파수)<br>• → **상호 보완** — 앙상블 가능성 시사 |

## 4. Python 구현 옵션

### 4.1 라이브러리 지원 현황

| 라이브러리 | LPC-SI 지원 | 비고 |
|-----------|------------|------|
| **pyiqa** (0.1.x) | ❌ 없음 | 주요 모델만 |
| **piq** | ❌ 없음 | FR-IQA 중심 |
| **scikit-image** | ❌ 직접 구현 | gabor 필터는 있으나 LPC 알고리즘 없음 |
| **PyWavelets (pywt)** | ✅ 일부 | 실수 wavelet 위주, complex steerable은 별도 필요 |
| **pyrtools** (LCV Lab) | ✅ steerable pyramid | Eero Simoncelli 연구실 공식 포팅 |

### 4.2 권장 구현 경로

```python
# 핵심 의존성
import numpy as np
import pyrtools as pt   # steerable pyramid (복소)

def lpc_si(img_gray: np.ndarray,
           scales=(1, 1.5, 2.0),
           n_orient: int = 8) -> float:
    """LPC-SI sharpness index"""
    # 1. Complex steerable pyramid 분해
    pyr = pt.pyramids.SteerablePyramidFreq(img_gray, height=3,
                                            order=n_orient-1,
                                            is_complex=True)
    coeffs_by_scale = [pyr.pyr_coeffs[(s, o)]
                       for s in range(3)
                       for o in range(n_orient)]

    # 2. 위치별 phase coherence
    eps = 1e-8
    pc_map = np.zeros_like(img_gray, dtype=float)
    w_map = np.zeros_like(img_gray, dtype=float)
    for o in range(n_orient):
        c_stack = np.stack([pyr.pyr_coeffs[(s, o)] for s in range(3)])
        sum_c = np.sum(c_stack, axis=0)
        sum_abs = np.sum(np.abs(c_stack), axis=0) + eps
        pc = np.abs(sum_c) / sum_abs
        energy = sum_abs
        pc_map += pc * energy
        w_map  += energy

    # 3. 가중 평균
    lpc = pc_map.sum() / (w_map.sum() + eps)
    return float(np.clip(lpc, 0.0, 1.0))
```

> ⚠️ 위는 골격만 제시. 정확한 스케일 비율, 방향 수, 정규화 상수는 원논문 §III.C·표 1 확인 필수.

### 4.3 검증 자료

- 원저자 MATLAB 코드:
  - `https://ece.uwaterloo.ca/~z70wang/research/lpcsi/` (Zhou Wang 연구실)
- LIVE Blur DB 기준 보고 성능: PLCC ≈ 0.92, SROCC ≈ 0.93
- Python 포팅 사례 (GitHub):
  - `andrewekhalel/sewar` — 일부 IQA 포함, LPC-SI는 미지원
  - `dingkeyan93/IQA-optimization` (PyTorch) — 일부 모듈

## 5. 본 프로젝트(0003_HSMB) 적용 검토

| 항목 | 내용 |
|------|------|
| **추가 위치** | `src/ps2000_통합IQA.py` 또는 `oais/iqa/lpc_si.py` (신규 모듈) |
| **PRD 영향** | §4.2 비교 NR-IQA 7종 → 8종(또는 9종 with FISH) 확장 검토 |
| **연동 작업** | F002-1 (E1-1 NR-IQA 측정) 산출 CSV 컬럼에 `lpc_si` 추가 |
| **검증 기준** | • 50조건 데이터에서 BEW와의 PLCC/SROCC<br>• HSMB와의 직교성(상관계수) 확인<br>• 모션블러 방향성 미반영 한계 보고 |
| **예상 공수** | 구현 2일 + 검증 1일 (pyrtools 활용 시) — FISH보다 무거움 |
| **종속성 추가** | `pyrtools >= 1.0.5` (또는 자체 complex steerable 구현) |

## 6. 참고문헌

1. R. Hassen, Z. Wang, and M. M. A. Salama, "Image sharpness assessment based on local phase coherence," *IEEE Transactions on Image Processing*, vol. 22, no. 7, pp. 2798–2810, Jul. 2013.
2. P. Kovesi, "Image features from phase congruency," *Videre: Journal of Computer Vision Research*, vol. 1, no. 3, 1999. (Phase 기반 feature 이론 기반)
3. A. V. Oppenheim and J. S. Lim, "The importance of phase in signals," *Proceedings of the IEEE*, vol. 69, no. 5, pp. 529–541, 1981.

## 7. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-05-17 | 초기 작성 — PRD 7종 외 추가 후보 검토용 |
