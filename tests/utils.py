""" Utils used for testing in biothings_client tests """
import logging

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


def descore(hit):
    """Pops the _score from a hit or hit list - _score can vary slightly between runs causing
    tests to fail."""
    if isinstance(hit, list):
        res = []
        for o in hit:
            o.pop("_score", None)
            res.append(o)
        return res
    else:
        hit.pop("_score", None)
        return hit


def cache_request(fn):
    """Return a from_cache flag along with the request result
    The actual request is made in the given <fn> function"""
    from_cache = False
    res = None
    logger = logging.getLogger("biothings.client")
    with StringIO() as buf:
        handler = logging.StreamHandler(buf)
        logger.addHandler(handler)
        try:
            res = fn()
            buf.flush()
            from_cache = "[ from cache ]" in buf.getvalue().strip()
        finally:
            logger.removeHandler(handler)
    return (from_cache, res)
