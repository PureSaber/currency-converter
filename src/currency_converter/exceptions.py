"""Custom exceptions for the currency converter."""


class CurrencyConverterError(Exception):
    """Base exception for all converter errors."""


class CurrencyNotSupportedError(CurrencyConverterError):
    """Raised when a currency code is not in the supported list.

    注意：这是配置白名单校验，与 forex-python 能否识别该币种无关。
    """

    def __init__(self, currency: str, supported: list[str]) -> None:
        self.currency = currency
        self.supported = supported
        super().__init__(f"Unsupported currency: {currency}. Supported: {', '.join(supported)}")


class InvalidAmountError(CurrencyConverterError):
    """Raised when the amount is negative or otherwise invalid."""

    def __init__(self, amount: float) -> None:
        self.amount = amount
        super().__init__(f"Invalid amount: {amount}. Amount must be non-negative.")


class RateNotAvailableError(CurrencyConverterError):
    """Raised when an exchange rate cannot be fetched or computed."""

    def __init__(self, from_currency: str, to_currency: str, reason: str = "") -> None:
        self.from_currency = from_currency
        self.to_currency = to_currency
        msg = f"Rate unavailable: {from_currency} -> {to_currency}"
        if reason:
            msg = f"{msg} ({reason})"
        super().__init__(msg)
