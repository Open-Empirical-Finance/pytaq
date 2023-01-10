from typing import Union, Optional, List
from datetime import datetime, date, time

import pandas as pd

from .postgresql import build_sql_query

DEFAULT_START_TIME_TRADES = time(hour=9, minute=30)
DEFAULT_END_TIME_TRADES = time(hour=16, minute=0)

TRADES_COLS_DB = [
    "date",
    "time_m",
    "ex",
    "sym_root",
    "sym_suffix",
    "size",
    "price",
    "tr_seqnum",
    "tr_scond",
]

TRADES_COLS_CLEAN = [
    "timestamp",
    "symbol",
    "ex",
    "size",
    "price",
    "dollar",
    "tr_seqnum",
    "tr_scond",
]


def get_trade_table(date: Union[datetime, date]) -> str:
    """Returns the trade table name for a given date for TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date

    Returns:
        str: Trade table name
    """
    return "ctm_" + date.strftime("%Y%m%d")


def get_trades_sql_query(
    date: Union[datetime, date],
    library: str = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = DEFAULT_START_TIME_TRADES,
    end_time: Optional[Union[datetime, time]] = DEFAULT_END_TIME_TRADES,
) -> str:
    """Retursn a SQL query to retreive trades from TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date
        library (str, optional): WRDS library to use, otherwise uses default.
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time for trades.
        end_time (Optional[Union[datetime, time]], optional): End time for trades.

    Returns:
        str: SQL query
    """
    table = get_trade_table(date)
    trade_cond = " AND tr_corr = '00' AND price > 0"
    return build_sql_query(
        columns=TRADES_COLS_DB,
        table=table,
        library=library,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time,
        extra_condition=trade_cond,
    )


def clean_trade_table(trades: pd.DataFrame) -> pd.DataFrame:
    """Cleans a trade table retreived from TAQ in WRDS

    NOTE: This function modifies the original DataFrame. Use `.copy()` to make a copy
    before calling the function if you want to keep the original unchanged.

    Args:
        trades (pd.DataFrame): Original trades table from TAQ in WRDS

    Returns:
        pd.DataFrame: Cleaned trades table
    """
    # Merge date and time
    trades["timestamp"] = trades[["date", "time_m"]].apply(
        lambda x: datetime.combine(x["date"], x["time_m"]), axis=1
    )
    # Merge symbol
    trades["symbol"] = trades["sym_root"]
    sel = trades.sym_suffix.notnull()
    trades.loc[sel, "symbol"] = (
        trades.loc[sel, "sym_root"] + " " + trades.loc[sel, "sym_suffix"]
    )
    # Compute dollar value
    trades["dollar"] = trades["price"] * trades["size"]

    return trades[TRADES_COLS_CLEAN]


def get_trades(
    date: Union[datetime, date],
    conn: "wrds.sql.Connection",
    library: str = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = DEFAULT_START_TIME_TRADES,
    end_time: Optional[Union[datetime, time]] = DEFAULT_END_TIME_TRADES,
) -> pd.DataFrame:
    """Retreives and cleans trades from TAQ in WRDS

    Args:
        date (Union[datetime, date]): The requested date
        conn (wrds.sql.Connection): Open connection to WRDS
        library (str, optional): WRDS library to use, otherwise uses default.
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time for trades.
        end_time (Optional[Union[datetime, time]], optional): End time for trades.

    Returns:
        pd.DataFrame: Trades table
    """
    return clean_trade_table(
        conn.raw_sql(
            get_trades_sql_query(
                date=date,
                library=library,
                symbols=symbols,
                start_time=start_time,
                end_time=end_time,
            )
        )
    )