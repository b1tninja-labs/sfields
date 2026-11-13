"""Command line entry point for sfields.

``python -m sfields parse VALUE --type dictionary`` parses a field value and prints its
canonical serialisation, or with ``--json`` the structure in the working group test suite's
JSON shape (Decimals appear as ``{"__type": "decimal", "value": "1.5"}`` because JSON
numbers cannot carry them exactly). Exit status is 0 on success, 1 when the value does not
parse and 2 for a usage error.
"""

from __future__ import annotations

import argparse
import decimal
import json
import sys
from typing import Any

from .conformance import to_json
from .errors import ParseError, SerializeError
from .typed import parse_field, serialize_field

USAGE = """\
Examples:
  python -m sfields parse 'a=1, b;tok=x' --type dictionary --json
  python -m sfields parse '"hello"' --type item"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sfields",
        description="Structured Field Values for HTTP: parser and serializer for lists, inner lists, dictionaries and parameters, with an explicit type for every item",
        epilog=USAGE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command")
    parse = commands.add_parser("parse", help="parse a field value (RFC 9651 sec. 4.2)")
    parse.add_argument("value", help="the field value, ASCII")
    parse.add_argument(
        "--type",
        dest="field_type",
        choices=("list", "dictionary", "item"),
        default="item",
        help="the field's top-level type (default: item)",
    )
    parse.add_argument("--json", action="store_true", help="print the suite's JSON shape")
    return parser


def _plain(value: Any) -> Any:
    if isinstance(value, decimal.Decimal):
        return {"__type": "decimal", "value": f"{value:f}"}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value


def main(argv: list[str] | None = None) -> int:
    """Run the command line; returns the exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "parse":
        parser.print_usage(sys.stderr)
        return 2
    try:
        parsed = parse_field(args.value, args.field_type)
        text = serialize_field(parsed)
    except (ParseError, SerializeError) as error:
        print(f"sfields: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(_plain(to_json(parsed)), ensure_ascii=False))
    else:
        print("" if text is None else text)
    return 0
