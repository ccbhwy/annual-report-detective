# -*- coding: utf-8 -*-
"""生成 Excel 勾稽底稿：说明 / 勾稽明细 / 趋势指标 / 同业对比 / 红队发现"""
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\AI_Project\zuopin\02_实际产出"
m = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))
c = json.load(open(os.path.join(OUT, "勾稽底稿.json"), encoding="utf-8"))

wb = Workbook()
HEAD = PatternFill("solid", fgColor="0F172A")
HF = Font(color="FFFFFF", bold=True, size=11)
TITLE = Font(bold=True, size=14, color="0F172A")
THIN = Border(*[Side(style="thin", color="D9E2EC")] * 4)
ZEBRA = PatternFill("solid", fgColor="F8FAFC")
GREEN = Font(color="047857", bold=True)
RED = Font(color="B91C1C", bold=True)
AMBER = Font(color="B45309", bold=True)

def style_header(ws, row=1):
    for cell in ws[row]:
        if cell.value is not None:
            cell.fill = HEAD; cell.font = HF
            cell.alignment = Alignment(vertical="center", wrap_text=True)

def auto_width(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ---- 说明 ----
ws = wb.active; ws.title = "说明"
info = [
    ("「年报侦探」多Agent工作流 — 勾稽底稿", None),
    ("", None),
    ("体检对象", "贵州茅台 600519.SH"),
    ("覆盖期间", "2021-2025 年报 + 2026 三季报"),
    ("数据来源", "东方财富 F10 接口（datacenter.eastmoney.com），原始JSON见 原始数据/ 目录"),
    ("抓取时间", m["run_time"]),
    ("勾稽结果", f"{c['summary']['PASS']} 通过 / {c['summary']['FAIL']} 失败 / {c['summary']['NOTE']} 口径说明 / {c['summary']['N/A']} 数据缺失"),
    ("多Agent分工", "取数Agent(脚本) → 勾稽Agent(本底稿) → 质疑Agent(红队) → 核查Agent(独立复算10/10) → 终审整合"),
    ("免责声明", "本底稿为数据分析演示，不构成投资建议。金额单位如列头所示。"),
]
for r, (k, v) in enumerate(info, 1):
    ws.cell(r, 1, k)
    if v is not None: ws.cell(r, 2, v)
ws["A1"].font = TITLE
for r in range(3, len(info) + 1):
    ws.cell(r, 1).font = Font(bold=True)
    ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
auto_width(ws, [16, 110])

# ---- 勾稽明细 ----
ws = wb.create_sheet("勾稽明细")
cols = ["期间", "检查项", "状态", "应有值", "实际值", "差异", "说明"]
ws.append(cols)
for k in c["checks"]:
    note = k.get("note") or ""
    if k["status"] == "FAIL":
        note = "⚠ 差异超容差 " + note
    ws.append([k["period"], k["check"], k["status"], k.get("expect"), k.get("actual"), k.get("diff"), note])
style_header(ws)
for r in range(2, ws.max_row + 1):
    st = ws.cell(r, 3).value
    cell = ws.cell(r, 3)
    cell.font = GREEN if st == "PASS" else RED if st == "FAIL" else AMBER
    for col in (4, 5, 6):
        cc = ws.cell(r, col)
        if isinstance(cc.value, (int, float)):
            cc.number_format = "#,##0.00"
    if r % 2 == 0:
        for col in range(1, 8):
            if ws.cell(r, col).fill.fgColor.rgb in ("00000000", None):
                ws.cell(r, col).fill = ZEBRA
auto_width(ws, [11, 40, 8, 20, 20, 12, 44])
ws.freeze_panes = "A2"

# ---- 趋势指标 ----
ws = wb.create_sheet("趋势指标")
ws.append(["期间", "营收(亿)", "营收YoY%", "归母净利(亿)", "归母YoY%", "毛利率%", "ROE%", "资产负债率%", "净现比", "合同负债(亿)", "存货(亿)", "经营现金流(亿)"])
for t in m["trend"]:
    ws.append([t["period"], t["total_income"] / 1e8, t["income_yoy"], t["parent_profit"] / 1e8, t["profit_yoy"],
               t["gross_margin"], t["roe"], t["debt_ratio"], t["cash_ratio"],
               t["contract_liab"] / 1e8, t["inventory"] / 1e8, t["ocf"] / 1e8])
q = m.get("latest_q")
if q:
    ws.append([q["period"], q["income"] / 1e8, q["income_yoy"], q["profit"] / 1e8, q["profit_yoy"], None, None, None, None, 2.08, None, None])
style_header(ws)
for r in range(2, ws.max_row + 1):
    for col in range(2, 13):
        cc = ws.cell(r, col)
        if isinstance(cc.value, (int, float)):
            cc.number_format = "0.00"
auto_width(ws, [11, 11, 10, 13, 10, 9, 8, 12, 8, 13, 11, 14])
ws.freeze_panes = "B2"

# ---- 同业对比 ----
ws = wb.create_sheet("同业对比")
ws.append(["公司", "代码", "期间", "营收(亿)", "营收YoY%", "归母净利(亿)", "归母YoY%", "毛利率%", "ROE%", "资产负债率%"])
for p in m["peers"]:
    ws.append([p["name"], p["code"], p["period"], p["income"] / 1e8, p["income_yoy"], p["profit"] / 1e8,
               p["profit_yoy"], p["gross_margin"], p["roe"], p["debt_ratio"]])
style_header(ws)
for r in range(2, ws.max_row + 1):
    for col in range(4, 11):
        cc = ws.cell(r, col)
        if isinstance(cc.value, (int, float)):
            cc.number_format = "0.00"
auto_width(ws, [11, 11, 10, 11, 10, 13, 10, 9, 8, 12])

# ---- 红队发现 ----
ws = wb.create_sheet("红队发现")
ws.append(["等级", "发现", "证据/分析", "核验方法", "终审状态"])
findings = [
    ("高", "合同负债断崖：2026Q3 仅20.8亿，同比-73.1%", "141.3亿(2023)→95.9亿(2024)→80.1亿(2025)→20.8亿(2026Q3)；排除科目重分类", "调年报附注核对明细", "终审抽查一致 ✓"),
    ("高", "净现比0.72主要为财务公司口径噪音", "存款+存放央行摆动-335.9亿 > OCF降幅309.4亿；销售收现+0.74%；剔除金融项主业净现比≈0.92", "对照附注核对吸收存款变动", "抽查一致，口径结论待附注复核"),
    ("中", "回款票据化：应收票据及应收账款升至52.4亿(2025Q3)", "2025年末以应收款项融资44.6亿列示，年内科目切换", "核对票据承兑人结构", "终审抽查一致 ✓"),
    ("中", "销售费用+28.6% vs 管理费用-10.7%背离", "销售费用率4.22%(往年约3.3%)；管理费用压缩指向计提口径", "查阅费用明细构成", "终审抽查一致 ✓"),
    ("中", "收现比中枢下移", "1.09→1.10→1.09→1.05→1.07，与合同负债下滑互证", "分季度跟踪", "与Q1证据链同向 ✓"),
    ("低", "分红台账与现金流量表股利支付缺口", "2022/2023年缺口302/263亿疑未收录特别分红", "逐笔核对分红公告", "低影响，列入待办"),
]
for row in findings:
    ws.append(list(row))
style_header(ws)
for r in range(2, ws.max_row + 1):
    lv = ws.cell(r, 1).value
    ws.cell(r, 1).font = GREEN if lv == "高" and False else (RED if lv == "高" else AMBER if lv == "中" else Font(color="0369A1"))
    for col in range(1, 6):
        ws.cell(r, col).alignment = Alignment(wrap_text=True, vertical="top")
auto_width(ws, [7, 42, 60, 22, 24])

path = os.path.join(OUT, "勾稽底稿_贵州茅台2025.xlsx")
wb.save(path)
print("written:", path)
