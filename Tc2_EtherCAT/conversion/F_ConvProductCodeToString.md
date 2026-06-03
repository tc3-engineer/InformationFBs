# F_ConvProductCodeToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57076747.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvProductCodeToString.TcPOU`](../examples/P_Demo_F_ConvProductCodeToString.TcPOU) |

---

## 1. 功能简述

把从站身份信息（`ST_EcSlaveIdentity`）转换为可读产品代码字符串，例如 `'EL6731-0000-0017'`。Tc2_EtherCAT 3.3.8.0 起也支持 ELM/EPP 系列如 `'EPP4374-0002-0018'` 与 `'ELM3704-0001-0016'`。

## 2. 接口定义

**FUNCTION 声明（PDF §10.3 原文）**：

> `FUNCTION F_ConvProductCodeToString : T_MaxString`
>
> Inputs:
> - `stSlaveIdentity : ST_EcSlaveIdentity;`

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stSlaveIdentity` | `ST_EcSlaveIdentity` | — | 从站身份信息，由 `FB_EcGetSlaveIdentity` 读出 |

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给字符串）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。把从站 `ST_EcSlaveIdentity` 中的 productCode 与 revisionNumber 等字段格式化为标准产品代码字符串。Beckhoff 产品命名约定如 `EL6731-0000-0017`，前缀 EL/EK/EP/ELM/EPP 等标识产品族，后跟版本与子型号编号。

**典型用法**：先用 `FB_EcGetSlaveIdentity` 取身份结构，再调本 FC 拿产品名称字符串。HMI 显示从站清单时直接用本 FC 输出，免去 HMI 端字符串拼接。

**典型陷阱**：第三方从站（非 Beckhoff）可能返回非标准字符串，需在业务侧加判定；ELM/EPP 支持需要 Tc2_EtherCAT ≥ 3.3.8.0。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| 产品代码字符串 | 如 `'EL6731-0000-0017'` |

## 5. 使用注意 / 常见坑

- **版本要求**：ELM/EPP 支持需 ≥ 3.3.8.0
- **第三方处理**（工程经验补充）：非 Beckhoff 返回值需业务侧验证

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvProductCodeToString.TcPOU`](../examples/P_Demo_F_ConvProductCodeToString.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 从站清单页：每行显示"序号 + 产品代码 + 状态"。本 FC 把 productCode 字段格式化成 'EL3008-0000-0017' 直接显示
- **价值**：HMI 直接绑字符串，免去手工拼接
- **替代方案对比**：HMI 自拼字符串 → 易错；本 FC → 标准格式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57076747.html
- **相关 FB / FC**：`FB_EcGetSlaveIdentity`、`ST_EcSlaveIdentity`、`F_CheckVendorId`
