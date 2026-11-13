# Changelog

The format follows Keep a Changelog, and this project adheres to Semantic Versioning.

## Unreleased

### Added

- RFC 9651 parsing and serialisation: `parse_field`, `parse_item`, `parse_list`, `parse_dictionary`,
  `inner_parse`, `parse_key`, `serialize_field`, `serialize_item`, `serialize_list`,
  `serialize_dictionary`, `inner_serialize`, with the `model` types and positional `ParseError`.
- `conformance.run_suite` and the vendored HTTP Working Group `structured-field-tests`
  (commit `10781e4`, BSD-style licence kept beside the data).
- `python -m sfields parse VALUE --type {list,dictionary,item} [--json]`.
- Hypothesis round-trip and never-crashes properties; RFC 9651's own examples as vectors.

## 0.0.0 - 2026-11-05

### Added

- Package skeleton, obligation matrix and CI gates for sfields.
- `sfields.apps` namespace reserved for composition that is not protocol behaviour.
