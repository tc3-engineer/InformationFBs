# FB_EcExtSyncCheck

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete] DC 32-bit (§11.4)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2285537547.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcExtSyncCheck.TcPOU`](../examples/P_Demo_FB_EcExtSyncCheck.TcPOU) |

---

## 1. 功能简述

已弃用的 32-bit DC 时间体系下的同步 helper。本 FB 与对应的 64-bit 版（`FB_EcExtSyncCheck64`）功能一致，但用 `T_DCTIME`（32-bit）而非 `T_DCTIME64`。新工程统一用 64-bit 版。

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §11.4.2.9 原文表格与 InfoSys topic。由于本 FC / FB 已被官方标为 outdated，新工程应改用对应的 64-bit 版本，本仓库保留文档仅为维护老工程时查询使用。

## 3. 行为说明

**触发**：调用即异步处理。本 FB 用法和 64-bit 版相同，但 32-bit DC 时间表达范围有限（仅 4 秒），对长时间窗的同步监控不可靠。Beckhoff 官方明确把本 FB 归入 [obsolete]，新工程应避免使用。

**典型陷阱**：32-bit 回卷导致跨越 4 秒的差值计算错误。新工程应统一迁移到 64-bit 等价 FB 完成精密时间同步监控链。维护老工程时本 FB 仍可用作短时窗同步判定，但应在版本演进里同步排期下线。

## 4. 错误码 / 返回值

多数 outdated DC 转换 FC 不暴露错误输出，入参越界或回卷边界时返回值不可信。完整错误码语义请对照 PDF §11.4.2.9 原文表格。

## 5. 使用注意 / 常见坑

- **已弃用**：新工程统一用 64-bit 等价 FC / FB
- **32-bit 回卷**（工程经验补充）：4 秒回卷使得长时间窗业务不可靠
- **保留仅为兼容**：老工程仍可调用，但应优先排期迁移

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcExtSyncCheck.TcPOU`](../examples/P_Demo_FB_EcExtSyncCheck.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老工程兼容：早期版本使用本 FB 做同步监控，新工程统一迁移到 `FB_EcExtSyncCheck64` 64-bit 版。
- **价值**：维护老工程时仍能查到该 FC / FB 的文档
- **替代方案对比**：本 FC / FB 已被 64-bit 等价 FC / FB 取代；新工程统一迁移

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §11.4.2.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2285537547.html
- **相关 FB / FC**：`FB_EcExtSyncCheck64`（推荐替代）
