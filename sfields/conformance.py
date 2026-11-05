"""the runner that replays the vendored test vectors.

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

    SuiteResult = Any  # placeholder: give it a real type in the milestone that needs it

__all__ = [
    "run_suite",
]


def run_suite(cases: Iterable) -> SuiteResult:
    """Pending behaviour defined by design.

    Not implemented yet. See the ``conformance.run_suite()`` row in ROADMAP.md; this stub
    raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("run_suite() is not implemented: design")
