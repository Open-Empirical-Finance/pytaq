import pandas as pd
import numpy as np

from ..utils.float_approx import float_equal


def locked_rows(asks: pd.Series, bids: pd.Series) -> pd.Series:
    """Identifies rows with a market lock (equal bid and ask)

    Args:
        asks (pd.Series): Ask quotes
        bids (pd.Series): Bid quotes

    Returns:
        pd.Series: Series of boolean indicating the lock status
    """
    return float_equal(s1=asks, s2=bids)


def crossed_rows(asks: pd.Series, bids: pd.Series) -> pd.Series:
    """Identifies rows with a market cross (ask lower than bid)

    Args:
        asks (pd.Series): Ask quotes
        bids (pd.Series): Bid quotes

    Returns:
        pd.Series: Series of boolean indicating the cross status
    """
    return asks < bids


def locked_crossed_rows(asks: pd.Series, bids: pd.Series) -> pd.Series:
    """Identifies rows with a market lock or cross (ask lower or equal to bid)

    Args:
        asks (pd.Series): Ask quotes
        bids (pd.Series): Bid quotes

    Returns:
        pd.Series: Series of boolean indicating the lock/cross status
    """
    return locked_rows(asks, bids) | crossed_rows(asks, bids)


def filter_locks_crosses(
    df: pd.DataFrame, asks: pd.Series, bids: pd.Series
) -> pd.DataFrame:
    """Filters locked and crossed rows from a DataFrame

    Args:
        df (pd.DataFrame): DataFrame to filter
        asks (pd.Series): Ask quotes
        bids (pd.Series): Bid quotes

    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    return df[~locked_rows(asks, bids)]
