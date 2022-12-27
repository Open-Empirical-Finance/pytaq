import pandas as pd
import numpy as np

"""
    Notes:
    In rare cases, trade prices and midpoints or two quotes can be the same, but
    comparison and arithmetic operations don't work as expected because of floating
    point approximation error.

    Numpy' `numpy.isclose()` can be used to deal with these situations.
"""

DEFAULT_ATOL = 0.000001


def float_equal(s1: pd.Series, s2: pd.Series, atol: float = DEFAULT_ATOL) -> pd.Series:
    """Compares two series for approximate equality.

    Args:
        s1 (pd.Series): First series to compare
        s2 (pd.Series): Second series to compare
        atol (float, optional): Absolute tolerance for comparison. Defaults to 0.000001.

    Returns:
        pd.Series: Series of boolean indicating approximate equality
    """
    if s1.index != s2.index:
        raise ValueError("s1 and s2 need the same index")

    series = pd.Series(np.isclose(s1, s2, atol=atol, rtol=0.0, equal_nan=True))
    series.index = s1.index
    return series


def float_zero(s: pd.Series, atol: float = DEFAULT_ATOL) -> pd.Series:
    """Compares a series for approximate equality with zero.

    Args:
        s (pd.Series): Series to compare with zero.
        atol (float, optional): Absolute tolerance for comparison. Defaults to 0.000001.

    Returns:
        pd.Series: Series of boolean indicating approximate equality with zero
    """
    return float_equal(s, pd.Series(0.0, index=s.index), atol=atol)


def correct_float_approx(
    series: pd.Series, s1: pd.Series, s2: pd.Series, atol: float = DEFAULT_ATOL
) -> pd.Series:
    """Changes values of a Series to NA when the corresponding entries in the two other
    series are numerically very close.

    Args:
        series (pd.Series): Series to correct
        s1 (pd.Series): First series to compare
        s2 (pd.Series): Second series to compare
        atol (float, optional): Absolute tolerance for comparison. Defaults to 0.000001.

    Returns:
        pd.Series: Corrected Series
    """
    equal = float_equal(s1=s1, s2=s1, atol=atol)

    if equal.index != series.index:
        raise ValueError("series, s1, and s2 need the same index")

    series[equal] = pd.NA
    return series
