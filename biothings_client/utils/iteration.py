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
    Ingests an iterable sequence and combines all elements into a string

    :param sequence: Iterable sequence for element concatenation
    :param sep: Delimiter to apply to the elements when concatenating, defaults to ","
    :param quoted: Flag to enable quoting of the elements within the string, defaults to True

    :return: Returns a concatenated string of the elements from the input sequence
    :rtype: string
    """
    if isinstance(sequence, (list, tuple)):
        if quoted:
            string_transform = sep.join(['"{}"'.format(safe_str(x)) for x in sequence])
        else:
            string_transform = sep.join(["{}".format(safe_str(x)) for x in sequence])
    elif isinstance(sequence, str):
        logger.warning("Input sequence provided is already in string format. No operation performed")
        string_transform = sequence
    else:
        logger.warning("Input sequence non-iterable %s. Unable to perform concatenation operation", sequence)
        string_transform = sequence
    return string_transform
