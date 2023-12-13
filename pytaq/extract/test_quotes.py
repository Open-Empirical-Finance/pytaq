import pandas as pd
import pytest

from .quotes import filter_withdrawned_quotes

# Sample data for testing
sample_data = pd.DataFrame(
    {
        "bid": [1.0, 2.0, None, 4.0, 5.0, 0.0],
        "ask": [2.0, None, 3.5, 6.0, 5.5, 1.0],
        "bidsiz": [100, 200, 300, None, 0, 50],
        "asksiz": [100, None, 0, 400, 500, 50],
    }
)

# Expected result
expected_result = pd.DataFrame(
    {
        "bid": [1.0],
        "ask": [2.0],
        "bidsiz": [100.0],
        "asksiz": [100.0],
    }
)


@pytest.mark.parametrize(
    "quotes, expected",
    [(sample_data, expected_result)],
)
def test_filter_withdrawned_quotes(quotes: pd.DataFrame, expected: pd.DataFrame):
    result = filter_withdrawned_quotes(quotes)
    pd.testing.assert_frame_equal(result, expected)
