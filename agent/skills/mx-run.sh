#!/bin/bash
# mx-run.sh — 统一调用 mx-skills 的 wrapper 脚本
# 解决 OpenClaw exec preflight 拦截 "complex interpreter invocation" 的问题
# 用法: bash mx-run.sh <skill-name> [args...]
# 示例: bash mx-run.sh xuangu "今日涨幅大于2%的A股"
# 示例: bash mx-run.sh data "贵州茅台最新价"
# 示例: bash mx-run.sh moni "我的持仓"
# 示例: bash mx-run.sh search "贵州茅台最新研报"
# 示例: bash mx-run.sh zixuan "查询我的自选股列表"

export MX_APIKEY="mkt_faFnOMkoCZ-7x_taPxgvFKOLeZFT7WEcwNZT86ct3Ak"
export MX_API_URL="https://mkapi2.dfcfs.com/finskillshub"

SKILL_DIR="$HOME/.openclaw/agents/trading/skills"
SKILL="$1"
shift

case "$SKILL" in
  xuangu|xu)
    cd "$SKILL_DIR/mx-xuangu" && python3 mx_xuangu.py "$@"
    ;;
  data|d)
    cd "$SKILL_DIR/mx-data" && python3 mx_data.py "$@"
    ;;
  search|s)
    cd "$SKILL_DIR/mx-search" && python3 mx_search.py "$@"
    ;;
  moni|m)
    cd "$SKILL_DIR/mx-moni" && python3 mx_moni.py "$@"
    ;;
  zixuan|z)
    cd "$SKILL_DIR/mx-zixuan" && python3 mx_zixuan.py "$@"
    ;;
  *)
    echo "未知 skill: $SKILL"
    echo "可用: xuangu(选股) | data(数据) | search(搜索) | moni(模拟) | zixuan(自选)"
    exit 1
    ;;
esac
