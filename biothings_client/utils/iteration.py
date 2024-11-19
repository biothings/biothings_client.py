from collections import Counter
from itertools import islice
from typing import Iterable
import logging


logger = logging.getLogger("biothings.client")
logger.setLevel(logging.INFO)


def safe_str(s, encoding="utf-8"):
    """Perform proper encoding if input is an unicode string."""
    try:
        _s = str(s)
    except UnicodeEncodeError:
        _s = s.encode(encoding)
    return _s


def list_itemcnt(li):
    """
    Return number of occurrence for each item in the list.
    """
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


def concatenate_list(sequence: Iterable, sep: str = ",", quoted: bool = True) -> str:
    """
    Combine all the elements of a list into a string

    Inputs:
    sequence: iterable data structure
    sep: delimiter for joining the entries in `sequence`
    quoted: boolean indicating to quote the elements from sequence
            while concatenating all the elements
    Output:
    string value representing the concatenated values
    """
    if isinstance(sequence, Iterable):
        if quoted:
            string_transform = sep.join(['"{}"'.format(safe_str(x)) for x in sequence])
        else:
            string_transform = sep.join(["{}".format(safe_str(x)) for x in sequence])
    else:
        logger.debug("Input sequence non-iterable %s. Unable to perform concatenation operation", sequence)
        string_transform = sequence
    return string_transform
