Averages
^^^^^^^^

.. _averages:

.. py:function:: TaqDaliy.compute_averages_ave_sw_dw(df, measures, simple=True, dollar_weighted=True, share_weighted=True)

   Accept a DataFrame, calculate selected kind of averages for selected measures(columns).

   :param df: DataFrame that has measures to calculate averages.
   :type df: Pandas DataFrame
   :param measures: Measures(columns) to calculate averages.
   :type measures: list[str]
   :param simple: If ``simple=True``, calculate simple averages for all measures with suffix '_Ave'
   :type simple: bool, default True
   :param dollar_weighted: If ``dollar_weighted=True``, calculate dollar_weighted averages for all measures with suffix '_DW'
   :type dollar_weighted: bool, default True
   :param share_weighted: If ``share_weighted=True``, calculate share_weighted averages for all measures with suffix '_SW'
   :type share_weighted: bool, default True
   :return: Some kind of averages.
   :rtype: Pandas DataFrame