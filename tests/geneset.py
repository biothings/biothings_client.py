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
        self.mgs = biothings_client.get_client("geneset")

    def test_metadata(self):
        meta = self.mgs.metadata()
        self.assertTrue("src" in meta)
        self.assertTrue("stats" in meta)
        self.assertTrue("total" in meta['stats'])

    def test_getgeneset(self):
        id = "WP100"
        gs = self.mgs.getgeneset(id)
        self.assertEqual(gs['_id'], id)
        self.assertEqual(gs['name'], 'Glutathione metabolism')
        self.assertEqual(gs['source'], 'wikipathways')
        self.assertEqual(gs['taxid'], '9606')
        self.assertGreaterEqual(len(gs['genes']), 19)
        self.assertEqual(gs['count'], len(gs['genes']))
        self.assertEqual(gs['wikipathways']['id'], id)

        # Check if all fields exists in wikipathways
        self.assertTrue('wikipathways' in gs)

        # Check if the gene exist with the values in the gene list:
        # "mygene_id": "2937",
        # "symbol": "GSS",

        # self.assertTrue(i['name'] == "2937dada" for i in gs['genes'])
        # self.assertTrue(gs['genes'].get)
        # self.assertTrue({
        #                     'name': 'Glutathione metabolism'
        #                 }.items() <= gs.items() )

    def test_query_fetch_all(self):

        # pdb-->reactome
        # q=source:reactome
        # _exists_:pdb ---> source:reactome

        # fetch_all won't work when caching is used.
        self.mgs.stop_caching()
        qres = self.mgs.query('source:reactome')
        total = qres['total']

        qres = self.mgs.query('source:reactome', fields='source,count,name', fetch_all=True)
        self.assertTrue(isinstance(qres, types.GeneratorType))
        self.assertEqual(total, len(list(qres)))

    def test_query_with_fields_as_list(self):
        qres1 = self.mgs.query("genes.ncbigene:1017", fields="name,symbol,source_id")
        qres2 = self.mgs.query("genes.ncbigene:1017", fields=["name", "symbol", "source_id"])
        self.assertTrue('hits' in qres1)
        self.assertEqual(len(qres1['hits']), 10)
        self.assertEqual(descore(qres1['hits']), descore(qres2['hits']))

    def test_getgeneset_with_fields(self):
        c = self.mgs.getgeneset("WP100", fields="chebi.name,genesetbl.inchi_key,pubgeneset.cid")
        self.assertTrue('_id' in c)
        self.assertTrue('chebi' in c)
        self.assertTrue('name' in c['chebi'])
        self.assertTrue('genesetbl' in c)
        self.assertTrue('inchi_key' in c['genesetbl'])
        self.assertTrue('pubgeneset' in c)
        self.assertTrue('cid' in c['pubgeneset'])

    # def get_getdrug(self):
    #     c = self.mgs.getdrug("CHEMBL1308")
    #     self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
    #     c = self.mgs.getdrug("7AXV542LZ4")
    #     self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
    #     c = self.mgs.getdrug("CHEBI:6431")
    #     self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

    # def test_getgenesets(self):
    #     c_li = self.mgs.getgenesets([
    #         "KTUFNOKKBVMGRW-UHFFFAOYSA-N",
    #         "HXHWSAZORRCQMX-UHFFFAOYSA-N",
    #         'DQMZLTXERSFNPB-UHFFFAOYSA-N'
    #     ])
    #     self.assertEqual(len(c_li), 3)
    #     self.assertEqual(c_li[0]['_id'], 'KTUFNOKKBVMGRW-UHFFFAOYSA-N')
    #     self.assertEqual(c_li[1]['_id'], 'HXHWSAZORRCQMX-UHFFFAOYSA-N')
    #     self.assertEqual(c_li[2]['_id'], 'DQMZLTXERSFNPB-UHFFFAOYSA-N')

    # def test_query(self):
    #     qres = self.mgs.query('genes.name:insulin', size=5)
    #     self.assertTrue('hits' in qres)
    #     self.assertEqual(len(qres['hits']), 5)

    def test_query_default_fields(self):
        self.mgs.query(q='glucose')

    def test_query_field(self):
        self.mgs.query(q='genes.ncbigene:1017')

    # def test_species_filter_blank_query(self):
    #     dog = self.mgs.query(species='9615')
    #     print(3, dog['hits'][0])
    #     self.assertEqual(dog['hits'][0]['taxid'], "9615")

    def test_species_filter_plus_query(self):
        dog = self.mgs.query(q='glucose', species='9615')
        self.assertEqual(dog['hits'][0]['taxid'], "9615")

    def test_query_by_id(self):
        query = self.mgs.query(q="_id:WP100")
        self.assertEqual(query['hits'][0]['_id'], "WP100")

    def test_query_by_name(self):
        kinase = self.mgs.query(q='name:kinase')
        self.assertIn('kinase', kinase['hits'][0]['name'].lower())

    def test_query_by_description(self):
        desc = self.mgs.query(q='description:cytosine deamination')
        self.assertIn('cytosine', desc['hits'][0]['description'].lower())
        self.assertIn('deamination', desc['hits'][0]['description'].lower())

    def test_query_by_source_go(self):
        go = self.mgs.query(q='source:go', fields='all')
        self.assertIn('go', go['hits'][0].keys())
        self.assertEqual(go['hits'][0]['source'], 'go')

    def test_query_by_source_ctd(self):
        ctd = self.mgs.query(q='source:ctd', fields='all')
        self.assertIn('ctd', ctd['hits'][0].keys())
        self.assertEqual(ctd['hits'][0]['source'], 'ctd')

    def test_query_by_source_msigdb(self):
        msigdb = self.mgs.query(q='source:msigdb', fields='all')
        self.assertIn('msigdb', msigdb['hits'][0].keys())
        self.assertEqual(msigdb['hits'][0]['source'], 'msigdb')

    def test_query_by_source_kegg(self):
        kegg = self.mgs.query(q='source:kegg', fields='all')
        self.assertIn('kegg', kegg['hits'][0].keys())
        self.assertEqual(kegg['hits'][0]['source'], 'kegg')

    def test_query_by_source_do(self):
        do = self.mgs.query(q='source:do', fields='all')
        self.assertIn('do', do['hits'][0].keys())
        self.assertEqual(do['hits'][0]['source'], 'do')

    def test_query_by_source_reactome(self):
        reactome = self.mgs.query(q='source:reactome', fields='all')
        self.assertIn('reactome', reactome['hits'][0].keys())
        self.assertEqual(reactome['hits'][0]['source'], 'reactome')

    def test_query_by_source_smpdb(self):
        smpdb = self.mgs.query(q='source:smpdb', fields='all')
        self.assertIn('smpdb', smpdb['hits'][0].keys())
        self.assertEqual(smpdb['hits'][0]['source'], 'smpdb')

    @unittest.skipIf(not biothings_client.caching_avail, "requests_cache not available")
    def test_caching(self):
        def _getgeneset():
            return self.mgs.getgenesets("1017")

        def _getgenesets():
            return self.mgs.getgenesets(["1017", "1018"])

        def _query():
            return self.mgs.query("cdk2")

        def _querymany():
            return self.mgs.querymany(['1017', '695'])

        def _cache_request(f):
            current_stdout = sys.stdout
            try:
                out = StringIO()
                sys.stdout = out
                r = f()
                output = out.getvalue().strip()
            finally:
                sys.stdout = current_stdout

            return ('[ from cache ]' in output, r)

        try:
            from_cache, pre_cache_r = _cache_request(_getgeneset)
            self.assertFalse(from_cache)

            if os.path.exists('mgsc.sqlite'):
                os.remove('mgsc.sqlite')
            self.mgs.set_caching('mgsc')

            # populate cache
            from_cache, cache_fill_r = _cache_request(_getgeneset)
            self.assertTrue(os.path.exists('mgsc.sqlite'))
            self.assertFalse(from_cache)
            # is it from the cache?
            from_cache, cached_r = _cache_request(_getgeneset)
            self.assertTrue(from_cache)

            self.mgs.stop_caching()
            # same query should be live - not cached
            from_cache, post_cache_r = _cache_request(_getgeneset)
            self.assertFalse(from_cache)

            self.mgs.set_caching('mgsc')

            # same query should still be sourced from cache
            from_cache, recached_r = _cache_request(_getgeneset)
            self.assertTrue(from_cache)

            self.mgs.clear_cache()
            # cache was cleared, same query should be live
            from_cache, clear_cached_r = _cache_request(_getgeneset)
            self.assertFalse(from_cache)

            # all requests should be identical except the _score, which can vary slightly
            for x in [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]:
                x.pop('_score', None)

            self.assertTrue(all([x == pre_cache_r for x in
                [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]]))

            # test getvariants POST caching
            from_cache, first_getgenes_r = _cache_request(_getgenesets)
            del first_getgenes_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_getgenes_r = _cache_request(_getgenesets)
            del second_getgenes_r
            self.assertTrue(from_cache)

            # test query GET caching
            from_cache, first_query_r = _cache_request(_query)
            del first_query_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_query_r = _cache_request(_query)
            del second_query_r
            self.assertTrue(from_cache)

            # test querymany POST caching
            from_cache, first_querymany_r = _cache_request(_querymany)
            del first_querymany_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_querymany_r = _cache_request(_querymany)
            del second_querymany_r
            self.assertTrue(from_cache)

        finally:
            self.mgs.stop_caching()
            os.remove('mgsc.sqlite')

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestGenesetClient)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
