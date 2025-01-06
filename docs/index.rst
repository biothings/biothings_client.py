.. biothings_client documentation master file, created by
   sphinx-quickstart on Tue Nov 20 16:32:47 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   (Manually updated in January 2025 after moderization efforts)

.. _MyGene.Info: http://mygene.info
.. _MyVariant.Info: http://myvariant.info
.. _MyChem.Info: http://mychem.info
.. _MyGene.py: https://pypi.org/project/mygene/
.. _MyVariant.py: https://pypi.org/project/myvariant/

Biothings_client.py
===================
`Biothings_client.py <https://pypi.org/project/biothings-client/>`_ is a unified python client providing an easy-to-use wrapper
for accessing *any* `BioThings API <http://biothings.io>`_ (e.g. MyGene.Info_, MyVariant.Info_, MyChem.Info_).  It is the descendent and eventual replacement
of both the MyGene.py_ and MyVariant.py_ python clients.

Requirements
============
    python >=3.7

Installation
=============


    * Option 1. Install from pypi repository using pip:

        .. code-block:: bash

          pip install biothings_client


    * Option 2. Install the latest commit from the github repository using pip:
    
        .. code-block:: bash

          pip install -e git+https://github.com/biothings/biothings_client.py#egg=biothings_client

Optional features / dependencies
================================
    * dataframe support (install using ``pip install biothings_client[dataframe]``)
      
      allows for formatting output from the client queries as a list of pandas `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_ objects.
      Requires the following optional dependenies 

        `pandas <http://pandas.pydata.org>`_

    * caching support (install using ``pip install biothings_client[caching]``)
      
      allows for local caching of client queries to a sqlite database.
      Requires the following optional dependenies 

        `hishel <https://hishel.com/>`_
        `anysqlite <https://pypi.org/project/anysqlite/>`_

Version history
===============

    `CHANGES.txt <https://raw.githubusercontent.com/biothings/biothings_client.py/master/CHANGES.txt>`_


Documentation
=============

    http://biothings-clientpy.readthedocs.org/

.. toctree::
    :maxdepth: 3
    :caption: Tutorials

    doc/quickstart
    doc/custom_api
    doc/subclassing

.. toctree::
    :maxdepth: 3
    :caption: Documentation

    doc/api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
