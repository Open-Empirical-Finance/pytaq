Realized Spreads & Price Impact
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DataFrame
---------

.. py:function:: TaqDaliy.compute_rs_and_pi(date=None, symbols=None, trade_and_nbbo_df=None, off_nbbo_df=None, delay=timedelta(minutes=5), suffix='5min', track_retail=None)

   Calculate realized spreads and price impacts based on three conventions: LR = Lee and Ready (1991), EMO = Ellis, Michaely, and O'hara (2000)
   and CLNV = Chakrabarty, Li, Nguyen, and Van ness (2006); find the nbbo midpoint for a specific delay subsequent to the trade.

   :param delay: A specific delay subsequent to the trade to find the nbbo midpoint.
   :type delay: timedelta object, default 5 minutes
   :param suffix: To determine columns related to delay.
   :type suffix: str, default '5min'
   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param trade_and_nbbo_df: Trade-NBBO table. If ``trade_and_nbbo_df=None``, get it directly from database using ``date`` and ``symbols``.
   :type trade_and_nbbo_df: Pandas DataFrame
   :param off_nbbo_df: Offical Complete NBBO. If ``off_nbbo_df=None``, get it directly from database using ``date`` and ``symbols``.
   :type off_nbbo_df: Pandas DataFrame
   :param track_retail: Compute retail sign following "Tracking retail investor activity" by Ekkehart Boehmer, Charles m. Jones, and Xiaoyan Zhang.
   :type track_retail: bool or None, default track_retail of TaqDaliy instance
   :return: Realized Spreads and Price Impacts.
   :rtype: Pandas DataFrame



**Example 1:** Calculate Realized Spreads and Price Impacts DataFrame by providing `date` and `symbols`.

.. literalinclude:: ../samples/micro/rs_pi1.py
  :language: Python

**Example 2:** Calculate Realized Spreads and Price Impacts DataFrame by providing `trade_and_nbbo_df` and ``off_nbbo_df`` local files.

.. literalinclude:: ../samples/micro/rs_pi2.py
  :language: Python

Both methods have the same output as below:

.. csv-table:: 
   :header-rows: 1

    timestamp,symbol,ex,size,price,tr_seqnum,best_bid,best_bidsizeshares,best_bidex,best_ask,best_asksizeshares,best_askex,qu_seqnum,midpoint,lock,cross,BuySellLR,BuySellEMO,BuySellCLNV,dollar,best_bid_next,best_ask_next,midpoint_next,DollarRealizedSpread_LR5min,PercentRealizedSpread_LR5min,DollarPriceImpact_LR5min,PercentPriceImpact_LR5min,DollarRealizedSpread_EMO5min,PercentRealizedSpread_EMO5min,DollarPriceImpact_EMO5min,PercentPriceImpact_EMO5min,DollarRealizedSpread_CLNV5min,PercentRealizedSpread_CLNV5min,DollarPriceImpact_CLNV5min,PercentPriceImpact_CLNV5min
    2016-12-07 09:30:00.006411,IBM,P,2,160.6000,2040,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,321.2000,160.83,160.87,160.850,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170
    2016-12-07 09:30:00.006448,IBM,P,2,160.6000,2041,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,321.2000,160.83,160.87,160.850,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170
    2016-12-07 09:30:00.019109,IBM,T,75,160.6000,2050,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,12045.0000,160.83,160.87,160.850,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170
    2016-12-07 09:30:00.019129,IBM,T,37,160.6000,2051,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,5942.2000,160.83,160.87,160.850,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170
    2016-12-07 09:30:00.081717,IBM,T,112,160.6000,2084,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,17987.2000,160.83,160.87,160.850,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170,-5.000000e-01,-3.110904e-03,6.700000e-01,0.004170

Average
-------

**Example 3:** Also, we can calculate Simple (Ave), Dollar-Weighted (DW), and Share-Weighted (SW) :ref:`averages <averages>` of Realized Spreads and Price Impacts:

.. literalinclude:: ../samples/micro/rs_pi3.py
  :language: Python


.. csv-table:: 
   :header-rows: 1

    DollarRealizedSpread_LR5min_Ave,DollarRealizedSpread_LR5min_DW,DollarRealizedSpread_LR5min_SW,PercentRealizedSpread_LR5min_Ave,PercentRealizedSpread_LR5min_DW,PercentRealizedSpread_LR5min_SW,DollarPriceImpact_LR5min_Ave,DollarPriceImpact_LR5min_DW,DollarPriceImpact_LR5min_SW,PercentPriceImpact_LR5min_Ave,PercentPriceImpact_LR5min_DW,PercentPriceImpact_LR5min_SW,DollarRealizedSpread_EMO5min_Ave,DollarRealizedSpread_EMO5min_DW,DollarRealizedSpread_EMO5min_SW,PercentRealizedSpread_EMO5min_Ave,PercentRealizedSpread_EMO5min_DW,PercentRealizedSpread_EMO5min_SW,DollarPriceImpact_EMO5min_Ave,DollarPriceImpact_EMO5min_DW,DollarPriceImpact_EMO5min_SW,PercentPriceImpact_EMO5min_Ave,PercentPriceImpact_EMO5min_DW,PercentPriceImpact_EMO5min_SW,DollarRealizedSpread_CLNV5min_Ave,DollarRealizedSpread_CLNV5min_DW,DollarRealizedSpread_CLNV5min_SW,PercentRealizedSpread_CLNV5min_Ave,PercentRealizedSpread_CLNV5min_DW,PercentRealizedSpread_CLNV5min_SW,DollarPriceImpact_CLNV5min_Ave,DollarPriceImpact_CLNV5min_DW,DollarPriceImpact_CLNV5min_SW,PercentPriceImpact_CLNV5min_Ave,PercentPriceImpact_CLNV5min_DW,PercentPriceImpact_CLNV5min_SW
    -0.01708,-0.018547,-0.018522,-0.000105,-0.000114,-0.000113,0.03844,0.039654,0.039669,0.000236,0.000243,0.000243,-0.014481,-0.020958,-0.021005,-0.000089,-0.000129,-0.000129,0.032667,0.03822,0.038286,0.0002,0.000234,0.000235,-0.018017,-0.024185,-0.024349,-0.000111,-0.000149,-0.00015,0.038344,0.04373,0.043921,0.000236,0.000269,0.00027