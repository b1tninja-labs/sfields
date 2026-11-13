"""A position in the ASCII input: the algorithms of RFC 9651 sec. 4.2 consume a string from the front."""

from __future__ import annotations

from .errors import ParseError, at

DIGITS = frozenset("0123456789")
LCALPHA = frozenset("abcdefghijklmnopqrstuvwxyz")
ALPHA = LCALPHA | frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
# RFC 9110 sec. 5.6.2: tchar
TCHAR = ALPHA | DIGITS | frozenset("!#$%&'*+-.^_`|~")
KEY_REST = LCALPHA | DIGITS | frozenset("_-.*")
LC_HEX = frozenset("0123456789abcdef")


class Cursor:
    """The not-yet-consumed tail of ``text`` begins at ``pos``."""

    __slots__ = ("pos", "text")

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def empty(self) -> bool:
        return self.pos >= len(self.text)

    def peek(self) -> str:
        """The first unconsumed character, or the empty string at the end."""
        return self.text[self.pos : self.pos + 1]

    def take(self) -> str:
        char = self.text[self.pos]
        self.pos += 1
        return char

    def skip(self, chars: str) -> None:
        """Discard leading characters drawn from ``chars`` (SP, or OWS = SP and HTAB)."""
        text, pos, end = self.text, self.pos, len(self.text)
        while pos < end and text[pos] in chars:
            pos += 1
        self.pos = pos

    def fail(self, reason: str, section: str) -> ParseError:
        return at(self.pos, reason, section)
