# F_CheckVendorId

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/57096587.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CheckVendorId.TcPOU`](../examples/P_Demo_F_CheckVendorId.TcPOU) |

---

## 1. 功能简述

判断给定的从站身份信息（`ST_EcSlaveIdentity`）是否来自 Beckhoff。返回 `BOOL`：是 Beckhoff 返回 `TRUE`，否则 `FALSE`。常用于厂商白名单校验或选择"Beckhoff 专有诊断逻辑"分支。

## 2. 接口定义

**FUNCTION 声明（PDF §4.22 原文逐字）**：

> `METHOD F_CheckVendorId : BOOL`（PDF 印刷为 METHOD，实际是 FUNCTION，行为等同）
>
> Inputs:
> - `stSlaveIdentity : ST_EcSlaveIdentity;`

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stSlaveIdentity` | `ST_EcSlaveIdentity` | — | 从站身份信息，由 `FB_EcGetSlaveIdentity` 读出 |

### VAR_OUTPUT

无（FUNCTION 通过返回值给结果）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：FUNCTION 同步执行，不需要 `bExecute` 触发。本质等价于 `stSlaveIdentity.vendorId = 16#00000002`（Beckhoff 的 EtherCAT Vendor ID）。调用本身不产生任何总线流量，仅是一次结构体字段比较，所以可以在任意 PLC 周期任意频率调用，不会影响 EtherCAT 网络性能或主站负载。

**返回值**：
- `TRUE`：`stSlaveIdentity.vendorId` 等于 Beckhoff 厂商 ID `16#00000002`
- `FALSE`：是其他厂商或 Vendor ID = 0（无效）

**典型用法**：
- 配合 `FB_EcGetSlaveIdentity` 做"厂商白名单"：装错牌子的从站直接报警
- "Beckhoff 专属诊断 FB" 入口判定：第三方从站走通用 SDO，Beckhoff 走专有逻辑
- 工程升级时校验现场实物厂商与配置预期一致

**典型陷阱**：
- 只检查 vendorId，不检查 productCode；EL3008 + EL3068 都是 Beckhoff，本 FC 都返 TRUE
- `stSlaveIdentity` 必须先用 `FB_EcGetSlaveIdentity` 读到才有效

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | Beckhoff 厂商 | 通过白名单 |
| `FALSE` | 非 Beckhoff / 无效 | 看 `vendorId` 字段定具体来源 |

## 5. 使用注意 / 常见坑

- **同步函数**：直接调用即可，无异步状态机
- **`stSlaveIdentity` 必须先填**：缺少 FB_EcGetSlaveIdentity 先读会返 FALSE（vendorId = 0）
- **作为入口判定**（工程经验补充）：写跨厂商兼容代码时是 IF/ELSE 主要判据

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CheckVendorId.TcPOU`](../examples/P_Demo_F_CheckVendorId.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：客户现场允许装第三方 EtherCAT 从站做特定功能；PLC 端对 Beckhoff 从站调专有 `FB_EcCoeReadBIC` 取 BIC，对第三方走通用 SDO 0x1018 取 vendor / product
- **价值**：把"厂商分支选择"封装成一行 IF
- **替代方案对比**：手写 `vendorId = 16#00000002` → 各处散落易错；本 FC → 单点维护

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.22
- **InfoSys topic**：https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/57096587.html
- **相关 FB / FC**：`FB_EcGetSlaveIdentity`（取身份）、`ST_EcSlaveIdentity`、`F_ConvProductCodeToString`
