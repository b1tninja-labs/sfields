"""The command line and the positional error constructor."""

from __future__ import annotations

import json

from sfields import ParseError, at
from sfields.cli import main


def test_at():
    error = at(3, "boom", "4.2.4")
    assert isinstance(error, ParseError)
    assert (error.offset, error.reason, error.section) == (3, "boom", "4.2.4")
    assert str(error) == "offset 3: boom (RFC 9651 sec. 4.2.4)"
    assert str(at(0, "x")) == "offset 0: x"


def test_cli_parse_prints_the_canonical_form(capsys):
    assert main(["parse", "a=1,   b;x=?0", "--type", "dictionary"]) == 0
    assert capsys.readouterr().out == "a=1, b;x=?0\n"


def test_cli_parse_json_uses_the_suite_shape(capsys):
    assert main(["parse", "1.5;a", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == [
        {"__type": "decimal", "value": "1.5"},
        [["a", True]],
    ]


def test_cli_reports_failure_with_status_1(capsys):
    assert main(["parse", "a,", "--type", "list"]) == 1
    assert "trailing comma" in capsys.readouterr().err


def test_cli_without_a_command_is_a_usage_error(capsys):
    assert main([]) == 2
    assert "usage" in capsys.readouterr().err
