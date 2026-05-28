"""Shared pytest fixtures and path setup."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Make ``cfr`` importable regardless of the pytest invocation cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def deterministic_numpy():
    """Reset the legacy global numpy RNG before every test.

    Newer code uses ``np.random.default_rng(seed)`` for determinism; this
    fixture only affects any incidental use of the legacy ``np.random.*``
    helpers, keeping test runs reproducible end-to-end.
    """
    np.random.seed(0)
