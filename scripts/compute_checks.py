# -*- coding: utf-8 -*-
"""勾稽Agent：确定性财务勾稽检查 + 指标计算。
输入: 02_实际产出/原始数据/*.json (东方财富F10)
输出: 02_实际产出/勾稽底稿.json, 02_实际产出/metrics.json
"""
import json, os, sys

BASE = r"D:\AI_Project\zuopin\02_实际产出\原始数据"
OUT = r"D:\AI_Project\zuopin\02_实际产出"
TOL = 1.0  # 1元容差（浮点+披露精度）

def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as f:
        d = json.load(f)
    return (d.get("result") or {}).get("data") or []

def annuals(rows, n=5):
    a = [r for r in rows if r.get("REPORT_TYPE") == "年报"]
    a.sort(key=lambda r: r.get("REPORT_DATE") or "", reverse=True)
    return a[:n]

def g(row, key):
    v = row.get(key)
    return float(v) if isinstance(v, (int, float)) else None

def chk(checks, period, name, expect, actual, comps, note=""):
    """comps: [(科目名, 值)]  expect/actual 数值"""
    if expect is None or actual is None:
        checks.append({"period": period, "check": name, "status": "N/A",
                       "expect": expect, "actual": actual, "diff": None, "comps": comps, "note": note})
        return
    diff = actual - expect
    status = "PASS" if abs(diff) <= TOL else "FAIL"
    checks.append({"period": period, "check": name, "status": status,
                   "expect": round(expect, 2), "actual": round(actual, 2),
                   "diff": round(diff, 2), "comps": comps, "note": note})

def pct(a, b):
    if a is None or b in (None, 0): return None
    return a / b * 100

# ---------- 载入 ----------
bal_rows = annuals(load("balance_600519.json"))
inc_rows = annuals(load("income_600519.json"))
cf_rows  = annuals(load("cashflow_600519.json"))
main_all = load("main_600519.json")
main_by_period = {r.get("REPORT_DATE_NAME"): r for r in main_all}
div_rows = load("dividend_600519.json")

periods = [r["REPORT_DATE_NAME"] for r in bal_rows]
bal = {r["REPORT_DATE_NAME"]: r for r in bal_rows}
inc = {r["REPORT_DATE_NAME"]: r for r in inc_rows}
cf  = {r["REPORT_DATE_NAME"]: r for r in cf_rows}

checks = []

# ---------- 一、资产负债表勾稽 ----------
for p in periods:
    b = bal[p]
    ta, tl, te = g(b,"TOTAL_ASSETS"), g(b,"TOTAL_LIABILITIES"), g(b,"TOTAL_EQUITY")
    chk(checks, p, "资产 = 负债 + 所有者权益", tl + te if tl and te else None, ta,
        [("负债合计",tl),("权益合计",te),("资产总计",ta)])
    tca, tnca = g(b,"TOTAL_CURRENT_ASSETS"), g(b,"TOTAL_NONCURRENT_ASSETS")
    chk(checks, p, "流动资产 + 非流动资产 = 资产总计", tca + tnca if tca and tnca else None, ta,
        [("流动资产",tca),("非流动资产",tnca),("资产总计",ta)])
    tcl, tnl = g(b,"TOTAL_CURRENT_LIAB"), g(b,"TOTAL_NONCURRENT_LIAB")
    chk(checks, p, "流动负债 + 非流动负债 = 负债合计", tcl + tnl if tcl and tnl else None, tl,
        [("流动负债",tcl),("非流动负债",tnl),("负债合计",tl)])
    pe, me = g(b,"TOTAL_PARENT_EQUITY"), g(b,"MINORITY_EQUITY")
    chk(checks, p, "归母权益 + 少数股东权益 = 权益合计", pe + me if pe and me else None, te,
        [("归母权益",pe),("少数股东权益",me),("权益合计",te)])

# ---------- 二、利润表勾稽 ----------
for p in periods:
    if p not in inc: continue
    i = inc[p]
    toi, toc, op = g(i,"TOTAL_OPERATE_INCOME"), g(i,"TOTAL_OPERATE_COST"), g(i,"OPERATE_PROFIT")
    add_names = [("其他收益","OTHER_INCOME"),("投资收益","INVEST_INCOME"),("公允价值变动","FAIRVALUE_CHANGE_INCOME"),
                 ("信用减值损失","CREDIT_IMPAIRMENT_INCOME"),("资产减值损失","ASSET_IMPAIRMENT_INCOME"),
                 ("资产处置收益","ASSET_DISPOSAL_INCOME")]
    add_total, comps = 0.0, [("营业总收入",toi),("营业总成本",-toc if toc else None)]
    missing = False
    for label,k in add_names:
        v = g(i,k)
        if v is None: continue
        add_total += v; comps.append((label,v))
    chk(checks, p, "营业利润 = 总收入 - 总成本 + 收益类科目", toi - toc + add_total if toi and toc else None, op, comps)
    ni, nbe, nbi = g(i,"NONBUSINESS_INCOME"), g(i,"NONBUSINESS_EXPENSE"), None
    tp = g(i,"TOTAL_PROFIT")
    chk(checks, p, "利润总额 = 营业利润 + 营业外收支", op + ni - nbe if None not in (op,ni,nbe) else None, tp,
        [("营业利润",op),("营业外收入",ni),("营业外支出",-nbe if nbe else None),("利润总额",tp)])
    tax, npf = g(i,"INCOME_TAX"), g(i,"NETPROFIT")
    chk(checks, p, "净利润 = 利润总额 - 所得税", tp - tax if tp and tax else None, npf,
        [("利润总额",tp),("所得税",-tax if tax else None),("净利润",npf)])
    pn, mn = g(i,"PARENT_NETPROFIT"), g(i,"MINORITY_INTEREST")
    chk(checks, p, "归母净利 + 少数股东损益 = 净利润", pn + mn if pn and mn else None, npf,
        [("归母净利",pn),("少数股东损益",mn),("净利润",npf)])

# ---------- 三、现金流量表勾稽 ----------
for p in periods:
    if p not in cf: continue
    c = cf[p]
    o, iv, f, fx = g(c,"NETCASH_OPERATE"), g(c,"NETCASH_INVEST"), g(c,"NETCASH_FINANCE"), g(c,"RATE_CHANGE_EFFECT")
    cadd = g(c,"CCE_ADD")
    chk(checks, p, "经营+投资+筹资+汇率 = 现金净增加额", o+iv+f+fx if None not in (o,iv,f,fx) else None, cadd,
        [("经营净额",o),("投资净额",iv),("筹资净额",f),("汇率影响",fx),("净增加额",cadd)])
    bc, be = g(c,"BEGIN_CCE"), g(c,"END_CCE")
    chk(checks, p, "期初现金 + 净增加额 = 期末现金", bc + cadd if bc and cadd else None, be,
        [("期初",bc),("净增加",cadd),("期末",be)])
    bcb, bce = g(c,"BEGIN_CASH"), g(c,"BEGIN_CASH_EQUIVALENTS")
    chk(checks, p, "期初现金 = 期初现金及等价物拆分", bcb + bce if None not in (bcb,bce) else None, bc,
        [("现金",bcb),("等价物",bce),("期初合计",bc)])
    ecb, ece = g(c,"END_CASH"), g(c,"END_CASH_EQUIVALENTS")
    chk(checks, p, "期末现金 = 期末现金及等价物拆分", ecb + ece if None not in (ecb,ece) else None, be,
        [("现金",ecb),("等价物",ece),("期末合计",be)])

# 跨期衔接：本期期初 = 上期期末
for idx in range(len(periods)-1):
    cur, prev = periods[idx], periods[idx+1]
    if cur in cf and prev in cf:
        chk(checks, cur, f"期初现金衔接 {prev}期末", g(cf[prev],"END_CCE"), g(cf[cur],"BEGIN_CCE"),
            [(f"{prev}期末",g(cf[prev],"END_CCE")),(f"{cur}期初",g(cf[cur],"BEGIN_CCE"))])

# ---------- 四、跨表勾稽 ----------
for p in periods:
    if p in bal and p in cf:
        mf, ec = g(bal[p],"MONETARYFUNDS"), g(cf[p],"END_CASH")
        diff = (ec - mf) if (ec and mf) else None
        checks.append({"period": p, "check": "货币资金 vs 现金流量表期末现金（口径差异）",
                       "status": "NOTE", "expect": mf, "actual": ec,
                       "diff": round(diff,2) if diff is not None else None,
                       "comps": [("货币资金",mf),("期末现金及等价物",ec)],
                       "note": "茅台含财务公司业务，存放央行款项/拆出资金口径不同，需解释不能算错"})
    if p in inc and p in cf:
        npf, oc = g(inc[p],"NETPROFIT"), g(cf[p],"NETCASH_OPERATE")
        ratio = round(oc/npf,3) if npf and oc else None
        checks.append({"period": p, "check": "净现比（经营现金流/净利润）", "status": "INFO",
                       "expect": None, "actual": ratio, "diff": None,
                       "comps": [("经营现金流",oc),("净利润",npf)], "note": "长期>0.8为佳"})

# ---------- 五、指标回算 vs 披露值 ----------
for p in periods:
    if p not in inc or p not in bal: continue
    i, b, m = inc[p], bal[p], main_by_period.get(p, {})
    oi, oc = g(i,"OPERATE_INCOME"), g(i,"OPERATE_COST")
    gm = pct(oi - oc, oi) if oi and oc else None
    disclosed = g(m,"XSMLL")
    if gm and disclosed:
        chk(checks, p, "毛利率回算 vs 披露(销售毛利率)", round(gm,2), round(disclosed,2),
            [("回算",round(gm,2)),("披露",round(disclosed,2))])
    pn, pe = g(i,"PARENT_NETPROFIT"), g(b,"TOTAL_PARENT_EQUITY")
    roe = pct(pn, pe)
    roe_d = g(m,"ROEJQ")  # 披露为加权，仅参考
    de, sc = g(i,"DEDUCT_PARENT_NETPROFIT"), None
    eps = pn / g(b,"SHARE_CAPITAL") if pn and g(b,"SHARE_CAPITAL") else None
    eps_d = g(i,"BASIC_EPS")
    if eps and eps_d:
        chk(checks, p, "EPS回算 vs 披露(基本每股收益)", round(eps,2), round(eps_d,2),
            [("回算",round(eps,2)),("披露",eps_d)])
    dr = pct(g(b,"TOTAL_LIABILITIES"), g(b,"TOTAL_ASSETS"))
    dr_d = g(m,"ZCFZL")
    if dr and dr_d:
        chk(checks, p, "资产负债率回算 vs 披露", round(dr,2), round(dr_d,2),
            [("回算",round(dr,2)),("披露",round(dr_d,2))])

# ---------- 汇总 ----------
summary = {"PASS":0,"FAIL":0,"NOTE":0,"INFO":0,"N/A":0}
for c in checks: summary[c["status"]] = summary.get(c["status"],0)+1
fails = [c for c in checks if c["status"]=="FAIL"]

# ---------- 指标趋势 ----------
metrics = {"company":"贵州茅台","code":"600519.SH","periods":periods,"trend":[]}
for p in periods:
    i, b, c, m = inc.get(p,{}), bal.get(p,{}), cf.get(p,{}), main_by_period.get(p,{})
    oi, oc = g(i,"OPERATE_INCOME"), g(i,"OPERATE_COST")
    row = {
        "period": p,
        "total_income": g(i,"TOTAL_OPERATE_INCOME"),
        "income_yoy": g(i,"TOTAL_OPERATE_INCOME_YOY"),
        "parent_profit": g(i,"PARENT_NETPROFIT"),
        "profit_yoy": g(i,"PARENT_NETPROFIT_YOY"),
        "gross_margin": round(pct(oi-oc,oi),2) if oi and oc else None,
        "net_margin": round(pct(g(i,"NETPROFIT"), g(i,"TOTAL_OPERATE_INCOME")),2),
        "roe": g(m,"ROEJQ"),
        "debt_ratio": g(m,"ZCFZL"),
        "ocf": g(c,"NETCASH_OPERATE"),
        "cash_ratio": round(g(c,"NETCASH_OPERATE")/g(i,"NETPROFIT"),3) if g(c,"NETCASH_OPERATE") and g(i,"NETPROFIT") else None,
        "inventory": g(b,"INVENTORY"),
        "contract_liab": g(b,"CONTRACT_LIAB"),
        "monetary": g(b,"MONETARYFUNDS"),
        "total_assets": g(b,"TOTAL_ASSETS"),
        "parent_equity": g(b,"TOTAL_PARENT_EQUITY"),
        "unassign_profit": g(b,"UNASSIGN_RPOFIT"),
        "eps": g(i,"BASIC_EPS"),
        "dividend_paid": g(c,"ASSIGN_DIVIDEND_PORFIT"),
    }
    metrics["trend"].append(row)

# 最新季报（三季报）
q3 = next((r for r in main_all if r.get("REPORT_TYPE")=="三季报"), None)
metrics["latest_q"] = None
if q3:
    inc_all = load("income_600519.json")
    q3i = next((r for r in inc_all if r.get("REPORT_DATE_NAME")==q3.get("REPORT_DATE_NAME")), None)
    metrics["latest_q"] = {
        "period": q3.get("REPORT_DATE_NAME"),
        "income": g(q3i,"TOTAL_OPERATE_INCOME") if q3i else g(q3,"TOTALOPERATEREVE"),
        "income_yoy": g(q3,"TOTALOPERATEREVETZ"),
        "profit": g(q3i,"PARENT_NETPROFIT") if q3i else g(q3,"PARENTNETPROFIT"),
        "profit_yoy": g(q3,"PARENTNETPROFITTZ"),
        "notice_date": (q3.get("NOTICE_DATE") or "")[:10],
    }

# 同业对比（最新年报）
peers = []
for code,fname,label in [("600519.SH","main_600519.json","贵州茅台"),("000858.SZ","main_000858.json","五粮液"),
                          ("000568.SZ","main_000568.json","泸州老窖"),("600809.SH","main_600809.json","山西汾酒")]:
    rows = load(fname)
    an = annuals(rows,1)[0]
    peers.append({"code":code,"name":label,"period":an.get("REPORT_DATE_NAME"),
                  "income":g(an,"TOTALOPERATEREVE"),"income_yoy":g(an,"TOTALOPERATEREVETZ"),
                  "profit":g(an,"PARENTNETPROFIT"),"profit_yoy":g(an,"PARENTNETPROFITTZ"),
                  "gross_margin":g(an,"XSMLL"),"roe":g(an,"ROEJQ"),"debt_ratio":g(an,"ZCFZL"),
                  "ocf_to_debt":g(an,"OCFYL")})
metrics["peers"] = peers

# 元数据
meta = {}
for f in ["balance_600519","income_600519","cashflow_600519","main_600519","dividend_600519"]:
    rows = load(f+".json")
    meta[f] = {"rows":len(rows),"latest":rows[0].get("REPORT_DATE_NAME") if rows else None,
               "notice_date":(rows[0].get("NOTICE_DATE") or "")[:10] if rows else None}
metrics["data_meta"] = meta
metrics["run_time"] = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(os.path.join(OUT,"勾稽底稿.json"),"w",encoding="utf-8") as f:
    json.dump({"summary":summary,"checks":checks,"fails":fails},f,ensure_ascii=False,indent=1)
with open(os.path.join(OUT,"metrics.json"),"w",encoding="utf-8") as f:
    json.dump(metrics,f,ensure_ascii=False,indent=1)

print("勾稽汇总:",summary)
print("期间:",periods)
for c in fails: print("FAIL:",c["period"],c["check"],"diff=",c["diff"])
print("最新季报:",metrics["latest_q"])
print("同业:",[(p_["name"],p_["income"],p_["profit"],p_["roe"]) for p_ in peers])
