#!/bin/bash
# feishu-doc.sh — 飞书文档操作 wrapper（使用 v2 API）
# 用法:
#   bash feishu-doc.sh create "标题" "markdown内容"
#   bash feishu-doc.sh overwrite <doc-token> "完整markdown内容"  ← 替换整个文档
#   bash feishu-doc.sh append <doc-token> "追加的markdown内容"
#   bash feishu-doc.sh fetch <doc-token>
#   bash feishu-doc.sh search "关键词"
#
# 注意：create 使用 v1 API（v2 暂不支持），其余使用 v2 API

CMD="$1"
shift

LARK_CLI="npx -y @larksuite/cli"

case "$CMD" in
  create)
    TITLE="$1"
    MARKDOWN="$2"
    $LARK_CLI docs +create --as bot --title "$TITLE" --markdown "$MARKDOWN"
    ;;
  overwrite)
    DOC="$1"
    CONTENT="$2"
    $LARK_CLI docs +update --api-version v2 --as bot --doc "$DOC" --command overwrite --content "$CONTENT" --doc-format markdown
    ;;
  append)
    DOC="$1"
    CONTENT="$2"
    $LARK_CLI docs +update --api-version v2 --as bot --doc "$DOC" --command append --content "$CONTENT" --doc-format markdown
    ;;
  str-replace)
    DOC="$1"
    PATTERN="$2"
    REPLACEMENT="$3"
    $LARK_CLI docs +update --api-version v2 --as bot --doc "$DOC" --command str_replace --pattern "$PATTERN" --content "$REPLACEMENT" --doc-format markdown
    ;;
  fetch)
    DOC="$1"
    $LARK_CLI docs +fetch --as user --doc "$DOC"
    ;;
  search)
    QUERY="$1"
    $LARK_CLI docs +search --as user --query "$QUERY"
    ;;
  *)
    echo "用法: feishu-doc.sh <create|overwrite|append|str-replace|fetch|search> [args]"
    echo ""
    echo "  create '标题' '内容'       - 创建新文档"
    echo "  overwrite <token> '内容'   - 替换整个文档内容"
    echo "  append <token> '内容'      - 追加到文档末尾"
    echo "  str-replace <token> '模式' '替换' - 替换匹配的文本"
    echo "  fetch <token>              - 获取文档内容"
    echo "  search '关键词'            - 搜索文档"
    exit 1
    ;;
esac
