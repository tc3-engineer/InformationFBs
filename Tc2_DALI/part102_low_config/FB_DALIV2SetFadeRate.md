# FB_DALIV2SetFadeRate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2SetFadeRate.TcPOU`](../examples/P_Demo_FB_DALIV2SetFadeRate.TcPOU) |

---

## 1. 功能简述

**设置镇流器 `FADE RATE` 寄存器**——DALI 镇流器内部存一个 `FADE RATE`（1..15）寄存器，决定 `Up` / `Down` 这类连续步进调光命令每秒的亮度变化步数。值越小变化越快。本 FB 把目标值（输入参数）通过 DTR0 写入灯具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nFadeRate        : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nFadeRate` | `BYTE` | — | 目标 `FADE RATE` 索引值 1..15（0 是非法值）。对应每秒的亮度变化步数：1 = 357.6 步/秒（最快）/ 7 = 11.18（默认）/ 15 = 0.044（最慢）。控制 `FB_DALIV2Up` / `Down` 等连续调光命令的速率 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrorId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE |
| `bError` | `BOOL` | 执行错时置 TRUE；下次 `bStart` 上升沿自动复位 |
| `nErrorId` | `UDINT` | 错误号（命令专用）；详见 §4 错误码表与全库错误码（PDF §4.1.4） |

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

**调用方式**：`bStart` 上升沿；本 FB 先发 `SET DTR` 命令把 `nFadeRate` 写入 DTR0 寄存器，再发 `STORE THE DTR AS FADE RATE` 命令把 DTR0 内容写入灯具的 `FADE RATE` 寄存器（EEPROM 失电保护）。

**`FADE RATE` 影响范围**：仅影响 `FB_DALIV2Up` / `Down` / `StepUp` / `StepDown` 这类逐步调光命令；不影响 `DAPC`（DAPC 用 `FADE TIME` 控制速率）。

**典型值**：办公照明用默认 7（约 28 步/秒，触感平滑）；舞台快速效果用 1..3（极快）；情绪照明用 13..15（极慢，给观众强烈渐进感）。

**典型陷阱**：① `nFadeRate = 0` 是非法值，灯具忽略不报错；② 与 `FADE TIME` 易混：`FADE RATE` 控制 Up/Down 的速率，`FADE TIME` 控制 DAPC 的渐变时长，是两套独立机制；③ 改完立即用 `FB_DALIV2QueryFadeTimeFadeRate` 验证生效。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- `nFadeRate` 合法范围 1..15；0 灯具忽略不报错。
- 本 FB 不影响 DAPC 的渐变（DAPC 用 `FADE TIME`）。
- EEPROM 写次数有限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetFadeRate.TcPOU`](../examples/P_Demo_FB_DALIV2SetFadeRate.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：舞台演出现场——同一组灯需要不同的调光速率：开场缓慢渐亮（`FADE RATE = 13`），高潮段快速变化（`FADE RATE = 2`）。本 FB 在演出脚本切换段落时切换灯具内部速率。
- **价值**：替代每次调光都改 PLC 循环时序——直接配置灯具内部，省心。
- **替代方案对比**：1) 用 PLC 循环连续 DAPC 自己控变化速率：复杂；2) 用 `FB_DALIV2SetFadeTime` 配 DAPC 做长渐变：DAPC 是绝对目标，FADE TIME 决定到达时间；3) **本 FB**：步进调光速率配置标准方法。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142792587.html
- **相关**：[`FB_DALIV2SetFadeTime`](FB_DALIV2SetFadeTime.md)（控制 DAPC 渐变时长）、[`FB_DALIV2QueryFadeTimeFadeRate`](../part102_low_queries/FB_DALIV2QueryFadeTimeFadeRate.md)、[`FB_DALIV2Up`](../part102_low_power/FB_DALIV2Up.md) / [`FB_DALIV2Down`](../part102_low_power/FB_DALIV2Down.md)
