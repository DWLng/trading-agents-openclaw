# Agent 记忆目录

本目录用于存储 Agent 的运行时记忆文件。

## 目录结构

```
memory/
├── YYYY-MM-DD.md              # 每日操作日志
├── YYYY-MM-DD-picks.md       # 每日选股结果
├── YYYY-MM-DD-review.md      # 每日复盘报告
├── analysis_plan.json         # 分析计划跟踪
├── strategy-params.md         # 策略参数历史
└── charts/                    # 图表缓存
```

## 文件说明

| 文件 | 内容 |
|------|------|
| `YYYY-MM-DD.md` | 当日完整对话摘要和操作记录 |
| `YYYY-MM-DD-picks.md` | 选股结果（含理由） |
| `YYYY-MM-DD-review.md` | 收盘复盘报告 |
| `strategy-params.md` | 策略参数演化记录 |
| `analysis_plan.json` | 多步骤分析的进度跟踪 |

## 保留策略

- 保留最近 30 天的日志
- 定期将重要洞察迁移到 skills 配置中
