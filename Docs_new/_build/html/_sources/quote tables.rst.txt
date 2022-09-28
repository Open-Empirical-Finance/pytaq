Qoute tables
^^^^^^^^^^^^

.. _quote:

.. py:function:: TaqDaliy.get_quote_table(date, symbols=None, nbbo_only=True, output_flags=False)

   Return a cleaned quote table for given symbols at specific date during normal quoting hours.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :param symbols: Symbols that data is related to it.
   :type symbols: list[str]
   :param nbbo_only: If True, keep only nbbo quotes. It should set to True if want touse in getting complete NBBO
   :type nbbo_only: bool, default True
   :param output_flags: If True, incorporate two columns ``qu_cond`` and ``qu_cancel``.
   :type output_flags: bool, default False
   :return: Quote table.
   :rtype: Pandas DataFrame


Cleaning
---------
* Quote condition must be normal:

  * Keep only rows where ``qu_cond`` is equal to one the following values: `['A', 'B', 'H', 'O', 'R', 'W']`

* Delete rows with canceled quotes:

  * Delete rows Where ``qu_cancel = 'B'``

* Delete rows with abnormal crossed markets:

  * Delete rows if ``best_ask`` < ``bid_bid``.

* Delete rows with abnormal spreads:

  * Delete rows if spread > $5.

* Delete rows if any quote or any size <= 0 or = null:

  * Delete row if ``best_ask`` or ``best_asksizeshares`` or ``best_bid`` or ``best_bidsizeshares`` <= 0 or = null.

* If ``nbbo_only=True``, keep only:

  * whether ``qu_source == 'C'`` and ``natbbo_ind == '1'``
  * Or ``qu_source == 'N'`` and ``natbbo_ind == '4'``


Example
---------

.. literalinclude:: ../samples/micro/quote.py
  :language: Python

The first few lines of the output file look like this:

.. csv-table:: 
   :header-rows: 1

    timestamp,symbol,best_bid,best_bidsizeshares,best_bidex,best_ask,best_asksizeshares,best_askex,qu_seqnum
    2016-12-07 09:00:05.396923,IBM,159.69,300,P,160.20,100,P,426557
    2016-12-07 09:00:05.396947,IBM,159.69,100,P,160.20,100,P,426558
    2016-12-07 09:00:05.398795,IBM,159.71,100,P,160.20,100,P,426561
    2016-12-07 09:00:10.397634,IBM,159.67,1300,P,160.20,100,P,426846
    2016-12-07 09:00:10.399425,IBM,159.70,100,P,160.20,100,P,426849