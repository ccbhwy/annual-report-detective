import json, sys
BASE = r"D:\AI_Project\zuopin\02_实际产出\原始数据"
for name in ["balance_600519", "income_600519", "cashflow_600519", "main_600519", "dividend_600519"]:
    with open(f"{BASE}\\{name}.json", encoding="utf-8") as f:
        d = json.load(f)
    rows = (d.get("result") or {}).get("data") or []
    print(f"===== {name}: {len(rows)} rows")
    if not rows:
        print("  EMPTY"); continue
    annual = [r for r in rows if r.get("REPORT_TYPE") == "年报"]
    r = (annual[0] if annual else rows[0])
    print(f"  sample period: {r.get('REPORT_DATE_NAME')}")
    nn = {k: v for k, v in r.items() if v is not None}
    for k in sorted(nn):
        print(f"  {k} = {nn[k]}")
