"""Configuration loading from YAML and environment variables."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class ApiRatesConfig:
    base_url: str
    timeout_seconds: int = 10


@dataclass(frozen=True)
class RatesConfig:
    provider: str
    static_rates: dict[str, float] = field(default_factory=dict)
    api: ApiRatesConfig | None = None


@dataclass(frozen=True)
class AppConfig:
    """应用级配置。frozen=True 表示加载后不可变，避免运行中被意外修改。"""
    default_base: str
    supported_currencies: list[str]
    rates: RatesConfig

    def is_supported(self, currency: str) -> bool:
        return currency.upper() in {c.upper() for c in self.supported_currencies}


def load_config(config_path: Path) -> AppConfig:
    """Load and validate application config from a YAML file."""
    load_dotenv()  # 读取 .env 中的 EXCHANGE_RATE_API_KEY 等（若后续扩展需要）

    with config_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    rates_raw = raw["rates"]
    api_raw = rates_raw.get("api")
    api_config = (
        ApiRatesConfig(
            base_url=api_raw["base_url"],
            timeout_seconds=api_raw.get("timeout_seconds", 10),
        )
        if api_raw
        else None
    )

    return AppConfig(
        default_base=raw["default_base"].upper(),
        supported_currencies=[c.upper() for c in raw["supported_currencies"]],
        rates=RatesConfig(
            provider=rates_raw["provider"],
            # 统一大写，避免 usd / USD 混用导致查表失败
            static_rates={k.upper(): float(v) for k, v in rates_raw.get("static_rates", {}).items()},
            api=api_config,
        ),
    )


def default_config_path() -> Path:
    """Return the default config path relative to the tool root."""
    # __file__ = .../src/currency_converter/config.py → parents[2] = tools/currency_converter/
    return Path(__file__).resolve().parents[2] / "configs" / "default.yaml"
