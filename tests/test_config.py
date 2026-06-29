"""Tests for configuration loading."""

from currency_converter.config import AppConfig, default_config_path, load_config


def test_load_default_config(default_config: AppConfig) -> None:
    assert default_config.default_base == "USD"
    assert "EUR" in default_config.supported_currencies
    assert default_config.rates.provider == "forex"
    assert default_config.rates.static_rates["USD"] == 1.0


def test_is_supported(default_config: AppConfig) -> None:
    assert default_config.is_supported("usd")
    assert not default_config.is_supported("XXX")


def test_default_config_path_exists() -> None:
    assert default_config_path().exists()
