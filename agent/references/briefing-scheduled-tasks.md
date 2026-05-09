# A股财经简报定时任务配置

> 本文件定义 trading agent 的定时简报推送功能，整合东财mx-search、问财wen-cai和AKShare三大数据源。

---

## 定时任务时间表

| 任务ID | 触发时间 | 推送时间 | 覆盖时段 | 说明 |
|--------|---------|---------|---------|------|
| morning-briefing | 07:30 | 08:00 | 前日23:30-07:30 | 早盘简报 |
| noon-briefing | 11:45 | 12:00 | 07:30-11:30 | 午盘简报 |
| afternoon-briefing | 15:15 | 15:30 | 11:30-15:00 | 收盘简报 |
| evening-briefing | 23:45 | 00:00 | 15:00-23:30 | 晚盘简报 |

**注**: 触发时间比推送时间提前15-30分钟，为报告生成预留时间。

---

## 数据源配置

### 环境变量（已在agent配置中）
- `MX_APIKEY` - 东财mx-search API密钥
- `IWENCAI_API_KEY` - 问财wen-cai API密钥

### 数据源说明

| 数据源 | 类型 | 用途 |
|--------|------|------|
| mx-search (东财) | Skill/API | 新闻、公告、研报搜索 |
| wen-cai (问财) | Skill/API | 新闻、公告、研报搜索 |
| AKShare | Python库 | A股行情、涨停板、龙虎榜数据 |

---

## 简报生成流程

### 1. 数据收集（调用Skills）

```
# 东财mx-search搜索
python skills/mx-search/mx_search.py "<搜索关键词>"

# 问财wen-cai搜索（如已安装wen-cai skill）
skillhub run wen-cai --type news --query "<搜索关键词>"

# AKShare行情数据
python -c "import akshare as ak; ak.stock_zh_a_spot_em()"
```

### 2. 报告生成检查项

- [ ] 读取前序报告（晚盘→午盘→早盘）
- [ ] 调用mx-search完成至少4组关键词搜索
- [ ] 调用wen-cai完成至少4组关键词搜索
- [ ] 使用AKShare获取行情数据（涨停池、龙虎榜等）
- [ ] 按模板格式生成报告
- [ ] 所有数据标注来源
- [ ] 无编造数据、无空白板块

### 3. 报告结构

```
# 📊 A股[时段]财经资讯报告

## 📈 一、隔夜/当日市场行情
### 1.1 美股/港股行情
### 1.2 A股指数表现
### 1.3 板块资金流向

## 📰 二、国内国际重点财经资讯
（至少8条，每条标注来源、影响分析）

## 🎤 三、名人大V券商研报观点
（至少5条，包含机构名称和评级）

## 🎯 四、当天重点关注
### 4.1 重点个股
### 4.2 重点板块/题材
### 4.3 潜在风险提示

## 📊 五、综合研判
### 5.1 市场情绪预判
### 5.2 操作策略建议
```

---

## Prompt模板位置

| 报告类型 | Prompt文件 |
|----------|-----------|
| 早盘简报 | `prompts/briefing/morning.md` |
| 午盘简报 | `prompts/briefing/noon.md` |
| 收盘简报 | `prompts/briefing/afternoon.md` |
| 晚盘简报 | `prompts/briefing/evening.md` |

---

## 手动触发命令

```bash
# 手动触发早盘简报
openclaw cron run morning-briefing

# 手动触发午盘简报
openclaw cron run noon-briefing

# 查看所有定时任务
openclaw cron list

# 查看任务运行历史
openclaw cron runs --id morning-briefing
```

---

## OpenClaw Cron配置示例

```bash
# 添加早盘简报定时任务
openclaw cron add \
  --name "morning-briefing" \
  --schedule "30 7 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行早盘简报任务（覆盖时段: 前日23:30-当日07:30）"

# 添加午盘简报定时任务
openclaw cron add \
  --name "noon-briefing" \
  --schedule "45 11 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行午盘简报任务（覆盖时段: 当日07:30-11:30）"

# 添加收盘简报定时任务
openclaw cron add \
  --name "afternoon-briefing" \
  --schedule "15 15 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行收盘简报任务（覆盖时段: 当日11:30-15:00）"

# 添加晚盘简报定时任务
openclaw cron add \
  --name "evening-briefing" \
  --schedule "45 23 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行晚盘简报任务（覆盖时段: 当日15:00-23:30）"
```

---

## 假期调整

非交易日（周末/节假日）建议禁用定时任务：

```bash
# 临时禁用所有任务
openclaw cron disable morning-briefing
openclaw cron disable noon-briefing
openclaw cron disable afternoon-briefing
openclaw cron disable evening-briefing

# 节后恢复
openclaw cron enable morning-briefing
openclaw cron enable noon-briefing
openclaw cron enable afternoon-briefing
openclaw cron enable evening-briefing
```

---

## 报告存储位置

生成的报告保存在：
```
~/.openclaw/workspace/trading/briefing/reports/
├── YYYY-MM-DD/
│   ├── MORNING_YYYYMMDD.md
│   ├── NOON_YYYYMMDD.md
│   ├── AFTERNOON_YYYYMMDD.md
│   └── EVENING_YYYYMMDD.md
```

---

## 校验规则

1. **不编造原则**：所有数据必须通过skill调用获取
2. **不留空原则**：每个板块必须有内容
3. **来源必标原则**：每条资讯标注来源
4. **数据时效原则**：所有数据属于覆盖时段内
