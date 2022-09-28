NBBO symbols
^^^^^^^^^^^^

.. py:function:: TaqDaliy.get_nbbo_symbols(date)

   Return a symbol list available for nbbo table at specific date. It only workes when Taqdaliy object is created by ``method='saspy'``.

   :param date: Day that market was open at it.
   :type date: datetime instance
   :return: symbol list table.
   :rtype: list[str]

Example
---------

.. literalinclude:: ../samples/micro/nbbo_symbols.py
  :language: Python