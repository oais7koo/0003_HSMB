# -*- coding: utf-8 -*-
# ################################################################################
# Title: E1-2 ps1204 BEW-H/V 측정 + NR-IQA 상관 분석
# Author: oaiskoo
# Date: 2026.05.18
# Version: v01
# Goal: 47조건 BEW-H/V 산출 → ps3100 IQA 조건별평균과 PLCC/SROCC/KRCC 상관 분석
# Changes:
#   - v01: 초기 버전
# Description:
#   - BEW 입력: data/ps1204_kict_eSFR/ (47조건, 01.png~10.png)
#   - IQA 입력: data/ps3100/03_조건별평균_*.xlsx (F002-1 산출물)
#   - BEW: common_iqa7.compute_bew_hv() — four-direction BEW-H/V 분리
#   - 상관: common_corr.correlation_matrix() — PLCC/SROCC/KRCC
#   - 체크포인트: 조건 완료 후 저장
# 참조: d9050_상세기획_E1_2_BEW_상관_분석.md, d3100, common_iqa7.compute_bew_hv
# ################################################################################
import argparse
import datetime
import os
import re
import sys
import time
import warnings
from glob import glob
from pathlib import Path

import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_iqa7 as iqa
import common_corr as corr

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
IQA_COLS = ["hsmb", "cpbd", "niqe", "niqe_matlab", "piqe",
            "brisque", "brisque_matlab", "dbcnn", "arniqa"]
BEW_COLS = ["bew_h", "bew_v"]

CONFIG = {
    "io": {
        "image_dir": "data/ps1204_kict_eSFR",
        "iqa_dir":   "data/ps3100",
        "output_dir": "data/ps3101",
        "checkpoint_csv": "data/ps3101/_checkpoint.csv",
    },
}

parser = argparse.ArgumentParser(description="E1-2 BEW-H/V 측정 + NR-IQA 상관분석")
parser.add_argument("--image_dir",       type=str, default=None)
parser.add_argument("--iqa_dir",         type=str, default=None)
parser.add_argument("--output_dir",      type=str, default=None)
parser.add_argument("--checkpoint_csv",  type=str, default=None)
parser.add_argument("--resume", action="store_true", help="체크포인트에서 재개")
args = parser.parse_args()

if args.image_dir:      CONFIG["io"]["image_dir"]      = args.image_dir
if args.iqa_dir:        CONFIG["io"]["iqa_dir"]        = args.iqa_dir
if args.output_dir:     CONFIG["io"]["output_dir"]     = args.output_dir
if args.checkpoint_csv: CONFIG["io"]["checkpoint_csv"] = args.checkpoint_csv

image_dir       = os.path.join(project_root, CONFIG["io"]["image_dir"])
iqa_dir         = os.path.join(project_root, CONFIG["io"]["iqa_dir"])
output_dir      = os.path.join(project_root, CONFIG["io"]["output_dir"])
checkpoint_path = os.path.join(project_root, CONFIG["io"]["checkpoint_csv"])
os.makedirs(output_dir, exist_ok=True)

# ################################################################################
# 한글 차트 설정
# ################################################################################
import platform
os_var = platform.system()
mpl.use("Agg")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11
if os_var == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_var == "Darwin":
    mpl.rc("font", family="AppleGothic")
else:
    plt.rcParams["font.family"] = "NanumGothic"

print(f"\n{'='*60}")
print("설정 정보")
print(f"{'='*60}")
print(f"이미지 디렉토리: {image_dir}")
print(f"IQA 입력 디렉토리: {iqa_dir}")
print(f"출력 디렉토리: {output_dir}")
print(f"{'='*60}")

# ################################################################################
# Function — 조건 파싱 (ps3100과 동일)
# ################################################################################
_COND_RE = re.compile(
    r"^(?P<lux>\d+)lx_(?P<iso>\d+)_(?P<shutter>\d+)us_(?P<speed>\d+)$"
)


def parse_condition(folder_name: str) -> dict:
    m = _COND_RE.match(folder_name)
    if not m:
        return {"lux": None, "iso": None, "shutter_us": None, "speed_kmh": None}
    return {
        "lux": int(m.group("lux")),
        "iso": int(m.group("iso")),
        "shutter_us": int(m.group("shutter")),
        "speed_kmh": int(m.group("speed")),
    }


def collect_conditions(base_dir: str) -> list:
    base = Path(base_dir)
    result, skipped = [], []
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        if parse_condition(d.name)["lux"] is None:
            skipped.append(d.name)
            continue
        result.append((d.name, str(d)))
    if skipped:
        print(f"  [SKIP] 파싱 불가 폴더 {len(skipped)}개: {skipped}")
    return result


def collect_frames(cond_dir: str) -> list:
    return sorted(glob(os.path.join(cond_dir, "*.png")))


def _imread_safe(path: str) -> np.ndarray:
    """한글 경로 대응 cv2 imread."""
    buf = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def save_checkpoint(rows: list, path: str):
    """체크포인트 저장 — 비치명적 (실패 시 경고 후 스킵)."""
    tmp = f"{path}.tmp"
    try:
        pd.DataFrame(rows).to_csv(tmp, index=False, encoding="utf-8-sig", float_format="%.4f")
    except Exception as e:
        print(f"  [WARN] 체크포인트 임시파일 쓰기 실패 (스킵): {e}")
        return
    for attempt in range(30):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt < 29:
                time.sleep(1.0)
            else:
                print(f"  [WARN] 체크포인트 replace 30회 실패 (스킵): {os.path.basename(path)}")


# ################################################################################
# Function — IQA 로드
# ################################################################################
def load_iqa_means() -> pd.DataFrame:
    """ps3100/03_조건별평균_*.xlsx → 47조건 × IQA 9컬럼."""
    xlsx_files = sorted(glob(os.path.join(iqa_dir, "03_*.xlsx")))
    if not xlsx_files:
        raise FileNotFoundError(f"03_*.xlsx 없음: {iqa_dir}")
    df = pd.read_excel(xlsx_files[-1], index_col=0)
    df = df[df.index != "best_group"].copy()
    df.index.name = "condition"
    df = df.reset_index()
    keep = ["condition"] + [c for c in IQA_COLS if c in df.columns]
    return df[keep]


# ################################################################################
# Function — Scatter
# ################################################################################
def _scatter_ax(ax: plt.Axes, x: np.ndarray, y: np.ndarray,
                xlabel: str, ylabel: str) -> None:
    mask = ~(np.isnan(x) | np.isnan(y))
    ax.scatter(x[mask], y[mask], alpha=0.75, s=50, edgecolors="none")
    if mask.sum() >= 3:
        r = corr.correlation_pair(x[mask], y[mask])
        ax.set_title(f"{xlabel} vs {ylabel}\nPLCC={r['plcc']:.3f}  SROCC={r['srocc']:.3f}",
                     fontsize=9)
    else:
        ax.set_title(f"{xlabel} vs {ylabel}", fontsize=9)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)


def save_scatter_hsmb(merged: pd.DataFrame, out_dir: str) -> None:
    """HSMB vs BEW-H / BEW-V scatter (1×2)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, bew in zip(axes, BEW_COLS):
        _scatter_ax(ax,
                    pd.to_numeric(merged["hsmb"], errors="coerce").values,
                    pd.to_numeric(merged[bew],    errors="coerce").values,
                    "HSMB", bew.upper())
    plt.tight_layout()
    p = os.path.join(out_dir, f"04_scatter_hsmb_{dsr}.png")
    plt.savefig(p, dpi=150)
    plt.close()
    print(f"  [SAVE] {os.path.basename(p)}")


def save_scatter_all(merged: pd.DataFrame, out_dir: str) -> None:
    """IQA 9종 vs BEW-H (3×3 grid)."""
    present = [c for c in IQA_COLS if c in merged.columns]
    fig, axes = plt.subplots(3, 3, figsize=(15, 13))
    for i, ax in enumerate(axes.flat):
        if i < len(present):
            _scatter_ax(ax,
                        pd.to_numeric(merged[present[i]], errors="coerce").values,
                        pd.to_numeric(merged["bew_h"],    errors="coerce").values,
                        present[i], "BEW-H")
        else:
            ax.set_visible(False)
    plt.tight_layout()
    p = os.path.join(out_dir, f"05_scatter_all_{dsr}.png")
    plt.savefig(p, dpi=150)
    plt.close()
    print(f"  [SAVE] {os.path.basename(p)}")


def save_anisotropy(bew_cond: pd.DataFrame, out_dir: str) -> None:
    """BEW_H - BEW_V 이방성 지표 — 속도별 분포."""
    df = bew_cond.dropna(subset=["bew_h", "bew_v"]).copy()
    df["anisotropy"] = df["bew_h"] - df["bew_v"]
    speeds = sorted(df["speed_kmh"].unique())
    means  = [df[df["speed_kmh"] == s]["anisotropy"].mean() for s in speeds]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([str(s) for s in speeds], means, color="steelblue", edgecolor="white")
    ax.set_xlabel("속도 (km/h)")
    ax.set_ylabel("BEW_H − BEW_V (이방성)")
    ax.set_title("속도별 평균 이방성 (BEW_H − BEW_V)\n값 클수록 수평 모션블러 강함")
    plt.tight_layout()
    p = os.path.join(out_dir, f"06_anisotropy_{dsr}.png")
    plt.savefig(p, dpi=150)
    plt.close()
    print(f"  [SAVE] {os.path.basename(p)}")


# ################################################################################
# Main
# ################################################################################
def main():
    conditions = collect_conditions(image_dir)
    print(f"\n조건 수: {len(conditions)}")

    # 체크포인트 재개
    done_items: set = set()
    all_rows: list = []
    if args.resume and os.path.exists(checkpoint_path):
        ckpt = pd.read_csv(checkpoint_path)
        if {"condition", "frame"}.issubset(ckpt.columns):
            ckpt = ckpt.drop_duplicates(subset=["condition", "frame"], keep="last")
        all_rows = ckpt.to_dict("records")
        done_items = {(r["condition"], r["frame"]) for r in all_rows}
        print(f"[RESUME] 완료된 이미지 {len(done_items)}장 로드")

    total = sum(len(collect_frames(d)) for _, d in conditions)
    print(f"전체 이미지 수: {total}")

    print(f"\n{'='*60}")
    print("BEW 산출 시작")
    print(f"{'='*60}")

    for cond_name, cond_dir in tqdm(conditions, desc="조건 처리"):
        frames = collect_frames(cond_dir)
        if not frames:
            continue
        cond_new = []
        for fp in frames:
            frame_name = os.path.basename(fp)
            if (cond_name, frame_name) in done_items:
                continue
            img = _imread_safe(fp)
            if img is None:
                print(f"  [WARN] 이미지 읽기 실패: {fp}")
                continue
            bew_h, bew_v = iqa.compute_bew_hv(img)
            meta = parse_condition(cond_name)
            row = {
                "condition":  cond_name,
                "lux":        meta["lux"],
                "iso":        meta["iso"],
                "shutter_us": meta["shutter_us"],
                "speed_kmh":  meta["speed_kmh"],
                "frame":      frame_name,
                "bew_h":      bew_h,
                "bew_v":      bew_v,
            }
            all_rows.append(row)
            done_items.add((cond_name, frame_name))
            cond_new.append(row)

        if cond_new:
            save_checkpoint(all_rows, checkpoint_path)
            h_mean = np.nanmean([r["bew_h"] for r in cond_new])
            v_mean = np.nanmean([r["bew_v"] for r in cond_new])
            print(f"  {cond_name} ({len(cond_new)}프레임)  "
                  f"bew_h={h_mean:.4f}  bew_v={v_mean:.4f}  Δ={h_mean-v_mean:.4f}")

    df_frame = pd.DataFrame(all_rows)

    print(f"\n{'='*60}")
    print("집계 및 상관 분석")
    print(f"{'='*60}")

    # 조건별 평균
    meta_cols = ["lux", "iso", "shutter_us", "speed_kmh"]
    bew_cond = (
        df_frame.groupby("condition")[["bew_h", "bew_v"] + meta_cols]
        .agg({**{"bew_h": "mean", "bew_v": "mean"},
              **{c: "first" for c in meta_cols}})
        .reset_index()
        .round(4)
    )
    bew_cond["anisotropy"] = (bew_cond["bew_h"] - bew_cond["bew_v"]).round(4)

    # IQA 로드 + 조인
    print("[1/4] IQA 조건별평균 로드...")
    iqa_df = load_iqa_means()
    print(f"  IQA 조건: {len(iqa_df)}개")

    merged = pd.merge(bew_cond, iqa_df, on="condition", how="inner")
    print(f"  BEW-IQA 매칭: {len(merged)}조건")
    if len(merged) == 0:
        raise RuntimeError("조인 결과 0행 — 조건명 불일치 확인 필요")

    # 상관 분석
    print("[2/4] 상관 분석 (PLCC/SROCC/KRCC)...")
    corr_df = corr.correlation_matrix(merged, IQA_COLS, BEW_COLS,
                                      col_x="IQA", col_y="BEW")

    # ── 저장 ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("결과 저장")
    print(f"{'='*60}")

    out_frame = os.path.join(output_dir, f"01_bew_per_frame_{dsr}.csv")
    out_cond  = os.path.join(output_dir, f"02_bew_per_condition_{dsr}.csv")
    out_corr  = os.path.join(output_dir, f"03_correlation_{dsr}.csv")

    df_frame.to_csv(out_frame, index=False, encoding="utf-8-sig", float_format="%.4f")
    bew_cond.to_csv(out_cond,  index=False, encoding="utf-8-sig", float_format="%.4f")
    corr_df.to_csv(out_corr,   index=False, encoding="utf-8-sig")
    print(f"  {os.path.basename(out_frame)}")
    print(f"  {os.path.basename(out_cond)}")
    print(f"  {os.path.basename(out_corr)}")

    print("[3/4] Scatter plot 생성...")
    save_scatter_hsmb(merged, output_dir)
    save_scatter_all(merged, output_dir)

    print("[4/4] 이방성 차트 생성...")
    save_anisotropy(bew_cond, output_dir)

    # ── 요약 ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("결과 요약")
    print(f"{'='*60}")
    print(f"총 프레임: {len(df_frame)}  조건: {df_frame['condition'].nunique()}")
    print(f"\nBEW 통계:")
    for col in BEW_COLS:
        v = bew_cond[col].dropna()
        print(f"  {col:<8} mean={v.mean():.4f}  std={v.std():.4f}")
    aniso = bew_cond["anisotropy"].dropna()
    print(f"  aniso    mean={aniso.mean():.4f}  std={aniso.std():.4f}")

    print(f"\nHSMB × BEW 상관:")
    hsmb_row = corr_df[corr_df["IQA"] == "hsmb"][["BEW", "N", "PLCC", "SROCC", "KRCC"]]
    print(hsmb_row.to_string(index=False))

    print(f"\n전체 IQA × BEW-H PLCC 요약:")
    bew_h_row = corr_df[corr_df["BEW"] == "bew_h"][["IQA", "PLCC", "SROCC"]].sort_values("PLCC")
    print(bew_h_row.to_string(index=False))

    etime = time.time()
    print(f"\n{prefix}_{workname} finished in {etime - stime:.2f} seconds")


if __name__ == "__main__":
    main()
