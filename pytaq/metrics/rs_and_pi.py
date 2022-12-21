from typing import Iterable, Tuple
from datetime import timedelta

import pandas as pd
import numpy as np

from ..utils.float_approx import correct_float_approx
from locks_crosses import filter_locks_crosses


BASE_SIGNS = ["LR", "EMO", "CLNV"]
RETAIL_SIGNS = ["BJZ"] + [x + "notBJZ" for x in BASE_SIGNS]


def dollar_realized_spread(
    sign: pd.Series,
    price: pd.Series,
    midpoint_next: pd.Series,
) -> pd.Series:
    s = sign * (price - midpoint_next) * 2
    return correct_float_approx(s, price, midpoint_next)


def percent_realized_spread(
    sign: pd.Series,
    price: pd.Series,
    midpoint_next: pd.Series,
) -> pd.Series:
    s = sign * (np.log(price) - np.log(midpoint_next)) * 2
    return correct_float_approx(s, price, midpoint_next)


def dollar_price_impact(
    sign: pd.Series,
    midpoint: pd.Series,
    midpoint_next: pd.Series,
) -> pd.Series:
    s = sign * (midpoint_next - midpoint) * 2
    return correct_float_approx(s, midpoint, midpoint_next)


def percent_price_impact(
    sign: pd.Series,
    midpoint: pd.Series,
    midpoint_next: pd.Series,
) -> pd.Series:
    s = sign * (np.log(midpoint_next) - np.log(midpoint)) * 2
    return correct_float_approx(s, midpoint, midpoint_next)


def rs_and_pi(
    df: pd.DataFrame,
    signs: Iterable[str],
    suffix: str = "",
    sign_col_prefix: str = "BuySell",
    price_col: str = "price",
    midpoint_col: str = "midpoint",
    midpoint_next_col: str = "midpoint_next",
    dollar_realized_spread_prefix: str = "DollarRealizedSpread_",
    percent_realized_spread_prefix: str = "PercentRealizedSpread_",
    dollar_price_impact_prefix: str = "DollarPriceImpact_",
    percent_price_impact_prefix: str = "PercentPriceImpact_",
    copy: bool = False,
) -> pd.DataFrame:
    if copy:
        df = df.copy()
    price = df[price_col]
    midpoint = df[midpoint_col]
    midpoint_next = df[midpoint_next_col]

    for sign_col_suffix in signs:
        sign = df[f"{sign_col_prefix}{sign_col_suffix}"]

        df[f"{dollar_realized_spread_prefix}{sign}{suffix}"] = dollar_realized_spread(
            sign=sign,
            price=price,
            midpoint_next=midpoint_next,
        )
        df[f"{percent_realized_spread_prefix}{sign}{suffix}"] = percent_realized_spread(
            sign=sign,
            price=price,
            midpoint_next=midpoint_next,
        )
        df[f"{dollar_price_impact_prefix}{sign}{suffix}"] = dollar_price_impact(
            sign=sign,
            midpoint=midpoint,
            midpoint_next=midpoint_next,
        )
        df[f"{percent_price_impact_prefix}{sign}{suffix}"] = percent_price_impact(
            sign=sign,
            midpoint=midpoint,
            midpoint_next=midpoint_next,
        )


def merge_future_nbbo(
    df: pd.DataFrame,
    nbbo_df: pd.DataFrame,
    delay: timedelta,
    symbol_col: str = "symbol",
    timestamp_col: str = "timestamp",
    best_bid_col: str = "best_bid",
    best_ask_col: str = "best_ask",
    midpoint_col: str = "midpoint",
    suffixes: Tuple[str, str] = ("", "_next"),
) -> pd.DataFrame:
    next_df = nbbo_df[[timestamp_col, symbol_col, best_bid_col, best_ask_col]].copy()
    next_df[midpoint_col] = (next_df[best_bid_col] + next_df[best_ask_col]) / 2
    next_df[timestamp_col] = next_df[timestamp_col] - delay

    df = df.sort_values([timestamp_col, symbol_col])
    next_df = next_df.sort_values([timestamp_col, symbol_col])

    return pd.merge_asof(
        df,
        next_df,
        on=timestamp_col,
        by=symbol_col,
        allow_exact_matches=False,
        suffixes=suffixes,
    )


def compute_rs_and_pi(
    trade_and_nbbo_df: pd.DataFrame,
    off_nbbo_df: pd.DataFrame,
    delay: timedelta = timedelta(minutes=5),
    suffix: str = "5min",
    track_retail: bool = False,
) -> pd.DataFrame:
    df = merge_future_nbbo(df=trade_and_nbbo_df, nbbo_df=off_nbbo_df, delay=delay)
    df = filter_locks_crosses(df, asks=df["best_ask_next"], bids=df["best_bid_next"])
    signs = BASE_SIGNS + RETAIL_SIGNS if track_retail else BASE_SIGNS

    return rs_and_pi(df, signs=signs, suffix=suffix)
