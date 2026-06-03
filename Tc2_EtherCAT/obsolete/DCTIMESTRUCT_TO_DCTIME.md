# DCTIMESTRUCT_TO_DCTIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `[obsolete] DC 32-bit (§11.4)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57062923.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_DCTIMESTRUCT_TO_DCTIME.TcPOU`](../examples/P_Demo_DCTIMESTRUCT_TO_DCTIME.TcPOU) |

---

## 1. 功能简述

已弃用的 DC 时间转换 FUNCTION。本 FC 操作的是 `T_DCTIME`（32-bit）类型；Beckhoff 推荐改用 64-bit 版（如 `DCTIME64STRUCT_TO_DCTIME6464` 或对应 64-bit FC）。新工程不要使用本 FC。

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §11.4.1.5 原文表格与 InfoSys topic。由于本 FC / FB 已被官方标为 outdated，新工程应改用对应的 64-bit 版本，本仓库保留文档仅为维护老工程时查询使用。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。本 FC 是早期 32-bit DC 时间体系的转换 helper，与对应 64-bit 版功能等价，区别仅在入参/返回值类型。32-bit DC 时间约 4 秒回卷使得本 FC 实际可用时间窗很小，Beckhoff 官方 PDF §11.4 已把这一系列 FC 归入 outdated，新工程应统一迁移到 64-bit 体系。

**典型陷阱**：32-bit 回卷导致超过 4 秒的转换出现歧义。

## 4. 错误码 / 返回值

多数 outdated DC 转换 FC 不暴露错误输出，入参越界或回卷边界时返回值不可信。完整错误码语义请对照 PDF §11.4.1.5 原文表格。

## 5. 使用注意 / 常见坑

- **已弃用**：新工程统一用 64-bit 等价 FC / FB
- **32-bit 回卷**（工程经验补充）：4 秒回卷使得长时间窗业务不可靠
- **保留仅为兼容**：老工程仍可调用，但应优先排期迁移

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCTIMESTRUCT_TO_DCTIME.TcPOU`](../examples/P_Demo_DCTIMESTRUCT_TO_DCTIME.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老工程兼容场景：早期工程使用 32-bit DC 时间链路，新工程统一迁移到 64-bit。
- **价值**：维护老工程时仍能查到该 FC / FB 的文档
- **替代方案对比**：本 FC / FB 已被 64-bit 等价 FC / FB 取代；新工程统一迁移

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §11.4.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57062923.html
- **相关 FB / FC**：对应 64-bit 等价 FC（推荐替代）
