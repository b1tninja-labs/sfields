"""canonical serialisation with byte-exact round trip (RFC 9651 sec. 4.1)."""

from __future__ import annotations

import base64
import decimal
from collections.abc import Mapping

from ._cursor import ALPHA, TCHAR
from .errors import SerializeError
from .keys import serialize_key
from .model import (
    BareItem,
    Boolean,
    ByteSequence,
    Date,
    Decimal,
    Dictionary,
    DisplayString,
    InnerList,
    Integer,
    Item,
    List,
    Member,
    Params,
    String,
    Token,
)

__all__ = [
    "serialize_bare_item",
    "serialize_dictionary",
    "serialize_inner_list",
    "serialize_item",
    "serialize_list",
    "serialize_parameters",
]

INT_LIMIT = 999_999_999_999_999
_TOKEN_REST = TCHAR | frozenset(":/")
_ROUND = decimal.Context(prec=60, rounding=decimal.ROUND_HALF_EVEN)
_MILLI = decimal.Decimal("0.001")


def _integer(value: object) -> str:
    """Serializing an Integer (RFC 9651 sec. 4.1.4)."""
    if type(value) is not int or not -INT_LIMIT <= value <= INT_LIMIT:
        raise SerializeError(f"{value!r} is not an integer within +-999,999,999,999,999")
    return str(value)


def _decimal(value: decimal.Decimal) -> str:
    """Serializing a Decimal (RFC 9651 sec. 4.1.5): three places, ties to even."""
    if not isinstance(value, decimal.Decimal) or not value.is_finite():
        raise SerializeError(f"{value!r} is not a decimal number")
    try:
        rounded = value.quantize(_MILLI, context=_ROUND)
    except decimal.InvalidOperation as error:
        raise SerializeError(f"{value!r} is out of range for a Decimal") from error
    whole, _, fraction = f"{abs(rounded):f}".partition(".")
    if len(whole) > 12:
        raise SerializeError(f"{value!r} has more than 12 digits before the decimal point")
    return f"{'-' if rounded < 0 else ''}{whole}.{fraction.rstrip('0') or '0'}"


def _string(value: str) -> str:
    """Serializing a String (RFC 9651 sec. 4.1.6)."""
    if not value.isascii() or any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):
        raise SerializeError("a String holds only printable ASCII")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _token(value: str) -> str:
    """Serializing a Token (RFC 9651 sec. 4.1.7)."""
    if not value or not value.isascii():
        raise SerializeError("a Token is non-empty ASCII")
    if (value[0] not in ALPHA and value[0] != "*") or any(c not in _TOKEN_REST for c in value[1:]):
        raise SerializeError(f"{value!r} is not a Token")
    return value


def _display_string(value: str) -> str:
    """Serializing a Display String (RFC 9651 sec. 4.1.11)."""
    try:
        data = value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise SerializeError("a Display String cannot hold surrogates") from error
    out = ['%"']
    for byte in data:
        if byte in (0x25, 0x22) or byte <= 0x1F or byte >= 0x7F:
            out.append(f"%{byte:02x}")
        else:
            out.append(chr(byte))
    out.append('"')
    return "".join(out)


def serialize_bare_item(value: BareItem) -> str:
    """Serializing a Bare Item (RFC 9651 sec. 4.1.3.1)."""
    match value:
        case Integer(v):
            return _integer(v)
        case Decimal(v):
            return _decimal(v)
        case String(v):
            return _string(v)
        case Token(v):
            return _token(v)
        case ByteSequence(v):
            if not isinstance(v, bytes | bytearray):
                raise SerializeError("a Byte Sequence holds bytes")
            return ":" + base64.b64encode(v).decode("ascii") + ":"
        case Boolean(v):
            if not isinstance(v, bool):
                raise SerializeError("a Boolean holds a bool")
            return "?1" if v else "?0"
        case Date(v):
            return "@" + _integer(v)
        case DisplayString(v):
            return _display_string(v)
    raise SerializeError(f"{value!r} is not a bare item")


def serialize_parameters(params: Params | Mapping[str, BareItem]) -> str:
    """Serializing Parameters (RFC 9651 sec. 4.1.1.2): Boolean true is the bare key."""
    out = []
    for key, value in params.items():
        out.append(";" + serialize_key(key))
        if value != Boolean(True):
            out.append("=" + serialize_bare_item(value))
    return "".join(out)


def serialize_item(item: Item) -> str:
    """Serializing an Item (RFC 9651 sec. 4.1.3)."""
    return serialize_bare_item(item.value) + serialize_parameters(item.params)


def serialize_inner_list(inner: InnerList) -> str:
    """Serializing an Inner List (RFC 9651 sec. 4.1.1.1)."""
    body = " ".join(serialize_item(item) for item in inner.items)
    return "(" + body + ")" + serialize_parameters(inner.params)


def _member(member: Member) -> str:
    if isinstance(member, InnerList):
        return serialize_inner_list(member)
    if isinstance(member, Item):
        return serialize_item(member)
    raise SerializeError(f"{member!r} is not an Item or Inner List")


def serialize_list(members: List) -> str:
    """Serialize a List, RFC 9651 sec. 4.1.1.

    An empty List gives the empty string; whether to omit the whole field is the caller's
    decision (sec. 4.1 paragraph 2, see :func:`sfields.typed.serialize_field`).
    """
    return ", ".join(_member(member) for member in members)


def serialize_dictionary(entries: Dictionary | Mapping[str, Member]) -> str:
    """Serialize a Dictionary, RFC 9651 sec. 4.1.2.

    A member whose value is Boolean true is written as its bare key followed by its
    parameters. Accepts a :class:`~sfields.model.Dictionary` or an ordered mapping.
    """
    out = []
    for key, member in entries.items():
        text = serialize_key(key)
        if isinstance(member, Item) and member.value == Boolean(True):
            text += serialize_parameters(member.params)
        else:
            text += "=" + _member(member)
        out.append(text)
    return ", ".join(out)
