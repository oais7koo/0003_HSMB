# -*- coding: utf-8 -*-
# ################################################################################
# Title: 7종 NR-IQA 정식 산출 라이브러리
# Author: oaiskoo
# Date: 2026.05.15
# Version: v01
# Goal: d0100 §4.2 표준 7종 NR-IQA를 정식 알고리즘/라이브러리로 산출하는 함수 모음
# Description:
#   - HSMB    : 자체 구현 (PRD §4.1 사양 — EdgeWeight=1.5, JNB=3, β=2.0, p_jnb=0.63)
#   - CPBD    : PyPI `cpbd` 패키지 (Narvekar & Karam, IEEE TIP 2011)
#   - NIQE    : pyiqa — `niqe` + `niqe_matlab` (두 변형 모두 산출)
#   - PIQE    : pyiqa — `piqe`
#   - BRISQUE : pyiqa — `brisque` + `brisque_matlab` (두 변형 모두 산출)
#   - DBCNN   : pyiqa — `dbcnn`
#   - ARNIQA  : pyiqa — `arniqa`
#   - pyiqa 모델은 (name, device)별 1회 로드 후 캐시 재사용
# 참조: d0001_prd.md §2.7, d0100_수정안의견.md §4.2, d3010_상세기획_E3_1_ps1010_IQA.md
# ################################################################################
from typing import Dict, Optional

import cv2
import numpy as np

LIB_VERSION = "v01"

# pyiqa 선택적 임포트 (torch/pyiqa 미설치 시 해당 메트릭만 비활성)
try:
    import torch
    import pyiqa
    _PYIQA_AVAILABLE = True
except ImportError:
    _PYIQA_AVAILABLE = False

# cpbd 선택적 임포트
try:
    import cpbd as _cpbd_pkg
    _CPBD_AVAILABLE = True
except ImportError:
    _CPBD_AVAILABLE = False


# ################################################################################
# 공통 유틸
# ################################################################################

def imread_safe(path: str, flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """Windows 한글 경로 대응 이미지 로드."""
    buf = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(buf, flags)


def _to_gray(img: np.ndarray) -> np.ndarray:
    """BGR 또는 그레이스케일 입력 → 그레이스케일 uint8."""
    if img.ndim == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def center_crop_half(img: np.ndarray) -> np.ndarray:
    """이미지 중앙에서 가로·세로 각 50% 영역을 크롭 (결과 면적 = 원본의 25%)."""
    h, w = img.shape[:2]
    ch, cw = h // 2, w // 2
    r0, c0 = (h - ch) // 2, (w - cw) // 2
    return img[r0:r0 + ch, c0:c0 + cw]


# ################################################################################
# 1. HSMB — 자체 구현 (PRD §4.1 사양)
# ################################################################################

class HSMBCalculator:
    """HSMB v1 — ps5010_HSMB_v1.py 정식 구현 (d0900 검증 완료).

    PRD §4.1 동결 사양: block_size=64, EdgeWeight=1.5, JNB=3, β=2.0, cdf[63].
    d0900 기준: 15000lx-500us-00km/h 평균 0.8893 (Δ=0.0000).
    출력: float [0,1] — 높을수록 선명.
    """

    W_JNB = 3          # ps5010 고정값
    PROFILE_LENGTH = 10
    CDF_INDEX = 63     # p_jnb ≈ 0.63

    def __init__(self, block_size: int = 64, threshold_ratio: float = 0.1,
                 beta: float = 2.0, edge_weight: float = 1.5,
                 direction: str = "four"):
        self.block_size = block_size
        self.threshold_ratio = float(threshold_ratio)
        self.beta = float(beta)
        self.edge_weight = float(edge_weight)
        self.direction = direction

    def _gradient_magnitude(self, blk: np.ndarray) -> np.ndarray:
        sx = cv2.Sobel(blk, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(blk, cv2.CV_32F, 0, 1, ksize=3)
        return cv2.magnitude(sx, sy)

    def _edge_pixels(self, mag: np.ndarray) -> np.ndarray:
        threshold = float(np.mean(mag)) * self.edge_weight
        return np.argwhere(mag > threshold)

    def _edge_dir(self, blk: np.ndarray, r: int, c: int):
        h, w = blk.shape
        dirs = ([(-1, 0), (1, 0), (0, -1), (0, 1)]
                if self.direction == "four"
                else [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)])
        center = float(blk[r, c])
        best, best_dir = -1.0, (0, 0)
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w:
                d = abs(float(blk[rr, cc]) - center)
                if d > best:
                    best, best_dir = d, (dr, dc)
        return best_dir

    def _edge_profile(self, blk: np.ndarray, r: int, c: int,
                      dr: int, dc: int) -> np.ndarray:
        h, w = blk.shape
        profile = []
        for i in range(self.PROFILE_LENGTH):
            rr, cc = r + dr * i, c + dc * i
            profile.append(float(blk[rr, cc]) if 0 <= rr < h and 0 <= cc < w else 0.0)
        return np.array(profile, dtype=np.float32)

    def _edge_width(self, profile: np.ndarray) -> Optional[float]:
        center = profile[0]
        if center == 0:
            return None
        thr = abs(center) * self.threshold_ratio
        for i in range(1, len(profile)):
            d_cur = abs(profile[i] - center)
            if d_cur >= thr:
                d_prev = abs(profile[i - 1] - center)
                if abs(d_cur - d_prev) < 1e-9:
                    return float(i)
                t = (thr - d_prev) / (d_cur - d_prev)
                return (i - 1) + t
        return None

    def calculate(self, img: np.ndarray) -> float:
        gray = _to_gray(img).astype(np.float32)
        h, w = gray.shape
        n_row, n_col = h // self.block_size, w // self.block_size
        hist = np.zeros(101, dtype=np.float32)
        total_edges = 0

        for br in range(n_row):
            for bc in range(n_col):
                rs, cs = br * self.block_size, bc * self.block_size
                blk = gray[rs:rs + self.block_size, cs:cs + self.block_size]
                mag = self._gradient_magnitude(blk)
                for r_loc, c_loc in self._edge_pixels(mag):
                    dr, dc = self._edge_dir(blk, r_loc, c_loc)
                    if (dr, dc) == (0, 0):
                        continue
                    profile = self._edge_profile(blk, r_loc, c_loc, dr, dc)
                    ew = self._edge_width(profile)
                    if ew is not None:
                        p_blur = 1 - np.exp(-abs(ew / self.W_JNB) ** self.beta)
                        idx = min(int(round(float(p_blur) * 100)), 100)
                        hist[idx] += 1
                        total_edges += 1

        pdf = hist / total_edges if total_edges > 0 else np.zeros(101)
        return round(float(np.cumsum(pdf)[self.CDF_INDEX]), 4)


# 기본 PRD 사양 인스턴스 (모듈 레벨 재사용)
_HSMB_DEFAULT = HSMBCalculator()


def compute_hsmb_v1(img: np.ndarray) -> float:
    """HSMB 스코어 산출 (PRD §4.1 = ps5010 v1, d0900 검증). 높을수록 선명."""
    return _HSMB_DEFAULT.calculate(img)


def compute_bew_hv(img: np.ndarray) -> tuple[float, float]:
    """BEW-H / BEW-V 산출 (Blur Edge Width by direction).

    HSMBCalculator (PRD §4.1 파라미터) 기반. four-direction 모드에서
    수평 이동 방향(dr=0, dc=±1) → BEW-H,
    수직 이동 방향(dr=±1, dc=0) → BEW-V 로 분리.
    엣지가 없으면 nan 반환.

    Returns
    -------
    (bew_h, bew_v) : 각 방향 edge width 평균 (픽셀 단위)
    """
    calc = _HSMB_DEFAULT
    gray = _to_gray(img).astype(np.float32)
    h, w = gray.shape
    n_row = h // calc.block_size
    n_col = w // calc.block_size
    ews_h: list[float] = []
    ews_v: list[float] = []
    for br in range(n_row):
        for bc in range(n_col):
            rs = br * calc.block_size
            cs = bc * calc.block_size
            blk = gray[rs:rs + calc.block_size, cs:cs + calc.block_size]
            mag = calc._gradient_magnitude(blk)
            for r_loc, c_loc in calc._edge_pixels(mag):
                dr, dc = calc._edge_dir(blk, r_loc, c_loc)
                if (dr, dc) == (0, 0):
                    continue
                profile = calc._edge_profile(blk, r_loc, c_loc, dr, dc)
                ew = calc._edge_width(profile)
                if ew is not None:
                    if dr == 0:
                        ews_h.append(ew)
                    else:
                        ews_v.append(ew)
    bew_h = round(float(np.mean(ews_h)), 4) if ews_h else float("nan")
    bew_v = round(float(np.mean(ews_v)), 4) if ews_v else float("nan")
    return bew_h, bew_v


# ################################################################################
# 2. CPBD — PyPI cpbd 패키지 (Narvekar & Karam, IEEE TIP 2011)
# ################################################################################

def compute_cpbd(img: np.ndarray) -> float:
    """CPBD 스코어 산출. 높을수록 선명. cpbd 패키지 필요."""
    if not _CPBD_AVAILABLE:
        raise ImportError("cpbd 패키지 미설치 — `uv add cpbd` 실행 필요")
    gray = _to_gray(img)
    return round(float(_cpbd_pkg.compute(gray)), 4)


# ################################################################################
# 3. pyiqa 기반 5종 (NIQE / PIQE / BRISQUE / DBCNN / ARNIQA)
# ################################################################################

_PYIQA_CACHE: Dict[tuple, object] = {}


def _default_device() -> str:
    return "cuda" if (_PYIQA_AVAILABLE and torch.cuda.is_available()) else "cpu"


def _get_pyiqa_metric(name: str, device: str):
    """(name, device)별 pyiqa 메트릭을 1회 생성 후 캐시."""
    if not _PYIQA_AVAILABLE:
        raise ImportError("pyiqa/torch 미설치 — `uv sync` 실행 필요")
    key = (name, device)
    if key not in _PYIQA_CACHE:
        _PYIQA_CACHE[key] = pyiqa.create_metric(name, device=device)
    return _PYIQA_CACHE[key]


def _img_to_tensor(img: np.ndarray, device: str):
    """BGR/그레이 numpy 이미지 → pyiqa 입력 텐서 (1,3,H,W) RGB [0,1]."""
    if img.ndim == 2:
        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    tensor = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).float() / 255.0
    return tensor.to(device)


def _pyiqa_score(name: str, img: np.ndarray, device: Optional[str]) -> float:
    device = device or _default_device()
    metric = _get_pyiqa_metric(name, device)
    tensor = _img_to_tensor(img, device)
    with torch.no_grad():
        score = metric(tensor)
    return round(float(score.item()), 4)


def compute_niqe(img: np.ndarray, matlab: bool = False,
                 device: Optional[str] = None) -> float:
    """NIQE 스코어. 낮을수록 선명. matlab=True 시 MATLAB 호환 변형."""
    return _pyiqa_score("niqe_matlab" if matlab else "niqe", img, device)


def compute_piqe(img: np.ndarray, device: Optional[str] = None) -> float:
    """PIQE 스코어. 낮을수록 선명."""
    return _pyiqa_score("piqe", img, device)


def compute_brisque(img: np.ndarray, matlab: bool = False,
                    device: Optional[str] = None) -> float:
    """BRISQUE 스코어. 낮을수록 선명. matlab=True 시 MATLAB 호환 변형."""
    return _pyiqa_score("brisque_matlab" if matlab else "brisque", img, device)


def compute_dbcnn(img: np.ndarray, device: Optional[str] = None) -> float:
    """DBCNN 스코어. 높을수록 선명."""
    return _pyiqa_score("dbcnn", img, device)


def compute_arniqa(img: np.ndarray, device: Optional[str] = None) -> float:
    """ARNIQA 스코어. 높을수록 선명."""
    return _pyiqa_score("arniqa", img, device)


# ################################################################################
# 4. 통합 — 7종(9컬럼) 일괄 산출
# ################################################################################

# 9개 출력 컬럼 (NIQE·BRISQUE는 기본/matlab 2변형)
METRIC_COLUMNS = [
    "hsmb", "cpbd", "niqe", "niqe_matlab", "piqe",
    "brisque", "brisque_matlab", "dbcnn", "arniqa",
]

# 메트릭별 방향 (해석 보조)
METRIC_DIRECTION = {
    "hsmb": "높을수록 선명",
    "cpbd": "높을수록 선명",
    "niqe": "낮을수록 선명",
    "niqe_matlab": "낮을수록 선명",
    "piqe": "낮을수록 선명",
    "brisque": "낮을수록 선명",
    "brisque_matlab": "낮을수록 선명",
    "dbcnn": "높을수록 선명",
    "arniqa": "높을수록 선명",
}


def compute_all(img: np.ndarray, device: Optional[str] = None) -> Dict[str, float]:
    """7종 NR-IQA(9컬럼) 일괄 산출. 메트릭 실패 시 해당 컬럼만 NaN."""
    device = device or _default_device()
    result: Dict[str, float] = {}

    for col, fn in (
        ("hsmb", lambda: compute_hsmb_v1(img)),
        ("cpbd", lambda: compute_cpbd(img)),
        ("niqe", lambda: compute_niqe(img, matlab=False, device=device)),
        ("niqe_matlab", lambda: compute_niqe(img, matlab=True, device=device)),
        ("piqe", lambda: compute_piqe(img, device=device)),
        ("brisque", lambda: compute_brisque(img, matlab=False, device=device)),
        ("brisque_matlab", lambda: compute_brisque(img, matlab=True, device=device)),
        ("dbcnn", lambda: compute_dbcnn(img, device=device)),
        ("arniqa", lambda: compute_arniqa(img, device=device)),
    ):
        try:
            result[col] = fn()
        except Exception:
            result[col] = float("nan")

    return result


def compute_all_from_path(path: str, device: Optional[str] = None,
                          center_crop: bool = False) -> Dict[str, float]:
    """이미지 경로 입력 버전 (Windows 한글 경로 대응).

    center_crop=True 시 가로·세로 가운데 50%(면적 25%) 영역만 사용해 산출한다.
    """
    img = imread_safe(path)
    if img is None:
        return {col: float("nan") for col in METRIC_COLUMNS}
    if center_crop:
        img = center_crop_half(img)
    return compute_all(img, device=device)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: uv run python src/common_iqa7.py <이미지경로>")
        print(f"pyiqa 가용: {_PYIQA_AVAILABLE} / cpbd 가용: {_CPBD_AVAILABLE}")
        sys.exit(0)

    scores = compute_all_from_path(sys.argv[1])
    print(f"입력: {sys.argv[1]}")
    for col in METRIC_COLUMNS:
        print(f"  {col:<16} {scores[col]:>10.4f}  ({METRIC_DIRECTION[col]})")
