Connecting to database
^^^^^^^^^^^^^^^^^^^^^^

.. py:function:: TaqDaliy(method=None, db=None, track_retail=False)

   Create TaqDaliy object. Can connect to database using 'PostgreSQL' or 'SASpy' method.
   To use local files, ``method`` and ``db`` can be None.

   :param method: The method of connecting to database, can be ``'postgresql'`` or ``'saspy'`` or None. If it is not None, ``db`` must be provided (not None) and only in this case can get data from databases. In any case, local files can be used.
   :type method: str or None
   :param db: Connection to database based on selected method.
   :type db: Connection or None
   :param track_retail: Compute retail sign following "Tracking retail investor activity" by Ekkehart Boehmer, Charles m. Jones, and Xiaoyan Zhang.
   :type track_retail: bool or None, default False
   :return: TaqDaliy object.


PostgreSQL
----------

**Example 1:** Creating TaqDaliy object and connecting to database by `postgresql` method.
As an example, we use WRDS database.

.. literalinclude:: ../samples/micro/postgresql.py
  :language: Python

SASpy
-----

**Example 2:** Creating TaqDaliy object and connecting to database by `saspy` method.
As an example, we use WRDS database. In this method, SAS 9.4 or higher must be installed on your machine.

.. literalinclude:: ../samples/micro/saspy.py
  :language: Python