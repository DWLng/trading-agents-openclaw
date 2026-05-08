# 数据目录

本目录用于存储本地 K 线数据。

## 目录结构

```
data/
├── README.md                   # 本文件
├── stock_list.parquet          # 股票列表（需运行脚本生成，5201只A股）
└── daily_kline/                # 日K线数据（由 bulk_download.py 下载）
    ├── sh.600000.parquet
    ├── sh.600519.parquet
    └── ...
```

## 初始化股票列表

运行以下命令生成完整的股票列表：

```python
import baostock as bs
import pandas as pd

bs.login()
rs = bs.query_stock_basic()
data = []
while rs.next():
    data.append(rs.get_row_data())
df = pd.DataFrame(data, columns=rs.fields)
a_shares = df[(df["type"] == "1") & (df["status"] == "1")][["code", "code_name", "ipoDate", "outDate", "type", "status"]]
a_shares.to_parquet("stock_list.parquet", index=False)
bs.logout()
print(f"已保存 {len(a_shares)} 只A股")
```

或使用本项目的脚本：

```bash
python3 scripts/bulk_download.py --stock-list-only
```

## 数据来源

- **baostock**：免费开源 A 股数据源，无需 API Key
- 5201 只 A 股（含主板、创业板、科创板、北交所）
