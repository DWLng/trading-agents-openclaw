# 超级深度调研报告工作流（超级融合版）

> **版本**: V1.1 Super Fusion | **融合来源**: deep-dive-workflow.md (13维度) + 机构级首次覆盖报告工作流(5-Task) | **适用对象**: 全面深度的A股/港股/美股上市公司投研分析
> **设计哲学**: 本工作流是deep-dive-workflow.md（13维度市场博弈视角）与机构级研报工作流的超级融合。前者提供"从生意本质到市场博弈"的全景覆盖，后者提供"从研究到估值到报告"的完整机构级生产流程。

---

## 一、框架概述

### 1.1 融合逻辑

| 来源框架 | 核心贡献 | 融合后继承 |
|----------|----------|-----------|
| **deep-dive-workflow.md (13维度)** | 市场维度视角（技术面/资金面/催化剂）、竞争对标、股东筹码、22种方法论工具箱 | 维度11-13实战框架、Level 1-4深度标准 |
| **机构级研报工作流(5-Task)** | 完整研报生产流程（研究→建模→估值→图表→报告）、6-8K字研究文档、6-tab Excel模型、25-35张图表、30-50页HTML报告 | 5-Task执行框架、交付物标准 |

### 1.2 适用场景

| 场景 | 推荐框架 |
|------|----------|
| 盘中快速决策（5分钟内） | analysis-method.md 六维快速分析 |
| 日常深度分析（4-12小时） | deep-dive-workflow.md 13维度 |
| 超级深度调研（15-25小时） | 本工作流 超级融合 |
| 选股报告 | HTML报告（Cloudflare Pages链接）|

### 1.3 输出格式说明

**所有分析报告统一输出为HTML格式**，原因：
- 支持图文并茂（嵌入base64图表）
- 支持复杂表格和样式
- 可通过链接分享，无需附件
- 跨平台兼容

**HTML报告命名**：`{股票代码}_{股票名}_超级深度调研_{日期}.html`
**存储位置**：`memory/reports/`

---

## 二、超级融合5-Task执行框架

### Task 0：准备与环境检查

**前置条件**：用户提供目标股票名称或代码

**执行步骤**：
1. 确认股票代码/名称
2. 创建工作目录 `memory/reports/{股票代码}_{日期}/`
3. 检查数据源可用性（mx-skills / wencai-skills）
4. 确认输出格式为HTML
5. **快速侦察**：使用东方财富K线图URL预览股票走势（见附录A）

**交付物**：
- 创建完成的确认消息
- 快速侦察截图（如需要）

---

### Task 1：公司研究（Company Research）

**前置条件**：Task 0完成

**核心目标**：生成6,000-8,000字的深度研究文档

**执行步骤**：
1. 加载 `references/deep-dive-workflow.md` 的维度1-6（公司画像、历史与发展、业务拆解、产业链、竞争对标、护城河）
2. 应用六段式框架的宏观情景设定（维度1）
3. 应用六段式框架的行业生命周期分析（维度2）
4. 应用六段式框架的公司竞争力评估（维度3）
5. 使用22种方法论工具箱进行深度分析

**研究文档结构（HTML格式）**：

```html
<!-- 约6,000-8,000字 -->
<h1>{股票名称}({代码}) 公司研究报告</h1>

<h2>一、公司画像</h2>
<!-- 公司基本信息、行业定位、一句话生意描述 -->

<h2>二、历史与发展</h2>
<!-- 里程碑时间线、关键一跃、管理层画像 -->

<h2>三、业务拆解</h2>
<!-- 业务板块矩阵、产品矩阵、大客户绑定、BOM结构 -->

<h2>四、产业链与行业分析</h2>
<!-- 行业规模/集中度、波特五力、议价权评估 -->

<h2>五、竞争对标</h2>
<!-- 竞争对手矩阵、赛道分类、竞争态势 -->

<h2>六、护城河评估</h2>
<!-- 五维护城河矩阵、综合评级 -->

<h2>七、宏观情景设定</h2>
<!-- 乐观/中性/悲观三种情景 -->

<h2>八、行业生命周期判断</h2>
<!-- 渗透率/增速分析、波特五力 -->

<h2>九、风险评估</h2>
<!-- 8类风险矩阵、地缘政治灰犀牛 -->
```

**交付物**：
- `memory/reports/{股票代码}_{日期}/01_公司研究.html`
- 文档长度：6,000-8,000字（不含HTML标签）

---

### Task 2：财务建模（Financial Modeling）

**前置条件**：Task 1完成

**核心目标**：构建完整的6-tab Excel财务模型

**执行步骤**：
1. 提取历史财务数据（3-5年）
2. 构建收入模型（20-30个产品线 + 15-20个地区）
3. 构建完整损益表（40-50个科目）
4. 构建现金流量表
5. 构建资产负债表
6. 构建情景分析（乐观/中性/悲观）
7. 准备DCF输入数据

**Excel模型结构（6 tabs）**：

| Tab | 内容 | 行数要求 |
|-----|------|----------|
| Revenue Model | 产品线营收 + 地区营收分解 | 20-30 + 15-20行 |
| Income Statement | 完整损益表 | 40-50行 |
| Cash Flow | 经营/投资/融资现金流 | 完整结构 |
| Balance Sheet | 资产负债表 | 完整结构 |
| Scenarios | Bull/Base/Bear情景对比 | 三情景完整参数 |
| DCF Inputs | 终端价值/WACC/增长率 | 准备Task 3使用 |

**交付物**：
- `memory/reports/{股票代码}_{日期}/02_财务模型.xlsx`

---

### Task 3：估值分析（Valuation Analysis）

**前置条件**：Task 2完成

**核心目标**：完成DCF + 可比公司法分析，生成目标价

**执行步骤**：
1. DCF估值（敏感性分析：WACC ±1%/±2%，永续增长率 ±0.5%/±1%）
2. 可比公司法（5-10家对标公司，含统计摘要：max/75th/median/25th/min）
3. 情景估值（Bull/Base/Bear）
4. 生成估值"足球场"图
5. 确定目标价和评级

**估值分析结构（HTML格式）**：

```html
<h1>{股票名称}({代码}) 估值分析报告</h1>

<h2>一、DCF估值</h2>
<!-- 详细假设、自由现金流预测、敏感性矩阵 -->

<h2>二、可比公司法</h2>
<!-- 5-10家对标公司表格、统计摘要 -->

<h2>三、情景分析</h2>
<!-- Bull/Base/Bear三种情景及概率 -->

<h2>四、估值足球场</h2>
<!-- 估值区间可视化 -->

<h2>五、综合评级与目标价</h2>
<!-- BUY/HOLD/SELL、目标价、预期涨幅 -->

<h2>六、关键催化剂</h2>
<!-- 3-5个核心驱动因素 -->
```

**交付物**：
- `memory/reports/{股票代码}_{日期}/03_估值分析.html`
- 更新 `02_财务模型.xlsx` 添加DCF tab

---

### Task 4：图表生成（Chart Generation）

**前置条件**：Task 1, 2, 3完成

**核心目标**：生成25-35张专业财务图表

**图表清单（35张）**：

| 类别 | 图表编号 | 内容 |
|------|----------|------|
| **投资摘要** | chart_01 | 历史股价走势图 |
| **财务表现** | chart_02-04, chart_10-12, chart_14 | 营收/利润/现金流/毛利率/ROE/杜邦分解 |
| **公司概况** | chart_05-09, chart_15-18 | 里程碑/产品/客户/竞争/市场份额 |
| **情景分析** | chart_13 | Bull/Base/Bear对比 |
| **估值** | chart_28-34 | DCF敏感性/估值区间/可比公司/足球场 |

**必须包含的4张核心图表**：
- chart_03: 营收产品结构（堆叠面积图）⭐
- chart_04: 营收地区分布（堆叠柱状图）⭐
- chart_28: DCF敏感性（双向热力图）⭐
- chart_32: 估值足球场（水平条形图）⭐

**图表要求**：
- 分辨率：300 DPI
- 格式：PNG或JPG
- 命名：`chart_{编号}_{描述}.png`

**交付物**：
- `memory/reports/{股票代码}_{日期}/charts/` 目录（35张图表）
- `memory/reports/{股票代码}_{日期}/04_图表目录.txt`

---

### Task 5：报告组装（Report Assembly）

**前置条件**：Task 1, 2, 3, 4全部完成

**核心目标**：同时生成飞书文档（用户习惯）+ HTML报告（动态效果）

**双重输出架构**：
1. **飞书文档**：用户习惯的格式，保持原有效果
2. **HTML报告**：使用 report-generator 生成，支持动态图表

**执行步骤**：

1. **创建飞书文档**：
   - 使用 `lark-doc` skill 创建飞书文档
   - 内容为完整的超级深度调研报告
   - 这是用户习惯的主要输出格式

2. **生成HTML报告**（并行）：
   - 构建包含 `title`、`dashboard`、`content_markdown` 的JSON
   - 调用 `report-generator` skill：
     ```bash
     python3 skills/report-generator/report_generator.py <input.json>
     ```
   - HTML使用Tailwind CSS + ECharts，支持动态图表

3. **部署到 Cloudflare Pages**：
   - 使用 `cf-upload` skill 部署生成的HTML
   - 获取永久在线链接

4. **返回结果**：
   - 发送飞书文档链接给用户
   - 同时发送HTML报告链接

**JSON数据格式**：

```json
{
    "title": "{股票名称}({代码}) 超级深度调研报告",
    "subtitle": "{日期}",
    "content_markdown": "<!-- 完整报告内容 -->",
    "dashboard": [
        {"label": "目标价", "value": "{目标价}元", "icon": "target", "value_class": "text-green-400"},
        {"label": "止损位", "value": "{止损}元", "icon": "shield", "value_class": "text-red-400"},
        {"label": "综合评级", "value": "{评级}", "icon": "star", "value_class": "text-blue-400"},
        {"label": "预期涨幅", "value": "{涨幅}%", "icon": "trending-up", "value_class": "text-green-400"}
    ],
    "kline_data": null,
    "fund_flow_data": null,
    "score": {评分}
}
```

**交付物**：
- 飞书文档链接
- HTML报告OSS链接：`memory/reports/{股票代码}_{日期}/超级深度调研报告.html`

---

## 三、质量控制清单

### Task 1 必过项
- [ ] 公司研究文档 6,000-8,000字
- [ ] 公司画像包含9项基本信息
- [ ] 历史里程碑至少6个关键事件
- [ ] 业务拆解覆盖所有主要板块（营收>5%）
- [ ] 波特五力分析完整
- [ ] 护城河五维度评估完整
- [ ] 宏观三种情景设定
- [ ] 8类风险矩阵

### Task 2 必过项
- [ ] Excel模型6个tabs完整
- [ ] 收入模型20-30个产品线
- [ ] 损益表40-50个科目
- [ ] 三种情景完整参数
- [ ] DCF输入数据准备完毕

### Task 3 必过项
- [ ] DCF敏感性分析完整（WACC ±1%/±2%，g ±0.5%/±1%）
- [ ] 5-10家可比公司分析
- [ ] 统计摘要（max/75th/median/25th/min）
- [ ] 估值足球场图
- [ ] 明确目标价和评级

### Task 4 必过项
- [ ] 至少25张图表
- [ ] 4张核心图表必须包含
- [ ] 300 DPI分辨率
- [ ] chart_03 营收产品结构图 ⭐
- [ ] chart_04 营收地区分布图 ⭐
- [ ] chart_28 DCF敏感性热力图 ⭐
- [ ] chart_32 估值足球场图 ⭐

### Task 5 必过项
- [ ] 飞书文档创建成功，获得文档链接
- [ ] HTML报告生成成功（使用report-generator）
- [ ] HTML报告上传Cloudflare Pages，获得分享链接
- [ ] 同时向用户发送两个链接
- [ ] JSON数据可被Jinja2模板正确渲染
- [ ] HTML报告部署Cloudflare Pages成功

---

## 四、执行流程图

```
用户请求超级深度调研
         ↓
┌─ Task 0: 准备环境 ─┐
│  - 确认股票代码     │
│  - 创建工作目录    │
│  - 检查数据源      │
│  - 快速侦察K线图   │
└────────┬───────────┘
         ↓
┌─ Task 1: 公司研究 ─┐
│  - 加载13维度框架  │
│  - 应用六段式分析  │
│  - 生成6-8K字Markdown│
└────────┬───────────┘
         ↓
┌─ Task 2: 财务建模 ─┐
│  - 提取历史数据   │
│  - 构建6-tab模型 │
│  - 三情景分析     │
└────────┬───────────┘
         ↓
┌─ Task 3: 估值分析 ─┐
│  - DCF + 可比公司法│
│  - 敏感性分析     │
│  - 目标价 + 评级  │
└────────┬───────────┘
         ↓
┌─ Task 4: 图表生成 ─┐
│  - 生成25-35张图表 │
│  - 4张核心图表⭐   │
└────────┬───────────┘
         ↓
┌─ Task 5: 报告组装 ─┐
│  - 创建飞书文档   │ ← 主要输出
│  - 构建Dashboard JSON│
│  - 调用report-generator│ ← HTML报告
│  - 部署Cloudflare Pages│
└────────┬───────────┘
         ↓
    同时输出：
    - 飞书文档链接
    - HTML报告Cloudflare Pages链接
```

---

## 五、输出方案

**主方案**：OSS + HTML（已配置）
- 使用 `report-generator` skill 生成HTML
- 使用 `cf-upload` skill 部署到 Cloudflare Pages
- 生成分享链接发送给用户

**流程**：
```
Markdown + JSON → report-generator.py → HTML报告 → cf_pages_deploy.py → Cloudflare Pages链接
```

**优点**：
- 完美保留HTML格式和ECharts动态图表
- 支持Tailwind CSS专业样式
- 分享链接永久有效

---

## 六、与deep-dive-workflow.md的关系

| 维度 | deep-dive-workflow.md | 本工作流 |
|------|----------------------|----------|
| 分析深度 | Level 1-4 | Level 4（全景覆盖）|
| 执行时间 | 1-25小时 | 15-25小时 |
| 交付物 | 飞书文档 + HTML报告 | 飞书文档 + HTML报告 |
| 图表 | 选画 | 25-35张（必须）|
| 财务模型 | 简化版 | 6-tab完整模型 |
| 流程 | 单次执行 | 5-Task分步验证 |

---

> **文档版本**: V1.1 Super Fusion
> **最后更新**: 2026年5月
> **适用范围**: 超级深度的上市公司投研分析
> **执行方式**: 严格按5-Task分步执行，每步验证前置条件

---

## 附录A：K线图快速预览URL方案（东方财富接口）

利用东方财富公开接口，无需数据获取和绘图代码，一行拼接生成带MACD的K线预览图。

### 适用场景

- Task 0 快速侦察阶段预览股票走势
- 选股初筛阶段快速预览多只股票
- 盘中监控时快速查看异动股K线
- 表格/列表悬浮预览（PySide6/PyQt cellEntered事件）

### 核心函数

```python
def get_stock_pic_url(code_str: str) -> str:
    """
    根据股票代码生成东方财富K线图（含MACD）的URL链接
    :param code_str: 股票代码，支持 '600000' 或 '600000.SH' 格式
    :return: 图片URL字符串，输入无效时返回空字符串
    """
    import pandas as pd
    if not code_str or pd.isna(code_str):
        return ""
    code_str = str(code_str).strip()
    if not code_str:
        return ""

    prefix = "0."
    if code_str.endswith('.SH'):       # 上海证券交易所
        prefix = "1."
        code_str = code_str[:-3]
    elif code_str.endswith('.SZ'):     # 深圳证券交易所
        prefix = "0."
        code_str = code_str[:-3]
    elif code_str.endswith('.BJ'):     # 北京证券交易所
        prefix = "0."
        code_str = code_str[:-3]
    else:
        # 智能推断：沪市6/5开头，深市0/3开头
        if code_str.startswith(('6', '5')):
            prefix = "1."

    url = (f"https://webquoteklinepic.eastmoney.com/GetPic.aspx?"
           f"nid={prefix}{code_str}&type=&unitWidth=-6&ef=&formula=MACD&AT=1&imageType=KXL")
    return url
```

### URL参数说明

| 参数 | 含义 | 可选值 |
|------|------|--------|
| `nid` | 市场前缀+代码 | `1.600000`（沪）、`0.000001`（深） |
| `formula` | 技术指标 | `MACD`（默认）、`KDJ`、空 |
| `imageType` | 图表类型 | `KXL`（K线图） |
| `unitWidth` | K线宽度 | `-6`（自适应） |

### 示例

```python
print(get_stock_pic_url("600000.SH"))  # 浦发银行
print(get_stock_pic_url("000001"))     # 平安银行
print(get_stock_pic_url("688981"))     # 科创板股票
```

### 注意事项

- 需联网调用，图片由东方财富服务器实时渲染
- 深色背景图片，不支持自定义配色
- Task 0 快速侦察用，正式Task 4图表仍使用matplotlib/mplfinance生成高质量图表
