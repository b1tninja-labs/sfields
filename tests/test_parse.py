"""Lists, Inner Lists, Dictionaries, parameters, keys and the field entry point
(RFC 9651 sec. 4.2 to 4.2.3.3).
"""

from __future__ import annotations

import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from sfields import (
    ParseError,
    inner_parse,
    parse_dictionary,
    parse_field,
    parse_key,
    parse_list,
)
from sfields.model import (
    Boolean,
    Dictionary,
    InnerList,
    Integer,
    Item,
    Params,
    String,
    Token,
)


def test_parse_list():
    members = parse_list('1, "a";x=2, (b c);y')
    assert members == (
        Item(Integer(1)),
        Item(String("a"), Params({"x": Integer(2)})),
        InnerList((Item(Token("b")), Item(Token("c"))), Params({"y": Boolean(True)})),
    )


def test_parse_dictionary():
    entries = parse_dictionary("a=1, b, c=(x y);q=?0")
    assert entries.keys() == ("a", "b", "c")
    assert entries["a"] == Item(Integer(1))
    assert entries["b"] == Item(Boolean(True))
    assert entries[2][0] == "c"  # by index as well as by key (sec. 3.2 para 2)
    assert entries["c"].params["q"] == Boolean(False)


def test_empty_list_and_dictionary():
    for text in ("", "   "):
        assert parse_list(text) == ()
        assert len(parse_dictionary(text)) == 0


def test_trailing_comma_fails():
    for text in ("a,", "a, ", "a,\t"):
        with pytest.raises(ParseError):
            parse_list(text)
    with pytest.raises(ParseError):
        parse_dictionary("a=1,")
    with pytest.raises(ParseError):
        parse_list(",")


def test_missing_comma_fails():
    with pytest.raises(ParseError):
        parse_list("a b")
    with pytest.raises(ParseError):
        parse_dictionary("a=1 b=2")
    with pytest.raises(ParseError):
        parse_list("a;b;")  # a parameter needs a key


def test_tab_is_ows_between_members():
    # sec. 4.2 para 12: the list and dictionary algorithms allow tabs
    assert len(parse_list("a,\tb\t,\tc")) == 3
    assert parse_dictionary("a=1\t,\tb=2").keys() == ("a", "b")


def test_dictionary_duplicate_key_keeps_first_position_last_value():
    entries = parse_dictionary("a=1, b=2, a=3")
    assert entries.keys() == ("a", "b")
    assert entries["a"] == Item(Integer(3))


def test_duplicate_parameter_keeps_first_position_last_value():
    item = parse_field("1;a=1;b=2;a=3", "item")
    assert item.params.items() == (("a", Integer(3)), ("b", Integer(2)))


def test_inner_parse():
    assert inner_parse("(1 2)") == InnerList((Item(Integer(1)), Item(Integer(2))))
    assert inner_parse("()") == InnerList(())
    assert inner_parse("( 1  2 );a=1") == InnerList(
        (Item(Integer(1)), Item(Integer(2))), Params({"a": Integer(1)})
    )
    with pytest.raises(ParseError):
        inner_parse("(1 2) x")


@pytest.mark.parametrize("text", ["(1,2)", "(1 2", "(1\t2)", "((1))", "(1;a=)", "(", "(1)x"])
def test_inner_list_refusals(text):
    # sec. 4.2.1.2: after an item the next character must be SP or ")"; Inner Lists do not nest
    with pytest.raises(ParseError):
        parse_list(text)


def test_inner_list_params_at_both_levels():
    (member,) = parse_list('("foo"; a=1;b=2);lvl=5')
    assert member.params["lvl"] == Integer(5)
    assert member.items[0].params.keys() == ("a", "b")


@pytest.mark.parametrize("key", ["a", "*", "a1", "a_b-c.d*", "*a", "a" * 64])
def test_parse_key(key):
    assert parse_key(key) == key


@pytest.mark.parametrize("key", ["", "A", "1a", "_a", "-a", ".a", "a b", "aB", "a=", "é"])
def test_key_charset(key):
    with pytest.raises(ParseError):
        parse_key(key)


def test_uppercase_key_is_refused_inside_a_dictionary():
    with pytest.raises(ParseError):
        parse_dictionary("A=1")
    with pytest.raises(ParseError):
        parse_field("1;A=1", "item")


def test_parse_field_steps():
    # sec. 4.2: ASCII conversion, leading SP, parse, leading SP, nothing may remain
    assert parse_field(b"  a  ", "item") == Item(Token("a"))
    assert parse_field(["a", "b"], "list") == (Item(Token("a")), Item(Token("b")))
    with pytest.raises(ParseError):
        parse_field(b"\xc3\xbc", "item")
    with pytest.raises(ParseError):
        parse_field("café", "item")
    with pytest.raises(ParseError):
        parse_field("a b", "item")
    with pytest.raises(ValueError, match="field_type"):
        parse_field("a", "map")


def test_multiple_field_lines_are_combined_with_a_comma():
    assert parse_field(["a=1", "b=2"], "dictionary") == parse_dictionary("a=1, b=2")
    # sec. 4.2 para 13: a String split across lines gains the comma and the space
    assert parse_field(['"foo', 'bar"'], "item") == Item(String("foo, bar"))
    # para 14: a Token split across lines cannot survive the comma
    with pytest.raises(ParseError):
        parse_field(["ab", "cd"], "item")


def test_nesting_is_not_possible():
    # sec. 3.1.1: an Inner List holds Items, not Inner Lists
    with pytest.raises(ParseError):
        parse_list("((a))")
    with pytest.raises(ParseError):
        parse_dictionary("a=((b))")


def test_huge_input_fails_fast():
    started = time.perf_counter()
    with pytest.raises(ParseError):
        parse_field("a," * (5 * 1024 * 1024), "list")
    assert time.perf_counter() - started < 1.0


def test_input_inside_the_limit_still_parses():
    # sec. 3.1, 3.1.2, 3.2: at least 1024 members, 256 parameters, 64-character keys
    assert len(parse_list(", ".join(["a"] * 1024))) == 1024
    assert len(parse_dictionary(", ".join(f"k{i}=1" for i in range(1024)))) == 1024
    assert len(parse_field("1" + "".join(f";p{i}" for i in range(256)), "item").params) == 256
    assert len(parse_list("(" + " ".join(["a"] * 256) + ")")[0].items) == 256


def test_members_with_no_stack_growth():
    # long flat input: no recursion in the scanners
    assert len(parse_list(", ".join(["(a b)"] * 20000))) == 20000


def test_dictionary_type():
    assert isinstance(parse_dictionary("a=1"), Dictionary)
    assert "a" in parse_dictionary("a=1")
    assert "b" not in parse_dictionary("a=1")
    with pytest.raises(KeyError):
        parse_dictionary("a=1")["b"]


@settings(max_examples=300, deadline=None)
@given(
    st.text(alphabet=st.characters(max_codepoint=0x80), max_size=60),
    st.sampled_from(["list", "dictionary", "item"]),
)
def test_parse_never_crashes_only_refuses(text, field_type):
    # any input either parses or raises ParseError: no IndexError, no ValueError from int()
    try:
        parsed = parse_field(text, field_type)
    except ParseError:
        return
    assert parsed is not None
