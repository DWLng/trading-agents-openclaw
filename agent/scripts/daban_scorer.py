#!/usr/bin/env python3
"""
A股打板评分系统 - 2026.05.06
读取涨停/炸板CSV数据，按100分制评分，生成复盘报告和JSON摘要
"""

import csv
import json
import re
import math
from datetime import datetime, time

# ===================== 数据加载 =====================

def load_csv(filepath):
    """加载CSV文件，处理BOM"""
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def safe_float(val, default=0.0):
    """安全转换浮点数"""
    if val is None or val == '' or val == '-':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_int(val, default=0):
    """安全转换整数"""
    if val is None or val == '' or val == '-':
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default

def parse_amount(amount_str):
    """
    解析金额字符串: "7848.34万" -> 78483400, "11.71亿" -> 1171000000
    返回float单位元
    """
    if not amount_str or amount_str == '-':
        return 0.0
    amount_str = str(amount_str).strip()
    try:
        if '亿' in amount_str:
            return float(amount_str.replace('亿', '')) * 1e8
        elif '万' in amount_str:
            return float(amount_str.replace('万', '')) * 1e4
        else:
            return float(amount_str)
    except (ValueError, TypeError):
        return 0.0

def parse_market_cap(cap_str):
    """解析市值: "109.70亿" -> 109.70 (亿元)"""
    if not cap_str or cap_str == '-':
        return 0.0
    cap_str = str(cap_str).strip()
    try:
        if '亿' in cap_str:
            return float(cap_str.replace('亿', ''))
        elif '万' in cap_str:
            return float(cap_str.replace('万', '')) / 10000
        else:
            return float(cap_str) / 1e8
    except (ValueError, TypeError):
        return 0.0

def parse_time_str(time_str):
    """解析时间字符串 '14:53:53' -> (14, 53)"""
    if not time_str or time_str == '-':
        return (15, 0)  # 默认最晚
    try:
        parts = time_str.split(':')
        h, m = int(parts[0]), int(parts[1])
        return (h, m)
    except (ValueError, TypeError, IndexError):
        return (15, 0)

# ===================== 板块/概念判断 =====================

def classify_concept(name, code, market_code):
    """根据股票名称和代码判断所属概念板块"""
    name = str(name).strip()
    code = str(code).strip()
    
    # AI算力/半导体存储 - 最强主线 (8分)
    ai_chip_names = ['通富微电', '兆易创新', '德明利', '朗科科技', '海光信息', '江波龙', '佰维存储',
                     '北京君正', '澜起科技', '寒武纪', '景嘉微', '国科微', '紫光国微', '韦尔股份',
                     '长电科技', '华天科技', '晶方科技', '中芯国际', '北方华创', '中微公司',
                     '芯原股份', '恒玄科技', '乐鑫科技', '瑞芯微', '全志科技', '富瀚微',
                     '圣邦股份', '卓胜微', '斯达半导', '士兰微', '华润微', '纳思达',
                     '至纯科技', '万业企业', '立昂微', '沪硅产业', '安集科技']
    
    storage_names = ['德明利', '朗科科技', '江波龙', '佰维存储', '兆易创新', '北京君正',
                     '深科技', '同有科技', '协创数据', '大为股份']
    
    opto_names = ['光迅科技', '中际旭创', '新易盛', '天孚通信', '光库科技', '剑桥科技',
                  '源杰科技', '长光华芯', '华工科技', '光弘科技', '联特科技', '太辰光',
                  '博创科技', '腾景科技', '德科立', '铭普光磁', '华脉科技']
    
    # 检查AI/半导体
    for n in ai_chip_names:
        if n in name:
            return ('半导体/AI芯片', 8)
    
    for n in storage_names:
        if n in name:
            return ('存储芯片', 8)
    
    # 检查光通信/CPO
    for n in opto_names:
        if n in name:
            return ('光通信/CPO', 8)
    
    # AI芯片相关关键词
    if any(kw in name for kw in ['芯', '微', '半导体', '电子', '集成电路']):
        return ('半导体/AI芯片', 8)
    
    if any(kw in name for kw in ['光', '通信']):
        return ('光通信/CPO', 8)
    
    # 算电协同/电力 (5分)
    power_names = ['大唐发电', '协鑫能科', '节能风电', '华电辽能', '豫能控股', '川润股份',
                   '内蒙华电', '华能国际', '华电国际', '国电电力', '长江电力', '三峡能源',
                   '中国核电', '龙源电力', '中闽能源', '太阳能', '京能电力', '申能股份',
                   '上海电力', '深圳能源', '广州发展', '浙江新能', '江苏新能', '甘肃能源',
                   '银星能源', '嘉泽新能', '中绿电', '云南能投', '吉电股份', '黔源电力',
                   '桂冠电力', '乐山电力', '西昌电力', '明星电力', '文山电力', '涪陵电力']
    for n in power_names:
        if n in name:
            return ('算电协同/电力', 5)
    
    if any(kw in name for kw in ['电力', '能源', '风电', '光伏', '核', '能']):
        return ('算电协同/电力', 5)
    
    # 锂电/新能源 (5分)
    lithium_names = ['丰元股份', '天赐材料', '永杉锂业', '容百科技', '蔚蓝锂芯',
                     '赣锋锂业', '天齐锂业', '华友钴业', '格林美', '杉杉股份',
                     '德方纳米', '恩捷股份', '星源材质', '当升科技', '中伟股份',
                     '雅化集团', '融捷股份', '盛新锂能', '西藏矿业', '西藏珠峰']
    for n in lithium_names:
        if n in name:
            return ('锂电/新能源', 5)
    
    if any(kw in name for kw in ['锂', '钴', '镍', '电池', '新能源']):
        return ('锂电/新能源', 5)
    
    # 军工/材料 (5分)
    military_names = ['西部材料', '云南锗业', '博敏电子', '锡华科技',
                      '航发动力', '中航沈飞', '中航西飞', '中直股份', '航天彩虹',
                      '鸿远电子', '火炬电子', '宏达电子', '振华科技',
                      '宝钛股份', '西部超导', '菲利华', '光威复材']
    for n in military_names:
        if n in name:
            return ('军工/材料', 5)
    
    if any(kw in name for kw in ['军工', '航天', '航发', '兵器', '光电', '材料']):
        return ('军工/材料', 5)
    
    # 建筑/基建 (2分)
    build_names = ['金螳螂', '中天精装', '诚邦股份', '园林股份',
                   '中国建筑', '中国交建', '中国铁建', '中国中铁', '中国电建',
                   '隧道股份', '上海建工', '四川路桥', '山东路桥']
    for n in build_names:
        if n in name:
            return ('建筑/基建', 2)
    
    # 消费/食品 (2分)
    consume_names = ['养元饮品', '奥康国际', '美年健康',
                     '贵州茅台', '五粮液', '伊利股份', '海天味业', '金龙鱼',
                     '双汇发展', '安井食品', '绝味食品', '三只松鼠']
    for n in consume_names:
        if n in name:
            return ('消费/食品', 2)
    
    # AI应用/软件 (8分)
    ai_app_names = ['东方国信', '卓易信息', '科大讯飞', '中科曙光', '浪潮信息',
                    '海康威视', '大华股份', '四维图新', '超图软件', '用友网络',
                    '金山办公', '深信服', '奇安信', '启明星辰', '绿盟科技',
                    '中科创达', '天融信', '安恒信息']
    for n in ai_app_names:
        if n in name:
            return ('AI应用/软件', 8)
    
    # 国企改革/央企 (5分)
    soe_names = ['中国长城', '大唐发电', '潍柴动力', '金融街',
                 '中国石化', '中国石油', '中国海油', '中国神华', '中国铝业',
                 '中国中冶', '中国化学', '中国中车', '中国通号', '中国中铁',
                 '中国铁建', '中国交建', '中国电建', '中国核建', '中国建筑',
                 '中国船舶', '中国重工', '中船防务']
    for n in soe_names:
        if n in name:
            return ('国企改革/央企', 5)
    
    if any(kw in name for kw in ['中国', '中航', '中核', '中铁', '中建', '中交', '中冶', '华电', '国电']):
        return ('国企改革/央企', 3)
    
    # 医药 (2分)
    if any(kw in name for kw in ['医药', '药', '医', '生物', '基因', '健康', '华仁']):
        return ('医药/生物', 2)
    
    # 汽车 (5分)
    if any(kw in name for kw in ['汽车', '车', '轮胎', '发动机', '变速', '底盘']):
        return ('汽车/零部件', 5)
    
    # 机械/设备 (5分)
    if any(kw in name for kw in ['重工', '机械', '设备', '装备', '制造', '机床', '电机']):
        return ('机械/设备', 5)
    
    # 化工 (2分)
    if any(kw in name for kw in ['化工', '化学', '石化', '材料', '塑料', '橡胶', '纤维']):
        return ('化工/材料', 2)
    
    # 环保 (2分)
    if any(kw in name for kw in ['环保', '环境', '节能', '水务', '清洁']):
        return ('环保/节能', 2)
    
    # 房地产 (2分)
    if any(kw in name for kw in ['地产', '房产', '置业', '开发', '城建', '城建', '城投']):
        return ('房地产', 2)
    
    # 农业 (2分)
    if any(kw in name for kw in ['农业', '农牧', '种业', '林业', '渔业', '养殖']):
        return ('农业', 2)
    
    # 金融
    if any(kw in name for kw in ['银行', '证券', '保险', '金融', '期货']):
        return ('金融', 2)
    
    # 有色金属
    if any(kw in name for kw in ['铜', '铝', '锌', '锗', '钨', '稀土', '矿业', '金属', '黄金', '白银']):
        return ('有色金属', 5)
    
    # 科技/数字经济 (5分)
    if any(kw in name for kw in ['科技', '信息', '数据', '智能', '数字', '软件', '网络', '互联']):
        return ('科技/数字经济', 5)
    
    # 其他
    return ('其他', 2)


# ===================== 评分函数 =====================

def score_board_time(fengban_time_str):
    """
    封板时间评分 (20分)
    <10:00=20, 10-10:30=18, 10:30-11:30=15, 13-14:00=12, 14-14:30=10, >14:30=6
    """
    h, m = parse_time_str(fengban_time_str)
    minutes = h * 60 + m
    
    if h < 10:
        return 20
    elif h == 10 and m < 30:
        return 18
    elif h == 10 or (h == 11 and m < 30):
        return 15
    elif h < 14 or (h == 13):
        return 12
    elif h == 14 and m < 30:
        return 10
    else:
        return 6

def score_fengdan_amount(amount_yuan):
    """
    封单强度评分 (15分)
    >5亿=15, 2-5亿=12, 1-2亿=10, 0.5-1亿=7, <0.5亿=4
    """
    yi = amount_yuan / 1e8
    if yi > 5:
        return 15
    elif yi > 2:
        return 12
    elif yi > 1:
        return 10
    elif yi > 0.5:
        return 7
    else:
        return 4

def score_board_stage(first_board_str):
    """
    连板阶段评分 (15分)
    首板=15, 2板=10, 3板=7, 4板+=4
    CSV中"首板"=首板, "-"=非首板(连板), 默认为2-3板=8分
    """
    if first_board_str == '首板':
        return 15
    else:
        return 8  # 非首板，取2-3板中间值

def score_turnover_rate(turnover_rate):
    """
    换手健康度 (12分)
    5-15%=12, 15-25%=9, 3-5%=7, >25%=4, <3%=5(一字板加分)
    """
    rate = safe_float(turnover_rate)
    if 5 <= rate <= 15:
        return 12
    elif 15 < rate <= 25:
        return 9
    elif 3 <= rate < 5:
        return 7
    elif rate > 25:
        return 4
    else:  # <3%
        return 5  # 一字板加分

def score_volume_ratio(vol_ratio):
    """
    量比评分 (10分)
    2-5=10, 1.5-2=7, >5=5, <1.5=4
    """
    ratio = safe_float(vol_ratio)
    if ratio == 0:
        return 4
    if 2 <= ratio <= 5:
        return 10
    elif 1.5 <= ratio < 2:
        return 7
    elif ratio > 5:
        return 5
    elif ratio < 1.5:
        return 4

def score_float_market_cap(cap_yi):
    """
    流通市值 (10分)
    30-100亿=10, 10-30亿=8, 100-300亿=7, <10亿=6, >300亿=5
    """
    if cap_yi == 0:
        return 5
    if 30 <= cap_yi <= 100:
        return 10
    elif 10 <= cap_yi < 30:
        return 8
    elif 100 < cap_yi <= 300:
        return 7
    elif cap_yi < 10:
        return 6
    else:  # >300亿
        return 5

def check_yiziban(vol_ratio, turnover_rate):
    """检测一字板: 量比<0.3且换手<3%"""
    return safe_float(vol_ratio) < 0.3 and safe_float(turnover_rate) < 3

def check_pe_loss(pe_str):
    """检测PE亏损"""
    pe = safe_float(pe_str)
    return pe < 0

def check_chuangyeban(market_plate_str):
    """检测是否为创业板(20cm)"""
    if not market_plate_str:
        return False
    return '创业板' in str(market_plate) or '科创板' in str(market_plate)

# ===================== 板块地位判断 =====================

def score_board_position(concept, concept_score, fengban_time_str, concept_group):
    """
    板块地位 (10分)
    板块龙头/最先封板=10, 板块前排=7, 跟风=4
    concept_group: list of (name, time_str) within same concept
    """
    if not concept_group:
        return 4
    
    # Sort by封板时间
    sorted_group = sorted(concept_group, key=lambda x: parse_time_str(x[1]))
    
    # If this stock is first to封板 in its group, it's the leader
    h, m = parse_time_str(fengban_time_str)
    first_h, first_m = parse_time_str(sorted_group[0][1])
    
    if (h, m) == (first_h, first_m) and len(sorted_group) >= 2:
        return 10  # 板块龙头
    elif len(sorted_group) <= 3:
        return 7  # 小板块前排
    else:
        # Among top 3
        my_idx = sum(1 for _, t in sorted_group if parse_time_str(t) <= (h, m))
        if my_idx <= 3:
            return 7  # 板块前排
        else:
            return 4  # 跟风


# ===================== 主评分函数 =====================

def score_stock(row, is_zhangting=True, concept_groups=None):
    """
    对单只股票打分
    Returns: (total_score, detail_dict)
    """
    name = row.get('名称', '')
    code = row.get('代码', '')
    market_code = row.get('市场代码简称', '')
    
    # 基础数据
    fengban_time = row.get('涨停首次封板时间 2026.05.06', '15:00:00')
    fengdan_amount_str = row.get('涨停封单额(元) 2026.05.06', '0')
    fengdan_amount = parse_amount(fengdan_amount_str)
    first_board = row.get('首板 2026.05.06', '首板')
    turnover_rate = safe_float(row.get('换手率(%) 2026.05.06', '0'))
    vol_ratio = safe_float(row.get('量比 2026.05.06', '0'))
    float_market_cap_str = row.get('流通市值(元) 2026.05.06', '0')
    float_market_cap_yi = parse_market_cap(float_market_cap_str)
    pe_str = row.get('市盈率(动)(倍) 2026.05.06', '0')
    market_plate = row.get('上市板块 截至2026.05.07最新', '')
    price = safe_float(row.get('最新价(元) 2026.05.06', '0'))
    pct_chg = safe_float(row.get('涨跌幅(%) 2026.05.06', '0'))
    total_amount_str = row.get('成交额(元) 2026.05.06', '0')
    total_amount = parse_amount(total_amount_str)
    zhaban_count = safe_int(row.get('炸板次数(次) 2026.05.06', '0'))
    
    # 概念分类
    concept_name, concept_strength = classify_concept(name, code, market_code)
    
    # ===== 一级指标 =====
    score_time = score_board_time(fengban_time)
    score_fengdan = score_fengdan_amount(fengdan_amount) if is_zhangting else 0
    score_board = score_board_stage(first_board)
    
    # ===== 二级指标 =====
    score_turnover = score_turnover_rate(turnover_rate)
    score_volratio = score_volume_ratio(vol_ratio)
    score_floatcap = score_float_market_cap(float_market_cap_yi)
    
    # ===== 三级指标 =====
    # 板块地位 - simplified: if first to封板 in concept, get higher score
    score_position = 4  # default跟风
    if concept_strength >= 8:
        # Check if this stock封板 earlier than most
        h, m = parse_time_str(fengban_time)
        minutes = h * 60 + m
        if h < 10:
            score_position = 10
        elif h == 10 and m < 30:
            score_position = 7
        elif minutes < 11 * 60 + 30:
            score_position = 7
        else:
            score_position = 4
    
    # 概念强度
    score_concept = concept_strength
    
    # ===== 加减分 =====
    bonus_pe = -3 if check_pe_loss(pe_str) else 0
    is_yiziban = check_yiziban(vol_ratio, turnover_rate)
    bonus_yiziban = 5 if is_yiziban else 0
    is_chuangye = check_chuangyeban(market_plate)
    bonus_chuangye = 2 if is_chuangye else 0
    
    # 炸板惩罚: 基础分×0.6
    is_zhaban = not is_zhangting
    
    # 计算总分
    subtotal = (score_time + score_fengdan + score_board + 
                score_turnover + score_volratio + score_floatcap +
                score_position + score_concept +
                bonus_pe + bonus_yiziban + bonus_chuangye)
    
    if is_zhaban:
        # 炸板分 = 基础分打分(但封单用0) × 0.6
        subtotal = subtotal * 0.6
    
    total = round(subtotal, 1)
    
    # 等级
    if total >= 85:
        grade = 'S'
    elif total >= 75:
        grade = 'A'
    elif total >= 65:
        grade = 'B'
    elif total >= 55:
        grade = 'C'
    else:
        grade = 'D'
    
    detail = {
        'name': name,
        'code': code,
        'market_code': market_code,
        'price': price,
        'pct_chg': pct_chg,
        'fengban_time': fengban_time,
        'fengdan_amount_yuan': fengdan_amount,
        'fengdan_amount_str': fengdan_amount_str,
        'first_board': first_board,
        'turnover_rate': turnover_rate,
        'vol_ratio': vol_ratio,
        'float_market_cap_yi': float_market_cap_yi,
        'pe': safe_float(pe_str),
        'market_plate': market_plate,
        'total_amount_yuan': total_amount,
        'concept': concept_name,
        'concept_strength': concept_strength,
        'is_yiziban': is_yiziban,
        'is_chuangye': is_chuangye,
        'is_zhaban': is_zhaban,
        'zhaban_count': zhaban_count,
        'scores': {
            '封板时间': score_time,
            '封单强度': score_fengdan,
            '连板阶段': score_board,
            '换手健康度': score_turnover,
            '量比': score_volratio,
            '流通市值': score_floatcap,
            '板块地位': score_position,
            '概念强度': score_concept,
            'PE亏损': bonus_pe,
            '一字板加分': bonus_yiziban,
            '创业板加分': bonus_chuangye,
        },
        'total_score': total,
        'grade': grade
    }
    
    return total, detail

# ===================== 主程序 =====================

def main():
    # 读取数据
    zhangting_path = '/Users/mac/Library/Application Support/openclaw/mx_data/output/mx_xuangu_今日涨停_非ST_排除北交所.csv'
    zhaban_path = '/Users/mac/Library/Application Support/openclaw/mx_data/output/mx_xuangu_今日曾涨停_现未涨停_非ST_排除北交所.csv'
    
    zhangting_rows = load_csv(zhangting_path)
    zhaban_rows = load_csv(zhaban_path)
    
    print(f"涨停股数: {len(zhangting_rows)}, 炸板股数: {len(zhaban_rows)}")
    
    # 评分
    all_results = []
    for row in zhangting_rows:
        score, detail = score_stock(row, is_zhangting=True)
        all_results.append(detail)
    
    for row in zhaban_rows:
        score, detail = score_stock(row, is_zhangting=False)
        all_results.append(detail)
    
    # 按分数排序
    all_results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # 分类
    s_grade = [r for r in all_results if r['grade'] == 'S']
    a_grade = [r for r in all_results if r['grade'] == 'A']
    b_grade = [r for r in all_results if r['grade'] == 'B']
    c_grade = [r for r in all_results if r['grade'] == 'C']
    d_grade = [r for r in all_results if r['grade'] == 'D']
    
    zhangting_only = [r for r in all_results if not r['is_zhaban']]
    zhaban_only = [r for r in all_results if r['is_zhaban']]
    
    print(f"\nS级: {len(s_grade)}, A级: {len(a_grade)}, B级: {len(b_grade)}, C级: {len(c_grade)}, D级: {len(d_grade)}")
    
    # ===================== 生成Markdown报告 =====================
    
    report = []
    report.append("# 📊 A股打板复盘报告")
    report.append(f"## 2026年5月6日（周二）")
    report.append("")
    
    # ---- 市场情绪总览 ----
    report.append("## 一、今日市场情绪总览")
    report.append("")
    
    # 统计
    first_board_count = sum(1 for r in zhangting_only if r['first_board'] == '首板')
    multi_board_count = len(zhangting_only) - first_board_count
    yiziban_count = sum(1 for r in zhangting_only if r['is_yiziban'])
    chuangye_count = sum(1 for r in zhangting_only if r['is_chuangye'])
    avg_score = sum(r['total_score'] for r in zhangting_only) / max(len(zhangting_only), 1)
    
    # 概念分布
    concept_dist = {}
    for r in zhangting_only:
        c = r['concept']
        concept_dist[c] = concept_dist.get(c, 0) + 1
    top_concepts = sorted(concept_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 时间分布
    time_dist = {'早盘(<10:30)': 0, '午盘(10:30-14:00)': 0, '尾盘(>14:00)': 0}
    for r in zhangting_only:
        h, m = parse_time_str(r['fengban_time'])
        if h < 10 or (h == 10 and m < 30):
            time_dist['早盘(<10:30)'] += 1
        elif h < 14:
            time_dist['午盘(10:30-14:00)'] += 1
        else:
            time_dist['尾盘(>14:00)'] += 1
    
    report.append(f"| 指标 | 数值 |")
    report.append(f"|------|------|")
    report.append(f"| 涨停股数（非ST/非北交所） | {len(zhangting_only)}只 |")
    report.append(f"| 炸板股数 | {len(zhaban_only)}只 |")
    report.append(f"| 炸板率 | {len(zhaban_only)}/{(len(zhangting_only)+len(zhaban_only))} = {len(zhaban_only)/(len(zhangting_only)+len(zhaban_only))*100:.1f}% |")
    report.append(f"| 首板数量 | {first_board_count}只 |")
    report.append(f"| 连板数量 | {multi_board_count}只 |")
    report.append(f"| 一字板数量 | {yiziban_count}只 |")
    report.append(f"| 创业板/科创板涨停 | {chuangye_count}只 |")
    report.append(f"| 涨停股平均分 | {avg_score:.1f}分 |")
    report.append(f"| 早盘封板(10:30前) | {time_dist['早盘(<10:30)']}只 |")
    report.append(f"| 午盘封板(10:30-14:00) | {time_dist['午盘(10:30-14:00)']}只 |")
    report.append(f"| 尾盘封板(14:00后) | {time_dist['尾盘(>14:00)']}只 |")
    report.append("")
    
    report.append("### 涨停概念分布 TOP5")
    report.append("")
    report.append("| 概念板块 | 涨停数量 |")
    report.append("|----------|---------|")
    for c, cnt in top_concepts:
        report.append(f"| {c} | {cnt}只 |")
    report.append("")
    
    report.append("### 市场情绪研判")
    report.append("")
    if len(zhaban_only) / max(len(zhangting_only) + len(zhaban_only), 1) > 0.25:
        report.append("> ⚠️ 炸板率偏高({:.1f}%)，市场封板意愿偏弱，注意追高风险。".format(
            len(zhaban_only)/(len(zhangting_only)+len(zhaban_only))*100))
    else:
        report.append("> ✅ 炸板率正常({:.1f}%)，市场封板意愿良好，打板环境友好。".format(
            len(zhaban_only)/(len(zhangting_only)+len(zhaban_only))*100))
    
    if time_dist['早盘(<10:30)'] >= 40:
        report.append("> 🔥 早盘封板占比高，资金抢筹积极，市场做多情绪旺盛。")
    elif time_dist['尾盘(>14:00)'] >= 30:
        report.append("> ⚠️ 尾盘封板占比较高，部分资金偏谨慎，注意次日溢价分化。")
    
    if '半导体/AI芯片' in concept_dist