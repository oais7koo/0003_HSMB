#!/usr/bin/env python3
"""
ps3011_e3_1_sfr_correlation.py  —  E3-1 SFR↔IQA 상관분석

입력:
  data/ps1010_chungsong_MTF/{조건}/Results/SFR_cypx.csv  (50개)
  data/ps3010/03_그룹별평균_*.xlsx  (IQA 9컬럼, 50조건)

산출:
  data/ps3010/e3_1_sfr_metrics.csv      조건별 R1090/MTF50 H·V 평균 (50행)
  data/ps3010/e3_1_correlation.csv      IQA 9 × SFR 4 상관 매트릭스 (PLCC/SROCC/KRCC)
  data/ps3010/e3_1_scatter_hsmb.png     HSMB vs SFR 4종 scatter (2×2)
  data/ps3010/e3_1_scatter_r1090h.png   전체 IQA vs R1090_H scatter (3×3)

ref: d3010 §9
"""
from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_corr as corr

# ── 경로 ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent
SFR_BASE  = BASE_DIR / "data" / "ps1010_chungsong_MTF"
OUT_DIR   = BASE_DIR / "data" / "ps3010"

IQA_COLS = ["hsmb", "cpbd", "niqe", "niqe_matlab", "piqe",
            "brisque", "brisque_matlab", "dbcnn", "arniqa"]
SFR_COLS = ["R1090_H", "R1090_V", "MTF50_H", "MTF50_V"]


# ── SFR 파싱 ──────────────────────────────────────────────────────────────────
def load_sfr_metrics() -> pd.DataFrame:
    """50개 SFR_cypx.csv → 조건별 R1090/MTF50 H·V 평균 DataFrame"""
    records: list[dict] = []
    paths = sorted(glob.glob(str(SFR_BASE / "*" / "Results" / "SFR_cypx.csv")))
    if not paths:
        raise FileNotFoundError(f"SFR_cypx.csv 없음: {SFR_BASE}")

    for path in paths:
        condition = Path(path).parent.parent.name
        try:
            # 헤더 2행: 0행=컬럼명, 1행=단위 → skiprows=[1]
            df = pd.read_csv(path, header=0, skiprows=[1])
            df.columns = [c.strip() for c in df.columns]

            hv_col    = "H/V"
            r1090_col = "R1090"
            mtf50_col = "MTF50"

            horiz = df[df[hv_col].str.contains("Horiz",    na=False)]
            vert  = df[df[hv_col].str.contains("Vertical", na=False)]

            records.append({
                "condition": condition,
                "R1090_H": pd.to_numeric(horiz[r1090_col], errors="coerce").mean(),
                "R1090_V": pd.to_numeric(vert[r1090_col],  errors="coerce").mean(),
                "MTF50_H": pd.to_numeric(horiz[mtf50_col], errors="coerce").mean(),
                "MTF50_V": pd.to_numeric(vert[mtf50_col],  errors="coerce").mean(),
            })
        except Exception as exc:
            print(f"  [WARN] {condition}: {exc}")

    return pd.DataFrame(records)


# ── IQA 로드 ──────────────────────────────────────────────────────────────────
def load_iqa_means() -> pd.DataFrame:
    """ps3010 03_그룹별평균.xlsx → 조건별 IQA 9컬럼"""
    xlsx_files = sorted(glob.glob(str(OUT_DIR / "03_*.xlsx")))
    if not xlsx_files:
        raise FileNotFoundError(f"03_*.xlsx 없음: {OUT_DIR}")
    df = pd.read_excel(xlsx_files[-1])
    df = df.rename(columns={df.columns[0]: "condition"})
    keep = ["condition"] + [c for c in IQA_COLS if c in df.columns]
    return df[keep]


# ── Scatter plot ──────────────────────────────────────────────────────────────
def _scatter_ax(ax: plt.Axes, x: np.ndarray, y: np.ndarray,
                xlabel: str, ylabel: str) -> None:
    mask = ~(np.isnan(x) | np.isnan(y))
    ax.scatter(x[mask], y[mask], alpha=0.75, s=45, edgecolors="none")
    if mask.sum() >= 3:
        r, _ = stats.pearsonr(x[mask], y[mask])
        sr, _ = stats.spearmanr(x[mask], y[mask])
        ax.set_title(f"{xlabel} vs {ylabel}\nPLCC={r:.3f}  SROCC={sr:.3f}", fontsize=9)
    else:
        ax.set_title(f"{xlabel} vs {ylabel}", fontsize=9)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)


def plot_scatter(merged: pd.DataFrame, out_dir: Path) -> None:
    # (A) HSMB vs 4 SFR
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for ax, sfr in zip(axes.flat, SFR_COLS):
        _scatter_ax(ax,
                    pd.to_numeric(merged["hsmb"], errors="coerce").values,
                    pd.to_numeric(merged[sfr],   errors="coerce").values,
                    "HSMB", sfr)
    plt.tight_layout()
    p = out_dir / "e3_1_scatter_hsmb.png"
    plt.savefig(p, dpi=150)
    plt.close()
    print(f"  [SAVE] {p.name}")

    # (B) 전체 IQA vs R1090_H  (3×3)
    present = [c for c in IQA_COLS if c in merged.columns]
    fig, axes = plt.subplots(3, 3, figsize=(15, 13))
    for i, ax in enumerate(axes.flat):
        if i < len(present):
            _scatter_ax(ax,
                        pd.to_numeric(merged[present[i]], errors="coerce").values,
                        pd.to_numeric(merged["R1090_H"],  errors="coerce").values,
                        present[i], "R1090_H")
        else:
            ax.set_visible(False)
    plt.tight_layout()
    p = out_dir / "e3_1_scatter_r1090h.png"
    plt.savefig(p, dpi=150)
    plt.close()
    print(f"  [SAVE] {p.name}")


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("E3-1 SFR↔IQA 상관분석  (ps3011)")
    print("=" * 60)

    # 1. SFR 파싱
    print("\n[1/5] SFR_cypx.csv 파싱...")
    sfr_df = load_sfr_metrics()
    print(f"  파싱 조건: {len(sfr_df)}개")
    sfr_out = OUT_DIR / "e3_1_sfr_metrics.csv"
    sfr_df.to_csv(sfr_out, index=False, encoding="utf-8-sig")
    print(f"  [SAVE] {sfr_out.name}")
    print(sfr_df[SFR_COLS].describe().round(4).to_string())

    # 2. IQA 로드
    print("\n[2/5] IQA 그룹별 평균 로드...")
    iqa_df = load_iqa_means()
    print(f"  IQA 조건: {len(iqa_df)}개  컬럼: {[c for c in IQA_COLS if c in iqa_df.columns]}")

    # 3. 조인
    print("\n[3/5] SFR ↔ IQA 조건명 조인...")
    merged = pd.merge(sfr_df, iqa_df, on="condition", how="inner")
    print(f"  매칭: {len(merged)}개  (SFR {len(sfr_df)} / IQA {len(iqa_df)})")
    if len(merged) == 0:
        # 디버그: 샘플 조건명 출력
        print("  [DEBUG] SFR 조건 샘플:", sfr_df["condition"].head(3).tolist())
        print("  [DEBUG] IQA 조건 샘플:", iqa_df["condition"].head(3).tolist())
        raise RuntimeError("조인 결과 0행 — 조건명 불일치 확인 필요")
    merged.to_csv(OUT_DIR / "e3_1_merged.csv", index=False, encoding="utf-8-sig")

    # 4. 상관 분석
    print("\n[4/5] 상관 분석 (PLCC/SROCC/KRCC)...")
    corr_df = corr.correlation_matrix(merged, IQA_COLS, SFR_COLS, col_x="IQA", col_y="SFR")
    corr_out = OUT_DIR / "e3_1_correlation.csv"
    corr_df.to_csv(corr_out, index=False, encoding="utf-8-sig")
    print(f"  [SAVE] {corr_out.name}")

    # 5. Scatter
    print("\n[5/5] Scatter plot 생성...")
    plot_scatter(merged, OUT_DIR)

    # ── 요약 ──────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("HSMB 상관 요약 (N={})".format(len(merged)))
    print("=" * 60)
    hsmb_row = corr_df[corr_df["IQA"] == "hsmb"][["SFR", "PLCC", "SROCC", "KRCC"]]
    print(hsmb_row.to_string(index=False))

    print("\n전체 IQA × R1090_H PLCC 요약:")
    r1090h = corr_df[corr_df["SFR"] == "R1090_H"][["IQA", "PLCC", "SROCC"]].sort_values("PLCC")
    print(r1090h.to_string(index=False))

    print("\n완료.")


if __name__ == "__main__":
    main()
