# FB_DALIV2RecallMinLevel

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
| Example | [`examples/P_Demo_FB_DALIV2RecallMinLevel.TcPOU`](../examples/P_Demo_FB_DALIV2RecallMinLevel.TcPOU) |

---

## 1. 功能简述

**召回最小亮度命令**——灯具调到自身 `MIN VALUE` 寄存器配置的亮度（默认 1 即最低对数档约 0.1%）。受 `FADE TIME` 渐变。注意：本命令不会关灯（0 = 关是另一个命令）；最低也是 `MIN VALUE`。

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

**调用方式**：`bStart` 上升沿；下发 `RECALL MIN LEVEL`；灯具调到 `MIN VALUE` 寄存器值。

**典型应用**：夜间值班调暗（保留可视性）、自然光足时降低人工灯亮度、智能家居睡前调暗。

**与 `DAPC = 1` 区别**：DAPC 1 固定到 1（约 0.1% 物理亮度，很可能根本看不见）；本 FB 调到灯具配置的 `MIN VALUE`（可能配为 30，即工程认可的最暗可见值）。

**典型陷阱**：① 灯具 `MIN VALUE` 默认 1 时看上去几乎全黑，用户会以为灯坏了；上线前应根据现场设置合理的 `MIN VALUE`；② 本命令不关灯，长时间停在 MIN 时电源仍消耗。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 实际亮度是 `MIN VALUE` 而非 1；工程配置 `MIN VALUE` 时要注意。
- 本 FB 不关灯；要关用 `FB_DALIV2Off`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2RecallMinLevel.TcPOU`](../examples/P_Demo_FB_DALIV2RecallMinLevel.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：智能家居睡前模式：用户说『睡眠模式』，PLC 广播本 FB 给卧室所有灯——按各灯 `MIN VALUE` （典型 1..30）调到最暗但不关，提供夜起照明。
- **价值**：比 DAPC=1 更灵活——各灯 `MIN VALUE` 可独立配置成不同的夜间值。
- **替代方案对比**：1) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=1)`：固定到 1；2) **本 FB**：按各灯 `MIN VALUE` 配置。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142777739.html
- **相关**：[`FB_DALIV2RecallMaxLevel`](FB_DALIV2RecallMaxLevel.md)、[`FB_DALIV2SetMinLevel`](../part102_low_config/FB_DALIV2SetMinLevel.md)、[`FB_DALIV2Off`](FB_DALIV2Off.md)（关灯）
