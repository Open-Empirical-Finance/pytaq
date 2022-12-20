import pandas as pd
import numpy as np


def compute_effective_spreads(trade_and_nbbo_df: pd.DataFrame):
    df = trade_and_nbbo_df.copy()

    sel = (df.cross == 1) | (df.lock == 1)
    df = df[~sel]

    df["DollarEffectiveSpread"] = np.abs(df["price"] - df["midpoint"]) * 2
    df["PercentEffectiveSpread"] = (
        np.abs(np.log(df["price"]) - np.log(df["midpoint"])) * 2
    )
    return df
