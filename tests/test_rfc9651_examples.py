"""RFC 9651's own examples are the vectors.

Every example field value in sections 3.1 to 3.3.8 is parsed as the type the section
describes and serialised again. Where the RFC prints a value whose spacing is not
canonical (``("foo"; a=1;b=2)``) the expected text is the output of the serialisation
algorithm of sec. 4.1, which is what the sec. 4.2 parse followed by sec. 4.1 serialisation
must give. Sources are quoted with their section so a reader can find each one with
``rfclib.read('RFC9651§<section>')``.
"""

from __future__ import annotations

import pytest

from sfields import parse_field, serialize_field

# (section, field_type, lines as received, canonical serialisation)
EXAMPLES = [
    ("3.1", "list", ["sugar, tea, rum"], "sugar, tea, rum"),
    ("3.1", "list", ["sugar, tea", "rum"], "sugar, tea, rum"),
    (
        "3.1.1",
        "list",
        ['("foo" "bar"), ("baz"), ("bat" "one"), ()'],
        '("foo" "bar"), ("baz"), ("bat" "one"), ()',
    ),
    (
        "3.1.1",
        "list",
        ['("foo"; a=1;b=2);lvl=5, ("bar" "baz");lvl=1'],
        '("foo";a=1;b=2);lvl=5, ("bar" "baz");lvl=1',
    ),
    (
        "3.1.2",
        "list",
        ['abc;a=1;b=2; cde_456, (ghi;jk=4 l);q="9";r=w'],
        'abc;a=1;b=2;cde_456, (ghi;jk=4 l);q="9";r=w',
    ),
    ("3.1.2", "item", ["1; a; b=?0"], "1;a;b=?0"),
    (
        "3.2",
        "dictionary",
        ['en="Applepie", da=:w4ZibGV0w6ZydGU=:'],
        'en="Applepie", da=:w4ZibGV0w6ZydGU=:',
    ),
    ("3.2", "dictionary", ["a=?0, b, c; foo=bar"], "a=?0, b, c;foo=bar"),
    (
        "3.2",
        "dictionary",
        ["rating=1.5, feelings=(joy sadness)"],
        "rating=1.5, feelings=(joy sadness)",
    ),
    (
        "3.2",
        "dictionary",
        ["a=(1 2), b=3, c=4;aa=bb, d=(5 6);valid"],
        "a=(1 2), b=3, c=4;aa=bb, d=(5 6);valid",
    ),
    ("3.2", "dictionary", ["foo=1, bar=2"], "foo=1, bar=2"),
    ("3.2", "dictionary", ["foo=1", "bar=2"], "foo=1, bar=2"),
    ("3.3", "item", ["5"], "5"),
    ("3.3", "item", ["5; foo=bar"], "5;foo=bar"),
    ("3.3.1", "item", ["42"], "42"),
    ("3.3.2", "item", ["4.5"], "4.5"),
    ("3.3.3", "item", ['"hello world"'], '"hello world"'),
    ("3.3.4", "item", ["foo123/456"], "foo123/456"),
    (
        "3.3.5",
        "item",
        [":cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==:"],
        ":cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==:",
    ),
    ("3.3.6", "item", ["?1"], "?1"),
    ("3.3.7", "item", ["@1659578233"], "@1659578233"),
    (
        "3.3.8",
        "item",
        ['%"This is intended for display to %c3%bcsers."'],
        '%"This is intended for display to %c3%bcsers."',
    ),
]


@pytest.mark.parametrize(
    ("section", "field_type", "lines", "canonical"),
    EXAMPLES,
    ids=[f"{e[0]}-{i}" for i, e in enumerate(EXAMPLES)],
)
def test_rfc9651_examples_roundtrip(section, field_type, lines, canonical):
    parsed = parse_field(lines, field_type)
    assert serialize_field(parsed) == canonical
    # and the canonical text is a fixed point of parse then serialise
    assert serialize_field(parse_field(canonical, field_type)) == canonical


def test_rfc9651_example_values_have_the_documented_types():
    from sfields.model import ByteSequence, Date, Decimal, DisplayString, Token

    assert parse_field("@1659578233", "item").value == Date(1659578233)
    assert parse_field("4.5", "item").value.__class__ is Decimal
    assert parse_field("foo123/456", "item").value == Token("foo123/456")
    assert parse_field(":cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==:", "item").value == (
        ByteSequence(b"pretend this is binary content.")
    )
    assert parse_field('%"This is intended for display to %c3%bcsers."', "item").value == (
        DisplayString("This is intended for display to üsers.")
    )
