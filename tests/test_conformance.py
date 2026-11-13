"""The working group's structured-field-tests, vendored under tests/data.

Provenance: https://github.com/httpwg/structured-field-tests at commit
10781e4a59c387853c900cc06cdd8a3fd7ae4134 (2026-10-30), licence in
tests/data/structured-field-tests/LICENSE.md. See tests/data/PROVENANCE.md. These vectors are
a secondary check; RFC 9651 is the norm.
"""

from __future__ import annotations

import decimal
import pathlib

import pytest

from sfields import run_suite
from sfields.conformance import SuiteResult, from_json, load_cases, to_json
from sfields.model import Decimal, Integer, Token

DATA = pathlib.Path(__file__).parent / "data" / "structured-field-tests"
FILES = sorted([*DATA.glob("*.json"), *DATA.glob("serialisation-tests/*.json")])

# can_fail vectors this implementation deliberately does not meet: it refuses base64 whose
# padding is partial or excessive, where RFC 9651 sec. 4.2.7 only says SHOULD NOT fail on
# *missing* padding. Pinned by name so a change in either direction is noticed.
EXPECTED_SKIPS = {"partially padded", "extra padding"}


def test_vendored_suite_is_present():
    assert len(FILES) >= 20
    assert (DATA / "LICENSE.md").is_file()


@pytest.mark.parametrize("path", FILES, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_vendored_suite_passes(path):
    result = run_suite(load_cases(path))
    assert result.ok, [f"{f.name}: {f.reason}" for f in result.failed]
    assert result.passed > 0
    assert {s.name for s in result.skipped} <= EXPECTED_SKIPS


def test_suite_covers_every_type():
    seen = set()
    for path in FILES:
        for case in load_cases(path):
            text = repr(case.get("expected"))
            for kind in ("token", "binary", "date", "displaystring"):
                if f"'{kind}'" in text:
                    seen.add(kind)
            if "expected" in case and case["header_type"] == "item":
                bare = case["expected"][0]
                seen.add(type(bare).__name__)
    assert {"token", "binary", "date", "displaystring", "int", "Decimal", "str", "bool"} <= seen


def test_each_failure_case_fails_loudly():
    # a must_fail record that parses is a failure of the implementation, and run_suite says so
    cases = [{"name": "accepts", "raw": ["1"], "header_type": "item", "must_fail": True}]
    result = run_suite(cases)
    assert [f.name for f in result.failed] == ["accepts"]
    assert result.passed == 0


def test_run_suite_reports_mismatches_and_skips():
    wrong = {"name": "wrong", "raw": ["1"], "header_type": "item", "expected": [2, []]}
    soft = {**wrong, "name": "soft", "can_fail": True}
    ok = {"name": "ok", "raw": ["1"], "header_type": "item", "expected": [1, []]}
    bad_canon = {**ok, "name": "canon", "canonical": ["2"]}
    result = run_suite([wrong, soft, ok, bad_canon])
    assert isinstance(result, SuiteResult)
    assert result.passed == 1
    assert [f.name for f in result.failed] == ["wrong", "canon"]
    assert [s.name for s in result.skipped] == ["soft"]
    assert not result.ok


def test_run_suite_does_not_swallow_a_crash():
    with pytest.raises(ValueError, match="field_type"):
        run_suite([{"name": "x", "raw": ["1"], "header_type": "map", "expected": []}])


def test_json_shape_roundtrip():
    item = from_json([{"__type": "token", "value": "a"}, [["k", 1]]], "item")
    assert item.value == Token("a")
    assert item.params["k"] == Integer(1)
    assert to_json(item) == [{"__type": "token", "value": "a"}, [["k", 1]]]
    assert from_json([], "list") == ()
    entries = from_json([["a", [decimal.Decimal("1.5"), []]]], "dictionary")
    assert entries["a"].value == Decimal(decimal.Decimal("1.5"))
