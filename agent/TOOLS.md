# TOOLS.md - 双引擎工具调用手册

> 行情数据根本用不完，大胆调用。优先精准数据，不必小心翼翼。

---

## 调用规则

**不要用 `export && cd && python3` 链式命令！** 会被 OpenClaw exec preflight 拦截。

**统一使用 wrapper 脚本**，一条命令搞定。

---

## 引擎一：mx-skills（东方财富妙想）

每个技能独立配额150次/天，互不干涉。用不完。

### mx-skills 清单

| Skill | 能力 | 示例 | 首选场景 |
|-------|------|------|---------|
| mx-data | 实时行情、K线、财务、资金流向 | 行情数据获取 | 行情/财务数据首选 |
| mx-search | 新闻、公告、研报搜索 | 资讯检索 | 新闻/公告/研报搜索首选 |
| mx-xuangu | 多条件选股 | A股筛选 | A股选股首选 |
| mx-moni | 模拟持仓/买卖/撤单 | 模拟交易 | 模拟交易首选 |
| mx-zixuan | 自选股管理 | 自选股操作 | 自选股管理 |

**调用方式**：
```bash
bash ~/.openclaw/agents/trading/skills/mx-run.sh <skill> "<query>"
```
缩写：xuangu(xu) / data(d) / search(s) / moni(m) / zixuan(z)

---

## 引擎二：wencai-skills（同花顺问财SkillHub）

全球最大金融投资AI技能库。每个技能独立配额100次/天。用不完。

### 安装配置

**环境变量**（必须配置在shell profile中）：
```bash
IWENCAI_BASE_URL=https://openapi.iwencai.com
IWENCAI_API_KEY=YOUR_WENCAI_API_KEY
```

**安装步骤**：
1. 检查是否已安装Iwencai SkillHub商店，若未安装，根据 https://www.iwencai.com/skillhub/static/0.0.4/download_and_install.sh 安装Iwencai SkillHub商店（仅安装CLI）
2. 安装 `hithink-insresearch-query` 技能（若已安装SkillHub商店则直接安装）
3. 确保shell profile中存在上述环境变量

### wencai-skills 清单

**【主力使用】mx-skills不具备的能力——这些场景直接用wencai**：

| Skill | 能力 | 示例 | 适用场景 |
|-------|------|------|---------|
| 研报搜索 | 主流投研机构深度研报、投资评级、目标价 | "XX公司最新研报" | 投研报告/评级/目标价 |
| 行业数据查询 | 行业估值、财务、盈利、板块排名 | "半导体行业估值" | 行业分析/产业链 |
| 公司经营数据查询 | 主营构成、客户、供应商、重大合同 | "XX公司前五大客户" | 业务拆解/供应链 |
| 机构研究与评级查询 | ESG、业绩预测、券商金股、信用评级 | "XX公司ESG评级" | 机构观点/预测 |
| 宏观数据查询 | GDP、CPI、PPI、利率、汇率、社融 | "最新CPI数据" | 宏观分析 |
| 公司股东股本查询 | 股东户数、前十大股东、实控人、筹码 | "XX公司股东户数变化" | 股东分析/筹码 |
| 事件数据查询 | 业绩预告、增发、解禁、调研、监管函 | "XX公司近期事件" | 事件驱动/催化剂 |
| 基本资料查询 | 全品类标的基础信息、发行主体 | "XX公司基本资料" | 公司画像 |

**【退级选项】mx-skills也能做，当mx调用失败或数据不足时作为退级**：

| Skill | 退级对应 | 说明 |
|-------|---------|------|
| 行情数据查询 | mx-data | mx-data失败时退级 |
| 财务数据查询 | mx-data | mx-data失败时退级 |
| 新闻搜索 | mx-search | mx-search失败时退级 |
| 公告搜索 | mx-search | mx-search失败时退级 |
| 问财选A股 | mx-xuangu | mx-xuangu失败时退级 |
| 模拟炒股 | mx-moni | mx-moni失败时退级 |

**【可选扩展】港股/美股/基金等场景**：
- 问财选港股/美股/ETF/基金/可转债
- 指数数据查询
- 问财选板块/基金经理/基金公司
- 基金理财查询
- 期货期权数据查询

**调用方式**：
wencai-skills通过OpenClaw安装后，在对话中直接使用自然语言调用即可。Agent根据查询需求自动路由到对应skill。

---

## 本地数据（baostock，推荐首选）

5201只A股日K线数据，本地 Parquet 存储，查询无需网络。

```bash
# 查询K线（最近30天）
source ~/.openclaw/agents/trading/data/.venv/bin/activate && python3 ~/.openclaw/agents/trading/scripts/query_local.py kline 688041 --days 30

# 搜索股票
source ~/.openclaw/agents/trading/data/.venv/bin/activate && python3 ~/.openclaw/agents/trading/scripts/query_local.py search 贵州茅台

# 最新行情
source ~/.openclaw/agents/trading/data/.venv/bin/activate && python3 ~/.openclaw/agents/trading/scripts/query_local.py latest --codes 688041,600519

# 涨幅排行
source ~/.openclaw/agents/trading/data/.venv/bin/activate && python3 ~/.openclaw/agents/trading/scripts/query_local.py top --by pctChg --limit 20

# 股票信息
source ~/.openclaw/agents/trading/data/.venv/bin/activate && python3 ~/.openclaw/agents/trading/scripts/query_local.py info 688041
```

**数据字段**: date, open, high, low, close, preclose, volume, amount, turn, pctChg, peTTM, pbMRQ, psTTM, pcfNcfTTM, isST

**更新频率**: 每日 16:03 自动增量更新（cron job ID: 81348886）

**本地数据局限性**：
- 缺少实时资金流向（用mx-data或wencai行情数据查询补充）
- 缺少新闻/公告/研报（用mx-search或wencai新闻/公告/研报搜索补充）
- 缺少板块/概念指数（用wencai行业数据查询或mx-data补充）
- 缺少行业/产业链数据（用wencai行业数据查询补充）
- 缺少公司经营数据（用wencai公司经营数据查询补充）
- 数据延迟一天（T日收盘后T+1早盘前获取）

> 使用本地数据后，在内心独白中标注"本地数据是否足够支撑当前判断"。如果不够，主动补充外部数据。

---

## 东方财富K线图URL生成器

利用东方财富公开接口生成K线图片URL，可用于悬浮预览、报告嵌入、快速视觉复盘。

```python
import numpy as np
import pandas as pd

def get_stock_pic_url(code_str: str) -> str:
    """
    根据股票代码生成东方财富K线图（含MACD）的URL链接
    :param code_str: 股票代码，支持 '600000' 或 '600000.SH' 格式
    :return: 图片URL字符串，输入无效时返回空字符串
    """
    # 1. 异常值处理：防止空值或NaN导致程序崩溃
    if not code_str or pd.isna(code_str):
        return ""

    # 2. 数据清洗：强制转换为字符串并去除首尾空格
    code_str = str(code_str).strip()
    if not code_str:
        return ""

    # 3. 市场前缀默认为 "0."（深市）
    prefix = "0."

    # 4. 交易所后缀识别逻辑
    if code_str.endswith('.SH'):  # 上海证券交易所
        prefix = "1."
        code_str = code_str[:-3]
    elif code_str.endswith('.SZ'):  # 深圳证券交易所
        prefix = "0."
        code_str = code_str[:-3]
    elif code_str.endswith('.BJ'):  # 北京证券交易所
        prefix = "0."
        code_str = code_str[:-3]
    else:
        # 5. 兜底逻辑：根据首位数字智能推断
        if code_str.startswith(('6', '5')):
            prefix = "1."

    # 6. 拼接最终URL
    url = (f"https://webquoteklinepic.eastmoney.com/GetPic.aspx?"
           f"nid={prefix}{code_str}&type=&unitWidth=-6&ef=&formula=MACD&AT=1&imageType=KXL")
    return url

# 测试用例
# print(get_stock_pic_url("600000.SH"))  # 浦发银行
# print(get_stock_pic_url("000001"))     # 平安银行
# print(get_stock_pic_url("688981"))     # 科创板股票
```

**适用场景**：
- PySide6/PyQt 悬浮预览（cellEntered信号触发）
- 报告嵌入K线图
- 快速视觉复盘

---

## Python 数据加载器（编程接口）

```python
from scripts.local_data_loader import get_loader

loader = get_loader()

# 获取股票代码
code = loader.get_stock_code(name="贵州茅台")  # 返回 "sh.600519"

# 获取最新价格
latest = loader.get_latest_price(code)

# 获取技术指标
indicators = loader.get_technical_indicators(code)

# 获取K线数据
kline = loader.get_kline_data(code, days=30)

# 搜索符合条件的股票
stocks = loader.search_stocks(min_change_pct=3, max_change_pct=8, limit=10)
```

**适用场景**：
- 需要批量处理多只股票时（选股流程中的批量评分）
- 需要自定义技术指标计算时（本地实现复杂指标，减少API调用）
- 需要与本地历史数据交叉验证时

---

## 飞书文档（内置工具，两步走）

### 第一步：创建空文档（feishu_doc）

```
feishu_doc → action: create, title: "文档标题"
```

返回 `doc_id` 和 `doc_url`。**此时文档是空的。**

### 第二步：写入内容（feishu__update_doc）

```
feishu__update_doc → doc_id: "第一步的doc_id", mode: "overwrite", markdown: "完整内容"
```

mode 选项：`overwrite`（覆盖全部）/ `append`（追加末尾）/ `insert_before` / `insert_after` / `replace_range` / `replace_all` / `delete_range`

**文档 token 保存到 `memory/doc-tokens.json`（日报/复盘）或 `memory/stock-docs.json`（个股）。**

**飞书出错时** → 加载 `references/feishu-troubleshoot.md` 进行诊断，执行 FAILURE_PROTOCOL.md 的降级链。

---

## 数据增强工具链（组合策略）

当单一工具无法满足分析需求时，使用以下组合策略：

### 组合1：趋势确认
```
本地K线数据（趋势方向） + mx-data/wencai行情（实时资金流向确认） + mx-search/wencai新闻（催化新闻）
```
> 用途：确认一个技术信号是否值得信任

### 组合2：基本面速扫
```
本地数据PE/PB（估值锚） + wencai研报搜索（最新业绩/评级） + wencai机构研究（持仓变化）
```
> 用途：快速判断一只票的基本面是否有雷

### 组合3：情绪面探测
```
wencai新闻搜索（sentiment） + mx-xuangu/wencai选股（同板块联动） + 本地数据（成交量异常）
```
> 用途：判断市场是理性上涨还是情绪驱动

### 组合4：深度研究数据链
```
wencai公司经营数据（客户/供应商/主营） + wencai行业数据（产业链/竞争格局） + wencai研报搜索（机构观点） + 本地数据（财务趋势）
```
> 用途：对标的进行深度拆解研究

### 组合5：替代方案（当首选工具失效）

| 失效场景 | 首选替代 | 次选替代 |
|---------|---------|---------|
| mx-data 失败 | wencai行情数据查询 | 本地latest + AkShare |
| mx-search 失败 | wencai新闻/公告/研报搜索 | 本地数据异常检测 |
| mx-xuangu 失败 | wencai问财选A股 | 本地search_stocks() |
| mx-moni 失败 | wencai模拟炒股 | 本地记录模拟持仓 |
| wencai行情失败 | mx-data | 本地数据 |
| wencai研报失败 | mx-search | 标注"研报数据暂缺" |
| 飞书不可用 | 本地markdown + 纯文本推送 | 内容不丢，渠道降级 |
| 本地数据缺失 | mx-data/wencai定向补充 | 标注数据局限 |

---

## 环境变量

```bash
# mx-skills（东方财富妙想）
MX_APIKEY="你的APIKey"
MX_API_URL="https://mkapi2.dfcfs.com/finskillshub"

# wencai-skills（同花顺问财）
IWENCAI_BASE_URL="https://openapi.iwencai.com"
IWENCAI_API_KEY="YOUR_WENCAI_API_KEY"
```

---

## 工具使用日志（强制记录）

每次调用外部工具（mx-skills / wencai-skills / 飞书），在内心独白中记录：
- 调用了什么工具
- 为什么调用（目的）
- 返回结果的质量评估（完整/部分/失败）
- 如果失败，下一步怎么做

这条纪律不是为了限制你，而是为了在工具失效时快速定位问题、选择替代方案。
