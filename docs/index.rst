.. biothings_client documentation master file, created by
   sphinx-quickstart on Tue Nov 20 16:32:47 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to biothings_client's documentation!
============================================

Biothings_client.py is a unified python client for accessing all BioThings APIs, such as:

* MyGene.info
* MyVariant.info
* MyChem.info

.. toctree::
   :maxdepth: 2
   index

Requirements
============
    python >=2.6 (including python3)

    requests_ (install using "pip install requests")

Optional dependencies
======================
    `pandas <http://pandas.pydata.org>`_ (install using "pip install pandas") is required for returning a list of gene objects as `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_.

Installation
=============

    Option 1
          Install directly from pip::

            pip install biothings_client

    Option 2
          download/extract the source code and run::

           python setup.py install

    Option 3
          install the latest code directly from the repository::

            pip install -e git+https://github.com/biothings/biothings_client.py#egg=biothings_client

Version history
===============

    `CHANGES.txt <https://raw.githubusercontent.com/SuLab/mygene.py/master/CHANGES.txt>`_

Tutorial
========

API
======

.. py:module:: biothings_client
.. autofunction:: get_client
.. autoclass:: MyGeneInfo
    :members:
    :inherited-members:
.. autoclass: MyVariantInfo
    :members:
    :inherited-members:
.. autoclass: MyChemInfo
    :members:
    :inherited-members:
.. autoclass: MyDiseaseInfo
    :members:
    :inherited-members:
.. autoclass: MyTaxonInfo
    :members:
    :inherited-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
