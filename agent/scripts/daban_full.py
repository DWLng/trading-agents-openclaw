#!/usr/bin/env python3
"""A股打板评分系统 - 2026.05.06 完整版"""
import csv, json, re, math

def load_csv(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def fl(v, d=0.0):
    try:
        return float(v) if v and v not in ('', '-') else d
    except:
        return d

def parse_amount(s):
    s = str(s).strip()
    if not s or s == '-': return 0.0
    try:
        if '亿' in s: return float(s.replace('亿',''))*1e8
        if '万' in s: return float(s.replace('万',''))*1e4
        return float(s)
    except: return 0.0

def parse_cap(s):
    s = str(s).strip()
    if not s or s == '-': return 0.0
    try:
        if '亿' in s: return float(s.replace('亿',''))
        if '万' in s: return float(s.replace('万',''))/1e4
        return float(s)/1e8
    except: return 0.0

def parse_t(s):
    if not s or s == '-': return 15,0
    try:
        p=s.split(':'); return int(p[0]),int(p[1])
    except: return 15,0

def classify(name, code, mc):
    n=str(name).strip()
    # AI/半导体/存储 8分
    ai=['通富微电','兆易创新','德明利','朗科科技','海光信息','江波龙','佰维存储',
        '北京君正','澜起科技','寒武纪','景嘉微','国科微','紫光国微','韦尔股份',
        '长电科技','华天科技','晶方科技','中芯国际','北方华创','中微公司',
        '芯原股份','恒玄科技','乐鑫科技','瑞芯微','全志科技','富瀚微',
        '圣邦股份','卓胜微','斯达半导','士兰微','华润微','纳思达',
        '至纯科技','万业企业','立昂微','沪硅产业','安集科技','拓荆科技',
        '华海清科','中科飞测','华虹半导体']
    stor=['德明利','朗科科技','江波龙','佰维存储','兆易创新','北京君正','深科技','同有科技']
    opt=['光迅科技','中际旭创','新易盛','天孚通信','光库科技','剑桥科技',
         '源杰科技','长光华芯','华工科技','光弘科技','联特科技','太辰光']
    for x in ai+stor:
        if x in n: return ('半导体/AI芯片',8)
    for x in opt:
        if x in n: return ('光通信/CPO',8)
    if any(k in n for k in ['芯','微','半导体','电子','集成电路']): return ('半导体/AI芯片',8)
    if any(k in n for k in ['光','通信']): return ('光通信/CPO',8)
    # 电力/算电 5分
    pw=['大唐发电','协鑫能科','节能风电','华电辽能','豫能控股','川润股份',
        '内蒙华电','华能国际','华电国际','国电电力','长江电力','三峡能源',
        '中国核电','龙源电力','中闽能源','太阳能','京能电力','申能股份',
        '上海电力','深圳能源','广州发展','浙江新能','江苏新能','甘肃能源',
        '银星能源','嘉泽新能','中绿电','云南能投','吉电股份','黔源电力']
    for x in pw:
        if x in n: return ('算电协同/电力',5)
    if any(k in n for k in ['电力','能源','风电','光伏']): return ('算电协同/电力',5)
    # 锂电/新能源 5分
    li=['丰元股份','天赐材料','永杉锂业','容百科技','蔚蓝锂芯',
        '赣锋锂业','天齐锂业','华友钴业','格林美','杉杉股份',
        '德方纳米','恩捷股份','星源材质','当升科技','中伟股份']
    for x in li:
        if x in n: return ('锂电/新能源',5)
    if any(k in n for k in ['锂','钴','电池','新能源']): return ('锂电/新能源',5)
    # 军工/材料 5分
    ml=['西部材料','云南锗业','博敏电子','锡华科技','航发动力','中航沈飞',
        '中航西飞','中直股份','航天彩虹','鸿远电子','火炬电子','宏达电子']
    for x in ml:
        if x in n: return ('军工/材料',5)
    if any(k in n for k in ['军工','航天','航发','兵器']): return ('军工/材料',5)
    # AI应用 8分
    aiapp=['东方国信','卓易信息','科大讯飞','中科曙光','浪潮信息','海康威视',
           '大华股份','四维图新','超图软件','用友网络','金山办公','深信服']
    for x in aiapp:
        if x in n: return ('AI应用/软件',8)
    # 国企/央企 5分
    soe=['中国长城','潍柴动力','金融街','中国石化','中国石油','中国海油',
         '中国神华','中国铝业','中国中冶','中国化学','中国中车','中国通号']
    for x in soe:
        if x in n: return ('国企改革/央企',5)
    if any(k in n for k in ['中国','中航','中核','华电','国电']): return ('国企改革/央企',3)
    # 汽车 5分
    if any(k in n for k in ['汽车','车','轮胎','发动机']): return ('汽车/零部件',5)
    # 机械 5分
    if any(k in n for k in ['重工','机械','设备','机床','电机']): return ('机械/设备',5)
    # 有色 5分
    if any(k in n for k in ['铜','铝','锌','锗','钨','稀土','矿业','黄金','白银']): return ('有色金属',5)
    # 科技 5分
    if any(k in n for k in ['科技','信息','数据','智能','数字','软件']): return ('科技/数字经济',5)
    # 消费 2分
    if any(k in n for k in ['饮品','食品','健康','医','药']): return ('消费/医药',2)
    # 建筑 2分
    if any(k in n for k in ['建筑','建工','路桥','园林']): return ('建筑/基建',2)
    # 化工 2分
    if any(k in n for k in ['化工','化学','石化','塑料']): return ('化工/材料',2)
    # 环保 2分
    if any(k in n for k in ['环保','环境','节能','水务']): return ('环保/节能',2)
    # 金融
    if any(k in n for k in ['银行','证券','保险','金融']): return ('金融',2)
    return ('其他',2)

def s_time(t):
    h,m=parse_t(t)
    if h<10: return 20
    if h==10 and m<30: return 18
    if h<11 or (h==11 and m<30): return 15
    if h<14: return 12
    if h==14 and m<30: return 10
    return 6

def s_amount(y):
    yi=y/1e8
    if yi>5: return 15
    if yi>2: return 12
    if yi>1: return 10
    if yi>0.5: return 7
    return 4

def s_board(fb):
    return 15 if fb=='首板' else 8

def s_turn(r):
    if 5<=r<=15: return 12
    if 15<r<=25: return 9
    if 3<=r<5: return 7
    if r>25: return 4
    return 5

def s_vr(v):
    v=fl(v)
    if v==0: return 4
    if 2<=v<=5: return 10
    if 1.5<=v<2: return 7
    if v>5: return 5
    return 4

def s_cap(c):
    if c==0: return 5
    if 30<=c<=100: return 10
    if 10<=c<30: return 8
    if 100<c<=300: return 7
    if c<10: return 6
    return 5

def yiziban(vr,tr):
    return fl(vr)<0.3 and fl(tr)<3

def score(row, is_zt):
    name=row.get('名称','')
    code=row.get('代码','')
    mc=row.get('市场代码简称','')
    fb_t=row.get('涨停首次封板时间 2026.05.06','15:00:00')
    fa_str=row.get('涨停封单额(元) 2026.05.06','0')
    fa=parse_amount(fa_str)
    fb_str=row.get('首板 2026.05.06','首板')
    tr=fl(row.get('换手率(%) 2026.05.06','0'))
    vr=fl(row.get('量比 2026.05.06','0'))
    cap=parse_cap(row.get('流通市值(元) 2026.05.06','0'))
    pe=fl(row.get('市盈率(动)(倍) 2026.05.06','0'))
    plate=row.get('上市板块 截至2026.05.07最新','')
    price=fl(row.get('最新价(元) 2026.05.06','0'))
    pct=fl(row.get('涨跌幅(%) 2026.05.06','0'))
    ta=parse_amount(row.get('成交额(元) 2026.05.06','0'))
    zc=0 if is_zt else fl(row.get('炸板次数(次) 2026.05.06','0'))
    concept,cs=classify(name,code,mc)
    st=s_time(fb_t)
    sa=s_amount(fa) if is_zt else 0
    sb=s_board(fb_str)
    str_=s_turn(tr)
    svr=s_vr(vr)
    sc=s_cap(cap)
    sp=4
    if cs>=8:
        h,m=parse_t(fb_t)
        if h<10: sp=10
        elif h==10 and m<30: sp=7
        elif h<12: sp=7
        else: sp=4
    pe_loss=-3 if pe<0 else 0
    yz=yiziban(vr,tr)
    yz_b=5 if yz else 0
    cy=2 if ('创业板' in plate or '科创板' in plate) else 0
    sub=st+sa+sb+str_+svr+sc+sp+cs+pe_loss+yz_b+cy
    if not is_zt:
        sub*=0.6
    total=round(sub,1)
    grade='S' if total>=85 else 'A' if total>=75 else 'B' if total>=65 else 'C' if total>=55 else 'D'
    return {
        'name':name,'code':code,'mc':mc,'price':price,'pct':pct,
        'fb_t':fb_t,'fa':fa,'fa_str':fa_str,'fb_str':fb_str,
        'tr':tr,'vr':vr,'cap':cap,'pe':pe,'plate':plate,
        'ta':ta,'zc':zc,'concept':concept,'cs':cs,
        'yz':yz,'cy':cy,'is_zt':is_zt,
        'scores':{'封板时间':st,'封单':sa,'连板':sb,'换手':str_,'量比':svr,'市值':sc,'板块':sp,'概念':cs,'PE':pe_loss,'一字板':yz_b,'20cm':cy},
        'total':total,'grade':grade
    }

def fengdan_fmt(y):
    yi=y/1e8
    if yi>=1: return f"{yi:.2f}亿"
    return f"{y/1e4:.2f}万"

def main():
    zr=load_csv('/Users/mac/Library/Application Support/openclaw/mx_data/output/mx_xuangu_今日涨停_非ST_排除北交所.csv')
    kr=load_csv('/Users/mac/Library/Application Support/openclaw/mx_data/output/mx_xuangu_今日曾涨停_现未涨停_非ST_排除北交所.csv')
    print(f"涨停:{len(zr)} 炸板:{len(kr)}")
    
    res=[]
    for r in zr: res.append(score(r,True))
    for r in kr: res.append(score(r,False))
    res.sort(key=lambda x:x['total'],reverse=True)
    
    zt=[r for r in res if r['is_zt']]
    zb=[r for r in res if not r['is_zt']]
    S=[r for r in res if r['grade']=='S']
    A=[r for r in res if r['grade']=='A']
    B=[r for r in res if r['grade']=='B']
    C=[r for r in res if r['grade']=='C']
    
    print(f"S:{len(S)} A:{len(A)} B:{len(B)} C:{len(C)}")
    
    # === Markdown ===
    md=[]
    md.append("# 📊 A股打板复盘报告")
    md.append("## 2026年5月6日（周二）")
    md.append("")
    md.append("## 一、今日市场情绪总览")
    md.append("")
    
    fb_cnt=sum(1 for r in zt if r['fb_str']=='首板')
    yz_cnt=sum(1 for r in zt if r['yz'])
    cy_cnt=sum(1 for r in zt if r['cy'])
    avg_sc=sum(r['total'] for r in zt)/max(len(zt),1)
    t早=sum(1 for r in zt if parse_t(r['fb_t'])[0]<10 or (parse_t(r['fb_t'])[0]==10 and parse_t(r['fb_t'])[1]<30))
    t午=sum(1 for r in zt if 10<=parse_t(r['fb_t'])[0]<14)
    t尾=sum(1 for r in zt if parse_t(r['fb_t'])[0]>=14)
    
    cd={}
    for r in zt:
        c=r['concept']; cd[c]=cd.get(c,0)+1
    top_c=sorted(cd.items(),key=lambda x:x[1],reverse=True)[:6]
    
    zhaban_rate=len(zb)/(len(zt)+len(zb))*100
    
    md.append(f"| 指标 | 数值 |")
    md.append(f"|------|------|")
    md.append(f"| 涨停股数（非ST/非北交所） | {len(zt)}只 |")
    md.append(f"| 炸板股数 | {len(zb)}只 |")
    md.append(f"| 炸板率 | {zhaban_rate:.1f}% |")
    md.append(f"| 首板数量 | {fb_cnt}只 |")
    md.append(f"| 连板数量 | {len(zt)-fb_cnt}只 |")
    md.append(f"| 一字板数量 | {yz_cnt}只 |")
    md.append(f"| 创业板/科创板涨停 | {cy_cnt}只 |")
    md.append(f"| 涨停股平均分 | {avg_sc:.1f}分 |")
    md.append(f"| 早盘封板(10:30前) | {t早}只({t早/len(zt)*100:.0f}%) |")
    md.append(f"| 午盘封板 | {t午}只({t午/len(zt)*100:.0f}%) |")
    md.append(f"| 尾盘封板(14:00后) | {t尾}只({t尾/len(zt)*100:.0f}%) |")
    md.append("")
    md.append("### 涨停概念分布 TOP6")
    md.append("| 概念板块 | 涨停数量 |")
    md.append("|----------|---------|")
    for c,cnt in top_c:
        md.append(f"| {c} | {cnt}只 |")
    md.append("")
    md.append("### 市场情绪研判")
    md.append("")
    if zhaban_rate>25:
        md.append(f"> ⚠️ 炸板率偏高({zhaban_rate:.1f}%)，市场封板意愿偏弱，注意追高风险。")
    else:
        md.append(f"> ✅ 炸板率正常({zhaban_rate:.1f}%)，市场封板意愿良好。")
    if t早/len(zt)>0.5:
        md.append("> 🔥 早盘封板占比高，资金抢筹积极。")
    elif t尾/len(zt)>0.35:
        md.append("> ⚠️ 尾盘封板占比较高，注意次日溢价分化。")
    if '半导体/AI芯片' in cd:
        md.append("> 🤖 半导体/AI芯片主线明确，今日强势。")
    md.append("")
    
    # === S级 ===
    md.append("## 二、S级打板标的（≥85分）")
    md.append("")
    if S:
        for r in S:
            sc=r['scores']
            md.append(f"### {r['name']}({r['mc']}{r['code']}) — {r['total']}分")
            md.append("")
            md.append(f"| 项目 | 数据 |")
            md.append(f"|------|------|")
            md.append(f"| 封板时间 | {r['fb_t']} ({sc['封板时间']}分) |")
            md.append(f"| 封单额 | {r['fa_str']} ({sc['封单']}分) |")
            md.append(f"| 连板 | {r['fb_str']} ({sc['连板']}分) |")
            md.append(f"| 换手率 | {r['tr']:.2f}% ({sc['换手']}分) |")
            md.append(f"| 量比 | {r['vr']:.2f} ({sc['量比']}分) |")
            md.append(f"| 流通市值 | {r['cap']:.1f}亿 ({sc['市值']}分) |")
            md.append(f"| 概念 | {r['concept']} ({sc['概念']}分) |")
            md.append(f"| 板块地位 | {'板块龙头' if sc['板块']==10 else '板块前排' if sc['板块']==7 else '跟风'} ({sc['板块']}分) |")
            yz_txt=" ✅ 一字板" if r['yz'] else ""
            cy_txt=" ✅ 20cm" if r['cy'] else ""
            pe_txt=" ⚠️ PE亏损" if sc['PE']<0 else ""
            md.append(f"| 特殊标记 | {yz_txt}{cy_txt}{pe_txt} |")
            md.append("")
            # 明日预测
            if r['is_zt']:
                if r['tr']>25:
                    pred="高开震荡，换手过大需谨慎"
                elif r['yz']:
                    pred="一字板开盘，溢价稳定，若开板需关注封单量"
                elif sc['封板时间']>=18:
                    pred="强势封板，次日溢价确定性高"
                elif r['cap']>100:
                    pred="市值偏大，溢价空间有限"
                else:
                    pred="良好封板，明日有望继续冲高"
            else:
                pred="炸板股，明日关注能否反包封板"
            md.append(f"> **明日预测**: {pred}")
            md.append("")
    else:
        md.append("今日无S级标的。\n")
    
    # === A级 ===
    md.append("## 三、A级打板标的（75-84分）")
    md.append("")
    if A:
        for r in A:
            sc=r['scores']
            md.append(f"### {r['name']}({r['mc']}{r['code']}) — {r['total']}分")
            md.append("")
            yz_txt="✅一字板" if r['yz'] else ""
            cy_txt="✅20cm" if r['cy'] else ""
            pe_txt="⚠️PE亏损" if sc['PE']<0 else ""
            if r['is_zt']:
                pred=f"{r['fb_t']}封板，封单{fengdan_fmt(r['fa'])}，{r['concept']}，{yz_txt}{cy_txt}{pe_txt}。明日溢价可期。"
            else:
                pred=f"炸板股，{r['zc']:.0f}次炸板，明日关注反包。"
            md.append(pred)
            md.append("")
    else:
        md.append("今日无A级标的。\n")
    
    # === B级 ===
    md.append("## 四、B级打板标的（65-74分）")
    md.append("")
    if B:
        md.append("| 股票 | 代码 | 封板时间 | 封单额 | 概念 | 换手 | 量比 | 市值 | 20cm | 一字板 | 分数 |")
        md.append("|------|------|----------|--------|------|------|------|------|------|-------|------|")
        for r in B:
            md.append(f"| {r['name']} | {r['mc']}{r['code']} | {r['fb_t']} | {r['fa_str']} | {r['concept']} | {r['tr']:.1f}% | {r['vr']:.2f} | {r['cap']:.0f}亿 | {'✅' if r['cy'] else ''} | {'✅' if r['yz'] else ''} | {r['total']} |")
        md.append("")
    else:
        md.append("今日无B级标的。\n")
    
    # === C/D级 ===
    md.append("## 五、C/D级标的（55-64分 / <55分）")
    md.append("")
    cd_res=[r for r in res if r['grade'] in ('C','D')]
    if cd_res:
        md.append(f"| 股票 | 代码 | 概念 | 分数 | 等级 | 主要问题 |")
        md.append("|------|------|------|------|------|----------|")
        for r in cd_res[:20]:
            issues=[]
            if r['scores']['封板时间']<=6: issues.append("封板太晚")
            if r['scores']['封单']<=4: issues.append("封单弱")
            if r['scores']['量比']<=4: issues.append("量比低")
            if r['scores']['PE']<0: issues.append("PE亏损")
            if not r['is_zt']: issues.append("炸板")
            md.append(f"| {r['name']} | {r['mc']}{r['code']} | {r['concept']} | {r['total']} | {r['grade']}级 | {'/'.join(issues) if issues else '综合评分低'} |")
        md.append("")
    else:
        md.append("无\n")
    
    # === 炸板分析 ===
    md.append("## 六、炸板分析")
    md.append("")
    if zb:
        md.append(f"共{len(zb)}只炸板股，详细列表：")
        md.append("")
        md.append("| 股票 | 代码 | 首次封板 | 炸板次数 | 最终涨幅 | 换手 | 量比 | 收盘价 | 炸板原因推测 | 明日反包？ |")
        md.append("|------|------|----------|---------|---------|------|------|--------|------------|----------|")
        for r in zb:
            h,m=parse_t(r['fb_t'])
            zb_reasons=[]
            if r['zc']>20: zb_reasons.append("多次炸板")
            if r['tr']>25: zb_reasons.append("换手过高")
            if r['vr']>5: zb_reasons.append("量比过大")
            if r['cap']>300: zb_reasons.append("市值过大")
            if r['scores']['封板时间']<=10: zb_reasons.append("封板太晚")
            zb_reason='; '.join(zb_reasons) if zb_reasons else '封单不足/市场分歧'
            if r['zc']<=5 and r['tr']<20 and r['scores']['封板时间']>=12:
                fanb="有望✅"
            elif r['zc']<=10 and r['tr']<25:
                fanb="观察🔍"
            else:
                fanb="谨慎❌"
            md.append(f"| {r['name']} | {r['mc']}{r['code']} | {r['fb_t']} | {r['zc']:.0f}次 | {r['pct']:.2f}% | {r['tr']:.1f}% | {r['vr']:.2f} | {r['price']:.2f} | {zb_reason} | {fanb} |")
        md.append("")
        zb_good=[r for r in zb if r['zc']<=5 and r['tr']<20 and r['scores']['封板时间']>=12]
        zb_bad=[r for r in zb if r['zc']>15 or r['tr']>30]
        md.append("**明日反包可能性较高**：")
        if zb_good:
            for r in zb_good:
                md.append(f"- {r['name']}({r['mc']}{r['code']})：炸{r['zc']:.0f}次，换手{r['tr']:.1f}%，{r['fb_t']}首次封板，明日若竞价高开+放量，有望反包")
        else:
            md.append("无特别高概率反包标的")
        md.append("")
        md.append("**需谨慎**（炸板严重，明日大概率低开或继续走弱）：")
        if zb_bad:
            for r in zb_bad:
                md.append(f"- {r['name']}({r['mc']}{r['code']})：炸{r['zc']:.0f}次，换手{r['tr']:.1f}%，{r['fb_t']}封板，主力封板意愿不足")
        md.append("")
    else:
        md.append("今日无炸板股。\n")
    
    # === 明日策略 ===
    md.append("## 七、明日打板策略建议")
    md.append("")
    
    # 强势方向
    strong_concepts=[c for c,cnt in top_c if cnt>=3]
    
    md.append("### 1. 重点关注方向")
    if strong_concepts:
        for c in strong_concepts[:3]:
            md.append(f"- **{c}**：今日涨停家数较多，明日关注龙头股竞价开盘情况")
    else:
        md.append("- 今日主线不明确，建议控制仓位，聚焦最强板块龙头")
    md.append("")
    
    # 选股标准
    md.append("### 2. 明日打板选股标准")
    md.append("")
    md.append("| 优先级 | 标准 | 说明 |")
    md.append("|--------|------|------|")
    md.append("| ⭐⭐⭐ | 竞价封单>1亿 | 封单强度决定溢价 |")
    md.append("| ⭐⭐⭐ | 10:00前封板 | 越早越强 |")
    md.append("| ⭐⭐ | 首板优先 | 首板溢价最高 |")
    md.append("| ⭐⭐ | 换手5-15% | 健康换手不易炸板 |")
    md.append("| ⭐⭐ | 量比2-5 | 资金参与活跃 |")
    md.append("| ⭐ | 流通市值30-100亿 | 中小盘弹性最佳 |")
    md.append("| ⭐ | 概念主线 | 聚焦今日强势板块 |")
    md.append("")
    
    # 风险提示
    md.append("### 3. 风险提示")
    md.append("")
    zhaban_high=[r for r in zb if r['zc']>15]
    if zhaban_high:
        md.append(f"⚠️ 今日{zhaban_high[0]['name']}等{zhaban_high[0]['zc']:.0f}次炸板股，明日低开概率大，切勿盲目抄底。")
    yz_zt=[r for r in zt if r['yz']]
    if yz_zt:
        md.append(f"⚠️ 今日{yz_zt[0]['name']}等{len(yz_zt)}只一字板，明日若开板需观察封单是否快速回补。")
    md.append("⚠️ 市场炸板率偏高时，追高位板需格外谨慎，优先选择早盘强势封板标的。")
    md.append("")
    
    md.append("---")
    md.append(f"*报告生成时间: 2026-05-06 收盘后 | 数据来源: 东方财富妙想*")
    
    # === JSON Summary ===
    json_out=[]
    for r in res:
        sc=r['scores']
        if r['grade'] in ('S','A','B'):
            if r['is_zt']:
                if r['tr']>25:
                    logic="换手过高，封板不稳，溢价有限"
                elif r['yz']:
                    logic=f"一字板，{r['concept']}，封单{fengdan_fmt(r['fa'])}，{r['fb_t']}封板"
                elif sc['封板时间']>=18:
                    logic=f"早盘强势封板，{r['concept']}，封单{fengdan_fmt(r['fa'])}，{r['fb_t']}封板"
                elif sc['封板时间']>=15:
                    logic=f"午前封板，{r['concept']}，封单{fengdan_fmt(r['fa'])}，{r['fb_t']}封板"
                else:
                    logic=f"{r['concept']}，{r['fb_t']}封板，换手{r['tr']:.1f}%"
            else:
                logic=f"炸板{sc['PE']:.0f}次，关注明日反包"
            
            if r['is_zt']:
                if r['tr']>25:
                    pred="明日高开震荡，谨慎持有"
                elif r['yz']:
                    pred="一字板开盘，高溢价，若开板关注封单回补"
                elif sc['封板时间']>=18:
                    pred="强势板，明日溢价确定，10cm目标+5%以上"
                else:
                    pred="良好板，明日溢价+3~5%"
            else:
                if r['zc']<=5:
                    pred="关注竞价，若高开+放量，可博弈反包"
                else:
                    pred="谨慎，炸板次数多，反包难度大"
        else:
            logic=f"{r['concept']}，综合评分低"
            pred="不参与"
        
        json_out.append({
            "code": r['mc']+r['code'],
            "name": r['name'],
            "score": r['total'],
            "grade": r['grade'],
            "concept": r['concept'],
            "logic": logic,
            "pred": pred
        })
    
    # Save
    md_text='\n'.join(md)
    with open('/Users/mac/.openclaw/agents/trading/memory/2026-05-06-daban-review.md','w',encoding='utf-8') as f:
        f.write(md_text)
    print("Markdown saved.")
    
    with open('/Users/mac/.openclaw/agents/trading/memory/2026-05-06-daban-summary.json','w',encoding='utf-8') as f:
        json.dump(json_out,f,ensure_ascii=False,indent=2)
    print("JSON saved.")
    
    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"涨停: {len(zt)}只, 炸板: {len(zb)}只, 炸板率: {zhaban_rate:.1f}%")
    print(f"S级: {len(S)}, A级: {len(A)}, B级: {len(B)}, C级: {len(C)}")
    print(f"首板: {fb_cnt}, 连板: {len(zt)-fb_cnt}, 一字板: {yz_cnt}, 20cm: {cy_cnt}")
    print(f"涨停平均分: {avg_sc:.1f}")
    print(f"TOP概念: {top_c}")
    print(f"\nS级标的:")
    for r in S:
        print(f"  {r['name']}({r['mc']}{r['code']}) {r['total']}分 {r['concept']}")
    print(f"\nA級标的:")
    for r in A:
        print(f"  {r['name']}({r['mc']}{r['code']}) {r['total']}分 {r['concept']}")

if __name__=='__main__':
    main()
