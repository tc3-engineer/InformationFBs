# DCTIME_TO_DCTIME64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Distributed Clocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2267334667.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_DCTIME_TO_DCTIME64.TcPOU`](../examples/P_Demo_DCTIME_TO_DCTIME64.TcPOU) |

---

## 1. 功能简述

把 32-bit `T_DCTIME` 转换为 64-bit `T_DCTIME64`。32-bit DC 时间约 4 秒就回卷一次，64-bit 范围扩展到几百年，业务一般用 64-bit 版本。

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §11.2.1 原文表格与 InfoSys topic。多数 DC 转换 FC 的入参与返回值是单一类型转换（如 `T_DCTIME64` → `T_DCTIMESTRUCT`），调用方式直接 `output := F_xxx(input);`。同步类 FB（`FB_EcExtSyncCheck64` 等）通过 `bExecute` / `bBusy` 异步执行后输出结果。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。把传入的 `T_DCTIME` 值（32-bit）放大为 `T_DCTIME64`（64-bit），高位补 0。本 FC 用于兼容旧 32-bit DC 时间到新 64-bit 体系。

**典型陷阱**：32-bit `T_DCTIME` 仅表示 0 ~ 4 s 范围；超出后已回卷，本 FC 无法恢复原始 64-bit 值。仅适用于『已知刚发生』的短时窗时间转换。 本 FC 主要用于把旧式 32-bit DC 时间适配进新 64-bit 业务流，新工程统一用 64-bit 可避免本 FC 的回卷盲区。

## 4. 错误码 / 返回值

多数 DC 转换 FC 不暴露错误输出，入参越界时返回值为 0 或饱和值（如 `nTimeDiff` 32-bit 溢出时返 `0xFFFFFFFF`）。同步类 FB（`FB_EcExtSyncCheck64` 等）通过 `bError` 表达错误。完整错误码语义请对照 PDF §11.2.1。

## 5. 使用注意 / 常见坑

- **DC 同步必须 OK**（工程经验补充）：所有 DC 转换之前先确认 `FB_EcExtSyncCheck64.bSynchronized = TRUE`
- **64-bit 优先**：新工程统一用 64-bit 体系，避免 32-bit 4 秒回卷
- **业务前置 gate**：DC 不同步时业务侧抑制本 FC 的输出进入执行链

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCTIME_TO_DCTIME64.TcPOU`](../examples/P_Demo_DCTIME_TO_DCTIME64.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：参见 §1 与 §3 描述的典型应用；本 FC / FB 是 DC 同步精密时间业务的基础工具
- **价值**：把 EtherCAT DC 物理同步时间体系与业务可用时间格式打通
- **替代方案对比**：手算时间换算 → 易错；本 FC / FB → 标准且与 DC 体系一致

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §11.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2267334667.html
- **相关 FB / FC**：`DCTIME64_TO_DCTIME`（逆运算）、`T_DCTIME`、`T_DCTIME64`
