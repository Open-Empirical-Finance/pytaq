#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 17:32:02 2020

@author: vincentgregoire
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta

from utils.time_to_sql import time_to_sql


class TaqDaily:
    def __init__(self, method=None, db=None, track_retail=False):
        if (method == "PostgreSQL") | (method == "SASPy"):
            self.method = method
            self.db = db
        elif method is None:
            self.method = method
            self.db = None
        else:
            raise ValueError(f"Unknown method for TaqDaily: {str(method)}")

        self.taq_library = "taqmsec"

        # Holden & Jacobsen defaults
        self.keep_qu_cond = ["A", "B", "H", "O", "R", "W"]
        # If quoted spread > $5 and bid (ask) has decreased (increased) by
        # $2.50 then remove that quote.
        self.max_spread = 5
        self.max_quote_change = 2.5

        self.delete_canceled_quotes = True
        self.delete_empty_quotes = True
        self.delete_crossed_markets = True
        self.delete_withdrawned_quotes = True
        self.delete_abnormal_spreads = True
        self.keep_changes_only = True

        self.start_time_quotes = time(hour=9, minute=0)
        self.end_time_quotes = time(hour=16, minute=0)
        self.start_time_trades = time(hour=9, minute=30)
        self.end_time_trades = time(hour=16, minute=0)

        # Should we compute trade sign for retail trades
        self.track_retail = track_retail

    #%%  Symbols SASPy query
    def get_nbbo_symbols_saspy(self, date):
        nbbo_table = "nbbom_" + date.strftime("%Y%m%d")

        sas_proc = (
            "proc sql;\n create table symbols as select distinct(sym_root) as symbol\n from "
            + self.taq_library
            + "."
            + nbbo_table
            + ";\n quit;"
        )
        self.db.submit(sas_proc)
        sas_symbols = self.db.sasdata(libref="work", table="symbols")
        df = sas_symbols.to_df()
        return list(df.symbol.unique())

    #%%  Get symbol list from nbbo table
    def get_nbbo_symbols(self, date):
        if self.method == "PostgreSQL":
            # TODO
            raise NotImplementedError(
                "Method PostgreSQL not yet supported for get_nbbo_symbols()"
            )
        elif self.method == "SASPy":
            return self.get_nbbo_symbols_saspy(date)
        elif self.method is None:
            raise ValueError("Method needed for get_nbbo_symbols()")
        else:
            raise ValueError(f"Unknown method for TaqDaily: {str(self.method)}")

    #%%  NBBO PostgreSQL query
    def get_nbbo_table_postgresql(self, date, symbols=None):
        nbbo_table = "nbbom_" + date.strftime("%Y%m%d")

        # Columns to retreive from database
        nbbo_cols = [
            "date",
            "time_m",
            "sym_root",
            "sym_suffix",
            "best_bid",
            "best_bidsiz",
            "best_ask",
            "best_asksiz",
            "qu_cond",
            "qu_seqnum",
            "best_askex",
            "best_bidex",
            "qu_cancel",
        ]

        select_cond = (
            "SELECT "
            + ", ".join(nbbo_cols)
            + " FROM "
            + self.taq_library
            + "."
            + nbbo_table
        )

        # This is for common stocks only, can tweak to have other symbols
        if symbols is not None:
            symbol_cond = (
                " WHERE sym_root IN ('"
                + "','".join(symbols)
                + "') AND sym_suffix IS NULL"
            )
        else:
            symbol_cond = " WHERE sym_suffix IS NULL"

        # Retreive quotes during normal trading hours, starting before market
        # open to ensure we have NBBO quotes at the beginning of the day.
        time_cond = (
            " AND (time_m BETWEEN "
            + time_to_sql(self.start_time_quotes, "'")
            + " AND "
            + time_to_sql(self.end_time_quotes, "'")
            + ")"
        )

        sql_query = select_cond + symbol_cond + time_cond
        return self.db.raw_sql(sql_query)

    #%%  NBBO sas query

    def get_nbbo_table_saspy(self, date, symbols=None):
        nbbo_table = "nbbom_" + date.strftime("%Y%m%d")

        # Columns to retreive from database
        nbbo_cols = [
            "date",
            "time_m",
            "sym_root",
            "sym_suffix",
            "best_bid",
            "best_bidsiz",
            "best_ask",
            "best_asksiz",
            "qu_cond",
            "qu_seqnum",
            "best_askex",
            "best_bidex",
            "qu_cancel",
        ]

        sas_proc = (
            "data DailyNBBO;\n set taqmsec."
            + nbbo_table
            + " (keep = "
            + " ".join(nbbo_cols)
            + ');\n where sym_root in ("'
            + '","'.join(symbols)
            + '") and sym_suffix = "" and (('
            + time_to_sql(self.start_time_quotes)
            + "t) <= time_m <= ("
            + time_to_sql(self.end_time_quotes)
            + "t));\n run;"
        )

        self.db.submit(sas_proc)
        sas_nbbo = self.db.sasdata(libref="work", table="DailyNBBO")
        df = sas_nbbo.to_df()
        df.columns = [c.lower() for c in df.columns]

        df["time_m"] = df.time_m.dt.time

        return df

    #%%  NBBO
    # TODO: add support for other than common stocks
    #       Add step 4 (changes only)
    def get_nbbo_table(self, date, symbols=None, output_flags=False):
        if self.method == "PostgreSQL":
            df = self.get_nbbo_table_postgresql(date, symbols)
        elif self.method == "SASPy":
            df = self.get_nbbo_table_saspy(date, symbols)
        elif self.method is None:
            raise ValueError("Method needed for get_nbbo_table()")
        else:
            raise ValueError(f"Unknown method for TaqDaily: {str(self.method)}")

        # Merge date and time
        df["timestamp"] = df[["date", "time_m"]].apply(
            lambda x: datetime.combine(x["date"], x["time_m"]), axis=1
        )

        return self.clean_nbbo_table(df, output_flags=output_flags)

    #%% NBBO cleanup
    def clean_nbbo_table(self, df, output_flags=False):
        # Post-SQL query cleanup

        # Merge symbol
        df["symbol"] = df["sym_root"]
        sel = df.sym_suffix.notnull()
        df.loc[sel, "symbol"] = (
            df.loc[sel, "sym_root"] + " " + df.loc[sel, "sym_suffix"]
        )

        if self.keep_qu_cond is not None:
            # Quote condition must be normal
            df = df[df.qu_cond.isin(self.keep_qu_cond)]

        if self.delete_canceled_quotes:
            # Delete if canceled
            df = df[df.qu_cancel != "B"]

        if self.delete_empty_quotes:
            # TODO: double-check, it seems this steps is actually wrong, you
            # should keep empty quotes. (step from H&J)
            # Delete if both ask and bid (or their size) are 0 or None
            del_sel = (
                ((df.best_ask <= 0) & (df.best_bid <= 0))
                | ((df.best_asksiz <= 0) & (df.best_bidsiz <= 0))
                | (df.best_ask.isnull() & df.best_bid.isnull())
                | (df.best_asksiz.isnull() & df.best_bidsiz.isnull())
            )

            df = df[~del_sel]

        df["spread"] = df.best_ask - df.best_bid
        df["midpoint"] = (df.best_ask + df.best_bid) / 2

        # If size or price = 0 or null, set price and size to null
        ask_sel = (
            (df.best_ask <= 0)
            | df.best_ask.isnull()
            | (df.best_asksiz <= 0)
            | df.best_asksiz.isnull()
        )
        df.loc[ask_sel, ["best_ask", "best_asksiz"]] = np.nan

        # If size or price = 0 or null, set price and size to null
        bid_sel = (
            (df.best_bid <= 0)
            | df.best_bid.isnull()
            | (df.best_bidsiz <= 0)
            | df.best_bidsiz.isnull()
        )
        df.loc[bid_sel, ["best_bid", "best_bidsiz"]] = np.nan

        # Bid/ask size are in round lots
        df["best_bidsizeshares"] = df.best_bidsiz * 100
        df["best_asksizeshares"] = df.best_asksiz * 100

        del df["best_bidsiz"]
        del df["best_asksiz"]

        if self.delete_abnormal_spreads:
            # Get previous midpoint
            # Note: H&J only sorts on sym_root, not sym_suffix.
            #       They also sort on date, not timestamps (this is weird)
            df = df.sort_values(["symbol", "timestamp"])

            df["lmid"] = df.groupby(["symbol"])["midpoint"].shift()

            # If quoted spread > $5 and bid (ask) has decreased (increased) by
            # $2.50 then remove that quote.
            # Note: not sure this is good in all cases, i.e. when looking at
            # large events.
            # Note that here behaviour is sligthly different than in SAS
            # Because of the way SAS handles comparison with missing value
            # (i.e. a missin value is always smaller than a number)
            # So if first row has spread greater than max spread, best_bid
            # will be set to missing by SAS but not best_ask. Python
            # won't set any to null.
            bid_sel = (df.spread > self.max_spread) & (
                df.best_bid < df.lmid - self.max_quote_change
            )
            df.loc[bid_sel, ["best_bid", "best_bidsizeshares"]] = np.nan
            ask_sel = (df.spread > self.max_spread) & (
                df.best_ask > df.lmid + self.max_quote_change
            )
            df.loc[ask_sel, ["best_ask", "best_asksizeshares"]] = np.nan

        if self.keep_changes_only:
            # Keep only changes
            # There is a slight difference here with the SAS code because
            # in Python np.nan == np.nan is False. Should not affect end
            # results, but this means consecutive entries with all null symbols
            # won't be removed.
            grp = df.groupby("symbol")
            sel = (
                (df["best_ask"] != grp["best_ask"].shift())
                | (df["best_bid"] != grp["best_bid"].shift())
                | (df["best_bidsizeshares"] != grp["best_bidsizeshares"].shift())
                | (df["best_asksizeshares"] != grp["best_asksizeshares"].shift())
            )
            df = df[sel]

        # Keep only relevant columns
        # Columns to output
        nbbo_out_cols = [
            "timestamp",
            "symbol",
            "best_bid",
            "best_bidsizeshares",
            "best_bidex",
            "best_ask",
            "best_asksizeshares",
            "best_askex",
            "qu_seqnum",
        ]

        if output_flags:
            nbbo_out_cols += ["qu_cond", "qu_cancel"]

        return df[nbbo_out_cols]

    #%% Quotes PostgreSQL

    def get_quote_table_postgresql(self, date, symbols=None):
        quote_table = "cqm_" + date.strftime("%Y%m%d")

        quote_cols = [
            "date",
            "time_m",
            "ex",
            "sym_root",
            "sym_suffix",
            "bid",
            "bidsiz",
            "ask",
            "asksiz",
            "qu_cond",
            "qu_seqnum",
            "natbbo_ind",
            "qu_source",
            "qu_cancel",
        ]

        select_cond = (
            "SELECT "
            + ", ".join(quote_cols)
            + " FROM "
            + self.taq_library
            + "."
            + quote_table
        )

        # This is for common stocks only, can tweak to have other symbols
        if symbols is not None:
            symbol_cond = (
                " WHERE sym_root IN ('"
                + "','".join(symbols)
                + "') AND sym_suffix IS NULL"
            )
        else:
            symbol_cond = " WHERE sym_suffix IS NULL"

        # Retreive quotes during normal trading hours, starting before market
        # open to ensure we have NBBO quotes at the beginning of the day.
        time_cond = (
            " AND (time_m BETWEEN "
            + time_to_sql(self.start_time_quotes, "'")
            + " AND "
            + time_to_sql(self.end_time_quotes, "'")
            + ")"
        )

        sql_query = select_cond + symbol_cond + time_cond
        return self.db.raw_sql(sql_query)

    #%% Quotes saspy

    def get_quote_table_saspy(self, date, symbols=None):
        quote_table = "cqm_" + date.strftime("%Y%m%d")

        quote_cols = [
            "date",
            "time_m",
            "ex",
            "sym_root",
            "sym_suffix",
            "bid",
            "bidsiz",
            "ask",
            "asksiz",
            "qu_cond",
            "qu_seqnum",
            "natbbo_ind",
            "qu_source",
            "qu_cancel",
        ]

        sas_proc = (
            "data DailyQuote;\n set taqmsec."
            + quote_table
            + " (keep = "
            + " ".join(quote_cols)
            + ")"
            + ';\n where sym_root in ("'
            + '","'.join(symbols)
            + '") and sym_suffix = "" and (('
            + time_to_sql(self.start_time_quotes)
            + "t) <= time_m <= ("
            + time_to_sql(self.end_time_quotes)
            + "t));\n run;"
        )

        self.db.submit(sas_proc)
        sas_quote = self.db.sasdata(libref="work", table="DailyQuote")
        df = sas_quote.to_df()
        df.columns = [c.lower() for c in df.columns]

        df["time_m"] = df.time_m.dt.time

        return df

    #%% Quotes

    def get_quote_table(self, date, symbols=None, nbbo_only=True, output_flags=False):
        if self.method == "PostgreSQL":
            df = self.get_quote_table_postgresql(date, symbols)
        elif self.method == "SASPy":
            df = self.get_quote_table_saspy(date, symbols)
        elif self.method is None:
            raise ValueError("Method needed for get_quote_table()")
        else:
            raise ValueError(f"Unknown method for TaqDaily: {str(self.method)}")

        # Merge date and time
        df["timestamp"] = df[["date", "time_m"]].apply(
            lambda x: datetime.combine(x["date"], x["time_m"]), axis=1
        )

        return self.clean_quote_table(
            df, nbbo_only=nbbo_only, output_flags=output_flags
        )

    def clean_quote_table(self, df, nbbo_only=True, output_flags=False):
        # Merge symbol
        df["symbol"] = df["sym_root"]
        sel = df.sym_suffix.notnull()
        df.loc[sel, "symbol"] = (
            df.loc[sel, "sym_root"] + " " + df.loc[sel, "sym_suffix"]
        )

        df["spread"] = df.ask - df.bid

        if self.keep_qu_cond is not None:
            # Quote condition must be normal
            df = df[df.qu_cond.isin(self.keep_qu_cond)]

        if self.delete_canceled_quotes:
            # Delete if canceled
            df = df[df.qu_cancel != "B"]

        if self.delete_crossed_markets:
            # Delete abnormal crossed markets
            df = df[df.bid <= df.ask]

        if self.delete_abnormal_spreads:
            # Delete abnormal spreads
            df = df[df.spread <= self.max_spread]

        if self.delete_withdrawned_quotes:
            # Delete withdrawn quotes (see H&J (2014) page 11 for details)
            del_sel = (
                df.ask.isnull()
                | (df.ask <= 0)
                | df.asksiz.isnull()
                | (df.asksiz <= 0)
                | df.bid.isnull()
                | (df.bid <= 0)
                | df.bidsiz.isnull()
                | (df.bidsiz <= 0)
            )
            df = df[~del_sel]

        df = df.rename(
            columns={"ask": "best_ask", "bid": "best_bid", "ex": "best_bidex"}
        )
        df["best_askex"] = df["best_bidex"]

        # Bid/ask size are in round lots
        df["best_bidsizeshares"] = df.bidsiz * 100
        df["best_asksizeshares"] = df.asksiz * 100

        del df["bidsiz"]
        del df["asksiz"]

        # Keep only those to be merged with NBBO file
        if nbbo_only:
            sel = ((df.qu_source == "C") & (df.natbbo_ind == "1")) | (
                (df.qu_source == "N") & (df.natbbo_ind == "4")
            )
            df = df[sel]

        quote_out_cols = [
            "timestamp",
            "symbol",
            "best_bid",
            "best_bidsizeshares",
            "best_bidex",
            "best_ask",
            "best_asksizeshares",
            "best_askex",
            "qu_seqnum",
        ]

        if output_flags:
            quote_out_cols += ["qu_cond", "natbbo_ind", "qu_source", "qu_cancel"]
        return df[quote_out_cols]

    #%% Trades PostgreSQL

    def get_trade_table_postgresql(self, date, symbols=None, get_cond=False):
        trade_table = "ctm_" + date.strftime("%Y%m%d")

        trade_cols = [
            "date",
            "time_m",
            "ex",
            "sym_root",
            "sym_suffix",
            "size",
            "price",
            "tr_seqnum",
        ]
        if get_cond:
            trade_cols += ["tr_scond"]

        select_cond = (
            "SELECT "
            + ", ".join(trade_cols)
            + " FROM "
            + self.taq_library
            + "."
            + trade_table
        )

        # This is for common stocks only, can tweak to have other symbols
        if symbols is not None:
            symbol_cond = (
                " WHERE sym_root IN ('"
                + "','".join(symbols)
                + "') AND sym_suffix IS NULL"
            )
        else:
            symbol_cond = " WHERE sym_suffix IS NULL"

        # Retreive quotes during normal trading hours, starting before market
        # open to ensure we have NBBO quotes at the beginning of the day.
        time_cond = (
            " AND (time_m BETWEEN "
            + time_to_sql(self.start_time_trades, "'")
            + " AND "
            + time_to_sql(self.end_time_trades, "'")
            + ")"
        )

        # Retreive only correct trades
        trade_cond = " AND tr_corr = '00' AND price > 0"

        sql_query = select_cond + symbol_cond + trade_cond + time_cond
        return self.db.raw_sql(sql_query)

    #%% Trades SASPy

    def get_trade_table_saspy(self, date, symbols=None, get_cond=False):
        trade_table = "ctm_" + date.strftime("%Y%m%d")

        trade_cols = [
            "date",
            "time_m",
            "ex",
            "sym_root",
            "sym_suffix",
            "size",
            "price",
            "tr_seqnum",
            "tr_corr",
        ]
        if get_cond:
            trade_cols += ["tr_scond"]

        sas_proc = (
            "data DailyTrade;\n set taqmsec."
            + trade_table
            + " (keep = "
            + " ".join(trade_cols)
            + ")"
            ';\n where sym_root in ("'
            + '","'.join(symbols)
            + '") and sym_suffix = ""  AND tr_corr = "00" AND price > 0 and (('
            + time_to_sql(self.start_time_trades)
            + "t) <= time_m <= ("
            + time_to_sql(self.end_time_trades)
            + "t));\n run;"
        )

        self.db.submit(sas_proc)
        sas_trade = self.db.sasdata(libref="work", table="DailyTrade")
        df = sas_trade.to_df()
        df.columns = [c.lower() for c in df.columns]
        del df["tr_corr"]

        df["time_m"] = df.time_m.dt.time
        return df

    #%% Trades

    def get_trade_table(self, date, symbols=None, get_cond=False):
        if self.method == "PostgreSQL":
            df = self.get_trade_table_postgresql(date, symbols, get_cond)
        elif self.method == "SASPy":
            df = self.get_trade_table_saspy(date, symbols, get_cond)
        elif self.method is None:
            raise ValueError("Method needed for get_trade_table()")
        else:
            raise ValueError(f"Unknown method for TaqDaily: {str(self.method)}")

        # Merge date and time
        df["timestamp"] = df[["date", "time_m"]].apply(
            lambda x: datetime.combine(x["date"], x["time_m"]), axis=1
        )

        return self.clean_trade_table(df, get_cond=get_cond)

    def clean_trade_table(self, df, get_cond=False):
        # Merge symbol
        df["symbol"] = df["sym_root"]
        sel = df.sym_suffix.notnull()
        df.loc[sel, "symbol"] = (
            df.loc[sel, "sym_root"] + " " + df.loc[sel, "sym_suffix"]
        )
        trade_out_cols = ["timestamp", "symbol", "ex", "size", "price", "tr_seqnum"]
        if get_cond:
            trade_out_cols += ["tr_scond"]

        return df[trade_out_cols]

    #%% Official Complete NBBO PostgreSQL

    def get_official_complete_nbbo_postgresql(self, date, symbols=None):
        nbbo_table = "complete_nbbo_" + date.strftime("%Y%m%d")

        # Columns to retreive from database
        nbbo_cols = [
            "date",
            "time_m",
            "sym_root",
            "sym_suffix",
            "best_bid",
            "best_bidsizeshares",
            "best_ask",
            "best_asksizeshares",
        ]

        select_cond = (
            "SELECT "
            + ", ".join(nbbo_cols)
            + " FROM "
            + self.taq_library
            + "."
            + nbbo_table
        )

        # This is for common stocks only, can tweak to have other symbols
        if symbols is not None:
            symbol_cond = (
                " WHERE sym_root IN ('"
                + "','".join(symbols)
                + "') AND sym_suffix IS NULL"
            )
        else:
            symbol_cond = " WHERE sym_suffix IS NULL"

        # Retreive quotes during normal trading hours, starting before market
        # open to ensure we have NBBO quotes at the beginning of the day.
        time_cond = (
            " AND (time_m BETWEEN "
            + time_to_sql(self.start_time_quotes, "'")
            + " AND "
            + time_to_sql(self.end_time_quotes, "'")
            + ")"
        )

        sql_query = select_cond + symbol_cond + time_cond
        return self.db.raw_sql(sql_query)

    #%% Official Complete NBBO SASPy

    def get_official_complete_nbbo_saspy(self, date, symbols=None):
        nbbo_table = "complete_nbbo_" + date.strftime("%Y%m%d")

        # Columns to retreive from database
        nbbo_cols = [
            "date",
            "time_m",
            "sym_root",
            "sym_suffix",
            "best_bid",
            "best_bidsizeshares",
            "best_ask",
            "best_asksizeshares",
        ]

        sas_proc = (
            "data DailyNBBO;\n set taqmsec."
            + nbbo_table
            + " (keep = "
            + " ".join(nbbo_cols)
            + ');\n where sym_root in ("'
            + '","'.join(symbols)
            + '") and sym_suffix = "" and (('
            + time_to_sql(self.start_time_quotes)
            + "t) <= time_m <= ("
            + time_to_sql(self.end_time_quotes)
            + "t));\n run;"
        )

        self.db.submit(sas_proc)
        sas_nbbo = self.db.sasdata(libref="work", table="DailyNBBO")
        df = sas_nbbo.to_df()
        df.columns = [c.lower() for c in df.columns]

        df["time_m"] = df.time_m.dt.time

        return df

    #%% Official Complete NBBO

    def get_official_complete_nbbo(
        self, date=None, symbols=None, nbbo_df=None, quote_df=None
    ):
        if (nbbo_df is None) | (quote_df is None):
            if self.method == "PostgreSQL":
                df = self.get_official_complete_nbbo_postgresql(date, symbols)
            elif self.method == "SASPy":
                df = self.get_official_complete_nbbo_saspy(date, symbols)
            elif self.method is None:
                raise ValueError("Method needed for get_official_complete_nbbo()")
            else:
                raise ValueError(f"Unknown method for TaqDaily: {str(self.method)}")
            # Merge date and time
            df["timestamp"] = df[["date", "time_m"]].apply(
                lambda x: datetime.combine(x["date"], x["time_m"]), axis=1
            )
            df = self.clean_official_complete_nbbo(df)
        else:
            # Note: Could use append() instead of concat()
            # df = nbbo_df.append(quote_df)
            df = pd.concat([nbbo_df, quote_df])
            df = df.sort_values(["symbol", "timestamp", "qu_seqnum"])

        # Remove duplicate quotes at same microsecond (keep last one based
        # on sequence number)

        if self.keep_changes_only:
            df = df.groupby(["symbol", "timestamp"]).last().reset_index()

        # # Drop obs with no change in obs.
        # df = df.groupby(['symbol', 'best_bid', 'best_bidsizeshares',
        #                  'best_bidex', 'best_ask', 'best_asksizeshares',
        #                  'best_askex']).first().reset_index()

        return df

    def clean_official_complete_nbbo(self, df):
        # Post-SQL query cleanup

        # Merge symbol
        df["symbol"] = df["sym_root"]
        sel = df.sym_suffix.notnull()
        df.loc[sel, "symbol"] = (
            df.loc[sel, "sym_root"] + " " + df.loc[sel, "sym_suffix"]
        )

        # Keep only relevant columns
        # Columns to output
        nbbo_out_cols = [
            "timestamp",
            "symbol",
            "best_bid",
            "best_bidsizeshares",
            "best_ask",
            "best_asksizeshares",
        ]

        df = df.sort_values(["symbol", "timestamp"])

        return df[nbbo_out_cols]

    #%%% Merge trades and NBBO
    # We merge the quote in effect at trade time

    def merge_trades_nbbo(
        self,
        date=None,
        symbols=None,
        trade_df=None,
        off_nbbo_df=None,
        track_retail=None,
    ):
        if track_retail is None:
            track_retail = self.track_retail

        if trade_df is None:
            trade_df = self.get_trade_table(date=date, symbols=symbols)
        if off_nbbo_df is None:
            off_nbbo_df = self.get_official_complete_nbbo(date=date, symbols=symbols)

        trade_df = trade_df.sort_values(["timestamp", "symbol"])
        off_nbbo_df = off_nbbo_df.sort_values(["timestamp", "symbol"])

        # Note: could use dask dataframe dd.merge_asof
        df = pd.merge_asof(
            trade_df,
            off_nbbo_df,
            on="timestamp",
            by="symbol",
            allow_exact_matches=False,
            suffixes=("", "_quote"),
        )

        # Note: H&J code is wrong I think,
        # df = pd.merge_asof(trade_df, off_nbbo_df, on='timestamp',
        #            by='symbol', allow_exact_matches=False,
        #            suffixes=('','_quote'))

        df["midpoint"] = (df["best_bid"] + df["best_ask"]) / 2
        df["lock"] = 0
        sel = df["best_bid"] == df["best_ask"]
        df.loc[sel, "lock"] = 1
        df["cross"] = 0
        sel = df["best_bid"] > df["best_ask"]
        df.loc[sel, "cross"] = 1

        # Trade direction (tick test)
        df = df.sort_values(["timestamp", "symbol"])
        # Note: could use dask array da.sign
        df["dir"] = np.sign(df.groupby(["symbol"])["price"].diff())
        df.loc[df["dir"] == 0, "dir"] = np.nan
        df["dir"] = df.groupby(["symbol"])["dir"].fillna(method="ffill")

        # First classification test: use tick test
        df["BuySellLR"] = df["dir"]
        df["BuySellEMO"] = df["dir"]
        df["BuySellCLNV"] = df["dir"]

        # Second classification test: use specified conditions of LR, EMO and
        # CLNV.
        sel_not_lc = (df["lock"] == 0) & (df["cross"] == 0)

        df.loc[sel_not_lc & (df["price"] > df["midpoint"]), "BuySellLR"] = 1
        df.loc[sel_not_lc & (df["price"] < df["midpoint"]), "BuySellLR"] = -1

        df.loc[sel_not_lc & (df["price"] == df["best_ask"]), "BuySellEMO"] = 1
        df.loc[sel_not_lc & (df["price"] == df["best_bid"]), "BuySellEMO"] = -1

        df["ofr30"] = df["best_ask"] - 0.3 * (df["best_ask"] - df["best_bid"])
        df["bid30"] = df["best_bid"] + 0.3 * (df["best_ask"] - df["best_bid"])
        sel = (df["price"] >= df["ofr30"]) & (df["price"] <= df["best_ask"])
        df.loc[sel_not_lc & sel, "BuySellCLNV"] = 1
        sel = (df["price"] <= df["bid30"]) & (df["price"] >= df["best_bid"])
        df.loc[sel_not_lc & sel, "BuySellCLNV"] = -1

        for x in ["dir", "ofr30", "bid30"]:
            del df[x]

        if track_retail:
            # Compute retail sign following "TRACKING RETAIL INVESTOR ACTIVITY"
            # by EKKEHART BOEHMER, CHARLES M. JONES, and XIAOYAN ZHANG
            def compute_retail_sign(s):
                out = np.full(s.shape, np.nan)
                for i in range(s.shape[0]):
                    z = 100 * np.mod(s[i], 0.01)
                    if (z >= 1e-4) & (z < 0.4):
                        out[i] = -1.0
                    if (z >= 0.6) & (z < (1 - 1e-4)):
                        out[i] = 1.0
                return out

            sel = df["ex"] == "D"
            df["BuySellBJZ"] = np.nan
            df.loc[sel, "BuySellBJZ"] = compute_retail_sign(df.loc[sel, "price"].values)

            sel = df["BuySellBJZ"].isnull()
            for x in ["LR", "EMO", "CLNV"]:
                df["BuySell" + x + "notBJZ"] = np.nan
                df.loc[sel, "BuySell" + x + "notBJZ"] = df.loc[sel, "BuySell" + x]

        df["dollar"] = df["price"] * df["size"]

        return df
