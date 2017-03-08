.. image:: https://badge.fury.io/py/myvariant.svg
    :target: https://pypi.python.org/pypi/myvariant

.. image:: https://img.shields.io/pypi/pyversions/myvariant.svg
    :target: https://pypi.python.org/pypi/myvariant

.. image:: https://img.shields.io/pypi/format/myvariant.svg
    :target: https://pypi.python.org/pypi/myvariant

Intro
=====

*biothings_client* is an easy-to-use Python wrapper to access any Biothings.api_-based backend service.  Currently, the following clients are available: 

    * gene - The client for MyGene.Info_, which provides access to gene objects.
    * variant - The client MyVariant.Info_, which provides access to genetic variant objects.
    * drug - The client for c.biothings.io_, which provides access to drug/compound objects.
    * taxon - The client for t.biothings.io_, which provides access to taxon objects.

.. _c.biothings.io: http://c.biothings.io
.. _t.biothings.io: http://t.biothings.io
.. _Biothings.api: http://biothings.io
.. _MyGene.Info: http://mygene.info
.. _MyVariant.Info: http://myvariant.info
.. _requests: https://pypi.python.org/pypi/requests

Requirements
============
    python >=2.6 (including python3)

    requests_ (install using "pip install requests")

Optional dependencies
======================
    * `pandas <http://pandas.pydata.org>`_ (install using "pip install pandas") is required for returning a list of variant objects as `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_.
    * `requests_cache <https://pypi.python.org/pypi/requests-cache>`_ (install using "pip install requests_cache") is required for local caching of API requests.

Installation
=============

    Option 1
          ::

           pip install biothings_client

    Option 2
          download/extract the source code and run::

           python setup.py install

    Option 3
          install the latest code directly from the repository::

            pip install -e git+https://github.com/sulab/biothings_client.py

Version history
===============

    `CHANGES.txt <https://raw.githubusercontent.com/sulab/biothings_client.py/master/CHANGES.txt>`_

Tutorial
=========

Documentation
=============

Usage
=====

.. code-block:: python

    In [1]: from biothings_client import get_client

    # get a client for variant objects

    In [2]: mv = get_client("variant")

    # see more variant client options at docs/variant_examples.rst

    In [3]: mv.getvariant("chr7:g.140453134T>C")
    Out[3]:  #output below is collapsed
    {"_id": "chr7:g.140453134T>C",
     "_version": 1,
     "chrom": "7",
     "cadd": {...},
     "clinvar": {...},
     "cosmic": {...},
     "dbnsfp": {...},
     "dbsnp": {...},
     "docm": {...},
     "hg19": {'end': 140453134, 'start': 140453134},
     "mutdb": {...},
     "snpeff": {...},
     "vcf": {
        "alt": "C",
        "position": "140453134",
        "ref": "T"
     }}

    # get a client for gene objects

    In [7]: mg = get_client("gene")
    
    # see more gene client examples in docs/gene_examples.rst

    In [8]: mg.getgene(1017, 'name,symbol,refseq')
    Out[8]:
    {'_id': '1017',
     '_score': 21.03413,
     'name': 'cyclin dependent kinase 2',
     'refseq': {'genomic': ['NC_000012.12', 'NC_018923.2', 'NG_034014.1'],
      'protein': ['NP_001277159.1',
       'NP_001789.2',
       'NP_439892.2',
       'XP_011536034.1'],
      'rna': ['NM_001290230.1', 'NM_001798.4', 'NM_052827.3', 'XM_011537732.1'],
      'translation': [{'protein': 'NP_001789.2', 'rna': 'NM_001798.4'},
       {'protein': 'NP_439892.2', 'rna': 'NM_052827.3'},
       {'protein': 'NP_001277159.1', 'rna': 'NM_001290230.1'},
       {'protein': 'XP_011536034.1', 'rna': 'XM_011537732.1'}]},
     'symbol': 'CDK2'}

    # get a client for drugs/compounds

    In [9]: md = get_client("drug")
    
    # see more drug client examples in docs/drug_examples.rst

    In [10]: md.getdrug("ATBDZSAENDYQDW-UHFFFAOYSA-N", fields="pubchem")
    Out[10]:
    {'_id': 'ATBDZSAENDYQDW-UHFFFAOYSA-N',
     '_version': 1,
     'pubchem': {'chiral_atom_count': 0,
      'chiral_bond_count': 0,
      'cid': 'CID4080429',
      'complexity': 250,
      'covalently-bonded_unit_count': 1,
      'defined_atom_stereocenter_count': 0,
      'defined_bond_stereocenter_count': 0,
      'exact_mass': 184.019415,
      'formal_charge': 0,
      'heavy_atom_count': 12,
      'hydrogen_bond_acceptor_count': 3,
      'hydrogen_bond_donor_count': 1,
      'inchi': 'InChI=1S/C8H8O3S/c1-2-7-4-3-5-8(6-7)12(9,10)11/h2-6H,1H2,(H,9,10,11)',
      'inchi_key': 'ATBDZSAENDYQDW-UHFFFAOYSA-N',
      'isotope_atom_count': 0,
      'iupac': {'traditional': '3-vinylbesylic acid'},
      'molecular_formula': 'C8H8O3S',
      'molecular_weight': 184.21232,
      'monoisotopic_weight': 184.019415,
      'rotatable_bond_count': 2,
      'smiles': {'isomeric': 'C=CC1=CC(=CC=C1)S(=O)(=O)O'},
      'tautomers_count': 1,
      'topological_polar_surface_area': 62.8,
      'undefined_atom_stereocenter_count': 0,
      'undefined_bond_stereocenter_count': 0,
      'xlogp': 1.4}}

    # get a client for taxa

    In [11]: mt = get_client("taxon")

    # more taxon client examples at docs/taxon_examples.rst

    In [12]: mt.gettaxon(9606)
    Out[12]:
    {'_id': '9606',
     '_version': 1,
     'authority': ['homo sapiens linnaeus, 1758'],
     'common_name': 'man',
     'genbank_common_name': 'human',
     'has_gene': True,
     'lineage': [9606,
      9605,
      207598,
      9604,
      314295,
      9526,
      314293,
      376913,
      9443,
      314146,
      1437010,
      9347,
      32525,
      40674,
      32524,
      32523,
      1338369,
      8287,
      117571,
      117570,
      7776,
      7742,
      89593,
      7711,
      33511,
      33213,
      6072,
      33208,
      33154,
      2759,
      131567,
      1],
     'other_names': ['humans'],
     'parent_taxid': 9605,
     'rank': 'species',
     'scientific_name': 'homo sapiens',
     'taxid': 9606,
     'uniprot_name': 'homo sapiens'}
Contact
========
