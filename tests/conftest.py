# from __future__ import annotations
#
# import sys
# from pathlib import Path
#
# ROOT = Path(__file__).resolve().parents[1]
# SRC = ROOT / "src"
# sys.path.insert(0, str(SRC))
# conftest.py
import pytest


def pytest_collection_modifyitems(config, items):
    if config.getoption("-m") == "bulk":
        # If user explicitly asked for bulk, do nothing and let them run
        return

    skip_bulk = pytest.mark.skip(reason="need -m bulk option to run")
    for item in items:
        if "bulk" in item.keywords:
            item.add_marker(skip_bulk)