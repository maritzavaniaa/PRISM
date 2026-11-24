"""Titik masuk: PYTHONPATH=src python -m prism scan <path>."""

import sys

from prism.cli import main

if __name__ == "__main__":
    sys.exit(main())
