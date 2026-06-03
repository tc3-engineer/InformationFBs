# F_ConvBK1120CouplerStateToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57073675.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvBK1120CouplerStateToString.TcPOU`](../examples/P_Demo_F_ConvBK1120CouplerStateToString.TcPOU) |

---

## 1. 功能简述

把 BK1120/BK1150/BK1250 总线耦合器状态字（WORD）转成可读字符串。`nState = 0` 返回 `'No error'`；非零按位掩码列出对应错误，多错误用逗号分隔。

## 2. 接口定义

**FUNCTION 声明（PDF §10.1 原文）**：

> `FUNCTION F_ConvBK1120CouplerStateToString : T_MaxString`
>
> Inputs:
> - `nState : WORD;` 耦合器状态

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nState` | `WORD` | — | BK 总线耦合器状态字，可从 System Manager 中 BK 耦合器输入连到 PLC 的 inputs 取得 |

**状态位含义**：
- `0x0000` = No error
- `0x0001` = K-Bus error
- `0x0002` = Configuration error
- `0x0010` = Outputs disabled
- `0x0020` = K-Bus overrun
- `0x0040` = Communication error (Inputs)
- `0x0080` = Communication error (Outputs)

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给字符串）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。本 FB 把位掩码翻译成人类可读字符串。`nState = 0` 返回 `'No error'`；多个错误位同时置时返回逗号分隔的字符串，例如 `nState = 16#0021` 返回类似 `'K-Bus error, K-Bus overrun'`。

**典型用法**：HMI 显示 BK 耦合器状态，直接绑本 FB 输出，无需 HMI 端自己解码位掩码。配合 System Manager 中 BK1120/BK1150/BK1250 的 PLC 输入链接，PLC 把 WORD 状态字传入本 FB 即得字符串。

**典型陷阱**：返回是字符串而非枚举，做业务比较时要注意大小写与精确匹配。`nState` WORD 高字节通常未用，只看低字节也行。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `'No error'` | 状态正常 |
| 含错误位字符串 | 列出每个置位错误，逗号分隔 |

## 5. 使用注意 / 常见坑

- **HMI 友好**：直接绑返回字符串
- **PLC 业务判定**：不要按字符串匹配，按 nState 位判断更可靠
- **BK 系列专用**（工程经验补充）：仅 BK1120/BK1150/BK1250 模式有效

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvBK1120CouplerStateToString.TcPOU`](../examples/P_Demo_F_ConvBK1120CouplerStateToString.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：现场用 BK1120 接 K-Bus 端子模块，HMI 状态总览页要显示"BK1120 状态: K-Bus error" 而非"0x0001"
- **价值**：把数字状态字翻译成可读字符串，让 HMI 工程师不必懂位掩码
- **替代方案对比**：HMI 端自己写转换逻辑 → 重复劳动；本 FC → 单点复用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57073675.html
- **相关 FB / FC**：`F_ConvMasterDevStateToString`、`F_ConvSlaveStateToString`
