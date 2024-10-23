import io
import logging


def cache_request(fn):
    """
    Return a from_cache flag along with the request result
    The actual request is made in the given <fn> function
    """
    from_cache = False
    res = None
    logger = logging.getLogger("biothings.client")
    with io.StringIO() as buf:
        handler = logging.StreamHandler(buf)
        logger.addHandler(handler)
        try:
            res = fn()
            buf.flush()
            from_cache = "[ from cache ]" in buf.getvalue().strip()
        finally:
            logger.removeHandler(handler)
    return (from_cache, res)
