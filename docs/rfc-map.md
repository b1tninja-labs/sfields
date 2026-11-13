# Where every claim in this repository comes from

| Document | Status | Published | Verified against the publisher record on |
|---|---|---|---|
| RFC 9651 | Proposed Standard | 2024-09 | 2026-11-05 |
| RFC 8941 | Obsolete | 2021-02 | 2026-11-05 |
| RFC 9110 | Internet Standard (STD 97) | 2022-06 | 2026-11-05 |
| RFC 4648 | Proposed Standard, current, obsoletes RFC 3548 | 2006-10 | 2026-11-13 |
| RFC 3629 (STD 63) | Internet Standard, current, no errata | 2003-11 | 2026-11-13 |

Citation rules, in the order they most often get broken:

1. Cite the document. A secondary write-up is a lead, not a source.
2. A section number is cited only if that section was read in full.
3. Errata are checked at each milestone freeze, not once at the start.
4. Where a claim came from a body outside the RFC series, that body is named here.

## What each document supplies

- RFC 9651: every algorithm (sec. 4.1 serialise, sec. 4.2 parse), the item types (sec. 3.3), the minimum limits (sec. 3), the ABNF (appendix C, non-normative) and the examples used as vectors in `tests/test_rfc9651_examples.py`. Verified erratum 8869 (sec. 3.3, Display String missing from the list of item types) is applied: sec. 4.2.3.1 step 7 dispatches `%` to Display Strings and the code follows it. RFC 8941 is obsolete (obsoleted by RFC 9651) and is not cited as a norm.
- RFC 9110 sec. 5.6.2: `tchar`, the Token alphabet. Sec. 5.2 and 5.3 (combining field lines) are cited through RFC 9651 sec. 4.2 paragraph 11. Six verified errata on RFC 9110, none on the sections used (checked 2026-11-13).
- RFC 4648 sec. 4 (base64) and sec. 8 (base16): Byte Sequences and Display String hex. Four verified errata, all editorial. Sec. 3.2 and 3.5 (padding, pad bits) are relaxed on parse by RFC 9651 sec. 4.2.7.
- RFC 3629 sec. 3: strict UTF-8 for Display Strings, which Python's `bytes.decode("utf-8")` implements (it refuses overlong forms and surrogates).

## Bodies outside the RFC series

- `httpwg/structured-field-tests`, the HTTP Working Group's conformance vectors. Vendored under `tests/data/structured-field-tests/` at commit `10781e4a59c387853c900cc06cdd8a3fd7ae4134` (2026-10-30). Its `LICENSE.md` was read raw on 2026-11-13: "Copyright (c) 2018- IETF Trust and the persons identified as authors of the code. All rights reserved." with a three-clause BSD-style grant (redistribution and use in source and binary forms, with or without modification, are permitted provided the copyright notice, conditions and disclaimer are retained and the names of the Internet Society, IETF or IETF Trust are not used to endorse). The notice is kept beside the data. `large-generated.json` (727 KB) is not vendored. The vectors are a secondary check; RFC 9651 is the norm. See `tests/data/PROVENANCE.md`.

## Incumbent check (PORTFOLIO D15), 2026-11-13

PyPI JSON API: `http-sfv` 0.9.9 (2024-01-25) is deprecated by its own README in favour of `http-sf`; `http-sf` 1.5.0 (2026-10-23) implements RFC 9651, is by the same author, and depends only on `typing_extensions`. `structured-field-values`, `structured-fields`, `sfv`, `structuredfields` and `httpsfv` are absent. The README's earlier sentence that the working group implementation is gone is therefore wrong for RFC 9651 and has been corrected. See ROADMAP section 5 for the owner decision.

Re-verify with the RFC library rather than memory: `info('RFCnnnn')` for current status, `errata('RFCnnnn')` for corrections, and `read('RFCnnnn', view='normative')` for the MUST and SHOULD statements that become obligation rows.
