from typing import Iterable, Tuple
from datetime import timedelta

import pandas as pd
import numpy as np


def correct_float_approx(
    series: pd.Series, s1: pd.Series, s2: pd.Series, atol: float = 0.000001
) -> pd.Series:
    """Changes values of a Series to NA when the corresponding entries in the two other
    series are numerically very close.

    Notes:
        In rare cases, trade prices and midpoints can be the same, but comparison and
        arithmetic operations won't work as expected because of floating point
        approximation error.

        Numpy `numpy.isclose()` can be used to deal with these situations.

    Args:
        series (pd.Series): Series to correct
        s1 (pd.Series): First series to compare
        s2 (pd.Series): Second series to compare
        atol (float, optional): Absolute tolerance for comparison. Defaults to 0.000001.

    Returns:
        pd.Series: Corrected Series
    """
    if s1.index != s2.index:
        raise ValueError("s1 and s2 need to have the same index")
    if s1.index != series.index:
        raise ValueError("series, s1, and s2 need to have the same index")

    sel = np.isclose(s1, s2, atol=atol, rtol=0.0, equal_nan=True)
    series[sel] = pd.NA
    return series


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


def remove_locks_crosses(df: pd.DataFrame, ask_col: str, bid_col: str) -> pd.DataFrame:
    locks = np.isclose(df[ask_col], df[bid_col])
    df = df[~locks]
    crosses = df[bid_col] > df[ask_col]
    return df[~crosses]


def compute_rs_and_pi(
    trade_and_nbbo_df: pd.DataFrame,
    off_nbbo_df: pd.DataFrame,
    delay: timedelta = timedelta(minutes=5),
    suffix: str = "5min",
    track_retail: bool = False,
) -> pd.DataFrame:
    df = merge_future_nbbo(df=trade_and_nbbo_df, nbbo_df=off_nbbo_df, delay=delay)
    df = remove_locks_crosses(df, ask_col="best_ask_next", bid_col="best_bid_next")

    signs = ["LR", "EMO", "CLNV"]
    if track_retail:
        signs += ["BJZ"] + [x + "notBJZ" for x in signs]

    return rs_and_pi(df, signs=signs, suffix=suffix)
