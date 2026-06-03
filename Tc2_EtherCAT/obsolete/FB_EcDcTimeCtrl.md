# FB_EcDcTimeCtrl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete] DC 32-bit (§11.4)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57084427.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcDcTimeCtrl.TcPOU`](../examples/P_Demo_FB_EcDcTimeCtrl.TcPOU) |

---

## 1. 功能简述

已弃用的 32-bit DC 时间组件提取 FB；功能等同 `FB_EcDcTimeCtrl64`，但入参类型为 `T_DCTIME`（32-bit）而非 `T_DCTIME64`。Beckhoff 推荐改用 64-bit 版。

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §11.4.1.9 原文表格与 InfoSys topic。由于本 FC / FB 已被官方标为 outdated，新工程应改用对应的 64-bit 版本，本仓库保留文档仅为维护老工程时查询使用。

## 3. 行为说明

**触发**：通过 method action（`A_GetYear` 等）提取组件。本 FB 与 `FB_EcDcTimeCtrl64` 行为一致，区别仅在入参类型，32-bit DC 时间约 4 秒回卷使得本 FB 实际可用时间窗很小。Beckhoff 官方建议新工程统一用 64-bit 版以避免回卷盲区。

**典型陷阱**：32-bit 回卷使得跨越 4 秒边界的时间提取结果不可信。

## 4. 错误码 / 返回值

多数 outdated DC 转换 FC 不暴露错误输出，入参越界或回卷边界时返回值不可信。完整错误码语义请对照 PDF §11.4.1.9 原文表格。

## 5. 使用注意 / 常见坑

- **已弃用**：新工程统一用 64-bit 等价 FC / FB
- **32-bit 回卷**（工程经验补充）：4 秒回卷使得长时间窗业务不可靠
- **保留仅为兼容**：老工程仍可调用，但应优先排期迁移

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcDcTimeCtrl.TcPOU`](../examples/P_Demo_FB_EcDcTimeCtrl.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老工程兼容：早期 32-bit DC 时间 API 现仍可用但不再演进；迁移到 `FB_EcDcTimeCtrl64`+ `T_DCTIME64` 体系是新工程的标准实践。
- **价值**：维护老工程时仍能查到该 FC / FB 的文档
- **替代方案对比**：本 FC / FB 已被 64-bit 等价 FC / FB 取代；新工程统一迁移

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §11.4.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57084427.html
- **相关 FB / FC**：`FB_EcDcTimeCtrl64`（推荐替代）、`T_DCTIME`、`T_DCTIME64`
