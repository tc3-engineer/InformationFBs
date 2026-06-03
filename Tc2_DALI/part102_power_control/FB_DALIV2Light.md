# FB_DALIV2Light

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Power Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2Light.TcPOU`](../examples/P_Demo_FB_DALIV2Light.TcPOU) |

---

## 1. 功能简述

**最简单的 DALI 开关 FB（high-level）**——`bSwitch` 电平 = 开关状态，TRUE 时灯调到 `nOnValue`，FALSE 时关灯。无调光功能。专门用于纯开关功能场景：洗手间灯、走廊感应灯、工业开关灯具等不需要 PLC 调光的应用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bOn                        : BOOL;
    bOff                       : BOOL;
    bToggle                    : BOOL;
    nAddr                      : BYTE             := 0;
    eAddrType                  : E_DALIV2AddrType := eDALIV2AddrTypeShort;
    nMasterDevAddr             : BYTE             := 0;
    tCycleActualLevelMasterDev : TIME             := t#0s;
    bLight                     : BOOL;
    bBusy                      : BOOL;
    bError                     : BOOL;
    nErrorId                   : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bOn` | `BOOL` | — | ⚠️ 待人工确认 |
| `bOff` | `BOOL` | — | ⚠️ 待人工确认 |
| `bToggle` | `BOOL` | — | ⚠️ 待人工确认 |
| `nAddr` | `BYTE` | `0` | 目标地址 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型 |
| `nMasterDevAddr` | `BYTE` | `0` | ⚠️ 待人工确认 |
| `tCycleActualLevelMasterDev` | `TIME` | `t#0s` | ⚠️ 待人工确认 |
| `bLight` | `BOOL` | — | ⚠️ 待人工确认 |
| `bBusy` | `BOOL` | — | ⚠️ 待人工确认 |
| `bError` | `BOOL` | — | ⚠️ 待人工确认 |
| `nErrorId` | `UDINT` | — | ⚠️ 待人工确认 |

### VAR_OUTPUT
无

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量 |


## 3. 行为说明

**电平触发**：`bSwitch` 变化时本 FB 发一次 DAPC（TRUE → `nOnValue`，FALSE → 0）；电平稳定后不重发。

**调用频率**：因为只在 `bSwitch` 变化时发命令，本 FB 不占用 DALI 总线带宽。

**典型应用**：（1）感应器联动——红外感应器触发，本 FB 切换灯具；（2）定时灯——PLC 时钟到点把 `bSwitch` 写 FALSE；（3）紧急联动——消防触发把 `bSwitch` 强制 FALSE。

**与 `Dimmer1Switch` 区别**：本 FB 仅开关，无调光，更简单；调光场景应用 `Dimmer1Switch`。

**典型陷阱**：① `nOnValue = 0` 时『开』变成『关』，无意义；② 多个本 FB 实例控同一灯具时互相覆盖。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 无调光功能，纯开关。
- `nOnValue` 不要设为 0。
- 电平触发，无去抖（输入信号要稳定）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Light.TcPOU`](../examples/P_Demo_FB_DALIV2Light.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：走廊红外感应器联动：感应到人触发开灯（`bSwitch := TRUE`），离开 30 秒后关灯。
- **价值**：替代手写一行 DAPC——封装了 DALI 命令排队 / 错误处理；专用于不需要调光的场景。
- **替代方案对比**：1) `FB_DALIV2Dimmer1Switch`：单按钮调光，过于复杂；2) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=0 or value)`：底层命令；3) **本 FB**：纯开关场景最简方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.2.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142916747.html
- **相关**：[`FB_DALIV2Dimmer1Switch`](FB_DALIV2Dimmer1Switch.md)（带调光）、[`FB_DALIV2LightControl`](FB_DALIV2LightControl.md)（带自动 / 手动模式切换）、[`FB_DALIV2StairwellDimmer`](FB_DALIV2StairwellDimmer.md)（楼梯间自动延时关灯）
