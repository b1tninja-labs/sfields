"""Inner Lists: parse and serialise (RFC 9651 sec. 3.1.1)."""

from __future__ import annotations

from ._cursor import Cursor
from .item import scan_item, scan_parameters
from .model import InnerList, Item
from .serialize import serialize_inner_list

__all__ = [
    "inner_parse",
    "inner_serialize",
    "scan_inner_list",
]


def scan_inner_list(cursor: Cursor) -> InnerList:
    """Parsing an Inner List, consuming from ``cursor`` (RFC 9651 sec. 4.2.1.2)."""
    if cursor.peek() != "(":
        raise cursor.fail("an Inner List starts with '('", "4.2.1.2")
    cursor.take()
    items: list[Item] = []
    while not cursor.empty():
        cursor.skip(" ")
        if cursor.peek() == ")":
            cursor.take()
            return InnerList(tuple(items), scan_parameters(cursor))
        items.append(scan_item(cursor))
        if cursor.peek() not in (" ", ")"):
            raise cursor.fail("an Inner List item is followed by SP or ')'", "4.2.1.2")
    raise cursor.fail("Inner List has no closing ')'", "4.2.1.2")


def inner_parse(encoded: str) -> InnerList:
    """Parse ``encoded`` as exactly one Inner List with its parameters, RFC 9651 sec. 4.2.1.2.

    Anything left after the Inner List fails.
    """
    cursor = Cursor(encoded)
    result = scan_inner_list(cursor)
    if not cursor.empty():
        raise cursor.fail("input remains after the Inner List", "4.2.1.2")
    return result


def inner_serialize(item: InnerList) -> str:
    """Serialize one Inner List with its parameters, RFC 9651 sec. 4.1.1.1."""
    return serialize_inner_list(item)
