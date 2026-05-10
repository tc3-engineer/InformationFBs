# Blocked

> 由 `/discover` `/doc-shard` `/verify` 命令在抓取或验证失败时追加。每条带 UTC 时间、原因、可能的解决路径。

---

## 2026-05-10 · Tc2_Standard / Trigger / 全批

- **触发命令**: `/doc-shard Tc2_Standard Trigger`
- **目标条目**: `F_TRIG`, `R_TRIG`（roadmap 中两条 pending）
- **原因**: 官方 PDF 与 InfoSys 两个可信源在本 session 网络环境下均返回 HTTP 403：
  - `https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf` → 403 Forbidden
  - `https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/index.html` → 403 Forbidden
- **CLAUDE.md 硬规则约束**:
  - 不允许用第三方资料 / 训练数据记忆补全
  - PDF 非 200 时必须记录到 `blocked.md`，且不允许私自切换到 InfoSys
- **状态**: F_TRIG / R_TRIG 未生成（既未写文档也未写例程），保持 `pending`
- **解除路径**:
  1. 在 [claude.ai/code](https://claude.ai/code) 把 session 环境改为 Custom，将 `download.beckhoff.com` 与 `infosys.beckhoff.com` 加入允许列表（详见仓库 README 第 3 节 "一次性配置"）
  2. 重新执行 `/doc-shard Tc2_Standard Trigger`
- **本批未做修改的文件**（避免半成品）:
  - `Tc2_Standard/trigger/F_TRIG.md`（仍未创建）
  - `Tc2_Standard/trigger/R_TRIG.md`（仍未创建）
  - `Tc2_Standard/examples/P_Demo_F_TRIG.xml`（仍未创建）
  - `Tc2_Standard/examples/P_Demo_R_TRIG.xml`（仍未创建）
