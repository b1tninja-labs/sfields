"""the data model: one explicit type for every item (RFC 9651 sec. 3).

A Python ``int`` cannot say whether it is an Integer or a Date, nor a ``str`` whether it is
a String, a Token or a Display String, so every bare item is a small frozen dataclass.
Parameters and Dictionaries are ordered maps reachable by index and by key (sec. 3.1.2,
sec. 3.2).
"""

from __future__ import annotations

import decimal
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, overload

__all__ = [
    "BareItem",
    "Boolean",
    "ByteSequence",
    "Date",
    "Decimal",
    "Dictionary",
    "DisplayString",
    "InnerList",
    "Integer",
    "Item",
    "List",
    "Member",
    "OrderedMap",
    "Params",
    "String",
    "Token",
]


@dataclass(frozen=True)
class Integer:
    """RFC 9651 sec. 3.3.1."""

    value: int


@dataclass(frozen=True)
class Decimal:
    """RFC 9651 sec. 3.3.2."""

    value: decimal.Decimal


@dataclass(frozen=True)
class String:
    """RFC 9651 sec. 3.3.3: printable ASCII only."""

    value: str


@dataclass(frozen=True)
class Token:
    """RFC 9651 sec. 3.3.4."""

    value: str


@dataclass(frozen=True)
class ByteSequence:
    """RFC 9651 sec. 3.3.5."""

    value: bytes


@dataclass(frozen=True)
class Boolean:
    """RFC 9651 sec. 3.3.6."""

    value: bool


@dataclass(frozen=True)
class Date:
    """RFC 9651 sec. 3.3.7: seconds since 1970-01-01T00:00:00Z."""

    value: int


@dataclass(frozen=True)
class DisplayString:
    """RFC 9651 sec. 3.3.8 (with erratum 8869): Unicode scalar values."""

    value: str


BareItem = Integer | Decimal | String | Token | ByteSequence | Boolean | Date | DisplayString


class OrderedMap[V]:
    """Unique keys in insertion order, reachable by index and by key (sec. 3.1.2, 3.2).

    Built from a mapping or from (key, value) pairs; a repeated key keeps its first
    position and takes its last value, which is what sec. 4.2.2 and 4.2.3.2 do.
    """

    __slots__ = ("_pairs",)

    def __init__(self, pairs: Iterable[tuple[str, V]] | Mapping[str, V] = ()) -> None:
        source = pairs.items() if isinstance(pairs, Mapping) else pairs
        merged: dict[str, V] = {}
        for key, value in source:
            merged[key] = value
        self._pairs: tuple[tuple[str, V], ...] = tuple(merged.items())

    @overload
    def __getitem__(self, key: int) -> tuple[str, V]: ...
    @overload
    def __getitem__(self, key: str) -> V: ...
    def __getitem__(self, key: int | str) -> tuple[str, V] | V:
        if isinstance(key, int):
            return self._pairs[key]
        for name, value in self._pairs:
            if name == key:
                return value
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        for name, value in self._pairs:
            if name == key:
                return value
        return default

    def keys(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self._pairs)

    def items(self) -> tuple[tuple[str, V], ...]:
        return self._pairs

    def __contains__(self, key: object) -> bool:
        return any(name == key for name, _ in self._pairs)

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._pairs)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, OrderedMap) and self._pairs == other._pairs

    def __hash__(self) -> int:
        return hash(self._pairs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({list(self._pairs)!r})"


class Params(OrderedMap[BareItem]):
    """Ordered parameters: keys to bare items (sec. 3.1.2)."""

    __slots__ = ()


def _as_params(params: Any) -> Params:
    return params if isinstance(params, Params) else Params(params)


@dataclass(frozen=True)
class Item:
    """A bare item with its parameters (sec. 3.3)."""

    value: BareItem
    params: Params = field(default_factory=Params)

    def __post_init__(self) -> None:
        object.__setattr__(self, "params", _as_params(self.params))


@dataclass(frozen=True)
class InnerList:
    """An array of Items with parameters of its own (sec. 3.1.1)."""

    items: tuple[Item, ...] = ()
    params: Params = field(default_factory=Params)

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "params", _as_params(self.params))


Member = Item | InnerList
List = tuple[Member, ...]


class Dictionary(OrderedMap[Member]):
    """An ordered map of keys to Items or Inner Lists (sec. 3.2)."""

    __slots__ = ()
