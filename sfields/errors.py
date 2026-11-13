"""positional parse errors rather than a bare ValueError.

A parse failure in RFC 9651 is all or nothing (sec. 4.2 paragraph 17), so the error
carries what a person debugging a header needs: the offset into the ASCII input at which
the algorithm gave up, a reason, and the section of RFC 9651 whose step failed.
"""

from __future__ import annotations

__all__ = [
    "ParseError",
    "SerializeError",
    "at",
]


class ParseError(ValueError):
    """Parsing failed; the whole field value is to be ignored (RFC 9651 sec. 4.2)."""

    def __init__(self, offset: int, reason: str, section: str = "") -> None:
        self.offset = offset
        self.reason = reason
        self.section = section
        where = f" (RFC 9651 sec. {section})" if section else ""
        super().__init__(f"offset {offset}: {reason}{where}")


class SerializeError(ValueError):
    """The structure cannot be serialized (RFC 9651 sec. 4.1)."""


def at(offset: int, reason: str, section: str = "") -> ParseError:
    """Build the positional error every parse failure raises (design, anchored on RFC 9651 sec. 4.2).

    ``offset`` is a character offset into the ASCII input, ``reason`` says what was wrong
    and ``section`` names the RFC 9651 section whose step failed. The caller raises it.
    """
    return ParseError(offset, reason, section)
