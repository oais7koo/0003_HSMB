# -*- coding: utf-8 -*-
# ################################################################################
# Title: HSMB v1 재계산 (ps2000 결과의 hsmb 컬럼만 v1으로 교체)
# Author: oaiskoo
# Date: 2026.04.28
# Version: v01
# Goal: ps2000 통합 IQA 결과를 그대로 가져와 hsmb 컬럼만 ps5010 v1 알고리즘으로 재계산
# Changes:
#   - v01: 초기 버전 — ps2000 산출물을 입력으로 받아 hsmb v1 결과로 교체
# Description:
#   - 입력: ps2000의 01/02/03 xlsx (data/ps2000/) — 기존 NR+DL+FR-IQA 결과
#   - HSMB 알고리즘: ps5010 v1 (threshold_ratio=0.1, p_beta=2, p_edge_weight=1.5)
#     · d0900 검증으로 확정된 파일1(`MTF(15000)-IQA 지표.xlsx`)의 산출 알고리즘
#   - hsmb 컬럼만 교체 → 그룹별 통계/평균을 재계산해 ps2000과 동일한 형식으로 저장
#   - 다른 IQA 지표(NR-23, DL-2, FR-6)는 ps2000 값을 그대로 유지
#   - 멀티프로세싱 + 한글 경로 대응
# Input:
#   - ./data/ps1204_kict_eSFR/  (이미지 원본, 47개 폴더 × 10 PNG)
#   - ./data/ps2000/01_전체데이터_*.xlsx (재사용 대상)
# Output: ./data/ps2010/01_전체데이터_*.xlsx, 02_그룹별통계_*.xlsx, 03_그룹별평균_*.xlsx
# ################################################################################
# Library
# ################################################################################
import os
import sys
import glob
import time
import datetime
import warnings
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

# Windows 한글 경로 대응 (cv2.imread monkey-patch)
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
warnings.filterwarnings("default")

# ################################################################################
# Parameter
# ################################################################################
CONFIG = {
    "io": {
        "image_dir": "data/ps1204_kict_eSFR",
        "source_dir": "data/ps2000",
        "output_dir": "data/ps2010",
        "extensions": ["bmp", "png", "jpg", "jpeg", "tif", "tiff"],
    },
    "hsmb_v1": {
        # ps5010_HSMB_v1.py 256~266줄 4번째 호출 — d0900 검증 확정 파라미터
        "block_size": 64,
        "threshold_ratio": 0.1,
        "p_beta": 2,
        "p_edge_weight": 1.5,
        "direction": "four",
    },
    "processing": {
        "parallel": True,
        "max_workers": max(1, (os.cpu_count() or 4) - 1),
    },
    "stats": {
        "skip_cols": {"sub_dir", "fnm", "quality_grade", "fr_grade"},
        "round": 4,
    },
}

image_dir = CONFIG["io"]["image_dir"]
source_dir = CONFIG["io"]["source_dir"]
output_dir = CONFIG["io"]["output_dir"]
EXTENSIONS = CONFIG["io"]["extensions"]
HSMB_PARAMS = CONFIG["hsmb_v1"]
os.makedirs(output_dir, exist_ok=True)


# ################################################################################
# Helper
# ################################################################################
def count_files_by_extensions(folder: str, extensions: List[str]) -> int:
    cnt = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().rsplit(".", 1)[-1] in extensions:
                cnt += 1
    return cnt


def _load_latest_xlsx(folder: str, pattern: str) -> str:
    paths = sorted(glob.glob(os.path.join(folder, pattern)))
    if not paths:
        raise FileNotFoundError(f"No xlsx matching '{pattern}' in {folder}")
    return paths[-1]


# ################################################################################
# HSMB v1 Calculator (ps5010_HSMB_v1.py 인라인)
# ################################################################################
class _HSMBv1Calculator:
    """ps5010_HSMB_v1.py 알고리즘 — 원형 HSMB v1.

    파라미터:
      block_size      = 64
      threshold_ratio = 0.1   (edge_width 임계비율)
      p_beta          = 2     (블러 감도)
      p_edge_weight   = 1.5   (edge selection 가중치)
      direction       = "four"
    출력 인덱스: cdf[63] (CPBD 방식 동일)
    """

    W_JNB = 3  # ps5010에서 고정
    PROFILE_LENGTH = 10
    CDF_INDEX = 63

    def __init__(self, block_size=64, threshold_ratio=0.1, p_beta=2,
                 p_edge_weight=1.5, direction="four"):
        self.block_size = block_size
        self.threshold_ratio = float(threshold_ratio)
        self.p_beta = float(p_beta)
        self.p_edge_weight = float(p_edge_weight)
        self.direction = direction

    def _gradient_magnitude(self, blk: np.ndarray) -> np.ndarray:
        sx = cv2.Sobel(blk, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(blk, cv2.CV_32F, 0, 1, ksize=3)
        return cv2.magnitude(sx, sy)

    def _edge_pixels(self, mag: np.ndarray) -> np.ndarray:
        # ps5010 find_strong_edge_pixels: 평균*가중치 이상
        threshold = float(np.mean(mag)) * self.p_edge_weight
        return np.argwhere(mag > threshold)

    def _edge_dir(self, blk: np.ndarray, r: int, c: int) -> Tuple[int, int]:
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

    def calculate_from_path(self, img_path: str) -> float:
        gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {img_path}")
        gray = gray.astype(np.float32)
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
                        p_blur = 1 - np.exp(-abs(ew / self.W_JNB) ** self.p_beta)
                        idx = min(int(round(float(p_blur) * 100)), 100)
                        hist[idx] += 1
                        total_edges += 1

        pdf = hist / total_edges if total_edges > 0 else np.zeros(101)
        cdf = np.cumsum(pdf)
        return round(float(cdf[self.CDF_INDEX]), 4)


def _calc_hsmb_v1(img_path: str, params: Dict) -> float:
    return _HSMBv1Calculator(**params).calculate_from_path(img_path)


# ################################################################################
# Worker (multiprocessing)
# ################################################################################
def _worker_hsmb(task: Tuple[str, str, str, Dict]) -> Tuple[str, str, Optional[float]]:
    sub_dir, fnm, img_path, params = task
    try:
        v = _calc_hsmb_v1(img_path, params)
    except Exception as e:
        print(f"[Worker error] {sub_dir}/{fnm}: {e}")
        v = None
    return sub_dir, fnm, v


# ################################################################################
# Main
# ################################################################################
def main():
    print(f"\n{'='*60}")
    print("HSMB v1 재계산 (ps2000 → ps2010)")
    print(f"{'='*60}")

    # 1) ps2000 결과 로드
    src_01 = _load_latest_xlsx(source_dir, "01_*.xlsx")
    print(f"[Source] {os.path.basename(src_01)}")

    xls = pd.ExcelFile(src_01)
    df01 = pd.read_excel(src_01, sheet_name=0)
    extra_sheets = {
        name: pd.read_excel(src_01, sheet_name=name)
        for name in xls.sheet_names if name != xls.sheet_names[0]
    }
    print(f"[Loaded] 전체데이터: {df01.shape} | 부가시트: {list(extra_sheets.keys())}")

    # 2) 작업 목록 구성
    tasks = []
    for _, row in df01.iterrows():
        sub_dir = row["sub_dir"]
        fnm = row["fnm"]
        img_path = os.path.join(image_dir, sub_dir, fnm)
        if os.path.exists(img_path):
            tasks.append((sub_dir, fnm, img_path, HSMB_PARAMS))
        else:
            print(f"[Missing] {img_path}")
    print(f"[Tasks] {len(tasks)}개 이미지 처리")

    # 3) 병렬 HSMB v1 계산
    n_workers = CONFIG["processing"]["max_workers"]
    print(f"[Workers] {n_workers}")
    results: Dict[Tuple[str, str], float] = {}
    if CONFIG["processing"]["parallel"]:
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = {executor.submit(_worker_hsmb, t): t for t in tasks}
            for fut in tqdm(as_completed(futures), total=len(tasks), desc="HSMB v1"):
                sub_dir, fnm, v = fut.result()
                results[(sub_dir, fnm)] = v
    else:
        for t in tqdm(tasks, desc="HSMB v1"):
            sub_dir, fnm, v = _worker_hsmb(t)
            results[(sub_dir, fnm)] = v

    # 4) hsmb 컬럼 교체
    df01_new = df01.copy()
    df01_new["hsmb"] = df01_new.apply(
        lambda r: results.get((r["sub_dir"], r["fnm"]), r.get("hsmb")), axis=1
    )

    # 5) 그룹별 통계/평균 재계산
    skip_cols = CONFIG["stats"]["skip_cols"]
    rnd = CONFIG["stats"]["round"]
    num_cols = [
        c for c in df01_new.columns
        if c not in skip_cols and pd.api.types.is_numeric_dtype(df01_new[c])
    ]
    stats_df = df01_new.groupby("sub_dir")[num_cols].agg(["mean", "std", "min", "max"]).round(rnd)
    means_df = df01_new.groupby("sub_dir")[num_cols].mean().round(rnd)
    best = {c: means_df[c].idxmax() for c in means_df.columns if means_df[c].notna().any()}
    means_df = pd.concat([means_df, pd.DataFrame([best], index=["best_group"])])

    # 6) 저장
    print(f"\n{'='*60}")
    print("결과 저장")
    print(f"{'='*60}")

    out_all   = os.path.join(output_dir, f"01_전체데이터_{dsr}.xlsx")
    out_stats = os.path.join(output_dir, f"02_그룹별통계_{dsr}.xlsx")
    out_means = os.path.join(output_dir, f"03_그룹별평균_{dsr}.xlsx")

    with pd.ExcelWriter(out_all, engine="openpyxl") as w:
        df01_new.to_excel(w, sheet_name="전체데이터", index=False)
        for name, sdf in extra_sheets.items():
            sdf.to_excel(w, sheet_name=name, index=False)

    with pd.ExcelWriter(out_stats, engine="openpyxl") as w:
        stats_df.to_excel(w, sheet_name="그룹별통계", index=True)

    with pd.ExcelWriter(out_means, engine="openpyxl") as w:
        means_df.to_excel(w, sheet_name="그룹별평균", index=True)

    print(f"출력: {out_all}")
    print(f"      {out_stats}")
    print(f"      {out_means}")

    # 검증 메시지
    sample = df01_new[df01_new["sub_dir"] == "15000lx_0640_500us_00"]
    if not sample.empty:
        print()
        print(f"[검증] 15000lx_0640_500us_00 hsmb v1 평균 = {sample['hsmb'].mean():.4f}  (d0900 target: 0.8893)")

    # ############################################################################
    # Finish
    # ############################################################################
    etime = time.time()
    print(f"\n{prefix}_{workname} finished in {etime - stime:.2f} seconds")
    return df01_new


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
