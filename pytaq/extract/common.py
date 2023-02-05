from datetime import datetime

import pandas as pd


def merge_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Merges date and time columns.

    Args:
        df (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    # Merge date and time
    df["timestamp"] = df[["date", "time_m"]].apply(
        lambda x: datetime.combine(x["date"], x["time_m"]), axis=1
    )
    return df


def merge_symbol(df: pd.DataFrame) -> pd.DataFrame:
    """Merges symbol and sym_root columns.

    Args:
        df (pd.DataFrame): Original DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    # Merge symbol
    df["symbol"] = df["sym_root"]
    sel = df.sym_suffix.notnull()
    df.loc[sel, "symbol"] = df.loc[sel, "sym_root"] + " " + df.loc[sel, "sym_suffix"]
    return df
