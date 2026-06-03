# FB_DALIV2RecallMaxLevel

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Power Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2RecallMaxLevel.TcPOU`](../examples/P_Demo_FB_DALIV2RecallMaxLevel.TcPOU) |

---

## 1. 功能简述

**召回最大亮度命令**——灯具调到自身 `MAX VALUE` 寄存器配置的亮度（默认 254 即 100%）。受 `FADE TIME` 影响渐变。常用于一键全亮（应急、消防全亮、舞台开场）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |

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

**调用方式**：`bStart` 上升沿；本 FB 下发 `RECALL MAX LEVEL` 命令；灯具调到 `MAX VALUE` 寄存器值（用 `FB_DALIV2SetMaxLevel` 配置）。

**渐变时间**：受 `FADE TIME` 寄存器影响。`FADE TIME = 0` 瞬时；其它值按 DALI 时间表渐变。

**与 `DAPC = 254` 区别**：DAPC 254 固定到 254；本 FB 调到 `MAX VALUE`（可能配置成 200 即 80%）。本 FB 更安全——不会越过配置的上限。

**典型应用**：应急照明（消防 / 火警联动一键全亮）；舞台开场一键满载；办公区到达时间统一开灯。广播下发可让整线灯具同时全亮，但每盏灯按各自 `MAX VALUE` 配置（不同灯可能到不同绝对值）。

**典型陷阱**：① 灯具 `MAX VALUE` 未配置时是默认 254，本 FB 与 DAPC=254 等效；② 渐变期间不要立即查询亮度，会读到中间值；③ 组寻址下若组成员 `MAX VALUE` 差别大，亮度看上去不一致。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 渐变时长由 `FADE TIME` 决定；要瞬时全亮先设 `FADE TIME = 0`。
- 实际亮度是 `MAX VALUE` 而非 254——工程配置 `MAX VALUE` 时要注意。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2RecallMaxLevel.TcPOU`](../examples/P_Demo_FB_DALIV2RecallMaxLevel.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：应急联动：火警触发，PLC 广播本 FB 给所有应急灯，自动全亮（按 `MAX VALUE` 配置，通常 254）。
- **价值**：比 DAPC=254 更安全，自动应用 `MAX VALUE` 钳位。
- **替代方案对比**：1) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=254)`：固定到 254，可能超过 `MAX VALUE` 被钳；2) **本 FB**：自动用 `MAX VALUE`，更符合工程意图。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142776203.html
- **相关**：[`FB_DALIV2RecallMinLevel`](FB_DALIV2RecallMinLevel.md)、[`FB_DALIV2SetMaxLevel`](../part102_low_config/FB_DALIV2SetMaxLevel.md)、[`FB_DALIV2DirectArcPowerControl`](FB_DALIV2DirectArcPowerControl.md)
