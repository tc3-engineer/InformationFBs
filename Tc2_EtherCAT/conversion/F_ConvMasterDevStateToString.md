# F_ConvMasterDevStateToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `Conversion Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57075211.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ConvMasterDevStateToString.TcPOU`](../examples/P_Demo_F_ConvMasterDevStateToString.TcPOU) |

---

## 1. 功能简述

把 EtherCAT 主站设备状态字（`FB_EcGetMasterDevState.nDevState`）转成可读字符串。`nState = 0` 返回 `'OK'`；非零按位列出错误，多错误用连字符分隔。

## 2. 接口定义

**FUNCTION 声明（PDF §10.2 原文）**：

> `FUNCTION F_ConvMasterDevStateToString : T_MaxString`
>
> Inputs:
> - `nState : WORD;` 主站设备状态

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nState` | `WORD` | — | 主站 DevState；可从 System Manager 中 EtherCAT 主站 inputs 链到 PLC |

**状态位含义**（部分）：
- `0x0001` = Link error
- `0x0002` = I/O locked after link error
- `0x0004` = Link error (redundancy adapter)
- `0x0008` = Missing one frame (redundancy mode)
- `0x0010` = Out of send resources
- `0x0020` = Watchdog triggered
- `0x0040` = Ethernet driver (miniport) not found
- `0x0080` = I/O reset active
- `0x0100` = At least one device in 'INIT' state
- `0x0200` = At least one device in 'PRE-OP' state
- `0x0400` = At least one device in 'SAFE-OP' state
- `0x0800` = At least one device indicates an error state
- `0x1000` = DC not in sync

### VAR_OUTPUT 参数

无（FUNCTION 通过返回值给字符串）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION。把 WORD 状态字翻成人类可读字符串，多错误用连字符分隔。是 `FB_EcGetMasterDevState` 输出的标准伴侣 FC —— 二者一起用是 HMI 主页"主站健康度"指示灯的标准实现。

**典型用法**：`sMasterStateText := F_ConvMasterDevStateToString(fbGetState.nDevState);` 业务侧直接绑 sMasterStateText 给 HMI。`nState = 0` 时返回 `'OK'`，HMI 显示绿灯；非 0 时返回错误描述串，HMI 显红灯并 tooltip 显示具体原因。

**典型陷阱**：返回是字符串，业务判定应该看原始 nState 而非字符串比较。多错误位置位时字符串可能较长，HMI 文本框要够宽。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `'OK'` | nState = 0，主站正常 |
| 含错误描述 | 列出每个置位错误，连字符分隔 |

## 5. 使用注意 / 常见坑

- **配合 `FB_EcGetMasterDevState`**：标准搭配
- **HMI 文本框宽度**（工程经验补充）：多错误时字符串可能 > 80 字符
- **业务判定不要按字符串**：按 nState 位掩码

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ConvMasterDevStateToString.TcPOU`](../examples/P_Demo_F_ConvMasterDevStateToString.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 主页"主站健康度"指示灯。绿 = 'OK'，红 = 错误（鼠标 hover tooltip 显示具体错误串）
- **价值**：底层位掩码 → 业务可读
- **替代方案对比**：HMI 自写解码 → 重复且滞后；本 FC → 单点维护

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §10.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57075211.html
- **相关 FB / FC**：`FB_EcGetMasterDevState`、`F_ConvSlaveStateToString`、`F_ConvStateToString`
