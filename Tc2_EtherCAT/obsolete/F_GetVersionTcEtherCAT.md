# F_GetVersionTcEtherCAT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `[obsolete] Library Version (§12)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/57099531.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcEtherCAT.TcPOU`](../examples/P_Demo_F_GetVersionTcEtherCAT.TcPOU) |

---

## 1. 功能简述

已弃用的库版本读取 FUNCTION，曾返回 Tc2_EtherCAT 库的版本号组件。Beckhoff 推荐改用全局结构 `stLibVersion_Tc2_EtherCAT` 替代本 FC，新工程不要再调用本 FC。

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §12.1 原文表格与 InfoSys topic。由于本 FC / FB 已被官方标为 outdated，新工程应改用对应的 64-bit 版本，本仓库保留文档仅为维护老工程时查询使用。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。`nVersionElement = 1` 返回 major，`2` 返回 minor，`3` 返回 revision。返回值 `UINT`。Beckhoff 官方 PDF §12.1 明确标记本 FC 为 outdated，新代码应改用 `stLibVersion_Tc2_EtherCAT.iMajor`、`.iMinor`、`.iBuild` 直接取字段。

**典型陷阱**：本 FC 不会消失但已不再演进；后续 Tc2_EtherCAT 版本号字段如有变化（如 build）本 FC 无法返回。现有老工程引用本 FC 可以暂时保留，但应在维护版本中替换为 GVL 字段访问。

## 4. 错误码 / 返回值

多数 outdated DC 转换 FC 不暴露错误输出，入参越界或回卷边界时返回值不可信。完整错误码语义请对照 PDF §12.1 原文表格。

## 5. 使用注意 / 常见坑

- **已弃用**：新工程统一用 64-bit 等价 FC / FB
- **32-bit 回卷**（工程经验补充）：4 秒回卷使得长时间窗业务不可靠
- **保留仅为兼容**：老工程仍可调用，但应优先排期迁移

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcEtherCAT.TcPOU`](../examples/P_Demo_F_GetVersionTcEtherCAT.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老工程兼容场景：早期代码用 `F_GetVersionTcEtherCAT(1)` 拿主版本号判定是否启用新 API。迁移路径：把所有调用替换成 `stLibVersion_Tc2_EtherCAT.iMajor` 直接读全局 GVL。
- **价值**：维护老工程时仍能查到该 FC / FB 的文档
- **替代方案对比**：本 FC / FB 已被 64-bit 等价 FC / FB 取代；新工程统一迁移

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §12.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/57099531.html
- **相关 FB / FC**：`stLibVersion_Tc2_EtherCAT`（推荐替代）、`Tc2_System.F_GetVersion*`
