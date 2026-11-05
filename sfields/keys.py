"""keyed structured fields for dictionaries addressed by key (RFC 9651).

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

__all__ = [
    "parse_key",
]


def parse_key(raw: str) -> str:
    """Pending behaviour defined by RFC 9651.

    Not implemented yet. See the ``keys.parse_key()`` row in ROADMAP.md; this stub raises
    on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("parse_key() is not implemented: RFC 9651")
