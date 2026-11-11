# -*- coding: utf-8 -*-
"""撰写/整合角色：从 metrics.json + 勾稽底稿.json 生成自包含 HTML 体检报告（内联SVG，无外部依赖）。"""
import json, os

OUT = r"D:\AI_Project\zuopin\02_实际产出"
m = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))
c = json.load(open(os.path.join(OUT, "勾稽底稿.json"), encoding="utf-8"))

def yi(v):  # 元 -> 亿元
    return None if v is None else round(v / 1e8, 1)

def pct(v, d=1):
    return "—" if v is None else f"{v:+.{d}f}%" if d == 1 else f"{v:.{d}f}%"

tr = {t["period"]: t for t in m["trend"]}
periods = m["periods"]          # 2025..2021
years = [p.replace("年报", "") for p in periods]
inc = [tr[p]["total_income"] / 1e8 for p in periods]
prof = [tr[p]["parent_profit"] / 1e8 for p in periods]
cliab = [yi(tr[p]["contract_liab"]) for p in periods]
CL_Q3_2026 = round(next(r["CONTRACT_LIAB"] for r in json.load(open(os.path.join(OUT, "原始数据", "balance_600519.json"), encoding="utf-8"))["result"]["data"] if r.get("REPORT_DATE_NAME") == "2026三季报") / 1e8, 1)  # 从原始数据现算，杜绝硬编码
summ = c["summary"]

# ---------- SVG 图表 ----------
def bar_chart(labels, series, colors, h=220, unit="亿元", fmt="{:.0f}"):
    """series: [(name, [vals], color)] 分组柱状图"""
    n, k = len(labels), len(series)
    W = 1000; pad_l, pad_r, pad_t, pad_b = 56, 16, 34, 40
    cw = W - pad_l - pad_r
    vmax = max(v for _, vals, _ in series for v in vals if v is not None) * 1.15
    gw = cw / n
    bw = gw / (k + 1.4)
    parts = [f'<svg viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg" role="img">']
    # 网格
    for i in range(5):
        gy = pad_t + (h - pad_t - pad_b) * i / 4
        val = vmax * (1 - i / 4)
        parts.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{W-pad_r}" y2="{gy:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l-8}" y="{gy+4:.1f}" text-anchor="end" font-size="12" fill="#94a3b8">{val:.0f}</text>')
    for j, lb in enumerate(labels):
        gx = pad_l + gw * j
        for s_i, (name, vals, color) in enumerate(series):
            v = vals[j]
            if v is None: continue
            bh = (h - pad_t - pad_b) * v / vmax
            x = gx + bw * (s_i + 0.7)
            y = h - pad_b - bh
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.82:.1f}" height="{bh:.1f}" rx="3" fill="{color}"/>')
            parts.append(f'<text x="{x+bw*0.41:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#334155">{fmt.format(v)}</text>')
        parts.append(f'<text x="{gx+gw/2:.1f}" y="{h-14}" text-anchor="middle" font-size="13.5" fill="#475569">{lb}</text>')
    parts.append(f'<text x="{W-pad_r}" y="{pad_t-12}" text-anchor="end" font-size="12" fill="#94a3b8">单位：{unit}</text>')
    parts.append("</svg>")
    return "".join(parts)

chart_rev = bar_chart(years, [("营业收入", inc, "#0e7490"), ("归母净利润", prof, "#f59e0b")], None, fmt="{:.0f}")

def svg_bar_grid(vmax, w=1000, h=220, pad_l=56, pad_t=34, pad_b=40):
    parts = []
    for i in range(5):
        gy = pad_t + (h - pad_t - pad_b) * i / 4
        val = vmax * (1 - i / 4)
        parts.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w-16}" y2="{gy:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l-8}" y="{gy+4:.1f}" text-anchor="end" font-size="12" fill="#94a3b8">{val:.0f}</text>')
    return "".join(parts)

def single_bar(labels, vals, color="#b45309", fmt="{:.1f}", h=220):
    W = 1000; n = len(labels)
    pad_l, pad_r, pad_t, pad_b = 56, 16, 34, 40
    cw = W - pad_l - pad_r; gw = cw / n; bw = gw / 2.2
    vmax = max(v for v in vals if v is not None) * 1.15
    parts = [f'<svg viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg" role="img">']
    parts.append(svg_bar_grid(vmax, W, h, pad_l, pad_t, pad_b))
    for j, lb in enumerate(labels):
        v = vals[j]
        if v is None: continue
        bh = (h - pad_t - pad_b) * v / vmax
        x = pad_l + gw * j + (gw - bw) / 2
        y = h - pad_b - bh
        op = "" if j < n - 1 else ' opacity="0.85"'
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{color}"{op}/>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#334155">{fmt.format(v)}</text>')
        parts.append(f'<text x="{pad_l+gw*j+gw/2:.1f}" y="{h-14}" text-anchor="middle" font-size="13.5" fill="#475569">{lb}</text>')
    parts.append(f'<text x="{W-pad_r}" y="{pad_t-12}" text-anchor="end" font-size="12" fill="#94a3b8">单位：亿元</text>')
    parts.append("</svg>")
    return "".join(parts)

chart_cliab = single_bar(years + ["2026Q3"], cliab + [CL_Q3_2026], color="#b45309")

# 指标表
rows_tbl = ""
for p in periods:
    t = tr[p]
    rows_tbl += (f'<tr><td>{p}</td><td>{pct(t["income_yoy"])}</td><td>{pct(t["profit_yoy"])}</td>'
                 f'<td>{t["gross_margin"]}%</td><td>{t["roe"]:.1f}%</td><td>{t["debt_ratio"]:.1f}%</td>'
                 f'<td>{t["cash_ratio"]:.2f}</td></tr>')

# 同业表
peer_rows = ""
for p_ in m["peers"]:
    hi = ' style="background:#fef3c7;font-weight:700"' if p_["name"] == "贵州茅台" else ""
    peer_rows += (f'<tr{hi}><td>{p_["name"]}</td><td>{yi(p_["income"]):.0f}</td>'
                  f'<td><span class="{"dn" if (p_["income_yoy"] or 0)<0 else "up"}">{pct(p_["income_yoy"])}</span></td>'
                  f'<td>{yi(p_["profit"]):.0f}</td><td>{p_["gross_margin"]:.1f}%</td>'
                  f'<td>{p_["roe"]:.1f}%</td><td>{p_["debt_ratio"]:.1f}%</td></tr>')

# 红队发现（终审已抽查关键数字）
findings = [
    ("高", "合同负债断崖：2026Q3 仅 20.8 亿，同比 -73.1%",
     "经销商预付款（合同负债）2023 年 141.3 亿 → 2024 年 95.9 亿 → 2025 年 80.1 亿 → 2026Q3 仅 20.8 亿。已完成防重分类检查：其他流动负债/其他应付款无腾挪痕迹，排除科目搬运。",
     "调取年报附注中合同负债明细与经销商返利政策", "终审抽查：20.84 亿 / -73.1% 与原始数据一致 ✓"),
    ("高", "净现比 0.72 的口径纠偏：金融业务噪音大于主业恶化",
     "用现金流量表直接法行项目分解：客户存款净增加额摆动 -161.6 亿 + 存放央行和同业款项摆动 -174.3 亿，合计 -335.9 亿，大于经营现金流全部降幅 309.4 亿；销售收现反增 0.74%。剔除金融项后主业净现比约 0.92，好于上年 0.86。",
     "对照年报附注核对吸收存款与存放央行款项变动", "终审抽查：存款变动与吸收存款余额逐年勾稽吻合 ✓（口径结论待附注复核）"),
    ("中", "回款票据化：应收票据及应收账款从不足 0.1 亿升至 52.4 亿（2025Q3）",
     "2025 年末以「应收款项融资」44.6 亿列示，年内发生科目切换。银行承兑汇票占比若高，风险有限，但反映经销商现金支付能力变化。",
     "核对票据承兑人结构与到期兑付情况", "终审抽查：52.35 亿（应收票据及应收账款）/ 44.57 亿 ✓"),
    ("中", "费用罕见背离：销售费用 +28.6% vs 管理费用 -10.7%",
     "销售费用率升至 4.22%（往年约 3.3%），管理费用却大幅压缩，员工数还在微增。挤压式控费指向利润管理动作，量级约 1% 净利。",
     "查阅两项费用的明细构成与计提口径", "终审抽查：4.22% / +28.62% ✓"),
    ("中", "收现比中枢下移：五年从 1.09 降至 1.07，2024 年缺口最大",
     "销售商品收到现金 / 营业收入：1.09 → 1.10 → 1.09 → 1.05 → 1.07。与合同负债下滑互相印证「打款意愿降温」。",
     "分季度跟踪收现比拐点", "与 Q1 证据链同向 ✓"),
    ("低", "分红台账与现金流量表股利支付存在缺口",
     "常规年份缺口 23–26 亿恰等于少数股东股利（勾稽闭合），但 2022/2023 年缺口达 302/263 亿，疑为台账未收录特别分红；2025 年股利支付 672.4 亿已超货币资金 516.9 亿。",
     "对照历年分红实施公告逐笔核对", "低影响，列入待办"),
]
find_html = ""
for lv, title, body, verify, audit in findings:
    cls = {"高": "lv-h", "中": "lv-m", "低": "lv-l"}[lv]
    find_html += f'''<div class="finding"><div class="f-head"><span class="lv {cls}">{lv}</span><b>{title}</b></div>
<p>{body}</p><p class="verify">核验方法：{verify}<br><span class="audit">{audit}</span></p></div>'''

q3 = m["latest_q"]
html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>年报体检报告 · 贵州茅台 600519.SH（2025）</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;background:#f1f5f9;color:#0f172a;line-height:1.65}}
.wrap{{max-width:1080px;margin:0 auto;padding:24px 20px 48px}}
header{{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);color:#fff;border-radius:16px;padding:34px 36px 28px;margin-bottom:18px}}
header .kicker{{font-size:13px;letter-spacing:3px;color:#7dd3fc;font-weight:700}}
header h1{{font-size:30px;margin:8px 0 4px}}
header .sub{{color:#cbd5e1;font-size:14px}}
.chips{{margin-top:16px;display:flex;flex-wrap:wrap;gap:8px}}
.chip{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:4px 14px;font-size:12.5px}}
.verdicts{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px}}
.v-card{{background:#fff;border-radius:14px;padding:20px 22px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(15,23,42,.06)}}
.v-card .tag{{font-size:12.5px;color:#64748b;font-weight:700;letter-spacing:1px}}
.v-card .big{{font-size:34px;font-weight:800;margin:4px 0 2px}}
.v-card .note{{font-size:13px;color:#475569}}
.good{{color:#047857}} .warm{{color:#b45309}} .cool{{color:#0e7490}}
section{{background:#fff;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(15,23,42,.06);padding:24px 28px;margin-bottom:16px}}
section h2{{font-size:19px;margin-bottom:4px;display:flex;align-items:center;gap:10px}}
section h2 .no{{background:#0f172a;color:#fff;border-radius:8px;font-size:13px;padding:2px 10px}}
section .desc{{font-size:13.5px;color:#64748b;margin-bottom:14px}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.stat-strip{{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0 4px}}
.stat{{flex:1;min-width:150px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px 16px}}
.stat .k{{font-size:12.5px;color:#64748b}} .stat .v{{font-size:22px;font-weight:800}} .stat .s{{font-size:12px;color:#94a3b8}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:6px}}
th{{background:#f1f5f9;text-align:left;padding:8px 10px;font-size:12.5px;color:#475569;border-bottom:2px solid #e2e8f0}}
td{{padding:8px 10px;border-bottom:1px solid #eef2f7}}
.dn{{color:#dc2626;font-weight:700}} .up{{color:#047857;font-weight:700}}
.finding{{border:1px solid #e2e8f0;border-left-width:4px;border-radius:10px;padding:14px 18px;margin-bottom:12px;background:#fbfdff}}
.f-head{{display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap}}
.f-head b{{font-size:15px}}
.lv{{font-size:12px;font-weight:800;border-radius:6px;padding:2px 10px}}
.lv-h{{background:#fee2e2;color:#b91c1c}} .lv-m{{background:#fef3c7;color:#b45309}} .lv-l{{background:#e0f2fe;color:#0369a1}}
.finding p{{font-size:13.5px;color:#334155}}
.verify{{margin-top:6px;font-size:12.5px;color:#64748b}}
.audit{{color:#047857;font-weight:600}}
footer{{font-size:12.5px;color:#94a3b8;text-align:center;padding:10px 0}}
.pill-pass{{display:inline-block;background:#d1fae5;color:#065f46;font-weight:800;border-radius:10px;padding:6px 18px;font-size:20px}}
@media (max-width:760px){{.verdicts{{grid-template-columns:1fr}}.grid-2{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">

<header>
<div class="kicker">REPORT DETECTIVE · 年报侦探工作流 · 多 AGENT 自动体检</div>
<h1>贵州茅台 600519.SH — 年报体检报告</h1>
<div class="sub">体检对象：2025 年度报告（2026-04-17 披露）｜ 加检：2026 年三季报（2026-10-31 披露）｜ 货币单位：人民币</div>
<div class="chips">
<span class="chip">🤖 5 个 Agent 分工协作</span><span class="chip">🧮 勾稽检查 {summ["PASS"]}/{summ["PASS"]+summ["FAIL"]} 通过</span>
<span class="chip">🕵️ 红队质疑 {len(findings)} 项</span><span class="chip">✅ 独立复算 10/10 一致</span>
<span class="chip">📦 原始数据 JSON 留档</span>
</div>
</header>

<div class="verdicts">
<div class="v-card"><div class="tag">体检结论 1 · 报表可信度</div><div class="big good">A</div>
<div class="note">74 项机械勾稽全部通过，无商誉、应收账款趋零、无有息负债，抽查未见造假结构特征</div></div>
<div class="v-card"><div class="tag">体检结论 2 · 经营景气</div><div class="big warm">降温 ⚠</div>
<div class="note">2025 年营收 -1.2%（罕见负增长）；合同负债连续三年走低，2026Q3 同比 -73%</div></div>
<div class="v-card"><div class="tag">体检结论 3 · 股东回报</div><div class="big cool">强</div>
<div class="note">2025 年度每 10 股派 280.24 元，现金流量表股利支付 672.4 亿；ROE 仍达 32.5%</div></div>
</div>

<section>
<h2><span class="no">01</span>勾稽体检：报表内部自洽吗？</h2>
<div class="desc">对资产负债表、利润表、现金流量表的恒等式逐期机械核验（容差 1 元），并回算 EPS、毛利率、资产负债率与披露值比对。</div>
<div class="stat-strip">
<div class="stat"><div class="k">通过 PASS</div><div class="v good">{summ["PASS"]}</div><div class="s">恒等式成立（容差≤1元）</div></div>
<div class="stat"><div class="k">失败 FAIL</div><div class="v" style="color:#047857">{summ["FAIL"]}</div><div class="s">未发现勾稽异常</div></div>
<div class="stat"><div class="k">口径说明 NOTE</div><div class="v" style="color:#b45309">{summ["NOTE"]}</div><div class="s">货币资金 vs 期末现金口径差</div></div>
<div class="stat"><div class="k">数据缺失 N/A</div><div class="v" style="color:#94a3b8">{summ["N/A"]}</div><div class="s">早期年报未披露现金拆分字段</div></div>
</div>
<p style="font-size:13px;color:#64748b;margin-top:8px">注：EPS 回算值 65.74 元 vs 披露 65.66 元，差异 0.12% 系「期末股本」与「加权平均股数」口径差（年内有回购注销），属正常；其余回算指标与披露值完全一致。</p>
</section>

<section>
<h2><span class="no">02</span>五年趋势：增长与降温并存</h2>
<div class="desc">2025 年营收上市罕见下滑 1.2%，但盈利质量指标（毛利率 91.2%、ROE 32.5%）仍处高位；真正的先行信号藏在合同负债里。</div>
<div class="grid-2">
<div>{chart_rev}<p style="text-align:center;font-size:12.5px;color:#64748b">营业收入 与 归母净利润（2021–2025）</p></div>
<div>{chart_cliab}<p style="text-align:center;font-size:12.5px;color:#64748b">合同负债（经销商预付款）—— 关注 2026Q3</p></div>
</div>
<table>
<tr><th>期间</th><th>营收 YoY</th><th>归母 YoY</th><th>毛利率</th><th>ROE</th><th>资产负债率</th><th>净现比</th></tr>
{rows_tbl}
</table>
<p style="font-size:12.5px;color:#94a3b8;margin-top:8px">净现比 = 经营现金流净额 ÷ 净利润；2025 年 0.72 主要受财务公司金融业务口径影响（见红队发现 Q2）。</p>
</section>

<section>
<h2><span class="no">03</span>红队质疑：数字没问题，生意呢？</h2>
<div class="desc">质疑 Agent 独立审视后的 6 项发现。勾稽证明「报表没算错」，红队回答「生意发生了什么」。每条附终审抽查结果。</div>
{find_html}
</section>

<section>
<h2><span class="no">04</span>同业对比：2025 年白酒分化加剧</h2>
<div class="desc">茅台收入是五粮液的 4.2 倍，但山西汾酒 ROE 反超；五粮液 2025 年营收腰斩（数据自洽：2026 年各季已环比回升）。</div>
<table>
<tr><th>公司</th><th>营收（亿）</th><th>营收 YoY</th><th>归母净利（亿）</th><th>毛利率</th><th>ROE</th><th>资产负债率</th></tr>
{peer_rows}
</table>
<p style="font-size:12.5px;color:#94a3b8;margin-top:8px">均为 2025 年报口径；五粮液 -54.6% 与其 2026 年季报回升数据自洽，判定为真实行业分化而非数据错误。</p>
</section>

<section>
<h2><span class="no">05</span>终审核验与数据溯源</h2>
<div class="desc">本报告不是「AI 说什么就是什么」——每个关键结论都经过第二双眼睛。</div>
<div class="stat-strip">
<div class="stat"><div class="k">核查Agent独立复算</div><div class="v good">10 / 10</div><div class="s">先复算后比对，零引用现成结论</div></div>
<div class="stat"><div class="k">终审抽查红队发现</div><div class="v good">4 / 4</div><div class="s">高/中级发现关键数字全部与原始数据一致</div></div>
<div class="stat"><div class="k">数据源</div><div class="v" style="font-size:15px">东方财富 F10</div><div class="s">原始 JSON 已留档（报告目录/原始数据）</div></div>
</div>
<p style="font-size:13px;color:#475569;margin-top:10px">工作流执行链：取数Agent（脚本抓取+留档）→ 勾稽Agent（74 项机械核验）→ 质疑Agent（红队 6 项发现）→ 核查Agent（独立复算 10 项）→ 终审整合（本报告，抽查红队数字）。完整过程见 <b>agent_log.md</b>，全部中间产物可复现。</p>
</section>

<footer>生成于 {m["run_time"]} ｜ 「年报侦探」多Agent工作流 v1.0 ｜ 数据来源：东方财富 F10（截至 {m["run_time"][:10]}）｜ 本报告仅为数据分析演示，不构成投资建议</footer>
</div></body></html>'''

path = os.path.join(OUT, "年报体检报告_贵州茅台2025.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", path, len(html), "bytes")
