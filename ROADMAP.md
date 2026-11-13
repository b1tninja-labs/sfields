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
| `parse.parse_list()` | RFC 9651 sec. 4.2.1 | `[ok]` | `tests/test_parse.py::test_parse_list`, `tests/test_rfc9651_examples.py::test_rfc9651_examples_roundtrip` | M1 |
| `parse.parse_dictionary()` | RFC 9651 sec. 4.2.2 | `[ok]` | `tests/test_parse.py::test_parse_dictionary`, `tests/test_parse.py::test_dictionary_duplicate_key_keeps_first_position_last_value` | M1 |
| `item.parse_item()` | RFC 9651 sec. 4.2.3 | `[ok]` | `tests/test_item.py::test_bare_items_valid` | M1 |
| `serialize.serialize_list()` | RFC 9651 sec. 4.1.1 | `[ok]` | `tests/test_serialize.py::test_list_roundtrip_property` | M1 |
| `serialize.serialize_dictionary()` | RFC 9651 sec. 4.1.2 | `[ok]` | `tests/test_serialize.py::test_serialize_dictionary_and_list`, `tests/test_serialize.py::test_dictionary_roundtrip_property` | M1 |
| `coding.inner_parse()` | RFC 9651 sec. 4.2.1.2 | `[ok]` | `tests/test_parse.py::test_inner_parse`, `tests/test_parse.py::test_inner_list_refusals` | M3 |
| `coding.inner_serialize()` | RFC 9651 sec. 4.1.1.1 | `[ok]` | `tests/test_serialize.py::test_serialize_dictionary_and_list` | M3 |
| `keys.parse_key()` | RFC 9651 sec. 4.2.3.3 | `[ok]` | `tests/test_parse.py::test_key_charset` | M1 |
| `errors.at()` | design: every parse failure names the offset and the RFC 9651 section whose step failed | `[ok]` | `tests/test_cli.py::test_at`, `tests/test_item.py::test_errors_say_where_and_which_section` | M1 |
| `conformance.run_suite()` | design, over the working group suite (BSD-3-Clause-style licence, see docs/rfc-map.md) | `[ok]` | `tests/test_conformance.py::test_vendored_suite_passes` | M5 |
| `typed.parse_field()` | RFC 9651 sec. 4.2 (M4 entry point) | `[ok]` | `tests/test_parse.py::test_parse_field_steps`, `tests/test_parse.py::test_multiple_field_lines_are_combined_with_a_comma` | M4 |
| `typed.serialize_field()` | RFC 9651 sec. 4.1 paragraph 2 | `[ok]` | `tests/test_serialize.py::test_empty_list_and_dictionary_are_omitted` | M4 |
| `item.scan_bare_item()` | RFC 9651 sec. 4.2.3.1 | `[ok]` | `tests/test_item.py::test_unrecognised_first_character` | M1 |
| `item.scan_parameters()` | RFC 9651 sec. 4.2.3.2 | `[ok]` | `tests/test_parse.py::test_duplicate_parameter_keeps_first_position_last_value` | M1 |
| `item.scan_number()` | RFC 9651 sec. 4.2.4 | `[ok]` | `tests/test_item.py::test_integer_decimal_limits_refused`, `tests/test_item.py::test_integer_decimal_limits_accepted` | M1 |
| `item.scan_string()` | RFC 9651 sec. 4.2.5 | `[ok]` | `tests/test_item.py::test_string_refusals`, `tests/test_item.py::test_string_escapes` | M1 |
| `item.scan_token()` | RFC 9651 sec. 4.2.6 | `[ok]` | `tests/test_item.py::test_string_1024_characters_and_tokens_512` | M2 |
| `item.scan_byte_sequence()` | RFC 9651 sec. 4.2.7 | `[ok]` | `tests/test_item.py::test_byte_sequence`, `tests/test_item.py::test_byte_sequence_refusals` | M2 |
| `item.scan_boolean()` | RFC 9651 sec. 4.2.8 | `[ok]` | `tests/test_item.py::test_boolean_invalid` | M1 |
| `item.scan_date()` | RFC 9651 sec. 4.2.9 | `[ok]` | `tests/test_item.py::test_date`, `tests/test_item.py::test_date_refusals` | M2 |
| `item.scan_display_string()` | RFC 9651 sec. 4.2.10, erratum 8869 | `[ok]` | `tests/test_item.py::test_display_string_erratum_8869`, `tests/test_item.py::test_display_string_refusals` | M2 |
| `serialize.serialize_bare_item()` | RFC 9651 sec. 4.1.3.1 to 4.1.11 | `[ok]` | `tests/test_serialize.py::test_serialize_bare_items`, `tests/test_serialize.py::test_serialize_refusals` | M1 |
| `serialize.serialize_item()` | RFC 9651 sec. 4.1.3, 4.1.1.2 | `[ok]` | `tests/test_serialize.py::test_boolean_true_param_serialises_bare` | M1 |
| `serialize.serialize_parameters()` | RFC 9651 sec. 4.1.1.2, 4.1.1.3 | `[ok]` | `tests/test_serialize.py::test_key_refusals_on_serialise` | M1 |
| `model.types` | RFC 9651 sec. 3: one explicit type per item | `[ok]` | `tests/test_item.py::test_types_are_distinct` | M1 |
| `serialize.decimal-rounding` | RFC 9651 sec. 4.1.5: three places, ties to even, 12 integer digits | `[ok]` | `tests/test_serialize.py::test_decimal_serialise_rounding`, `tests/test_serialize.py::test_decimal_with_13_integer_digits_refused` | M2 |
| `limits.minimum-support` | RFC 9651 sec. 3.1, 3.1.1, 3.1.2, 3.2, 3.3.3, 3.3.4: 1024 members, 256 inner members and parameters, 64-character keys, 1024-character Strings, 512-character Tokens | `[ok]` | `tests/test_parse.py::test_input_inside_the_limit_still_parses`, `tests/test_item.py::test_string_1024_characters_and_tokens_512` | M1 |
| `limits.field-length` | implementation limit, not an RFC rule: 1 MiB per field value (`typed.MAX_FIELD_LENGTH`) | `[ok]` | `tests/test_parse.py::test_huge_input_fails_fast` | M1 |
| `limits.byte-sequence-16384` | RFC 9651 sec. 3.3.5: at least 16384 decoded octets | `[ok]` | `tests/test_item.py::test_byte_sequence_16384` | M2 |
| `parse.never-crashes` | hostile input: any text parses or raises ParseError, nothing else | `[ok]` | `tests/test_parse.py::test_parse_never_crashes_only_refuses` | M1 |
| `conformance.large-generated` | `large-generated.json` (727,664 bytes, sha256 `ade790e9...b4dbfab14d3c4`) vendored at the pinned commit; 11 cases, all pass, none skipped | `[ok]` | `tests/test_conformance.py::test_large_generated` | M5 |
| `interop.non-python` | design: interoperability evidence against a non-Python implementation (README publication checklist); `http-sf` is Python and is not that | `[ ]` | `docs/interop.md` (to be written) | M6 |
| `positioning.incumbent` | design: PORTFOLIO D15 incumbent re-check - `http-sf` 1.5.0 is live (owner decision, section 5) | `[ ]` | an owner decision, no test | M6 |

## 2. Milestones

- M1 items, lists and dictionaries with canonical round trip (done 2026-11-13)
- M2 byte sequences, dates, display strings and tokens with their edge cases, including erratum 8869 (done)
- M3 Inner Lists, parse and serialise (done)
- M4 the field_type entry point: List, Dictionary or Item (RFC 9651 sec. 4.2) (done)
- M5 conformance runner over the vendored suite, reported in CI (runner done; all 23 vendored files pass; `large-generated.json` is vendored and passes; CI runs the whole suite)
- M6 publication: 0.1.0 with the suite pass count on the landing page (blocked on the incumbent decision in section 5)

Every milestone is accepted by its rows above flipping to `[ok]` with a named test, not by
the code existing. Coverage in `pyproject.toml` ratchets in the same commit.

## 3. Errata watch

- RFC 9651 carries 1 verified erratum, 8869 (Technical), sec. 3.3: the list of item types omits Display Strings; the corrected text adds Display String (sec. 3.3.8). Read it before writing the tests, not after.
- RFC 8941 is obsolete: cite it only when explaining what changed, never as the norm.
- Read 2026-11-13: erratum 8869 is the only verified erratum on RFC 9651; none touches sec. 4.1 or 4.2. RFC 9110 has 6 verified errata, none on sec. 5.3 or 5.6.2 (the sections this project cites). RFC 4648 has 4 verified errata, all editorial (sec. 3.5 grammar, 5 article, 10 test-vector note, 16.2 link). RFC 3629 has none.
- Review claim corrected: the group-D review said unpadded base64 fails (brief 2). RFC 9651 sec. 4.2.7 paragraph 10 says parsers SHOULD NOT fail on missing padding, and `:aGVsbG8:` parses here. What is refused is padding that is partial or excessive, which the suite marks `can_fail` ("partially padded", "extra padding"); both are pinned in `tests/test_conformance.py::EXPECTED_SKIPS`.
- Review claim corrected: `@1.5` fails because sec. 4.2.9 step 4 rejects a Decimal, as the review said; it is pinned in `test_date_refusals`.

## 4. Deliberate non-goals

| Non-goal | Status | Revisit when |
|---|---|---|
| HTTP semantics, header registries or a client: values only, in and out | `[no]` | a named document requires it |
| a lenient parser for malformed headers: refuse loudly and let the caller decide | `[no]` | a named document requires it |
| the full set of registered structured fields defined by other specifications | `[no]` | a named document requires it |

## 5. Open questions

- Decided in the first pass: the working group suite is vendored (licence read raw and recorded in docs/rfc-map.md and tests/data/PROVENANCE.md); M2 and M4 now have rows of their own.
- OWNER DECISION: `http-sf` (Mark Nottingham, the RFC 9651 editor) is a live, RFC 9651 implementation: 1.5.0 released 2026-10-23, `typing_extensions` its only runtime dependency. The README sentence that the reference implementation "is gone from PyPI" was true only of the deprecated `http-sfv` (0.9.9, 2024-01-25, RFC 8941). PORTFOLIO D15 says to demote the project if the incumbent is live. This pass implemented the whole of RFC 9651 anyway because the brief asked for it and h3tunnel needs it by path; the question left is whether to publish, keep it as an internal leaf, or retire it.
- Should `Decimal` JSON output in the CLI follow the suite's bare-number shape, with exactness lost, rather than the `{"__type": "decimal"}` object it prints today?
- Should the model give `Dictionary` and `Params` a `dict`-style `__setitem__`? They are immutable ordered maps now; a builder is easy to add if a consumer wants one.

## 6. Publication checklist

- [ ] every `[ ]` row above either `[ok]` or moved to a named later milestone
- [ ] `docs/research.md` claims re-verified and the dated ones either promoted or deleted
- [ ] interoperability evidence recorded in `docs/` against a non-Python implementation
- [ ] `tools/check_dist.py` proves the wheel ships the fixtures the README promises
- [ ] version 0.1.0 tagged, trusted publisher configured, README badges uncommented
