"""Bare items: what each type accepts, what it refuses, and where the failure is reported.

The accept and refuse lists come from the step-by-step algorithms of RFC 9651 sec. 4.2.3
to 4.2.10 (read through rfclib), not from memory of RFC 8941.
"""

from __future__ import annotations

import decimal

import pytest

from sfields import ParseError, parse_item
from sfields.model import (
    Boolean,
    ByteSequence,
    Date,
    Decimal,
    DisplayString,
    Integer,
    String,
    Token,
)

D = decimal.Decimal


def value(text):
    return parse_item(text).value


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("42", Integer(42)),
        ("-42", Integer(-42)),
        ("0", Integer(0)),
        ("-0", Integer(0)),
        ("0002", Integer(2)),
        ("4.5", Decimal(D("4.5"))),
        ("-4.5", Decimal(D("-4.5"))),
        ("4.0", Decimal(D("4"))),
        ('"hello world"', String("hello world")),
        ('""', String("")),
        ("foo123/456", Token("foo123/456")),
        ("*foo", Token("*foo")),
        ("a:b/c", Token("a:b/c")),
        ("?1", Boolean(True)),
        ("?0", Boolean(False)),
        ("@0", Date(0)),
        ("@-1", Date(-1)),
    ],
)
def test_bare_items_valid(text, expected):
    assert value(text) == expected
    assert type(value(text)) is type(expected)


def test_types_are_distinct():
    assert Integer(1) != Decimal(D(1))
    assert Integer(1) != Date(1)
    assert String("a") != Token("a")
    assert String("a") != DisplayString("a")
    assert parse_item("1").value != parse_item("1.0").value
    assert parse_item("@1").value != parse_item("1").value


@pytest.mark.parametrize(
    "text",
    [
        "999999999999999",
        "-999999999999999",
        "999999999999.999",
        "-999999999999.999",
        "1.000",
        "0.001",
    ],
)
def test_integer_decimal_limits_accepted(text):
    parse_item(text)


@pytest.mark.parametrize(
    "text",
    [
        "1000000000000000",  # 16 digits
        "-1000000000000000",
        "1000000000000.0",  # 13 digits before the point
        "1.2345",  # 4 fraction digits
        "1.",
        "1.2.3",
        "-",
        "--1",
        "-.5",
        ".5",
        "1.0000000000000000",
    ],
)
def test_integer_decimal_limits_refused(text):
    with pytest.raises(ParseError):
        parse_item(text)


def test_decimal_value_keeps_its_digits():
    assert value("0.5") == Decimal(D("0.5"))
    assert value("-0.0") == Decimal(D("0"))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (r'"a\"b"', 'a"b'),
        (r'"a\\b"', "a\\b"),
        ('"  padded  "', "  padded  "),
        ('"~ !"', "~ !"),
    ],
)
def test_string_escapes(text, expected):
    assert value(text) == String(expected)


@pytest.mark.parametrize(
    "text",
    [
        r'"a\nb"',  # only a quote or backslash can be escaped (sec. 3.3.3 para 6)
        '"a\tb"',  # tab
        '"a\x7fb"',  # DEL
        "'single'",
        '"unterminated',
        '"ends with backslash\\',
        '"',
    ],
)
def test_string_refusals(text):
    with pytest.raises(ParseError):
        parse_item(text)


def test_string_1024_characters_and_tokens_512():
    # sec. 3.3.3 para 7 and 3.3.4 para 4: parsers MUST support at least these lengths
    assert value('"' + "a" * 1024 + '"') == String("a" * 1024)
    assert value("t" * 512) == Token("t" * 512)
    assert value("t" * 5000) == Token("t" * 5000)


def test_token_stops_at_a_non_token_character():
    with pytest.raises(ParseError):
        parse_item("foo bar")
    with pytest.raises(ParseError):
        parse_item("foo=bar")


@pytest.mark.parametrize("text", ["?2", "?", "?10", "?t", "1?"])
def test_boolean_invalid(text):
    with pytest.raises(ParseError):
        parse_item(text)


@pytest.mark.parametrize("text", ["!", "(", "[", "{", "<", "=", "_a", ".5", ""])
def test_unrecognised_first_character(text):
    with pytest.raises(ParseError):
        parse_item(text)


def test_trailing_garbage_refused_and_sp_discarded():
    with pytest.raises(ParseError):
        parse_item("1 2")
    assert value("  1  ") == Integer(1)
    with pytest.raises(ParseError):
        parse_item("1\t")  # HTAB is OWS in lists, not SP around an item (sec. 4.2 steps 2 and 6)


def test_byte_sequence():
    assert value(":cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==:") == ByteSequence(
        b"pretend this is binary content."
    )
    assert value("::") == ByteSequence(b"")
    # padding is optional (sec. 4.2.7 para 10) and non-zero pad bits are accepted (para 11)
    assert value(":aGVsbG8:") == ByteSequence(b"hello")
    assert value(":iZ==:") == ByteSequence(b"\x89")


@pytest.mark.parametrize(
    "text",
    [
        ":aGVsbG8=",  # no closing colon
        ":aGVs bG8=:",  # whitespace
        ":aGVs\nbG8=:",  # line feed (para 12)
        ":aGVs-bG8=:",  # URL-safe alphabet
        ":a:",  # one data character cannot be base64
        ":=aGVsbG8:",  # padding in the middle
    ],
)
def test_byte_sequence_refusals(text):
    with pytest.raises(ParseError):
        parse_item(text)


def test_date():
    assert value("@1659578233") == Date(1659578233)
    # sec. 3.3.7 para 5: all days in years 1 to 9999 MUST be supported
    assert value("@-62135596800") == Date(-62135596800)
    assert value("@253402214400") == Date(253402214400)


@pytest.mark.parametrize("text", ["@1.5", "@", "@-", "@a", "@@1", "@ 1"])
def test_date_refusals(text):
    with pytest.raises(ParseError):
        parse_item(text)


def test_display_string_erratum_8869():
    # Erratum 8869: the list of item types in sec. 3.3 omits Display Strings, but sec. 4.2.3.1
    # step 7 dispatches "%" to them. A parser that follows the printed list rejects these.
    assert value('%"This is intended for display to %c3%bcsers."') == DisplayString(
        "This is intended for display to üsers."
    )
    assert value('%""') == DisplayString("")
    assert value('%"a%22b%25c"') == DisplayString('a"b%c')
    assert value('%"%f0%9f%98%80"') == DisplayString("\U0001f600")


@pytest.mark.parametrize(
    "text",
    [
        '%"%C3%BC"',  # uppercase hex
        '%"%c3"',  # not UTF-8
        '%"%c3%28"',  # invalid continuation
        '%"%ed%a0%80"',  # an encoded surrogate
        '%"%c0%80"',  # overlong
        '%"ü"',  # raw non-ASCII (also not ASCII input)
        '%"unterminated',
        '%"a%2"',  # truncated escape
        '%"a%',
        '%"a\x01b"',
        '%"a\x7fb"',
        "%foo",
        '%"%zz"',
    ],
)
def test_display_string_refusals(text):
    with pytest.raises(ParseError):
        parse_item(text)


def test_display_string_in_a_dictionary_and_as_a_parameter():
    from sfields import parse_dictionary

    assert parse_dictionary('a=%"%c3%bc"')["a"].value == DisplayString("ü")
    assert parse_item('1;p=%"%c3%bc"').params["p"] == DisplayString("ü")


def test_errors_say_where_and_which_section():
    with pytest.raises(ParseError) as caught:
        parse_item("12345678901234567")
    assert caught.value.section == "4.2.4"
    assert caught.value.offset == 15
    assert "4.2.4" in str(caught.value)
    with pytest.raises(ParseError) as caught:
        parse_item('"abc\\q"')
    assert caught.value.offset == 5
    assert caught.value.section == "4.2.5"


def test_byte_sequence_16384():
    # sec. 3.3.5 para 4: parsers MUST support at least 16384 octets after decoding
    import base64

    payload = bytes(range(256)) * 64
    assert len(payload) == 16384
    text = ":" + base64.b64encode(payload).decode() + ":"
    assert value(text) == ByteSequence(payload)
