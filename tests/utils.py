''' Utils used for testing in biothings_client tests '''

def descore(hit):
    ''' Pops the _score from a hit or hit list - _score can vary slightly between runs causing
        tests to fail.  '''
    if isinstance(hit, list):
        res = []
        for o in hit:
            o.pop('_score', None)
            res.append(o)
        return res
    else:
        hit.pop('_score', None)
        return hit
