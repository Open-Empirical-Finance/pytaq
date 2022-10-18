Trade-NBBO tables
^^^^^^^^^^^^^^^^^

.. py:function:: TaqDaliy.merge_trades_nbbo(date=None, symbols=None, trade_df=None, off_nbbo_df=None, track_retail=None)
   
   .. Merge trade and NBBO tables based on closest quote before trade.

   Return Trades table along with last quote before trade from NBBO (National Best Bid and Offer) table for given symbols at specific date during normal trading hours.
   Classify trades as "buys" or "sells" using three conventions: LR = Lee and Ready (1991), EMO = Ellis, Michaely, and O'hara (2000) and CLNV = Chakrabarty, Li, Nguyen, and Van ness (2006); determine nbbo midpoint and locked and crossed nbbos.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param trade_df: Trade table. If ``trade_df=None``, get it directly from database using ``date`` and ``symbols``.
   :type trade_df: Pandas DataFrame
   :param off_nbbo_df: Offical Complete NBBO. If ``off_nbbo_df=None``, get it directly from database using ``date`` and ``symbols``.
   :type off_nbbo_df: Pandas DataFrame
   :param track_retail: Compute retail sign following "Tracking retail investor activity" by Ekkehart Boehmer, Charles m. Jones, and Xiaoyan Zhang.
   :type track_retail: bool or None, default track_retail of TaqDaliy instance
   :return: Official Complete NBBO.
   :rtype: Pandas DataFrame



Example
---------

**Example 1:** Retreive Trade-NBBO table by providing `date` and `symbols`.

.. literalinclude:: ../samples/micro/trade_nbbo1.py
  :language: Python

**Example 2:** Retreive Trade-NBBO table from local DataFrames.

.. literalinclude:: ../samples/micro/trade_nbbo2.py
  :language: Python

Both methods have the same output. The first few lines of the output file look like this:

.. csv-table:: 
   :header-rows: 1

    timestamp,symbol,ex,size,price,tr_seqnum,best_bid,best_bidsizeshares,best_ask,best_asksizeshares,midpoint,lock,cross,BuySellLR,BuySellEMO,BuySellCLNV,dollar
    2016-12-07 09:30:00.006411,IBM,P,2,160.6000,2040,160.43,500,160.60,500,160.515,0,0,1.0,1.0,1.0,321.2000
    2016-12-07 09:30:00.006448,IBM,P,2,160.6000,2041,160.43,500,160.60,500,160.515,0,0,1.0,1.0,1.0,321.2000
    2016-12-07 09:30:00.019109,IBM,T,75,160.6000,2050,160.43,500,160.60,500,160.515,0,0,1.0,1.0,1.0,12045.0000
    2016-12-07 09:30:00.019129,IBM,T,37,160.6000,2051,160.43,500,160.60,500,160.515,0,0,1.0,1.0,1.0,5942.2000
    2016-12-07 09:30:00.081717,IBM,T,112,160.6000,2084,160.43,500,160.60,500,160.515,0,0,1.0,1.0,1.0,17987.2000