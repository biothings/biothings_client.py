.. biothings_client documentation master file, created by
   sphinx-quickstart on Tue Nov 20 16:32:47 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _requests: http://docs.python-requests.org/en/latest/
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
    Python >=2.7 (including python3)

    (Python 2.6 might still work, but is not supported any more since v0.2.0)

    requests_ (install using ``pip install requests``)

Optional dependencies
======================
    * `pandas <http://pandas.pydata.org>`_ (install using ``pip install pandas``) is required for returning a list of objects as
      `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_.
    * `requests-cache <https://pypi.org/project/requests-cache/>`_ (install using ``pip install requests-cache``) is required to
      use the local data caching function.


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

    `CHANGES.txt <https://raw.githubusercontent.com/biothings/biothings_client.py/master/CHANGES.txt>`_


Documentation
=============

    http://biothings-clientpy.readthedocs.org/

.. toctree::
    :maxdepth: 3
    :caption: Tutorials

    doc/Quick-Start
    doc/Custom-API
    doc/Subclassing

.. toctree::
    :maxdepth: 3
    :caption: Documentation

    doc/API


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
