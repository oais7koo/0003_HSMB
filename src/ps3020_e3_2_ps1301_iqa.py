# -*- coding: utf-8 -*-
# ################################################################################
# Title: E3-2 ps1301 실제 크랙 이미지 데이터셋 NR-IQA 일괄 산출
# Author: oaiskoo
# Date: 2026.05.17
# Version: v02
# Goal: ps1301_real_crack_cam2 50조건 frame 737장 → d0100 표준 7종(9컬럼) NR-IQA 스코어 산출
# Changes:
#   - v02: 대용량 대응 — 이미지 가로·세로 가운데 50%(면적 25%) center crop 후 IQA 산출
#   - v01: 초기 버전 — ps3010 준용, ps1301 폴더명 파서로 교체 (A안: IQA 산출만)
# Description:
#   - 입력: data/ps1301_real_crack_cam2/ (50조건 폴더 crack_*, 각 폴더 직속 frame_*.png)
#   - 대용량(~55MB, 8K) → 가로·세로 가운데 50% center crop 후 IQA 산출 (center_crop=True)
#   - IQA 라이브러리: common_iqa7.compute_all_from_path() — 9컬럼
#   - 조건 폴더명 파싱: crack_d{거리}_ISO{값}_V{속도}  (거리 d25 → 2.5m)
#   - is_defocus: ISO=400이면 1 (PRD §2.6 의도적 defocus 조건)
#   - 중간 체크포인트: 조건 단위 incremental 저장
#   - 출력 형식: ps3010과 동일 (01/02/03 xlsx + 04 histogram)
# Input: ./data/ps1301_real_crack_cam2/
# Output: ./data/ps3020/01_전체데이터_*.xlsx, 02_그룹별통계_*.xlsx, 03_그룹별평균_*.xlsx
# 참조: d3020_상세기획_E3_2_ps1301_IQA.md, d1301_real_crack_cam2.md, d0001_prd.md §2.7
# ################################################################################
# Library
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

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_iqa7 as iqa

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
        "image_dir": "data/ps1301_real_crack_cam2",
        "output_dir": "data/ps3020",
        "checkpoint_csv": "data/ps3020/_checkpoint.csv",
    },
    "processing": {
        "device": None,    # None → common_iqa7 자동 (GPU 우선)
    },
    "stats": {
        "skip_cols": {"condition", "frame", "is_defocus"},
        "round": 4,
    },
}


def resolve_device_name(device_arg: str | None) -> str:
    """실제 추론에 사용될 디바이스 문자열을 반환."""
    return device_arg or iqa._default_device()

parser = argparse.ArgumentParser(description="E3-2 ps1301 NR-IQA 일괄 산출")
parser.add_argument("--image_dir", type=str, default=None)
parser.add_argument("--output_dir", type=str, default=None)
parser.add_argument("--checkpoint_csv", type=str, default=None)
parser.add_argument("--device", type=str, default=None, help="cuda / cpu")
parser.add_argument("--resume", action="store_true", help="체크포인트에서 재개")
args = parser.parse_args()

if args.image_dir:
    CONFIG["io"]["image_dir"] = args.image_dir
if args.output_dir:
    CONFIG["io"]["output_dir"] = args.output_dir
if args.checkpoint_csv:
    CONFIG["io"]["checkpoint_csv"] = args.checkpoint_csv
if args.device:
    CONFIG["processing"]["device"] = args.device

image_dir = os.path.join(project_root, CONFIG["io"]["image_dir"])
output_dir = os.path.join(project_root, CONFIG["io"]["output_dir"])
checkpoint_path = os.path.join(project_root, CONFIG["io"]["checkpoint_csv"])
os.makedirs(output_dir, exist_ok=True)

# ################################################################################
# 한글 차트 설정
# ################################################################################
import platform
os_var = platform.system()
mpl.use("Agg")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 13
if os_var == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_var == "Darwin":
    mpl.rc("font", family="AppleGothic")
else:
    plt.rcParams["font.family"] = "NanumGothic"

# 설정 출력
print(f"\n{'='*60}")
print("설정 정보")
print(f"{'='*60}")
print(f"입력 디렉토리: {image_dir}")
print(f"출력 디렉토리: {output_dir}")
print(f"디바이스: {CONFIG['processing']['device'] or '자동(GPU 우선)'}")
print(f"pyiqa 가용: {iqa._PYIQA_AVAILABLE} / cpbd 가용: {iqa._CPBD_AVAILABLE}")
print(f"{'='*60}")


# ################################################################################
# Function
# ################################################################################

# 조건 폴더명 파싱: crack_d25_ISO100_V60  (거리 d25 = 2.5m)
_COND_RE = re.compile(
    r"^crack_d(?P<dist>\d+)_ISO(?P<iso>\d+)_V(?P<speed>\d+)$"
)


def parse_condition(folder_name: str) -> dict:
    """조건 폴더명 파싱 → 메타 dict. 거리 d25 → 2.5m (× 0.1)."""
    m = _COND_RE.match(folder_name)
    if not m:
        return {"distance_m": None, "iso": None, "speed_kmh": None, "is_defocus": None}
    iso_val = int(m.group("iso"))
    return {
        "distance_m": int(m.group("dist")) / 10.0,
        "iso": iso_val,
        "speed_kmh": int(m.group("speed")),
        "is_defocus": 1 if iso_val == 400 else 0,
    }


def collect_conditions(base_dir: str) -> list:
    """(조건명, 절대경로) 목록 — crack_* 폴더만."""
    base = Path(base_dir)
    return sorted(
        [(d.name, str(d)) for d in base.iterdir()
         if d.is_dir() and d.name.startswith("crack_")],
        key=lambda x: x[0],
    )


def collect_frames(cond_dir: str) -> list:
    """조건 폴더 직속 frame_*.png만 수집."""
    return sorted(glob(os.path.join(cond_dir, "frame_*.png")))


def process_frame(cond_name: str, fp: str, device) -> dict:
    """단일 frame IQA 산출 → 행 dict 반환.

    ps1301은 대용량(~55MB, 8K)이므로 가로·세로 가운데 50%(면적 25%)만 사용.
    """
    meta = parse_condition(cond_name)
    scores = iqa.compute_all_from_path(fp, device=device, center_crop=True)
    row = {
        "condition": cond_name,
        "distance_m": meta["distance_m"],
        "iso": meta["iso"],
        "speed_kmh": meta["speed_kmh"],
        "frame": os.path.basename(fp),
        "is_defocus": meta["is_defocus"],
    }
    row.update(scores)
    row["run_device"] = resolve_device_name(device)
    row["common_iqa7_version"] = getattr(iqa, "LIB_VERSION", "unknown")

    if iqa._PYIQA_AVAILABLE:
        import torch
        torch.cuda.empty_cache()

    return row


def save_checkpoint(rows: list, path: str):
    """체크포인트를 원자적으로 저장 (Windows PermissionError 재시도 포함)."""
    tmp_path = f"{path}.tmp"
    pd.DataFrame(rows).to_csv(
        tmp_path, index=False, encoding="utf-8-sig", float_format="%.4f"
    )
    for attempt in range(30):
        try:
            os.replace(tmp_path, path)
            break
        except PermissionError:
            if attempt < 29:
                time.sleep(1.0)
            else:
                raise


def build_stats(df: pd.DataFrame, skip_cols: set) -> pd.DataFrame:
    """조건별 기술통계 (mean/std/min/max)."""
    num_cols = [c for c in df.columns if c not in skip_cols
                and pd.api.types.is_numeric_dtype(df[c])]
    stats = df.groupby("condition")[num_cols].agg(["mean", "std", "min", "max"])
    stats.columns = ["_".join(c) for c in stats.columns]
    meta = df.groupby("condition")[["distance_m", "iso", "speed_kmh", "is_defocus"]].first()
    return pd.concat([meta, stats], axis=1).reset_index()


def build_means(df: pd.DataFrame, skip_cols: set, rnd: int) -> pd.DataFrame:
    """조건별 평균 + best_group 행."""
    num_cols = [c for c in df.columns if c not in skip_cols
                and pd.api.types.is_numeric_dtype(df[c])]
    means = df.groupby("condition")[num_cols].mean().round(rnd)
    best = {c: means[c].idxmax() for c in means.columns if means[c].notna().any()}
    return pd.concat([means, pd.DataFrame([best], index=["best_group"])])


def save_histogram(df: pd.DataFrame, out_dir: str):
    """9개 메트릭 히스토그램 저장."""
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    for ax, col in zip(axes.flatten(), iqa.METRIC_COLUMNS):
        vals = df[col].dropna()
        ax.hist(vals, bins=30, color="steelblue", edgecolor="white")
        ax.set_title(f"{col}\n({iqa.METRIC_DIRECTION[col]})")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")
    plt.tight_layout()
    out_path = os.path.join(out_dir, f"04_histogram_{dsr}.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"히스토그램 저장: {out_path}")


# ################################################################################
# Main
# ################################################################################
def main():
    device = CONFIG["processing"]["device"]
    skip_cols = CONFIG["stats"]["skip_cols"]
    rnd = CONFIG["stats"]["round"]

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
        done_items = {(r["condition"], r["frame"]) for _, r in ckpt.iterrows()}
        print(f"[RESUME] 완료된 이미지 {len(done_items)}장 로드")

    total_images = sum(len(collect_frames(d)) for _, d in conditions)
    print(f"전체 이미지 수: {total_images}")
    print(f"처리 대상 조건 수: {len(conditions)}\n")

    print(f"{'='*60}")
    print("IQA 산출 시작")
    print(f"{'='*60}")

    done_cond_count = 0
    for cond_name, cond_dir in tqdm(conditions, desc="조건 처리"):
        frames = collect_frames(cond_dir)
        if not frames:
            print(f"  [SKIP] {cond_name}: frame 없음")
            continue

        cond_hsmb = []
        for fp in frames:
            frame_name = os.path.basename(fp)
            item_key = (cond_name, frame_name)
            if item_key in done_items:
                continue
            row = process_frame(cond_name, fp, device)
            all_rows.append(row)
            done_items.add(item_key)
            cond_hsmb.append(row.get("hsmb", float("nan")))

        # 조건 완료 후 체크포인트 (이미지 단위 → 조건 단위로 변경: Windows Defender 락 방지)
        if cond_hsmb:
            save_checkpoint(all_rows, checkpoint_path)

        if cond_hsmb:
            done_cond_count += 1
            hsmb_mean = np.nanmean(cond_hsmb)
            print(f"  {cond_name} ({len(cond_hsmb)}프레임)  hsmb_mean={hsmb_mean:.4f}")

    if done_cond_count == 0 and args.resume:
        print("[INFO] 재개 대상 없음: 모든 이미지가 이미 체크포인트에 기록되어 있습니다.")

    df = pd.DataFrame(all_rows)

    # 컬럼 정렬
    meta_cols = [
        "condition", "distance_m", "iso", "speed_kmh", "frame", "is_defocus",
        "run_device", "common_iqa7_version",
    ]
    df = df[[c for c in meta_cols + iqa.METRIC_COLUMNS if c in df.columns]]

    # ############################################################################
    # 저장
    # ############################################################################
    print(f"\n{'='*60}")
    print("결과 저장")
    print(f"{'='*60}")

    out_all   = os.path.join(output_dir, f"01_전체데이터_{dsr}.xlsx")
    out_stats = os.path.join(output_dir, f"02_그룹별통계_{dsr}.xlsx")
    out_means = os.path.join(output_dir, f"03_그룹별평균_{dsr}.xlsx")

    with pd.ExcelWriter(out_all, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="전체데이터", index=False)

    stats_df = build_stats(df, skip_cols)
    with pd.ExcelWriter(out_stats, engine="openpyxl") as w:
        stats_df.to_excel(w, sheet_name="그룹별통계", index=False)

    means_df = build_means(df, skip_cols, rnd)
    with pd.ExcelWriter(out_means, engine="openpyxl") as w:
        means_df.to_excel(w, sheet_name="그룹별평균", index=True)

    print(f"출력: {out_all}")
    print(f"      {out_stats}")
    print(f"      {out_means}")

    save_histogram(df, output_dir)

    # 요약
    print(f"\n{'='*60}")
    print("결과 요약")
    print(f"{'='*60}")
    print(f"총 프레임: {len(df)}")
    print(f"조건 수: {df['condition'].nunique()}")
    print(f"defocus(ISO=400) 프레임: {df['is_defocus'].sum()}")
    print("\n메트릭 통계:")
    for col in iqa.METRIC_COLUMNS:
        vals = df[col].dropna()
        if len(vals):
            print(f"  {col:<16} mean={vals.mean():.4f}  std={vals.std():.4f}  "
                  f"nan={df[col].isna().sum()}")

    # ############################################################################
    # Finish
    # ############################################################################
    etime = time.time()
    print(f"\n{prefix}_{workname} finished in {etime-stime:.2f} seconds")


if __name__ == "__main__":
    main()
