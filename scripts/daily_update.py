#!/usr/bin/env python3
"""
每日增量更新脚本 — baostock 版本
收盘后运行，更新本地 K 线数据。替代已失效的 akshare/eastmoney 方案。

用法:
  python3 daily_update.py                        # 正常增量更新（全量）
  python3 daily_update.py --batch-size 200       # 限制每次更新数量
  python3 daily_update.py --check                # 仅检查需要更新的股票
  python3 daily_update.py --date 2026-05-07      # 指定日期（默认今天）
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

import baostock as bs


class DailyUpdater:
    """每日数据更新器 — baostock 数据源"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/agents/trading/data")
        self.data_dir = Path(data_dir)
        self.kline_dir = self.data_dir / "daily_kline"
        self.stock_list_path = self.data_dir / "stock_list.parquet"
        self.progress_file = self.data_dir / "update_progress.json"
        self._bs_logged_in = False

    def _baostock_login(self):
        """登录 baostock（幂等）"""
        if self._bs_logged_in:
            return True
        lg = bs.login()
        if lg.error_code != '0':
            print(f"baostock 登录失败: {lg.error_msg}")
            return False
        self._bs_logged_in = True
        return True

    def _baostock_logout(self):
        """登出 baostock"""
        if self._bs_logged_in:
            bs.logout()
            self._bs_logged_in = False

    def get_update_list(self, target_date: str = None) -> list:
        """获取需要更新的股票列表（增量检测）"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")

        if not self.stock_list_path.exists():
            print(f"股票列表文件不存在: {self.stock_list_path}")
            return []

        df = pd.read_parquet(self.stock_list_path)
        all_codes = df["code"].tolist()

        need_update = []
        target_dt = pd.Timestamp(target_date)

        for code in all_codes:
            file_code = code.replace(".", "_")
            kline_file = self.kline_dir / f"{file_code}.parquet"

            if not kline_file.exists():
                need_update.append(code)
                continue

            try:
                kline_df = pd.read_parquet(kline_file)
                date_col = "date" if "date" in kline_df.columns else "trade_date"
                last_date = pd.to_datetime(kline_df[date_col]).max()

                if last_date < target_dt:
                    need_update.append(code)
            except Exception:
                need_update.append(code)

        return need_update

    def _fetch_stock_kline(self, code: str, start_date: str, end_date: str) -> pd.DataFrame | None:
        """
        通过 baostock 获取单只股票的日K线数据
        返回 DataFrame with columns: date, open, high, low, close, volume, amount, turn
        """
        try:
            # baostock 频率参数: d=日k线, adjustflag=2 前复权
            rs = bs.query_history_k_data_plus(
                code,
                "date,open,high,low,close,volume,amount,turn",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"
            )

            if rs.error_code != '0':
                return None

            rows = []
            while rs.next():
                rows.append(rs.get_row_data())

            if not rows:
                return None

            df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume", "amount", "turn"])

            # 过滤空行（baostock 有时返回全空字符串的行）
            df = df[df["open"] != ""]

            # 类型转换
            df["date"]   = pd.to_datetime(df["date"])
            df["open"]   = pd.to_numeric(df["open"], errors='coerce').astype('float64')
            df["high"]   = pd.to_numeric(df["high"], errors='coerce').astype('float64')
            df["low"]    = pd.to_numeric(df["low"], errors='coerce').astype('float64')
            df["close"]  = pd.to_numeric(df["close"], errors='coerce').astype('float64')
            df["volume"] = pd.to_numeric(df["volume"], errors='coerce').astype('Int64')
            df["amount"] = pd.to_numeric(df["amount"], errors='coerce').astype('float64')
            df["turn"]   = pd.to_numeric(df["turn"], errors='coerce').astype('float64')

            # 去掉 NaN 行
            df = df.dropna(subset=["close"])

            return df if not df.empty else None

        except Exception as e:
            print(f"  [网络] {code} 请求异常: {e}")
            return None

    def update_stock(self, code: str, start_date: str, end_date: str) -> bool:
        """
        增量更新单只股票数据。
        start_date 到 end_date 区间内的新数据会被追加到本地文件。
        """
        df_new = self._fetch_stock_kline(code, start_date, end_date)
        if df_new is None or df_new.empty:
            return False

        file_code = code.replace(".", "_")
        kline_file = self.kline_dir / f"{file_code}.parquet"

        # 确保新数据列类型一致
        for col in ["open", "high", "low", "close", "amount", "turn"]:
            df_new[col] = pd.to_numeric(df_new[col], errors='coerce').astype('float64')
        df_new["volume"] = pd.to_numeric(df_new["volume"], errors='coerce').astype('Int64')
        df_new["date"] = pd.to_datetime(df_new["date"])

        if kline_file.exists():
            existing = pd.read_parquet(kline_file)
            if "date" not in existing.columns and "trade_date" in existing.columns:
                existing = existing.rename(columns={"trade_date": "date"})
            existing["date"] = pd.to_datetime(existing["date"])

            # 统一旧数据类型
            for col in ["open", "high", "low", "close", "amount", "turn"]:
                if col in existing.columns:
                    existing[col] = pd.to_numeric(existing[col], errors='coerce').astype('float64')
            if "volume" in existing.columns:
                existing["volume"] = pd.to_numeric(existing["volume"], errors='coerce').astype('Int64')

            df = pd.concat([existing, df_new], ignore_index=True)
            df = df.drop_duplicates(subset=["date"]).sort_values("date")
        else:
            df = df_new.sort_values("date")

        cols = ["date", "open", "high", "low", "close", "volume", "amount", "turn"]
        df = df[[c for c in cols if c in df.columns]]

        df.to_parquet(kline_file, index=False)
        return True

    def run_daily_update(
        self,
        batch_size: int = 0,
        target_date: str = None,
        sleep_ms: int = 80
    ) -> dict:
        """
        执行每日增量更新。

        参数:
          batch_size: 限制更新数量（0=全部）
          target_date: 目标日期，默认今天
          sleep_ms: 每次API调用之间的延迟（毫秒），避免服务器压力
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")

        print(f"=== 每日数据更新 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
        print(f"数据源: baostock | 目标日期: {target_date}")

        # 登录 baostock
        if not self._baostock_login():
            return {"updated": 0, "failed": 0, "skipped": 0, "error": "login_failed"}

        try:
            need_update = self.get_update_list(target_date)
            total = len(need_update)
            print(f"需要更新: {total} 只股票")

            if total == 0:
                print("数据已是最新，无需更新")
                return {"updated": 0, "failed": 0, "skipped": 0}

            to_process = need_update if batch_size == 0 else need_update[:batch_size]
            n = len(to_process)
            print(f"本次处理: {n} 只 (batch_size={'全部' if batch_size == 0 else batch_size})")

            updated = 0
            failed = 0
            skipped = 0
            start_time = time.time()
            errors = []

            # 计算查询起始日期：取最后有效日前一天的交易日
            # 保守起见，从5天前开始查询，重叠部分会被去重
            query_start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

            for i, code in enumerate(to_process):
                # 进度报告
                if i > 0 and i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    eta = (n - i) / rate if rate > 0 else 0
                    print(f"进度: {i}/{n} ({100*i//n}%) | "
                          f"成功:{updated} 失败:{failed} | "
                          f"速度:{rate:.1f}只/秒 | "
                          f"预计剩余:{eta:.0f}秒")

                try:
                    success = self.update_stock(code, query_start, target_date)
                    if success:
                        updated += 1
                    else:
                        # 静默失败：可能是新股、停牌、退市
                        skipped += 1
                except Exception as e:
                    failed += 1
                    err_msg = str(e)[:100]
                    if len(errors) < 10:
                        errors.append(f"{code}: {err_msg}")

                # 温和限速
                if sleep_ms > 0:
                    time.sleep(sleep_ms / 1000.0)

            elapsed = time.time() - start_time

        finally:
            self._baostock_logout()

        # 汇总
        print(f"\n{'='*50}")
        print(f"更新完成！")
        print(f"  成功: {updated}")
        print(f"  跳过: {skipped} (新股/停牌/无数据)")
        print(f"  失败: {failed}")
        print(f"  剩余: {len(need_update) - n}")
        print(f"  耗时: {elapsed:.1f}秒 ({elapsed/60:.1f}分钟)")
        if updated > 0:
            print(f"  平均: {elapsed/updated:.2f}秒/只")

        if errors:
            print(f"\n错误样本 (前{len(errors)}):")
            for e in errors:
                print(f"  - {e}")

        # 保存进度
        progress = {
            "date": target_date,
            "source": "baostock",
            "total_need_update": total,
            "processed": n,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "remaining": len(need_update) - n,
            "elapsed_seconds": round(elapsed, 1),
            "avg_seconds_per_stock": round(elapsed / n, 3) if n > 0 else 0,
            "errors": errors[:5]
        }

        with open(self.progress_file, "w") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

        return progress


def main():
    """CLI 入口"""
    updater = DailyUpdater()
    batch_size = 0
    target_date = None

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--check":
            target = sys.argv[i+1] if i+1 < len(sys.argv) and not sys.argv[i+1].startswith("--") else None
            if target:
                i += 1
            need = updater.get_update_list(target)
            print(f"需要更新: {len(need)} 只股票")
            if need:
                print("前20只:", need[:20])
            return
        elif arg == "--batch-size":
            batch_size = int(sys.argv[i+1]) if i+1 < len(sys.argv) else 200
            i += 1
        elif arg == "--date":
            target_date = sys.argv[i+1] if i+1 < len(sys.argv) else None
            i += 1
        elif arg == "--help" or arg == "-h":
            print(__doc__)
            return
        i += 1

    result = updater.run_daily_update(batch_size=batch_size, target_date=target_date)
    return 0 if result.get("updated", 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
