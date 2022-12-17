from typing import Union
from datetime import datetime, time


def time_to_sql(ts: Union[datetime, time], quote_char: str = '"') -> str:
    """Converts a time or datetime object to a SQL string representation.

    Args:
        ts (Union[datetime, time]): Time to convert
        quote_char (str, optional): Character to use for quotes. Defaults to '"'.

    Returns:
        str: SQL string representation
    """
    ms = int(round(ts.microsecond / 1000))
    return f"{quote_char}{ts.hour:02}:{ts.minute:02}:{ts.second:02}.{ms:03}{quote_char}"
