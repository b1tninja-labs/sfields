"""list and dictionary parsing with member and parameter structure (RFC 9651).

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

__all__ = [
    "parse_dictionary",
    "parse_list",
]


def parse_list(raw: str) -> list:
    """Pending behaviour defined by RFC 9651.

    Not implemented yet. See the ``parse.parse_list()`` row in ROADMAP.md; this stub
    raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("parse_list() is not implemented: RFC 9651")


def parse_dictionary(raw: str) -> dict:
    """Pending behaviour defined by RFC 9651.

    Not implemented yet. See the ``parse.parse_dictionary()`` row in ROADMAP.md; this
    stub raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("parse_dictionary() is not implemented: RFC 9651")
