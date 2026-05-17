# -*- coding: utf-8 -*-
"""
common_corr.py — 상관계수 공통 계산 라이브러리

PLCC (Pearson) / SROCC (Spearman) / KRCC (Kendall) + p값 산출.
차트 생성은 각 호출 스크립트에서 직접 처리한다.

사용 스크립트: ps3011, ps3101, (E2/F003-1 예정)
"""
from __future__ import annotations

LIB_VERSION = "v01"

import numpy as np
import pandas as pd
from scipy import stats


def correlation_pair(x, y, min_n: int = 3) -> dict:
    """두 1D 배열의 PLCC/SROCC/KRCC + p값 반환.

    NaN은 쌍 단위로 자동 제거.
    유효 쌍 수 n < min_n이면 모든 지표를 NaN으로 반환.

    Returns
    -------
    dict with keys: n, plcc, plcc_p, srocc, srocc_p, krcc, krcc_p
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    xm, ym, n = x[mask], y[mask], int(mask.sum())
    if n < min_n:
        return {"n": n,
                "plcc": np.nan, "plcc_p": np.nan,
                "srocc": np.nan, "srocc_p": np.nan,
                "krcc": np.nan,  "krcc_p": np.nan}
    plcc,  pp = stats.pearsonr(xm, ym)
    srocc, sp = stats.spearmanr(xm, ym)
    krcc,  kp = stats.kendalltau(xm, ym)
    return {"n": n,
            "plcc":  round(float(plcc),  4), "plcc_p":  round(float(pp), 4),
            "srocc": round(float(srocc), 4), "srocc_p": round(float(sp), 4),
            "krcc":  round(float(krcc),  4), "krcc_p":  round(float(kp), 4)}


def correlation_matrix(df: pd.DataFrame,
                       x_cols: list[str],
                       y_cols: list[str],
                       col_x: str = "X",
                       col_y: str = "Y",
                       min_n: int = 3) -> pd.DataFrame:
    """x_cols × y_cols 모든 쌍의 상관계수 매트릭스 DataFrame.

    Parameters
    ----------
    df     : 데이터 (조건별 평균 등)
    x_cols : X축 컬럼 목록 (예: IQA 9종)
    y_cols : Y축 컬럼 목록 (예: SFR 4종, BEW 2종)
    col_x  : 출력 DataFrame의 X 컬럼명 (기본 "X")
    col_y  : 출력 DataFrame의 Y 컬럼명 (기본 "Y")
    min_n  : 유효 쌍 수 최솟값 (기본 3)

    Returns
    -------
    DataFrame — columns: [col_x, col_y, N, PLCC, PLCC_p, SROCC, SROCC_p, KRCC, KRCC_p]
    """
    rows: list[dict] = []
    for xc in x_cols:
        if xc not in df.columns:
            continue
        for yc in y_cols:
            if yc not in df.columns:
                continue
            x = pd.to_numeric(df[xc], errors="coerce").values
            y = pd.to_numeric(df[yc], errors="coerce").values
            r = correlation_pair(x, y, min_n=min_n)
            rows.append({
                col_x:    xc,
                col_y:    yc,
                "N":      r["n"],
                "PLCC":   r["plcc"],  "PLCC_p":  r["plcc_p"],
                "SROCC":  r["srocc"], "SROCC_p": r["srocc_p"],
                "KRCC":   r["krcc"],  "KRCC_p":  r["krcc_p"],
            })
    return pd.DataFrame(rows)
