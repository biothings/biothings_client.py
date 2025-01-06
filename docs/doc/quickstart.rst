.. _Quick Start:

.. _MyGene.py: https://pypi.org/project/mygene/
.. _BioThings API: http://biothings.io


Quick Start
===========

biothings_client was made to allow easy programmatic access to any `BioThings API`_ backend.  We do this by generating configuration
parameters (and documentation) that define a particular API on-the-fly.  This is done using the *get_client* function.  To use the
*get_client* function, you only need to specify the entity type you want a client for as a string.  Consider the following code:

.. code-block:: python

    In [1]: from biothings_client import get_client

    In [2]: gene_client = get_client('gene')

    In [3]: type(gene_client)
    Out[3]: biothings_client.MyGeneInfo

The ``gene_client`` variable in the code above *is* a ``MyGeneInfo`` object (exactly as obtained through the MyGene.py_ package).  As such,
all of the methods available in the MyGene.py_ client are available in the biothings_client generated gene client. So the above code block
is equivalent to the way you use MyGene.py_ client package before:

.. code-block:: python

    In [1]: import mygene

    In [2]: gene_client = mygene.MyGeneInfo()get_client('gene')

    In [3]: type(gene_client)
    Out[3]: mygene.MyGeneInfo

Use the client for MyGene.info API - Genes
------------------------------------------

Once you get the ``gene_client`` instance from biothings_client, the rest is exactly the same:

.. code-block:: python

    In [4]: gene_client.getgene('1017', fields='symbol,name')
    Out[4]:
    {'_id': '1017',
     '_score': 13.166854,
     'name': 'cyclin dependent kinase 2',
     'symbol': 'CDK2'}

    In [5]: gene_client.getgenes(['1017', '1018'], species='human', fields='symbol,name')
    querying 1-2...done.
    Out[5]:
    [{'_id': '1017',
      '_score': 20.773563,
      'name': 'cyclin dependent kinase 2',
      'query': '1017',
      'symbol': 'CDK2'},
     {'_id': '1018',
      '_score': 21.309164,
      'name': 'cyclin dependent kinase 3',
      'query': '1018',
      'symbol': 'CDK3'}]

    In [6]: gene_client.query('uniprot:P24941', fields='symbol,name')
    Out[6]:
    {'hits': [{'_id': '1017',
     '_score': 14.752583,
     'name': 'cyclin dependent kinase 2',
     'symbol': 'CDK2'}],
     'max_score': 14.752583,
     'took': 3,
     'total': 1}

    In [7]: gene_client.querymany(['P24941', 'O14727'], scopes='uniprot', fields='symbol,name')
    querying 1-2...done.
    Finished.
    Out[7]:
    [{'_id': '1017',
      '_score': 14.176394,
      'name': 'cyclin dependent kinase 2',
      'query': 'P24941',
      'symbol': 'CDK2'},
    {'_id': '317',
     '_score': 14.75709,
     'name': 'apoptotic peptidase activating factor 1',
     'query': 'O14727',
     'symbol': 'APAF1'}]

    In [8]: gene_client.metadata()
    Out[8]:
    {'app_revision': 'c2a3aaa5fdac7b05fe243c1de62e6b3a3cf2b773',
     'available_fields': 'http://mygene.info/metadata/fields',
     'build_date': '2018-11-26T08:11:23.790634',
     'build_version': '20181126',
     'genome_assembly': {'frog': 'xenTro3',
      'fruitfly': 'dm3',
      'human': 'hg38',
      'mouse': 'mm10',
      'nematode': 'ce10',
      'pig': 'susScr2',
      'rat': 'rn4',
      'zebrafish': 'zv9'},
     'source': None,
     'src': {'PantherDB': {'stats': {'PantherDB': 156054},
       'version': '2017-12-11'},
      'cpdb': {'stats': {'cpdb': 21141}, 'version': '33'},
      'ensembl': {'stats': {'ensembl_acc': 3228635,
        'ensembl_gene': 3187005,
        'ensembl_genomic_pos': 3183045,
        'ensembl_interpro': 2307500,
        'ensembl_pfam': 2100435,
        'ensembl_prosite': 1266847},
       'version': '94'},
      'ensembl_genomic_pos_hg19': {'stats': {'ensembl_genomic_pos_hg19': 55966},
       'version': None},
      'ensembl_genomic_pos_mm9': {'stats': {'ensembl_genomic_pos_mm9': 38646},
       'version': None},
      'entrez': {'stats': {'entrez_accession': 22406332,
        'entrez_gene': 22521690,
        'entrez_genomic_pos': 2632698,
        'entrez_go': 204359,
        'entrez_refseq': 22370423,
        'entrez_retired': 243656,
        'entrez_unigene': 543053},
       'version': '20181126'},
      'exac': {'stats': {'broadinstitute_exac': 18240}, 'version': '0.3.1'},
      'generif': {'stats': {'generif': 96431}, 'version': '20181126'},
      'homologene': {'stats': {'homologene': 269019}, 'version': '68'},
      'pharmgkb': {'stats': {'pharmgkb': 26833}, 'version': '2018-11-05'},
      'pharos': {'stats': {'pharos': 19828}, 'version': '5.2.0'},
      'reactome': {'stats': {'reactome': 71935}, 'version': '2018-09-24'},
      'reagent': {'stats': {'reagent': 38621}, 'version': None},
      'refseq': {'stats': {'entrez_ec': 19773, 'entrez_genesummary': 27713},
       'version': '91'},
      'reporter': {'stats': {'reporter': 426561}, 'version': None},
      'ucsc': {'stats': {'ucsc_exons': 208266}, 'version': '20181115'},
      'umls': {'stats': {'umls': 39665}, 'version': '2017-05-08'},
      'uniprot': {'stats': {'uniprot': 9411447}, 'version': '20181107'},
      'uniprot_ipi': {'stats': {'uniprot_ipi': 157025}, 'version': None},
      'uniprot_pdb': {'stats': {'uniprot_pdb': 30379}, 'version': '20181107'},
      'uniprot_pir': {'stats': {'uniprot_pir': 153446}, 'version': '20181107'},
      'wikipedia': {'stats': {'wikipedia': 11075}, 'version': None}},
     'src_version': {'PantherDB': '2017-12-11',
      'cpdb': '33',
      'ensembl': '94',
      'ensembl_genomic_pos_hg19': None,
      'ensembl_genomic_pos_mm9': None,
      'entrez': '20181126',
      'exac': '0.3.1',
      'generif': '20181126',
      'homologene': '68',
      'pharmgkb': '2018-11-05',
      'pharos': '5.2.0',
      'reactome': '2018-09-24',
      'reagent': None,
      'refseq': '91',
      'reporter': None,
      'ucsc': '20181115',
      'umls': '2017-05-08',
      'uniprot': '20181107',
      'uniprot_ipi': None,
      'uniprot_pdb': '20181107',
      'uniprot_pir': '20181107',
      'wikipedia': None},
     'stats': {'total_ensembl_genes': 24436578,
      'total_ensembl_genes_mapped_to_entrez': 1355996,
      'total_ensembl_only_genes': 1873808,
      'total_entrez_genes': 22521690,
      'total_genes': 24395498,
      'total_species': 23801},
     'taxonomy': {'frog': 8364,
      'fruitfly': 7227,
      'human': 9606,
      'mouse': 10090,
      'nematode': 6239,
      'pig': 9823,
      'rat': 10116,
      'thale-cress': 3702,
      'zebrafish': 7955}}

In addition to the ``gene_client``, you can generate a client to any of the other `BioThings API`_
services we offer.  See the following code snippet:

Use the client for MyVariant.info API - Variants
------------------------------------------------

.. code-block:: python

    In [10]: variant_client = get_client('variant')

    In [11]: variant_client.query('dbnsfp.genename:BTK', fields='_id')
    Out[11]:
    {'hits': [{'_id': 'chrX:g.100614336C>T', '_score': 10.192645},
      {'_id': 'chrX:g.100608911G>A', '_score': 10.192645},
      {'_id': 'chrX:g.100608917G>C', '_score': 10.192645},
      {'_id': 'chrX:g.100608872T>A', '_score': 10.192645},
      {'_id': 'chrX:g.100608887A>T', '_score': 10.192645},
      {'_id': 'chrX:g.100608891T>C', '_score': 10.192645},
      {'_id': 'chrX:g.100608282T>C', '_score': 10.192645},
      {'_id': 'chrX:g.100608230A>T', '_score': 10.192645},
      {'_id': 'chrX:g.100604881C>T', '_score': 10.192645},
      {'_id': 'chrX:g.100608204A>G', '_score': 10.192645}],
     'max_score': 10.192645,
     'took': 10,
     'total': 5143}


Use the client for MyChem.info API - Chemicals/Drugs
----------------------------------------------------

.. code-block:: python

    In [12]: chem_client = get_client('chem')

    In [13]: chem_client.getchem('DB00551', fields='drugbank.name')
    Out[13]:
    {'_id': 'RRUDCFGSUDOHDG-UHFFFAOYSA-N',
     'drugbank': {'_license': 'https://goo.gl/kvVASD',
      'name': 'Acetohydroxamic Acid'}}


Use the client for MyDisease.info API - Disease
-----------------------------------------------

.. code-block:: python

    In [13]: disease_client = get_client('disease')

    In [14]: disease_client.query('diabetes')
    Out[14]:
    {'hits': [{'_id': 'MONDO:0005443',
       '_score': 3.466746,
       'mondo': {'label': 'type 2 diabetes nephropathy',
        'xrefs': {'efo': '0004997'}}},
      {'_id': 'MONDO:0023227',
       '_score': 3.466746,
       'mondo': {'definition': 'A form of diabetes insipidus that manifests during pregnancy (or in some cases, after pregnancy). It is characterized by theappearance of a polyuric-polydipsic syndrome that resultsin fluid intake ranging from 3 to 20 L/day. It is also charac-terized by excretion of abnormally high volumes of dilutedurine. This polyuria is insipid, i.e., the urine concentrationof dissolved substances is very low.',
        'label': 'gestational diabetes insipidus',
        'xrefs': {'gard': '0010702', 'mesh': 'C548014', 'umls': 'C2932666'}}},
      {'_id': 'MONDO:0001344',
       '_score': 3.466746,
       'mondo': {'label': 'obsolete neonatal diabetes mellitus'}},
      {'_id': 'MONDO:0019846',
       '_score': 3.4068294,
       'hpo': {'disease_name': 'Acquired central diabetes insipidus',
        'orphanet': '95626',
        'phenotype_related_to_disease': [{'aspect': 'P',
          'assigned_by': 'ORPHA:orphadata',
          'evidence': 'TAS',
          'frequency': 'HP:0040281',
          'hpo_id': 'HP:0000873'},
         {'aspect': 'P',
          'assigned_by': 'ORPHA:orphadata',
          'evidence': 'TAS',
          'frequency': 'HP:0040281',
          'hpo_id': 'HP:0001824'},
         {'aspect': 'P',
          'assigned_by': 'ORPHA:orphadata',
          'evidence': 'TAS',
          'frequency': 'HP:0040281',
          'hpo_id': 'HP:0001959'},
         {'aspect': 'P',
          'assigned_by': 'ORPHA:orphadata',
          'evidence': 'TAS',
          'frequency': 'HP:0040281',
          'hpo_id': 'HP:0100515'}]},
       'mondo': {'definition': 'Acquired central diabetes insipidus (acquired CDI) is a subtype of central diabetes insipidus (CDI, see this term), characterized by polyuria and polydipsia, due to an idiopathic or secondary decrease in vasopressin (AVP) production.',
        'label': 'acquired central diabetes insipidus',
        'xrefs': {'icd10': 'E23.2', 'orphanet': '95626'}}},
      {'_id': 'MONDO:0022650',
       '_score': 3.2161584,
       'mondo': {'label': 'cardiomyopathy diabetes deafness',
        'xrefs': {'gard': '0001103'}}},
      {'_id': 'MONDO:0005442',
       '_score': 3.1703691,
       'mondo': {'label': 'type 1 diabetes nephropathy',
        'xrefs': {'efo': '0004996'}}},
      {'_id': 'MONDO:0015967',
       '_score': 3.1703691,
       'mondo': {'definition': 'Rare genetic diabetes mellitus.',
        'label': 'rare genetic diabetes mellitus',
        'xrefs': {'orphanet': '183625'}}},
      {'_id': 'MONDO:0022971',
       '_score': 3.1703691,
       'mondo': {'label': 'diabetes persistent mullerian ducts',
        'xrefs': {'gard': '0001840'}}},
      {'_id': 'MONDO:0022993',
       '_score': 3.1703691,
       'mondo': {'definition': 'Diabetes insipidus caused by excessive intake of water due to psychological factors or damage to the thirst-regulating mechanism.',
        'label': 'dipsogenic diabetes insipidus',
        'xrefs': {'gard': '0010703',
         'mesh': 'C548013',
         'ncit': 'C129735',
         'sctid': '82800008',
         'umls': 'C0268813'}}},
      {'_id': 'MONDO:0015888',
       '_score': 3.1530147,
       'mondo': {'label': 'other rare diabetes mellitus',
        'xrefs': {'orphanet': '181381'}}}],
     'max_score': 3.466746,
     'took': 17,
     'total': 120}

Use the client for t.biothings.io API - Taxnomy
-----------------------------------------------


.. code-block:: python

    In [15]: taxon_client = get_client('taxon')

    In [16]: taxon_client.gettaxon(9606)
    Out[16]:
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
     'parent_taxid': 9605,
     'rank': 'species',
     'scientific_name': 'homo sapiens',
     'taxid': 9606,
     'uniprot_name': 'homo sapiens'}
