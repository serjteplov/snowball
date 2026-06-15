"""Allow running the package as a module: python -m package_snowball."""

from __future__ import annotations

import sys

from package_snowball.entrypoints.cli import main

if __name__ == "__main__":
    sys.exit(main())
