"""canonical serialisation with byte-exact round trip (RFC 9651).

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

__all__ = [
    "serialize_dictionary",
    "serialize_list",
]


def serialize_list(members: list) -> str:
    """Pending behaviour defined by RFC 9651 sec. 4.1.1.

    Not implemented yet. See the ``serialize.serialize_list()`` row in ROADMAP.md; this
    stub raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("serialize_list() is not implemented: RFC 9651 sec. 4.1.1")


def serialize_dictionary(entries: dict) -> str:
    """Pending behaviour defined by RFC 9651 sec. 4.1.2.

    Not implemented yet. See the ``serialize.serialize_dictionary()`` row in ROADMAP.md;
    this stub raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("serialize_dictionary() is not implemented: RFC 9651 sec. 4.1.2")
