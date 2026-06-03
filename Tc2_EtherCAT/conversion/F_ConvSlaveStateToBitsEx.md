# F_ConvSlaveStateToBitsEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239485707.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvSlaveStateToBitsEx.TcPOU`](../examples/P_Demo_F_ConvSlaveStateToBitsEx.TcPOU) |

---

## 1. 功能简述

`F_ConvSlaveStateToBits` 的扩展版，返回 `ST_EcSlaveStateBitsEx`（含 4 端口 link 状态扩展位）。Ex 版多了 D 端口 link 状态等扩展字段，用于 EK1122 等 4 端口耦合器。

## 2. 接口定义

**FUNCTION 声明（PDF §10.6 原文）**：

> `FUNCTION F_ConvSlaveStateToBitsEx : ST_EcSlaveStateBitsEx`
>
> Inputs:
> - `stEcSlaveState : ST_EcSlaveState;`

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stEcSlaveState` | `ST_EcSlaveState` | — | 从站状态结构 |

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给结构体）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。返回 `ST_EcSlaveStateBitsEx`（详见 §13.13），比基础 Bits 版多含 4 端口 link 状态扩展位。基础版的字段在 Ex 版中都保留，所以从基础版升级到 Ex 版只需替换 FC 调用与结构体类型，业务判定字段可以保持不变。

**与 `F_ConvSlaveStateToBits` 选择**：
- 3 端口从站（EK1100 等）用基础版即可
- 4 端口从站（EK1122 等分支耦合器）用 Ex 版

**典型陷阱**：3 端口从站调本 FB 时 D 端口字段无意义，不要据此判定。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `ST_EcSlaveStateBitsEx` | 各 bit 字段已展开（含 4 端口 link） |

## 5. 使用注意 / 常见坑

- **4 端口从站专用**
- **D 端口字段**（工程经验补充）：仅 EK1122 等 4 端口设备有意义
- **与基础版兼容**：基础字段相同

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvSlaveStateToBitsEx.TcPOU`](../examples/P_Demo_F_ConvSlaveStateToBitsEx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：分支耦合器 EK1122 状态监视，需要看 D 端口是否连通
- **价值**：4 端口精度，分支链路诊断
- **替代方案对比**：基础 Bits 版 → 无 D 端口；本 FC → 完整

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239485707.html
- **相关 FB / FC**：`F_ConvSlaveStateToBits`、`ST_EcSlaveStateBitsEx`、`FB_EcGetSlaveCrcErrorEx`
