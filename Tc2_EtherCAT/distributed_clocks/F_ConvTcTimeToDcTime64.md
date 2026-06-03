# F_ConvTcTimeToDcTime64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Distributed Clocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2285558027.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvTcTimeToDcTime64.TcPOU`](../examples/P_Demo_F_ConvTcTimeToDcTime64.TcPOU) |

---

## 1. 功能简述

把 TwinCAT 系统时间转为 TwinCAT DC 系统时间。

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §11.3.2 原文表格与 InfoSys topic。多数 DC 转换 FC 的入参与返回值是单一类型转换（如 `T_DCTIME64` → `T_DCTIMESTRUCT`），调用方式直接 `output := F_xxx(input);`。同步类 FB（`FB_EcExtSyncCheck64` 等）通过 `bExecute` / `bBusy` 异步执行后输出结果。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。输入『TwinCAT 时间 + DcToTcTimeOffset』，输出 DC 时间。在 TwinCAT 与 DC 时间体系之间换算。

**典型用法**：业务里用 TwinCAT 时间记录事件，要同步到 DC 时间做物理同步。

**典型陷阱**：偏移由 `FB_EcExtSyncCheck64` 维护，业务侧不要硬编码。 本 FC 是 Tc-DC 偏移管理流程的标准 helper，通常封装在 sync monitor 任务中持续运行。

## 4. 错误码 / 返回值

多数 DC 转换 FC 不暴露错误输出，入参越界时返回值为 0 或饱和值（如 `nTimeDiff` 32-bit 溢出时返 `0xFFFFFFFF`）。同步类 FB（`FB_EcExtSyncCheck64` 等）通过 `bError` 表达错误。完整错误码语义请对照 PDF §11.3.2。

## 5. 使用注意 / 常见坑

- **DC 同步必须 OK**（工程经验补充）：所有 DC 转换之前先确认 `FB_EcExtSyncCheck64.bSynchronized = TRUE`
- **64-bit 优先**：新工程统一用 64-bit 体系，避免 32-bit 4 秒回卷
- **业务前置 gate**：DC 不同步时业务侧抑制本 FC 的输出进入执行链

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvTcTimeToDcTime64.TcPOU`](../examples/P_Demo_F_ConvTcTimeToDcTime64.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：参见 §1 与 §3 描述的典型应用；本 FC / FB 是 DC 同步精密时间业务的基础工具
- **价值**：把 EtherCAT DC 物理同步时间体系与业务可用时间格式打通
- **替代方案对比**：手算时间换算 → 易错；本 FC / FB → 标准且与 DC 体系一致

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §11.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2285558027.html
- **相关 FB / FC**：`F_ConvTcTimeToExtTime64`、`FB_EcExtSyncCheck64`
