# Provenance of the vendored test vectors

- Source: https://github.com/httpwg/structured-field-tests (the HTTP Working Group's Structured Field test suite).
- Commit: `10781e4a59c387853c900cc06cdd8a3fd7ae4134`, committed 2026-10-30T04:52:07Z.
- Fetched: 2026-11-13, each file from `raw.githubusercontent.com` at that commit.
- Licence: `structured-field-tests/LICENSE.md`, read raw before vendoring: copyright IETF Trust and the persons identified as
  authors of the code, a three-clause BSD-style grant. Redistribution requires keeping that notice, which is kept in
  `structured-field-tests/LICENSE.md`. `NOTICE` at the repository root names the suite.
- Files: every `*.json` in the repository root, `large-generated.json` included (727,664 bytes, sha256 `ade790e9425083bb8e8f5082a6c0b7565877feefdd59d37ed76b4dbfab14d3c4`, fetched 2026-11-13 from the same commit), every file in `serialisation-tests/`, and the
  suite's `README.md` (the format description) and `LICENSE.md`. Not vendored: `generate.py`, `schema/`, `.github/`.
- Status: a secondary check. RFC 9651 is the norm; a vector that disagrees with the RFC text is reported upstream and
  not obeyed. Never fetch at test time; to refresh, change the commit here and re-run the suite.
- Skipped on purpose: the two `can_fail` base64 padding cases named in `tests/test_conformance.py::EXPECTED_SKIPS`.
