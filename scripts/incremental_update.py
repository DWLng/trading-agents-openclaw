#!/usr/bin/env python3
"""
A股历史数据增量更新器（基于 baostock）
========================================
只下载每个股票从上次更新日期到今天的增量数据，
追加到已有的 parquet 文件中。

用法:
    python3 incremental_update.py              # 增量更新所有股票
    python3 incremental_update.py --code 600519 # 只更新指定股票
    python3 incremental_update.py --dry-run     # 只检查，不实际下载
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
PROGRESS_FILE = DATA_DIR / "incremental_progress.json"

KLINE_FIELDS = "date,open,high,low,close,preclose,volume,amount,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"


def get_all_parquet_files():
    """获取所有已下载的 parquet 文件。"""
    return sorted(KLINE_DIR.glob("*.parquet"))


def get_last_date(filepath: Path) -> str:
    """获取 parquet 文件中最新的日期。"""
    try:
        df = pd.read_parquet(filepath, columns=["date"])
        return df["date"].max()
    except Exception:
        return None


def code_to_baostock(code: str) -> str:
    """sh_600519 → sh.600519"""
    return code.replace("_", ".")


def baostock_to_filename(code: str) -> str:
    """sh.600519 → sh_600519.parquet"""
    return code.replace(".", "_") + ".parquet"


def download_incremental(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """下载单只股票的增量数据。"""
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
        return pd.DataFrame()
    df = pd.DataFrame(data, columns=rs.fields)
    return df


def update_single(filepath: Path, end_date: str, dry_run: bool = False) -> dict:
    """增量更新单个 parquet 文件。"""
    code_file = filepath.stem  # sh_600519
    code_bs = code_to_baostock(code_file)  # sh.600519

    last_date = get_last_date(filepath)
    if last_date is None:
        return {"code": code_file, "status": "error", "msg": "无法读取最后日期"}

    # 计算增量起始日期（last_date + 1 天）
    last_dt = datetime.strptime(last_date, "%Y-%m-%d")
    start_dt = last_dt + timedelta(days=1)
    start_date = start_dt.strftime("%Y-%m-%d")

    if start_date > end_date:
        return {"code": code_file, "status": "up_to_date", "last_date": last_date}

    if dry_run:
        return {"code": code_file, "status": "needs_update", "from": start_date, "to": end_date}

    # 下载增量数据
    new_df = download_incremental(code_bs, start_date, end_date)
    if new_df.empty:
        return {"code": code_file, "status": "no_new_data", "last_date": last_date}

    # 读取原有数据并追加
    old_df = pd.read_parquet(filepath)
    combined = pd.concat([old_df, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["date"]).sort_values("date")

    # 保存
    combined.to_parquet(filepath, index=False)
    return {
        "code": code_file,
        "status": "updated",
        "new_rows": len(new_df),
        "total_rows": len(combined),
        "from": start_date,
        "to": end_date,
    }


def main():
    parser = argparse.ArgumentParser(description="A股数据增量更新")
    parser.add_argument("--code", help="只更新指定股票代码（如 sh_600519）")
    parser.add_argument("--end-date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="更新截止日期（默认今天）")
    parser.add_argument("--dry-run", action="store_true", help="只检查，不实际下载")
    parser.add_argument("--batch-size", type=int, default=50, help="批处理大小")
    args = parser.parse_args()

    KLINE_DIR.mkdir(parents=True, exist_ok=True)

    # 登录 baostock
    lg = bs.login()
    if lg.error_code != "0":
        print(f"❌ baostock 登录失败: {lg.error_msg}")
        sys.exit(1)

    try:
        if args.code:
            # 更新单只股票
            filepath = KLINE_DIR / f"{args.code}.parquet"
            if not filepath.exists():
                print(f"❌ 文件不存在: {filepath}")
                sys.exit(1)
            result = update_single(filepath, args.end_date, args.dry_run)
            print(json.dumps(result, ensure_ascii=False))
        else:
            # 批量增量更新
            files = get_all_parquet_files()
            total = len(files)
            print(f"📊 检查 {total} 只股票的增量更新...")

            stats = {"up_to_date": 0, "updated": 0, "no_new_data": 0, "error": 0, "needs_update": 0}
            updated_codes = []

            for i, filepath in enumerate(files):
                result = update_single(filepath, args.end_date, args.dry_run)
                status = result["status"]
                stats[status] = stats.get(status, 0) + 1

                if status == "updated":
                    updated_codes.append(result["code"])
                    print(f"  ✅ {result['code']}: +{result['new_rows']} 行 ({result['from']} ~ {result['to']})")

                if (i + 1) % args.batch_size == 0:
                    print(f"  进度: {i + 1}/{total} ({(i + 1) / total * 100:.1f}%)")

            print(f"\n📈 增量更新完成:")
            print(f"  已最新: {stats['up_to_date']}")
            print(f"  已更新: {stats['updated']}")
            print(f"  无新数据: {stats['no_new_data']}")
            print(f"  需更新(dry-run): {stats['needs_update']}")
            print(f"  错误: {stats['error']}")

            if updated_codes:
                print(f"\n  更新的股票: {', '.join(updated_codes[:20])}{'...' if len(updated_codes) > 20 else ''}")

            # 保存进度
            progress = {
                "last_update": args.end_date,
                "stats": stats,
                "updated_codes": updated_codes,
                "timestamp": datetime.now().isoformat(),
            }
            with open(PROGRESS_FILE, "w") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

    finally:
        bs.logout()


if __name__ == "__main__":
    main()
