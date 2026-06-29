"""Shared fixtures for currency_converter tests."""

from pathlib import Path

import pytest

from currency_converter.config import load_config


@pytest.fixture
def tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def default_config(tool_root: Path):
    return load_config(tool_root / "configs" / "default.yaml")
