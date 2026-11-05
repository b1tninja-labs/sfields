"""positional parse errors rather than a bare ValueError.

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    ParseError = Any  # placeholder: give it a real type in the milestone that needs it

__all__ = [
    "at",
]


def at(offset: int, reason: str) -> ParseError:
    """Pending behaviour defined by design.

    Not implemented yet. See the ``errors.at()`` row in ROADMAP.md; this stub raises on
    purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("at() is not implemented: design")
