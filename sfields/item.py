"""the item types: integers, decimals, strings, tokens, byte sequences, booleans, dates,
display strings, and the parameters that ride on them (RFC 9651 sec. 4.2.3).

Each ``scan_*`` function follows its algorithm step by step on a cursor, because the
failure points are the specification: a regular expression would accept what a step
rejects. Whole-field entry points live in :mod:`sfields.typed`.
"""

from __future__ import annotations

import base64
import binascii
import decimal

from ._cursor import ALPHA, DIGITS, LC_HEX, TCHAR, Cursor
from .errors import ParseError, at
from .keys import scan_key
from .model import (
    BareItem,
    Boolean,
    ByteSequence,
    Date,
    Decimal,
    DisplayString,
    Integer,
    Item,
    Params,
    String,
    Token,
)

__all__ = [
    "parse_item",
    "scan_bare_item",
    "scan_item",
    "scan_parameters",
]

_B64 = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
_TOKEN_REST = TCHAR | frozenset(":/")


def _before(cursor: Cursor, reason: str, section: str) -> ParseError:
    """An error positioned at the character that was just consumed."""
    return at(cursor.pos - 1, reason, section)


def scan_number(cursor: Cursor) -> Integer | Decimal:
    """Parsing an Integer or Decimal (RFC 9651 sec. 4.2.4)."""
    is_decimal = False
    sign = 1
    digits: list[str] = []
    if cursor.peek() == "-":
        cursor.take()
        sign = -1
    if cursor.empty():
        raise cursor.fail("empty integer", "4.2.4")
    if cursor.peek() not in DIGITS:
        raise cursor.fail("a number needs a digit here", "4.2.4")
    while not cursor.empty():
        char = cursor.peek()
        if char in DIGITS:
            cursor.take()
            digits.append(char)
        elif not is_decimal and char == ".":
            if len(digits) > 12:
                raise cursor.fail("more than 12 digits before the decimal point", "4.2.4")
            cursor.take()
            digits.append(char)
            is_decimal = True
        else:
            break
        if not is_decimal and len(digits) > 15:
            raise _before(cursor, "integer longer than 15 digits", "4.2.4")
        if is_decimal and len(digits) > 16:
            raise _before(cursor, "decimal longer than 16 characters", "4.2.4")
    number = "".join(digits)
    if not is_decimal:
        return Integer(sign * int(number))
    if number.endswith("."):
        raise cursor.fail("decimal ends with '.'", "4.2.4")
    if len(number) - number.index(".") - 1 > 3:
        raise cursor.fail("more than three digits after the decimal point", "4.2.4")
    return Decimal(sign * decimal.Decimal(number))


def scan_string(cursor: Cursor) -> String:
    """Parsing a String (RFC 9651 sec. 4.2.5)."""
    if cursor.peek() != '"':
        raise cursor.fail("a String starts with a double quote", "4.2.5")
    cursor.take()
    out: list[str] = []
    while not cursor.empty():
        char = cursor.take()
        if char == "\\":
            if cursor.empty():
                raise cursor.fail("backslash at the end of input", "4.2.5")
            following = cursor.take()
            if following not in ('"', "\\"):
                raise _before(cursor, "only a double quote or backslash may be escaped", "4.2.5")
            out.append(following)
        elif char == '"':
            return String("".join(out))
        elif ord(char) <= 0x1F or ord(char) >= 0x7F:
            raise _before(cursor, "character not allowed in a String", "4.2.5")
        else:
            out.append(char)
    raise cursor.fail("String has no closing double quote", "4.2.5")


def scan_token(cursor: Cursor) -> Token:
    """Parsing a Token (RFC 9651 sec. 4.2.6)."""
    first = cursor.peek()
    if not first or (first not in ALPHA and first != "*"):
        raise cursor.fail("a Token starts with a letter or '*'", "4.2.6")
    text, start, end = cursor.text, cursor.pos, len(cursor.text)
    pos = start + 1
    while pos < end and text[pos] in _TOKEN_REST:
        pos += 1
    cursor.pos = pos
    return Token(text[start:pos])


def scan_byte_sequence(cursor: Cursor) -> ByteSequence:
    """Parsing a Byte Sequence (RFC 9651 sec. 4.2.7).

    Padding is optional and non-zero pad bits are tolerated, as the SHOULD NOTs of
    sec. 4.2.7 paragraphs 10 and 11 ask; characters outside the base64 alphabet fail.
    """
    if cursor.peek() != ":":
        raise cursor.fail("a Byte Sequence starts with a colon", "4.2.7")
    cursor.take()
    close = cursor.text.find(":", cursor.pos)
    if close < 0:
        raise cursor.fail("Byte Sequence has no closing colon", "4.2.7")
    start = cursor.pos
    content = cursor.text[start:close]
    bad = next((i for i, char in enumerate(content) if char not in _B64), None)
    if bad is not None:
        raise at(start + bad, "character outside the base64 alphabet", "4.2.7")
    body = content.rstrip("=")
    padding = len(content) - len(body)
    if "=" in body or len(body) % 4 == 1 or (padding and (len(body) + padding) % 4):
        raise at(start, "malformed base64", "4.2.7")
    try:
        data = base64.b64decode(body + "=" * (-len(body) % 4), validate=True)
    except binascii.Error as error:
        raise at(start, f"base64 decoding failed: {error}", "4.2.7") from error
    cursor.pos = close + 1
    return ByteSequence(data)


def scan_boolean(cursor: Cursor) -> Boolean:
    """Parsing a Boolean (RFC 9651 sec. 4.2.8)."""
    if cursor.peek() != "?":
        raise cursor.fail("a Boolean starts with '?'", "4.2.8")
    cursor.take()
    char = cursor.peek()
    if char == "1":
        cursor.take()
        return Boolean(True)
    if char == "0":
        cursor.take()
        return Boolean(False)
    raise cursor.fail("a Boolean is ?1 or ?0", "4.2.8")


def scan_date(cursor: Cursor) -> Date:
    """Parsing a Date (RFC 9651 sec. 4.2.9)."""
    if cursor.peek() != "@":
        raise cursor.fail("a Date starts with '@'", "4.2.9")
    cursor.take()
    start = cursor.pos
    number = scan_number(cursor)
    if isinstance(number, Decimal):
        raise at(start, "a Date is an integer", "4.2.9")
    return Date(number.value)


def scan_display_string(cursor: Cursor) -> DisplayString:
    """Parsing a Display String (RFC 9651 sec. 4.2.10, as corrected by erratum 8869)."""
    if cursor.text[cursor.pos : cursor.pos + 2] != '%"':
        raise cursor.fail('a Display String starts with %"', "4.2.10")
    cursor.pos += 2
    data = bytearray()
    while not cursor.empty():
        char = cursor.take()
        if ord(char) <= 0x1F or ord(char) >= 0x7F:
            raise _before(cursor, "character not allowed in a Display String", "4.2.10")
        if char == "%":
            octet_hex = cursor.text[cursor.pos : cursor.pos + 2]
            if len(octet_hex) < 2:
                raise _before(cursor, "truncated percent-encoding", "4.2.10")
            if octet_hex[0] not in LC_HEX or octet_hex[1] not in LC_HEX:
                raise _before(cursor, "percent-encoding needs two lowercase hex digits", "4.2.10")
            cursor.pos += 2
            data.append(int(octet_hex, 16))
        elif char == '"':
            try:
                return DisplayString(data.decode("utf-8"))
            except UnicodeDecodeError as error:
                raise _before(cursor, "content is not valid UTF-8", "4.2.10") from error
        else:
            data.append(ord(char))
    raise cursor.fail("Display String has no closing double quote", "4.2.10")


def scan_bare_item(cursor: Cursor) -> BareItem:
    """Parsing a Bare Item: dispatch on the first character (RFC 9651 sec. 4.2.3.1)."""
    first = cursor.peek()
    if not first:
        raise cursor.fail("an item was expected but the input ended", "4.2.3.1")
    if first == "-" or first in DIGITS:
        return scan_number(cursor)
    if first == '"':
        return scan_string(cursor)
    if first in ALPHA or first == "*":
        return scan_token(cursor)
    if first == ":":
        return scan_byte_sequence(cursor)
    if first == "?":
        return scan_boolean(cursor)
    if first == "@":
        return scan_date(cursor)
    if first == "%":
        return scan_display_string(cursor)
    raise cursor.fail("unrecognized item type", "4.2.3.1")


def scan_parameters(cursor: Cursor) -> Params:
    """Parsing Parameters (RFC 9651 sec. 4.2.3.2); a repeated key keeps its first position."""
    found: dict[str, BareItem] = {}
    while not cursor.empty():
        if cursor.peek() != ";":
            break
        cursor.take()
        cursor.skip(" ")
        key = scan_key(cursor)
        value: BareItem = Boolean(True)
        if cursor.peek() == "=":
            cursor.take()
            value = scan_bare_item(cursor)
        found[key] = value
    return Params(found)


def scan_item(cursor: Cursor) -> Item:
    """Parsing an Item (RFC 9651 sec. 4.2.3)."""
    bare = scan_bare_item(cursor)
    return Item(bare, scan_parameters(cursor))


def parse_item(raw: str) -> Item:
    """Parse ``raw`` as a whole field value of type "item", RFC 9651 sec. 4.2.3.

    Leading and trailing SP are discarded and anything else left over fails, as sec. 4.2
    requires. ``raw`` must be ASCII; for several field lines or bytes use
    :func:`sfields.typed.parse_field`.
    """
    from .typed import parse_field

    result = parse_field(raw, "item")
    if not isinstance(result, Item):  # pragma: no cover - parse_field returns an Item here
        raise TypeError("parse_field returned a non-Item for an item")
    return result
