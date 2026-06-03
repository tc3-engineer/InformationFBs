# F_ConvSlaveStateToBits

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57079819.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvSlaveStateToBits.TcPOU`](../examples/P_Demo_F_ConvSlaveStateToBits.TcPOU) |

---

## 1. 功能简述

把 `ST_EcSlaveState` 拆解为 `ST_EcSlaveStateBits` 位结构，让业务侧用具名 bit 字段（如 `bInit`、`bPreOp`、`bSafeOp`、`bOp`、`bErr`、`bLinkOk` 等）直接判定，比手工 AND 位掩码更可读。

## 2. 接口定义

**FUNCTION 声明（PDF §10.5 原文）**：

> `FUNCTION F_ConvSlaveStateToBits : ST_EcSlaveStateBits`
>
> Inputs:
> - `stEcSlaveState : ST_EcSlaveState;` （含 deviceState : BYTE; linkState : BYTE;）

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stEcSlaveState` | `ST_EcSlaveState` | — | 从站状态结构 |

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给结构体）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。把 `state.deviceState` 中各 bit 拆到 `ST_EcSlaveStateBits` 结构对应字段，业务侧直接判定 `bits.bOp` 比 `state.deviceState = 0x08` 可读。

**`ST_EcSlaveStateBits` 字段**（详见 §13.12）：含 `bInit`、`bPreOp`、`bSafeOp`、`bOp`、`bErr`、`bLinkOk` 等。每一位对应 deviceState / linkState 的一个语义 bit，让业务侧无需懂位掩码即可写状态判定逻辑。配合 `FB_EcGetSlaveState` 输出，是从位掩码到具名字段的标准桥接 FC。

**典型用法**：业务条件判定中替代位掩码运算。`IF F_ConvSlaveStateToBits(state).bOp THEN ...` 比 `IF state.deviceState = 16#08 THEN ...` 更易读。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `ST_EcSlaveStateBits` | 各 bit 字段已展开 |

## 5. 使用注意 / 常见坑

- **可读性优先**：业务判定首选本 FC
- **性能影响**（工程经验补充）：FC 调用本身极轻，无性能负担
- **配 Ex 版**：扩展位用 `F_ConvSlaveStateToBitsEx`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvSlaveStateToBits.TcPOU`](../examples/P_Demo_F_ConvSlaveStateToBits.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：业务条件 `if 从站在 OP 且无错误 then` 写成 `IF stBits.bOp AND NOT stBits.bErr THEN`，比位掩码运算可读
- **价值**：业务代码可读性
- **替代方案对比**：手算位掩码 → 易错；本 FC → 具名字段

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57079819.html
- **相关 FB / FC**：`F_ConvSlaveStateToBitsEx`、`ST_EcSlaveStateBits`、`F_ConvSlaveStateToString`
