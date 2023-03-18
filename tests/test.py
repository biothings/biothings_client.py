import os
import sys
import unittest

sys.path.insert(0, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])

import biothings_client

sys.stdout.write(
    '"biothings_client {0}" loaded from "{1}"\n'.format(biothings_client.__version__, biothings_client.__file__)
)

try:
    from chem import suite as chem_suite
    from gene import suite as gene_suite
    from geneset import suite as geneset_suite
    from variant import suite as variant_suite
except ImportError:
    from tests.chem import suite as chem_suite
    from tests.gene import suite as gene_suite
    from tests.geneset import suite as geneset_suite
    from tests.variant import suite as variant_suite


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

        geneset_client = biothings_client.get_client(url= "https://mygeneset.info/v1")
        self.assertEqual(type(geneset_client).__name__, "MyGenesetInfo")

    def test_generate_settings_from_url(self):
        client_settings =  biothings_client._generate_settings("geneset", url="https://mygeneset.info/v1")
        self.assertEqual(client_settings["class_kwargs"]["_default_url"], "https://mygeneset.info/v1")
        self.assertEqual(client_settings["class_name"], "MyGenesetInfo")


def suite():
    _biothings_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBiothingsClient)
    _gene_suite = gene_suite()
    _variant_suite = variant_suite()
    _chem_suite = chem_suite()
    _geneset_suite = geneset_suite()
    _total_suite = unittest.TestSuite()
    _total_suite.addTest(_biothings_suite)
    _total_suite.addTest(_gene_suite)
    _total_suite.addTest(_variant_suite)
    _total_suite.addTest(_chem_suite)
    _total_suite.addTest(_geneset_suite)
    return _total_suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
