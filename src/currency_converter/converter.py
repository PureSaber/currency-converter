"""Core currency conversion logic."""

from datetime import datetime, timezone

from currency_converter.config import AppConfig
from currency_converter.exceptions import CurrencyNotSupportedError, InvalidAmountError
from currency_converter.models import ConversionRequest, ConversionResult
from currency_converter.rates import RateProvider, create_rate_provider


class CurrencyConverter:
    """Convert amounts between currencies using a pluggable rate provider."""

    def __init__(self, config: AppConfig, rate_provider: RateProvider | None = None) -> None:
        self._config = config
        # rate_provider 可注入 mock，测试时不必联网
        self._rate_provider = rate_provider or create_rate_provider(config)

    @property
    def supported_currencies(self) -> list[str]:
        return list(self._config.supported_currencies)

    def convert(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert *request.amount* from *request.from_currency* to *request.to_currency*.

        Raises:
            InvalidAmountError: amount is negative
            CurrencyNotSupportedError: currency not in supported list
            RateNotAvailableError: rate cannot be obtained
        """
        self._validate_request(request)

        rate = self._rate_provider.get_rate(request.from_currency, request.to_currency)
        converted = request.amount * rate

        return ConversionResult(
            request=request,
            converted_amount=converted,
            rate=rate,
            timestamp=datetime.now(timezone.utc),  # UTC 便于跨时区对比和日志
        )

    def _validate_request(self, request: ConversionRequest) -> None:
        if request.amount < 0:
            raise InvalidAmountError(request.amount)
        # 只校验配置里声明的 supported_currencies，与 forex-python 支持的全量币种解耦
        for currency in (request.from_currency, request.to_currency):
            if not self._config.is_supported(currency):
                raise CurrencyNotSupportedError(currency, self._config.supported_currencies)
