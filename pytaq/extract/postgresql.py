from typing import List, Optional, Union
from datetime import datetime, time

from utils.time_to_sql import time_to_sql

DEFAULT_LIBRARY = "taqmsec"


def select_statement(
    columns: List[str], table: str, library: Optional[str] = None
) -> str:
    """Returns a SQL select statement to retreive a list of columns from a WRDS table

    Args:
        columns (List[str]): List of columns to retreive
        table (str): WRDS table to use
        library (Optional[str], optional): WRDS library to use. Defaults to "taqmsec".

    Returns:
        str: Select statement
    """
    if library is None:
        library = DEFAULT_LIBRARY
    return f"SELECT {', '.join(columns)} FROM {library}.{table}"


def symbol_condition(symbols: Optional[List[str]] = None) -> str:
    """Returns a SQL where condition to select the symbols and exclude symbols with no suffixes

    Args:
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.

    Returns:
        str: Where condition
    """
    if symbols is not None and len(symbols) > 0:
        return (
            " WHERE sym_root IN ('" + "','".join(symbols) + "') AND sym_suffix IS NULL"
        )
    else:
        return " WHERE sym_suffix IS NULL"


def time_condition(
    start_time: Optional[Union[datetime, time]] = None,
    end_time: Optional[Union[datetime, time]] = None,
) -> str:
    """Returns a SQL condition to filter on time

    Args:
        start_time (Optional[Union[datetime, time]], optional): Start time, or None to start from the beginning. Defaults to None.
        end_time (Optional[Union[datetime, time]], optional): Start time, or None to go until the end. Defaults to None.

    Returns:
        str: SQL condition
    """
    if start_time and end_time:
        return (
            " AND (time_m BETWEEN "
            + time_to_sql(start_time, "'")
            + " AND "
            + time_to_sql(end_time, "'")
            + ")"
        )
    elif start_time:
        return " AND (time_m > " + time_to_sql(start_time, "'") + ")"
    elif end_time:
        return " AND (time_m < " + time_to_sql(end_time, "'") + ")"
    else:
        return ""


def build_sql_query(
    columns: List[str],
    table: str,
    library: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    start_time: Optional[Union[datetime, time]] = None,
    end_time: Optional[Union[datetime, time]] = None,
    extra_condition: str = "",
) -> str:
    """Returns a SQL query statement to retreive a filtered list of columns from a WRDS table

    Args:
        columns (List[str]): List of columns to retreive
        table (str): WRDS table to use
        library (Optional[str], optional): WRDS library to use. Defaults to "taqmsec".
        symbols (Optional[List[str]], optional): List of symbols to retreive, or None for all symbols.
        start_time (Optional[Union[datetime, time]], optional): Start time, or None to start from the beginning. Defaults to None.
        end_time (Optional[Union[datetime, time]], optional): Start time, or None to go until the end. Defaults to None.
        extra_condition (str, optional): Extra condition to append at the end of the query. Defaults to "".

    Returns:
        str: SQL query
    """
    return (
        select_statement(columns=columns, table=table, library=library)
        + symbol_condition(symbols=symbols)
        + time_condition(start_time=start_time, end_time=end_time)
        + extra_condition
    )
