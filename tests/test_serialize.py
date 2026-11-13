"""Serialisation (RFC 9651 sec. 4.1): canonical output, refusals and rounding, plus a
property test that parse and serialise are inverse.
"""

from __future__ import annotations

import decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from sfields import (
    SerializeError,
    inner_serialize,
    parse_field,
    serialize_dictionary,
    serialize_field,
    serialize_item,
    serialize_list,
)
from sfields.model import (
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
    Params,
    String,
    Token,
)

D = decimal.Decimal


def one(bare):
    return serialize_item(Item(bare))


@pytest.mark.parametrize(
    ("bare", "text"),
    [
        (Integer(42), "42"),
        (Integer(-42), "-42"),
        (Integer(0), "0"),
        (Integer(999_999_999_999_999), "999999999999999"),
        (Integer(-999_999_999_999_999), "-999999999999999"),
        (String('a"b\\c'), '"a\\"b\\\\c"'),
        (String(""), '""'),
        (Token("foo123/456"), "foo123/456"),
        (Token("*a:b"), "*a:b"),
        (
            ByteSequence(b"pretend this is binary content."),
            ":cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==:",
        ),
        (ByteSequence(b""), "::"),
        (Boolean(True), "?1"),
        (Boolean(False), "?0"),
        (Date(1659578233), "@1659578233"),
        (Date(-62135596800), "@-62135596800"),
        (DisplayString("ü"), '%"%c3%bc"'),
        (DisplayString('say "hi" 100%'), '%"say %22hi%22 100%25"'),
        (DisplayString("a\tb"), '%"a%09b"'),
        (DisplayString("\U0001f600"), '%"%f0%9f%98%80"'),
        (DisplayString(""), '%""'),
    ],
)
def test_serialize_bare_items(bare, text):
    assert one(bare) == text


@pytest.mark.parametrize(
    ("value", "text"),
    [
        ("4.5", "4.5"),
        ("0.0", "0.0"),
        ("-0.0", "0.0"),
        ("2", "2.0"),
        ("1.0005", "1.0"),  # tie rounds to the even digit (sec. 4.1.5 step 2)
        ("1.0015", "1.002"),
        ("1.0025", "1.002"),
        ("1.0035", "1.004"),
        ("-1.0015", "-1.002"),
        ("-0.0004", "0.0"),  # rounds to zero, which is not "less than 0": no sign
        ("-0.0005", "0.0"),
        ("-0.0006", "-0.001"),
        ("5.230", "5.23"),
        ("123456789012.9996", "123456789013.0"),
        ("999999999999.999", "999999999999.999"),
        ("0.5", "0.5"),
    ],
)
def test_decimal_serialise_rounding(value, text):
    assert one(Decimal(D(value))) == text


def test_decimal_with_13_integer_digits_refused():
    with pytest.raises(SerializeError):
        one(Decimal(D("1000000000000.0")))
    with pytest.raises(SerializeError):
        one(Decimal(D("999999999999.9996")))  # rounds up to 13 digits
    with pytest.raises(SerializeError):
        one(Decimal(D("1E+100")))
    with pytest.raises(SerializeError):
        one(Decimal(D("NaN")))
    with pytest.raises(SerializeError):
        one(Decimal(D("Infinity")))


@pytest.mark.parametrize(
    "bare",
    [
        Integer(1_000_000_000_000_000),
        Integer(-1_000_000_000_000_000),
        Integer(True),  # a bool is not an integer item
        Date(253_402_214_400_000_000),
        String("tab\there"),
        String("nl\n"),
        String("del\x7f"),
        String("café"),
        Token(""),
        Token("1abc"),
        Token("a b"),
        Token("a,b"),
        Token("café"),
        DisplayString("\ud800"),  # sec. 4.1.11 para 13: surrogates fail
    ],
)
def test_serialize_refusals(bare):
    with pytest.raises(SerializeError):
        one(bare)


def test_boolean_true_param_serialises_bare():
    item = Item(Integer(1), Params({"a": Boolean(True), "b": Boolean(False)}))
    assert serialize_item(item) == "1;a;b=?0"


def test_serialize_dictionary_and_list():
    entries = Dictionary(
        [
            ("a", Item(Boolean(False))),
            ("b", Item(Boolean(True))),
            ("c", Item(Boolean(True), Params({"foo": Token("bar")}))),
            (
                "d",
                InnerList((Item(Integer(5)), Item(Integer(6))), Params({"valid": Boolean(True)})),
            ),
        ]
    )
    assert serialize_dictionary(entries) == "a=?0, b, c;foo=bar, d=(5 6);valid"
    assert serialize_dictionary({"a": Item(Integer(1))}) == "a=1"  # an ordered mapping works too
    assert serialize_list((Item(Token("a")), InnerList(()))) == "a, ()"
    assert (
        inner_serialize(InnerList((Item(String("x")),), Params({"q": Integer(1)}))) == '("x");q=1'
    )


def test_key_refusals_on_serialise():
    for key in ("A", "1a", "", "a b", "é"):
        with pytest.raises(SerializeError):
            serialize_dictionary({key: Item(Integer(1))})
        with pytest.raises(SerializeError):
            serialize_item(Item(Integer(1), Params({key: Integer(1)})))


def test_empty_list_and_dictionary_are_omitted():
    # sec. 4.1 para 2: an empty List or Dictionary is not serialised at all
    assert serialize_field(()) is None
    assert serialize_field(Dictionary()) is None
    assert serialize_list(()) == ""
    assert serialize_field(Item(Integer(1))) == "1"
    with pytest.raises(SerializeError):
        serialize_field("nope")


# -- property: parse(serialize(x)) == x, serialize(parse(t)) == t -------------------------

KEYS = st.from_regex(r"[a-z*][a-z0-9_.*-]{0,10}", fullmatch=True)
STRINGS = st.text(alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E), max_size=20)
TOKENS = st.from_regex(r"[A-Za-z*][A-Za-z0-9!#$%&'*+.^_`|~:/-]{0,10}", fullmatch=True)
DECIMALS = st.decimals(min_value=D("-999999999999.999"), max_value=D("999999999999.999"), places=3)
BARES: st.SearchStrategy[BareItem] = st.one_of(
    st.integers(-999_999_999_999_999, 999_999_999_999_999).map(Integer),
    DECIMALS.map(Decimal),
    STRINGS.map(String),
    TOKENS.map(Token),
    st.binary(max_size=20).map(ByteSequence),
    st.booleans().map(Boolean),
    st.integers(-62_135_596_800, 253_402_214_400).map(Date),
    st.text(alphabet=st.characters(exclude_categories=["Cs"]), max_size=10).map(DisplayString),
)
PARAMS = st.lists(st.tuples(KEYS, BARES), max_size=3, unique_by=lambda kv: kv[0]).map(Params)
ITEMS = st.builds(Item, BARES, PARAMS)
MEMBERS = st.one_of(ITEMS, st.builds(InnerList, st.lists(ITEMS, max_size=3).map(tuple), PARAMS))


@settings(max_examples=150, deadline=None)
@given(st.lists(MEMBERS, min_size=1, max_size=4).map(tuple))
def test_list_roundtrip_property(members):
    text = serialize_list(members)
    assert parse_field(text, "list") == members
    assert serialize_list(parse_field(text, "list")) == text


@settings(max_examples=150, deadline=None)
@given(st.lists(st.tuples(KEYS, MEMBERS), min_size=1, max_size=4, unique_by=lambda kv: kv[0]))
def test_dictionary_roundtrip_property(pairs):
    entries = Dictionary(pairs)
    text = serialize_dictionary(entries)
    assert parse_field(text, "dictionary") == entries
    assert serialize_dictionary(parse_field(text, "dictionary")) == text
