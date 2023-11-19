from datetime import date, datetime, time
from typing import List, Optional, Union

import pandas as pd

from .common import merge_symbol
from .hj_defaults import HJ_END_TIME_QUOTES, HJ_START_TIME_QUOTES
from .postgresql import build_sql_query

OFF_NBBO_COLS_DB = [
    "date",
    "time_m",
    "sym_root",
    "sym_suffix",
    "best_bid",
    "best_bidsizeshares",
    "best_ask",
    "best_asksizeshares",
]

OFF_NBBO_COLS_CLEAN = [
    "timestamp",
    "symbol",
    "best_bid",
    "best_bidsizeshares",
    "best_ask",
    "best_asksizeshares",
]


def get_official_complete_nbbo_table(date: Union[datetime, date]) -> str:
    """Returns the Official complete NBBO table name for a given date for TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date

    Returns:
        str: Official complete NBBO table name
    """
    return "complete_nbbo_" + date.strftime("%Y%m%d")


def get_official_complete_nbbo_sql_query(
    date: Union[datetime, date],
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = HJ_START_TIME_QUOTES,
    end_time: Optional[Union[datetime, time]] = HJ_END_TIME_QUOTES,
) -> str:
    """Returns a SQL query to retreive the official complete NBBO from TAQ in WRDS

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
        columns=OFF_NBBO_COLS_DB,
        table=get_official_complete_nbbo_table(date),
        library=library,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time,
    )


def clean_official_complete_nbbo_table(nbbo: pd.DataFrame) -> pd.DataFrame:
    """Cleans the official complete NBBO table

    NOTE: This function modifies the original DataFrame. Use `.copy()` to make a copy
    before calling the function if you want to keep the original unchanged.

    Args:
        nbbo (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    nbbo = merge_symbol(nbbo)
    nbbo = nbbo.sort_values(["symbol", "timestamp"])
    return nbbo[OFF_NBBO_COLS_CLEAN]


def get_official_complete_nbbo(
    date: Union[datetime, date],
    conn: "wrds.sql.Connection",
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = HJ_START_TIME_QUOTES,
    end_time: Optional[Union[datetime, time]] = HJ_END_TIME_QUOTES,
) -> pd.DataFrame:
    """Retreives and cleans the official complete NBBO table from TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date
        conn (wrds.sql.Connection): Open connection to WRDS
        library (str, optional): WRDS library to use, otherwise uses default.
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time for quotes.
        end_time (Optional[Union[datetime, time]], optional): End time for quotes.

    Returns:
        pd.DataFrame: Official complete NBBO table
    """
    return clean_official_complete_nbbo_table(
        conn.raw_sql(
            get_official_complete_nbbo_sql_query(
                date=date,
                library=library,
                symbols=symbols,
                start_time=start_time,
                end_time=end_time,
            )
        )
    )
