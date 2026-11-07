# Specification completeness -- and the roadmap it implies

This is the project's north star: every protocol obligation sfields could plausibly take on,
with an honest status against the code at `HEAD`. It is blunt about gaps on purpose. A
roadmap that overstates its coverage is not a plan, it is marketing.

**The honesty rule:** a row may read `[ok]` only when a named test would fail if the
behaviour regressed. Reading the code and agreeing with it is not enough. That is how
"decoded but never sent" quietly becomes "implemented".

Legend: `[ok]` implemented and pinned by a named test -- `[part]` partial, with what is
missing stated -- `[ ]` not implemented -- `[no]` deliberate non-goal.

A Where cell marked `(to be written)` names the test that will pin the row once it exists; no
such test has been written yet, and the row cannot leave `[ ]` until it has. The Milestone
column places the row on the ladder in section 2, and `-` means it is not placed yet.

Update the affected row in the same commit that changes the behaviour. A row and its test
drift apart within one release, and the document becomes useless exactly when it is needed.

## 1. Obligations

| Obligation | Spec | Status | Where | Milestone |
|---|---|---|---|---|
| `parse.parse_list()` | RFC 9651 sec. 4.2.1 | `[ ]` | `tests/test_obligations.py::test_parse_list` (to be written) | M1 |
| `parse.parse_dictionary()` | RFC 9651 sec. 4.2.2 | `[ ]` | `tests/test_obligations.py::test_parse_dictionary` (to be written) | M1 |
| `item.parse_item()` | RFC 9651 sec. 4.2.3 | `[ ]` | `tests/test_obligations.py::test_parse_item` (to be written) | M1 |
| `serialize.serialize_list()` | RFC 9651 sec. 4.1.1 | `[ ]` | `tests/test_obligations.py::test_serialize_list` (to be written) | M1 |
| `serialize.serialize_dictionary()` | RFC 9651 sec. 4.1.2 | `[ ]` | `tests/test_obligations.py::test_serialize_dictionary` (to be written) | M1 |
| `coding.inner_parse()` | RFC 9651 sec. 4.2.1.2 | `[ ]` | `tests/test_obligations.py::test_inner_parse` (to be written) | M3 |
| `coding.inner_serialize()` | RFC 9651 sec. 4.1.1.1 | `[ ]` | `tests/test_obligations.py::test_inner_serialize` (to be written) | M3 |
| `keys.parse_key()` | RFC 9651 sec. 4.2.3.3 | `[ ]` | `tests/test_obligations.py::test_parse_key` (to be written) | M1 |
| `errors.at()` | design | `[ ]` | `tests/test_obligations.py::test_at` (to be written) | M1 |
| `conformance.run_suite()` | design | `[ ]` | `tests/test_obligations.py::test_run_suite` (to be written) | M5 |

## 2. Milestones

- M1 items, lists and dictionaries with canonical round trip
- M2 byte sequences, dates, display strings and tokens with their edge cases, including erratum 8869
- M3 Inner Lists, parse and serialise
- M4 the field_type entry point: List, Dictionary or Item (RFC 9651 sec. 4.2)
- M5 conformance runner over the vendored suite, reported in CI
- M6 publication: 0.1.0 with the suite pass count on the landing page

Every milestone is accepted by its rows above flipping to `[ok]` with a named test, not by
the code existing. Coverage in `pyproject.toml` ratchets in the same commit.

## 3. Errata watch

- RFC 9651 carries 1 verified erratum, 8869 (Technical), sec. 3.3: the list of item types omits Display Strings; the corrected text adds Display String (sec. 3.3.8). Read it before writing the tests, not after.
- RFC 8941 is obsolete: cite it only when explaining what changed, never as the norm.

## 4. Deliberate non-goals

| Non-goal | Status | Revisit when |
|---|---|---|
| HTTP semantics, header registries or a client: values only, in and out | `[no]` | a named document requires it |
| a lenient parser for malformed headers: refuse loudly and let the caller decide | `[no]` | a named document requires it |
| the full set of registered structured fields defined by other specifications | `[no]` | a named document requires it |

## 5. Open questions

- vendor the working group test suite as data, and record its provenance
- M2 (display strings, dates, byte sequences, tokens) and M4 (the RFC 9651 sec. 4.2 field_type entry point) have no api rows of their own: add rows, or fold them into M1

## 6. Publication checklist

- [ ] every `[ ]` row above either `[ok]` or moved to a named later milestone
- [ ] `docs/research.md` claims re-verified and the dated ones either promoted or deleted
- [ ] interoperability evidence recorded in `docs/` against a non-Python implementation
- [ ] `tools/check_dist.py` proves the wheel ships the fixtures the README promises
- [ ] version 0.1.0 tagged, trusted publisher configured, README badges uncommented
