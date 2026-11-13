"""Allow python -m sfields without installing the console script."""

from __future__ import annotations

import sys

from .cli import main

sys.exit(main())
