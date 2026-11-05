"""the item types: integers, decimals, strings, tokens, byte sequences, booleans, dates.

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
    "parse_item",
]


def parse_item(raw: str) -> Item:
    """Pending behaviour defined by RFC 9651.

    Not implemented yet. See the ``item.parse_item()`` row in ROADMAP.md; this stub
    raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("parse_item() is not implemented: RFC 9651")
