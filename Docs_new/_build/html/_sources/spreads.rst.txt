Spreads
^^^^^^^

.. py:function:: TaqDaliy.compute_spreads(date=None, symbols=None, off_nbbo_df=None, start_time_spreads=None, end_time_spreads=None)

   Calculate Quoted Spreads and Depths and return as a DataFrame for given symbols at specific date.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param off_nbbo_df: If ``off_nbbo_df`` is provided , calculate Quoted Spreads and Depths from it as a local file, otherwise get it directly from database.
   :type off_nbbo_df: Pandas DataFrame
   :param start_time_spreads: Start time of quotes to consider for calculating.
   :type start_time_spreads: time object, default 9:30
   :param end_time_spreads: End time of quotes to consider for calculating.
   :type end_time_spreads: time object, default 16:30
   :return: Quoted Spreads and Depths.
   :rtype: Pandas DataFrame


Example
---------

**Example 1:** Calculate Quoted Spreads and Depths by providing `date` and `symbols`.

.. literalinclude:: ../samples/micro/spreads1.py
  :language: Python

**Example 2:** Calculate Quoted Spreads and Depths by providing `off_nbbo_df` local file.

.. literalinclude:: ../samples/micro/spreads2.py
  :language: Python

Both methods have the same output as below:

.. csv-table:: 
   :header-rows: 1

    quoted_spread_dollar,quoted_spread_percent,best_ofr_depth_dollar,best_bid_depth_dollar,best_ofr_depth_share,best_bid_depth_share
    0.034944,0.000215,91575.259793,41712.50821,559.449067,256.56779