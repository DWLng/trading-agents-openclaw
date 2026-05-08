#!/usr/bin/env python3
"""
飞书文档管理器
===============
维护股票代码 -> 飞书文档的映射关系，支持：
1. 首次分析：创建新文档
2. 重复分析：在同一文档中追加新的分析记录
3. 历史追踪：保留同一股票的历次分析时间线

映射文件：{REPO_DIR}/trading-agents/data/doc_registry.json
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from feishu_doc_client import FeishuDocClient

REGISTRY_PATH = Path(__file__).parent.parent / "data" / "doc_registry.json"


def _load_registry() -> Dict[str, Any]:
    """加载文档注册表。"""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_registry(registry: Dict[str, Any]):
    """保存文档注册表。"""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


def get_or_create_doc(ticker: str, ticker_name: str = "") -> Dict[str, str]:
    """
    获取或创建股票分析文档。

    Returns:
        {"document_id": "xxx", "url": "https://...", "is_new": True/False}
    """
    registry = _load_registry()
    normalized_ticker = ticker.upper().replace(".SZ", "").replace(".SS", "").replace(".SH", "").replace(".BJ", "")

    if normalized_ticker in registry:
        doc_info = registry[normalized_ticker]
        # 验证文档是否仍然存在（可选）
        return {
            "document_id": doc_info["document_id"],
            "url": doc_info["url"],
            "is_new": False,
        }

    # 创建新文档
    client = FeishuDocClient(account_id="trading")
    title = f"{ticker_name or normalized_ticker} 投研分析"
    doc = client.create_document(title=title)

    registry[normalized_ticker] = {
        "document_id": doc["document_id"],
        "url": doc["url"],
        "title": title,
        "created_at": datetime.now().isoformat(),
        "analysis_count": 0,
        "analysis_history": [],
    }
    _save_registry(registry)

    return {
        "document_id": doc["document_id"],
        "url": doc["url"],
        "is_new": True,
    }


def record_analysis(ticker: str, analysis_date: str, rating: str, doc_id: str):
    """记录一次分析到注册表中。"""
    registry = _load_registry()
    normalized_ticker = ticker.upper().replace(".SZ", "").replace(".SS", "").replace(".SH", "").replace(".BJ", "")

    if normalized_ticker not in registry:
        return

    entry = registry[normalized_ticker]
    entry["analysis_count"] = entry.get("analysis_count", 0) + 1
    entry["last_analysis"] = analysis_date
    entry["last_rating"] = rating

    history = entry.setdefault("analysis_history", [])
    history.append({
        "date": analysis_date,
        "rating": rating,
        "timestamp": datetime.now().isoformat(),
    })
    # 只保留最近 20 条历史
    if len(history) > 20:
        history = history[-20:]
    entry["analysis_history"] = history

    _save_registry(registry)


def get_doc_history(ticker: str) -> List[Dict[str, str]]:
    """获取某只股票的历史分析记录。"""
    registry = _load_registry()
    normalized_ticker = ticker.upper().replace(".SZ", "").replace(".SS", "").replace(".SH", "").replace(".BJ", "")
    if normalized_ticker in registry:
        return registry[normalized_ticker].get("analysis_history", [])
    return []


def get_all_registry() -> Dict[str, Any]:
    """获取完整的注册表（用于管理）。"""
    return _load_registry()
