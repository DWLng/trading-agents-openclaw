#!/usr/bin/env python3
"""
本地A股数据查询工具
用法:
  python3 query_local.py kline 000001 [--days 30]
  python3 query_local.py info 000001
  python3 query_local.py search 贵州茅台
  python3 query_local.py top [--by pctChg] [--limit 10]
  python3 query_local.py latest [--codes 000001,600519]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

DATA_DIR = Path.home() / ".openclaw/agents/trading/data"
KLINE_DIR = DATA_DIR / "daily_kline"
META_FILE = DATA_DIR / "stock_list.parquet"


def get_stock_list():
    if not META_FILE.exists():
        print("股票列表不存在，请先运行 bulk_download.py")
        sys.exit(1)
    return pd.read_parquet(META_FILE)


def load_kline(code, days=None):
    """加载单只股票K线数据"""
    # 尝试不同格式
    for fmt in [f"{code}.parquet", f"sh_{code}.parquet", f"sz_{code}.parquet",
                f"sh_{code.zfill(6)}.parquet", f"sz_{code.zfill(6)}.parquet"]:
        fpath = KLINE_DIR / fmt
        if fpath.exists():
            df = pd.read_parquet(fpath)
            if days:
                df = df.tail(days)
            return df
    return None


def cmd_kline(args):
    """查询K线数据"""
    df = load_kline(args.code, args.days)
    if df is None:
        print(f"未找到 {args.code} 的数据")
        return
    print(f"# {args.code} 最近 {len(df)} 个交易日")
    if args.format == "csv":
        print(df.to_csv(index=False))
    elif args.format == "json":
        records = df.to_dict(orient="records")
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        # 表格格式
        cols = ["date", "open", "high", "low", "close", "volume", "pctChg", "turn"]
        available = [c for c in cols if c in df.columns]
        print(df[available].to_string(index=False))


def cmd_info(args):
    """查询股票基本信息"""
    stock_list = get_stock_list()
    code = args.code.zfill(6)
    matches = stock_list[stock_list["code"].str.contains(code)]
    if len(matches) == 0:
        print(f"未找到 {args.code}")
        return
    for _, row in matches.iterrows():
        print(f"代码: {row['code']}")
        print(f"名称: {row['code_name']}")
        print(f"上市日期: {row['ipoDate']}")
        # 检查本地数据
        df = load_kline(row["code"])
        if df is not None:
            print(f"本地K线: {len(df)} 行 ({df['date'].min()} ~ {df['date'].max()})")
        else:
            print(f"本地K线: 无数据")


def cmd_search(args):
    """按名称搜索股票"""
    stock_list = get_stock_list()
    keyword = args.keyword
    matches = stock_list[stock_list["code_name"].str.contains(keyword, na=False)]
    print(f"搜索 \"{keyword}\" 找到 {len(matches)} 只:")
    for _, row in matches.head(20).iterrows():
        df = load_kline(row["code"])
        latest = ""
        if df is not None and len(df) > 0:
            last = df.iloc[-1]
            latest = f" | 最新:{last.get('close', 'N/A')} 涨跌:{last.get('pctChg', 'N/A')}%"
        print(f"  {row['code']} {row['code_name']}{latest}")


def cmd_latest(args):
    """查询最新行情"""
    stock_list = get_stock_list()
    if args.codes:
        codes = args.codes.split(",")
    else:
        # 默认查询所有有本地数据的股票
        codes = stock_list["code"].tolist()

    results = []
    for code in codes:
        code = code.strip().zfill(6)
        df = load_kline(code)
        if df is not None and len(df) > 0:
            last = df.iloc[-1]
            name_row = stock_list[stock_list["code"].str.contains(code)]
            name = name_row.iloc[0]["code_name"] if len(name_row) > 0 else code
            results.append({
                "code": code,
                "name": name,
                "date": last.get("date"),
                "close": last.get("close"),
                "pctChg": last.get("pctChg"),
                "volume": last.get("volume"),
                "turn": last.get("turn"),
            })

    if not results:
        print("无数据")
        return

    rdf = pd.DataFrame(results)
    rdf = rdf.sort_values("pctChg", ascending=False)
    print(f"最新行情 ({rdf.iloc[0].get('date', 'N/A')}):")
    print(rdf.to_string(index=False))


def cmd_top(args):
    """排行榜"""
    stock_list = get_stock_list()
    results = []
    for _, row in stock_list.iterrows():
        df = load_kline(row["code"])
        if df is not None and len(df) > 0:
            last = df.iloc[-1]
            results.append({
                "code": row["code"],
                "name": row["code_name"],
                "date": last.get("date"),
                "close": last.get("close"),
                "pctChg": last.get("pctChg"),
                "volume": last.get("volume"),
                "turn": last.get("turn"),
            })

    rdf = pd.DataFrame(results)
    rdf = rdf.sort_values(args.by, ascending=False).head(args.limit)
    print(f"Top {args.limit} by {args.by}:")
    print(rdf.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="本地A股数据查询")
    sub = parser.add_subparsers(dest="command")

    p_kline = sub.add_parser("kline", help="查询K线")
    p_kline.add_argument("code", help="股票代码")
    p_kline.add_argument("--days", type=int, default=30, help="最近N天")
    p_kline.add_argument("--format", choices=["table", "csv", "json"], default="table")

    p_info = sub.add_parser("info", help="股票信息")
    p_info.add_argument("code", help="股票代码")

    p_search = sub.add_parser("search", help="搜索股票")
    p_search.add_argument("keyword", help="关键词")

    p_latest = sub.add_parser("latest", help="最新行情")
    p_latest.add_argument("--codes", type=str, default=None, help="逗号分隔的代码")

    p_top = sub.add_parser("top", help="排行榜")
    p_top.add_argument("--by", default="pctChg", help="排序字段")
    p_top.add_argument("--limit", type=int, default=10, help="显示数量")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"kline": cmd_kline, "info": cmd_info, "search": cmd_search,
     "latest": cmd_latest, "top": cmd_top}[args.command](args)


if __name__ == "__main__":
    main()
