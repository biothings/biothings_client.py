import unittest
import sys
import os
import types
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
sys.path.insert(0, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])

try:
    from utils import descore
except ImportError:
    from tests.utils import descore

import biothings_client
sys.stdout.write('"biothings_client {0}" loaded from "{1}"\n'.format(biothings_client.__version__, biothings_client.__file__))


class TestGenesetClient(unittest.TestCase):

    def setUp(self):
        self.mc = biothings_client.get_client("geneset")

    def test_metadata(self):
        meta = self.mc.metadata()
        self.assertTrue("src" in meta)
        self.assertTrue("stats" in meta)
        self.assertTrue("total" in meta['stats'])

    def test_getgeneset(self):
        g = self.mc.getgeneset("D005947_9615")
        self.assertEqual(len(g), 2)
        self.assertEqual(g[0]['_id'], 'D005947_9615')
        self.assertEqual(g[0]['name'], 'Glucose interactions')
        self.assertEqual(g[0]['source'], 'ctd')
        self.assertEqual(g[0]['taxid'], '9615')
        self.assertEqual(g[1]['_id'], 'D005947_9615')
        self.assertEqual(g[1]['name'], 'Glucose interactions')
        self.assertEqual(g[1]['source'], 'ctd')
        self.assertEqual(g[1]['taxid'], '9615')

    # def test_getgeneset_with_fields(self):
    #     c = self.mc.getgeneset("7AXV542LZ4", fields="chebi.name,genesetbl.inchi_key,pubgeneset.cid")
    #     self.assertTrue('_id' in c)
    #     self.assertTrue('chebi' in c)
    #     self.assertTrue('name' in c['chebi'])
    #     self.assertTrue('genesetbl' in c)
    #     self.assertTrue('inchi_key' in c['genesetbl'])
    #     self.assertTrue('pubgeneset' in c)
    #     self.assertTrue('cid' in c['pubgeneset'])

    # def get_getdrug(self):
    #     c = self.mc.getdrug("CHEMBL1308")
    #     self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
    #     c = self.mc.getdrug("7AXV542LZ4")
    #     self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
    #     c = self.mc.getdrug("CHEBI:6431")
    #     self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    # def test_getgenesets(self):
    #     c_li = self.mc.getgenesets([
    #         "KTUFNOKKBVMGRW-UHFFFAOYSA-N",
    #         "HXHWSAZORRCQMX-UHFFFAOYSA-N",
    #         'DQMZLTXERSFNPB-UHFFFAOYSA-N'
    #     ])
    #     self.assertEqual(len(c_li), 3)
    #     self.assertEqual(c_li[0]['_id'], 'KTUFNOKKBVMGRW-UHFFFAOYSA-N')
    #     self.assertEqual(c_li[1]['_id'], 'HXHWSAZORRCQMX-UHFFFAOYSA-N')
    #     self.assertEqual(c_li[2]['_id'], 'DQMZLTXERSFNPB-UHFFFAOYSA-N')

    # def test_query(self):
    #     qres = self.mc.query('chebi.name:albendazole', size=5)
    #     self.assertTrue('hits' in qres)
    #     self.assertEqual(len(qres['hits']), 5)

    def test_query_default_fields(self):
        self.mc.query(q='glucose')

    def test_query_field(self):
        self.mc.query(q='genes.ncbigene:1017')

    # def test_species_filter_blank_query(self):
    #     dog = self.mc.query(species='9615')
    #     print(3, dog['hits'][0])
    #     assert dog['hits'][0]['taxid'] == "9615"

    def test_species_filter_plus_query(self):
        dog = self.mc.query(q='glucose', species='9615')
        assert dog['hits'][0]['taxid'] == "9615"

    def test_query_by_id(self):
        query = self.mc.query(q="_id:WP100")
        assert query['hits'][0]['_id'] == "WP100"

    def test_query_by_name(self):
        kinase = self.mc.query(q='name:kinase')
        assert 'kinase' in kinase['hits'][0]['name'].lower()

    def test_query_by_description(self):
        desc = self.mc.query(q='description:cytosine deamination')
        assert 'cytosine' in desc['hits'][0]['description'].lower()
        assert 'deamination' in desc['hits'][0]['description'].lower()

    def test_query_by_source_go(self):
        go = self.mc.query(q='source:go', fields='all')
        assert 'go' in go['hits'][0].keys()
        assert go['hits'][0]['source'] == 'go'

    def test_query_by_source_ctd(self):
        ctd = self.mc.query(q='source:ctd', fields='all')
        assert 'ctd' in ctd['hits'][0].keys()
        assert ctd['hits'][0]['source'] == 'ctd'

    def test_query_by_source_msigdb(self):
        msigdb = self.mc.query(q='source:msigdb', fields='all')
        assert 'msigdb' in msigdb['hits'][0].keys()
        assert msigdb['hits'][0]['source'] == 'msigdb'

    def test_query_by_source_kegg(self):
        kegg = self.mc.query(q='source:kegg', fields='all')
        assert 'kegg' in kegg['hits'][0].keys()
        assert kegg['hits'][0]['source'] == 'kegg'

    def test_query_by_source_do(self):
        do = self.mc.query(q='source:do', fields='all')
        assert 'do' in do['hits'][0].keys()
        assert do['hits'][0]['source'] == 'do'

    def test_query_by_source_reactome(self):
        reactome = self.mc.query(q='source:reactome', fields='all')
        assert 'reactome' in reactome['hits'][0].keys()
        assert reactome['hits'][0]['source'] == 'reactome'

    def test_query_by_source_smpdb(self):
        smpdb = self.mc.query(q='source:smpdb', fields='all')
        assert 'smpdb' in smpdb['hits'][0].keys()
        assert smpdb['hits'][0]['source'] == 'smpdb'

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestGenesetClient)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
