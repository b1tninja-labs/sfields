"""the runner that replays the vendored test vectors.

The vectors are the HTTP working group's ``structured-field-tests`` (BSD-3-Clause style
licence, IETF Trust; see tests/data/structured-field-tests/LICENSE.md). They are a
secondary check: RFC 9651 is the norm, and a vector that disagrees with the RFC text is
reported to the suite, not obeyed.

The JSON format is the suite's README: ``raw`` field lines, ``header_type``, ``expected``,
``must_fail``, ``can_fail`` and ``canonical``. Decimals are read as the digits written
(``parse_float=decimal.Decimal``), never as binary floats.
"""

from __future__ import annotations

import base64
import decimal
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ParseError, SerializeError
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
    Member,
    Params,
    String,
    Token,
)
from .typed import Field, parse_field, serialize_field

__all__ = [
    "Failure",
    "SuiteResult",
    "from_json",
    "load_cases",
    "run_suite",
    "to_json",
]


@dataclass(frozen=True)
class Failure:
    """One vector that did not behave as the suite requires."""

    name: str
    reason: str


@dataclass(frozen=True)
class SuiteResult:
    """What a run found. ``skipped`` are ``can_fail`` vectors the implementation did not meet."""

    passed: int
    failed: tuple[Failure, ...]
    skipped: tuple[Failure, ...]

    @property
    def ok(self) -> bool:
        return not self.failed


def load_cases(path: Path | str) -> list[dict[str, Any]]:
    """Read one vector file, keeping decimals exact."""
    text = Path(path).read_text(encoding="utf-8")
    cases = json.loads(text, parse_float=decimal.Decimal)
    if not isinstance(cases, list):
        raise ValueError(f"{path}: a vector file is a JSON array of test records")
    return cases


def _bare(value: Any) -> BareItem:
    if isinstance(value, bool):
        return Boolean(value)
    if isinstance(value, int):
        return Integer(value)
    if isinstance(value, decimal.Decimal):
        return Decimal(value)
    if isinstance(value, str):
        return String(value)
    if isinstance(value, Mapping):
        kind, body = value["__type"], value["value"]
        if kind == "token":
            return Token(body)
        if kind == "binary":
            return ByteSequence(base64.b32decode(body + "=" * (-len(body) % 8)))
        if kind == "date":
            return Date(body)
        if kind == "displaystring":
            return DisplayString(body)
    raise ValueError(f"not a bare item in the suite's JSON: {value!r}")


def _params(pairs: Any) -> Params:
    return Params([(key, _bare(value)) for key, value in pairs])


def _member(value: Any) -> Member:
    first, params = value
    if isinstance(first, list):
        return InnerList(tuple(Item(_bare(b), _params(p)) for b, p in first), _params(params))
    return Item(_bare(first), _params(params))


def from_json(expected: Any, header_type: str) -> Field:
    """The suite's ``expected`` structure as a model value (suite README, Test Format)."""
    if header_type == "item":
        item = _member(expected)
        if isinstance(item, InnerList):
            raise ValueError("an item cannot be an Inner List")
        return item
    if header_type == "list":
        return tuple(_member(member) for member in expected)
    if header_type == "dictionary":
        return Dictionary([(key, _member(member)) for key, member in expected])
    raise ValueError(f"unknown header_type {header_type!r}")


def _bare_json(value: BareItem) -> Any:
    match value:
        case Boolean(v) | String(v) | Integer(v) | Decimal(v):
            return v
        case Token(v):
            return {"__type": "token", "value": v}
        case ByteSequence(v):
            return {"__type": "binary", "value": base64.b32encode(v).decode("ascii")}
        case Date(v):
            return {"__type": "date", "value": v}
        case DisplayString(v):
            return {"__type": "displaystring", "value": v}
    raise ValueError(f"not a bare item: {value!r}")


def _params_json(params: Params) -> list[Any]:
    return [[key, _bare_json(value)] for key, value in params.items()]


def _member_json(member: Member) -> Any:
    if isinstance(member, InnerList):
        return [
            [[_bare_json(i.value), _params_json(i.params)] for i in member.items],
            _params_json(member.params),
        ]
    return [_bare_json(member.value), _params_json(member.params)]


def to_json(structure: Field) -> Any:
    """A model value as the suite's ``expected`` structure; Decimals stay ``decimal.Decimal``."""
    if isinstance(structure, tuple):
        return [_member_json(member) for member in structure]
    if isinstance(structure, Dictionary):
        return [[key, _member_json(member)] for key, member in structure.items()]
    return _member_json(structure)


def _canonical(case: Mapping[str, Any], produced: str | None) -> str | None:
    """Compare serialisation with the vector's canonical form; None when they agree."""
    want = list(case["canonical"] if "canonical" in case else case.get("raw", ()))
    got = [] if produced is None else [produced]
    if got == want:
        return None
    return f"serialized to {got!r}, the vector wants {want!r}"


def _verdict(case: Mapping[str, Any]) -> str | None:
    """None when the vector is met, otherwise why not."""
    header_type = case["header_type"]
    must_fail = bool(case.get("must_fail", False))
    if "raw" in case:
        try:
            parsed = parse_field(case["raw"], header_type, max_length=None)
        except ParseError as error:
            return None if must_fail else f"parse failed: {error}"
        if must_fail:
            return f"parsed to {parsed!r}, the vector must fail"
        expected = from_json(case["expected"], header_type)
        if parsed != expected:
            return f"parsed to {parsed!r}, the vector expects {expected!r}"
        try:
            return _canonical(case, serialize_field(parsed))
        except SerializeError as error:
            return f"serialize failed: {error}"
    expected = from_json(case["expected"], header_type)
    try:
        produced = serialize_field(expected)
    except SerializeError:
        return None if must_fail else "serialize failed on a value that must serialize"
    if must_fail:
        return f"serialized to {produced!r}, the vector must fail"
    return _canonical(case, produced)


def run_suite(cases: Iterable[Mapping[str, Any]]) -> SuiteResult:
    """Replay test records and report; design (the runner for the working group suite).

    A record with ``raw`` is parsed and its result compared with ``expected``, then
    serialised and compared with ``canonical`` (or ``raw``). A record without ``raw`` is a
    serialisation case. ``must_fail`` records must be refused with a
    :class:`~sfields.errors.ParseError` or :class:`~sfields.errors.SerializeError`; any
    other exception propagates, because a crash is not a refusal. A ``can_fail`` record
    that is not met is ``skipped``, never counted as passed.
    """
    passed = 0
    failed: list[Failure] = []
    skipped: list[Failure] = []
    for case in cases:
        why = _verdict(case)
        if why is None:
            passed += 1
        elif case.get("can_fail", False):
            skipped.append(Failure(case["name"], why))
        else:
            failed.append(Failure(case["name"], why))
    return SuiteResult(passed, tuple(failed), tuple(skipped))
