from typing import Union, Optional
from datetime import time

import pandas as pd


def filter_timestamp(
    df: pd.DataFrame,
    timestamp: Union[str, pd.Series],
    start_time: Optional[time] = None,
    end_time: Optional[time] = None,
) -> pd.DataFrame:
    """Filters a DataFrame based on timestamp

    Args:
        df (pd.DataFrame): DataFrame to filter
        timestamp (Union[str, pd.Series]): Timestamp to use for filtering
        start_time (Optional[time], optional): Start time
        end_time (Optional[time], optional): End time

    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if isinstance(timestamp, str):
        timestamp = df[timestamp]
    elif isinstance(timestamp, pd.Series):
        if timestamp.index != df.index:
            raise ValueError("df and timestamp should have the same index")
    else:
        raise ValueError("timestamp should be a pandas Series or a column name.")

    if start_time is not None and end_time is not None:
        return df[(timestamp.dt.time >= start_time) & (timestamp.dt.time < end_time)]
    elif start_time is not None:
        return df[timestamp.dt.time >= start_time]
    elif end_time is not None:
        return df[timestamp.dt.time < end_time]
    return df
