#!/usr/bin/env python3
"""
本地数据加载器
优先使用本地 Parquet 数据，失败再调用 API
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import json


class LocalDataLoader:
    """本地数据加载器"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/agents/trading/data")
        self.data_dir = Path(data_dir)
        self.kline_dir = self.data_dir / "daily_kline"
        self.stock_list_path = self.data_dir / "stock_list.parquet"

        # 缓存
        self._stock_list = None
        self._kline_cache = {}

    @property
    def stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        if self._stock_list is None:
            if self.stock_list_path.exists():
                self._stock_list = pd.read_parquet(self.stock_list_path)
            else:
                self._stock_list = pd.DataFrame()
        return self._stock_list

    def get_stock_code(self, name: str = None, code: str = None) -> Optional[str]:
        """
        根据名称或代码获取标准代码

        Args:
            name: 股票名称 (如 "贵州茅台")
            code: 股票代码 (如 "600519" 或 "sh.600519")

        Returns:
            标准代码 (如 "sh.600519") 或 None
        """
        df = self.stock_list
        if df.empty:
            return None

        if code:
            # 标准化代码格式
            if not code.startswith(("sh.", "sz.")):
                if code.startswith("6"):
                    code = f"sh.{code}"
                else:
                    code = f"sz.{code}"
            matches = df[df["code"] == code]
            if not matches.empty:
                return code

        if name:
            matches = df[df["code_name"].str.contains(name, na=False)]
            if not matches.empty:
                return matches.iloc[0]["code"]

        return None

    def get_kline_data(
        self,
        code: str,
        days: int = 30,
        end_date: str = None
    ) -> Optional[pd.DataFrame]:
        """
        获取 K 线数据

        Args:
            code: 股票代码 (如 "sh.600519")
            days: 获取天数
            end_date: 结束日期 (YYYY-MM-DD)，默认今天

        Returns:
            DataFrame 或 None
        """
        # 标准化代码
        if not code.startswith(("sh.", "sz.")):
            if code.startswith("6"):
                code = f"sh.{code}"
            else:
                code = f"sz.{code}"

        # 检查缓存
        cache_key = f"{code}_{days}_{end_date}"
        if cache_key in self._kline_cache:
            return self._kline_cache[cache_key]

        # 查找本地文件 (支持 sh.600519 和 sh_600519 两种格式)
        kline_file = self.kline_dir / f"{code}.parquet"
        if not kline_file.exists():
            # 尝试下划线格式
            code_underscore = code.replace(".", "_")
            kline_file = self.kline_dir / f"{code_underscore}.parquet"
        if not kline_file.exists():
            return None

        try:
            df = pd.read_parquet(kline_file)

            # 确保日期列存在
            if "date" not in df.columns and "trade_date" in df.columns:
                df = df.rename(columns={"trade_date": "date"})

            # 转换日期
            df["date"] = pd.to_datetime(df["date"])

            # 过滤日期范围
            if end_date:
                end_dt = pd.to_datetime(end_date)
            else:
                end_dt = datetime.now()

            start_dt = end_dt - timedelta(days=days)
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

            # 排序
            df = df.sort_values("date")

            # 缓存
            self._kline_cache[cache_key] = df

            return df

        except Exception as e:
            print(f"Error loading kline data for {code}: {e}")
            return None

    def get_latest_price(self, code: str) -> Optional[Dict]:
        """
        获取最新价格

        Returns:
            {
                "code": "sh.600519",
                "name": "贵州茅台",
                "price": 1800.0,
                "change_pct": 1.5,
                "volume": 12345,
                "date": "2026-05-02"
            }
        """
        df = self.get_kline_data(code, days=5)
        if df is None or df.empty:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        price = latest.get("close", latest.get("收盘价", 0))
        prev_close = prev.get("close", prev.get("收盘价", price))
        change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0

        return {
            "code": code,
            "name": self._get_stock_name(code),
            "price": float(price),
            "change_pct": round(change_pct, 2),
            "volume": int(latest.get("volume", latest.get("成交量", 0))),
            "date": latest["date"].strftime("%Y-%m-%d"),
        }

    def get_technical_indicators(self, code: str, days: int = 60) -> Optional[Dict]:
        """
        计算技术指标

        Returns:
            {
                "ma5": float,
                "ma10": float,
                "ma20": float,
                "ma60": float,
                "rsi": float,
                "macd_dif": float,
                "macd_dea": float,
                "macd_histogram": float,
                "volume_ratio": float,
            }
        """
        df = self.get_kline_data(code, days=days)
        if df is None or len(df) < 20:
            return None

        # 获取收盘价列
        close_col = "close" if "close" in df.columns else "收盘价"
        volume_col = "volume" if "volume" in df.columns else "成交量"

        if close_col not in df.columns:
            return None

        close = df[close_col].astype(float)
        volume = df[volume_col].astype(float) if volume_col in df.columns else None

        # 计算均线
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None

        # 计算 RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]

        # 计算 MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        macd_histogram = (dif - dea) * 2

        # 计算量比
        volume_ratio = 1.0
        if volume is not None and len(volume) >= 5:
            avg_vol_5 = volume.rolling(5).mean().iloc[-2]
            latest_vol = volume.iloc[-1]
            volume_ratio = latest_vol / avg_vol_5 if avg_vol_5 > 0 else 1.0

        return {
            "ma5": round(float(ma5), 2) if pd.notna(ma5) else None,
            "ma10": round(float(ma10), 2) if pd.notna(ma10) else None,
            "ma20": round(float(ma20), 2) if pd.notna(ma20) else None,
            "ma60": round(float(ma60), 2) if pd.notna(ma60) and ma60 else None,
            "rsi": round(float(rsi), 2) if pd.notna(rsi) else None,
            "macd_dif": round(float(dif.iloc[-1]), 4),
            "macd_dea": round(float(dea.iloc[-1]), 4),
            "macd_histogram": round(float(macd_histogram.iloc[-1]), 4),
            "volume_ratio": round(volume_ratio, 2),
        }

    def search_stocks(
        self,
        min_change_pct: float = None,
        max_change_pct: float = None,
        min_volume: float = None,
        min_turnover: float = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索符合条件的股票

        Args:
            min_change_pct: 最小涨跌幅 (%)
            max_change_pct: 最大涨跌幅 (%)
            min_volume: 最小成交量 (万元)
            min_turnover: 最小换手率 (%)
            limit: 返回数量

        Returns:
            股票列表
        """
        results = []
        df = self.stock_list

        if df.empty:
            return results

        # 随机采样一些股票检查
        sample_codes = df["code"].sample(min(100, len(df))).tolist()

        for code in sample_codes:
            latest = self.get_latest_price(code)
            if latest is None:
                continue

            # 应用过滤条件
            if min_change_pct is not None and latest["change_pct"] < min_change_pct:
                continue
            if max_change_pct is not None and latest["change_pct"] > max_change_pct:
                continue

            # 获取更多数据
            kline = self.get_kline_data(code, days=5)
            if kline is None or kline.empty:
                continue

            volume_col = "volume" if "volume" in kline.columns else "成交量"
            if volume_col in kline.columns and min_volume is not None:
                avg_volume = kline[volume_col].astype(float).mean()
                if avg_volume < min_volume * 10000:  # 转换为元
                    continue

            results.append(latest)

            if len(results) >= limit:
                break

        return sorted(results, key=lambda x: x["change_pct"], reverse=True)

    def get_data_coverage(self) -> Dict:
        """获取数据覆盖情况"""
        total_stocks = len(self.stock_list)
        downloaded = len(list(self.kline_dir.glob("*.parquet")))

        return {
            "total_stocks": total_stocks,
            "downloaded": downloaded,
            "coverage_pct": round(downloaded / total_stocks * 100, 1) if total_stocks > 0 else 0,
            "data_size_mb": sum(f.stat().st_size for f in self.kline_dir.glob("*.parquet")) / 1024 / 1024,
        }

    def _get_stock_name(self, code: str) -> str:
        """获取股票名称"""
        df = self.stock_list
        if df.empty:
            return code
        matches = df[df["code"] == code]
        if not matches.empty:
            return matches.iloc[0].get("code_name", code)
        return code


# 全局实例
_loader = None


def get_loader() -> LocalDataLoader:
    """获取全局数据加载器"""
    global _loader
    if _loader is None:
        _loader = LocalDataLoader()
    return _loader


# 命令行测试
if __name__ == "__main__":
    loader = get_loader()

    # 显示数据覆盖
    coverage = loader.get_data_coverage()
    print("=== 数据覆盖情况 ===")
    print(f"股票列表: {coverage['total_stocks']} 只")
    print(f"已下载: {coverage['downloaded']} 只")
    print(f"覆盖率: {coverage['coverage_pct']}%")
    print(f"数据大小: {coverage['data_size_mb']:.1f} MB")

    # 测试获取贵州茅台数据
    print("\n=== 测试: 贵州茅台 ===")
    code = loader.get_stock_code(name="贵州茅台")
    print(f"代码: {code}")

    if code:
        latest = loader.get_latest_price(code)
        print(f"最新价: {latest}")

        indicators = loader.get_technical_indicators(code)
        print(f"技术指标: {indicators}")
