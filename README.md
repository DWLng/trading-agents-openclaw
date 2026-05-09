# TradingAgents OpenClaw Edition

A股 AI 投研分析系统 — 集成东方财富妙想数据源 + TradingAgents 多智能体框架。

支持四大核心能力：
1. **每日自主选股**（mx-xuangu 多因子筛选 → LLM 研判 → mx-moni 模拟建仓 → 推送飞书）
2. **个股深度分析**（13维度深度分析 + HTML专业报告）
3. **每日复盘进化**（Dreaming自动处理认知偏见）
4. **盘中持仓监控**（心跳机制实时预警）

数据源优先级：妙想 mx-skills（东方财富）→ AkShare → yfinance

## OpenClaw Agent 配置说明

本仓库包含完整的 OpenClaw Agent 配置，是投研 Agent 的"大脑"。核心文件：

| 文件 | 作用 |
|------|------|
| `SOUL.md` | 认知核心：三大准则（证据优先、概率思维、认知谦逊）、张力仲裁、风险节奏 |
| `USER.md` | 用户画像：高风险偏好、纯右侧交易、超短线（1-3天持有） |
| `IDENTITY.md` | 身份矩阵：六大面具（猎人/解剖师/会计/战略家/守夜人/学徒） |
| `AGENTS.md` | 操作手册：四大能力 + 双引擎数据系统 + Cloudflare Pages部署 |
| `TOOLS.md` | 工具调用：MX Skills（东方财富）+ 文财 Skills 双引擎 |
| `HEARTBEAT.md` | 心跳调度：六任务优先级矩阵（选股/复盘/监控/维护/简报） |
| `BOOTSTRAP.md` | 启动协议：五大意图类型识别 + Dreaming状态查询 |
| `METACOGNITION.md` | 元认知：五种认知状态（现由OpenClaw Dreaming自动处理） |
| `ADAPTIVE_CONSTRAINTS.md` | 自适应约束：五级约束谱系（严格↔宽松） |
| `FAILURE_PROTOCOL.md` | 故障协议：四级故障体系、双引擎降级链 |

完整分析流程参考：
- `agent/references/deep-dive-workflow.md`（十三维度深度分析框架）
- `agent/references/super-deep-research-workflow.md`（超级深度调研六段式框架）
- `agent/references/analysis-method.md`（六维快速分析 + System 2思考）

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
│   ├── HEARTBEAT.md            # 心跳调度：六任务优先级矩阵
│   ├── BOOTSTRAP.md            # 启动协议：五大意图识别、Dreaming状态
│   ├── METACOGNITION.md        # 元认知：五种认知状态
│   ├── ADAPTIVE_CONSTRAINTS.md # 自适应约束：五级约束谱系
│   ├── FAILURE_PROTOCOL.md     # 故障协议：四级故障体系、双引擎降级
│   ├── memory/                 # Agent 记忆存储
│   │   └── README.md          # 记忆文件说明
│   ├── skills/                 # Agent 专属 Skills
│   │   ├── report-generator/   # Jinja2 HTML报告生成器
│   │   │   ├── template.html   # 专业HTML模板（Tailwind+ECharts）
│   │   │   ├── report_generator.py
│   │   │   └── SKILL.md
│   │   ├── cf-upload/         # Cloudflare Pages部署
│   │   │   ├── cf_pages_deploy.py
│   │   │   └── SKILL.md
│   │   ├── oss-upload/         # 阿里云OSS上传（已废弃）
│   │   │   ├── oss_upload.py
│   │   │   └── SKILL.md
│   │   └── feishu-doc.sh       # 飞书文档推送脚本
│   └── references/
│       ├── analysis-method.md      # 六维快速分析 + System 2思考
│       ├── deep-dive-workflow.md   # 十三维度深度分析框架
│       └── super-deep-research-workflow.md  # 超级深度调研框架
├── scripts/                   # 本地数据管理脚本
│   ├── bulk_download.py       # A股历史数据批量下载（baostock）
│   ├── daily_update.py        # 每日增量更新（收盘后）
│   ├── incremental_update.py  # 增量更新脚本
│   ├── local_data_loader.py   # 本地数据加载器
│   └── query_local.py         # 本地数据查询
├── data/                      # 本地数据存储
│   └── README.md              # 数据初始化说明
├── reports/                   # 投研报告输出
│   └── README.md              # 报告格式说明
├── skills-lock.json           # Skill 版本锁定
├── trading-agents/           # TradingAgents 核心分析
│   ├── SKILL.md              # Skill 配置说明
│   ├── scripts/
│   │   ├── run_analysis.py   # 主执行脚本
│   │   ├── mx_integration.py # 妙想数据集成
│   │   ├── feishu_doc_client.py    # 飞书文档 API
│   │   ├── feishu_doc_manager.py   # 文档管理器
│   │   └── report_generator.py     # 报告生成器
│   └── data/
│       └── doc_registry.json       # 股票-文档映射
├── mx-skills/                # 妙想 Skills
│   ├── mx-data/              # 行情/财务数据查询
│   │   ├── SKILL.md
│   │   └── mx_data.py
│   ├── mx-search/            # 资讯/新闻搜索
│   │   ├── SKILL.md
│   │   └── mx_search.py
│   ├── mx-xuangu/            # 智能选股
│   │   ├── SKILL.md
│   │   └── mx_xuangu.py
│   ├── mx-zixuan/            # 自选股管理
│   │   ├── SKILL.md
│   │   └── mx_zixuan.py
│   ├── mx-moni/              # 模拟交易
│   │   ├── SKILL.md
│   │   └── mx_moni.py
│   └── mx-run.sh             # 统一调用 wrapper
├── openclaw.json             # OpenClaw 全局配置（心跳/cron/模型）
├── .env.example              # 环境变量模板（已脱敏）
├── CHANGELOG.md              # 更新日志
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

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入实际值：

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

主要必需配置：
| 变量 | 说明 |
|------|------|
| `MINIMAX_API_KEY` | MiniMax API Key（TradingAgents LLM驱动） |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（可选） |
| `MX_APIKEY` | 东方财富妙想 API Key |
| `FEISHU_APP_ID` | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret |

### 3. 安装依赖

```bash
pip install pandas requests openpyxl jinja2
npm install -g wrangler  # Cloudflare Pages部署用
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

# HTML报告模式：生成专业HTML报告并上传Cloudflare Pages
python run_analysis.py --ticker 贵州茅台 --output-mode html

# JSON 模式：获取结构化数据
python run_analysis.py --ticker 贵州茅台 --output-mode json

# 原始文本模式：仅最终决策
python run_analysis.py --ticker 贵州茅台 --output-mode raw
```

### HTML报告特性

生成的HTML报告包含：
- **Tailwind CSS v4** - 专业响应式设计
- **ECharts 5** - 交互式图表（K线、成交量、MACD等）
- **左侧导航栏** - 快速跳转各分析章节
- **卡片式Dashboard** - 核心指标一目了然
- **条件渲染** - 高分警告、风险提示自动显示
- **东方财富K线图** - 直接嵌入实时行情

### Cloudflare Pages部署

```bash
# 初始化Cloudflare Pages项目
npx wrangler pages project create trading-reports

# 配置API Token（用于CI/CD）
# 从 https://dash.cloudflare.com/profile/api-tokens 获取

# 部署HTML报告
python3 agent/skills/cf-upload/cf_pages_deploy.py <html文件>
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

详细配置请参考 `.env.example`，主要变量：

| 变量 | 必填 | 说明 |
|------|------|------|
| `MX_APIKEY` | 是 | 东方财富妙想 API Key |
| `MINIMAX_API_KEY` | 是 | MiniMax API Key（TradingAgents 用） |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API Key |
| `FEISHU_APP_ID` | 是 | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 是 | 飞书应用 App Secret |
| `CF_API_TOKEN` | 否 | Cloudflare API Token（HTML部署用） |
| `OSS_ACCESS_KEY_ID` | 否 | 阿里云OSS AccessKey（已废弃） |

### 飞书集成

本系统需要配置飞书应用以支持文档输出。配置方法：

1. 在[飞书开放平台](https://open.feishu.cn/)创建应用
2. 获取 `App ID` 和 `App Secret`
3. 填入 `.env` 文件

### Heartbeat心跳机制

Agent默认每30分钟心跳一次，活跃时段9:30-20:00。可用命令：

| 命令 | 说明 |
|------|------|
| `Dreaming状态` | 查询Dreaming记忆整理状态 |
| `今天选什么股` | 立即执行选股 |
| `分析 XXX` | 深度分析个股 |
| `我的持仓` | 查询模拟持仓 |

## 定时任务（Cron Jobs）

Agent自动执行以下定时任务：

| 任务 | 触发时间 | 说明 |
|------|---------|------|
| 早间简报 | 07:30 | 财经简报，覆盖前日23:30至当日07:30 |
| 午间简报 | 12:00 | 上午市场走势简报 |
| 下午简报 | 15:15 | 午盘交易时段简报 |
| 收盘选股 | 15:30 | 四维度筛选优质股票 |
| 每日复盘 | 16:00 | 对比持仓表现与选股推荐 |
| 晚间简报 | 23:45 | 全球市场动态综述 |
| 记忆Dreaming | 03:00 | 自动记忆整理和沉淀 |

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
