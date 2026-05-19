# -*- coding: utf-8 -*-
# ################################################################################
# Title: E3-3 ps1302 프린트 크랙 이미지 데이터셋 NR-IQA 일괄 산출
# Author: oaiskoo
# Date: 2026.05.17
# Version: v02
# Goal: ps1302_print_crack 50장 → d0100 표준 7종(9컬럼) NR-IQA 스코어 산출
# Changes:
#   - v02: 대용량 대응 — 이미지 가로·세로 가운데 50%(면적 25%) center crop 후 IQA 산출
#   - v01: 초기 버전 — ps3010 준용, ps1302 평면 구조(조건 폴더 없음) 대응
# Description:
#   - 입력: data/ps1302_print_crack/ 루트 직속 cam1_*.png 50장 (조건 폴더 없음)
#   - 대용량 → 가로·세로 가운데 50% center crop 후 IQA 산출 (center_crop=True)
#   - IQA 라이브러리: common_iqa7.compute_all_from_path() — 9컬럼
#   - 파일명 파싱: cam1_v{속도}_iso{값}_d{거리}[_x]  (거리 d25 → 2.5m)
#   - is_defocus: ISO=400이면 1 / is_excluded: 파일명에 _x 접미사면 1
#   - 조건당 1장 → 02·03 그룹별통계 생략 (01 전체데이터 + 04 histogram만)
# Input: ./data/ps1302_print_crack/
# Output: ./data/ps3030/01_전체데이터_*.xlsx, 04_histogram_*.png
# 참조: d3030_상세구현_E3_3_ps1302_IQA.md, d1302_print_crack.md, d0001_prd.md §2.7
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
        "image_dir": "data/ps1302_print_crack",
        "output_dir": "data/ps3030",
        "checkpoint_csv": "data/ps3030/_checkpoint.csv",
    },
    "processing": {
        "device": None,    # None → common_iqa7 자동 (GPU 우선)
    },
}

parser = argparse.ArgumentParser(description="E3-3 ps1302 NR-IQA 일괄 산출")
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

# 파일명 파싱: cam1_v60_iso100_d25  또는  cam1_v60_iso100_d65_x  (거리 d25 = 2.5m)
_FNAME_RE = re.compile(
    r"^cam1_v(?P<speed>\d+)_iso(?P<iso>\d+)_d(?P<dist>\d+)(?P<x>_x)?$"
)


def parse_filename(stem: str) -> dict:
    """파일명(확장자 제외) 파싱 → 메타 dict. 거리 d25 → 2.5m (× 0.1)."""
    m = _FNAME_RE.match(stem)
    if not m:
        return {"speed_kmh": None, "iso": None, "distance_m": None,
                "is_defocus": None, "is_excluded": None}
    iso_val = int(m.group("iso"))
    return {
        "speed_kmh": int(m.group("speed")),
        "iso": iso_val,
        "distance_m": int(m.group("dist")) / 10.0,
        "is_defocus": 1 if iso_val == 400 else 0,
        "is_excluded": 1 if m.group("x") else 0,
    }


def collect_images(base_dir: str) -> list:
    """데이터셋 루트 직속 cam1_*.png 목록 (평면 구조, 조건 폴더 없음)."""
    return sorted(glob(os.path.join(base_dir, "cam1_*.png")))


def process_image(fp: str, device) -> dict:
    """단일 이미지 IQA 산출 → 행 dict.

    ps1302는 대용량이므로 가로·세로 가운데 50%(면적 25%)만 사용.
    """
    stem = os.path.splitext(os.path.basename(fp))[0]
    meta = parse_filename(stem)
    scores = iqa.compute_all_from_path(fp, device=device, center_crop=True)
    row = {
        "filename": os.path.basename(fp),
        "speed_kmh": meta["speed_kmh"],
        "iso": meta["iso"],
        "distance_m": meta["distance_m"],
        "is_defocus": meta["is_defocus"],
        "is_excluded": meta["is_excluded"],
    }
    row.update(scores)

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
    for attempt in range(10):
        try:
            os.replace(tmp_path, path)
            break
        except PermissionError:
            if attempt < 9:
                time.sleep(0.5)
            else:
                raise


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

    images = collect_images(image_dir)
    print(f"\n이미지 수: {len(images)}")

    # 체크포인트 재개 (파일 단위)
    done_files: set = set()
    all_rows: list = []
    if args.resume and os.path.exists(checkpoint_path):
        ckpt = pd.read_csv(checkpoint_path)
        if "filename" in ckpt.columns:
            ckpt = ckpt.drop_duplicates(subset=["filename"], keep="last")
        all_rows = ckpt.to_dict("records")
        done_files = set(ckpt["filename"].unique())
        print(f"[RESUME] 완료된 이미지 {len(done_files)}장 로드")

    todo = [fp for fp in images if os.path.basename(fp) not in done_files]
    print(f"처리 대상: {len(todo)}장\n")

    print(f"{'='*60}")
    print("IQA 산출 시작")
    print(f"{'='*60}")

    for fp in tqdm(todo, desc="이미지 처리"):
        stem = os.path.splitext(os.path.basename(fp))[0]
        if not _FNAME_RE.match(stem):
            print(f"  [SKIP] {os.path.basename(fp)}: 파일명 파싱 실패")
            continue

        row = process_image(fp, device)
        all_rows.append(row)

        # 파일 단위 체크포인트
        save_checkpoint(all_rows, checkpoint_path)

    df = pd.DataFrame(all_rows)

    # 컬럼 정렬
    meta_cols = ["filename", "speed_kmh", "iso", "distance_m", "is_defocus", "is_excluded"]
    df = df[[c for c in meta_cols + iqa.METRIC_COLUMNS if c in df.columns]]

    # ############################################################################
    # 저장 (조건당 1장 → 02·03 그룹별통계 생략, 01 + 04만)
    # ############################################################################
    print(f"\n{'='*60}")
    print("결과 저장")
    print(f"{'='*60}")

    out_all = os.path.join(output_dir, f"01_전체데이터_{dsr}.xlsx")
    with pd.ExcelWriter(out_all, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="전체데이터", index=False)
    print(f"출력: {out_all}")

    save_histogram(df, output_dir)

    # 요약
    print(f"\n{'='*60}")
    print("결과 요약")
    print(f"{'='*60}")
    print(f"총 이미지: {len(df)}")
    print(f"defocus(ISO=400): {df['is_defocus'].sum()}  /  excluded(_x): {df['is_excluded'].sum()}")
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
