"""Command-line interface for the currency converter."""

import argparse
import sys
from pathlib import Path

from currency_converter.config import default_config_path, load_config
from currency_converter.converter import CurrencyConverter
from currency_converter.exceptions import CurrencyConverterError
from currency_converter.models import ConversionRequest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="currency_converter",
        description="Convert an amount from one currency to another.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="Path to YAML config file",
    )
    parser.add_argument("--list-currencies", action="store_true", help="List supported currencies")
    parser.add_argument("--amount", type=float, help="Amount to convert")
    # from 是 Python 关键字，argparse 用 dest 映射到 from_currency
    parser.add_argument("--from", dest="from_currency", metavar="CUR", help="Source currency code")
    parser.add_argument("--to", dest="to_currency", metavar="CUR", help="Target currency code")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)
    converter = CurrencyConverter(config)

    if args.list_currencies:
        print("Supported currencies:")
        for code in converter.supported_currencies:
            print(f"  {code}")
        return

    missing = [
        name
        for name, value in [("amount", args.amount), ("from", args.from_currency), ("to", args.to_currency)]
        if value is None
    ]
    if missing:
        parser.error(f"the following arguments are required: {', '.join('--' + m for m in missing)}")

    request = ConversionRequest(
        amount=args.amount,
        from_currency=args.from_currency,
        to_currency=args.to_currency,
    )

    try:
        result = converter.convert(request)
    except CurrencyConverterError as exc:
        # 统一捕获业务异常，向用户输出可读错误信息
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"{result.original_amount:.2f} {result.from_currency} "
        f"= {result.converted_amount:.2f} {result.to_currency} "
        f"(rate: {result.rate:.6f})"
    )


if __name__ == "__main__":
    main()
