from typing import Union, List

import pandas as pd
import numpy as np

from ..utils.float_approx import float_zero, float_equal
from ..metrics.locks_crosses import locked_crossed_rows

DEFAULT_CLNV_THRESHOLD = 0.3

BASE_SIGNS = ["LR", "EMO", "CLNV"]
RETAIL_SIGNS = ["BJZ"] + [x + "notBJZ" for x in BASE_SIGNS]


def sign_tick(
    df: pd.DataFrame,
    groupby_col: Union[str, List[str]] = "symbol",
    timestamp_col: str = "timestamp",
    price_col: str = "price",
) -> pd.Series:

    if isinstance(groupby_col, str):
        group = [groupby_col]
    elif not isinstance(groupby_col, list):
        raise ValueError("groupby_col should be str or a list of str.")

    # Trade direction (tick test)
    df = (
        df[[timestamp_col] + group + [price_col]]
        .sort_values([timestamp_col] + group)
        .copy()
    )

    df["dir"] = np.sign(df.groupby(group)[price_col].diff())
    df.loc[float_zero(df["dir"]), "dir"] = np.nan
    return df.groupby(group)["dir"].fillna(method="ffill")


def sign_lr(
    price: pd.Series,
    midpoint: pd.Series,
    tick_dir: pd.Series,
    lock_cross: pd.Series,
) -> pd.Series:
    lr_dir = tick_dir.copy()
    keep_tick = lock_cross | float_equal(price, midpoint)

    lr_dir[~keep_tick & (price > midpoint)] = 1
    lr_dir[~keep_tick & (price < midpoint)] = -1
    return lr_dir


def sign_emo(
    price: pd.Series,
    best_bid: pd.Series,
    best_ask: pd.Series,
    tick_dir: pd.Series,
    lock_cross: pd.Series,
) -> pd.Series:
    emo_dir = tick_dir.copy()

    emo_dir[~lock_cross & float_equal(price, best_ask)] = 1
    emo_dir[~lock_cross & float_equal(price, best_bid)] = -1
    return emo_dir


def sign_clnv(
    price: pd.Series,
    best_bid: pd.Series,
    best_ask: pd.Series,
    tick_dir: pd.Series,
    lock_cross: pd.Series,
    threshold: float = DEFAULT_CLNV_THRESHOLD,
) -> pd.Series:
    clnv_dir = tick_dir.copy()

    ask_th = best_ask - threshold * (best_ask - best_bid)
    bid_th = best_bid + threshold * (best_ask - best_bid)

    clnv_dir[~lock_cross & (price >= ask_th) & (price <= best_ask)] = 1
    clnv_dir[~lock_cross & (price <= bid_th) & (price >= best_bid)] = -1

    return clnv_dir


def sign_bjz(price: pd.Series, ex: pd.Series) -> pd.Series:
    # Compute retail sign following "TRACKING RETAIL INVESTOR ACTIVITY"
    # by EKKEHART BOEHMER, CHARLES M. JONES, and XIAOYAN ZHANG
    def compute_retail_sign(s):
        out = np.full(s.shape, np.nan)
        for i in range(s.shape[0]):
            z = 100 * np.mod(s[i], 0.01)
            if (z >= 1e-4) & (z < 0.4):
                out[i] = -1.0
            if (z >= 0.6) & (z < (1 - 1e-4)):
                out[i] = 1.0
        return out

    bjz_dir = pd.Series(np.nan, index=price.index)

    bjz_dir[ex == "D"] = compute_retail_sign(bjz_dir[ex == "D"].values)

    return bjz_dir


def sign_trades(
    df: pd.DataFrame,
    groupby_col: Union[str, List[str]] = "symbol",
    timestamp_col: str = "timestamp",
    price_col: str = "price",
    sign_col_prefix: str = "BuySell",
    clnv_threshold: float = DEFAULT_CLNV_THRESHOLD,
) -> pd.DataFrame:

    df["midpoint"] = (df["best_bid"] + df["best_ask"]) / 2
    lock_cross = locked_crossed_rows(asks=df["best_ask"], bids=df["best_bid"])

    tick_dir = sign_tick(
        df=df, groupby_col=groupby_col, timestamp_col=timestamp_col, price_col=price_col
    )

    df[f"{sign_col_prefix}LR"] = sign_lr(
        price=df[price_col],
        midpoint=df["midpoint"],
        tick_dir=tick_dir,
        lock_cross=lock_cross,
    )
    df[f"{sign_col_prefix}EMO"] = sign_emo(
        price=df[price_col],
        best_bid=df["best_bid"],
        best_ask=df["best_ask"],
        tick_dir=tick_dir,
        lock_cross=lock_cross,
    )
    df[f"{sign_col_prefix}CLNV"] = sign_emo(
        price=df[price_col],
        best_bid=df["best_bid"],
        best_ask=df["best_ask"],
        tick_dir=tick_dir,
        lock_cross=lock_cross,
        threshold=clnv_threshold,
    )
    df[f"{sign_col_prefix}BJZ"] = sign_bjz(price=df[price_col], ex=df["ex"])

    sel = df[f"{sign_col_prefix}BJZ"].isnull()
    for x in ["LR", "EMO", "CLNV"]:
        df[f"{sign_col_prefix}{x}notBJZ"] = np.nan
        df.loc[sel, f"{sign_col_prefix}{x}notBJZ"] = df.loc[
            sel, f"{sign_col_prefix}{x}"
        ]

    return df
