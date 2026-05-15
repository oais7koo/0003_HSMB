# -*- coding: utf-8 -*-
# ################################################################################
# Title: NR-IQA + DL-IQA + FR-IQA 통합 이미지별 분석 (독립 실행형)
# Author: oaiskoo
# Date: 2026.04.23
# Version: v04
# Goal: 이미지별 NR-IQA(23개) + DL-IQA(2개) + FR-IQA(6개) 통합 계산 및 Excel 리포트 생성
# Changes:
#   - v04: DL-IQA 추가 (DBCNN + ARNIQA, pyiqa 기반 순차 처리, --no_dl 옵션)
#   - v03: input_dir → data/ps1204_kict_eSFR / FR-IQA 기준을 속도 _00 그룹으로 동적 매핑
#   - v02: oais 패키지 의존성 제거 — 모든 함수 인라인 포함 (독립 실행형)
#   - v01: 초기 버전 (ps6310 NR-IQA + ps6320 FR-IQA 통합)
# Description:
#   - NR-IQA: 참조 없이 각 이미지 품질 지표 계산 (블러·노이즈·대비·통계·HSMB 등)
#   - DL-IQA: DBCNN + ARNIQA (pyiqa, torch 필요 / --no_dl 로 비활성화 가능)
#   - FR-IQA: 속도 _00 그룹을 기준으로 SSIM/PSNR/MSE/MAE/UQI/MS-SSIM 계산
#   - 이미지별 1행으로 NR+DL+FR 통합 DataFrame 구성 → Excel 3종 출력
#   - 멀티프로세싱 + 한글 경로 대응 / oais 패키지 불필요
# Input: ./data/{input_dir}/*/  (첫 번째 서브디렉토리 = 원본/Reference)
# Output: ./data/ps6350/
# ################################################################################
# Library
# ################################################################################
import os
import sys
import stat
import shutil
import time
import glob
import argparse
import platform
import datetime
import warnings
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
from skimage.metrics import structural_similarity as _ssim_func
from skimage.metrics import peak_signal_noise_ratio as _psnr_func

# DL-IQA 선택적 임포트 (torch/pyiqa 미설치 시 자동 비활성화)
try:
    import torch
    import torchvision.transforms as _tv_transforms
    from PIL import Image as _PILImage
    import pyiqa as _pyiqa_lib
    _DL_AVAILABLE = True
except ImportError:
    _DL_AVAILABLE = False

# Windows 한글 경로 대응 (cv2.imread monkey-patch) — 모든 import 완료 후 적용
_orig_cv2_imread = cv2.imread


def _imread_safe(path, flags=cv2.IMREAD_COLOR):
    buf = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(buf, flags)


cv2.imread = _imread_safe

# ################################################################################
# Setting
# ################################################################################
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

prefix = os.path.splitext(os.path.basename(__file__))[0][:6]
workname = os.path.splitext(os.path.basename(__file__))[0][6:]
dsr = datetime.datetime.now().strftime("%y%m%d%H%M")
print(prefix + "_" + workname + "_" + dsr)

stime = time.time()
mpl.use("Agg")
warnings.filterwarnings("default")

# ################################################################################
# Parameter
# ################################################################################
# =============================================================================
# 파라미터 설정 (수정 가능)
# =============================================================================
CONFIG = {
    "io": {
        "input_dir": "data/ps1204_kict_eSFR",
        "extensions": ["bmp", "png", "jpg", "jpeg", "tif", "tiff"],
    },
    "nr_iqa": {
        "include_hsmb": True,
        "hsmb": {
            "block_size": 64,
            "threshold_ratio": 0.1,
            "beta": 2.0,
            "edge_weight": 1.5,
            "direction": "four",
        },
    },
    "fr_iqa": {
        "enabled": True,
        "include_ms_ssim": True,
    },
    "dl_iqa": {
        "enabled": True,   # False = DL-IQA 스킵 / --no_dl 플래그로도 비활성화
        "device": None,    # None=자동(CUDA 우선), 'cpu', 'cuda'
    },
    "processing": {
        "parallel": True,
        "max_workers": None,
    },
    "output": {
        "save_histograms": True,
        "key_nr_metrics": ["hsmb", "cpbd", "brisque", "weighted_score"],
        "key_fr_metrics": ["fr_psnr", "fr_ssim"],
    },
}
# =============================================================================

parser = argparse.ArgumentParser(description="NR+FR 통합 IQA 분석")
parser.add_argument("--reset", type=str, default="y")
parser.add_argument("--input_dir", "-i", type=str, default=None)
parser.add_argument("--no_hsmb", action="store_true")
parser.add_argument("--no_fr", action="store_true")
parser.add_argument("--no_parallel", action="store_true")
parser.add_argument("--no_dl", action="store_true")
args = parser.parse_args()

if args.input_dir:
    CONFIG["io"]["input_dir"] = args.input_dir
if args.no_hsmb:
    CONFIG["nr_iqa"]["include_hsmb"] = False
if args.no_fr:
    CONFIG["fr_iqa"]["enabled"] = False
if args.no_parallel:
    CONFIG["processing"]["parallel"] = False
if args.no_dl:
    CONFIG["dl_iqa"]["enabled"] = False

cpu_cores = mp.cpu_count()
max_workers = CONFIG["processing"]["max_workers"] or max(1, cpu_cores - 2)

os_var = platform.system()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 15
if os_var == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_var == "Darwin":
    mpl.rc("font", family="AppleGothic")
else:
    plt.rcParams["font.family"] = "NanumGothic"


# ################################################################################
# ── Utils (oais.utils 인라인) ────────────────────────────────────────────────
# ################################################################################

def _onerror(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise exc_info[1].with_traceback(exc_info[2])


def make_output_dir(root_dir: str, prefix: str, rmfolder: str = "n") -> str:
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"root_dir does not exist: {root_dir!r}")
    output_dir = root_dir + "/" + prefix
    if os.path.exists(output_dir):
        if rmfolder == "y":
            shutil.rmtree(output_dir, onerror=_onerror)
            os.makedirs(output_dir)
    else:
        os.makedirs(output_dir)
    return output_dir


def count_files_by_extensions(folder: str, extensions: List[str]) -> int:
    count = 0
    for ext in extensions:
        count += len(glob.glob(os.path.join(folder, "**", f"*.{ext}"), recursive=True))
        count += len(glob.glob(os.path.join(folder, "**", f"*.{ext.upper()}"), recursive=True))
    return count


# ################################################################################
# ── NR-IQA (oais.iqa.nr_iqa 인라인) ─────────────────────────────────────────
# ################################################################################

class ImageQualityAssessment:
    """NR-IQA 메트릭 계산 클래스"""

    # ── 블러/선명도 ──────────────────────────────────────────────────────────

    @staticmethod
    def calculate_laplacian_variance(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    @staticmethod
    def calculate_tenengrad(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(gx**2 + gy**2)
        thr = np.percentile(mag, 90)
        return float(np.sum(mag[mag > thr] ** 2))

    @staticmethod
    def calculate_brenner_gradient(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        diff = gray[2:, :].astype(float) - gray[:-2, :].astype(float)
        return float(np.sum(diff**2))

    @staticmethod
    def calculate_fft_blur_score(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        fft_shift = np.fft.fftshift(np.fft.fft2(gray))
        mag = np.abs(fft_shift)
        rows, cols = gray.shape
        y, x = np.ogrid[:rows, :cols]
        dist = np.sqrt((x - cols // 2)**2 + (y - rows // 2)**2)
        mask = dist > min(rows, cols) // 4
        return float(np.mean(mag[mask]))

    @staticmethod
    def calculate_cpbd(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        edges = cv2.Canny(gray, 50, 150)
        return float(np.sum(edges > 0) / (gray.shape[0] * gray.shape[1]))

    # ── 노이즈 ───────────────────────────────────────────────────────────────

    @staticmethod
    def calculate_noise_estimate_mad(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        return float(np.median(np.abs(lap)) / 0.6745)

    @staticmethod
    def calculate_noise_gaussian_blur_diff(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return float(np.mean(cv2.absdiff(gray, blurred)))

    @staticmethod
    def calculate_snr(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        noise = np.std(gray)
        return float("inf") if noise == 0 else float(20 * np.log10(np.mean(gray) / noise))

    # ── 대비/색상 ─────────────────────────────────────────────────────────────

    @staticmethod
    def calculate_rms_contrast(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        return float(np.sqrt(np.mean((gray - np.mean(gray))**2)))

    @staticmethod
    def calculate_michelson_contrast(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        i_max, i_min = float(np.max(gray)), float(np.min(gray))
        return 0.0 if i_max + i_min == 0 else (i_max - i_min) / (i_max + i_min)

    @staticmethod
    def calculate_colorfulness(img: np.ndarray) -> float:
        if len(img.shape) != 3:
            return 0.0
        B, G, R = cv2.split(img.astype("float"))
        rg = np.absolute(R - G)
        yb = np.absolute(0.5 * (R + G) - B)
        return float(np.sqrt(np.std(rg)**2 + np.std(yb)**2) + 0.3 * np.sqrt(np.mean(rg)**2 + np.mean(yb)**2))

    @staticmethod
    def calculate_saturation(img: np.ndarray) -> float:
        if len(img.shape) != 3:
            return 0.0
        return float(np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1] / 255.0))

    @staticmethod
    def calculate_brightness(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        return float(np.mean(gray))

    @staticmethod
    def calculate_dynamic_range(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        return float(np.max(gray) - np.min(gray))

    # ── 통계 ─────────────────────────────────────────────────────────────────

    @staticmethod
    def calculate_entropy(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist / np.sum(hist)
        hist = hist[hist > 0]
        return float(-np.sum(hist * np.log2(hist)))

    @staticmethod
    def calculate_histogram_uniformity(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist / np.sum(hist)
        return float(1.0 - np.sum(np.abs(hist - np.ones(256) / 256)) / 2.0)

    # ── 고급 NR-IQA ──────────────────────────────────────────────────────────

    @staticmethod
    def calculate_brisque(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        sharpness = min(100, max(0, 100 - cv2.Laplacian(gray, cv2.CV_64F).var() / 10))
        contrast = min(100, max(0, 100 - float(gray.std())))
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = min(100, float(cv2.absdiff(gray, blur).mean()) * 10)
        return float(sharpness * 0.5 + contrast * 0.3 + noise * 0.2)

    @staticmethod
    def calculate_niqe_simple(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        mu = cv2.GaussianBlur(gray.astype(float), (7, 7), 1.5)
        sigma = np.sqrt(cv2.GaussianBlur((gray.astype(float) - mu)**2, (7, 7), 1.5))
        dist = np.sqrt((np.mean(mu) - 127.5)**2 + (np.mean(sigma) - 50.0)**2)
        return float(min(100, dist / 2))

    @staticmethod
    def calculate_piqe_simple(img: np.ndarray) -> float:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        h, w = gray.shape
        bs = 16
        distortions = []
        for i in range(0, h - bs, bs):
            for j in range(0, w - bs, bs):
                blk = gray[i:i+bs, j:j+bs]
                if np.var(blk) > 100:
                    gx = cv2.Sobel(blk, cv2.CV_64F, 1, 0, ksize=3)
                    gy = cv2.Sobel(blk, cv2.CV_64F, 0, 1, ksize=3)
                    distortions.append(100 - min(100, float(np.mean(np.sqrt(gx**2 + gy**2)))))
        return float(np.mean(distortions)) if distortions else 50.0

    @staticmethod
    def classify_quality(score: float) -> str:
        if score >= 0.8: return "A"
        if score >= 0.6: return "B"
        if score >= 0.4: return "C"
        if score >= 0.2: return "D"
        return "F"


def _calc_nr_metrics(img: np.ndarray, include_hsmb: bool, hsmb_params: Dict) -> Dict:
    """단일 이미지의 모든 NR-IQA 메트릭 계산"""
    iqa = ImageQualityAssessment()
    result = {
        "laplacian_variance": iqa.calculate_laplacian_variance(img),
        "tenengrad":          iqa.calculate_tenengrad(img),
        "brenner_gradient":   iqa.calculate_brenner_gradient(img),
        "fft_blur_score":     iqa.calculate_fft_blur_score(img),
        "cpbd":               iqa.calculate_cpbd(img),
        "noise_mad":          iqa.calculate_noise_estimate_mad(img),
        "noise_gaussian_diff":iqa.calculate_noise_gaussian_blur_diff(img),
        "snr":                iqa.calculate_snr(img),
        "rms_contrast":       iqa.calculate_rms_contrast(img),
        "michelson_contrast": iqa.calculate_michelson_contrast(img),
        "colorfulness":       iqa.calculate_colorfulness(img),
        "saturation":         iqa.calculate_saturation(img),
        "brightness":         iqa.calculate_brightness(img),
        "dynamic_range":      iqa.calculate_dynamic_range(img),
        "entropy":            iqa.calculate_entropy(img),
        "histogram_uniformity": iqa.calculate_histogram_uniformity(img),
        "brisque":            iqa.calculate_brisque(img),
        "niqe_simple":        iqa.calculate_niqe_simple(img),
        "piqe_simple":        iqa.calculate_piqe_simple(img),
    }
    if include_hsmb:
        p = hsmb_params or {}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        result["hsmb"] = _calc_hsmb_from_array(
            gray,
            block_size=p.get("block_size", 64),
            threshold_ratio=p.get("threshold_ratio", 0.3),
            beta=p.get("beta", 1.8),
            edge_weight=p.get("edge_weight", 0.8),
            direction=p.get("direction", "four"),
        )
    brisque_n = max(0, 1 - result["brisque"] / 100)
    lap_n     = min(1, result["laplacian_variance"] / 500)
    noise_n   = max(0, 1 - result["noise_mad"] / 50)
    ws = 0.3 * brisque_n + 0.3 * result["cpbd"] + 0.2 * lap_n + 0.2 * noise_n
    result["weighted_score"] = round(float(ws), 4)
    result["quality_grade"]  = iqa.classify_quality(ws)
    return result


# ################################################################################
# ── HSMB (oais.iqa.hsmb 인라인) ──────────────────────────────────────────────
# ################################################################################

class _HSMBCalculator:
    LAPLACIAN_NORM   = 800.0
    FFT_NORM         = 1200000.0
    ADJ_BASELINE     = 0.5
    HSMB_ADJ_FACTOR  = 0.1
    FFT_ADJ_FACTOR   = 0.05
    CONTRAST_EXP     = 0.25
    SCORE_MIN        = 0.1
    SCORE_SCALE      = 0.85

    def __init__(self, block_size=64, threshold_ratio=0.3, beta=1.8,
                 edge_weight=0.8, direction="four", noise_threshold=5.0, use_clahe=True):
        self.block_size      = block_size
        self.threshold_ratio = threshold_ratio
        self.beta            = beta
        self.edge_weight     = edge_weight
        self.direction       = direction
        self.noise_threshold = noise_threshold
        self.use_clahe       = use_clahe

    def _preprocess(self, gray: np.ndarray) -> np.ndarray:
        if self.use_clahe:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray.astype(np.uint8))
        else:
            enhanced = gray.astype(np.uint8)
        return cv2.GaussianBlur(enhanced.astype(np.float32), (3, 3), 0.5)

    def _gradient_magnitude(self, blk: np.ndarray) -> np.ndarray:
        sx = cv2.Scharr(blk, cv2.CV_32F, 1, 0)
        sy = cv2.Scharr(blk, cv2.CV_32F, 0, 1)
        mag = cv2.magnitude(sx, sy)
        mag[mag < self.noise_threshold] = 0
        return mag

    def _edge_pixels(self, mag: np.ndarray) -> np.ndarray:
        mu, sigma = np.mean(mag), np.std(mag)
        thr = (mu + sigma * 0.5) * self.edge_weight
        return np.argwhere(mag > thr)

    def _edge_dir(self, blk: np.ndarray, r: int, c: int) -> Tuple[int, int]:
        h, w = blk.shape
        dirs = [(-1,0),(1,0),(0,-1),(0,1)] if self.direction == "four" else \
               [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        center = float(blk[r, c])
        best, best_dir = -1, (0, 0)
        for dr, dc in dirs:
            rr, cc = r+dr, c+dc
            if 0 <= rr < h and 0 <= cc < w:
                d = abs(float(blk[rr, cc]) - center)
                if d > best:
                    best, best_dir = d, (dr, dc)
        return best_dir

    def _edge_profile(self, blk: np.ndarray, r, c, dr, dc, length=10) -> np.ndarray:
        h, w = blk.shape
        profile = []
        for i in range(length):
            rr, cc = r + dr*i, c + dc*i
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
                d_prev = abs(profile[i-1] - center)
                if abs(d_cur - d_prev) < 1e-9:
                    return float(i)
                t = (thr - d_prev) / (d_cur - d_prev)
                return (i - 1) + t
        return float(len(profile))

    def calculate_from_array(self, gray: np.ndarray) -> float:
        preprocessed = self._preprocess(gray)
        h, w = preprocessed.shape
        n_row, n_col = h // self.block_size, w // self.block_size
        hist = np.zeros(101, dtype=np.float32)
        total_edges = 0
        total_lap, total_fft = 0.0, 0.0

        for br in range(n_row):
            for bc in range(n_col):
                rs, cs = br * self.block_size, bc * self.block_size
                blk = preprocessed[rs:rs+self.block_size, cs:cs+self.block_size]
                mag = self._gradient_magnitude(blk)
                # laplacian var
                lap_var = float(cv2.Laplacian(blk.astype(np.uint8), cv2.CV_64F).var())
                # fft high freq energy
                fs = np.fft.fftshift(np.fft.fft2(blk))
                bh, bw = blk.shape
                ch, cw = bh//2, bw//2
                mask = np.zeros((bh, bw))
                mask[:ch//2, :] = 1; mask[ch+ch//2:, :] = 1
                mask[:, :cw//2] = 1; mask[:, cw+cw//2:] = 1
                fft_e = float(np.sum(np.abs(fs) * mask))
                total_lap += lap_var
                total_fft += fft_e

                for r_loc, c_loc in self._edge_pixels(mag):
                    dr, dc = self._edge_dir(blk, r_loc, c_loc)
                    if (dr, dc) == (0, 0):
                        continue
                    profile = self._edge_profile(blk, r_loc, c_loc, dr, dc)
                    ew = self._edge_width(profile)
                    if ew is not None:
                        p_blur = 1 - np.exp(-(abs(ew / 3.0) ** self.beta))
                        idx = min(int(round(float(p_blur) * 100)), 100)
                        hist[idx] += 1
                        total_edges += 1

        n_blks = n_row * n_col or 1
        pdf = hist / total_edges if total_edges > 0 else np.zeros(101)
        base_hsmb = float(np.cumsum(pdf)[63])
        lap_score = min(1.0, (total_lap / n_blks) / self.LAPLACIAN_NORM)
        fft_score = min(1.0, (total_fft / n_blks) / self.FFT_NORM)

        sharpness = 1 - base_hsmb
        score = lap_score \
            + (sharpness - self.ADJ_BASELINE) * self.HSMB_ADJ_FACTOR \
            + (fft_score  - self.ADJ_BASELINE) * self.FFT_ADJ_FACTOR
        score = np.clip(score, 0.0, 1.0) ** self.CONTRAST_EXP
        score = np.clip(self.SCORE_MIN + score * self.SCORE_SCALE, 0.0, 1.0)
        return round(float(score), 4)


def _calc_hsmb_from_array(gray: np.ndarray, block_size=64, threshold_ratio=0.3,
                           beta=1.8, edge_weight=0.8, direction="four",
                           noise_threshold=5.0, use_clahe=True) -> float:
    return _HSMBCalculator(
        block_size=block_size, threshold_ratio=threshold_ratio,
        beta=beta, edge_weight=edge_weight, direction=direction,
        noise_threshold=noise_threshold, use_clahe=use_clahe,
    ).calculate_from_array(gray)


# ################################################################################
# ── DL-IQA (oais.iqa.dl_iqa 인라인) ──────────────────────────────────────────
# ################################################################################

class DeepLearningIQA:
    """PyIQA 기반 딥러닝 IQA: DBCNN + ARNIQA (0~1, 높을수록 좋음)"""

    SUPPORTED_METRICS = ["dbcnn", "arniqa"]
    DEFAULT_MAX_SIZE = 2048

    def __init__(self, device=None, max_size=DEFAULT_MAX_SIZE):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        elif device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA 미사용 가능 → CPU로 폴백")
            self.device = "cpu"
        else:
            self.device = device
        self.max_size = max_size
        self.metrics_cache = {}
        print(f"DeepLearningIQA device: {self.device}")
        if self.device == "cuda":
            try:
                print(f"  GPU: {torch.cuda.get_device_name(0)}")
            except Exception:
                pass

    def _load_model(self, metric_name: str):
        if metric_name in self.metrics_cache:
            return self.metrics_cache[metric_name]
        print(f"  모델 로드: {metric_name}...")
        model = _pyiqa_lib.create_metric(metric_name, device=self.device)
        self.metrics_cache[metric_name] = model
        return model

    def _preprocess(self, image_path: str) -> "torch.Tensor":
        img = _PILImage.open(image_path).convert("RGB")
        if img.width > self.max_size or img.height > self.max_size:
            img.thumbnail((self.max_size, self.max_size), _PILImage.Resampling.LANCZOS)
        tensor = _tv_transforms.ToTensor()(img).unsqueeze(0)
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                tensor = tensor.cuda()
            except Exception:
                self.device = "cpu"
        return tensor

    def evaluate_multiple_metrics(self, image_path: str, metric_names=None) -> Dict:
        if metric_names is None:
            metric_names = self.SUPPORTED_METRICS
        results = {}
        try:
            tensor = self._preprocess(image_path)
            for name in metric_names:
                try:
                    model = self._load_model(name)
                    with torch.no_grad():
                        score = model(tensor)
                    results[name] = round(float(score.item()), 4)
                except Exception:
                    results[name] = -1.0
            if self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()
        except RuntimeError as e:
            if "CUDA" in str(e):
                self.device = "cpu"
                self.metrics_cache.clear()
                return self.evaluate_multiple_metrics(image_path, metric_names)
            for name in metric_names:
                results[name] = -1.0
        except Exception:
            for name in metric_names:
                results[name] = -1.0
        return results

    def clear_cache(self):
        self.metrics_cache.clear()
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass


# ################################################################################
# ── FR-IQA (oais.iqa.fr_iqa 인라인) ──────────────────────────────────────────
# ################################################################################

def _calc_ssim(img1: np.ndarray, img2: np.ndarray, full: bool = False):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    min_sz = min(img1.shape[0], img1.shape[1])
    win_size = max(3, (min_sz if min_sz % 2 == 1 else min_sz - 1)) if min_sz < 7 else 7
    return _ssim_func(img1, img2, multichannel=True, win_size=win_size, channel_axis=2, full=full)


def _calc_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return float(_psnr_func(img1, img2))


def _calc_mse(img1: np.ndarray, img2: np.ndarray) -> float:
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return float(np.mean((img1.astype(float) - img2.astype(float))**2))


def _calc_mae(img1: np.ndarray, img2: np.ndarray) -> float:
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    return float(np.mean(np.abs(img1.astype(float) - img2.astype(float))))


def _calc_uqi(img1: np.ndarray, img2: np.ndarray, window_size: int = 8) -> float:
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    i1, i2 = img1.astype(np.float64), img2.astype(np.float64)
    mu1 = cv2.blur(i1, (window_size, window_size))
    mu2 = cv2.blur(i2, (window_size, window_size))
    s1  = cv2.blur(i1**2, (window_size, window_size)) - mu1**2
    s2  = cv2.blur(i2**2, (window_size, window_size)) - mu2**2
    s12 = cv2.blur(i1*i2, (window_size, window_size)) - mu1*mu2
    num = 4 * s12 * mu1 * mu2
    den = (s1 + s2) * (mu1**2 + mu2**2)
    uqi_map = np.ones_like(i1)
    mask = den != 0
    uqi_map[mask] = num[mask] / den[mask]
    return float(np.mean(uqi_map))


def _calc_ms_ssim(ref: np.ndarray, dist: np.ndarray, data_range: int = 255) -> float:
    weights = [0.0448, 0.2856, 0.3001, 0.2363, 0.1333]
    if ref.shape != dist.shape:
        dist = cv2.resize(dist, (ref.shape[1], ref.shape[0]))
    r, d = ref.copy().astype(np.float64), dist.copy().astype(np.float64)
    vals = []
    for i, w in enumerate(weights):
        kw = {"channel_axis": 2, "data_range": data_range} if len(r.shape) == 3 else {"data_range": data_range}
        vals.append(_ssim_func(r, d, **kw))
        if i < len(weights) - 1:
            r = cv2.resize(r, (r.shape[1]//2, r.shape[0]//2))
            d = cv2.resize(d, (d.shape[1]//2, d.shape[0]//2))
            if r.shape[0] < 16 or r.shape[1] < 16:
                break
    return float(np.prod([v**w for v, w in zip(vals, weights[:len(vals)])]))


def _calc_fr_iqa(ref_img: np.ndarray, test_img: np.ndarray) -> dict:
    if ref_img.shape != test_img.shape:
        test_img = cv2.resize(test_img, (ref_img.shape[1], ref_img.shape[0]))
    ssim_score, ssim_map = _calc_ssim(ref_img, test_img, full=True)
    psnr_score = _calc_psnr(ref_img, test_img)
    mse_score  = _calc_mse(ref_img, test_img)
    mae_score  = _calc_mae(ref_img, test_img)
    uqi_score  = _calc_uqi(ref_img, test_img)
    ws = 0.4 * max(0, min(1, ssim_score)) + 0.35 * min(1, psnr_score / 50) + 0.25 * max(0, min(1, uqi_score))
    grade = "A" if ws >= 0.8 else "B" if ws >= 0.6 else "C" if ws >= 0.4 else "D" if ws >= 0.2 else "F"
    return {
        "ssim": float(ssim_score), "psnr": float(psnr_score),
        "mse": float(mse_score),   "mae": float(mae_score),
        "uqi": float(uqi_score),   "weighted_score": float(ws),
        "grade": grade,            "ssim_map": ssim_map,
    }


# ################################################################################
# ── Metadata (oais.iqa.metadata 인라인) ──────────────────────────────────────
# ################################################################################

def _make_nr_desc_df() -> pd.DataFrame:
    rows = [
        ("laplacian_variance",  "라플라시안 분산",     "Laplacian Variance",            "높을수록 선명", "0~inf",   "sharpness"),
        ("tenengrad",           "테넨그라드",          "Tenengrad",                     "높을수록 선명", "0~inf",   "sharpness"),
        ("brenner_gradient",    "브레너 그래디언트",    "Brenner Gradient",              "높을수록 선명", "0~inf",   "sharpness"),
        ("fft_blur_score",      "FFT 블러 스코어",      "FFT Blur Score",                "높을수록 선명", "0~1",     "sharpness"),
        ("cpbd",                "CPBD",                "Cumul. Prob. of Blur Detection", "높을수록 선명", "0~1",     "sharpness"),
        ("noise_mad",           "노이즈 MAD",           "Noise MAD",                     "낮을수록 좋음", "0~inf",   "noise"),
        ("noise_gaussian_diff", "가우시안 차이 노이즈",  "Gaussian Difference Noise",     "낮을수록 좋음", "0~inf",   "noise"),
        ("snr",                 "SNR",                 "Signal-to-Noise Ratio",         "높을수록 좋음", "dB",      "noise"),
        ("rms_contrast",        "RMS 대비",             "RMS Contrast",                  "높을수록 대비 높음", "0~127.5", "contrast"),
        ("michelson_contrast",  "마이켈슨 대비",         "Michelson Contrast",            "높을수록 대비 높음", "0~1", "contrast"),
        ("colorfulness",        "색상 풍부도",           "Colorfulness",                  "높을수록 풍부", "0~inf",   "color"),
        ("saturation",          "평균 채도",             "Saturation",                    "높을수록 색 선명", "0~1",  "color"),
        ("brightness",          "평균 밝기",             "Brightness",                    "0~255, 중간값 적정", "0~255","brightness"),
        ("dynamic_range",       "다이나믹 레인지",        "Dynamic Range",                 "높을수록 다양", "0~255",  "information"),
        ("entropy",             "엔트로피",              "Entropy",                       "높을수록 정보량 많음", "0~8", "information"),
        ("histogram_uniformity","히스토그램 균일도",      "Histogram Uniformity",          "높을수록 균일", "0~1",    "information"),
        ("brisque",             "BRISQUE",              "BRISQUE",                       "낮을수록 좋음", "0~100",  "perceptual"),
        ("niqe_simple",         "NIQE (간이)",           "NIQE (Simplified)",             "낮을수록 좋음", "0~inf",  "perceptual"),
        ("piqe_simple",         "PIQE (간이)",           "PIQE (Simplified)",             "낮을수록 좋음", "0~100",  "perceptual"),
        ("hsmb",                "HSMB",                "Hybrid Sharpness Metric Based", "높을수록 선명", "0~1",    "hybrid"),
        ("weighted_score",      "종합 점수",             "Weighted Score",                "높을수록 좋음", "0~1",    "composite"),
        ("quality_grade",       "품질 등급",             "Quality Grade",                 "A>B>C>D>F",    "A~F",    "composite"),
        ("dl_dbcnn",            "DBCNN (딥러닝)",        "Deep Bilinear CNN",             "높을수록 좋음", "0~1",    "deep_learning"),
        ("dl_arniqa",           "ARNIQA (딥러닝)",       "Advanced RN-IQA",               "높을수록 좋음", "0~1",    "deep_learning"),
    ]
    return pd.DataFrame(rows, columns=["metric", "name_ko", "name_en", "interpretation", "range", "category"])


def _make_fr_desc_df(metrics: List[str] = None) -> pd.DataFrame:
    all_rows = {
        "ssim":     ("SSIM",    "Structural Similarity Index",     "높을수록 유사 (1=동일)", "-1~1"),
        "psnr":     ("PSNR",    "Peak Signal-to-Noise Ratio",      "높을수록 좋음 (30dB↑ 우수)", "0~inf dB"),
        "mse":      ("MSE",     "Mean Squared Error",              "낮을수록 유사 (0=동일)", "0~inf"),
        "mae":      ("MAE",     "Mean Absolute Error",             "낮을수록 유사 (0=동일)", "0~255"),
        "uqi":      ("UQI",     "Universal Quality Index",         "높을수록 유사 (1=동일)", "-1~1"),
        "ms_ssim":  ("MS-SSIM", "Multi-Scale SSIM",                "높을수록 유사", "0~1"),
        "weighted_score": ("종합점수", "FR Weighted Score",         "높을수록 좋음", "0~1"),
        "grade":    ("등급",    "FR Grade",                        "A>B>C>D>F", "A~F"),
    }
    target = metrics or list(all_rows.keys())
    records = [
        {"메트릭": m, "전체명": all_rows[m][1], "타입": "FR-IQA",
         "값의 의미": all_rows[m][2], "값 범위": all_rows[m][3]}
        for m in target if m in all_rows
    ]
    return pd.DataFrame(records)


# ################################################################################
# IO
# ################################################################################
output_dir = make_output_dir(os.path.join(project_root, "data"), prefix, rmfolder="n")

print(f"\n{'='*60}")
print("설정 정보")
print(f"{'='*60}")
print(f"입력 디렉토리  : {CONFIG['io']['input_dir']}")
print(f"출력 디렉토리  : {output_dir}")
print(f"NR-IQA HSMB  : {CONFIG['nr_iqa']['include_hsmb']}")
print(f"DL-IQA 활성   : {CONFIG['dl_iqa']['enabled']} (DBCNN + ARNIQA, available={_DL_AVAILABLE})")
print(f"FR-IQA 활성   : {CONFIG['fr_iqa']['enabled']}")
print(f"병렬 처리     : {CONFIG['processing']['parallel']} (워커: {max_workers})")
print(f"{'='*60}")

input_dir  = os.path.join(project_root, CONFIG["io"]["input_dir"])
EXTENSIONS = CONFIG["io"]["extensions"]

sub_dirs = sorted([
    d for d in os.listdir(input_dir)
    if os.path.isdir(os.path.join(input_dir, d)) and not d.startswith(".")
])
print(f"처리할 디렉토리: {len(sub_dirs)}개")
print(f"총 파일 수     : {count_files_by_extensions(input_dir, EXTENSIONS)}")


# ################################################################################
# Function
# ################################################################################

def _speed0_ref_path(sub_dir: str, fname: str, base_input_dir: str) -> Optional[str]:
    """sub_dir의 마지막 _XX를 _00으로 치환한 참조 이미지 경로 반환. 없으면 None."""
    parts = sub_dir.rsplit("_", 1)
    if len(parts) != 2:
        return None
    ref_dir_name = parts[0] + "_00"
    ref_path = os.path.join(base_input_dir, ref_dir_name, fname)
    return ref_path if os.path.exists(ref_path) else None


def process_single_image(args: tuple) -> dict:
    """
    단일 이미지에 대해 NR-IQA + FR-IQA 통합 계산 (멀티프로세싱용)

    args:
        ref_path (str|None) : 원본 이미지 경로. None = FR 스킵 (원본 디렉토리)
        dist_path (str)     : 평가 대상 이미지 경로
        sub_dir (str)       : 서브디렉토리 이름
        idx (int)           : 정렬 인덱스
        hsmb_params (dict)  : HSMB 파라미터
        include_hsmb (bool) : HSMB 포함 여부
        fr_enabled (bool)   : FR-IQA 활성 여부
        include_ms_ssim (bool): MS-SSIM 포함 여부
    """
    ref_path, dist_path, sub_dir, idx, hsmb_params, include_hsmb, fr_enabled, include_ms_ssim = args

    result = {"idx": idx, "sub_dir": sub_dir, "fnm": os.path.basename(dist_path)}

    dist_img = cv2.imread(dist_path)
    if dist_img is None:
        result["load_error"] = True
        return result

    # NR-IQA
    try:
        result.update(_calc_nr_metrics(dist_img, include_hsmb, hsmb_params))
    except Exception as e:
        result["nr_error"] = str(e)

    # FR-IQA
    if fr_enabled and ref_path is not None and ref_path != dist_path:
        ref_img = cv2.imread(ref_path)
        if ref_img is not None:
            try:
                fr = _calc_fr_iqa(ref_img, dist_img)
                fr.pop("ssim_map", None)
                for k, v in fr.items():
                    result[f"fr_{k}"] = v
                if include_ms_ssim:
                    result["fr_ms_ssim"] = round(float(_calc_ms_ssim(ref_img, dist_img)), 4)
            except Exception as e:
                result["fr_error"] = str(e)

    return result


def _insert_histogram_to_xlsx(df: pd.DataFrame, sub_dir: str, metric: str,
                               xlsx_path: str, cell: str) -> None:
    import tempfile
    from openpyxl import load_workbook
    from openpyxl.drawing.image import Image as XLImage

    col_data = df.loc[df["sub_dir"] == sub_dir, metric].dropna()
    if col_data.empty:
        return

    plt.figure(figsize=(6, 4))
    range_01 = metric in ("fr_ssim", "fr_ms_ssim", "fr_uqi", "weighted_score")
    if range_01:
        plt.hist(col_data, bins=50, range=(0, 1), edgecolor="black", alpha=0.7)
    else:
        plt.hist(col_data, bins=50, edgecolor="black", alpha=0.7)
    plt.title(f"{sub_dir} — {metric}")
    plt.xlabel(metric)
    plt.ylabel("Frequency")

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".png")
    os.close(tmp_fd)
    plt.savefig(tmp_path, format="png", bbox_inches="tight")
    plt.close()

    wb = load_workbook(xlsx_path)
    ws = wb.active
    ws.add_image(XLImage(tmp_path), cell)
    wb.save(xlsx_path)
    os.unlink(tmp_path)


# ################################################################################
# Main
# ################################################################################

def main():
    print(f"\n{'='*60}")
    print("NR+FR 통합 IQA 계산 시작")
    print(f"{'='*60}")

    hsmb_params  = CONFIG["nr_iqa"]["hsmb"]
    include_hsmb = CONFIG["nr_iqa"]["include_hsmb"]
    fr_enabled   = CONFIG["fr_iqa"]["enabled"]
    inc_ms_ssim  = CONFIG["fr_iqa"]["include_ms_ssim"]

    # 작업 목록 구성 — FR-IQA 기준: 같은 조건 그룹의 속도 _00 디렉토리
    all_tasks = []
    for sub_dir in sub_dirs:
        sub_dir_path = os.path.join(input_dir, sub_dir)
        img_files = sorted([
            f for f in glob.glob(os.path.join(sub_dir_path, "*"))
            if f.lower().rsplit(".", 1)[-1] in EXTENSIONS
        ])
        is_speed0 = sub_dir.endswith("_00")
        for img_path in img_files:
            fname = os.path.basename(img_path)
            if fr_enabled and not is_speed0:
                use_ref = _speed0_ref_path(sub_dir, fname, input_dir)
            else:
                use_ref = None  # 속도 0 디렉토리는 FR 기준 자신 → 스킵
            all_tasks.append((use_ref, img_path, sub_dir, len(all_tasks),
                              hsmb_params, include_hsmb, fr_enabled, inc_ms_ssim))

    print(f"총 처리할 이미지: {len(all_tasks)}개")

    # 처리
    all_results = []
    if CONFIG["processing"]["parallel"]:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_single_image, t): t for t in all_tasks}
            for future in tqdm(as_completed(futures), total=len(all_tasks), desc="통합 IQA"):
                try:
                    all_results.append(future.result())
                except Exception as e:
                    print(f"처리 오류: {e}")
    else:
        for task in tqdm(all_tasks, desc="통합 IQA"):
            all_results.append(process_single_image(task))

    all_results.sort(key=lambda x: x.get("idx", 0))

    # DL-IQA (순차 처리 — 모델을 1회만 로드해 재사용)
    dl_enabled = CONFIG["dl_iqa"]["enabled"]
    if dl_enabled and _DL_AVAILABLE:
        print(f"\n{'='*60}")
        print("DL-IQA 계산 (DBCNN + ARNIQA)")
        print(f"{'='*60}")
        dl = DeepLearningIQA(device=CONFIG["dl_iqa"]["device"])
        idx_to_pos = {r.get("idx", i): i for i, r in enumerate(all_results)}
        for task in tqdm(all_tasks, desc="DL-IQA"):
            _, dist_path, _, idx, *_ = task
            dl_scores = dl.evaluate_multiple_metrics(dist_path)
            pos = idx_to_pos.get(idx)
            if pos is not None:
                all_results[pos]["dl_dbcnn"]  = dl_scores.get("dbcnn",  -1.0)
                all_results[pos]["dl_arniqa"] = dl_scores.get("arniqa", -1.0)
        dl.clear_cache()
    elif dl_enabled and not _DL_AVAILABLE:
        print("[경고] torch/pyiqa 미설치 → DL-IQA 스킵 (uv add torch pyiqa)")

    rlt_df = pd.DataFrame(all_results)
    drop_cols = [c for c in ["idx", "load_error", "nr_error", "fr_error"] if c in rlt_df.columns]
    rlt_df.drop(columns=drop_cols, inplace=True)
    print(f"처리 완료: {len(rlt_df)}개 | 컬럼: {len(rlt_df.columns)}개")

    # ############################################################################
    # Save
    # ############################################################################
    print(f"\n{'='*60}")
    print("결과 저장")
    print(f"{'='*60}")

    out_all   = os.path.join(output_dir, f"01_전체데이터_{dsr}.xlsx")
    out_stats = os.path.join(output_dir, f"02_그룹별통계_{dsr}.xlsx")
    out_means = os.path.join(output_dir, f"03_그룹별평균_{dsr}.xlsx")

    skip_cols = {"sub_dir", "fnm", "quality_grade", "fr_grade"}
    num_cols  = [c for c in rlt_df.columns if c not in skip_cols]

    stats_df  = rlt_df.groupby("sub_dir")[num_cols].agg(["mean", "std", "min", "max"]).round(4)
    means_df  = rlt_df.groupby("sub_dir")[num_cols].mean().round(4)
    best      = {c: means_df[c].idxmax() for c in means_df.columns if means_df[c].notna().any()}
    means_df  = pd.concat([means_df, pd.DataFrame([best], index=["best_group"])])

    with pd.ExcelWriter(out_all, engine="openpyxl") as w:
        rlt_df.to_excel(w, sheet_name="전체데이터", index=False)
        _make_nr_desc_df().to_excel(w, sheet_name="NR메트릭설명", index=False)
        _make_fr_desc_df(["ssim", "psnr", "mse", "mae", "uqi", "ms_ssim"]).to_excel(w, sheet_name="FR메트릭설명", index=False)

    with pd.ExcelWriter(out_stats, engine="openpyxl") as w:
        stats_df.to_excel(w, sheet_name="그룹별통계", index=True)

    with pd.ExcelWriter(out_means, engine="openpyxl") as w:
        means_df.to_excel(w, sheet_name="그룹별평균", index=True)

    if CONFIG["output"]["save_histograms"]:
        key_metrics = CONFIG["output"]["key_nr_metrics"] + (
            CONFIG["output"]["key_fr_metrics"] if fr_enabled else []
        )
        key_metrics = [m for m in key_metrics if m in rlt_df.columns]
        print(f"히스토그램: {key_metrics}")
        for i, sd in enumerate(tqdm(sub_dirs, desc="히스토그램")):
            for j, metric in enumerate(key_metrics):
                try:
                    _insert_histogram_to_xlsx(rlt_df, sd, metric, out_stats,
                                              f"{chr(65 + j * 9)}{(i + 1) * 20}")
                except Exception as e:
                    print(f"히스토그램 오류 ({sd}, {metric}): {e}")

    dl_cols = [c for c in rlt_df.columns if c.startswith("dl_")]
    fr_cols = [c for c in rlt_df.columns if c.startswith("fr_")]
    nr_cols = [c for c in rlt_df.columns if not c.startswith("fr_") and not c.startswith("dl_") and c not in skip_cols]
    print(f"출력: {out_all}")
    print(f"      {out_stats}")
    print(f"      {out_means}")
    speed0_dirs = [d for d in sub_dirs if d.endswith("_00")]
    print(f"FR기준(속도_00): {len(speed0_dirs)}개 | 그룹: {len(sub_dirs)}개 | NR: {len(nr_cols)}개 | DL: {len(dl_cols)}개 | FR: {len(fr_cols)}개")

    # ############################################################################
    # Finish
    # ############################################################################
    etime = time.time()
    print(f"\n{prefix}_{workname} finished in {etime - stime:.2f} seconds")
    return rlt_df


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
