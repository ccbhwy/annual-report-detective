#!/bin/bash
# 拉取东方财富F10财报数据 -> 02_实际产出/原始数据/
set -u
OUT="/d/AI_Project/zuopin/02_实际产出/原始数据"
BASE='https://datacenter.eastmoney.com/securities/api/data/v1/get'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

fetch() { # $1=url $2=file
  curl -s -m 25 -A "$UA" -H "Referer: https://emweb.securities.eastmoney.com/" "$1" -o "$OUT/$2"
  local sz=$(stat -c%s "$OUT/$2" 2>/dev/null || echo 0)
  echo "$2 : ${sz} bytes"
}

STATEMENTS="GBALANCE GINCOME GCASHFLOW"
for st in $STATEMENTS; do
  f=$(echo "$st" | tr 'A-Z' 'a-z')
  case $st in GBALANCE) f=balance;; GINCOME) f=income;; GCASHFLOW) f=cashflow;; esac
  fetch "$BASE?reportName=RPT_F10_FINANCE_${st}&columns=ALL&filter=(SECUCODE%3D%22600519.SH%22)&pageNumber=1&pageSize=24&sortTypes=-1&sortColumns=REPORT_DATE&source=HSF10&client=PC" "${f}_600519.json"
done

for s in 000858.SZ 000568.SZ 600809.SH; do
  fetch "$BASE?reportName=RPT_F10_FINANCE_MAINFINADATA&columns=ALL&filter=(SECUCODE%3D%22$s%22)&pageNumber=1&pageSize=40&sortTypes=-1&sortColumns=REPORT_DATE&source=HSF10&client=PC" "main_${s%%.*}.json"
done
echo "done"
