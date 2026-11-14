# 「年报侦探」AutoClaw 创造力挑战第六期 · 参赛作品包

> 自由创作赛道｜多 Agent 工作流｜AutoClaw 实测：74 项勾稽全过 / 独立复算 10/10
> 产出：HTML 体检报告 · Excel 勾稽底稿 · 发布文案与配图

## 这是什么

一套**上市公司年报体检工作流**：5 个 AI Agent 分工协作（取数 → 勾稽 → 质疑 → 核查 → 终审），
三道核验关（74 项勾稽、红队对抗、独立复算），把一份年报变成一页带证据链的体检报告。

已用贵州茅台 2025 年报实测：**勾稽 74/74 通过，独立复算 10/10 一致**，产出可直接截图的报告与底稿。

## 目录导航

```
zuopin/
├── README.md                      ← 你在这里
├── 01_工作流蓝图/
│   ├── blueprint.md               ← 工作流设计文档（5角色/3道关）
│   └── 主指令_AutoClaw.md         ← ★ 可直接粘贴进 AutoClaw 的完整指令
├── 02_实际产出/                    ← 全部真实产物
│   ├── 年报体检报告_贵州茅台2025.html   ← ★ 核心作品，浏览器打开即可截图
│   ├── 勾稽底稿_贵州茅台2025.xlsx       ← 5 sheet 数据底稿
│   ├── agent_log.md               ← 多Agent运行日志（诚实台账）
│   ├── Agent输出_质疑Agent.md     ← 红队报告（6项发现）
│   ├── Agent输出_核查Agent.md     ← 终审核验报告（10/10）
│   ├── 勾稽底稿.json / metrics.json ← 计算中间产物
│   └── 原始数据/                   ← 东财F10原始JSON（证据链）
└── scripts/                       ← 全部可复现脚本
    ├── fetch_data.sh / compute_checks.py / build_report.py / build_xlsx.py
```

## 复现方式

```bash
bash scripts/fetch_data.sh          # 抓取原始数据
python -I scripts/compute_checks.py # 勾稽计算
python -I scripts/build_report.py   # 生成HTML报告
python -I scripts/build_xlsx.py     # 生成Excel底稿
```
