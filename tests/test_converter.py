"""Tests for conversion logic."""

from unittest.mock import MagicMock

import pytest

from currency_converter.config import load_config
from currency_converter.converter import CurrencyConverter
from currency_converter.exceptions import CurrencyNotSupportedError, InvalidAmountError
from currency_converter.models import ConversionRequest
from currency_converter.rates import StaticRateProvider


@pytest.fixture
def static_config(tool_root):
    config = load_config(tool_root / "configs" / "default.yaml")
    # 默认配置是 provider: forex（需联网）；测试强制改为 static，保证离线可重复运行
    from dataclasses import replace

    return replace(
        config,
        rates=replace(config.rates, provider="static"),
    )


def test_validate_rejects_negative_amount(static_config) -> None:
    converter = CurrencyConverter(static_config)
    request = ConversionRequest(amount=-1.0, from_currency="USD", to_currency="EUR")
    with pytest.raises(InvalidAmountError):
        converter.convert(request)


def test_validate_rejects_unsupported_currency(static_config) -> None:
    converter = CurrencyConverter(static_config)
    request = ConversionRequest(amount=100.0, from_currency="USD", to_currency="XXX")
    with pytest.raises(CurrencyNotSupportedError):
        converter.convert(request)


def test_convert_usd_to_eur_with_mock(static_config) -> None:
    # 注入 mock 的 RateProvider，只测 convert 逻辑，不依赖 forex-python 网络
    mock_provider = MagicMock()
    mock_provider.get_rate.return_value = 0.92

    converter = CurrencyConverter(static_config, rate_provider=mock_provider)
    result = converter.convert(ConversionRequest(100.0, "USD", "EUR"))

    assert result.from_currency == "USD"
    assert result.to_currency == "EUR"
    assert result.converted_amount == pytest.approx(92.0)
    assert result.rate == pytest.approx(0.92)
    mock_provider.get_rate.assert_called_once_with("USD", "EUR")


def test_static_rate_provider_cross_rate(static_config) -> None:
    provider = StaticRateProvider(static_config.rates, static_config.default_base)
    rate = provider.get_rate("USD", "EUR")
    assert rate == pytest.approx(0.92)


def test_static_rate_provider_same_currency(static_config) -> None:
    provider = StaticRateProvider(static_config.rates, static_config.default_base)
    assert provider.get_rate("USD", "USD") == 1.0


def test_convert_with_static_provider(static_config) -> None:
    converter = CurrencyConverter(static_config)
    result = converter.convert(ConversionRequest(100.0, "USD", "EUR"))
    assert result.converted_amount == pytest.approx(92.0)
