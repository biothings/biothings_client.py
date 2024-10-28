import os
import sys
import unittest

import biothings_client

sys.path.insert(0, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])


sys.stdout.write(
    '"biothings_client {0}" loaded from "{1}"\n'.format(biothings_client.__version__, biothings_client.__file__)
)


class TestBiothingsClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_client(self):
        gene_client = biothings_client.get_client("gene")
        self.assertEqual(type(gene_client).__name__, "MyGeneInfo")

        variant_client = biothings_client.get_client("variant")
        self.assertEqual(type(variant_client).__name__, "MyVariantInfo")

        chem_client = biothings_client.get_client("chem")
        self.assertEqual(type(chem_client).__name__, "MyChemInfo")

        # drug_client as an alias of chem_client
        drug_client = biothings_client.get_client("drug")
        self.assertEqual(type(drug_client).__name__, "MyChemInfo")

        disease_client = biothings_client.get_client("disease")
        self.assertEqual(type(disease_client).__name__, "MyDiseaseInfo")

        taxon_client = biothings_client.get_client("taxon")
        self.assertEqual(type(taxon_client).__name__, "MyTaxonInfo")

        geneset_client = biothings_client.get_client("geneset")
        self.assertEqual(type(geneset_client).__name__, "MyGenesetInfo")

        geneset_client = biothings_client.get_client(url="https://mygeneset.info/v1")
        self.assertEqual(type(geneset_client).__name__, "MyGenesetInfo")

    def test_generate_settings_from_url(self):
        client_settings = biothings_client.client.base.generate_settings("geneset", url="https://mygeneset.info/v1")
        self.assertEqual(client_settings["class_kwargs"]["_default_url"], "https://mygeneset.info/v1")
        self.assertEqual(client_settings["class_name"], "MyGenesetInfo")
