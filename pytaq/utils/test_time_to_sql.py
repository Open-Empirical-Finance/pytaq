from datetime import datetime, time

from .time_to_sql import time_to_sql


def test_time_to_sql() -> None:
    assert time_to_sql(datetime(2022, 2, 2, 13, 32, 43, 120693)) == '"13:32:43.121"'
    assert time_to_sql(time(13, 32, 43, 120693)) == '"13:32:43.121"'

    assert time_to_sql(time(7, 1, 1, 100000), quote_char="'") == "'07:01:01.100'"
