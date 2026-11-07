# sfields

<!-- PyPI badges go live with the first release. Until then a version badge renders
     "no version" on the landing page, which reads as a defect rather than a date, so
     the badges stay commented out until the tag exists.
-->

**Pre-alpha shell.** The package surface, the obligation matrix and the CI gates exist.
No protocol behaviour is implemented: every public function raises `NotImplementedError`,
and the test suite records that rather than hiding it. Read
[ROADMAP.md](ROADMAP.md) before depending on any of it.

sfields -- structured field values, current specification

The HTTP Specification maintenance and transport area published RFC 9651 in September 2024, which obsoletes RFC 8941 and adds two item types, Dates and Display Strings (RFC 9651 Appendix D). The reference Python implementation the working group maintained is gone from PyPI, checked on 2026-11-05, and the name structured-fields could not safely reuse it anyway because a delisted name stays reserved. New HTTP fields are specified in this notation constantly, so a Python project either hand-rolls a parser for each one or vendors a stale copy of the deprecated code. This is the small library that ends that.

## The gap, with a date

PyPI was queried on 2026-11-05 for this name and for every neighbouring project. Landscape
claims rot quickly: two projects in this portfolio shipped within five days of the survey,
which is why the table below carries dates instead of adjectives.

| Project | Version | Last release | Why it is not this project |
|---|---|---|---|
| structured-field-values | - | - | the working group implementation, deprecated and no longer installable |
| structured-fields | - | - | absent from PyPI (2026-11-05) |
| structured | 0.1 | 2016-01-14 | an unrelated query language for data structures |

What this project intends to add:

- implement RFC 9651 rather than RFC 8941, including the additions the older text lacks
- Inner Lists and parameters on both the parse and the serialise path (RFC 9651 sec. 3.1.1, sec. 3.1.2)
- Dates and Display Strings, the two types RFC 8941 lacks, with round trip guarantees
- strict error reporting that names the byte position, because header bugs are silent bugs
- a conformance runner over the working group test suite, vendored as data with its provenance recorded

## Specification spine

Status and publication dates below were read from the RFC Editor record on 2026-11-05. A
section number is cited only where that section was read in full; everything else cites the
document, which is the honest grain size for a plan. See [docs/rfc-map.md](docs/rfc-map.md).

| Document | Status | Published | What it gives this project |
|---|---|---|---|
| RFC 9651 | Proposed Standard | 2024-09 | the current syntax, plus the Date and Display String types |
| RFC 8941 | Obsolete | 2021-02 | what most existing notes and libraries still describe |
| RFC 9110 | Internet Standard (STD 97) | 2022-06 | the field and trailer model this notation describes values for |

### Errata watch

- RFC 9651 carries 1 verified erratum, 8869 (Technical), sec. 3.3: the list of item types omits Display Strings; the corrected text adds Display String (sec. 3.3.8). Read it before writing the tests, not after.
- RFC 8941 is obsolete: cite it only when explaining what changed, never as the norm.

## Module layout

| Module | Responsibility |
|---|---|
| `parse` | list and dictionary parsing with member and parameter structure (RFC 9651) |
| `item` | the item types: integers, decimals, strings, tokens, byte sequences, booleans, dates, display strings |
| `serialize` | canonical serialisation with byte-exact round trip (RFC 9651) |
| `coding` | Inner Lists: parse and serialise (RFC 9651 sec. 3.1.1) |
| `typed` | the field_type entry point: a field value parsed as a List, Dictionary or Item (RFC 9651 sec. 4.2) |
| `keys` | dictionary and parameter keys (RFC 9651 sec. 4.1.1.3, sec. 4.2.3.3) |
| `errors` | positional parse errors rather than a bare ValueError |
| `conformance` | the runner that replays the vendored test vectors |

## What it does not do

- HTTP semantics, header registries or a client: values only, in and out
- a lenient parser for malformed headers: refuse loudly and let the caller decide
- the full set of registered structured fields defined by other specifications


## Install

```bash
git clone https://github.com/b1tninja/sfields.git
cd sfields
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
```

Not published to PyPI yet. The name is reserved for this repository's trusted publisher at
the moment of the first release.

## Development

All four gates must pass, on Linux and Windows alike:

```bash
ruff check . && ruff format --check .
mypy sfields
pytest -q --cov
python -O -m pytest -q
```

The last line is the one that matters most in a protocol library. `-O` strips `assert`, and a
parser whose bounds checks were asserts stops being a parser under production flags. Wire
paths raise named exceptions; asserts belong in tests and nowhere else.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
