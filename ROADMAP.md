# Specification completeness -- and the roadmap it implies

This is the project's north star: every protocol obligation sfields could plausibly take on,
with an honest status against the code at `HEAD`. It is blunt about gaps on purpose. A
roadmap that overstates its coverage is not a plan, it is marketing.

**The honesty rule:** a row may read `[ok]` only when a named test would fail if the
behaviour regressed. Reading the code and agreeing with it is not enough. That is how
"decoded but never sent" quietly becomes "implemented".

Legend: `[ok]` implemented and pinned by a named test -- `[part]` partial, with what is
missing stated -- `[ ]` not implemented -- `[no]` deliberate non-goal.

Update the affected row in the same commit that changes the behaviour. A row and its test
drift apart within one release, and the document becomes useless exactly when it is needed.

## 1. Obligations

| Obligation | Spec | Status | Where |
|---|---|---|---|
| `parse.parse_list()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::parse_list` |
| `parse.parse_dictionary()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::parse_dictionary` |
| `item.parse_item()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::parse_item` |
| `serialize.serialize_list()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::serialize_list` |
| `serialize.serialize_dictionary()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::serialize_dictionary` |
| `coding.inner_parse()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::inner_parse` |
| `coding.inner_serialize()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::inner_serialize` |
| `keys.parse_key()` | RFC 9651 | `[ ]` | `tests/test_obligations.py::parse_key` |
| `errors.at()` | design | `[ ]` | `tests/test_obligations.py::at` |
| `conformance.run_suite()` | design | `[ ]` | `tests/test_obligations.py::run_suite` |

## 2. Milestones

- M1 items, lists and dictionaries with canonical round trip
- M2 byte sequences, dates and tokens with their edge cases
- M3 inner and outer coding
- M4 keyed and typed fields
- M5 conformance runner over the vendored suite, reported in CI
- M6 publication: 0.1.0 with the suite pass count on the landing page

Every milestone is accepted by its rows above flipping to `[ok]` with a named test, not by
the code existing. Coverage in `pyproject.toml` ratchets in the same commit.

## 3. Errata watch

- RFC 9651 carries 1 verified erratum. Read it before writing the tests, not after.
- RFC 8941 is obsolete: cite it only when explaining what changed, never as the norm.

## 4. Deliberate non-goals

| Non-goal | Status | Revisit when |
|---|---|---|
| HTTP semantics, header registries or a client: values only, in and out | `[no]` | a named document requires it |
| a lenient parser for malformed headers: refuse loudly and let the caller decide | `[no]` | a named document requires it |
| the full set of registered structured fields defined by other specifications | `[no]` | a named document requires it |

## 5. Open questions

- vendor the working group test suite as data, and record its provenance

## 6. Publication checklist

- [ ] every `[ ]` row above either `[ok]` or moved to a named later milestone
- [ ] `docs/research.md` claims re-verified and the dated ones either promoted or deleted
- [ ] interoperability evidence recorded in `docs/` against a non-Python implementation
- [ ] `tools/check_dist.py` proves the wheel ships the fixtures the README promises
- [ ] version 0.1.0 tagged, trusted publisher configured, README badges uncommented
