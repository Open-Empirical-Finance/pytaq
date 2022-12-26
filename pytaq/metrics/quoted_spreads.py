from datetime import datetime, time, date
from typing import Union, List

import pandas as pd
import numpy as np

from ..cleaning.timestamps import filter_timestamp
from locks_crosses import filter_locks_crosses


def compute_quote_inforce(
    df: pd.DataFrame,
    end_timestamp: datetime,
    groupby_col: Union[str, List[str]] = "symbol",
    timestamp_col: str = "timestamp",
    inforce_col: str = "inforce",
) -> pd.Series:

    # Compute time between each quote
    df[inforce_col] = df.groupby(groupby_col)[timestamp_col].diff().dt.total_seconds()
    df[inforce_col] = df.groupby(groupby_col)[inforce_col].shift(-1)
    # The entries for last quote of the day are missing.
    sel = df.inforce.isnull()
    df.loc[sel, inforce_col] = np.abs(
        (end_timestamp - df.loc[sel, timestamp_col]).dt.total_seconds()
    )


def compute_spreads(df: pd.DataFrame) -> pd.DataFrame:
    # Compute spread measures
    df["quoted_spread_dollar"] = df.best_ask - df.best_bid
    df["quoted_spread_percent"] = np.log(df.best_ask) - np.log(df.best_bid)
    df["best_ofr_depth_dollar"] = df.best_ask * df.best_asksizeshares
    df["best_bid_depth_dollar"] = df.best_bid * df.best_bidsizeshares
    df["best_ofr_depth_share"] = df.best_asksizeshares
    df["best_bid_depth_share"] = df.best_bidsizeshares
    return df


def compute_weighted_averages(
    df: pd.DataFrame,
    measures: List[str],
    groupby_col: Union[str, List[str]] = "symbol",
    inforce_col: str = "inforce",
) -> pd.DataFrame:
    def compute_wspreads(x):
        out = {}
        for m in measures:
            y = x[[m, inforce_col]].dropna()
            if (y[inforce_col].sum() == 0) or (y[inforce_col].isnull().all()):
                out[m] = np.nan
            else:
                out[m] = np.average(y[m], weights=y[inforce_col], axis=0)
        return pd.Series(out)

    return df.groupby(groupby_col)[measures + [inforce_col]].apply(compute_wspreads)


def compute_weighted_spreads(
    date: date,
    off_nbbo_df: pd.DataFrame,
    start_time: time = None,
    end_time: time = None,
) -> Union[pd.DataFrame, None]:
    df = filter_timestamp(
        off_nbbo_df, timestamp=off_nbbo_df.timestamp, start_time=start_time
    ).copy()

    if len(df) == 0:
        return None

    df = compute_quote_inforce(df, end_timestamp=datetime.combine(date, end_time))

    # Delete locked and crossed quotes
    df = filter_locks_crosses(df, asks=df.best_ask, bids=df.best_bid)

    df = compute_spreads(df)

    # Compute daily weighted averages
    return compute_weighted_averages(
        df,
        measures=[
            "quoted_spread_dollar",
            "quoted_spread_percent",
            "best_ofr_depth_dollar",
            "best_bid_depth_dollar",
            "best_ofr_depth_share",
            "best_bid_depth_share",
        ],
    )
