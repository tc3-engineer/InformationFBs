# F_ConvSlaveStateToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57078283.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvSlaveStateToString.TcPOU`](../examples/P_Demo_F_ConvSlaveStateToString.TcPOU) |

---

## 1. 功能简述

把 `ST_EcSlaveState`（含 deviceState + linkState）转换为可读字符串。内部调用 `F_ConvStateToString` 做 deviceState 翻译。是单从站状态可读化的标准 FC。

## 2. 接口定义

**FUNCTION 声明（PDF §10.4 原文）**：

> `FUNCTION F_ConvSlaveStateToString : T_MaxString`
>
> Inputs:
> - `state : ST_EcSlaveState;` （含 deviceState : BYTE; linkState : BYTE;）

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `state` | `ST_EcSlaveState` | — | 从站状态结构，由 `FB_EcGetSlaveState` 等读出 |

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给字符串）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。把 `state.deviceState` 翻译为可读字符串（INIT / PREOP / SAFEOP / OP 等）。多个错误位置位时空格分隔。本 FC 内部调用 `F_ConvStateToString` 处理 deviceState，二者输出格式一致；区别在于本 FC 接受结构体（适合 `FB_EcGetSlaveState` 输出），另一个接受 WORD（适合 `FB_EcGetMasterState` 输出）。

**典型用法**：HMI 从站详情页显示状态用。`sSlaveStateText := F_ConvSlaveStateToString(fbGetState.state)` 一行搞定。

**典型陷阱**：仅翻译 deviceState，linkState 未翻译；要看 linkState 用 `F_ConvSlaveStateToBits` 拆位。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| 状态字符串 | 如 `'OP'`、`'SAFEOP'`、`'INIT'` 或组合 |

## 5. 使用注意 / 常见坑

- **仅 deviceState 翻译**：linkState 单独看
- **HMI 直接显示**（工程经验补充）
- **配合 `FB_EcGetSlaveState`**：标准搭配

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvSlaveStateToString.TcPOU`](../examples/P_Demo_F_ConvSlaveStateToString.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 从站详情页"当前状态: OP"显示
- **价值**：HMI 直接绑字符串
- **替代方案对比**：HMI 自写 switch case → 重复；本 FC → 单点

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57078283.html
- **相关 FB / FC**：`F_ConvStateToString`、`F_ConvSlaveStateToBits`、`FB_EcGetSlaveState`、`ST_EcSlaveState`
