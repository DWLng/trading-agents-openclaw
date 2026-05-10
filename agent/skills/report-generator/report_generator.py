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
    "stock_code": "600519",  // 可选，提供则自动获取K线数据
    "content_markdown": "# 公司画像\n\n这是分析内容...",
    "dashboard": [
        {"label": "目标价", "value": "2200元", "icon": "target", "value_class": "text-green-400"}
    ],
    "kline_data": null,  // ECharts K线图配置（如果提供stock_code则自动从本地数据获取）
    "fund_flow_data": null,  // ECharts 资金流配置
    "alert_type": null,  // "risk" 或 null
    "alert_message": "",
    "score": null
}
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("请先安装jinja2: pip install jinja2")
    sys.exit(1)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("警告: pandas未安装，将无法读取本地K线数据")

# 本地数据源路径
LOCAL_DATA_DIR = Path.home() / ".openclaw" / "agents" / "trading" / "data" / "daily_kline"


def normalize_stock_code(code: str) -> str:
    """标准化股票代码为6位纯数字格式"""
    if not code:
        return ""
    # 移除非数字字符
    code = ''.join(c for c in str(code) if c.isdigit())
    # 补齐6位
    return code.zfill(6)


def get_market_prefix(code: str) -> str:
    """根据股票代码判断市场前缀

    Returns:
        "sh" for 上海, "sz" for 深圳/北京
    """
    if code.startswith(('6', '5')):
        return "sh"  # 上海
    elif code.startswith(('0', '3', '4', '8')):
        return "sz"  # 深圳/北京
    return "sz"


def get_latest_data_date(stock_code: str) -> str:
    """获取本地数据的最新日期"""
    if not LOCAL_DATA_DIR.exists():
        return None

    code = normalize_stock_code(stock_code)
    market = get_market_prefix(code)
    filename = f"{market}_{code}.parquet"
    filepath = LOCAL_DATA_DIR / filename

    if not filepath.exists():
        return None

    try:
        df = pd.read_parquet(filepath)
        if df is None or df.empty:
            return None
        return df['date'].max()
    except Exception:
        return None


def fetch_kline_from_local(stock_code: str, days: int = 90) -> dict:
    """从本地parquet文件获取K线数据

    Args:
        stock_code: 6位股票代码
        days: 获取最近N天数据

    Returns:
        ECharts配置的dict对象
    """
    if not PANDAS_AVAILABLE:
        return {}

    try:
        code = normalize_stock_code(stock_code)
        if not code:
            return {}

        market = get_market_prefix(code)
        filename = f"{market}_{code}.parquet"
        filepath = LOCAL_DATA_DIR / filename

        if not filepath.exists():
            print(f"本地数据文件不存在: {filepath}")
            return {}

        df = pd.read_parquet(filepath)
        if df is None or df.empty:
            return {}

        # 获取最近N天数据
        df = df.tail(days)

        # 提取日期和OHLC数据
        dates = df['date'].tolist()
        ohlc_data = df[['open', 'close', 'low', 'high']].values.tolist()

        # 格式化日期为简单格式 (MM/DD)
        formatted_dates = []
        for d in dates:
            if isinstance(d, str) and '-' in d:
                parts = d.split('-')
                if len(parts) == 3:
                    formatted_dates.append(f"{parts[1]}/{parts[2]}")
                else:
                    formatted_dates.append(d)
            else:
                formatted_dates.append(str(d))

        return {
            "xAxis": {"data": formatted_dates},
            "series": [{
                "type": "candlestick",
                "data": ohlc_data,
                "itemStyle": {
                    "color": "#ef4444",      # 上涨红色（中国红涨）
                    "color0": "#22c55e",      # 下跌绿色（中国绿跌）
                    "borderColor": "#ef4444",
                    "borderColor0": "#22c55e"
                }
            }],
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "grid": {"left": "10%", "right": "10%", "bottom": "15%"},
            "xAxis": {
                "type": "category",
                "data": formatted_dates,
                "boundaryGap": True,
                "axisLabel": {"rotate": 45}
            },
            "yAxis": {"scale": True}
        }

    except Exception as e:
        print(f"读取本地K线数据失败: {e}")
        return {}


def fetch_kline_via_mx_api(stock_code: str, days: int = 90) -> dict:
    """通过mx-data API获取K线数据作为补充

    Args:
        stock_code: 6位股票代码
        days: 获取最近N天数据

    Returns:
        ECharts配置的dict对象
    """
    try:
        code = normalize_stock_code(stock_code)
        if not code:
            return {}

        # 判断市场
        market = "sh" if code.startswith(('6', '5')) else "sz"
        full_code = f"{code}.{'SH' if market == 'sh' else 'SZ'}"

        # 计算日期范围
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d")

        # 调用mx_data API
        mx_script = Path(__file__).parent.parent / "mx-data" / "mx_data.py"
        if mx_script.exists():
            import subprocess
            query = f"{full_code}近{ days }个交易日每日开盘价收盘价最高价最低价"
            result = subprocess.run(
                ["python3", str(mx_script), query],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "MX_APIKEY": os.environ.get("MX_APIKEY", "")}
            )
            if result.returncode == 0:
                # 解析mx_data输出，提取JSON
                # mx_data输出到文件，需要读取
                output_dir = Path.home() / ".openclaw" / "workspace" / "mx_data" / "output"
                if output_dir.exists():
                    files = list(output_dir.glob("mx_data_*.xlsx"))
                    if files:
                        # 读取最新的Excel文件
                        df = pd.read_excel(sorted(files)[-1])
                        if not df.empty:
                            # 转换格式
                            dates = df.iloc[:, 0].astype(str).tolist()[-days:]
                            ohlc_data = df.iloc[:, 1:5].values.tolist()[-days:]
                            formatted_dates = []
                            for d in dates:
                                if isinstance(d, str) and '-' in d:
                                    parts = d.split('-')
                                    if len(parts) == 3:
                                        formatted_dates.append(f"{parts[1]}/{parts[2]}")
                                    else:
                                        formatted_dates.append(d)
                                else:
                                    formatted_dates.append(str(d))
                            return {
                                "xAxis": {"data": formatted_dates},
                                "series": [{
                                    "type": "candlestick",
                                    "data": ohlc_data,
                                    "itemStyle": {
                                        "color": "#ef4444",      # 上涨红色（中国红涨）
                                        "color0": "#22c55e",      # 下跌绿色（中国绿跌）
                                        "borderColor": "#ef4444",
                                        "borderColor0": "#22c55e"
                                    }
                                }],
                                "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
                                "grid": {"left": "10%", "right": "10%", "bottom": "15%"},
                                "xAxis": {"type": "category", "data": formatted_dates, "boundaryGap": True, "axisLabel": {"rotate": 45}},
                                "yAxis": {"scale": True}
                            }
    except Exception as e:
        print(f"通过mx-data API获取K线数据失败: {e}")
    return {}


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


def generate_report_filename(input_data: dict) -> str:
    """生成纯ASCII文件名，确保URL中可完整识别为超链接

    命名格式：
    - 选股日报: stock-pick_YYYYMMDD.html
    - 个股深度分析: deep-research_{code}_{date}.html
    - 个股超级深度调研: super-deep_{code}_{date}.html
    - 个股快速分析: quick-analysis_{code}_{date}.html
    - 复盘报告: recap_YYYYMMDD.html
    - 预警通知: alert_{code}_{date}.html
    """
    stock_code = input_data.get('stock_code', '')
    report_type = input_data.get('report_type', 'report')  # 默认类型
    date_str = datetime.now().strftime('%Y%m%d')

    # 标准化股票代码
    normalized_code = normalize_stock_code(stock_code)

    # 根据类型生成文件名
    if report_type == 'stock-pick':
        return f"stock-pick_{date_str}.html"
    elif report_type == 'deep-research':
        return f"deep-research_{normalized_code}_{date_str}.html"
    elif report_type == 'super-deep':
        return f"super-deep_{normalized_code}_{date_str}.html"
    elif report_type == 'quick-analysis':
        return f"quick-analysis_{normalized_code}_{date_str}.html"
    elif report_type == 'recap':
        return f"recap_{date_str}.html"
    elif report_type == 'alert':
        return f"alert_{normalized_code}_{date_str}.html"
    else:
        # 默认格式：包含代码和日期
        if normalized_code:
            return f"report_{normalized_code}_{date_str}.html"
        else:
            return f"report_{date_str}.html"


def generate_report(input_data: dict, output_dir: Path = None) -> Path:
    """生成HTML报告"""

    # 检查是否提供了stock_code，如果有则自动获取K线数据
    stock_code = input_data.get('stock_code')
    kline_data = input_data.get('kline_data')
    fund_flow_data = input_data.get('fund_flow_data')

    # 如果提供了stock_code且kline_data为空，则自动从本地获取
    if stock_code and not kline_data:
        stock_code_normalized = normalize_stock_code(stock_code)
        if stock_code_normalized:
            print(f"检测到股票代码: {stock_code_normalized}，正在从本地获取K线数据...")

            # 优先从本地获取
            kline_data = fetch_kline_from_local(stock_code_normalized)

            if kline_data:
                latest_date = get_latest_data_date(stock_code_normalized)
                print(f"K线数据获取成功: {len(kline_data.get('series', [{}])[0].get('data', []))} 条 (本地数据最新日期: {latest_date})")

                # 检查本地数据是否太旧（超过5个交易日）
                if latest_date:
                    try:
                        latest = datetime.strptime(latest_date, "%Y-%m-%d")
                        days_diff = (datetime.now() - latest).days
                        if days_diff > 7:
                            print(f"⚠️ 本地数据较旧({days_diff}天前)，考虑使用mx-data补充...")
                            # 可以在这里调用mx-data补充最新数据，但本地数据已足够使用
                    except:
                        pass
            else:
                print("本地K线数据获取失败，尝试通过mx-data API获取...")
                # 尝试通过mx-data API获取
                kline_data = fetch_kline_via_mx_api(stock_code_normalized)
                if kline_data:
                    print("mx-data API获取成功")
                else:
                    print("mx-data API获取也失败")

    # 设置默认值
    data = {
        'title': input_data.get('title', 'TradingAgent 分析报告'),
        'subtitle': input_data.get('subtitle', ''),
        'stock_code': stock_code,
        'content_markdown': input_data.get('content_markdown', ''),
        'dashboard': input_data.get('dashboard', []),
        'kline_data': kline_data,
        'fund_flow_data': fund_flow_data,
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

    # 生成纯ASCII文件名
    filename = generate_report_filename(input_data)
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
