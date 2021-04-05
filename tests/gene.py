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

class TestGeneClient(unittest.TestCase):

    def setUp(self):
        self.mg = biothings_client.get_client("gene")
        self.query_list1 = ['1007_s_at', '1053_at', '117_at', '121_at', '1255_g_at',
                            '1294_at', '1316_at', '1320_at', '1405_i_at', '1431_at']

    def test_metadata(self):
        meta = self.mg.metadata()
        self.assertTrue("stats" in meta)
        self.assertTrue("total_genes" in meta['stats'])

    def test_getgene(self):
        g = self.mg.getgene("1017")
        self.assertEqual(g['_id'], "1017")
        self.assertEqual(g['symbol'], 'CDK2')

    def test_getgene_with_fields(self):
        g = self.mg.getgene("1017", fields="name,symbol,refseq")
        self.assertTrue('_id' in g)
        self.assertTrue('name' in g)
        self.assertTrue('symbol' in g)
        self.assertTrue('refseq' in g)
        self.assertFalse('summary' in g)

    def test_getgene_with_fields_as_list(self):
        g1 = self.mg.getgene("1017", fields="name,symbol,refseq")
        g2 = self.mg.getgene("1017", fields=["name", "symbol", "refseq"])
        self.assertEqual(g1, g2)

    def test_getgenes(self):
        g_li = self.mg.getgenes([1017, 1018, 'ENSG00000148795'])
        self.assertEqual(len(g_li), 3)
        self.assertEqual(g_li[0]['_id'], '1017')
        self.assertEqual(g_li[1]['_id'], '1018')
        self.assertEqual(g_li[2]['_id'], '1586')

    def test_query(self):
        qres = self.mg.query('cdk2', size=5)
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 5)

    def test_query_with_fields_as_list(self):
        qres1 = self.mg.query("entrezgene:1017", fields="name,symbol,refseq")
        qres2 = self.mg.query("entrezgene:1017", fields=["name", "symbol", "refseq"])
        self.assertTrue('hits' in qres1)
        self.assertEqual(len(qres1['hits']), 1)
        self.assertEqual(descore(qres1['hits']), descore(qres2['hits']))

    def test_query_reporter(self):
        qres = self.mg.query('reporter:1000_at')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], '5595')

    def test_query_symbol(self):
        qres = self.mg.query('symbol:cdk2', species='mouse')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], '12566')

    def test_query_fetch_all(self):
        # fetch_all won't work when caching is used.
        self.mg.stop_caching()
        qres = self.mg.query('_exists_:pdb')
        total = qres['total']

        qres = self.mg.query('_exists_:pdb', fields='pdb', fetch_all=True)
        self.assertTrue(isinstance(qres, types.GeneratorType))
        self.assertEqual(total, len(list(qres)))

    def test_querymany(self):
        qres = self.mg.querymany([1017, '695'], verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mg.querymany("1017,695", verbose=False)
        self.assertEqual(len(qres), 2)

    def test_querymany_with_scopes(self):
        qres = self.mg.querymany([1017, '695'], scopes='entrezgene', verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mg.querymany([1017, 'BTK'], scopes='entrezgene,symbol', verbose=False)
        self.assertTrue(len(qres) >= 2)

    def test_querymany_species(self):
        qres = self.mg.querymany([1017, '695'], scopes='entrezgene', species='human', verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mg.findgenes([1017, '695'], scopes='entrezgene', species=9606, verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mg.findgenes([1017, 'CDK2'], scopes='entrezgene,symbol', species=9606, verbose=False)
        self.assertEqual(len(qres), 2)

    def test_querymany_fields(self):
        qres1 = self.mg.findgenes([1017, 'CDK2'], scopes='entrezgene,symbol', fields=['uniprot', 'unigene'], species=9606, verbose=False)
        self.assertEqual(len(qres1), 2)

        qres2 = self.mg.findgenes("1017,CDK2", scopes='entrezgene,symbol'.split(','), fields='uniprot,unigene', species=9606, verbose=False)
        self.assertEqual(len(qres2), 2)

        self.assertEqual(descore(qres1), descore(qres2))

    def test_querymany_notfound(self):
        qres = self.mg.findgenes([1017, '695', 'NA_TEST'], scopes='entrezgene', species=9606)
        self.assertEqual(len(qres), 3)
        self.assertEqual(qres[2], {"query": 'NA_TEST', "notfound": True})

    @unittest.skipIf(not biothings_client.df_avail, "pandas not available")
    def test_querymany_dataframe(self):
        from pandas import DataFrame
        qres = self.mg.querymany(self.query_list1, scopes='reporter', as_dataframe=True)
        self.assertTrue(isinstance(qres, DataFrame))
        self.assertTrue('name' in qres.columns)
        self.assertEqual(set(self.query_list1), set(qres.index))

    def test_querymany_step(self):
        qres1 = self.mg.querymany(self.query_list1, scopes='reporter')
        default_step = self.mg.step
        self.mg.step = 3
        qres2 = self.mg.querymany(self.query_list1, scopes='reporter')
        self.mg.step = default_step
        qres1 = descore(sorted(qres1, key=lambda doc: doc['_id']))
        qres2 = descore(sorted(qres2, key=lambda doc: doc['_id']))
        self.assertEqual(qres1, qres2)

    def test_get_fields(self):
        fields = self.mg.get_fields()
        self.assertTrue('uniprot' in fields.keys())
        self.assertTrue('exons' in fields.keys())

        fields = self.mg.get_fields('kegg')
        self.assertTrue('pathway.kegg' in fields.keys())

    @unittest.skipIf(not biothings_client.caching_avail, "requests_cache not available")
    def test_caching(self):
        def _getgene():
            return self.mg.getgene("1017")

        def _getgenes():
            return self.mg.getgenes(["1017", "1018"])

        def _query():
            return self.mg.query("cdk2")

        def _querymany():
            return self.mg.querymany(['1017', '695'])

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
            from_cache, pre_cache_r = _cache_request(_getgene)
            self.assertFalse(from_cache)

            if os.path.exists('mgc.sqlite'):
                os.remove('mgc.sqlite')
            self.mg.set_caching('mgc')

            # populate cache
            from_cache, cache_fill_r = _cache_request(_getgene)
            self.assertTrue(os.path.exists('mgc.sqlite'))
            self.assertFalse(from_cache)
            # is it from the cache?
            from_cache, cached_r = _cache_request(_getgene)
            self.assertTrue(from_cache)

            self.mg.stop_caching()
            # same query should be live - not cached
            from_cache, post_cache_r = _cache_request(_getgene)
            self.assertFalse(from_cache)

            self.mg.set_caching('mgc')

            # same query should still be sourced from cache
            from_cache, recached_r = _cache_request(_getgene)
            self.assertTrue(from_cache)

            self.mg.clear_cache()
            # cache was cleared, same query should be live
            from_cache, clear_cached_r = _cache_request(_getgene)
            self.assertFalse(from_cache)

            # all requests should be identical except the _score, which can vary slightly
            for x in [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]:
                x.pop('_score', None)

            self.assertTrue(all([x == pre_cache_r for x in
                [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]]))

            # test getvariants POST caching
            from_cache, first_getgenes_r = _cache_request(_getgenes)
            del first_getgenes_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_getgenes_r = _cache_request(_getgenes)
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
            self.mg.stop_caching()
            os.remove('mgc.sqlite')

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestGeneClient)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
