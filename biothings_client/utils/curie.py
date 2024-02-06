"""
Methods that provide CURIE ID query support to the biothings client
"""

import functools
import logging
import re
from typing import Iterable

from . import str_types

logger = logging.getLogger("biothings.client")


def generate_annotation_prefix_patterns(prefix_mapping):
    """
    Takes the optionally provided BIOLINK_MODEL_PREFIX_BIOTHINGS_MAPPING
    configuration and generates the regex patterns for matching against our
    annotation queries
    """
    biolink_curie_regex_list = []
    for (
        biolink_prefix,
        mapping,
    ) in prefix_mapping.items():
        expression = re.compile(rf"({biolink_prefix}):(?P<term>[^:]+)", re.I)
        field_match = mapping["field"]
        pattern = (expression, field_match)
        biolink_curie_regex_list.append(pattern)
    return biolink_curie_regex_list


def parse_query(query, regex_mapping):
    """
    Parsing method for handling the provided query

    Inputs Arguments:
    query: string argument indicating the id value to search against our indices
    Can be of the form:
    _id = <term>
    _id = <scope>:<term>
    regex_mapping: dictionary mapping of the following structure:
    <regex_pattern>:<matched_fields>

    Outputs:
    Returns a tuple of the modified or unmodified query and any potential transformed fields
    """
    discovered_fields = []
    for regex, fields in regex_mapping:
        match = re.fullmatch(regex, query)
        if match:
            logger.debug(f"Discovered match: {regex} -> {query}")
            named_groups = match.groupdict()
            query = named_groups.get("term", query)
            discovered_fields = named_groups.get("scope", [])
            logger.debug(f"Transformed query: {query} Discovered fields: {fields}")
            break
    return (query, discovered_fields)


def transform_query(func):
    """
    Decorator for adding support to the CURIE ID querying without modifying the
    original signature API for the clients.

    Intended to support the _get_annotation and _get_annotations client methods
    """

    @functools.wraps(func)
    def _support_curie_id(self, *args, **kwargs):
        """
        Provides the regex pattern matching over the associated query to extract potentially
        embedded fields within the term

        In the case of supporting CURIE ID values, we leverage the biolink prefixes to map the
        biolink term to an equivalent biothings term.

        Otherwise we default to atttempting to support the basic <scope>:<term> structure

        This method handles the GET request method _get_annotation which expects a singular ID
        """

        query = ""
        fields = ""
        if len(args) == 0:
            query = str(kwargs.get("_id", query))
            fields = kwargs.get("fields", fields)
        elif len(args) == 1:
            query = str(args[0])
            fields = kwargs.get("fields", fields)
        elif len(args) == 2:
            query = str(args[0])
            fields = args[1]

        input_fields = self._format_list(fields)

        logger.debug(f"Input prior to transformation <query: {query}> <fields: {fields}>")
        query, discovered_fields = parse_query(query, self.annotation_prefix_patterns)
        discovered_fields = self._format_list(discovered_fields)
        total_fields = input_fields + discovered_fields

        args = ()
        kwargs["_id"] = query
        kwargs["fields"] = total_fields

        return func(self, *args, **kwargs)

    @functools.wraps(func)
    def _support_multiple_curie_id(self, *args, **kwargs):
        """
        Provides the regex pattern matching over the associated query to extract potentially
        embedded fields within the term

        In the case of supporting CURIE ID values, we leverage the biolink prefixes to map the
        biolink term to an equivalent biothings term.

        Otherwise we default to atttempting to support the basic <scope>:<term> structure

        This method handles the POST request method _get_annotations which expects a collection of
        ID values
        """
        query_collection = []
        fields = []
        if len(args) == 0:
            query_collection = kwargs.get("ids", query_collection)
            fields = kwargs.get("fields", fields)
        elif len(args) == 1:
            query_collection = args[0]
            fields = kwargs.get("fields", fields)
        elif len(args) == 2:
            query_collection = args[0]
            fields = args[1]

        if isinstance(query_collection, str_types):
            if query_collection == "":
                query_collection = []
            else:
                query_delimiter = ","
                query_collection = query_collection.split(query_delimiter)

        if not (isinstance(query_collection, (list, tuple, Iterable))):
            raise ValueError(f'Input "ids" must be an iterable type. "ids" is of type {type(query_collection)}')

        logger.debug(f"Input prior to transformation <query values: {query_collection}> <fields: {fields}>")

        query_aggregation = []
        field_aggregation = self._format_list(fields)
        for query_entry in query_collection:
            query, discovered_fields = parse_query(str(query_entry), self.annotation_prefix_patterns)
            discovered_fields = self._format_list(discovered_fields)

            query_aggregation.append(query)
            field_aggregation += discovered_fields

        args = ()
        kwargs["ids"] = query_aggregation
        kwargs["fields"] = field_aggregation

        return func(self, *args, **kwargs)

    function_mapping = {"_getannotation": _support_curie_id, "_getannotations": _support_multiple_curie_id}
    return function_mapping[func.__name__]
