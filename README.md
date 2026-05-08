# TradingAgents OpenClaw Edition

A股 AI 投研分析系统 — 集成东方财富妙想数据源 + TradingAgents 多智能体框架。

支持两大核心能力：
1. **每日自主选股**（mx-xuangu 多因子筛选 → LLM 研判 → mx-moni 模拟建仓 → 推送飞书）
2. **个股深度分析**（12个Agent协作：技术面→情绪面→新闻面→基本面→多空辩论→风控→决策）

数据源优先级：妙想 mx-skills（东方财富）→ AkShare → yfinance

## OpenClaw Agent 配置说明

本仓库包含完整的 OpenClaw Agent 配置，是投研 Agent 的"大脑"。核心文件：

| 文件 | 作用 |
|------|------|
| `SOUL.md` | 认知核心：三大准则（证据优先、概率思维、认知谦逊）、张力仲裁、风险节奏 |
| `USER.md` | 用户画像：高风险偏好、纯右侧交易、超短线（1-3天持有） |
| `IDENTITY.md` | 身份矩阵：六大面具（猎人/解剖师/会计/战略家/守夜人/学徒） |
| `AGENTS.md` | 操作手册：每日选股、个股分析、每日复盘、持仓监控四大能力 |
| `TOOLS.md` | 工具调用：MX Skills（东方财富）+ 文财 Skills 双引擎 |
| `HEARTBEAT.md` | 心跳调度：15:30选股、16:00复盘、9:30持仓监控 |
| `BOOTSTRAP.md` | 启动协议：五大意图类型识别、风格校准 |
| `METACOGNITION.md` | 元认知：五种认知状态（常规/探索/危机/反思/创新） |
| `ADAPTIVE_CONSTRAINTS.md` | 自适应约束：五级约束谱系（严格↔宽松） |
| `FAILURE_PROTOCOL.md` | 故障协议：四级故障体系、双引擎降级链 |

完整分析流程参考 `agent/references/deep-dive-workflow.md`（十三维度深度分析框架）。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    TradingAgents 分析框架                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Market       │  │ Social       │  │ News         │      │
│  │ Analyst      │  │ Analyst      │  │ Analyst      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Fundamentals │  │ Bull/Bear    │──▶ Research Manager     │
│  │ Analyst      │  │ Researcher   │                         │
│  └──────────────┘  └──────────────┘                         │
│                              │                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Risk (×3)    │  │ Trader       │  │ Portfolio    │      │
│  │ Management   │  │              │  │ Manager      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    妙想 MX Skills 数据层                      │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐│
│  │mx-data │  │mx-search│ │mx-xuangu│ │mx-zixuan│ │mx-moni││
│  │ 行情/财务 │  │ 资讯搜索 │  │ 智能选股  │  │ 自选管理  │  │ 模拟交易 ││
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    飞书文档输出层                             │
│           投研报告自动生成/更新到飞书文档                      │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
trading-agents-openclaw/
├── agent/                      # OpenClaw Agent 配置（核心认知层）
│   ├── SOUL.md                 # 认知核心：三大准则、张力仲裁、风险节奏
│   ├── USER.md                 # 用户画像：高风险偏好、右侧交易、超短线
│   ├── IDENTITY.md             # 身份矩阵：六大面具、四层认知
│   ├── AGENTS.md               # 操作手册：四大能力、双引擎数据系统
│   ├── TOOLS.md                # 工具调用指南：MX Skills + 文财 Skills
│   ├── HEARTBEAT.md            # 心跳调度：选股/复盘/监控任务节律
│   ├── BOOTSTRAP.md            # 启动协议：五大意图识别、风格校准
│   ├── METACOGNITION.md        # 元认知：五种认知状态、模式识别
│   ├── ADAPTIVE_CONSTRAINTS.md # 自适应约束：五级约束谱系
│   ├── FAILURE_PROTOCOL.md     # 故障协议：四级故障体系、双引擎降级
│   ├── memory/                 # Agent 记忆存储
│   │   └── README.md          # 记忆文件说明
│   └── references/
│       ├── analysis-method.md  # 六维快速分析框架
│       └── deep-dive-workflow.md  # 十三维度深度分析框架
├── scripts/                   # 本地数据管理脚本
│   ├── bulk_download.py       # A股历史数据批量下载（baostock）
│   ├── daily_update.py        # 每日增量更新（收盘后）
│   ├── incremental_update.py   # 增量更新脚本
│   ├── local_data_loader.py   # 本地数据加载器
│   └── query_local.py         # 本地数据查询
├── data/                      # 本地数据存储
│   └── README.md              # 数据初始化说明
├── reports/                   # 投研报告输出
│   └── README.md              # 报告格式说明
├── skills-lock.json           # Skill 版本锁定
├── trading-agents/           # TradingAgents 核心分析
│   ├── SKILL.md             # Skill 配置说明
│   ├── scripts/
│   │   ├── run_analysis.py  # 主执行脚本
│   │   ├── mx_integration.py # 妙想数据集成
│   │   ├── feishu_doc_client.py    # 飞书文档 API
│   │   ├── feishu_doc_manager.py  # 文档管理器
│   │   └── report_generator.py    # 报告生成器
│   └── data/
│       └── doc_registry.json      # 股票-文档映射
├── mx-skills/               # 妙想 Skills
│   ├── mx-data/             # 行情/财务数据查询
│   │   ├── SKILL.md
│   │   └── mx_data.py
│   ├── mx-search/           # 资讯/新闻搜索
│   │   ├── SKILL.md
│   │   └── mx_search.py
│   ├── mx-xuangu/           # 智能选股
│   │   ├── SKILL.md
│   │   └── mx_xuangu.py
│   ├── mx-zixuan/           # 自选股管理
│   │   ├── SKILL.md
│   │   └── mx_zixuan.py
│   ├── mx-moni/             # 模拟交易
│   │   ├── SKILL.md
│   │   └── mx_moni.py
│   └── mx-run.sh            # 统一调用 wrapper
├── .env.example             # 环境变量模板
├── .gitignore               # Git 忽略配置
└── README.md
```

## 环境准备

### 1. 安装 TradingAgents

```bash
git clone https://github.com/TauricResearch/TradingAgents.git ~/TradingAgents-Kimi
cd ~/TradingAgents-Kimi
pip install -e .
```

### 2. 获取 API Keys

#### 妙想 MX API Key
1. 前往 [东方财富妙想 Skills](https://dl.dfcfs.com/m/itc4) 获取 API Key
2. 设置环境变量：
   ```bash
   export MX_APIKEY="your_mx_apikey_here"
   ```

#### MiniMax API Key（TradingAgents LLM 驱动）
```bash
export MINIMAX_API_KEY="your_minimax_key"
```

### 3. 安装依赖

```bash
pip install pandas requests openpyxl
```

## 快速开始

### 方式一：使用 MX Skills（推荐）

```bash
# 设置 API Key
export MX_APIKEY="your_mx_apikey_here"

# 选股示例
cd mx-skills
python mx-xuangu/mx_xuangu.py "ROE大于15% 市盈率小于30 净利润增长率大于20%"

# 数据查询示例
python mx-data/mx_data.py "贵州茅台最新价 涨跌幅 市盈率"

# 资讯搜索示例
python mx-search/mx_search.py "贵州茅台最新研报"
```

### 方式二：使用 TradingAgents 深度分析

```bash
# 设置环境变量
export MX_APIKEY="your_mx_apikey_here"
export MINIMAX_API_KEY="your_minimax_key"
export TRADINGAGENTS_PROJECT="$HOME/TradingAgents-Kimi"

# 执行分析
cd trading-agents/scripts
python run_analysis.py --ticker 贵州茅台 --date 2026-05-06 --market cn
```

### 方式三：使用 Wrapper 脚本

```bash
# 设置环境变量
export MX_APIKEY="your_mx_apikey_here"

# 统一调用接口
bash mx-skills/mx-run.sh xuangu "今日涨幅大于2%的A股"
bash mx-skills/mx-run.sh data "贵州茅台最新价"
bash mx-skills/mx-run.sh search "宁德时代最新研报"
```

## 输出模式

```bash
# 飞书文档模式（默认）：生成专业投研报告
python run_analysis.py --ticker 贵州茅台 --output-mode feishu-doc

# 飞书消息模式：直接发送 Markdown 摘要
python run_analysis.py --ticker 贵州茅台 --output-mode feishu-msg

# JSON 模式：获取结构化数据
python run_analysis.py --ticker 贵州茅台 --output-mode json

# 原始文本模式：仅最终决策
python run_analysis.py --ticker 贵州茅台 --output-mode raw
```

## MX Skills 详解

| Skill | 功能 | 数据源 |
|-------|------|--------|
| mx-data | 行情/财务/资金流数据 | 东方财富 |
| mx-search | 研报/新闻/公告搜索 | 东方财富 |
| mx-xuangu | 多因子条件选股 | 东方财富 |
| mx-zixuan | 自选股管理 | 东方财富 |
| mx-moni | 模拟买卖/持仓查询 | 东方财富 |

## 配置说明

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MX_APIKEY` | 是 | 东方财富妙想 API Key |
| `MINIMAX_API_KEY` | 是 | MiniMax API Key（TradingAgents 用） |
| `TRADINGAGENTS_PROJECT` | 否 | TradingAgents 项目路径，默认 `~/TradingAgents-Kimi` |
| `MX_OUTPUT_DIR` | 否 | MX Skills 输出目录，默认 `~/.openclaw/workspace/mx_data/output` |

### 飞书集成

本系统需要配置飞书应用以支持文档输出。配置方法：

1. 在[飞书开放平台](https://open.feishu.cn/)创建应用
2. 获取 `App ID` 和 `App Secret`
3. 配置到 OpenClaw 或直接修改 `feishu_doc_client.py` 中的凭据

## 成本控制

| 操作 | Token 消耗 | 频率 |
|------|-----------|------|
| 选股研判 | ~20K tokens | 每日1次 |
| 个股深度分析 | ~87K tokens | 按需 |
| 复盘分析 | ~15K tokens | 每日1次 |

降本方式：
- 选股用轻量模型（MiniMax-M2.5）
- 深度分析用标准模型（MiniMax-M2.7-highspeed）
- 减少 TradingAgents 辩论轮次

## 故障排查

| 问题 | 解决 |
|------|------|
| "MX_APIKEY not set" | 设置环境变量 `export MX_APIKEY=your_key` |
| mx-skills 调用失败 | 检查 MX_APIKEY 是否正确 |
| mx-moni "未绑定模拟账户" | 前往妙想 Skills 页面创建并绑定模拟账户 |
| mx-xuangu 结果为空 | 放宽筛选条件 |
| TradingAgents 超时 | 使用后台模式，减少 debate 轮次 |
| 飞书消息太长 | 改用 feishu-doc 模式 |

## 免责声明

- 本系统**仅用于研究目的**，不构成投资建议
- 模拟交易 only，不涉及真实资金
- API Key 通过环境变量管理，不硬编码

## License

MIT
