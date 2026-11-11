# 核查Agent 终审报告

## 运行信息

- **核查时间**：2026-11-09 23:55（与工作流产出 run_time "2026-11-09 23:45:26" 同日）
- **核查方法**：不依赖工作流结论文件，先用 `python -I`（隔离模式）直接读取原始 JSON 现场独立复算 10 项关键数字，**复算完成后**再读取 `勾稽底稿.json` 与 `metrics.json` 逐项比对
- **数据源（只读）**：
  - `D:\AI_Project\zuopin\02_实际产出\原始数据\balance_600519.json`（东财 F10 资产负债表，result.data 共 24 行）
  - `D:\AI_Project\zuopin\02_实际产出\原始数据\income_600519.json`（利润表，24 行）
  - `D:\AI_Project\zuopin\02_实际产出\原始数据\cashflow_600519.json`（现金流量表，24 行）
  - `D:\AI_Project\zuopin\02_实际产出\原始数据\main_000858.json`（五粮液主要指标，40 行）
  - `D:\AI_Project\zuopin\02_实际产出\原始数据\main_600519.json`（茅台主要指标，40 行）
- **取数规则**：按 `REPORT_DATE_NAME == "2025年报"`（`REPORT_TYPE == "年报"`）过滤，各表均命中唯一一行（2025-12-31，公告日 2026-04-17）；股本取资产负债表 `SHARE_CAPITAL`
- **待比对文件**：`D:\AI_Project\zuopin\02_实际产出\勾稽底稿.json`（74 PASS / 0 FAIL）、`D:\AI_Project\zuopin\02_实际产出\metrics.json`

## 复算比对表

金额单位：亿元人民币（比率除外）；完整精度见下方"关键金额完整精度对照"。

| # | 核查项 | 独立复算值 | 工作流结论值 | 一致性 |
|---|--------|-----------|-------------|--------|
| 1 | 资产总计 = 负债合计 + 所有者权益合计 | 3038.3484 = 498.7559 + 2539.5925，**差额 0.00 元** | 底稿同项 expect=actual=3038.3484亿，diff=0.0，PASS（负债 498.7559 / 权益 2539.5925，逐项相同） | 一致 |
| 2 | 营业利润 = 总收入−总成本+其他收益+投资收益+公允价值变动+信用减值+资产处置 | 1720.5417 − 573.7082 + 0.0285 + 0.0006 + 0.0762 + 0.0172 + 0.0031 = **1148.0895亿**，与报表营业利润差额 0.00 元 | 底稿同项 expect=actual=1148.0895亿（114,808,950,164.24），diff=0.0，PASS，7 个分项金额逐项相同 | 一致 |
| 3 | 净利润 = 利润总额 − 所得税 | 1147.5526 − 294.4494 = **853.1032亿**，差额 0.00 元 | 底稿同项 853.1032亿（85,310,324,833.67），diff=0.0，PASS | 一致 |
| 4 | 归母净利 + 少数股东损益 = 净利润 | 823.2007 + 29.9026 = **853.1032亿**，差额 0.00 元 | 底稿同项 853.1032亿，diff=0.0，PASS | 一致 |
| 5 | EPS 回算 = 归母净利 ÷ 股本 ≈ BASIC_EPS | 82,320,067,101.68 ÷ 1,252,270,215 = **65.7367 元** vs 披露 BASIC_EPS **65.66**，差 0.0767 元（0.12%） | 底稿"EPS回算 vs 披露"：expect 65.74 / actual 65.66 / diff −0.08，PASS；metrics eps=65.66 | 一致（约等；差异为"期末股本回算 vs 加权平均股数"的已知口径差，双方回算值相同，均判 PASS，见结论①） |
| 6 | 毛利率 = (营业收入−营业成本)/营业收入 | (1688.3810 − 148.9228) ÷ 1688.3810 = **91.1796%**（0.91179552） | metrics trend[0].gross_margin=91.18、peers 茅台 gross_margin=91.1795516835；底稿"毛利率回算 vs 披露" 91.18 vs 91.18，PASS | 一致（口径正确：使用营业收入而非营业总收入，见结论②） |
| 7 | 净现比 = 经营现金流净额 ÷ 净利润 | 615.2220 ÷ 853.1032 = **0.721158** | metrics cash_ratio=0.721；底稿 INFO 项 actual=0.721 | 一致（工作流为 3 位小数舍入） |
| 8 | 现金净增加额 = 经营+投资+筹资+汇率影响 | 615.2220 + (−316.4190) + (−734.2708) + 0.0230 = **−435.4448亿**（−43,544,479,810.11），与 CCE_ADD 差额仅 8×10⁻⁶ 元（浮点表示）；补充复算 END_CCE−BEGIN_CCE 亦等于净增加额 | 底稿"经营+投资+筹资+汇率 = 现金净增加额"：expect=actual=−435.4448亿，diff=−0.0，PASS；"期初+净增=期末" 1264.2561亿 亦 PASS | 一致（−0.0 与 8×10⁻⁶ 均为浮点表示误差，非实际差异） |
| 9 | 五粮液 2025 营收同比 = 2025收入/2024收入 − 1 | 405.2851 ÷ 891.7518 − 1 = **−54.5518%**（两口径营业总收入/营业收入结果相同）；东财官方同比字段 TOTALOPERATEREVETZ = −54.5518% 互证 | metrics peers 五粮液 income_yoy = **−54.551804064166** | 一致（"约 −54.5%"成立） |
| 10 | 茅台 2025 营收 ÷ 五粮液 2025 营收 | 1720.5417 ÷ 405.2851 = **4.2453 倍**（营业总收入口径；营业收入口径为 4.1659 倍） | metrics peers 茅台 income 1720.5417亿 / 五粮液 income 405.2851亿，比值同为 4.2453 | 一致（"约 4.2 倍"成立；工作流文件未单列倍数字段，此值由其 peers 收入数据复算，与我独立取数完全相同，见结论③） |

**关键金额完整精度对照（元）**：

- 资产总计 303,834,844,021.44 ＝ 负债 49,875,590,112.37 ＋ 权益 253,959,253,909.07（补充：流动 2,525.1866亿＋非流动 513.1618亿 亦精确恒等）
- 营业利润 114,808,950,164.24；利润总额 114,755,261,605.08；净利润 85,310,324,833.67；归母 82,320,067,101.68；少数股东 2,990,257,731.99
- 经营现金流净额 61,522,204,989.35；现金净增加额 −43,544,479,810.11（期末 126,425,609,447.72 − 期初 169,970,089,257.83）
- 五粮液 2025 营收 40,528,509,770.23 / 2024 营收 89,175,178,322.70；茅台 2025 营收 172,054,171,890.91

## 核查结论

**总体声明：10 项关键数字全部复算一致，0 项不一致。** 工作流产出的勾稽底稿（74 PASS / 0 FAIL）与 metrics.json 中与本次清单相关的全部数值，与我从原始数据的独立复算在完整精度下吻合；未发现任何计算错误、漏项或口径错配。三点口径说明（均为合理差异，非错误）：

1. **第 5 项 EPS 差 0.0767 元（0.12%）**：用期末股本回算得 65.74，披露 BASIC_EPS 65.66 系按发行在外加权平均股数计算（茅台报告期内股本因回购注销变动所致），属准则内正常口径差。工作流同样以 65.74 回算并标注 PASS，处理正确，不算差异。
2. **第 6 项毛利率口径**：若误用营业总收入（1720.54亿，含财务公司利息收入）对营业总成本相除会得 66.66%，那是营业利润率性质而非毛利率。工作流按营业收入口径得 91.18%，与披露及本次复算一致，口径选用正确。
3. **第 10 项倍数口径**：营业总收入口径 4.2453 倍、营业收入口径 4.1659 倍，两者均支持"约 4.2 倍"表述。建议对外发布时注明采用口径；工作流未单列倍数字段，仅提供两家收入数据，结论不受影响。
4. 附注：底稿将"货币资金 516.91亿 vs 现金流量表期末现金 1179.53亿"（茅台含财务公司业务，存放央行款项/拆出资金口径不同）标为 NOTE 而非 FAIL，该处理恰当，不影响本清单 10 项。

**发布判断：该工作流产出（勾稽底稿.json、metrics.json）经独立终审核验，关键数字全部可复核、可追溯，可以对外发布。** 建议发布时随附上述三点口径说明。

## 附录：复算代码片段（python -I 独立运行，先复算后比对）

```python
# -*- coding: utf-8 -*-
import json, os
BASE = r"D:\AI_Project\zuopin\02_实际产出\原始数据"

def load(fname):
    with open(os.path.join(BASE, fname), "r", encoding="utf-8") as f:
        return json.load(f)["result"]["data"]

def pick_annual(rows, name):            # 按报告期名过滤年报，唯一命中
    sel = [r for r in rows if r.get("REPORT_DATE_NAME") == name]
    assert len(sel) == 1
    return sel[0]

b25 = pick_annual(load("balance_600519.json"), "2025年报")
i25 = pick_annual(load("income_600519.json"),  "2025年报")
c25 = pick_annual(load("cashflow_600519.json"),"2025年报")
w25 = pick_annual(load("main_000858.json"),    "2025年报")
w24 = pick_annual(load("main_000858.json"),    "2024年报")
m25 = pick_annual(load("main_600519.json"),    "2025年报")

# C1 资产 = 负债 + 权益
TA, TL, TE = (float(b25[k]) for k in ("TOTAL_ASSETS","TOTAL_LIABILITIES","TOTAL_EQUITY"))
print("C1 delta =", TA - (TL + TE))                        # -> 0.0

# C2 营业利润 = 总收入 - 总成本 + 收益类科目
TOI, TOC = float(i25["TOTAL_OPERATE_INCOME"]), float(i25["TOTAL_OPERATE_COST"])
OP = float(i25["OPERATE_PROFIT"])
c2 = (TOI - TOC + float(i25["OTHER_INCOME"]) + float(i25["INVEST_INCOME"])
      + float(i25["FAIRVALUE_CHANGE_INCOME"]) + float(i25["CREDIT_IMPAIRMENT_INCOME"])
      + float(i25["ASSET_DISPOSAL_INCOME"]))
print("C2 delta =", OP - c2)                                # -> 0.0

# C3 净利润 = 利润总额 - 所得税 ;  C4 归母 + 少数 = 净利润
NP, TP, TAX = float(i25["NETPROFIT"]), float(i25["TOTAL_PROFIT"]), float(i25["INCOME_TAX"])
PN, MI = float(i25["PARENT_NETPROFIT"]), float(i25["MINORITY_INTEREST"])
print("C3 delta =", NP - (TP - TAX), "| C4 delta =", NP - (PN + MI))   # -> 0.0 0.0

# C5 EPS 回算 vs BASIC_EPS
SC, BE = float(b25["SHARE_CAPITAL"]), float(i25["BASIC_EPS"])
print("C5 EPS_calc = %.6f vs BASIC_EPS %.2f" % (PN / SC, BE))          # -> 65.736665 vs 65.66

# C6 毛利率（营业收入口径）
OI_rev, OC = float(i25["OPERATE_INCOME"]), float(i25["OPERATE_COST"])
print("C6 GM = %.8f" % ((OI_rev - OC) / OI_rev))                       # -> 0.91179552

# C7 净现比 ;  C8 现金净增加额 = 经营+投资+筹资+汇率
NO = float(c25["NETCASH_OPERATE"])
print("C7 ratio = %.6f" % (NO / NP))                                   # -> 0.721158
c8 = (NO + float(c25["NETCASH_INVEST"]) + float(c25["NETCASH_FINANCE"])
      + float(c25["RATE_CHANGE_EFFECT"]))
CCE = float(c25["CCE_ADD"])
print("C8 delta =", CCE - c8, "| END-BEGIN =", float(c25["END_CCE"]) - float(c25["BEGIN_CCE"]))

# C9 五粮液营收同比 ;  C10 茅台/五粮液
W25, W24 = float(w25["TOTALOPERATEREVE"]), float(w24["TOTALOPERATEREVE"])
M25 = float(m25["TOTALOPERATEREVE"])
print("C9 yoy = %.8f" % (W25 / W24 - 1))                               # -> -0.54551804
print("C10 ratio = %.6f" % (M25 / W25))                                # -> 4.245263
```

（复算脚本输出与上述各值一致；比对阶段才读取 勾稽底稿.json 与 metrics.json。）
