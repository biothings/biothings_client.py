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


class TestChemClient(unittest.TestCase):

    def setUp(self):
        self.mc = biothings_client.get_client("chem")
        self.query_list1 = ["QCYGXOCMWHSXSU-UHFFFAOYSA-N","ADFOMBKCPIMCOO-BTVCFUMJSA-N",
                            "DNUTZBZXLPWRJG-UHFFFAOYSA-N","DROLRDZYPMOKLM-BIVLZKPYSA-N",
                            "KPBZROQVTHLCDU-GOSISDBHSA-N","UTUUIUQHGDRVPU-UHFFFAOYSA-K",
                            "WZWDUEKBAIXVCC-IGHBBLSQSA-N","IAJIIJBMBCZPSW-BDAKNGLRSA-N",
                            "NASIOHFAYPRIAC-JTQLQIEISA-N","VGWIQFDQAFSSKA-UHFFFAOYSA-N"]

    def test_metadata(self):
        meta = self.mc.metadata()
        self.assertTrue("src" in meta)
        self.assertTrue("stats" in meta)
        self.assertTrue("total" in meta['stats'])

    def test_getchem(self):
        c = self.mc.getchem("ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        self.assertEqual(c['chebi']['name'], 'guanidine')

    def test_getchem_with_fields(self):
        c = self.mc.getchem("DB00553", fields="chebi.name,drugbank.id,pubchem.cid")
        self.assertTrue('_id' in c)
        self.assertTrue('chebi' in c)
        self.assertTrue('name' in c['chebi'])
        self.assertTrue('drugbank' in c)
        self.assertTrue('id' in c['drugbank'])
        self.assertTrue('pubchem' in c)
        self.assertTrue('cid' in c['pubchem'])

    def get_getdrug(self):
        c = self.mc.getdrug("DB00551")
        self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        c = self.mc.getdrug("CHEMBL1308")
        self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        c = self.mc.getdrug("7AXV542LZ4")
        self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        c = self.mc.getdrug("CHEBI:6431")
        self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")

        # PubChem CID
        # not working yet
        # c = self.mc.getdrug("CID:1990")
        # self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")
        # c = self.mc.getdrug("1990")
        # self.assertEqual(c['_id'], "ZRALSGWEFCBTJO-UHFFFAOYSA-N")


    def test_getchems(self):
        c_li = self.mc.getchems([
            "KTUFNOKKBVMGRW-UHFFFAOYSA-N",
            "HXHWSAZORRCQMX-UHFFFAOYSA-N",
            'DQMZLTXERSFNPB-UHFFFAOYSA-N'
        ])
        self.assertEqual(len(c_li), 3)
        self.assertEqual(c_li[0]['_id'], 'KTUFNOKKBVMGRW-UHFFFAOYSA-N')
        self.assertEqual(c_li[1]['_id'], 'HXHWSAZORRCQMX-UHFFFAOYSA-N')
        self.assertEqual(c_li[2]['_id'], 'DQMZLTXERSFNPB-UHFFFAOYSA-N')

    def test_query(self):
        qres = self.mc.query('chebi.name:albendazole', size=5)
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 5)

    def test_query_drugbank(self):
        qres = self.mc.query('drugbank.id:DB00536')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_chebi(self):
        qres = self.mc.query(r'chebi.id:CHEBI\:42820')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_chembl(self):
        qres = self.mc.query('chembl.smiles:"CC(=O)NO"')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'RRUDCFGSUDOHDG-UHFFFAOYSA-N')

    def test_query_drugcentral(self):
        qres = self.mc.query('drugcentral.drug_use.contraindication.umls_cui:C0023530', fields='drugcentral', size=50)
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 50)

        # not working yet
        # qres = self.mc.query('drugcentral.xrefs.kegg_drug:D00220')
        # self.assertTrue('hits' in qres)
        # self.assertEqual(len(qres['hits']), 1)
        # self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_pubchem(self):
        qres = self.mc.query('pubchem.molecular_formula:C2H5NO2', fields='pubchem', size=20)
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 20)

        qres = self.mc.query('pubchem.inchi:"InChI=1S/CH5N3/c2-1(3)4/h(H5,2,3,4)"')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_ginas(self):
        qres = self.mc.query('ginas.approvalID:JU58VJ6Y3B')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_pharmgkb(self):
        qres = self.mc.query('pharmgkb.id:PA164781028')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_ndc(self):
        qres = self.mc.query('ndc.productndc:"0085-0492"')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_sider(self):
        qres = self.mc.query('sider.meddra.umls_id:C0232487', fields='sider', size=5)
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 5)
        # self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_unii(self):
        qres = self.mc.query('unii.unii:JU58VJ6Y3B')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')

    def test_query_aeolus(self):
        qres = self.mc.query('aeolus.rxcui:50675')
        self.assertTrue('hits' in qres)
        self.assertEqual(len(qres['hits']), 1)
        self.assertEqual(qres['hits'][0]['_id'], 'ZRALSGWEFCBTJO-UHFFFAOYSA-N')


    def test_query_fetch_all(self):
        # fetch_all won't work when caching is used.
        self.mc.stop_caching()
        q = 'drugcentral.drug_use.contraindication.umls_cui:C0023530'
        qres = self.mc.query(q, size=0)
        total = qres['total']

        qres = self.mc.query(q, fields='drugcentral.drug_use', fetch_all=True)
        self.assertTrue(isinstance(qres, types.GeneratorType))
        self.assertEqual(total, len(list(qres)))

    def test_querymany(self):
        qres = self.mc.querymany(["ZRALSGWEFCBTJO-UHFFFAOYSA-N", "RRUDCFGSUDOHDG-UHFFFAOYSA-N"], verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mc.querymany("ZRALSGWEFCBTJO-UHFFFAOYSA-N,RRUDCFGSUDOHDG-UHFFFAOYSA-N", verbose=False)
        self.assertEqual(len(qres), 2)

    def test_querymany_with_scopes(self):
        qres = self.mc.querymany(["DB00536", 'DB00533'], scopes='drugbank.id', verbose=False)
        self.assertEqual(len(qres), 2)

        qres = self.mc.querymany(["DB00536", '4RZ82L2GY5'], scopes='drugbank.id,unii.unii', verbose=False)
        self.assertTrue(len(qres) >= 2)

    def test_querymany_fields(self):
        qres1 = self.mc.querymany(["DB00536", 'DB00533'], scopes='drugbank.id',
                                  fields=['drugbank.name', 'unii.registry_number'], verbose=False)
        self.assertEqual(len(qres1), 2)

        qres2 = self.mc.querymany(["DB00536", 'DB00533'], scopes='drugbank.id',
                                   fields='drugbank.name,unii.registry_number', verbose=False)
        self.assertEqual(len(qres2), 2)

        self.assertEqual(descore(qres1), descore(qres2))

    def test_querymany_notfound(self):
        qres = self.mc.querymany(['DB00536', 'DB00533', 'NA_TEST'], scopes='drugbank.id')
        self.assertEqual(len(qres), 3)
        self.assertEqual(qres[2], {"query": 'NA_TEST', "notfound": True})

    @unittest.skipIf(not biothings_client.df_avail, "pandas not available")
    def test_querymany_dataframe(self):
        from pandas import DataFrame
        qres = self.mc.querymany(self.query_list1, scopes='_id', fields="pubchem", as_dataframe=True)
        self.assertTrue(isinstance(qres, DataFrame))
        self.assertTrue('pubchem.inchi' in qres.columns)
        self.assertEqual(set(self.query_list1), set(qres.index))

    def test_querymany_step(self):
        qres1 = self.mc.querymany(self.query_list1, scopes='_id', fields="pubchem")
        default_step = self.mc.step
        self.mc.step = 3
        qres2 = self.mc.querymany(self.query_list1, scopes='_id', fields="pubchem")
        self.mc.step = default_step
        qres1 = descore(sorted(qres1, key=lambda doc: doc['_id']))
        qres2 = descore(sorted(qres2, key=lambda doc: doc['_id']))
        self.assertEqual(qres1, qres2)

    def test_get_fields(self):
        fields = self.mc.get_fields()
        self.assertTrue('drugbank.id' in fields.keys())
        self.assertTrue('pharmgkb.trade_names' in fields.keys())

        fields = self.mc.get_fields('unii')
        self.assertTrue('unii.molecular_formula' in fields.keys())

    @unittest.skipIf(not biothings_client.caching_avail, "requests_cache not available")
    def test_caching(self):

        def _getchem():
            return self.mc.getchem("ZRALSGWEFCBTJO-UHFFFAOYSA-N")

        def _getdrugs():
            return self.mc.getdrugs(["ZRALSGWEFCBTJO-UHFFFAOYSA-N", "RRUDCFGSUDOHDG-UHFFFAOYSA-N"])

        def _query():
            return self.mc.query('chebi.name:albendazole', size=5)

        def _querymany():
            return self.mc.querymany(["DB00536", 'DB00533'], scopes='drugbank.id')

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
            from_cache, pre_cache_r = _cache_request(_getchem)
            self.assertFalse(from_cache)

            cache_name = 'mcc'
            cache_file = cache_name + ".sqlite"

            if os.path.exists(cache_file):
                os.remove(cache_file)
            self.mc.set_caching(cache_name)

            # populate cache
            from_cache, cache_fill_r = _cache_request(_getchem)
            self.assertTrue(os.path.exists(cache_file))
            self.assertFalse(from_cache)
            # is it from the cache?
            from_cache, cached_r = _cache_request(_getchem)
            self.assertTrue(from_cache)

            self.mc.stop_caching()
            # same query should be live - not cached
            from_cache, post_cache_r = _cache_request(_getchem)
            self.assertFalse(from_cache)

            self.mc.set_caching(cache_name)

            # same query should still be sourced from cache
            from_cache, recached_r = _cache_request(_getchem)
            self.assertTrue(from_cache)

            self.mc.clear_cache()
            # cache was cleared, same query should be live
            from_cache, clear_cached_r = _cache_request(_getchem)
            self.assertFalse(from_cache)

            # all requests should be identical except the _score, which can vary slightly
            for x in [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]:
                x.pop('_score', None)

            self.assertTrue(all([x == pre_cache_r for x in
                [pre_cache_r, cache_fill_r, cached_r, post_cache_r, recached_r, clear_cached_r]]))

            # test getvariants POST caching
            from_cache, first_getgenes_r = _cache_request(_getdrugs)
            del first_getgenes_r
            self.assertFalse(from_cache)
            # should be from cache this time
            from_cache, second_getgenes_r = _cache_request(_getdrugs)
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
            self.mc.stop_caching()
            os.remove(cache_file)


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestChemClient)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
