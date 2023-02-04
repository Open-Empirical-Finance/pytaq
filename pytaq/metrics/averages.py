from typing import Iterable, Tuple, Union
import pandas as pd
import numpy as np


def compute_averages(
    df: pd.DataFrame,
    cols: Iterable[str],
    group: str = "symbol",
    weights: Iterable[Tuple[Union[str, None], str]] = [
        (None, ""),
    ],
) -> pd.DataFrame:
    """Computes simple and weighted averages of a DataFrame columns'.

    Averages are computed for every column of `df` in `cols`, grouped by `group`.
    Weighting to apply are provided as tuples in `weights`, where the first element
    if the weighting column (or None for a simple average) and the second element is
    the suffix to append to the resulting column.

    Args:
        df (pd.DataFrame): DataFrame to operate on
        cols (Iterable[str]): Columns to compute the average
        group (str): Columns to group by
        weights (Iterable[Tuple(Union[str, None], str)]): Weights to apply. Defaults to [ (None, ""), ].

    Returns:
        pd.DataFrame: DataFrame of the averages
    """
    weight_cols = [x[0] for x in weights if x[0] is not None]

    def compute_wavg(x):
        out = {}
        # For each, compute average, share-weighted and dollar-weighted
        for c in cols:
            y = x[[c] + weight_cols].dropna()

            for weight_col, suffix in weights:
                try:
                    out[f"{c}{suffix}"] = np.average(
                        y[c],
                        weights=y[weight_col] if weight_col is not None else None,
                        axis=0,
                    )
                except Exception:
                    out[f"{c}{suffix}"] = np.nan

        return pd.Series(out)

    return df.groupby(group)[list(cols) + weight_cols].apply(compute_wavg)


def compute_averages_ave_sw_dw(
    df: pd.DataFrame,
    measures: Iterable[str],
    simple: bool = True,
    dollar_weighted: bool = True,
    share_weighted: bool = True,
) -> pd.DataFrame:
    """Computes simple and weighted averages by symbol for multiple measure.'.

    Args:
        df (pd.DataFrame): DataFrame to operate on
        measures (Iterable[str]): _description_
        simple (bool, optional): _description_. Defaults to True.
        dollar_weighted (bool, optional): _description_. Defaults to True.
        share_weighted (bool, optional): _description_. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame of the averages
    """

    weights = []
    if simple:
        weights.append((None, "_Ave"))
    if dollar_weighted:
        weights.append(("dollar", "_DW"))
    if share_weighted:
        weights.append(("size", "_SW"))

    return compute_averages(df=df, cols=measures, group="symbol", weights=weights)
