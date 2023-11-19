from datetime import date, datetime, time
from typing import Iterable, List, Optional, Union

import pandas as pd

from .common import merge_datetime, merge_symbol
from .hj_defaults import (
    HJ_END_TIME_QUOTES,
    HJ_KEEP_QU_COND,
    HJ_MAX_SPREAD,
    HJ_START_TIME_QUOTES,
)
from .postgresql import build_sql_query

QUOTES_COLS_DB = [
    "date",
    "time_m",
    "ex",
    "sym_root",
    "sym_suffix",
    "bid",
    "bidsiz",
    "ask",
    "asksiz",
    "qu_cond",
    "qu_seqnum",
    "natbbo_ind",
    "qu_source",
    "qu_cancel",
]

QUOTES_COLS_CLEAN = [
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

QUOTES_COLS_FLAGS = ["qu_cond", "natbbo_ind", "qu_source", "qu_cancel"]


def get_quotes_table(date: Union[datetime, date]) -> str:
    """Returns the quotes table name for a given date for TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date

    Returns:
        str: Quotes table name
    """
    return "cqm_" + date.strftime("%Y%m%d")


def get_quotes_sql_query(
    date: Union[datetime, date],
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = HJ_START_TIME_QUOTES,
    end_time: Optional[Union[datetime, time]] = HJ_END_TIME_QUOTES,
) -> str:
    """Returns a SQL query to retreive the quotes from TAQ in WRDS

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
        columns=QUOTES_COLS_DB,
        table=get_quotes_table(date),
        library=library,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time,
    )


def filter_withdrawned_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    """Filters withdrawned quotes from the quotes table

    NOTE: See H&J (2014) page 11 for details.

    Args:
        quotes (pd.DataFrame): Quotes table

    Returns:
        pd.DataFrame: Quotes table without withdrawned quotes
    """
    return quotes[
        ~(
            quotes.ask.isnull()
            | (quotes.ask <= 0)
            | quotes.asksiz.isnull()
            | (quotes.asksiz <= 0)
            | quotes.bid.isnull()
            | (quotes.bid <= 0)
            | quotes.bidsiz.isnull()
            | (quotes.bidsiz <= 0)
        )
    ]


def filter_quote_table(
    quotes: pd.DataFrame,
    keep_qu_cond: Optional[Iterable[str]] = HJ_KEEP_QU_COND,
    delete_canceled_quotes: bool = True,
    delete_crossed_markets: bool = True,
    delete_withdrawned_quotes: bool = True,
    delete_abnormal_spreads: bool = True,
    max_spread: float = HJ_MAX_SPREAD,
    nbbo_only: bool = True,
) -> pd.DataFrame:
    """Filters the quote table of the TAQ database based on specified criteria.

    NOTE: This function modifies the original DataFrame. Use `.copy()` to make a copy
    before calling the function if you want to keep the original unchanged.

    Args:
        quotes (pd.DataFrame): The input quote table from the TAQ database.
        keep_qu_cond (Optional[Iterable[str]], default=HJ_KEEP_QU_COND): A list of quote conditions to keep.
        delete_canceled_quotes (bool, default=True): Whether to delete canceled quotes.
        delete_crossed_markets (bool, default=True): Whether to delete quotes with crossed markets.
        delete_withdrawned_quotes (bool, default=True): Whether to delete withdrawned quotes.
        delete_abnormal_spreads (bool, default=True): Whether to delete quotes with abnormal spreads.
        max_spread (float, default=HJ_MAX_SPREAD): The maximum spread allowed for a quote.
        nbbo_only (bool, default=True): Whether to keep only NBBO quotes.

    Returns:
        pd.DataFrame: The filtered quote table.

    """
    if keep_qu_cond is not None and len(keep_qu_cond) > 0:
        # Quote condition must be normal
        quotes = quotes[quotes.qu_cond.isin(keep_qu_cond)]

    if delete_canceled_quotes:
        # Delete if canceled
        quotes = quotes[quotes.qu_cancel != "B"]

    if delete_crossed_markets:
        # Delete abnormal crossed markets
        quotes = quotes[quotes.bid <= quotes.ask]

    if delete_abnormal_spreads:
        # Delete abnormal spreads
        quotes["spread"] = quotes.ask - quotes.bid
        quotes = quotes[quotes.spread <= max_spread]

    if delete_withdrawned_quotes:
        # Delete withdrawned quotes
        quotes = filter_withdrawned_quotes(quotes)

    # Keep only those to be merged with NBBO file
    if nbbo_only:
        quotes = quotes[
            ((quotes.qu_source == "C") & (quotes.natbbo_ind == "1"))
            | ((quotes.qu_source == "N") & (quotes.natbbo_ind == "4"))
        ]

    return quotes


def clean_quote_table(
    quotes: pd.DataFrame,
    keep_qu_cond: Optional[Iterable[str]] = HJ_KEEP_QU_COND,
    delete_canceled_quotes: bool = True,
    delete_crossed_markets: bool = True,
    delete_withdrawned_quotes: bool = True,
    delete_abnormal_spreads: bool = True,
    max_spread: float = HJ_MAX_SPREAD,
    nbbo_only: bool = True,
    output_flags: bool = False,
) -> pd.DataFrame:
    """Cleans a quote table retreived from TAQ in WRDS

    NOTE: This function modifies the original DataFrame. Use `.copy()` to make a copy
    before calling the function if you want to keep the original unchanged.

    Args:
        quotes (pd.DataFrame): Original quote table from TAQ in WRDS
        keep_qu_cond (Optional[Iterable[str]], default=HJ_KEEP_QU_COND): A list of quote conditions to keep.
        delete_canceled_quotes (bool, default=True): Whether to delete canceled quotes.
        delete_crossed_markets (bool, default=True): Whether to delete quotes with crossed markets.
        delete_withdrawned_quotes (bool, default=True): Whether to delete withdrawned quotes.
        delete_abnormal_spreads (bool, default=True): Whether to delete quotes with abnormal spreads.
        max_spread (float, default=HJ_MAX_SPREAD): The maximum spread allowed for a quote.
        nbbo_only (bool, default=True): Whether to keep only NBBO quotes.
        output_flags (bool, default=False): Whether to output flags.

    Returns:
        pd.DataFrame: Cleaned quote table

    """
    quotes = merge_symbol(merge_datetime(quotes))

    quotes = filter_quote_table(
        quotes=quotes,
        keep_qu_cond=keep_qu_cond,
        delete_canceled_quotes=delete_canceled_quotes,
        delete_crossed_markets=delete_crossed_markets,
        delete_withdrawned_quotes=delete_withdrawned_quotes,
        delete_abnormal_spreads=delete_abnormal_spreads,
        max_spread=max_spread,
        nbbo_only=nbbo_only,
    )

    quotes = quotes.rename(
        columns={"ask": "best_ask", "bid": "best_bid", "ex": "best_bidex"}
    )
    quotes["best_askex"] = quotes["best_bidex"]

    # Bid/ask size are in round lots
    quotes["best_bidsizeshares"] = quotes.bidsiz * 100
    quotes["best_asksizeshares"] = quotes.asksiz * 100

    if output_flags:
        return quotes[QUOTES_COLS_CLEAN + QUOTES_COLS_FLAGS]
    return quotes[QUOTES_COLS_CLEAN]


def get_quotes(
    date: Union[datetime, date],
    conn: "wrds.sql.Connection",
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = HJ_START_TIME_QUOTES,
    end_time: Optional[Union[datetime, time]] = HJ_END_TIME_QUOTES,
    keep_qu_cond: Optional[Iterable[str]] = HJ_KEEP_QU_COND,
    delete_canceled_quotes: bool = True,
    delete_crossed_markets: bool = True,
    delete_withdrawned_quotes: bool = True,
    delete_abnormal_spreads: bool = True,
    max_spread: float = HJ_MAX_SPREAD,
    nbbo_only: bool = True,
    output_flags: bool = False,
) -> pd.DataFrame:
    """Retreives and cleans quotes from TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date
        conn (wrds.sql.Connection): WRDS connection
        library (str, optional): WRDS library to use, otherwise uses default.
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time for quotes.
        end_time (Optional[Union[datetime, time]], optional): End time for quotes.
        keep_qu_cond (Optional[Iterable[str]], optional): A list of quote conditions to keep. Defaults to HJ_KEEP_QU_COND.
        delete_canceled_quotes (bool, optional): Whether to delete canceled quotes. Defaults to True.
        delete_crossed_markets (bool, optional): Whether to delete quotes with crossed markets. Defaults to True.
        delete_withdrawned_quotes (bool, optional): Whether to delete withdrawned quotes. Defaults to True.
        delete_abnormal_spreads (bool, optional): Whether to delete quotes with abnormal spreads. Defaults to True.
        max_spread (float, optional): The maximum spread allowed for a quote. Defaults to HJ_MAX_SPREAD.
        nbbo_only (bool, optional): Whether to keep only NBBO quotes. Defaults to True.
        output_flags (bool, optional): Whether to output flags. Defaults to False.

    Returns:
        pd.DataFrame: Quotes table


    """
    return clean_quote_table(
        conn.raw_sql(
            get_quotes_sql_query(
                date=date,
                library=library,
                symbols=symbols,
                start_time=start_time,
                end_time=end_time,
            )
        ),
        keep_qu_cond=keep_qu_cond,
        delete_canceled_quotes=delete_canceled_quotes,
        delete_crossed_markets=delete_crossed_markets,
        delete_withdrawned_quotes=delete_withdrawned_quotes,
        delete_abnormal_spreads=delete_abnormal_spreads,
        max_spread=max_spread,
        nbbo_only=nbbo_only,
        output_flags=output_flags,
    )
