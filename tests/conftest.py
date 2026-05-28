"""Shared pytest fixtures."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def deterministic_numpy():
    np.random.seed(0)
