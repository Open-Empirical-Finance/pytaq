""" Default parameters from Holden & Jacobsen """

from datetime import time

HJ_KEEP_QU_COND = {"A", "B", "H", "O", "R", "W"}
HJ_MAX_SPREAD = 5.0
HJ_MAX_QUOTE_CHANGE = 2.5

HJ_DELETE_CANCELED_QUOTES = True
HJ_DELETE_EMPTY_QUOTES = True
HJ_DELETE_ABNORMAL_SPREADS = True
HJ_DELETE_WITHDRAWN_QUOTES = True
HJ_DELETE_CROSSED_MARKETS = True
HJ_KEEP_CHANGES_ONLY = True
HJ_TRACK_RETAIL = False


HJ_START_TIME_TRADES = time(hour=9, minute=30)
HJ_END_TIME_TRADES = time(hour=16, minute=0)
HJ_START_TIME_QUOTES = time(hour=9, minute=0)
HJ_END_TIME_QUOTES = time(hour=16, minute=0)
