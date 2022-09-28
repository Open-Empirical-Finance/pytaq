Official Complete NBBO tables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:function:: TaqDaliy.get_official_complete_nbbo(date=None, symbols=None, nbbo_df=None, quote_df=None)

   Return Official Complete NBBO (National Best Bid and Offer) table for given symbols at specific date during normal quoting hours.
   The nbbo file is incomplete by itself (if a single exchange has the best bid and offer, the quote is included in the quotes file, but not the nbbo file). To create the complete official nbbo, we need to merge with the quotes file.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param nbbo_df(quote_df): If both ``nbbo_df`` and ``quote_df`` are provided, retreive Offical NBBO by merging them together (local files), otherwise get it directly from database.
   :type nbbo_df(quote_df): Pandas DataFrame
   :return: Official Complete NBBO.
   :rtype: Pandas DataFrame


.. Tip::

    If you are using local files, beware to set option ``nbbo_only=True`` when getting :ref:`quote_df <quote>`


Example
---------

**Example 1:** get Offical Complete NBBO directly from database.

.. literalinclude:: ../samples/micro/off_nbbo1.py
  :language: Python

**Example 2:** retreive Offical Complete NBBO from local DataFrames.

.. literalinclude:: ../samples/micro/off_nbbo2.py
  :language: Python

Both methods have the same output. The first few lines of the output file look like this:

.. csv-table:: 
   :header-rows: 1

    symbol,timestamp,best_bid,best_bidsizeshares,best_bidex,best_ask,best_asksizeshares,best_askex,qu_seqnum
    IBM,2016-12-07 09:00:05.396923,159.69,300.0,P,160.20,100.0,P,426557
    IBM,2016-12-07 09:00:05.396947,159.69,100.0,P,160.20,100.0,P,426558
    IBM,2016-12-07 09:00:05.398795,159.71,100.0,P,160.20,100.0,P,426561
    IBM,2016-12-07 09:00:10.397634,159.67,1300.0,P,160.20,100.0,P,426846
    IBM,2016-12-07 09:00:10.399425,159.70,100.0,P,160.20,100.0,P,426849