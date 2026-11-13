"""sfields -- structured field values, current specification.

The HTTP Specification maintenance and transport area published RFC 9651 in September 2024,
which obsoletes RFC 8941 and adds two item types, Dates and Display Strings (RFC 9651
Appendix D).
"""

from __future__ import annotations

from . import apps, cli, coding, conformance, errors, item, keys, model, parse, serialize, typed
from .coding import inner_parse, inner_serialize
from .conformance import run_suite
from .errors import ParseError, SerializeError, at
from .item import parse_item
from .keys import parse_key
from .parse import parse_dictionary, parse_list
from .serialize import serialize_dictionary, serialize_item, serialize_list
from .typed import parse_field, serialize_field

__version__ = "0.1.0"

__all__ = [
    "ParseError",
    "SerializeError",
    "__version__",
    "apps",
    "at",
    "cli",
    "coding",
    "conformance",
    "errors",
    "inner_parse",
    "inner_serialize",
    "item",
    "keys",
    "model",
    "parse",
    "parse_dictionary",
    "parse_field",
    "parse_item",
    "parse_key",
    "parse_list",
    "run_suite",
    "serialize",
    "serialize_dictionary",
    "serialize_field",
    "serialize_item",
    "serialize_list",
    "typed",
]
