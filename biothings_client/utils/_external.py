"""
Any functions we provide as auxillary or helper
functions for the client are stored here and exposed in the
__init__ for usage by the users

We likely don't use these throughout the biothings.api core
code, but the users might so we want to maintain that here while
also indicating the purposes of the collection of functions in the
module
"""

from typing import Any, Union


def alwayslist(value: Any) -> Union[list, tuple]:
    """
    Simple transformation function that ensures the output is an iterable.

    Control Flow:
    If the input value is a {list, tuple}, we no-opt and return the value unchanged
    Otherwise, we wrap the value in a list and then return that list

    Example:

    >>> x = 'abc'
    >>> for xx in alwayslist(x):
    ...     print xx
    >>> x = ['abc', 'def']
    >>> for xx in alwayslist(x):
    ...     print xx

    """
    if isinstance(value, (list, tuple)):
        return value
    else:
        return [value]
