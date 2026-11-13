"""dictionary and parameter keys (RFC 9651 sec. 4.1.1.3, sec. 4.2.3.3)."""

from __future__ import annotations

from ._cursor import KEY_REST, LCALPHA, Cursor
from .errors import SerializeError

__all__ = [
    "parse_key",
    "scan_key",
    "serialize_key",
]


def scan_key(cursor: Cursor) -> str:
    """Parsing a Key, consuming from ``cursor`` (RFC 9651 sec. 4.2.3.3)."""
    first = cursor.peek()
    if not first or (first not in LCALPHA and first != "*"):
        raise cursor.fail("a key starts with a lowercase letter or '*'", "4.2.3.3")
    text, start, end = cursor.text, cursor.pos, len(cursor.text)
    pos = start + 1
    while pos < end and text[pos] in KEY_REST:
        pos += 1
    cursor.pos = pos
    return text[start:pos]


def parse_key(raw: str) -> str:
    """Parse ``raw`` as exactly one key, RFC 9651 sec. 4.2.3.3.

    The whole input must be the key: anything left over is a failure here, although inside
    a Dictionary or Parameters the same algorithm simply stops at the first character that
    cannot belong to a key.
    """
    cursor = Cursor(raw)
    key = scan_key(cursor)
    if not cursor.empty():
        raise cursor.fail("character not allowed in a key", "4.2.3.3")
    return key


def serialize_key(key: str) -> str:
    """Serializing a Key (RFC 9651 sec. 4.1.1.3)."""
    if not key.isascii():
        raise SerializeError("key is not ASCII")
    if not key or any(char not in KEY_REST for char in key):
        raise SerializeError(f"key {key!r} contains characters a key cannot have")
    if key[0] not in LCALPHA and key[0] != "*":
        raise SerializeError(f"key {key!r} must start with a lowercase letter or '*'")
    return key
