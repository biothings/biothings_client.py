Instantiating a Client for a Custom BioThings API
=================================================

The Quick Start tutorial shows how to get clients for all publicly available BioThings APIs.
What if you create your own custom BioThings API?

With biothings_client, you can generate client settings for any future APIs created with BioThings API.  The `BioThings API Single source tutorial <https://biothingsapi.readthedocs.io/en/latest/doc/single_source_tutorial.html>`_ explains how to set up a simple BioThings API from PharmGKB gene data.  The following code snippet shows an example of how to setup biothings_client to access that custom API:

.. code-block:: python

    In [1]: from biothings_client import get_client

    In [2]: pharmgkb_client = get_client('gene', url='http://35.164.95.182:8000/v1')

    In [3]: pharmgkb_client.query('ncbi_gene_id:1017', fields='pharmgkb_accession_id')
    Out[3]:
    {'hits': [{'_id': 'cOydWmcBViFqgJfo4gdM',
       '_score': 7.495912,
       'pharmgkb_accession_id': 'PA101'}],
     'max_score': 7.495912,
     'took': 10,
     'total': 1}

The **url** parameter to **get_client** specifies where the BioThings API endpoint is located (the
address above is temporary and is no longer serviced by us).  The entity parameter is still 'gene' (as the entity type of PharmGKB gene is gene).
