Effective Spreads
^^^^^^^^^^^^^^^^^

DataFrame
---------

.. py:function:: TaqDaliy.compute_effective_spreads(date=None, symbols=None, trade_and_nbbo_df=None)

   Accept Trade-NBBO DataFrame, calculate `Dollar Effective Spreads` and `Percent Effective Spreads`,
   remove crossed and locked quotes, and return as Effetive Spreads DataFrame for given symbols at specific date.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param trade_and_nbbo_df: If ``trade_and_nbbo_df`` is provided , calculate Effective Spreads DataFrame from it as a local file, otherwise get it directly from database.
   :type trade_and_nbbo_df: Pandas DataFrame
   :return: Effetive Spreads.
   :rtype: Pandas DataFrame



**Example 1:** Calculate Effetive Spreads DataFrame by providing `date` and `symbols`.

.. literalinclude:: ../samples/micro/eff_spreads1.py
  :language: Python

**Example 2:** Calculate Effetive Spreads DataFrame by providing `trade_and_nbbo_df` local file.

.. literalinclude:: ../samples/micro/eff_spreads2.py
  :language: Python

Both methods have the same output as below:

.. csv-table:: 
   :header-rows: 1

    timestamp,symbol,ex,size,price,tr_seqnum,best_bid,best_bidsizeshares,best_bidex,best_ask,best_asksizeshares,best_askex,qu_seqnum,midpoint,lock,cross,BuySellLR,BuySellEMO,BuySellCLNV,dollar,DollarEffectiveSpread,PercentEffectiveSpread
    2016-12-07 09:30:00.006411,IBM,P,2,160.6000,2040,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,321.2000,1.700000e-01,1.058811e-03
    2016-12-07 09:30:00.006448,IBM,P,2,160.6000,2041,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,321.2000,1.700000e-01,1.058811e-03
    2016-12-07 09:30:00.019109,IBM,T,75,160.6000,2050,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,12045.0000,1.700000e-01,1.058811e-03
    2016-12-07 09:30:00.019129,IBM,T,37,160.6000,2051,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,5942.2000,1.700000e-01,1.058811e-03
    2016-12-07 09:30:00.081717,IBM,T,112,160.6000,2084,160.43,500.0,Z,160.60,500.0,P,511415,160.515,0,0,1.0,1.0,1.0,17987.2000,1.700000e-01,1.058811e-03

Average
-------

**Example 3:** Also, we can calculate Simple (Ave), Dollar-Weighted (DW), and Share-Weighted (SW) :ref:`averages <averages>` of Dollar Effective Spreads and Percent Effective Spreads:

.. literalinclude:: ../samples/micro/eff_spreads3.py
  :language: Python


.. csv-table:: 
   :header-rows: 1

    DollarEffectiveSpread_Ave,DollarEffectiveSpread_DW,DollarEffectiveSpread_SW,PercentEffectiveSpread_Ave,PercentEffectiveSpread_DW,PercentEffectiveSpread_SW
    0.021439,0.021186,0.021226,0.000132,0.00013,0.00013