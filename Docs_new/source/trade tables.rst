Trade tables
^^^^^^^^^^^^

.. py:function:: TaqDaliy.get_trade_table(date, symbols=None, get_cond=False)

   Return a cleaned trade table for given symbols at specific date during normal trading hours.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param get_cond: If True, incorporate column ``tr_scond``.
   :type get_cond: bool, default False
   :return: Trade table.
   :rtype: Pandas DataFrame


Cleaning
---------
* Retreive only correct trades:

  * Keep only rows where ``tr_scond = 00`` and ``price > 0``


Example
---------

.. literalinclude:: ../samples/micro/trade.py
  :language: Python

The first few lines of the output file look like this:

.. csv-table:: 
   :header-rows: 1

    timestamp,symbol,ex,size,price,tr_seqnum
    2016-12-07 09:30:00.006411,IBM,P,2,160.6000,2040
    2016-12-07 09:30:00.006448,IBM,P,2,160.6000,2041
    2016-12-07 09:30:00.019109,IBM,T,75,160.6000,2050
    2016-12-07 09:30:00.019129,IBM,T,37,160.6000,2051
    2016-12-07 09:30:00.081717,IBM,T,112,160.6000,2084