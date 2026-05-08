#!/usr/bin/env python3
"""
妙想Skill集成模块
================
统一调用东方财富妙想Skill，为TradingAgents分析提供数据支撑：
- mx-data: 财务数据、估值、行情
- mx-search: 行业资讯、个股新闻、研报
- mx-xuangu: 同行业选股对比
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# 将 mx skill 目录加入路径
for d in ["mx-data", "mx-search", "mx-xuangu"]:
    skill_path = Path(__file__).parent.parent.parent / d
    if skill_path.exists() and str(skill_path) not in sys.path:
        sys.path.insert(0, str(skill_path))

from mx_data import MXData
from mx_search import MXSearch
from mx_xuangu import MXSelectStock


class MXIntegration:
    """妙想Skill集成客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MX_APIKEY")
        if not self.api_key:
            raise ValueError("MX_APIKEY 环境变量未设置")

        self.data = MXData(api_key=self.api_key)
        self.search = MXSearch(api_key=self.api_key)
        self.xuangu = MXSelectStock(api_key=self.api_key)

    def fetch_stock_financials(self, stock_name: str) -> Dict[str, Any]:
        """获取股票核心财务数据：PE、PB、ROE、营收、利润"""
        queries = [
            f"{stock_name}PE市盈率PB市净率ROE净资产收益率",
            f"{stock_name}最近3年每年净利润营业收入毛利率",
            f"{stock_name}资产负债率经营现金流净额",
        ]
        results = {}
        for q in queries:
            try:
                result = self.data.query(q)
                tables, cond, rows, err = self.data.parse_result(result)
                if not err and tables:
                    key = tables[0]["sheet_name"]
                    results[key] = {
                        "rows": tables[0]["rows"][:10],
                        "fieldnames": tables[0]["fieldnames"],
                    }
            except Exception as e:
                results[f"query_error_{q[:20]}"] = str(e)
        return results

    def fetch_stock_news(self, stock_name: str, days: int = 7) -> List[Dict[str, str]]:
        """获取个股相关新闻和研报"""
        queries = [
            f"{stock_name}最新研报",
            f"{stock_name}机构观点",
            f"{stock_name}最近新闻",
        ]
        all_news = []
        for q in queries:
            try:
                result = self.search.search(q)
                content = self.search.extract_content(result)
                all_news.append({"query": q, "content": content[:500]})
            except Exception as e:
                pass
        return all_news[:20]

    def fetch_industry_analysis(self, stock_name: str) -> Dict[str, Any]:
        """获取行业分析数据"""
        queries = [
            f"{stock_name}属于什么行业主营业务",
            f"{stock_name}行业平均PE PB ROE",
            f"{stock_name}行业景气度发展趋势",
        ]
        industry_data = {}
        for q in queries:
            try:
                result = self.data.query(q)
                tables, cond, rows, err = self.data.parse_result(result)
                if not err and tables:
                    industry_data[tables[0]["sheet_name"]] = {
                        "rows": tables[0]["rows"][:10],
                        "fieldnames": tables[0]["fieldnames"],
                    }
            except:
                pass

        # 用资讯获取行业深度分析
        industry_search_queries = [
            f"{stock_name}行业发展前景趋势分析",
            f"{stock_name}行业政策",
        ]
        industry_views = []
        for q in industry_search_queries:
            try:
                result = self.search.search(q)
                content = self.search.extract_content(result)
                if content:
                    industry_views.append({"query": q, "content": content[:500]})
            except:
                pass

        return {
            "industry_data": industry_data,
            "industry_views": industry_views,
        }

    def fetch_peer_comparison(self, stock_name: str) -> Dict[str, Any]:
        """获取同行业竞品对比数据"""
        queries = [
            f"{stock_name}同行业对比PE PB ROE毛利率",
            f"{stock_name}竞争对手市场份额",
        ]
        peer_data = {}
        for q in queries:
            try:
                result = self.data.query(q)
                tables, cond, rows, err = self.data.parse_result(result)
                if not err and tables:
                    peer_data[tables[0]["sheet_name"]] = {
                        "rows": tables[0]["rows"][:15],
                        "fieldnames": tables[0]["fieldnames"],
                    }
            except:
                pass

        # 用选股器找同行业股票
        try:
            xuangu_result = self.xuangu.search(f"ROE大于15% 市值大于100亿的消费行业股票")
            rows, data_source, err = self.xuangu.extract_data(xuangu_result)
            if not err and rows:
                peer_data["同行业选股"] = {
                    "rows": rows[:10],
                    "fieldnames": list(rows[0].keys()) if rows else [],
                }
        except:
            pass

        return peer_data

    def fetch_institutional_views(self, stock_name: str) -> List[Dict[str, str]]:
        """获取机构观点和研报"""
        queries = [
            f"{stock_name}券商研报评级目标价",
            f"{stock_name}基金持仓变动",
            f"{stock_name}北向资金流入流出",
        ]
        all_views = []
        for q in queries:
            try:
                result = self.search.search(q)
                content = self.search.extract_content(result)
                if content:
                    all_views.append({"query": q, "content": content[:400]})
            except:
                pass
        return all_views[:15]

    def fetch_macro_and_sector(self, stock_name: str) -> Dict[str, Any]:
        """获取宏观经济和板块数据"""
        queries = [
            "沪深300指数最新点位涨跌幅",
            "北向资金最近7天每日净流入",
            "A股两市融资融券余额",
        ]
        macro_data = {}
        for q in queries:
            try:
                result = self.data.query(q)
                tables, cond, rows, err = self.data.parse_result(result)
                if not err and tables:
                    macro_data[tables[0]["sheet_name"]] = {
                        "rows": tables[0]["rows"][:10],
                        "fieldnames": tables[0]["fieldnames"],
                    }
            except:
                pass
        return macro_data

    def comprehensive_analysis(self, stock_name: str) -> Dict[str, Any]:
        """综合分析：一次调用获取所有数据"""
        results = {}

        print(f"[MX] 获取 {stock_name} 核心财务数据...", file=sys.stderr)
        results["financials"] = self.fetch_stock_financials(stock_name)

        print(f"[MX] 获取 {stock_name} 行业分析...", file=sys.stderr)
        results["industry"] = self.fetch_industry_analysis(stock_name)

        print(f"[MX] 获取 {stock_name} 竞品对比...", file=sys.stderr)
        results["peers"] = self.fetch_peer_comparison(stock_name)

        print(f"[MX] 获取 {stock_name} 机构观点...", file=sys.stderr)
        results["institutional"] = self.fetch_institutional_views(stock_name)

        print(f"[MX] 获取宏观经济数据...", file=sys.stderr)
        results["macro"] = self.fetch_macro_and_sector(stock_name)

        print(f"[MX] 获取 {stock_name} 最新资讯...", file=sys.stderr)
        results["news"] = self.fetch_stock_news(stock_name)

        return results


def format_mx_data_for_report(mx_results: Dict[str, Any]) -> str:
    """将妙想数据格式化为报告可用的文本"""
    sections = []

    # 财务数据
    financials = mx_results.get("financials", {})
    if financials:
        sections.append("=== 核心财务数据 ===")
        for name, data in financials.items():
            if isinstance(data, dict) and "rows" in data:
                sections.append(f"\n{name}:")
                for row in data["rows"][:5]:
                    line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                    sections.append(f"  {line}")

    # 行业分析
    industry = mx_results.get("industry", {})
    if industry:
        sections.append("\n=== 行业分析 ===")
        for name, data in industry.items():
            if isinstance(data, dict) and "rows" in data:
                sections.append(f"\n{name}:")
                for row in data["rows"][:3]:
                    line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                    sections.append(f"  {line}")

    # 同行业对比
    peers = mx_results.get("peers", {})
    if peers:
        sections.append("\n=== 同行业对比 ===")
        for name, data in peers.items():
            if isinstance(data, dict) and "rows" in data:
                sections.append(f"\n{name}:")
                for row in data["rows"][:5]:
                    line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                    sections.append(f"  {line}")

    # 机构观点
    institutional = mx_results.get("institutional", [])
    if institutional:
        sections.append("\n=== 机构观点 ===")
        for view in institutional[:8]:
            if isinstance(view, dict):
                title = view.get("query", "")
                content = view.get("content", "")[:200]
                sections.append(f"  {title}: {content}")

    # 宏观数据
    macro = mx_results.get("macro", {})
    if macro:
        sections.append("\n=== 宏观环境 ===")
        for name, data in macro.items():
            if isinstance(data, dict) and "rows" in data:
                sections.append(f"\n{name}:")
                for row in data["rows"][:3]:
                    line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                    sections.append(f"  {line}")

    # 资讯
    news = mx_results.get("news", [])
    if news:
        sections.append("\n=== 最新资讯 ===")
        for item in news[:5]:
            if isinstance(item, dict):
                sections.append(f"  {item.get('query', '')}: {item.get('content', '')[:150]}")

    return "\n".join(sections)
