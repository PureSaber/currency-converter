# Currency Converter

将一种货币的金额转换为另一种货币（例如 100 USD → EUR）。一个量化研究过程中的辅助工具项目。

采用 **配置与代码分离**、**汇率源可插拔** 结构：支持 `forex-python` 实时汇率与本地静态汇率表。

## 目录结构

```
currency-converter/
├── configs/default.yaml
├── src/currency_converter/
│   ├── cli.py              # 命令行入口
│   ├── config.py           # 配置加载
│   ├── converter.py        # 核心转换逻辑
│   ├── rates.py            # 汇率源（forex / static）
│   ├── models.py
│   └── exceptions.py
└── tests/
```

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -e ".[dev]"

python -m currency_converter --amount 100 --from USD --to EUR
python -m currency_converter --list-currencies
pytest -q
```

## 配置

`configs/default.yaml` 中 `rates.provider`：

| 值 | 说明 |
|----|------|
| `forex` | 实时汇率（默认，需联网） |
| `static` | 本地静态汇率表（离线测试） |
| `api` | 兼容别名，实际走 forex-python |

## 相关仓库

本仓库为独立项目，与其他量化研究仓库并列维护。学习路线图见 [quant-research-notes](../quant-research-notes)（本地工作区）或你的 GitHub `quant-research-notes` 仓库。
