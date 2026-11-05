"""inner and outer coding of nested fields (RFC 9651).

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    Item = Any  # placeholder: give it a real type in the milestone that needs it

__all__ = [
    "inner_parse",
    "inner_serialize",
]


def inner_parse(encoded: str) -> Item:
    """Pending behaviour defined by RFC 9651.

    Not implemented yet. See the ``coding.inner_parse()`` row in ROADMAP.md; this stub
    raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("inner_parse() is not implemented: RFC 9651")


def inner_serialize(item: Item) -> str:
    """Pending behaviour defined by RFC 9651.

    Not implemented yet. See the ``coding.inner_serialize()`` row in ROADMAP.md; this
    stub raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("inner_serialize() is not implemented: RFC 9651")
