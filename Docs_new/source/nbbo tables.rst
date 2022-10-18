NBBO tables
^^^^^^^^^^^

.. ::

..   taq.get_nbbo_table(date, symbols=None, output_flags=False)

.. Returns a cleaned NBBO table for given symbols at specific date.

.. py:function:: TaqDaliy.get_nbbo_table(date, symbols=None, output_flags=False)

   Return a cleaned NBBO (National Best Bid and Offer) table for given symbols at specific date during normal quoting hours.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param output_flags: If True, incorporate two columns ``qu_cond`` and ``qu_cancel``.
   :type output_flags: bool, default False
   :return: NBBO table.
   :rtype: Pandas DataFrame

.. Parameters
.. -----------
.. * date: a datetime instance that indicates a day.
.. * symbols: a list of strings
.. * output_flags: boolian, if True incorporates two columns: ``qu_cond`` and ``qu_cancel`` 


Cleaning
---------
* Quote condition must be normal:

  * Keep only rows where ``qu_cond`` is equal to one the following values: `['A', 'B', 'H', 'O', 'R', 'W']`

* Delete rows with canceled quotes:

  * Delete rows Where ``qu_cancel = 'B'``

* Delete rows with empty quotes:

  * Delete rows if both ``best_ask`` and ``bid_bid`` (or their size) are 0 or None

* If quote or size <= 0 or = null, set quote and size to null:

  * If ``best_ask`` or ``best_asksizeshares`` <= 0 or = null, set both of them to null
  * If ``best_bid`` or ``best_bidsizeshares`` <= 0 or = null, set both of them to null

* If abnormal spreads, set quote and size to null:

  * If quoted spread > $5 and ``best_ask`` has decreased by $2.50, set ``best_ask`` and ``best_asksizeshares`` to null .
  * If quoted spread > $5 and ``best_bid`` has increased by $2.50, set ``best_bid`` and ``best_bidsizeshares`` to null .

* Keep only when there is any changes in ``best_ask``, ``best_bid``, ``best_bidsizeshares``, or ``best_asksizeshares``

Example
---------

.. literalinclude:: ../samples/micro/nbbo.py
  :language: Python

The first few lines of the output file look like this:

.. csv-table:: 
   :header-rows: 1

    timestamp,symbol,best_bid,best_bidsizeshares,best_bidex,best_ask,best_asksizeshares,best_askex,qu_seqnum
    2016-12-07 09:00:57.415649,IBM,159.70,100.0,P,160.25,300.0,T,428253
    2016-12-07 09:00:57.902121,IBM,159.67,1300.0,P,160.25,300.0,T,428349
    2016-12-07 09:00:57.902143,IBM,159.67,1100.0,P,160.25,300.0,T,428350
    2016-12-07 09:00:57.905189,IBM,159.69,100.0,P,160.25,300.0,T,428353
    2016-12-07 09:01:20.756511,IBM,159.70,100.0,P,160.25,300.0,T,429958