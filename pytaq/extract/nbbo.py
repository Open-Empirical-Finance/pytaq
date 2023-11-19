from datetime import date, datetime, time
from typing import Iterable, List, Optional, Union

import numpy as np
import pandas as pd

from .common import merge_symbol
from .hj_defaults import (
    HJ_DELETE_ABNORMAL_SPREADS,
    HJ_DELETE_CANCELED_QUOTES,
    HJ_DELETE_EMPTY_QUOTES,
    HJ_END_TIME_QUOTES,
    HJ_KEEP_CHANGES_ONLY,
    HJ_KEEP_QU_COND,
    HJ_MAX_QUOTE_CHANGE,
    HJ_MAX_SPREAD,
    HJ_START_TIME_QUOTES,
)
from .postgresql import build_sql_query

NBBO_COLS_DB = [
    "date",
    "time_m",
    "sym_root",
    "sym_suffix",
    "best_bid",
    "best_bidsiz",
    "best_ask",
    "best_asksiz",
    "qu_cond",
    "qu_seqnum",
    "best_askex",
    "best_bidex",
    "qu_cancel",
]

NBBO_COLS_CLEAN = [
    "timestamp",
    "symbol",
    "best_bid",
    "best_bidsizeshares",
    "best_bidex",
    "best_ask",
    "best_asksizeshares",
    "best_askex",
    "qu_seqnum",
]

NBBO_COLS_FLAGS = [
    "qu_cond",
    "qu_cancel",
]


def get_nbbo_table(date: Union[datetime, date]) -> str:
    """Returns the NBBO table name for a given date for TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date

    Returns:
        str: NBBO table name
    """
    return "nbbom_" + date.strftime("%Y%m%d")


def get_nbbo_sql_query(
    date: Union[datetime, date],
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = HJ_START_TIME_QUOTES,
    end_time: Optional[Union[datetime, time]] = HJ_END_TIME_QUOTES,
) -> str:
    """Returns a SQL query to retreive the NBBO from TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date
        library (str, optional): WRDS library to use, otherwise uses default.
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time for quotes.
        end_time (Optional[Union[datetime, time]], optional): End time for quotes.

    Returns:
        str: SQL query
    """
    return build_sql_query(
        columns=NBBO_COLS_DB,
        table=get_nbbo_table(date),
        library=library,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time,
    )


def filter_empty_quotes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete if both ask and bid (or their size) are 0 or None

    Args:
        df (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """

    # TODO: double-check, it seems this steps is actually wrong, you
    # should keep empty quotes. (This step is from H&J).
    # Delete if both ask and bid (or their size) are 0 or None
    empty_sel = (
        ((df.best_ask <= 0) & (df.best_bid <= 0))
        | ((df.best_asksiz <= 0) & (df.best_bidsiz <= 0))
        | (df.best_ask.isnull() & df.best_bid.isnull())
        | (df.best_asksiz.isnull() & df.best_bidsiz.isnull())
    )

    df = df[~empty_sel]

    return df


def compute_spreads_best_quotes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute spreads and best quotes

    NOTE: This function modifies the original DataFrame. Use `.copy()` to make a copy
    before calling the function if you want to keep the original unchanged.

    Args:
        df (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """

    df["spread"] = df.best_ask - df.best_bid
    df["midpoint"] = (df.best_ask + df.best_bid) / 2

    # If size or price = 0 or null, set price and size to null
    ask_sel = (
        (df.best_ask <= 0)
        | df.best_ask.isnull()
        | (df.best_asksiz <= 0)
        | df.best_asksiz.isnull()
    )
    df.loc[ask_sel, ["best_ask", "best_asksiz"]] = np.nan

    # If size or price = 0 or null, set price and size to null
    bid_sel = (
        (df.best_bid <= 0)
        | df.best_bid.isnull()
        | (df.best_bidsiz <= 0)
        | df.best_bidsiz.isnull()
    )
    df.loc[bid_sel, ["best_bid", "best_bidsiz"]] = np.nan

    # Bid/ask size are in round lots
    df["best_bidsizeshares"] = df.best_bidsiz * 100
    df["best_asksizeshares"] = df.best_asksiz * 100

    del df["best_bidsiz"]
    del df["best_asksiz"]
    return df


def filter_abnormal_spreads(
    df: pd.DataFrame, max_spread: float, max_quote_change: float
) -> pd.DataFrame:
    """
    Filter rows if quoted spread or quote change too large.

    Args:
        df (pd.DataFrame): Original DataFrame
        max_spread (float): Maximum quoted spread, in dollars
        max_quote_change (float): Maximum quote change, in dollars

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """

    # Get previous midpoint
    # Note: H&J only sorts on sym_root, not sym_suffix.
    #       They also sort on date, not timestamps (this is weird)
    df = df.sort_values(["symbol", "timestamp"])

    df["lmid"] = df.groupby(["symbol"])["midpoint"].shift()

    # If quoted spread > $5 and bid (ask) has decreased (increased) by
    # $2.50 then remove that quote.
    # Note: not sure this is good in all cases, i.e. when looking at
    # large events.
    # Note that here behaviour is sligthly different than in SAS
    # Because of the way SAS handles comparison with missing value
    # (i.e. a missing value is always smaller than a number)
    # So if first row has spread greater than max spread, best_bid
    # will be set to missing by SAS but not best_ask. Python
    # won't set any to null.
    bid_sel = (df.spread > max_spread) & (df.best_bid < df.lmid - max_quote_change)
    df.loc[bid_sel, ["best_bid", "best_bidsizeshares"]] = np.nan
    ask_sel = (df.spread > max_spread) & (df.best_ask > df.lmid + max_quote_change)
    df.loc[ask_sel, ["best_ask", "best_asksizeshares"]] = np.nan

    return df


def filter_changes_only(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only changes, i.e. consecutive entries with different quotes

    Args:
        df (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """

    # Keep only changes
    # There is a slight difference here with the SAS code because
    # in Python np.nan == np.nan is False. Should not affect end
    # results, but this means consecutive entries with all null symbols
    # won't be removed. We add a second condition to remove those.
    grp = df.groupby("symbol")
    sel = (
        (df["best_ask"] != grp["best_ask"].shift())
        | (df["best_bid"] != grp["best_bid"].shift())
        | (df["best_bidsizeshares"] != grp["best_bidsizeshares"].shift())
        | (df["best_asksizeshares"] != grp["best_asksizeshares"].shift())
    )

    sel_all_null = (
        df["best_ask"].isnull()
        & df["best_bid"].isnull()
        & df["best_bidsizeshares"].isnull()
        & df["best_asksizeshares"].isnull()
        & grp["best_ask"].shift().isnull()
        & grp["best_bid"].shift().isnull()
        & grp["best_bidsizeshares"].shift().isnull()
        & grp["best_asksizeshares"].shift().isnull()
    )

    df = df[sel | sel_all_null]
    return df


def clean_nbbo_table(
    nbbo: pd.DataFrame,
    keep_qu_cond: Iterable[str] = HJ_KEEP_QU_COND,
    delete_canceled_quotes: bool = HJ_DELETE_CANCELED_QUOTES,
    delete_empty_quotes: bool = HJ_DELETE_EMPTY_QUOTES,
    delete_abnormal_spreads: bool = HJ_DELETE_ABNORMAL_SPREADS,
    keep_changes_only: bool = HJ_KEEP_CHANGES_ONLY,
    max_spread: float = HJ_MAX_SPREAD,
    max_quote_change: float = HJ_MAX_QUOTE_CHANGE,
    output_flags: bool = False,
):
    """Cleans a NBBO table retreived from TAQ in WRDS

    NOTE: This function modifies the original DataFrame. Use `.copy()` to make a copy
    before calling the function if you want to keep the original unchanged.

    Args:
        nbbo (pd.DataFrame): Original NBBO table from TAQ in WRDS
        keep_qu_cond (Iterable[str], optional): Quote conditions to keep, or None for all conditions.
        delete_canceled_quotes (bool, optional): Delete canceled quotes.
        delete_empty_quotes (bool, optional): Delete empty quotes.
        delete_abnormal_spreads (bool, optional): Delete abnormal spreads.
        keep_changes_only (bool, optional): Keep only changes.
        max_spread (float, optional): Maximum quoted spread, in dollars.
        max_quote_change (float, optional): Maximum quote change, in dollars.
        output_flags (bool, optional): Output quote flags.

    Returns:
        pd.DataFrame: Cleaned NBBO table
    """

    nbbo = merge_symbol(nbbo)

    if keep_qu_cond is not None:
        # Quote condition must be normal
        nbbo = nbbo[nbbo.qu_cond.isin(keep_qu_cond)]
    if delete_canceled_quotes:
        # Delete if canceled
        nbbo = nbbo[nbbo.qu_cancel != "B"]
    if delete_empty_quotes:
        nbbo = filter_empty_quotes(nbbo)

    nbbo = compute_spreads_best_quotes(nbbo)

    if delete_abnormal_spreads:
        nbbo = filter_abnormal_spreads(
            nbbo, max_spread=max_spread, max_quote_change=max_quote_change
        )

    if keep_changes_only:
        nbbo = filter_changes_only(nbbo)

    # Keep only relevant columns
    # Columns to output
    nbbo_out_cols = (
        NBBO_COLS_CLEAN + NBBO_COLS_FLAGS if output_flags else NBBO_COLS_CLEAN
    )

    return nbbo[nbbo_out_cols]


def get_nbbo(
    date: Union[datetime, date],
    conn: "wrds.sql.Connection",
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = HJ_START_TIME_QUOTES,
    end_time: Optional[Union[datetime, time]] = HJ_END_TIME_QUOTES,
    keep_qu_cond: Iterable[str] = HJ_KEEP_QU_COND,
    delete_canceled_quotes: bool = HJ_DELETE_CANCELED_QUOTES,
    delete_empty_quotes: bool = HJ_DELETE_EMPTY_QUOTES,
    delete_abnormal_spreads: bool = HJ_DELETE_ABNORMAL_SPREADS,
    keep_changes_only: bool = HJ_KEEP_CHANGES_ONLY,
    max_spread: float = HJ_MAX_SPREAD,
    max_quote_change: float = HJ_MAX_QUOTE_CHANGE,
    output_flags: bool = False,
) -> pd.DataFrame:
    """Retreives and cleans the NBBO from TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date
        conn (wrds.sql.Connection): Open connection to WRDS
        library (str, optional): WRDS library to use, otherwise uses default.
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time for quotes.
        end_time (Optional[Union[datetime, time]], optional): End time for quotes.
        keep_qu_cond (Iterable[str], optional): Quote conditions to keep, or None for all conditions.
        delete_canceled_quotes (bool, optional): Delete canceled quotes.
        delete_empty_quotes (bool, optional): Delete empty quotes.
        delete_abnormal_spreads (bool, optional): Delete abnormal spreads.
        keep_changes_only (bool, optional): Keep only changes.
        max_spread (float, optional): Maximum quoted spread, in dollars.
        max_quote_change (float, optional): Maximum quote change, in dollars.
        output_flags (bool, optional): Output quote flags.

    Returns:
        pd.DataFrame: NBBO table
    """
    return clean_nbbo(
        conn.raw_sql(
            get_nbbo_sql_query(
                date=date,
                library=library,
                symbols=symbols,
                start_time=start_time,
                end_time=end_time,
            )
        ),
        keep_qu_cond=keep_qu_cond,
        delete_canceled_quotes=delete_canceled_quotes,
        delete_empty_quotes=delete_empty_quotes,
        delete_abnormal_spreads=delete_abnormal_spreads,
        keep_changes_only=keep_changes_only,
        max_spread=max_spread,
        max_quote_change=max_quote_change,
        output_flags=output_flags,
    )
