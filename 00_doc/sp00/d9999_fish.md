# FISH — Fast Image SHarpness 지표

> NR-IQA 후보 추가 검토용 (PRD §4.2 7종 외 후보)

## 1. 기본 정보

| 항목 | 내용 |
|------|------|
| **정식 명칭** | FISH (Fast Image SHarpness) |
| **저자** | Phong V. Vu, Damon M. Chandler |
| **연도** | 2012 |
| **출처** | IEEE Signal Processing Letters, vol. 19, no. 7, pp. 423–426 |
| **DOI** | 10.1109/LSP.2012.2199980 |
| **분류** | NR-IQA (No-Reference), Sharpness 전용 |
| **출력 범위** | 비음수 실수 (값↑ = 선명↑) |
| **공식 코드** | MATLAB 원본 (Vu & Chandler 연구실 페이지) |

## 2. 핵심 원리

### 2.1 알고리즘 개요

1. **3-level DWT** (Discrete Wavelet Transform) 수행
   - 일반적으로 9/7 또는 Daubechies wavelet 사용
2. 각 레벨 `l ∈ {1,2,3}`의 3개 고주파 부대역(LH, HL, HH)에서 **log-energy** 계산
   ```
   E_{l,b} = log10(1 + (1/N) Σ |c_{l,b}|²)
   ```
3. 레벨별 log-energy를 가중 합산 (저레벨일수록 가중치 높음)
   ```
   E_l = (1 − α_l) × (E_{l,LH} + E_{l,HL})/2  +  α_l × E_{l,HH}
   ```
4. 다중 스케일 가중합으로 최종 점수 산출
   ```
   FISH = Σ_l 2^{(3−l)} × E_l
   ```

### 2.2 Local FISH (FISHbb, Block-Based)

- 16×16 또는 32×32 블록 단위로 계산 후 상위 1% 평균
- 공간적 sharpness map 생성 가능 → 부분 블러 검출에 강함

## 3. 특성

| 항목 | 내용 |
|------|------|
| **장점** | • 빠름 (wavelet 기반, FFT 대비 경량)<br>• 부분 블러(local blur) 검출 우수<br>• 학습 불필요 (NSS 모델 없음) |
| **단점** | • 노이즈에 민감 (HH 부대역 과대 반응)<br>• 색수차·압축 아티팩트 영향<br>• 모션블러 방향성 미반영 |
| **HSMB 대비** | • HSMB: edge-width 통계 기반 (Weibull CDF)<br>• FISH: wavelet 부대역 에너지 기반<br>• → **직교적 정보** 제공 → 비교군으로 유용 |

## 4. Python 구현 옵션

### 4.1 라이브러리 지원 현황

| 라이브러리 | FISH 지원 | 비고 |
|-----------|----------|------|
| **pyiqa** (0.1.x) | ❌ 없음 | NIQE/BRISQUE/PIQE/DBCNN/ARNIQA만 |
| **piq** | ❌ 없음 | FR-IQA 중심 |
| **scikit-image** | ❌ 직접 구현 | `skimage.measure` wavelet 유틸 활용 가능 |
| **PyWavelets (pywt)** | ✅ 구성요소 | DWT만 제공, 알고리즘은 직접 구현 |

### 4.2 권장 구현 경로

```python
# 핵심 의존성
import pywt          # DWT
import numpy as np

def fish(img_gray: np.ndarray) -> float:
    """FISH global sharpness index"""
    coeffs = pywt.wavedec2(img_gray, 'db2', level=3)
    # coeffs[0] = approx, coeffs[1..3] = (LH, HL, HH) tuples
    scores = []
    for l, (lh, hl, hh) in enumerate(coeffs[1:], start=1):
        e_lh = np.log10(1 + (lh ** 2).mean())
        e_hl = np.log10(1 + (hl ** 2).mean())
        e_hh = np.log10(1 + (hh ** 2).mean())
        alpha = 0.8  # 논문 값 확인 필요
        e_l = (1 - alpha) * (e_lh + e_hl) / 2 + alpha * e_hh
        scores.append((2 ** (3 - l)) * e_l)
    return float(sum(scores))
```

> ⚠️ 위는 골격만 제시. 정확한 α, 가중치, normalization은 원논문 표 1 확인 필수.

### 4.3 검증 자료

- 원저자 MATLAB 코드: `http://vision.eng.shizuoka.ac.jp/` (Chandler 연구실)
- Python 포팅 사례 (GitHub):
  - `mikhailiuk/pyfish` (비공식, 검증 필요)
  - 일부 NR-IQA 벤치마크 저장소에 포함됨

## 5. 본 프로젝트(0003_HSMB) 적용 검토

| 항목 | 내용 |
|------|------|
| **추가 위치** | `src/ps2000_통합IQA.py` 또는 `oais/iqa/fish.py` (신규 모듈) |
| **PRD 영향** | §4.2 비교 NR-IQA 7종 → 8종 확장 검토 |
| **연동 작업** | F002-1 (E1-1 NR-IQA 측정) 산출 CSV 컬럼에 `fish` 추가 |
| **검증 기준** | • 50조건 데이터에서 BEW와의 PLCC/SROCC<br>• HSMB와의 직교성(상관계수) 확인 |
| **예상 공수** | 구현 1일 + 검증 1일 (PyWavelets 활용 시) |

## 6. 참고문헌

1. P. V. Vu and D. M. Chandler, "A fast wavelet-based algorithm for global and local image sharpness estimation," *IEEE Signal Processing Letters*, vol. 19, no. 7, pp. 423–426, Jul. 2012.
2. P. V. Vu, C. T. Vu, and D. M. Chandler, "A spatiotemporal most-apparent-distortion model for video quality assessment," *ICIP 2011*.

## 7. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | 2026-05-17 | 초기 작성 — PRD 7종 외 추가 후보 검토용 |
