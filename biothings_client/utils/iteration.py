from collections import Counter
from itertools import islice
from typing import (
    Any,
    Iterable,
    Iterator,
    List,
    Tuple,
    TypeVar,
    Union,
    overload,
)
import logging
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
elif sys.version_info <= (3, 7):
    from typing_extensions import Literal


logger = logging.getLogger("biothings.client")
logger.setLevel(logging.INFO)


T = TypeVar("T")


def safe_str(s: Any, encoding: str = "utf-8") -> str:
    """Perform proper encoding if input is an unicode string."""
    try:
        _s = str(s)
    except UnicodeEncodeError:
        _s = s.encode(encoding).decode(encoding)
    return _s


def list_itemcnt(li: Iterable[T]) -> List[Tuple[T, int]]:
    """
    Return number of occurrence for each item in the list.
    """
    return list(Counter(li).items())


@overload
def iter_n(iterable: Iterable[T], n: int, with_cnt: Literal[False]) -> Iterator[Tuple[T, ...]]: ...


@overload
def iter_n(iterable: Iterable[T], n: int, with_cnt: Literal[True]) -> Iterator[Tuple[Tuple[T, ...], int]]: ...


def iter_n(
    iterable: Iterable[T], n: int, with_cnt: bool = False
) -> Union[Iterator[Tuple[T, ...]], Iterator[Tuple[Tuple[T, ...], int]]]:
    """
    Iterate an iterator by chunks (of n)
    if with_cnt is True, return (chunk, cnt) each time
    """
    it = iter(iterable)
    cnt: int = 0
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        if with_cnt:
            cnt += len(chunk)
            yield (chunk, cnt)
        else:
            yield chunk


def concatenate_list(sequence: Iterable[Any], sep: str = ",", quoted: bool = True) -> Any:
    """
    Ingests an iterable sequence and combines all elements into a string

    :param sequence: Iterable sequence for element concatenation
    :param sep: Delimiter to apply to the elements when concatenating, defaults to ","
    :param quoted: Flag to enable quoting of the elements within the string, defaults to True

    :return: Returns a concatenated string of the elements from the input sequence
    :rtype: string
    """
    string_transform: Any
    if isinstance(sequence, (list, tuple)):
        if quoted:
            string_transform = sep.join(['"{}"'.format(safe_str(x)) for x in sequence])
        else:
            string_transform = sep.join(["{}".format(safe_str(x)) for x in sequence])
    elif isinstance(sequence, str):
        logger.debug("Input sequence provided is already in string format. No operation performed")
        string_transform = sequence
    else:
        logger.warning(
            "Input sequence non-iterable %s. Unable to perform concatenation operation",
            sequence,
        )
        string_transform = sequence
    return string_transform
