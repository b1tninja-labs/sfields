"""list and dictionary parsing with member and parameter structure (RFC 9651 sec. 4.2.1, 4.2.2)."""

from __future__ import annotations

from ._cursor import Cursor
from .coding import scan_inner_list
from .item import scan_item, scan_parameters
from .keys import scan_key
from .model import Boolean, Dictionary, Item, List, Member

__all__ = [
    "parse_dictionary",
    "parse_list",
    "scan_dictionary",
    "scan_list",
    "scan_member",
]

OWS = " \t"


def scan_member(cursor: Cursor) -> Member:
    """Parsing an Item or Inner List (RFC 9651 sec. 4.2.1.1)."""
    if cursor.peek() == "(":
        return scan_inner_list(cursor)
    return scan_item(cursor)


def scan_list(cursor: Cursor) -> List:
    """Parsing a List (RFC 9651 sec. 4.2.1)."""
    members: list[Member] = []
    while not cursor.empty():
        members.append(scan_member(cursor))
        cursor.skip(OWS)
        if cursor.empty():
            return tuple(members)
        if cursor.take() != ",":
            raise cursor.fail("list members are separated by a comma", "4.2.1")
        cursor.skip(OWS)
        if cursor.empty():
            raise cursor.fail("trailing comma", "4.2.1")
    return tuple(members)


def scan_dictionary(cursor: Cursor) -> Dictionary:
    """Parsing a Dictionary (RFC 9651 sec. 4.2.2); a repeated key keeps its first position."""
    found: dict[str, Member] = {}
    while not cursor.empty():
        key = scan_key(cursor)
        member: Member
        if cursor.peek() == "=":
            cursor.take()
            member = scan_member(cursor)
        else:
            member = Item(Boolean(True), scan_parameters(cursor))
        found[key] = member
        cursor.skip(OWS)
        if cursor.empty():
            return Dictionary(found)
        if cursor.take() != ",":
            raise cursor.fail("dictionary members are separated by a comma", "4.2.2")
        cursor.skip(OWS)
        if cursor.empty():
            raise cursor.fail("trailing comma", "4.2.2")
    return Dictionary(found)


def parse_list(raw: str) -> List:
    """Parse ``raw`` as a whole field value of type "list", RFC 9651 sec. 4.2.1.

    Returns a tuple of Items and Inner Lists; an empty or all-SP value is the empty list.
    """
    from .typed import parse_field

    result = parse_field(raw, "list")
    if not isinstance(result, tuple):  # pragma: no cover
        raise TypeError("parse_field returned a non-List for a list")
    return result


def parse_dictionary(raw: str) -> Dictionary:
    """Parse ``raw`` as a whole field value of type "dictionary", RFC 9651 sec. 4.2.2.

    A repeated key keeps its first position and takes its last value.
    """
    from .typed import parse_field

    result = parse_field(raw, "dictionary")
    if not isinstance(result, Dictionary):  # pragma: no cover
        raise TypeError("parse_field returned a non-Dictionary for a dictionary")
    return result
