#!/usr/bin/env python3
"""
A股历史数据批量下载器（基于 baostock）
用法: python3 bulk_download.py [--years 5] [--resume]
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import baostock as bs
import pandas as pd

DATA_DIR = Path.home() / ".openclaw/agents/trading/data"
KLINE_DIR = DATA_DIR / "daily_kline"
META_FILE = DATA_DIR / "stock_list.parquet"
PROGRESS_FILE = DATA_DIR / "download_progress.json"

KLINE_FIELDS = "date,open,high,low,close,preclose,volume,amount,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"


def get_a_share_codes():
    """获取所有活跃A股代码"""
    rs = bs.query_stock_basic()
    data = []
    while rs.next():
        data.append(rs.get_row_data())
    df = pd.DataFrame(data, columns=rs.fields)
    # type=1 (股票), status=1 (上市)
    a_shares = df[(df["type"] == "1") & (df["status"] == "1")].copy()
    return a_shares


def download_kline(code, start_date, end_date):
    """下载单只股票的日K线数据"""
    rs = bs.query_history_k_data_plus(
        code,
        KLINE_FIELDS,
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="2",  # 前复权
    )
    data = []
    while rs.next():
        data.append(rs.get_row_data())
    if not data:
        return None
    df = pd.DataFrame(data, columns=rs.fields)
    # 转换数据类型
    for col in ["open", "high", "low", "close", "preclose", "volume", "amount", "turn", "pctChg", "peTTM", "pbMRQ", "psTTM", "pcfNcfTTM"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_progress():
    """加载下载进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": [], "failed": [], "last_run": None}


def save_progress(progress):
    """保存下载进度"""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="A股历史数据批量下载")
    parser.add_argument("--years", type=int, default=5, help="下载年数（默认5年）")
    parser.add_argument("--resume", action="store_true", help="断点续传，跳过已下载的股票")
    parser.add_argument("--batch-size", type=int, default=100, help="每批处理数量（默认100）")
    args = parser.parse_args()

    # 创建目录
    KLINE_DIR.mkdir(parents=True, exist_ok=True)

    # 登录
    lg = bs.login()
    if lg.error_code != "0":
        print(f"登录失败: {lg.error_msg}")
        sys.exit(1)
    print(f"baostock 登录成功")

    # 获取股票列表
    stock_list = get_a_share_codes()
    codes = stock_list["code"].tolist()
    print(f"A股股票总数: {len(codes)}")

    # 保存股票列表
    stock_list.to_parquet(META_FILE, index=False)
    print(f"股票列表已保存: {META_FILE}")

    # 计算日期范围
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.years * 365)).strftime("%Y-%m-%d")
    print(f"数据范围: {start_date} ~ {end_date}")

    # 加载进度
    progress = load_progress()
    completed = set(progress["completed"]) if args.resume else set()

    if completed:
        print(f"断点续传: 已完成 {len(completed)} 只，跳过")

    # 下载
    total = len(codes)
    success = 0
    failed = 0
    skipped = 0
    start_time = time.time()

    for i, code in enumerate(codes):
        if code in completed:
            skipped += 1
            continue

        try:
            df = download_kline(code, start_date, end_date)
            if df is not None and len(df) > 0:
                # 保存为 Parquet
                out_file = KLINE_DIR / f"{code.replace('.', '_')}.parquet"
                df.to_parquet(out_file, index=False, engine="pyarrow")
                success += 1
                progress["completed"].append(code)
            else:
                failed += 1
                progress["failed"].append({"code": code, "reason": "empty data"})
        except Exception as e:
            failed += 1
            progress["failed"].append({"code": code, "reason": str(e)[:200]})

        # 进度显示
        done = success + failed + skipped
        if done % 100 == 0 or done == total:
            elapsed = time.time() - start_time
            rate = (success + failed) / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate / 60 if rate > 0 else 0
            print(f"  [{done}/{total}] 成功:{success} 失败:{failed} 跳过:{skipped} | "
                  f"{rate:.1f}只/秒 | 预计剩余: {eta:.0f}分钟")

        # 每批保存进度
        if done % args.batch_size == 0:
            save_progress(progress)

    # 最终保存
    progress["last_run"] = datetime.now().isoformat()
    save_progress(progress)

    elapsed = time.time() - start_time
    print(f"\n下载完成!")
    print(f"  成功: {success}, 失败: {failed}, 跳过: {skipped}")
    print(f"  耗时: {elapsed/60:.1f} 分钟")
    print(f"  数据目录: {KLINE_DIR}")

    # 统计文件大小
    total_size = sum(f.stat().st_size for f in KLINE_DIR.glob("*.parquet"))
    print(f"  总大小: {total_size/(1024**2):.1f} MB")

    bs.logout()


if __name__ == "__main__":
    main()
