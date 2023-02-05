import pandas as pd


def merge_trades_official_nbbo(
    trades: pd.DataFrame,
    off_nbbo: pd.DataFrame,
) -> pd.DataFrame:
    """Merges the trades with the corresponding official NBBO at the time.

    Args:
        trades (pd.DataFrame): Trades
        off_nbbo (pd.DataFrame): Official NBBO

    Returns:
        pd.DataFrame: Trades with the corresponding NBBO
    """
    trades = trades.sort_values(["timestamp", "symbol"])
    off_nbbo = off_nbbo.sort_values(["timestamp", "symbol"])

    return pd.merge_asof(
        trades,
        off_nbbo,
        on="timestamp",
        by="symbol",
        allow_exact_matches=False,
        suffixes=("", "_quote"),
    )
