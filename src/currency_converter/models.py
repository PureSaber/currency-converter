"""Data models for conversion input and output."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConversionRequest:
    """Input for a single currency conversion."""

    amount: float
    from_currency: str
    to_currency: str

    def __post_init__(self) -> None:
        # frozen dataclass 字段默认不可赋值，需用 object.__setattr__ 在初始化时规范化
        object.__setattr__(self, "from_currency", self.from_currency.upper())
        object.__setattr__(self, "to_currency", self.to_currency.upper())


@dataclass(frozen=True)
class ConversionResult:
    """Output of a successful conversion."""

    request: ConversionRequest
    converted_amount: float
    rate: float
    timestamp: datetime

    @property
    def from_currency(self) -> str:
        return self.request.from_currency

    @property
    def to_currency(self) -> str:
        return self.request.to_currency

    @property
    def original_amount(self) -> float:
        # 便捷属性，CLI 打印时不必写 result.request.amount
        return self.request.amount
