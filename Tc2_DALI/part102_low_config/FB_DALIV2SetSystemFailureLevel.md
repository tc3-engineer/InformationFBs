# FB_DALIV2SetSystemFailureLevel

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
| Example | [`examples/P_Demo_FB_DALIV2SetSystemFailureLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetSystemFailureLevel.TcPOU) |

---

## 1. 功能简述

**设置镇流器 `SYSTEM FAILURE LEVEL` 寄存器**——DALI 总线物理失效（如 PLC 死机或 KL6821 断电）导致灯具长时间收不到命令时，灯具会自动调到 `SYSTEM FAILURE LEVEL` 值。类似 `POWER ON LEVEL`，但触发条件是 DALI 总线断、不是 220V 断。出厂默认 254（全亮）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart              : BOOL;
    nAddr               : BYTE;
    eAddrType           : E_DALIV2AddrType        := eDALIV2AddrTypeShort;
    eCommandPriority    : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nSystemFailureLevel : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播） |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nSystemFailureLevel` | `BYTE` | — | ⚠️ 待人工确认 |

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

**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nFailureLevel`，下发 `STORE THE DTR AS SYSTEM FAILURE LEVEL` 写入 EEPROM。

**触发时机**：灯具在约 200..400 ms 收不到任何 DALI 命令（KL6821 / PLC 失联）后自动调到 `SYSTEM FAILURE LEVEL`。比 `POWER ON LEVEL` 更敏感——总线一旦失联立即生效。

**典型应用**：① 应急照明法规：总线断时灯具自动全亮（254），保护逃生路径；② 普通办公照明：总线断时维持当前亮度（MASK），让用户不感知；③ 装饰灯：总线断时关灯（0），节能。

**与 KL6821 KBus watchdog 的关系**：KL6821 端子也有自己的 KBus 看门狗（K-Bus 主断时端子触发 DALI 命令）；`SYSTEM FAILURE LEVEL` 是灯具端独立的二级保险——KL6821 也死了灯具仍可自救。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 范围 0..254 或 MASK (255)。
- 默认 254 在总线频繁短断时会大量全亮，慎选。
- 应急照明法规可能强制要求非 MASK 值（如 193 = 75% 亮度），按法规配置。
- 与 `FB_KL6821Config.eCommandKBusWatchdog` 协同——前者是端子自动发 DALI 命令；本 FB 是灯具自救。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2SetSystemFailureLevel.TcPOU`](../examples/P_Demo_FB_DALIV2SetSystemFailureLevel.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：医院应急照明：要求 DALI 总线断时灯具自动全亮 (254)，保护病人疏散通道。
- **价值**：灯具硬件层面的故障保险，PLC / 端子全挂时也能保证安全。
- **替代方案对比**：1) `FB_KL6821Config.eCommandKBusWatchdog`：KL6821 端子层故障保险；2) **本 FB**：灯具层故障保险；两者并用形成两道防线。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.3.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142803339.html
- **相关**：[`FB_DALIV2QuerySystemFailureLevel`](../part102_low_queries/FB_DALIV2QuerySystemFailureLevel.md)、[`FB_DALIV2SetPowerOnLevel`](FB_DALIV2SetPowerOnLevel.md)、[`FB_KL6821Config`](../kl6821_base/FB_KL6821Config.md)
