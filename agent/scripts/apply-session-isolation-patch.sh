#!/bin/bash
# apply-session-isolation-patch.sh
# 自动应用飞书插件 Session 隔离补丁
# 每次 OpenClaw 升级后自动运行

set -e

PATCHES_DIR="$HOME/.openclaw/agents/trading/patches"
LARK_PLUGIN_DIR="$HOME/.openclaw/extensions/openclaw-lark"
DISPATCH_CONTEXT_FILE="$LARK_PLUGIN_DIR/src/messaging/inbound/dispatch-context.js"

echo "🔧 应用 Session 隔离补丁..."

# 检查补丁文件是否存在
if [ ! -f "$PATCHES_DIR/larksuite-openclaw-lark+2026.4.1.patch" ]; then
    echo "❌ 补丁文件不存在: $PATCHES_DIR/larksuite-openclaw-lark+2026.4.1.patch"
    exit 1
fi

# 检查目标文件是否存在
if [ ! -f "$DISPATCH_CONTEXT_FILE" ]; then
    echo "❌ 目标文件不存在: $DISPATCH_CONTEXT_FILE"
    echo "   飞书插件可能未安装，跳过补丁应用"
    exit 0
fi

# 检查是否已经打过补丁（通过检查特征字符串）
if grep -q "Session isolation: append chat_id prefix" "$DISPATCH_CONTEXT_FILE" 2>/dev/null; then
    echo "✅ 补丁已应用，跳过"
    exit 0
fi

# 应用补丁
echo "📦 应用补丁到 $DISPATCH_CONTEXT_FILE..."
cd "$LARK_PLUGIN_DIR"

# 使用 patch 命令或手动应用
if command -v patch &> /dev/null; then
    patch -p1 < "$PATCHES_DIR/larksuite-openclaw-lark+2026.4.1.patch"
    echo "✅ 补丁应用成功"
else
    # 手动应用（fallback）
    echo "⚠️ patch 命令不可用，尝试手动应用..."
    # 这里可以添加手动应用逻辑
    echo "❌ 请手动应用补丁或安装 patch 命令"
    exit 1
fi

echo "✨ 完成"
