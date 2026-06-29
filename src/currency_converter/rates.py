"""Exchange rate providers.

汇率源抽象层：转换逻辑（converter）不直接依赖 forex-python 或 YAML，
通过 RateProvider 接口切换 static / forex 等实现，便于测试和扩展。
"""

from abc import ABC, abstractmethod

from forex_python.converter import CurrencyRates
# forex-python 自带异常；映射为本项目的 RateNotAvailableError，CLI 层统一处理
from forex_python.converter import RatesNotAvailableError as ForexRatesNotAvailableError

from currency_converter.config import AppConfig, RatesConfig
from currency_converter.exceptions import RateNotAvailableError


class RateProvider(ABC):
    """Abstract interface for fetching exchange rates."""

    @abstractmethod
    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Return the rate to multiply *from_currency* amount to get *to_currency*.

        Example: get_rate("USD", "EUR") -> 0.92 means 100 USD * 0.92 = 92 EUR
        """
        ...


class StaticRateProvider(RateProvider):
    """Rates loaded from config static_rates table (offline / testing).

    static_rates 中每个值表示「1 单位 default_base 可兑换多少该货币」。
    例如 base=USD, EUR: 0.92 表示 1 USD = 0.92 EUR。
    """

    def __init__(self, rates_config: RatesConfig, base_currency: str) -> None:
        self._rates = rates_config.static_rates
        self._base = base_currency.upper()  # 预留：校验 static_rates 是否以 base 为锚

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        src = from_currency.upper()
        dst = to_currency.upper()
        if src == dst:
            return 1.0

        if src not in self._rates or dst not in self._rates:
            raise RateNotAvailableError(src, dst, "currency not in static_rates")

        # 交叉汇率：先换成 base，再换成目标货币
        # rate(A→B) = rates[B] / rates[A]
        # 例：USD→EUR = 0.92/1.0 = 0.92；CNY→EUR = 0.92/7.24
        return self._rates[dst] / self._rates[src]


class ForexPythonRateProvider(RateProvider):
    """Real-time rates via forex-python (CurrencyRates)."""

    def __init__(self, client: CurrencyRates | None = None) -> None:
        # 允许注入 client，单元测试时可 mock，避免真实网络请求
        self._client = client or CurrencyRates()

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        src = from_currency.upper()
        dst = to_currency.upper()
        if src == dst:
            return 1.0

        try:
            return float(self._client.get_rate(src, dst))
        except ForexRatesNotAvailableError as exc:
            raise RateNotAvailableError(src, dst, str(exc)) from exc


class ApiRateProvider(RateProvider):
    """Legacy alias — delegates to ForexPythonRateProvider.

    保留此类是为了兼容 configs 里 provider: api 的旧写法；
    实际汇率获取已统一走 forex-python，不再手写 HTTP 请求。
    """

    def __init__(self, rates_config: RatesConfig) -> None:
        if rates_config.api is None:
            raise RateNotAvailableError("", "", "API config is missing")
        self._provider = ForexPythonRateProvider()

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        return self._provider.get_rate(from_currency, to_currency)


def create_rate_provider(config: AppConfig) -> RateProvider:
    """Factory: create the rate provider specified in config."""
    provider = config.rates.provider.lower()
    # 工厂模式：根据 YAML 中 rates.provider 选择实现，调用方无需 if/else
    if provider == "static":
        return StaticRateProvider(config.rates, config.default_base)
    if provider == "forex":
        return ForexPythonRateProvider()
    if provider == "api":
        return ApiRateProvider(config.rates)
    raise ValueError(f"Unknown rates provider: {config.rates.provider}")
