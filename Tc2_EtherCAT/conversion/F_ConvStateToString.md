# F_ConvStateToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57081355.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvStateToString.TcPOU`](../examples/P_Demo_F_ConvStateToString.TcPOU) |

---

## 1. 功能简述

把 EtherCAT 从站状态字（WORD）转成可读字符串。`nState = 0` 返回空串；`nState = 1` 返回 `'INIT '`，多状态空格分隔。`F_ConvSlaveStateToString` 内部调用本 FC。

## 2. 接口定义

**FUNCTION 声明（PDF §10.7 原文）**：

> `FUNCTION F_ConvStateToString : T_MaxString`
>
> Inputs:
> - `nState : WORD;`

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nState` | `WORD` | — | 从站状态字 |

**状态位含义**：
- `0x___1` = 'INIT'
- `0x___2` = 'PREOP'
- `0x___4` = 'SAFEOP'
- `0x___8` = 'OP'
- 高位含错误位标识

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给字符串）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。是 `F_ConvSlaveStateToString` 的底层 FC —— 后者拿 `ST_EcSlaveState` 结构体，本 FC 直接拿 WORD。用法上常配合 `FB_EcGetMasterState` 输出（它返回 WORD 而非结构体）。二者的输出格式一致，只是入参类型不同，按调用方拿到的数据形态选择即可。

**典型用法**：`sMasterStateText := F_ConvStateToString(fbGetMaster.state);` 把主站状态 WORD 翻译。

**典型陷阱**：返回带空格的字符串（不仅是 'OP' 而是 'OP '），业务侧字符串匹配需注意 trim。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| 状态字符串 | 如 `'OP '`、`'INIT '` 或组合 |

## 5. 使用注意 / 常见坑

- **与 `F_ConvSlaveStateToString` 选择**：拿 WORD 用本 FC；拿结构体用 `F_ConvSlaveStateToString`
- **返回含空格**（工程经验补充）：业务侧 trim
- **HMI 字符串显示**：直接绑

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvStateToString.TcPOU`](../examples/P_Demo_F_ConvStateToString.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示主站状态 —— `FB_EcGetMasterState` 输出 WORD，本 FC 翻译成字符串
- **价值**：底层位掩码 → 业务可读
- **替代方案对比**：HMI 自写 → 重复；本 FC → 单点

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57081355.html
- **相关 FB / FC**：`F_ConvSlaveStateToString`（拿结构体）、`FB_EcGetMasterState`、`FB_EcGetSlaveState`
