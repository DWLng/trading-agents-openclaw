---
name: report-generator
description: |
  TradingAgent 报告生成与渲染工具。
  将结构化的 Markdown/JSON 数据渲染为专业的 HTML 研报。
  支持：Tailwind CSS 响应式布局、ECharts 动态图表、左侧导航栏、Dashboard卡片、条件渲染样式。
  用于替代 LLM 手写 HTML，实现数据与表现层分离。
homepage: https://github.com/openclaw-trading/report-generator
version: 1.0.0
---

# report-generator 报告生成器

## 核心思想

**数据与表现层分离**：让 Agent 只输出结构化的 Markdown/JSON，由 Python 脚本+Jinja2 模板渲染为完美 HTML。

## 工作流程

```
Agent 输出 Markdown/JSON
        ↓
report_generator.py 渲染
        ↓
生成完美 HTML 报告
        ↓
cf_pages_deploy.py 部署到 Cloudflare Pages
        ↓
分享链接给用户
```

## 输入JSON格式

```json
{
    "title": "贵州茅台(600519) 深度分析",
    "subtitle": "2026-05-10 | 超级深度调研",
    "content_markdown": "# 公司画像\n\n这是分析内容...",
    "dashboard": [
        {"label": "目标价", "value": "2200元", "icon": "target", "value_class": "text-green-400"},
        {"label": "止损位", "value": "1800元", "icon": "shield", "value_class": "text-red-400"},
        {"label": "综合评分", "value": "82分", "icon": "star", "value_class": "text-blue-400"},
        {"label": "主力资金", "value": "净流入", "icon": "trending-up", "value_class": "text-green-400"}
    ],
    "kline_data": null,
    "fund_flow_data": null,
    "alert_type": null,
    "alert_message": "",
    "score": 82
}
```

## 使用方法

### 命令行

```bash
# 基本用法
python3 skills/report-generator/report_generator.py <输入文件.json>

# 指定输出目录
python3 skills/report-generator/report_generator.py <输入文件.json> /tmp/reports
```

### 在Agent中调用

```python
import subprocess
import json

# 准备数据
report_data = {
    "title": "贵州茅台(600519) 深度分析",
    "content_markdown": markdown_content,
    "dashboard": [
        {"label": "综合评分", "value": "82分", "icon": "star", "value_class": "text-blue-400"}
    ],
    "score": 82
}

# 写入临时JSON
with open("/tmp/report_input.json", "w", encoding="utf-8") as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

# 调用生成器
result = subprocess.run(
    ["python3", "/Users/mac/.openclaw/agents/trading/skills/report-generator/report_generator.py",
     "/tmp/report_input.json"],
    capture_output=True,
    text=True
)

output_path = result.stdout.strip().split("\n")[-1].replace("路径: ", "")
```

## 模板特性

| 特性 | 说明 |
|------|------|
| Tailwind CSS | CDN引入，自动暗黑模式 |
| ECharts | 支持K线图、资金流图动态交互 |
| 左侧导航栏 | 自动生成TOC，点击平滑滚动 |
| Dashboard卡片 | 顶部4格关键指标卡片 |
| 条件渲染 | 高分警告、风控Banner |
| 响应式 | 手机/电脑自适应 |

## ECharts图表数据格式

### K线图

```json
{
    "title": {"text": "K线走势"},
    "tooltip": {"trigger": "axis"},
    "xAxis": {"data": ["2026-05-01", "2026-05-02", ...]},
    "yAxis": {},
    "series": [
        {"name": "K线", "type": "candlestick", "data": [[open, close, low, high], ...]},
        {"name": "MA5", "type": "line", "data": [...]}
    ]
}
```

### 资金流图

```json
{
    "title": {"text": "资金流向"},
    "tooltip": {"trigger": "axis"},
    "xAxis": {"data": [...]},
    "yAxis": {},
    "series": [
        {"name": "主力资金", "type": "bar", "data": [...]}
    ]
}
```
