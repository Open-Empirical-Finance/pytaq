""" Default parameters from Holden & Jacobsen """

from datetime import time


HJ_KEEP_QU_COND = {"A", "B", "H", "O", "R", "W"}
HJ_MAX_SPREAD = 5.0
HJ_MAX_QUOTE_CHANGE = 2.5


HJ_START_TIME_TRADES = time(hour=9, minute=30)
HJ_END_TIME_TRADES = time(hour=16, minute=0)
HJ_START_TIME_QUOTES = time(hour=9, minute=0)
HJ_END_TIME_QUOTES = time(hour=16, minute=0)
