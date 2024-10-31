from collections import Counter
from itertools import islice


def safe_str(s, encoding="utf-8"):
    """Perform proper encoding if input is an unicode string."""
    try:
        _s = str(s)
    except UnicodeEncodeError:
        _s = s.encode(encoding)
    return _s


def list_itemcnt(li):
    """Return number of occurrence for each item in the list."""
    return list(Counter(li).items())


def iter_n(iterable, n, with_cnt=False):
    """
    Iterate an iterator by chunks (of n)
    if with_cnt is True, return (chunk, cnt) each time
    """
    it = iter(iterable)
    if with_cnt:
        cnt = 0
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        if with_cnt:
            cnt += len(chunk)
            yield (chunk, cnt)
        else:
            yield chunk
