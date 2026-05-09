---
name: trading-agents
description: |
  A股AI投研分析系统 — 集成东方财富妙想数据源 + TradingAgents 多智能体框架。
  支持两大核心能力：
  1. 每日自主选股（mx-xuangu 多因子筛选 → LLM 研判 → mx-moni 模拟建仓 → 推送飞书）
  2. 个股深度分析（12个Agent协作：技术面→情绪面→新闻面→基本面→多空辩论→风控→决策）
  数据源优先级：妙想mx-skills（东方财富）→ AkShare → yfinance
license: MIT
compatibility: openclaw
metadata:
  version: "2.0.0"
  tags: [finance, trading, stock, analysis, a-share, stock-picking, minimax, akshare, dfcfw]
  author: user
  openclaw:
    emoji: "📈"
    requires:
      bins: [python3]
      paths:
        - /Users/mac/TradingAgents-Kimi
---

# TradingAgents Skill v2 | AI 选股 + 投研分析

本 Skill 是 A 股 AI 投研系统的核心，整合了**东方财富妙想 5 个 Skills** + **TradingAgents 多智能体框架**。

## 能力矩阵

| 能力 | 触发方式 | 数据源 | 输出 |
|------|---------|--------|------|
| 每日自主选股 | heartbeat 自动 / 用户手动 | mx-xuangu + mx-data + mx-search | 选股报告 + 模拟建仓 |
| 个股深度分析 | 用户指令 | mx-data + mx-search + TradingAgents | 飞书文档/消息 |
| 每日复盘 | heartbeat 自动 | mx-moni + 历史选股记录 | 复盘报告 + 参数建议 |
| 模拟炒股 | 随选股/分析自动执行 | mx-moni | 买卖操作记录 |

## 妙想 Skills 集成

| Skill | 路径 | 核心用途 | 调用方式 |
|-------|------|---------|---------|
| mx-data | `skills/mx-data/` | 行情/财务/资金流数据 | `python3 mx_data.py "{query}"` |
| mx-search | `skills/mx-search/` | 研报/新闻/公告搜索 | `python3 mx_search.py "{query}"` |
| mx-xuangu | `skills/mx-xuangu/` | 多因子条件选股 | `python3 mx_xuangu.py "{条件}"` |
| mx-zixuan | `skills/mx-zixuan/` | 自选股管理 | `python3 mx_zixuan.py "{query}"` |
| mx-moni | `skills/mx-moni/` | 模拟买卖/持仓查询 | `python3 mx_moni.py "{query}"` |

**调用前必须**: `export MX_APIKEY="YOUR_MX_APIKEY"`

## 选股流程（详细）

### Step 1: 多因子筛选（mx-xuangu）

运行 4 组选股条件：

```bash
cd ~/.openclaw/agents/trading/skills/mx-xuangu
export MX_APIKEY="YOUR_MX_APIKEY"

# 技术面强势
python3 mx_xuangu.py "今日涨幅1%-5% 成交量大于5亿 换手率3%-15% 量比大于1.5"

# 资金面强势
python3 mx_xuangu.py "今日主力净流入大于5000万 涨幅大于0%"

# 基本面优质
python3 mx_xuangu.py "ROE大于15% 市盈率小于30 净利润增长率大于20%"

# 热门概念
python3 mx_xuangu.py "近5日涨幅大于10% 成交量大于3亿"
```

### Step 2: 数据增强（mx-data）

对候选股票 Top10 补充详细数据：

```bash
cd ~/.openclaw/agents/trading/skills/mx-data
python3 mx_data.py "{股票名}最新价 涨跌幅 成交量 市盈率 市净率 ROE 主力资金流向"
```

### Step 3: 消息面扫描（mx-search）

```bash
cd ~/.openclaw/agents/trading/skills/mx-search
python3 mx_search.py "{股票名}最新研报 公告 新闻"
```

### Step 4: LLM 综合研判

将所有数据汇总，由 LLM 从 4 个维度评分并排序，输出 Top 5-10 推荐股票。

### Step 5: 模拟建仓（mx-moni）

```bash
cd ~/.openclaw/agents/trading/skills/mx-moni
python3 mx_moni.py "市价买入 {代码} {数量} 股"
```

### Step 6: 推送报告

格式化选股报告推送到飞书。

## 个股深度分析流程

### 触发话术

- "分析贵州茅台" / "看看 600519"
- "宁德时代怎么样" / "帮我分析 300750"
- "TradingAgents AAPL"

### 执行流程

1. **立即回复**: "正在启动分析 {股票}，预计 5-8 分钟..."
2. **快速数据**: mx-data + mx-search 获取实时数据
3. **深度分析**: `run_analysis.py --ticker {code} --output-mode feishu-doc`
4. **输出结果**: 飞书文档 URL 或消息摘要

### TradingAgents 12-Agent 架构

```
Analyst Team (4个)        Research Debate (3个)     Risk Management (4个)
├─ Market Analyst         ├─ Bull Researcher        ├─ Aggressive Analyst
├─ Social Analyst         ├─ Bear Researcher        ├─ Conservative Analyst
├─ News Analyst           └─ Research Manager       ├─ Neutral Analyst
└─ Fundamentals Analyst                            └─ Portfolio Manager
                                                    │
Trader Agent ──────────────────────────────────────▶ 最终决策
```

## 参数说明

```bash
python3 scripts/run_analysis.py \
  --ticker <股票代码或名称> \
  --date <分析日期 yyyy-mm-dd> \
  --market <auto|cn|us> \
  --output-mode <feishu-doc|feishu-msg|json|raw>
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--ticker` | 是 | 股票代码或名称。A股: `600519`/`贵州茅台`。美股: `AAPL` |
| `--date` | 否 | 分析日期，默认前天 |
| `--market` | 否 | `auto`(默认)/`cn`/`us` |
| `--output-mode` | 否 | `feishu-doc`(默认)/`feishu-msg`/`json`/`raw` |

## 复盘流程

每日自动执行：

1. 查询模拟持仓（mx-moni）
2. 读取 3 天前选股记录
3. 计算命中率和收益率
4. 分析成败原因
5. 建议参数调整
6. 更新 memory/strategy-params.md

## 完整日志

每次分析保存到: `~/.tradingagents/logs/{ticker}/`

## 故障排查

| 问题 | 解决 |
|------|------|
| mx-skills 调用失败 | 检查 MX_APIKEY 是否正确 |
| mx-moni "未绑定模拟账户" | 前往妙想 Skills 页面创建并绑定模拟账户 |
| mx-xuangu 结果为空 | 放宽筛选条件 |
| TradingAgents 超时 | 使用后台模式，减少 debate 轮次 |
| 飞书消息太长 | 改用 feishu-doc 模式 |

## 安全说明

- 本 Skill 仅用于研究目的，不构成投资建议
- 模拟交易 only，不涉及真实资金
- API Key 通过环境变量管理，不硬编码
