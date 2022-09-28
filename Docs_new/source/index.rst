.. pytaq documentation master file, created by
   sphinx-quickstart on Fri Aug 12 22:12:32 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pytaq's documentation!
=================================

Pytaq is a python module for processing TAQ data (Trade And Qoute data).
This module replicates the code of the paper "Liquidity Measurement Problems in Fast, Competitive Markets: Expensive and Cheap Solutions».

MeatPy's latest documentation is available at `<https://pytaq.readthedocs.io/en/latest/>`_ and the source code is available on `GitHub <https://github.com/vgreg/pataq>`_.

Installation
------------

You can install Pytaq using ``pip install pytaq``.


Connecting to databases
-----------------------
Pytaq can connect to following databases and get data:

* PostgreSQL
* SASpy

Getting data
-------------
It is able to get following tables:

* NBBO
* Quote
* Trade
* Official Complete NBBO
* Trade-NBBO

Processing data
----------------
Using the tables downloaded from databases or local data, Pytaq computes following items:

* Spreads
* Effective Spreads
* Realized Spreads & Price Impact

.. .. _INTRODUCTION:
.. .. toctree::
..    :maxdepth: 2
..    :caption: Intro:

..    introduction

.. toctree::
   :maxdepth: 2
   :caption: Creatting TaqDaliy object

   connecting


.. toctree::
   :maxdepth: 2
   :caption: Getting Data

   nbbo symbols
   nbbo tables
   quote tables
   trade tables
   official complete nbbo tables
   trade nbbo tables


.. toctree::
   :maxdepth: 2
   :caption: Processing Data

   spreads
   averages
   effective spreads
   realized spreads & price impact


.. .. toctree::
..    :maxdepth: 2
..    :caption: Contents:

..    modules


Credits
--------
Pytaq was created by `Vincent Grégoire <http://www.vincentgregoire.com/>`_ (HEC Montréal)

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
