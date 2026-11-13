"""the field_type entry point: a field value parsed as a List, Dictionary or Item (RFC 9651
sec. 4.2), and its serialisation (sec. 4.1).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from ._cursor import Cursor
from .errors import SerializeError, at
from .item import scan_item
from .model import Dictionary, Item, List
from .parse import scan_dictionary, scan_list
from .serialize import serialize_dictionary, serialize_item, serialize_list

__all__ = [
    "MAX_FIELD_LENGTH",
    "Field",
    "FieldType",
    "combine_field_lines",
    "parse_field",
    "serialize_field",
]

FieldType = Literal["list", "dictionary", "item"]
Field = List | Dictionary | Item

# An implementation limit, not an RFC 9651 rule: the RFC fixes only minimums a parser MUST
# support (1024 members, 16384 octets of Byte Sequence). One mebibyte leaves those far
# behind while bounding the work a hostile header can cause.
MAX_FIELD_LENGTH = 1 << 20


def combine_field_lines(lines: Iterable[str]) -> str:
    """Join field lines into one comma-separated value (RFC 9651 sec. 4.2 paragraph 11)."""
    return ", ".join(lines)


def parse_field(
    raw: bytes | str | Iterable[str],
    field_type: FieldType,
    *,
    max_length: int | None = MAX_FIELD_LENGTH,
) -> Field:
    """Parse a field value of the given type, RFC 9651 sec. 4.2.

    ``raw`` is the value as bytes or str, or several field lines that are combined with
    ", " first. Steps: convert to ASCII, discard leading SP, parse, discard leading SP,
    fail if anything remains. A failure raises :class:`sfields.errors.ParseError`; per
    sec. 4.2 paragraph 17 the caller then ignores the whole field or treats the message as
    malformed. ``max_length`` bounds the input (``None`` removes the bound).
    """
    if isinstance(raw, bytes | bytearray):
        try:
            text = bytes(raw).decode("ascii")
        except UnicodeDecodeError as error:
            raise at(error.start, "input is not ASCII", "4.2") from error
    elif isinstance(raw, str):
        text = raw
    else:
        text = combine_field_lines(raw)
    if max_length is not None and len(text) > max_length:
        raise at(max_length, f"input longer than the {max_length} character limit", "4.2")
    if not text.isascii():
        offset = next(i for i, char in enumerate(text) if ord(char) > 0x7F)
        raise at(offset, "input is not ASCII", "4.2")
    cursor = Cursor(text)
    cursor.skip(" ")
    output: Field
    if field_type == "list":
        output = scan_list(cursor)
    elif field_type == "dictionary":
        output = scan_dictionary(cursor)
    elif field_type == "item":
        output = scan_item(cursor)
    else:
        raise ValueError(f"field_type must be list, dictionary or item, not {field_type!r}")
    cursor.skip(" ")
    if not cursor.empty():
        raise cursor.fail("input remains after the field value", "4.2")
    return output


def serialize_field(structure: Field) -> str | None:
    """Serialize a top-level structure, RFC 9651 sec. 4.1.

    An empty List or Dictionary is not serialized at all (sec. 4.1 paragraph 2), which is
    ``None`` here: omit the field name too.
    """
    if isinstance(structure, tuple):
        return serialize_list(structure) if structure else None
    if isinstance(structure, Dictionary):
        return serialize_dictionary(structure) if len(structure) else None
    if isinstance(structure, Item):
        return serialize_item(structure)
    raise SerializeError("not a List, Dictionary or Item")
