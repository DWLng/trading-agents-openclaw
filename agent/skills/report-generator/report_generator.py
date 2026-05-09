#!/usr/bin/env python3
"""
TradingAgent 报告生成器
将Markdown/JSON数据渲染为专业HTML报告

用法:
    python3 report_generator.py <输入文件.json> [输出目录]

输入JSON格式:
{
    "title": "贵州茅台(600519) 深度分析",
    "subtitle": "2026-05-10",
    "content_markdown": "# 公司画像\n\n这是分析内容...",
    "dashboard": [
        {"label": "目标价", "value": "2200元", "icon": "target", "value_class": "text-green-400"}
    ],
    "kline_data": null,  // ECharts K线图配置
    "fund_flow_data": null,  // ECharts 资金流配置
    "alert_type": null,  // "risk" 或 null
    "alert_message": "",
    "score": null
}
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("请先安装jinja2: pip install jinja2")
    sys.exit(1)


TEMPLATE_DIR = Path(__file__).parent
DEFAULT_OUTPUT_DIR = Path.home() / ".openclaw" / "agents" / "trading" / "memory" / "reports"


def load_template():
    """加载Jinja2模板"""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    return env.get_template('template.html')


def load_input_data(input_path: str) -> dict:
    """加载输入数据"""
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_data(data: dict) -> list:
    """验证必填字段，返回错误列表"""
    errors = []
    required = ['title', 'content_markdown']

    for field in required:
        if field not in data or not data[field]:
            errors.append(f"缺少必填字段: {field}")

    return errors


def generate_report(input_data: dict, output_dir: Path = None) -> Path:
    """生成HTML报告"""

    # 设置默认值
    data = {
        'title': input_data.get('title', 'TradingAgent 分析报告'),
        'subtitle': input_data.get('subtitle', ''),
        'content_markdown': input_data.get('content_markdown', ''),
        'dashboard': input_data.get('dashboard', []),
        'kline_data': input_data.get('kline_data'),
        'fund_flow_data': input_data.get('fund_flow_data'),
        'alert_type': input_data.get('alert_type'),
        'alert_message': input_data.get('alert_message', ''),
        'score': input_data.get('score'),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    # 创建输出目录
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    safe_title = data['title'].replace('/', '_').replace('\\', '_')[:50]
    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_path = output_dir / filename

    # 渲染模板
    template = load_template()
    html_content = template.render(**data)

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python3 report_generator.py <输入文件.json> [输出目录]")
        print("\n示例:")
        print("  python3 report_generator.py analysis.json")
        print("  python3 report_generator.py analysis.json /tmp/reports")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR

    try:
        # 加载数据
        data = load_input_data(input_path)

        # 验证
        errors = validate_data(data)
        if errors:
            print("数据验证失败:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)

        # 生成报告
        output_path = generate_report(data, output_dir)
        print(f"报告生成成功!")
        print(f"路径: {output_path}")
        print(f"可直接在浏览器中打开查看")

    except Exception as e:
        print(f"生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
